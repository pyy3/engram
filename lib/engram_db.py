"""
Shared SQLite database for Engram usage analytics.

Database location: $ENGRAM_HOME/engram-usage.db (default: ~/.engram/engram-usage.db)
Falls back to ~/.claude/engram-usage.db if it exists there already.
"""
import os
import sqlite3
from contextlib import closing
from pathlib import Path

SCHEMA = """
CREATE TABLE IF NOT EXISTS events (
    id INTEGER PRIMARY KEY,
    timestamp TEXT NOT NULL,
    project TEXT NOT NULL,
    operation TEXT NOT NULL,
    layer TEXT,
    file_path TEXT,
    bytes INTEGER DEFAULT 0,
    tokens_est INTEGER DEFAULT 0,
    details TEXT
);
"""

VALID_OPERATIONS = {"start", "end", "search", "read", "write"}


def get_db_path():
    """Resolve DB path: ENGRAM_HOME first, fall back to legacy ~/.claude/."""
    engram_home = Path(os.environ.get("ENGRAM_HOME", Path.home() / ".engram"))
    primary = engram_home / "engram-usage.db"
    legacy = Path.home() / ".claude" / "engram-usage.db"

    if primary.exists():
        return primary
    if legacy.exists():
        return legacy
    # New install — use ENGRAM_HOME
    primary.parent.mkdir(parents=True, exist_ok=True)
    return primary


def get_db():
    """Open (and auto-create) the analytics database. Use with closing()."""
    db_path = get_db_path()
    db_path.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(str(db_path))
    conn.execute(SCHEMA)
    conn.commit()
    return conn


def open_db():
    """Context-manager wrapper: use as `with open_db() as conn:`."""
    return closing(get_db())
