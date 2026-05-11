"""
Knowledge gap tracking library for engram.

Detects search misses and tracks them as knowledge gaps.
Gaps accumulate in .claude/memory/semantic/.gaps.jsonl.

Usage:
    from gaps import GapStore, is_miss

    store = GapStore(memory_root)
    if is_miss(result):
        store.record(query, best_score, embedding)
    match = store.find_match(query_embedding)
"""

import json
import os
import time
from pathlib import Path
from datetime import datetime


GAPS_FILE = ".gaps.jsonl"
GAPS_EMBEDDINGS_FILE = ".gaps-embeddings.json"
MISS_SCORE_THRESHOLD = 0.30
GAP_SIMILARITY_THRESHOLD = 0.75


def is_miss(result: dict) -> bool:
    """Determine if a search result represents a knowledge miss."""
    chunks = result.get("chunks", [])
    files = result.get("files", [])

    # Zero results = definite miss
    if not chunks and not files:
        return True

    # Best score below threshold = miss
    best = 0.0
    for c in chunks:
        best = max(best, c.get("score", 0))
    for f in files:
        best = max(best, f.get("score", 0))

    return best < MISS_SCORE_THRESHOLD


def cosine_similarity(a: list, b: list) -> float:
    """Compute cosine similarity between two vectors."""
    if not a or not b or len(a) != len(b):
        return 0.0
    dot = sum(x * y for x, y in zip(a, b))
    norm_a = (sum(x * x for x in a) ** 0.5) or 1.0
    norm_b = (sum(x * x for x in b) ** 0.5) or 1.0
    return dot / (norm_a * norm_b)


class GapStore:
    """Manages knowledge gap records in a JSONL file."""

    def __init__(self, memory_root: Path):
        self.memory_root = memory_root
        self.gaps_path = memory_root / "semantic" / GAPS_FILE
        self._emb_path = memory_root / "semantic" / GAPS_EMBEDDINGS_FILE

    def _load(self) -> list[dict]:
        """Load all gap records."""
        if not self.gaps_path.exists():
            return []
        gaps = []
        for line in self.gaps_path.read_text(encoding="utf-8").splitlines():
            line = line.strip()
            if line:
                try:
                    gaps.append(json.loads(line))
                except json.JSONDecodeError:
                    continue
        return gaps

    def _append(self, record: dict):
        """Append a gap record."""
        self.gaps_path.parent.mkdir(parents=True, exist_ok=True)
        with open(self.gaps_path, "a", encoding="utf-8") as f:
            f.write(json.dumps(record) + "\n")

    def _save_all(self, gaps: list[dict]):
        """Rewrite all gap records (atomic via temp file)."""
        self.gaps_path.parent.mkdir(parents=True, exist_ok=True)
        tmp = self.gaps_path.with_suffix(".tmp")
        with open(tmp, "w", encoding="utf-8") as f:
            for gap in gaps:
                f.write(json.dumps(gap) + "\n")
        os.replace(str(tmp), str(self.gaps_path))

    def _load_embeddings(self) -> dict:
        """Load embedding sidecar {gap_id: vector}."""
        if not self._emb_path.exists():
            return {}
        try:
            return json.loads(self._emb_path.read_text(encoding="utf-8"))
        except (json.JSONDecodeError, OSError):
            return {}

    def _save_embedding(self, gap_id: str, embedding: list):
        """Save an embedding to the sidecar file."""
        embs = self._load_embeddings()
        embs[gap_id] = embedding
        self._emb_path.parent.mkdir(parents=True, exist_ok=True)
        tmp = self._emb_path.with_suffix(".tmp")
        with open(tmp, "w", encoding="utf-8") as f:
            json.dump(embs, f)
        os.replace(str(tmp), str(self._emb_path))

    def _next_id(self) -> str:
        """Generate next gap ID (timestamp-based, no race conditions)."""
        return f"g-{datetime.now().strftime('%Y%m%d-%H%M%S-%f')}"

    def record(self, query: str, best_score: float, embedding: list = None):
        """Record a new knowledge gap."""
        gap_id = self._next_id()
        record = {
            "id": gap_id,
            "query": query,
            "timestamp": datetime.now().isoformat(),
            "best_score": round(best_score, 4),
            "times_searched": 1,
            "last_searched": datetime.now().isoformat(),
            "status": "open",
        }
        self._append(record)
        if embedding:
            self._save_embedding(gap_id, embedding)
        return record

    def find_match(self, query_embedding: list) -> dict | None:
        """Find an existing gap that matches the query embedding."""
        if not query_embedding:
            return None
        gaps = self._load()
        embs = self._load_embeddings()
        for gap in gaps:
            if gap.get("status") != "open":
                continue
            gap_emb = embs.get(gap.get("id")) or gap.get("embedding")
            if gap_emb:
                sim = cosine_similarity(query_embedding, gap_emb)
                if sim > GAP_SIMILARITY_THRESHOLD:
                    return gap
        return None

    def find_match_by_text(self, query: str) -> dict | None:
        """Find an existing gap by exact or substring query match."""
        q_lower = query.lower().strip()
        gaps = self._load()
        for gap in gaps:
            if gap.get("status") != "open":
                continue
            if gap.get("query", "").lower().strip() == q_lower:
                return gap
        return None

    def increment(self, gap_id: str):
        """Increment times_searched for a gap."""
        gaps = self._load()
        for gap in gaps:
            if gap.get("id") == gap_id:
                gap["times_searched"] = gap.get("times_searched", 1) + 1
                gap["last_searched"] = datetime.now().isoformat()
                break
        self._save_all(gaps)

    def fill(self, query: str):
        """Mark a gap as filled."""
        gaps = self._load()
        q_lower = query.lower().strip()
        for gap in gaps:
            if gap.get("query", "").lower().strip() == q_lower and gap.get("status") == "open":
                gap["status"] = "filled"
                gap["filled_at"] = datetime.now().isoformat()
                break
        self._save_all(gaps)

    def dismiss(self, query: str):
        """Dismiss a gap (false positive)."""
        gaps = self._load()
        q_lower = query.lower().strip()
        for gap in gaps:
            if gap.get("query", "").lower().strip() == q_lower and gap.get("status") == "open":
                gap["status"] = "dismissed"
                break
        self._save_all(gaps)

    def list_open(self) -> list[dict]:
        """List all open gaps (without embeddings for display)."""
        gaps = self._load()
        result = []
        for gap in gaps:
            if gap.get("status") == "open":
                display = {k: v for k, v in gap.items() if k != "embedding"}
                result.append(display)
        return result

    def stats(self) -> dict:
        """Return gap statistics."""
        gaps = self._load()
        total = len(gaps)
        open_count = sum(1 for g in gaps if g.get("status") == "open")
        filled = sum(1 for g in gaps if g.get("status") == "filled")
        dismissed = sum(1 for g in gaps if g.get("status") == "dismissed")
        frequent = sorted(
            [g for g in gaps if g.get("status") == "open"],
            key=lambda g: g.get("times_searched", 0),
            reverse=True,
        )[:5]
        return {
            "total": total,
            "open": open_count,
            "filled": filled,
            "dismissed": dismissed,
            "most_searched": [
                {"query": g["query"], "times": g.get("times_searched", 1)}
                for g in frequent
            ],
        }
