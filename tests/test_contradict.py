#!/usr/bin/env python3
"""Tests for engram-contradict — negation, numeric mismatch, opposition, storage."""

import sys
import json
import tempfile
from pathlib import Path

# Import the contradict module
import importlib.util
import importlib.machinery

_contradict_path = str(Path(__file__).parent.parent / "bin" / "engram-contradict")
_loader = importlib.machinery.SourceFileLoader("engram_contradict", _contradict_path)
spec = importlib.util.spec_from_loader("engram_contradict", _loader)
engram_contradict = importlib.util.module_from_spec(spec)
spec.loader.exec_module(engram_contradict)


def test_negation_detect():
    """Detect negation contradiction."""
    text_a = "We use JWT tokens for API authentication. Tokens expire after 1 hour."
    text_b = "We don't use JWT tokens for API authentication. Session cookies are preferred."
    hits = engram_contradict.detect_negation(text_a, text_b)
    assert len(hits) > 0, f"Expected negation hit, got none"
    assert hits[0]["signal"] == "negation"
    print("  PASS: negation detected")


def test_negation_no_false_positive():
    """No false positive when both agree."""
    text_a = "We use JWT tokens for authentication."
    text_b = "We use OAuth2 tokens for authorization."
    hits = engram_contradict.detect_negation(text_a, text_b)
    # Both have "use" (no negation), so no hit
    assert len(hits) == 0, f"Expected no negation hit, got {len(hits)}"
    print("  PASS: no negation false positive")


def test_numeric_mismatch():
    """Detect numeric value contradictions."""
    text_a = "timeout: 30\nretries: 3"
    text_b = "timeout: 60\nretries: 3"
    hits = engram_contradict.detect_numeric_mismatch(text_a, text_b)
    assert len(hits) == 1, f"Expected 1 numeric mismatch, got {len(hits)}"
    assert hits[0]["signal"] == "numeric_mismatch"
    assert "timeout" in hits[0]["snippet_a"]
    print("  PASS: numeric mismatch detected")


def test_numeric_no_mismatch():
    """No false positive when numbers match."""
    text_a = "timeout: 30\nretries: 3"
    text_b = "timeout: 30\nretries: 3"
    hits = engram_contradict.detect_numeric_mismatch(text_a, text_b)
    assert len(hits) == 0
    print("  PASS: no numeric false positive")


def test_opposition_detect():
    """Detect opposition verb pairs."""
    text_a = "Enable debug logging for the API server during development."
    text_b = "Disable debug logging for the API server in production."
    hits = engram_contradict.detect_opposition(text_a, text_b)
    assert len(hits) > 0, f"Expected opposition hit, got none"
    assert hits[0]["signal"] == "opposition"
    print("  PASS: opposition detected")


def test_check_pair_combined():
    """check_pair runs all detectors."""
    text_a = "timeout: 30\nWe use JWT for auth."
    text_b = "timeout: 60\nWe don't use JWT for auth."
    hits = engram_contradict.check_pair(text_a, text_b)
    signals = {h["signal"] for h in hits}
    assert "numeric_mismatch" in signals, f"Missing numeric_mismatch in {signals}"
    assert "negation" in signals, f"Missing negation in {signals}"
    print("  PASS: check_pair combines all detectors")


def test_contradiction_store():
    """Store records, list, and resolve."""
    with tempfile.TemporaryDirectory() as tmp:
        memory = Path(tmp) / ".claude" / "memory"
        (memory / "semantic").mkdir(parents=True)

        store = engram_contradict.ContradictionStore(memory)

        hit = {"signal": "negation", "snippet_a": "use JWT", "snippet_b": "don't use JWT"}
        rec = store.record("semantic/auth.md", "semantic/api.md", 0.82, hit)

        assert rec["status"] == "unresolved"
        assert rec["id"].startswith("c-")

        unresolved = store.list_unresolved()
        assert len(unresolved) == 1

        store.resolve(rec["id"])
        unresolved = store.list_unresolved()
        assert len(unresolved) == 0
        print("  PASS: contradiction store CRUD")


def test_duplicate_detection():
    """Store rejects duplicate contradictions."""
    with tempfile.TemporaryDirectory() as tmp:
        memory = Path(tmp) / ".claude" / "memory"
        (memory / "semantic").mkdir(parents=True)

        store = engram_contradict.ContradictionStore(memory)

        hit = {"signal": "negation", "snippet_a": "a", "snippet_b": "b"}
        store.record("file_a.md", "file_b.md", 0.8, hit)

        assert store.is_duplicate("file_a.md", "file_b.md", "negation") is True
        assert store.is_duplicate("file_b.md", "file_a.md", "negation") is True
        assert store.is_duplicate("file_a.md", "file_c.md", "negation") is False
        print("  PASS: duplicate detection")


def test_extract_sentences():
    """Sentence extraction handles markdown."""
    text = "# Heading\n\nFirst sentence here.\nSecond sentence there.\nShort."
    sents = engram_contradict._extract_sentences(text)
    assert len(sents) >= 2
    assert any("First sentence" in s for s in sents)
    print("  PASS: sentence extraction")


if __name__ == "__main__":
    print("Running contradiction detection tests...\n")

    test_negation_detect()
    test_negation_no_false_positive()
    test_numeric_mismatch()
    test_numeric_no_mismatch()
    test_opposition_detect()
    test_check_pair_combined()
    test_contradiction_store()
    test_duplicate_detection()
    test_extract_sentences()

    print("\nAll contradiction detection tests passed!")
