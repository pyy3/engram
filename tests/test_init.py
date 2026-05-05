#!/usr/bin/env python3
"""Tests for engram-init scaffolding."""

import os
import subprocess
import tempfile
from pathlib import Path

ENGRAM_BIN = Path(__file__).parent.parent / "bin"


def run_init(project_dir: str, *extra_args) -> subprocess.CompletedProcess:
    """Run engram-init in a directory."""
    cmd = ["bash", str(ENGRAM_BIN / "engram-init"), project_dir] + list(extra_args)
    return subprocess.run(cmd, capture_output=True, text=True, cwd=project_dir)


def test_basic_init():
    """engram init should create the full directory structure."""
    with tempfile.TemporaryDirectory() as tmp:
        result = run_init(tmp)
        assert result.returncode == 0, f"Init failed: {result.stderr}"

        # Check directories
        assert (Path(tmp) / ".claude" / "memory" / "active").is_dir()
        assert (Path(tmp) / ".claude" / "memory" / "semantic").is_dir()
        assert (Path(tmp) / ".claude" / "memory" / "procedural").is_dir()
        assert (Path(tmp) / ".claude" / "memory" / "lossless").is_dir()
        assert (Path(tmp) / ".claude" / "scripts").is_dir()

        # Check seed files
        assert (Path(tmp) / ".claude" / "memory" / "active" / "current-tasks.md").exists()
        assert (Path(tmp) / ".claude" / "memory" / "active" / "context-inject.md").exists()

        # Check CLAUDE.md
        assert (Path(tmp) / "CLAUDE.md").exists()
        content = (Path(tmp) / "CLAUDE.md").read_text()
        assert "Engram" in content
        assert "5-Layer" in content

        print("  PASS: basic init creates full structure")


def test_idempotent_init():
    """Running init twice should not duplicate or overwrite."""
    with tempfile.TemporaryDirectory() as tmp:
        run_init(tmp)

        # Modify a file
        tasks = Path(tmp) / ".claude" / "memory" / "active" / "current-tasks.md"
        tasks.write_text("# My custom tasks\n- task 1\n")

        # Run init again
        result = run_init(tmp)
        assert result.returncode == 0

        # Custom content should be preserved
        assert "My custom tasks" in tasks.read_text()

        # CLAUDE.md should not be duplicated
        claude_md = (Path(tmp) / "CLAUDE.md").read_text()
        assert claude_md.count("## Engram") == 1

        print("  PASS: init is idempotent")


def test_init_with_existing_claude_md():
    """Init should append protocol to existing CLAUDE.md."""
    with tempfile.TemporaryDirectory() as tmp:
        # Create existing CLAUDE.md
        claude_md = Path(tmp) / "CLAUDE.md"
        claude_md.write_text("# My Project\n\nExisting content here.\n")

        run_init(tmp)

        content = claude_md.read_text()
        assert "My Project" in content, "Original content should be preserved"
        assert "Engram" in content, "Engram protocol should be appended"

        print("  PASS: appends to existing CLAUDE.md")


def test_init_creates_gitignore():
    """Init should create .gitignore for cache directory."""
    with tempfile.TemporaryDirectory() as tmp:
        run_init(tmp)

        gitignore = Path(tmp) / ".claude" / "memory" / ".gitignore"
        assert gitignore.exists()
        assert ".cache/" in gitignore.read_text()

        print("  PASS: creates .gitignore for cache")


if __name__ == "__main__":
    print("Running engram-init tests...\n")

    test_basic_init()
    test_idempotent_init()
    test_init_with_existing_claude_md()
    test_init_creates_gitignore()

    print("\nAll tests passed!")
