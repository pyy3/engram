"""Script installer for engram-memory pip package."""
import os
import shutil
import stat
from pathlib import Path


def install_scripts():
    """Install engram scripts to ENGRAM_HOME/bin/."""
    engram_home = Path(os.environ.get("ENGRAM_HOME", Path.home() / ".engram"))
    bin_dir = engram_home / "bin"
    bin_dir.mkdir(parents=True, exist_ok=True)

    # Find source scripts (shipped with package)
    pkg_dir = Path(__file__).parent
    source_bin = pkg_dir.parent.parent / "bin"

    if not source_bin.is_dir():
        print(f"Warning: bin/ not found at {source_bin}")
        return

    for script in source_bin.iterdir():
        if script.is_file() and script.name.startswith("engram"):
            dest = bin_dir / script.name
            shutil.copy2(script, dest)
            dest.chmod(dest.stat().st_mode | stat.S_IEXEC)

    print(f"Scripts installed to {bin_dir}")
