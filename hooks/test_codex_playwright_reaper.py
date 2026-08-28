#!/usr/bin/env python3
from __future__ import annotations

import json
import os
import shutil
import signal
import subprocess
import sys
import tempfile
import time
import unittest
from pathlib import Path


HOOK_DIR = Path(__file__).parent
REAPER_SCRIPT = HOOK_DIR / "codex_playwright_reaper.py"
MEMO_GUARD_SCRIPT = HOOK_DIR / "codex_memo_guard.py"


class PlaywrightReaperTest(unittest.TestCase):
    def setUp(self) -> None:
        self.processes: list[subprocess.Popen[bytes]] = []
        self.addCleanup(self.cleanup_processes)
        self._temp_dir = tempfile.TemporaryDirectory()
        self.addCleanup(self._temp_dir.cleanup)
        node = shutil.which("node")
        if node is None:
            self.fail("node is required for the Playwright daemon boundary test")
        self.node = node
        self.node_daemon_script = (
            Path(self._temp_dir.name)
            / "node-daemon"
            / "node_modules"
            / "playwright-core"
            / "lib"
            / "entry"
            / "cliDaemon.js"
        )
        self.node_daemon_script.parent.mkdir(parents=True)
        self.node_daemon_script.write_text(
            "setTimeout(() => {}, 60_000);\n",
            encoding="utf-8",
        )
        self.non_node_daemon_script = (
            Path(self._temp_dir.name)
            / "non-node-daemon"
            / "node_modules"
            / "playwright-core"
            / "lib"
            / "entry"
            / "cliDaemon.js"
        )
        self.non_node_daemon_script.parent.mkdir(parents=True)
        self.non_node_daemon_script.write_text(
            "import time\ntime.sleep(60)\n",
            encoding="utf-8",
        )

    def spawn_fake_process(
        self, thread_id: str, *, daemon_marker: bool
    ) -> subprocess.Popen[bytes]:
        env = os.environ.copy()
        env["CODEX_THREAD_ID"] = thread_id
        marker = str(
            self.node_daemon_script
            if daemon_marker
            else self.non_node_daemon_script
        )
        command = (
            [self.node, marker, "fake-profile"]
            if daemon_marker
            else [sys.executable, marker, "fake-profile"]
        )
        process = subprocess.Popen(
            command,
            env=env,
            start_new_session=True,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
        )
        self.processes.append(process)
        deadline = time.monotonic() + 2
        while time.monotonic() < deadline:
            try:
                cmdline = Path(f"/proc/{process.pid}/cmdline").read_bytes()
            except FileNotFoundError:
                break
            if marker.encode() in cmdline:
                return process
            time.sleep(0.01)
        self.fail(f"fake daemon {process.pid} did not start")

    def spawn_fake_daemon(self, thread_id: str) -> subprocess.Popen[bytes]:
        return self.spawn_fake_process(thread_id, daemon_marker=True)

    def run_hook(
        self, script: Path, payload: dict[str, object]
    ) -> subprocess.CompletedProcess[str]:
        return subprocess.run(
            [sys.executable, str(script), "stop"]
            if script == MEMO_GUARD_SCRIPT
            else [sys.executable, str(script)],
            input=json.dumps(payload),
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            check=False,
        )

    def assert_process_exits(self, process: subprocess.Popen[bytes]) -> None:
        deadline = time.monotonic() + 2
        while time.monotonic() < deadline:
            if process.poll() is not None:
                return
            time.sleep(0.01)
        self.fail(f"process group {process.pid} is still running")

    def cleanup_processes(self) -> None:
        for process in self.processes:
            if process.poll() is not None:
                continue
            try:
                os.killpg(process.pid, signal.SIGKILL)
            except ProcessLookupError:
                pass
            process.wait(timeout=2)

    def test_standalone_reaps_only_the_matching_thread(self) -> None:
        owned = self.spawn_fake_daemon("owned-thread")
        unrelated = self.spawn_fake_daemon("other-thread")
        same_thread_non_node = self.spawn_fake_process(
            "owned-thread", daemon_marker=False
        )

        result = self.run_hook(
            REAPER_SCRIPT,
            {"hook_event_name": "Stop", "session_id": "owned-thread"},
        )

        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(result.stdout, "")
        self.assert_process_exits(owned)
        self.assertIsNone(unrelated.poll())
        self.assertIsNone(same_thread_non_node.poll())

    def test_configured_stop_hook_reaps_even_without_a_memo(self) -> None:
        owned = self.spawn_fake_daemon("owned-thread")
        with tempfile.TemporaryDirectory() as cwd:
            result = self.run_hook(
                MEMO_GUARD_SCRIPT,
                {
                    "cwd": cwd,
                    "hook_event_name": "Stop",
                    "session_id": "owned-thread",
                    "turn_id": "turn-1",
                },
            )

        self.assertEqual(result.returncode, 0, result.stderr)
        self.assert_process_exits(owned)

    def test_subagent_stop_does_not_reap_the_main_thread(self) -> None:
        owned = self.spawn_fake_daemon("owned-thread")
        with tempfile.TemporaryDirectory() as cwd:
            result = self.run_hook(
                MEMO_GUARD_SCRIPT,
                {
                    "agent_id": "subagent-1",
                    "cwd": cwd,
                    "hook_event_name": "Stop",
                    "session_id": "owned-thread",
                    "turn_id": "turn-1",
                },
            )

        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIsNone(owned.poll())

    def test_non_stop_or_missing_event_fails_without_reaping(self) -> None:
        for script in (REAPER_SCRIPT, MEMO_GUARD_SCRIPT):
            for event_name in ("UserPromptSubmit", None):
                with self.subTest(script=script.name, event_name=event_name):
                    owned = self.spawn_fake_daemon("owned-thread")
                    payload: dict[str, object] = {"session_id": "owned-thread"}
                    if script == MEMO_GUARD_SCRIPT:
                        payload.update(cwd=tempfile.gettempdir(), turn_id="turn-1")
                    if event_name is not None:
                        payload["hook_event_name"] = event_name

                    result = self.run_hook(script, payload)

                    self.assertNotEqual(result.returncode, 0)
                    self.assertIsNone(owned.poll())


if __name__ == "__main__":
    unittest.main()
