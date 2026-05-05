#!/usr/bin/env python3
"""Tests for the Qdrant client library."""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent / "lib"))

from qdrant import QdrantClient, QdrantError


def test_health_check_offline():
    """Health check should return False when Qdrant isn't running on test port."""
    client = QdrantClient("http://127.0.0.1:59999")  # unlikely to be in use
    assert client.healthy() is False
    print("  PASS: health check returns False when offline")


def test_collection_exists_offline():
    """collection_exists should raise or return False when Qdrant isn't reachable."""
    client = QdrantClient("http://127.0.0.1:59999")
    try:
        result = client.collection_exists("test")
        # If it doesn't raise, it should return False
        assert result is False
    except QdrantError:
        pass  # Also acceptable — raising is fine
    print("  PASS: collection_exists handles offline gracefully")


def test_client_url_normalization():
    """Client should handle trailing slashes."""
    client = QdrantClient("http://localhost:6333/")
    assert client.url == "http://localhost:6333"

    client2 = QdrantClient("http://localhost:6333")
    assert client2.url == "http://localhost:6333"
    print("  PASS: URL normalization works")


def test_qdrant_live():
    """Integration test — only runs if Qdrant is actually available."""
    client = QdrantClient("http://127.0.0.1:6333")

    if not client.healthy():
        print("  SKIP: Qdrant not running (live tests skipped)")
        return

    test_collection = "_engram_test_collection"

    # Clean up from previous test runs
    try:
        client.delete_collection(test_collection)
    except QdrantError:
        pass

    # Create collection
    client.create_collection(test_collection, vector_size=4)
    assert client.collection_exists(test_collection)

    # Upsert
    client.upsert(test_collection, [
        {"id": 1, "vector": [1.0, 0.0, 0.0, 0.0], "payload": {"text": "hello"}},
        {"id": 2, "vector": [0.0, 1.0, 0.0, 0.0], "payload": {"text": "world"}},
        {"id": 3, "vector": [0.9, 0.1, 0.0, 0.0], "payload": {"text": "hi"}},
    ])

    # Count
    count = client.count(test_collection)
    assert count == 3, f"Expected 3, got {count}"

    # Search
    results = client.search(test_collection, vector=[1.0, 0.0, 0.0, 0.0], limit=2)
    assert len(results) == 2
    assert results[0]["payload"]["text"] == "hello"  # most similar
    assert results[1]["payload"]["text"] == "hi"     # second most similar

    # Delete
    client.delete_points(test_collection, [1])
    count = client.count(test_collection)
    assert count == 2

    # Cleanup
    client.delete_collection(test_collection)
    assert not client.collection_exists(test_collection)

    print("  PASS: full Qdrant CRUD lifecycle (live)")


if __name__ == "__main__":
    print("Running Qdrant client tests...\n")

    test_health_check_offline()
    test_collection_exists_offline()
    test_client_url_normalization()
    test_qdrant_live()

    print("\nAll tests passed!")
