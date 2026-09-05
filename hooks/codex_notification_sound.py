#!/usr/bin/env python3
from __future__ import annotations

import argparse
import io
import json
from pathlib import Path
import subprocess
import sys
from urllib.parse import urlencode
from urllib.request import Request, urlopen
import wave


SOUNDS = Path(__file__).resolve().parent / "sounds" / "zundamon"


def generate(engine_url: str) -> None:
    template = json.loads((SOUNDS / "template.json").read_text(encoding="utf-8"))

    def request(path: str, data: bytes | None = None) -> bytes:
        req = Request(engine_url.rstrip("/") + path, data=data,
                      headers={"Content-Type": "application/json"})
        with urlopen(req, timeout=60) as response:
            return response.read()

    version = json.loads(request("/version"))
    if version != template["engine_version"]:
        raise ValueError(f"expected VOICEVOX {template['engine_version']}, got {version}")
    styles = [style["id"] for speaker in json.loads(request("/speakers"))
              if speaker["name"] == template["speaker"]
              for style in speaker["styles"] if style["name"] == template["style"]]
    if len(styles) != 1:
        raise ValueError("VOICEVOX speaker/style must match exactly once")
    speaker_id = styles[0]
    audio_files = {}
    for name in ("complete", "question"):
        params = urlencode({"text": template["phrases"][name], "speaker": speaker_id})
        query = json.loads(request("/audio_query?" + params, b""))
        query["speedScale"] = template["speed_scale"]
        audio = request(f"/synthesis?speaker={speaker_id}", json.dumps(query).encode())
        with wave.open(io.BytesIO(audio)) as wav:
            if wav.getnframes() == 0:
                raise ValueError(f"empty audio: {name}")
            print(f"{name}.wav: {wav.getnframes() / wav.getframerate():.2f}s")
        audio_files[name] = audio
    for name, audio in audio_files.items():
        target = SOUNDS / f"{name}.wav"
        temporary = target.with_suffix(".wav.tmp")
        temporary.write_bytes(audio)
        temporary.replace(target)


def notify() -> None:
    payload = json.load(sys.stdin)
    if not isinstance(payload, dict) or not isinstance(payload.get("hook_event_name"), str):
        raise ValueError("hook input must contain hook_event_name")
    if any(payload.get(key) is not None for key in ("agent_id", "agent_type")):
        return
    event = payload["hook_event_name"]
    if event == "Stop":
        name = "complete"
    elif event == "PreToolUse" and payload["tool_name"] == "request_user_input":
        name = "question"
    else:
        return
    subprocess.run(["paplay", str(SOUNDS / f"{name}.wav")], check=True, timeout=8)


def main() -> int:
    parser = argparse.ArgumentParser(description="Play Codex notification voices or regenerate their WAV files.")
    parser.add_argument("--generate", action="store_true")
    parser.add_argument("--engine-url", default="http://127.0.0.1:50021")
    args = parser.parse_args()
    try:
        if args.generate:
            generate(args.engine_url)
        else:
            notify()
    except (OSError, ValueError, KeyError, wave.Error, subprocess.SubprocessError) as error:
        # A Stop hook's exit 2 requests continuation; playback failures must not do that.
        print(f"Codex notification: {error}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
