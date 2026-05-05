#!/usr/bin/env python3
"""Tests for engram hooks install/remove."""

import json
import subprocess
import tempfile
from pathlib import Path

ENGRAM_BIN = Path(__file__).parent.parent / "bin"


def setup_project(tmp: Path):
    """Create minimal engram project for hook testing."""
    subprocess.run(
        ["bash", str(ENGRAM_BIN / "engram-init"), str(tmp)],
        capture_output=True, text=True, cwd=str(tmp)
    )


def test_hooks_install():
    """engram hooks install should add hooks to settings.json."""
    with tempfile.TemporaryDirectory() as tmp:
        tmp = Path(tmp)
        setup_project(tmp)

        # Run hooks install
        result = subprocess.run(
            ["bash", str(ENGRAM_BIN / "engram-hooks"), "install"],
            capture_output=True, text=True, cwd=str(tmp)
        )
        assert result.returncode == 0, f"Install failed: {result.stderr}"

        # Check settings.json
        settings_path = tmp / ".claude" / "settings.json"
        assert settings_path.exists(), "settings.json not created"

        settings = json.loads(settings_path.read_text())
        assert "hooks" in settings
        assert "PostToolUse" in settings["hooks"]
        assert "Stop" in settings["hooks"]

        # Check hook scripts created
        assert (tmp / ".claude" / "scripts" / "engram-hook-checkpoint").exists()
        assert (tmp / ".claude" / "scripts" / "engram-hook-session-end").exists()

        print("  PASS: hooks install creates settings + scripts")


def test_hooks_remove():
    """engram hooks remove should clean up."""
    with tempfile.TemporaryDirectory() as tmp:
        tmp = Path(tmp)
        setup_project(tmp)

        # Install then remove
        subprocess.run(
            ["bash", str(ENGRAM_BIN / "engram-hooks"), "install"],
            capture_output=True, text=True, cwd=str(tmp)
        )
        result = subprocess.run(
            ["bash", str(ENGRAM_BIN / "engram-hooks"), "remove"],
            capture_output=True, text=True, cwd=str(tmp)
        )
        assert result.returncode == 0, f"Remove failed: {result.stderr}"

        # Check hooks removed from settings
        settings = json.loads((tmp / ".claude" / "settings.json").read_text())
        hooks = settings.get("hooks", {})
        assert "PostToolUse" not in hooks or not hooks["PostToolUse"]
        assert "Stop" not in hooks or not hooks["Stop"]

        # Check scripts removed
        assert not (tmp / ".claude" / "scripts" / "engram-hook-checkpoint").exists()
        assert not (tmp / ".claude" / "scripts" / "engram-hook-session-end").exists()

        print("  PASS: hooks remove cleans up everything")


def test_hooks_idempotent():
    """Installing hooks twice should not duplicate entries."""
    with tempfile.TemporaryDirectory() as tmp:
        tmp = Path(tmp)
        setup_project(tmp)

        # Install twice
        for _ in range(2):
            subprocess.run(
                ["bash", str(ENGRAM_BIN / "engram-hooks"), "install"],
                capture_output=True, text=True, cwd=str(tmp)
            )

        settings = json.loads((tmp / ".claude" / "settings.json").read_text())
        # Should have exactly 1 PostToolUse hook, not 2
        assert len(settings["hooks"]["PostToolUse"]) == 1
        assert len(settings["hooks"]["Stop"]) == 1

        print("  PASS: hooks install is idempotent")


if __name__ == "__main__":
    print("Running hooks tests...\n")

    test_hooks_install()
    test_hooks_remove()
    test_hooks_idempotent()

    print("\nAll tests passed!")
