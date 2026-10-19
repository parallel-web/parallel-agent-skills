from __future__ import annotations

import base64
import json
import os
import shutil
import struct
import subprocess
import tempfile
import unittest
import xml.etree.ElementTree as ET
import zipfile
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
MANIFEST_PATH = Path(".antigravity-plugin/plugin.json")
PACKAGE_FILES = {
    ".antigravity-plugin/plugin.json": ".antigravity-plugin/plugin.json",
    "mcp_config.json": "mcp_config.json",
    "assets/antigravity.svg": "assets/antigravity.svg",
    "README.md": "docs/antigravity.md",
    "LICENSE": "LICENSE",
}


class AntigravityPluginTestCase(unittest.TestCase):
    def test_root_manifest_resolves_search_config_and_logo_from_repository_root(self):
        plugin = REPO_ROOT
        self.assertEqual({"plugin.json"}, {p.name for p in (plugin / ".antigravity-plugin").iterdir()})
        self.assertFalse((plugin / "plugins/antigravity/parallel").exists())
        self.assertFalse(any((plugin / source).is_symlink() for source in PACKAGE_FILES.values()))

        manifest = json.loads((plugin / MANIFEST_PATH).read_text())
        self.assertEqual("parallel", manifest["name"])
        self.assertEqual((REPO_ROOT / "VERSION").read_text().strip(), manifest["version"])
        for field in ("displayName", "description", "author", "suggestedPrompts"):
            self.assertTrue(manifest[field], field)
        self.assertLessEqual(len(manifest["suggestedPrompts"]), 3)
        logo = ET.parse(plugin / manifest["logo"]).getroot()
        width, height = float(logo.attrib["width"]), float(logo.attrib["height"])
        self.assertEqual(width, height)
        self.assertGreaterEqual(width, 128)
        self.assertEqual([0, 0, width, height], [float(v) for v in logo.attrib["viewBox"].split()])
        brand = logo.find("{http://www.w3.org/2000/svg}image")
        self.assertIsNotNone(brand)
        self.assertAlmostEqual(0.1, float(brand.attrib["x"]) / width)
        self.assertAlmostEqual(0.1, float(brand.attrib["y"]) / height)
        self.assertAlmostEqual(0.8, float(brand.attrib["width"]) / width)
        self.assertAlmostEqual(0.8, float(brand.attrib["height"]) / height)
        header, encoded = brand.attrib["href"].split(",", 1)
        self.assertEqual("data:image/png;base64", header)
        original = base64.b64decode(encoded, validate=True)
        self.assertEqual((REPO_ROOT / ".claude-plugin/icon.png").read_bytes(), original)
        image_width, image_height = struct.unpack(">II", original[16:24])
        self.assertEqual(image_width, image_height)

        config = json.loads((plugin / "mcp_config.json").read_text())
        canonical = json.loads((REPO_ROOT / ".mcp.json").read_text())
        self.assertEqual(
            {"mcpServers": {"parallel-search": {
                "serverUrl": canonical["mcpServers"]["parallel-search"]["url"],
            }}},
            config,
        )
        # An exact native connection shape also excludes credential prompts,
        # auth headers, local subprocesses, and the legacy url transport field.


class AntigravityReleaseTestCase(unittest.TestCase):
    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory()
        self.addCleanup(self.temporary.cleanup)
        self.root = Path(self.temporary.name)
        self.repo = self.root / "repo"
        shutil.copytree(
            REPO_ROOT,
            self.repo,
            ignore=shutil.ignore_patterns(
                ".git", ".agent", ".venv", "node_modules", "dist", "release-assets", "__pycache__"
            ),
            symlinks=True,
        )
        (self.repo / "node_modules").symlink_to(REPO_ROOT / "node_modules", target_is_directory=True)
        self.version = (self.repo / "VERSION").read_text().strip()

    def run_command(self, *args, check=True, env=None):
        result = subprocess.run(args, cwd=self.repo, env=env, text=True, capture_output=True)
        if check:
            self.assertEqual(0, result.returncode, result.stdout + result.stderr)
        return result

    def run_script(self, script, *args, **kwargs):
        return self.run_command("node", "node_modules/tsx/dist/cli.mjs", script, *args, **kwargs)

    def test_archives_preserve_skills_and_ship_only_installable_plugin_files(self):
        plugin = self.repo
        # Unrelated authoring files must never enter a distributed package.
        (plugin / "private-notes.txt").write_text("must not ship\n")
        self.run_script("scripts/build.ts", "archives", "--version", self.version, "--output", "release-assets")
        output = self.repo / "release-assets"
        skill_dirs = [p for p in (self.repo / "skills").iterdir() if (p / "SKILL.md").is_file()]
        expected = {f"{p.name}-{self.version}.zip" for p in skill_dirs}
        plugin_archive = f"parallel-antigravity-{self.version}.zip"
        self.assertEqual(expected | {plugin_archive}, {p.name for p in output.iterdir()})

        for directory in skill_dirs:
            with zipfile.ZipFile(output / f"{directory.name}-{self.version}.zip") as archive:
                for source in directory.rglob("*"):
                    if source.is_file():
                        name = f"{directory.name}/{source.relative_to(directory).as_posix()}"
                        self.assertEqual(source.read_bytes(), archive.read(name))

        with zipfile.ZipFile(output / plugin_archive) as archive:
            self.assertEqual({f"parallel/{p}" for p in PACKAGE_FILES}, set(archive.namelist()))
            archive.extractall(self.root / "unpacked")
        installed = self.root / "unpacked/parallel"
        for name, source in PACKAGE_FILES.items():
            self.assertEqual((plugin / source).read_bytes(), (installed / name).read_bytes())
        manifest = json.loads((installed / MANIFEST_PATH).read_text())
        self.assertTrue((installed / manifest["logo"]).is_file())
        self.assertEqual({"plugin.json"}, {p.name for p in (installed / ".antigravity-plugin").iterdir()})
        for component in ("skills", "agents", "rules", "hooks.json"):
            self.assertFalse((installed / component).exists())

    def test_mismatched_archive_version_preserves_existing_output(self):
        output = self.repo / "release-assets"
        output.mkdir()
        sentinel = output / "previous-artifact.zip"
        sentinel.write_bytes(b"retain previous build")
        result = self.run_script(
            "scripts/build.ts", "archives", "--version", "999.0.0", "--output", "release-assets", check=False
        )
        self.assertNotEqual(0, result.returncode)
        self.assertIn("version", result.stderr.lower())
        self.assertEqual(b"retain previous build", sentinel.read_bytes())

    def test_archive_builder_still_accepts_tag_prefixed_versions(self):
        version = f"v{self.version}"
        self.run_script("scripts/build.ts", "archives", "--version", version, "--output", "release-assets")
        self.assertTrue((self.repo / "release-assets" / f"parallel-antigravity-{version}.zip").is_file())

    def test_release_pr_commits_every_version_update(self):
        # Exercise the actual release operator against a disposable local remote.
        # Only GitHub is stubbed, so no network publication can happen.
        remote = self.root / "remote.git"
        self.run_command("git", "init", "--bare", str(remote))
        self.run_command("git", "init", "-b", "main")
        self.run_command("git", "config", "user.name", "Release Test")
        self.run_command("git", "config", "user.email", "release-test@example.com")
        self.run_command("git", "config", "commit.gpgsign", "false")
        self.run_command("git", "config", "core.hooksPath", str(self.root / "no-hooks"))
        self.run_command("git", "add", ".")
        self.run_command("git", "commit", "-m", "Release fixture")
        self.run_command("git", "remote", "add", "origin", str(remote))
        self.run_command("git", "push", "-u", "origin", "main")
        bin_dir = self.root / "bin"
        bin_dir.mkdir()
        gh = bin_dir / "gh"
        gh.write_text(
            '#!/bin/sh\ncase "$1 $2" in\n'
            '  "auth status") exit 0 ;;\n'
            '  "pr create") printf "%s\\n" "$@" > "$TEST_GH_ARGS"; '
            'printf "https://example.com/local-release-review\\n" ;;\n'
            '  *) exit 70 ;;\nesac\n'
        )
        gh.chmod(0o755)
        environment = dict(os.environ, PATH=f"{bin_dir}{os.pathsep}{os.environ['PATH']}",
                           TEST_GH_ARGS=str(self.root / "gh-args"))
        self.run_script("scripts/open-release-pr.ts", "--part", "patch", env=environment)
        major, minor, patch = self.version.split(".")
        expected = f"{major}.{minor}.{int(patch) + 1}"
        self.assertEqual(expected, (self.repo / "VERSION").read_text().strip())
        for path in (".claude-plugin/plugin.json", ".codex-plugin/plugin.json", MANIFEST_PATH):
            committed = self.run_command("git", "show", f"HEAD:{path}").stdout
            self.assertEqual(expected, json.loads(committed)["version"], str(path))
        marketplace = json.loads(self.run_command("git", "show", "HEAD:.claude-plugin/marketplace.json").stdout)
        self.assertEqual(expected, marketplace["metadata"]["version"])
        self.assertEqual(expected, marketplace["plugins"][0]["version"])
        self.assertEqual("", self.run_command("git", "status", "--porcelain").stdout)
        self.assertIn(f"release/v{expected}", (self.root / "gh-args").read_text())


if __name__ == "__main__":
    unittest.main()
