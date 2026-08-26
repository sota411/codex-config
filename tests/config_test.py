from __future__ import annotations

import json
import os
import shlex
import subprocess
import tomllib
import unittest
from pathlib import Path


CODEX_HOME = Path(__file__).resolve().parents[1]


class CodexConfigTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.config = tomllib.loads((CODEX_HOME / "config.toml").read_text(encoding="utf-8"))

    def test_main_agent_keeps_max_reasoning(self) -> None:
        self.assertEqual(self.config["model"], "gpt-5.6-sol")
        self.assertEqual(self.config["model_reasoning_effort"], "max")
        self.assertEqual(self.config["plan_mode_reasoning_effort"], "max")

    def test_codex_accepts_the_live_config_in_strict_mode(self) -> None:
        result = subprocess.run(
            ["codex", "app-server", "--stdio", "--strict-config"],
            cwd=CODEX_HOME,
            stdin=subprocess.DEVNULL,
            text=True,
            capture_output=True,
            check=False,
        )
        self.assertEqual(result.returncode, 0, result.stderr)

    def test_secret_env_files_are_ignored_inside_tracked_trees(self) -> None:
        protected = (
            "user-skills/example/.env",
            "user-skills/example/.env.local",
            "user-skills/example/.dev.vars",
            "user-skills/example/.dev.vars.local",
            "user-skills/example/.envrc",
            "user-skills/example/.envrc.local",
        )
        templates = (
            "user-skills/example/.env.example",
            "user-skills/example/.dev.vars.template",
            "user-skills/example/.envrc.dist",
        )
        root_templates = (".env.example", ".dev.vars.template", ".envrc.dist")
        for path in protected:
            with self.subTest(path=path):
                result = subprocess.run(
                    ["git", "check-ignore", "--no-index", "--quiet", "--", path],
                    cwd=CODEX_HOME,
                    check=False,
                )
                self.assertEqual(result.returncode, 0, path)
        for path in templates:
            with self.subTest(path=path):
                result = subprocess.run(
                    ["git", "check-ignore", "--no-index", "--quiet", "--", path],
                    cwd=CODEX_HOME,
                    check=False,
                )
                self.assertEqual(result.returncode, 1, path)
        for path in root_templates:
            with self.subTest(path=path):
                result = subprocess.run(
                    ["git", "check-ignore", "--no-index", "--quiet", "--", path],
                    cwd=CODEX_HOME,
                    check=False,
                )
                self.assertEqual(result.returncode, 0, path)

    def test_hook_commands_reference_existing_scripts(self) -> None:
        hooks = self.config["hooks"]
        for event in ("PreToolUse", "UserPromptSubmit", "Stop"):
            with self.subTest(event=event):
                command = hooks[event][0]["hooks"][0]["command"]
                tokens = shlex.split(os.path.expandvars(command))
                self.assertGreaterEqual(len(tokens), 2)
                self.assertTrue(Path(tokens[1]).is_file(), tokens[1])

    def test_hook_configuration_is_portable(self) -> None:
        hooks = self.config["hooks"]
        for event in ("PreToolUse", "UserPromptSubmit", "Stop"):
            with self.subTest(event=event):
                command = hooks[event][0]["hooks"][0]["command"]
                self.assertIn("$HOME/.codex/hooks/", command)
                self.assertNotIn("/home/sota411", command)

    def test_mcp_settings_do_not_embed_static_credentials(self) -> None:
        for name, server in self.config.get("mcp_servers", {}).items():
            with self.subTest(server=name):
                self.assertNotIn("env", server)
                self.assertNotIn("http_headers", server)

    def test_custom_agent_profiles_are_valid_toml(self) -> None:
        expected_efforts = {
            "scout_fast": "low",
            "tester_fast": "low",
            "worker_standard": "medium",
            "reviewer_deep": "max",
            "specialist_max": "max",
        }
        actual: dict[str, str] = {}
        for path in sorted((CODEX_HOME / "agents").glob("*.toml")):
            profile = tomllib.loads(path.read_text(encoding="utf-8"))
            actual[profile["name"]] = profile["model_reasoning_effort"]
        self.assertEqual(actual, expected_efforts)

    def test_reviewer_deep_uses_requested_model_and_effort(self) -> None:
        profile = tomllib.loads(
            (CODEX_HOME / "agents" / "reviewer_deep.toml").read_text(encoding="utf-8")
        )
        self.assertEqual(profile["model"], "gpt-5.6-luna")
        self.assertEqual(profile["model_reasoning_effort"], "max")

    def test_custom_agent_models_and_efforts_exist_in_current_catalog(self) -> None:
        result = subprocess.run(
            ["codex", "debug", "models"],
            cwd=CODEX_HOME,
            text=True,
            capture_output=True,
            check=False,
        )
        self.assertEqual(result.returncode, 0, result.stderr)
        catalog = json.loads(result.stdout)
        supported = {
            model["slug"]: {level["effort"] for level in model["supported_reasoning_levels"]}
            for model in catalog["models"]
        }
        for path in sorted((CODEX_HOME / "agents").glob("*.toml")):
            profile = tomllib.loads(path.read_text(encoding="utf-8"))
            with self.subTest(profile=profile["name"]):
                self.assertIn(profile["model"], supported)
                self.assertIn(
                    profile["model_reasoning_effort"],
                    supported[profile["model"]],
                )


if __name__ == "__main__":
    unittest.main()
