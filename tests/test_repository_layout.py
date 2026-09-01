from __future__ import annotations

import re
import unittest
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
SKILLS_ROOT = REPO_ROOT / "skills"
PROJECT_SKILLS_ROOT = REPO_ROOT / ".agents" / "skills"


class RepositoryLayoutTestCase(unittest.TestCase):
    def test_skill_directory_matches_frontmatter_name(self):
        for skill_directory in sorted(SKILLS_ROOT.iterdir()):
            skill_file = skill_directory / "SKILL.md"
            if not skill_file.is_file():
                continue

            match = re.search(
                r"^name:\s*([^\s]+)\s*$",
                skill_file.read_text(encoding="utf-8"),
                re.MULTILINE,
            )
            with self.subTest(skill=skill_directory.name):
                self.assertIsNotNone(match, f"{skill_file} has no frontmatter name")
                self.assertEqual(skill_directory.name, match.group(1))

    def test_project_skill_links_resolve_to_matching_skill_directories(self):
        for link in sorted(PROJECT_SKILLS_ROOT.iterdir()):
            expected_target = SKILLS_ROOT / link.name
            with self.subTest(link=link.name):
                self.assertTrue(link.is_symlink(), f"expected a skill link: {link}")
                self.assertTrue(link.exists(), f"broken skill link: {link}")
                self.assertEqual(expected_target.resolve(), link.resolve())
                self.assertTrue((link / "SKILL.md").is_file())

    def test_every_skill_has_a_project_discovery_link(self):
        skill_names = {
            directory.name
            for directory in SKILLS_ROOT.iterdir()
            if (directory / "SKILL.md").is_file()
        }
        link_names = {link.name for link in PROJECT_SKILLS_ROOT.iterdir()}

        self.assertEqual(skill_names, link_names)

    def test_relative_skill_links_resolve_within_the_skill(self):
        markdown_link = re.compile(r"\]\(([^)]+)\)")

        for skill_file in sorted(SKILLS_ROOT.glob("*/SKILL.md")):
            for raw_target in markdown_link.findall(
                skill_file.read_text(encoding="utf-8")
            ):
                if raw_target.startswith(("#", "http://", "https://")):
                    continue

                relative_target = raw_target.split("#", 1)[0]
                if not relative_target.lower().endswith(".md"):
                    continue

                target = (skill_file.parent / relative_target).resolve()

                with self.subTest(skill=skill_file.parent.name, target=raw_target):
                    self.assertTrue(target.is_file(), f"broken skill link: {raw_target}")
                    self.assertTrue(target.is_relative_to(skill_file.parent.resolve()))

    def test_migration_skill_is_project_discoverable(self):
        link = PROJECT_SKILLS_ROOT / "migrate-to-parallel"

        self.assertTrue(link.is_symlink())
        self.assertTrue(link.exists())

    def test_memory_skill_is_project_discoverable(self):
        link = PROJECT_SKILLS_ROOT / "parallel-memory"

        self.assertTrue(link.is_symlink())
        self.assertTrue(link.exists())


if __name__ == "__main__":
    unittest.main()
