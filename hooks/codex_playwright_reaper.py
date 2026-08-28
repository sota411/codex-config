#!/usr/bin/env python3
from __future__ import annotations

import json
import os
import signal
import sys
import time
from pathlib import Path


PROC_ROOT = Path("/proc")
DAEMON_ARG_SUFFIX = b"/playwright-core/lib/entry/cliDaemon.js"
THREAD_ENV_PREFIX = b"CODEX_THREAD_ID="
NODE_EXECUTABLE_NAMES = frozenset({"node", "nodejs"})
TERMINATE_TIMEOUT_SECONDS = 1.0
POLL_INTERVAL_SECONDS = 0.02


def main() -> int:
    payload = read_payload()
    reap_for_payload(payload)
    return 0


def read_payload() -> dict[str, object]:
    raw = sys.stdin.read()
    if not raw.strip():
        raise ValueError("hook payload is empty")
    payload = json.loads(raw)
    if not isinstance(payload, dict):
        raise TypeError("hook payload must be an object")
    return payload


def reap_for_payload(payload: dict[str, object]) -> int:
    require_stop_event(payload)
    if payload.get("agent_id") is not None or payload.get("agent_type") is not None:
        return 0

    session_id = payload.get("session_id")
    if not isinstance(session_id, str) or not session_id:
        raise ValueError("hook payload requires a non-empty session_id")
    return reap_thread(session_id)


def require_stop_event(payload: dict[str, object]) -> None:
    if "hook_event_name" not in payload:
        raise KeyError("hook payload missing required key: hook_event_name")
    actual = str(payload["hook_event_name"])
    if actual != "Stop":
        raise ValueError(f"expected hook event Stop, got {actual}")


def reap_thread(thread_id: str) -> int:
    targets: list[int] = []
    for entry in PROC_ROOT.iterdir():
        if not entry.name.isdigit():
            continue
        pid = int(entry.name)
        if not is_owned_daemon(entry, thread_id):
            continue
        try:
            process_group = os.getpgid(pid)
            process_session = os.getsid(pid)
        except ProcessLookupError:
            continue
        if process_group != pid or process_session != pid:
            print(
                f"codex-playwright-reaper: skipped unsafe target pid={pid}",
                file=sys.stderr,
            )
            continue
        targets.append(pid)

    remaining: set[int] = set()
    for process_group in targets:
        try:
            os.killpg(process_group, signal.SIGTERM)
        except ProcessLookupError:
            continue
        remaining.add(process_group)

    deadline = time.monotonic() + TERMINATE_TIMEOUT_SECONDS
    while remaining and time.monotonic() < deadline:
        remaining = {
            process_group
            for process_group in remaining
            if process_group_exists(process_group)
        }
        if remaining:
            time.sleep(POLL_INTERVAL_SECONDS)

    for process_group in remaining:
        try:
            os.killpg(process_group, signal.SIGKILL)
        except ProcessLookupError:
            pass

    return len(targets)


def is_owned_daemon(process_dir: Path, thread_id: str) -> bool:
    try:
        argv = process_dir.joinpath("cmdline").read_bytes().split(b"\0")
        if len(argv) < 3 or not argv[1].endswith(DAEMON_ARG_SUFFIX):
            return False
        executable_name = Path(os.readlink(process_dir / "exe")).name
        if executable_name not in NODE_EXECUTABLE_NAMES:
            return False
        environ = process_dir.joinpath("environ").read_bytes().split(b"\0")
    except (FileNotFoundError, PermissionError, ProcessLookupError):
        return False

    expected = THREAD_ENV_PREFIX + thread_id.encode("utf-8")
    return expected in environ


def process_group_exists(process_group: int) -> bool:
    try:
        os.killpg(process_group, 0)
    except ProcessLookupError:
        return False
    except PermissionError:
        return True
    return True


if __name__ == "__main__":
    raise SystemExit(main())
