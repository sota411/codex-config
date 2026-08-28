#!/usr/bin/env python3
from __future__ import annotations

import os
import stat
import subprocess
import tempfile
import unittest
from pathlib import Path


WRAPPER = Path(__file__).with_name("playwright_cli.sh")


class PlaywrightCliWrapperTest(unittest.TestCase):
    def setUp(self) -> None:
        self._temp_dir = tempfile.TemporaryDirectory()
        self.addCleanup(self._temp_dir.cleanup)
        self.bin_dir = Path(self._temp_dir.name)
        npx = self.bin_dir / "npx"
        npx.write_text(
            "#!/usr/bin/env bash\n"
            "printf '<%s>\\n' \"$@\"\n",
            encoding="utf-8",
        )
        npx.chmod(npx.stat().st_mode | stat.S_IXUSR)

    def run_wrapper(
        self,
        *args: str,
        thread_id: str | None = "thread-from-codex",
        configured_session: str | None = None,
    ) -> subprocess.CompletedProcess[str]:
        env = os.environ.copy()
        env["PATH"] = f"{self.bin_dir}:{env['PATH']}"
        if thread_id is None:
            env.pop("CODEX_THREAD_ID", None)
        else:
            env["CODEX_THREAD_ID"] = thread_id
        if configured_session is None:
            env.pop("PLAYWRIGHT_CLI_SESSION", None)
        else:
            env["PLAYWRIGHT_CLI_SESSION"] = configured_session
        return subprocess.run(
            ["bash", str(WRAPPER), *args],
            env=env,
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            check=False,
        )

    def test_wrapper_is_executable(self) -> None:
        self.assertTrue(os.access(WRAPPER, os.X_OK))

    def test_codex_thread_is_the_default_session(self) -> None:
        result = self.run_wrapper("open", "https://example.com")

        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(
            result.stdout.splitlines(),
            [
                "<--yes>",
                "<--package>",
                "<@playwright/cli>",
                "<playwright-cli>",
                "<--session>",
                "<thread-from-codex>",
                "<open>",
                "<https://example.com>",
            ],
        )

    def test_explicit_session_overrides_environment_defaults(self) -> None:
        result = self.run_wrapper(
            "-s=manual", "snapshot", configured_session="configured-session"
        )

        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(
            result.stdout.splitlines(),
            [
                "<--yes>",
                "<--package>",
                "<@playwright/cli>",
                "<playwright-cli>",
                "<-s=manual>",
                "<snapshot>",
            ],
        )

    def test_session_like_value_after_delimiter_keeps_codex_thread(self) -> None:
        result = self.run_wrapper("eval", "--", "--session")

        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(
            result.stdout.splitlines(),
            [
                "<--yes>",
                "<--package>",
                "<@playwright/cli>",
                "<playwright-cli>",
                "<--session>",
                "<thread-from-codex>",
                "<eval>",
                "<-->",
                "<--session>",
            ],
        )

    def test_configured_session_overrides_codex_thread(self) -> None:
        result = self.run_wrapper(
            "snapshot", configured_session="configured-session"
        )

        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("<configured-session>", result.stdout.splitlines())
        self.assertNotIn("<thread-from-codex>", result.stdout.splitlines())

    def test_outside_codex_keeps_the_cli_default(self) -> None:
        result = self.run_wrapper("list", thread_id=None)

        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertNotIn("<--session>", result.stdout.splitlines())


if __name__ == "__main__":
    unittest.main()
