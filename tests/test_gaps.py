#!/usr/bin/env python3
"""Tests for lib/gaps.py — miss detection, gap storage, similarity matching."""

import sys
import json
import tempfile
from pathlib import Path

# Add lib/ to path
sys.path.insert(0, str(Path(__file__).parent.parent / "lib"))

from gaps import GapStore, is_miss, cosine_similarity


def test_is_miss_empty():
    """Empty results = miss."""
    result = {"chunks": [], "files": [], "keywords": []}
    assert is_miss(result) is True
    print("  PASS: empty results detected as miss")


def test_is_miss_low_score():
    """Low score results = miss."""
    result = {"chunks": [{"score": 0.15}], "files": [], "keywords": []}
    assert is_miss(result) is True
    print("  PASS: low score results detected as miss")


def test_is_miss_good_score():
    """Good score results = not a miss."""
    result = {"chunks": [{"score": 0.65}], "files": [], "keywords": []}
    assert is_miss(result) is False
    print("  PASS: good score results not a miss")


def test_is_miss_file_score():
    """File score above threshold = not a miss."""
    result = {"chunks": [], "files": [{"score": 0.45}], "keywords": []}
    assert is_miss(result) is False
    print("  PASS: file score above threshold not a miss")


def test_gap_record_and_list():
    """Record a gap and list it."""
    with tempfile.TemporaryDirectory() as tmp:
        memory = Path(tmp) / ".claude" / "memory"
        (memory / "semantic").mkdir(parents=True)

        store = GapStore(memory)
        rec = store.record("k8s autoscaling", 0.12)

        assert rec["status"] == "open"
        assert rec["query"] == "k8s autoscaling"
        assert rec["best_score"] == 0.12

        open_gaps = store.list_open()
        assert len(open_gaps) == 1
        assert open_gaps[0]["query"] == "k8s autoscaling"
        print("  PASS: record and list gap")


def test_gap_fill():
    """Fill a gap."""
    with tempfile.TemporaryDirectory() as tmp:
        memory = Path(tmp) / ".claude" / "memory"
        (memory / "semantic").mkdir(parents=True)

        store = GapStore(memory)
        store.record("k8s autoscaling", 0.12)
        store.fill("k8s autoscaling")

        open_gaps = store.list_open()
        assert len(open_gaps) == 0
        print("  PASS: fill gap removes from open list")


def test_gap_dismiss():
    """Dismiss a gap."""
    with tempfile.TemporaryDirectory() as tmp:
        memory = Path(tmp) / ".claude" / "memory"
        (memory / "semantic").mkdir(parents=True)

        store = GapStore(memory)
        store.record("false positive", 0.0)
        store.dismiss("false positive")

        open_gaps = store.list_open()
        assert len(open_gaps) == 0
        print("  PASS: dismiss gap removes from open list")


def test_gap_increment():
    """Increment search count."""
    with tempfile.TemporaryDirectory() as tmp:
        memory = Path(tmp) / ".claude" / "memory"
        (memory / "semantic").mkdir(parents=True)

        store = GapStore(memory)
        rec = store.record("missing topic", 0.1)
        store.increment(rec["id"])

        open_gaps = store.list_open()
        assert open_gaps[0]["times_searched"] == 2
        print("  PASS: increment times_searched")


def test_gap_find_by_text():
    """Find gap by text match."""
    with tempfile.TemporaryDirectory() as tmp:
        memory = Path(tmp) / ".claude" / "memory"
        (memory / "semantic").mkdir(parents=True)

        store = GapStore(memory)
        store.record("k8s autoscaling", 0.12)

        match = store.find_match_by_text("k8s autoscaling")
        assert match is not None
        assert match["query"] == "k8s autoscaling"

        no_match = store.find_match_by_text("completely different")
        assert no_match is None
        print("  PASS: find gap by text match")


def test_gap_find_by_embedding():
    """Find gap by embedding similarity."""
    with tempfile.TemporaryDirectory() as tmp:
        memory = Path(tmp) / ".claude" / "memory"
        (memory / "semantic").mkdir(parents=True)

        store = GapStore(memory)
        emb = [1.0, 0.0, 0.0, 0.5]
        store.record("k8s autoscaling", 0.12, embedding=emb)

        # Similar embedding should match
        similar_emb = [0.95, 0.05, 0.0, 0.48]
        match = store.find_match(similar_emb)
        assert match is not None

        # Different embedding should not match
        diff_emb = [0.0, 1.0, 0.0, 0.0]
        no_match = store.find_match(diff_emb)
        assert no_match is None
        print("  PASS: find gap by embedding similarity")


def test_gap_stats():
    """Stats aggregation."""
    with tempfile.TemporaryDirectory() as tmp:
        memory = Path(tmp) / ".claude" / "memory"
        (memory / "semantic").mkdir(parents=True)

        store = GapStore(memory)
        store.record("topic a", 0.1)
        store.record("topic b", 0.2)
        store.record("topic c", 0.15)
        store.fill("topic b")

        s = store.stats()
        assert s["total"] == 3
        assert s["open"] == 2
        assert s["filled"] == 1
        assert s["dismissed"] == 0
        print("  PASS: gap stats")


def test_cosine_sim():
    """Cosine similarity sanity."""
    assert abs(cosine_similarity([1, 0], [1, 0]) - 1.0) < 0.001
    assert abs(cosine_similarity([1, 0], [0, 1])) < 0.001
    assert cosine_similarity([], [1]) == 0.0
    print("  PASS: cosine similarity")


def test_no_embedding_gaps():
    """Gaps without embeddings still work."""
    with tempfile.TemporaryDirectory() as tmp:
        memory = Path(tmp) / ".claude" / "memory"
        (memory / "semantic").mkdir(parents=True)

        store = GapStore(memory)
        store.record("no emb query", 0.0)

        # find_match should return None (no embeddings to compare)
        match = store.find_match([1.0, 0.0])
        assert match is None

        open_gaps = store.list_open()
        assert len(open_gaps) == 1
        print("  PASS: gaps without embeddings functional")


if __name__ == "__main__":
    print("Running gap tracking tests...\n")

    test_is_miss_empty()
    test_is_miss_low_score()
    test_is_miss_good_score()
    test_is_miss_file_score()
    test_gap_record_and_list()
    test_gap_fill()
    test_gap_dismiss()
    test_gap_increment()
    test_gap_find_by_text()
    test_gap_find_by_embedding()
    test_gap_stats()
    test_cosine_sim()
    test_no_embedding_gaps()

    print("\nAll gap tracking tests passed!")
