from __future__ import annotations

import os
import re
import shlex
import shutil
import subprocess
import unittest
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
SKILL_PATH = REPO_ROOT / "skills" / "parallel-monitor" / "SKILL.md"

# This matrix intentionally mirrors the Monitor surface documented by the skill.
# The tests derive its command and flag inventory from SKILL.md and validate each
# concrete invocation against the mapping below.
MONITOR_CONTRACT: dict[str, tuple[str, ...]] = {
    "create": ("--frequency", "--webhook", "--metadata", "--output-schema", "--json"),
    "list": ("-n", "--status", "--json"),
    "events": ("--cursor", "--event-group-id", "--json"),
    "get": ("--json",),
    "update": ("--frequency", "--webhook", "--json"),
    "trigger": ("--json",),
    "cancel": ("--json",),
}

OBSOLETE_COMMANDS = ("simulate", "delete", "event-group")
OBSOLETE_FLAGS = ("--cadence", "--lookback")


def documented_monitor_invocations(skill_text: str) -> list[tuple[str, tuple[str, ...], str]]:
    invocations: list[tuple[str, tuple[str, ...], str]] = []
    for match in re.finditer(r"(?m)(?:^|`)(parallel-cli monitor [^`\n]+)", skill_text):
        invocation = match.group(1).strip()
        tokens = shlex.split(invocation)
        command = tokens[2]
        flags = tuple(token.split("=", 1)[0] for token in tokens[3:] if token.startswith("-"))
        invocations.append((command, flags, invocation))
    return invocations


class ParallelMonitorCliContractTestCase(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.skill_text = SKILL_PATH.read_text(encoding="utf-8")
        cls.cli_path = shutil.which("parallel-cli")
        if cls.cli_path is None:
            raise RuntimeError(
                "parallel-cli is required for the Monitor contract test; "
                "install the released parallel-web-tools package"
            )

        version = cls.run_cli("--version")
        if version.returncode != 0:
            raise RuntimeError(
                "parallel-cli --version failed: "
                f"{version.stderr.strip() or version.stdout.strip()}"
            )
        cls.cli_version = version.stdout.strip()

    @classmethod
    def run_cli(cls, *args: str) -> subprocess.CompletedProcess[str]:
        environment = os.environ.copy()
        environment.update({"COLUMNS": "120", "NO_COLOR": "1"})
        return subprocess.run(
            [cls.cli_path, *args],
            capture_output=True,
            check=False,
            env=environment,
            text=True,
        )

    def assert_cli_succeeded(self, result: subprocess.CompletedProcess[str], invocation: str):
        self.assertEqual(
            0,
            result.returncode,
            f"{invocation} failed against {self.cli_version}:\n{result.stderr or result.stdout}",
        )

    def test_documented_commands_exist_in_released_cli(self):
        argument_hint = re.search(
            r"^argument-hint:\s*<([^>]+)>",
            self.skill_text,
            re.MULTILINE,
        )
        self.assertIsNotNone(argument_hint, "parallel-monitor has no command argument-hint")
        documented_commands = set(argument_hint.group(1).split("|"))
        expected_commands = set(MONITOR_CONTRACT)
        self.assertEqual(
            expected_commands,
            documented_commands,
            "argument-hint and Monitor contract matrix disagree",
        )

        invocations = documented_monitor_invocations(self.skill_text)
        self.assertTrue(invocations, "parallel-monitor has no concrete CLI examples")
        invoked_commands = {command for command, _, _ in invocations}
        self.assertLessEqual(
            invoked_commands,
            expected_commands,
            "SKILL.md invokes a Monitor command missing from the contract matrix",
        )

        result = self.run_cli("monitor", "--help")
        self.assert_cli_succeeded(result, "parallel-cli monitor --help")
        for command in sorted(expected_commands):
            with self.subTest(command=command):
                self.assertRegex(
                    result.stdout,
                    rf"(?m)^\s+{re.escape(command)}\s+",
                    f"{command!r} is documented but missing from {self.cli_version}",
                )

    def test_documented_flags_exist_under_the_correct_commands(self):
        monitor_documentation = self.skill_text.partition("## Setup")[0]
        documented_long_flags = set(re.findall(r"(?<![\w-])--[a-z][a-z-]*", monitor_documentation))
        expected_long_flags = {
            flag
            for flags in MONITOR_CONTRACT.values()
            for flag in flags
            if flag.startswith("--")
        }
        self.assertEqual(
            expected_long_flags,
            documented_long_flags,
            "documented Monitor flags and contract matrix disagree",
        )

        for command, flags, invocation in documented_monitor_invocations(self.skill_text):
            with self.subTest(invocation=invocation):
                self.assertIn(
                    command,
                    MONITOR_CONTRACT,
                    f"{invocation!r} uses a command missing from the contract matrix",
                )
                undocumented_for_command = set(flags) - set(MONITOR_CONTRACT[command])
                self.assertFalse(
                    undocumented_for_command,
                    f"{invocation!r} assigns flags to the wrong Monitor command: "
                    f"{sorted(undocumented_for_command)}",
                )

        for command, flags in MONITOR_CONTRACT.items():
            result = self.run_cli("monitor", command, "--help")
            self.assert_cli_succeeded(result, f"parallel-cli monitor {command} --help")
            for flag in flags:
                with self.subTest(command=command, flag=flag):
                    self.assertRegex(
                        result.stdout,
                        rf"(?<![\w-]){re.escape(flag)}(?=[\s,=])",
                        f"{flag!r} is documented for {command!r} but missing from {self.cli_version}",
                    )

    def test_obsolete_monitor_surface_is_not_documented(self):
        obsolete_command_pattern = "|".join(map(re.escape, OBSOLETE_COMMANDS))
        self.assertNotRegex(
            self.skill_text,
            rf"\bparallel-cli\s+monitor\s+(?:{obsolete_command_pattern})\b",
        )
        self.assertNotRegex(
            self.skill_text,
            rf"\*\*(?:{obsolete_command_pattern})\*\*",
        )
        self.assertNotRegex(
            self.skill_text,
            rf"`monitor\s+(?:{obsolete_command_pattern})\b",
        )
        for flag in OBSOLETE_FLAGS:
            with self.subTest(flag=flag):
                self.assertNotIn(flag, self.skill_text)


if __name__ == "__main__":
    unittest.main()
