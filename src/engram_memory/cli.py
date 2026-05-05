#!/usr/bin/env python3
"""Engram CLI entry point for pip-installed package."""
import os
import sys
import subprocess
from pathlib import Path


def get_bin_dir() -> Path:
    """Find the bin/ directory with engram scripts."""
    # When installed via pip, scripts are bundled in the package
    pkg_dir = Path(__file__).parent
    bin_dir = pkg_dir / "bin"
    if bin_dir.is_dir():
        return bin_dir
    # Fallback: check ENGRAM_HOME
    engram_home = Path(os.environ.get("ENGRAM_HOME", Path.home() / ".engram"))
    return engram_home / "bin"


def main():
    """Main CLI entry point."""
    bin_dir = get_bin_dir()
    engram_script = bin_dir / "engram"

    if not engram_script.exists():
        print("Error: engram scripts not found.")
        print(f"Searched: {bin_dir}")
        print("Run: engram-memory-setup")
        sys.exit(1)

    # Pass through to the bash script
    args = [str(engram_script)] + sys.argv[1:]
    try:
        result = subprocess.run(args, env={**os.environ, "PATH": f"{bin_dir}:{os.environ.get('PATH', '')}"})
        sys.exit(result.returncode)
    except FileNotFoundError:
        print("Error: bash not found. Engram requires bash.")
        sys.exit(1)


if __name__ == "__main__":
    main()
