from __future__ import annotations

import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest


SCRIPT = Path(__file__).with_name("codex_notification_sound.py")


class NotificationSoundTest(unittest.TestCase):
    def test_hook_events_select_the_expected_audio(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            log = root / "played"
            player = root / "paplay"
            player.write_text('#!/bin/sh\nprintf "%s\\n" "$1" >> "$PLAY_LOG"\n', encoding="utf-8")
            player.chmod(0o755)
            env = dict(os.environ, PATH=f"{root}:{os.environ['PATH']}", PLAY_LOG=str(log))
            cases = [
                ({"hook_event_name": "Stop"}, "complete.wav"),
                ({"hook_event_name": "PreToolUse", "tool_name": "request_user_input"}, "question.wav"),
                ({"hook_event_name": "Stop", "agent_id": "child"}, None),
                ({"hook_event_name": "PreToolUse", "tool_name": "request_user_input", "agent_type": "worker"}, None),
                ({"hook_event_name": "SubagentStop"}, None),
                ({"hook_event_name": "Interrupt"}, None),
                ({"hook_event_name": "PreToolUse", "tool_name": "Bash"}, None),
            ]
            for payload, expected in cases:
                with self.subTest(payload=payload):
                    log.unlink(missing_ok=True)
                    result = subprocess.run([sys.executable, str(SCRIPT)], input=json.dumps(payload),
                                            text=True, capture_output=True, env=env)
                    self.assertEqual(result.returncode, 0, result.stderr)
                    self.assertEqual(result.stdout, "")
                    played = [Path(line).name for line in log.read_text().splitlines()] if log.exists() else []
                    self.assertEqual(played, [expected] if expected else [])
            for malformed in ("not json", "{}", '[]'):
                with self.subTest(malformed=malformed):
                    log.unlink(missing_ok=True)
                    result = subprocess.run([sys.executable, str(SCRIPT)], input=malformed,
                                            text=True, capture_output=True, env=env)
                    self.assertEqual(result.returncode, 1)
                    self.assertTrue(result.stderr)
                    self.assertFalse(log.exists())
            player.write_text('#!/bin/sh\nexit 2\n', encoding="utf-8")
            result = subprocess.run([sys.executable, str(SCRIPT)], input='{"hook_event_name":"Stop"}',
                                    text=True, capture_output=True, env=env)
            # Exit 2 would ask a Stop hook to continue the agent's work.
            self.assertEqual(result.returncode, 1)
            self.assertTrue(result.stderr)


if __name__ == "__main__":
    unittest.main()
