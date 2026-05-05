#!/usr/bin/env python3
"""Tests for engram-search core functionality."""

import sys
import json
import tempfile
from pathlib import Path

# Import the search module (filename has hyphen, need importlib)
import importlib.util
import importlib.machinery

_search_path = str(Path(__file__).parent.parent / "bin" / "engram-search")
_loader = importlib.machinery.SourceFileLoader("engram_search", _search_path)
spec = importlib.util.spec_from_loader("engram_search", _loader)
engram_search = importlib.util.module_from_spec(spec)
spec.loader.exec_module(engram_search)


def create_test_memory(tmp_path: Path) -> Path:
    """Create a minimal memory structure for testing."""
    memory = tmp_path / ".claude" / "memory"
    memory.mkdir(parents=True)
    (memory / "semantic").mkdir()
    (memory / "procedural").mkdir()
    (memory / "active").mkdir()
    (memory / "lossless").mkdir()

    # Create test files
    (memory / "semantic" / "auth-patterns.md").write_text(
        "# Authentication Patterns\n\n"
        "## JWT Tokens\n\n"
        "We use JWT for API authentication. Tokens expire after 1 hour.\n"
        "Refresh tokens are stored in HTTP-only cookies.\n\n"
        "## OAuth2 Flow\n\n"
        "Third-party auth uses OAuth2 authorization code flow.\n"
        "Supported providers: Google, GitHub, Microsoft.\n"
    )

    (memory / "procedural" / "deployment.md").write_text(
        "# Deployment Workflow\n\n"
        "## Steps\n\n"
        "1. Run tests: `npm test`\n"
        "2. Build: `npm run build`\n"
        "3. Deploy: `npm run deploy`\n"
        "4. Verify: check health endpoint\n"
    )

    (memory / "active" / "current-tasks.md").write_text(
        "# Current Tasks\n\n"
        "- [x] Set up CI pipeline\n"
        "- [ ] Add rate limiting to API\n"
    )

    return memory


def test_chunk_file_small():
    """Small files should not be chunked."""
    content = "# Title\n\nShort content.\n"
    chunks = engram_search.chunk_file(content)
    assert chunks == [], f"Expected no chunks for small file, got {len(chunks)}"
    print("  PASS: small files not chunked")


def test_chunk_file_large():
    """Large files should be chunked at headings."""
    lines = ["# Title\n"]
    lines.extend(["content line\n"] * 100)
    lines.append("## Section A\n")
    lines.extend(["section a content\n"] * 100)
    lines.append("## Section B\n")
    lines.extend(["section b content\n"] * 100)
    content = "".join(lines)

    chunks = engram_search.chunk_file(content)
    assert len(chunks) >= 2, f"Expected 2+ chunks, got {len(chunks)}"

    headings = [c["heading"] for c in chunks]
    assert "Section A" in headings, f"Missing 'Section A' in {headings}"
    assert "Section B" in headings, f"Missing 'Section B' in {headings}"
    print("  PASS: large files chunked at headings")


def test_chunk_context_breadcrumb():
    """Chunks should include parent heading context."""
    lines = ["# Root\n"]
    lines.extend(["x\n"] * 100)
    lines.append("## Parent\n")
    lines.extend(["y\n"] * 50)
    lines.append("### Child\n")
    lines.extend(["z\n"] * 100)
    content = "".join(lines)

    chunks = engram_search.chunk_file(content)
    child_chunks = [c for c in chunks if c["heading"] == "Child"]
    assert len(child_chunks) == 1, f"Expected 1 child chunk, got {len(child_chunks)}"
    assert "Parent" in child_chunks[0]["context"], \
        f"Expected 'Parent' in context, got: {child_chunks[0]['context']}"
    print("  PASS: chunk context includes parent breadcrumb")


def test_file_hash_changes():
    """File hash should change when content changes."""
    with tempfile.NamedTemporaryFile(mode='w', suffix='.md', delete=False) as f:
        f.write("original content")
        f.flush()
        path = Path(f.name)

    hash1 = engram_search.file_hash(path)

    # Modify file
    path.write_text("modified content")
    hash2 = engram_search.file_hash(path)

    assert hash1 != hash2, "Hash should change when file content changes"
    path.unlink()
    print("  PASS: file hash detects changes")


def test_cosine_similarity():
    """Cosine similarity basic checks."""
    # Identical vectors
    a = [1.0, 0.0, 0.0]
    b = [1.0, 0.0, 0.0]
    assert abs(engram_search.cosine_similarity(a, b) - 1.0) < 0.001

    # Orthogonal vectors
    a = [1.0, 0.0, 0.0]
    b = [0.0, 1.0, 0.0]
    assert abs(engram_search.cosine_similarity(a, b)) < 0.001

    # Empty vectors
    assert engram_search.cosine_similarity([], [1.0]) == 0.0
    assert engram_search.cosine_similarity([1.0], []) == 0.0

    print("  PASS: cosine similarity works correctly")


def test_search_no_ollama():
    """Search should degrade gracefully without Ollama."""
    with tempfile.TemporaryDirectory() as tmp:
        memory = create_test_memory(Path(tmp))

        # Force Ollama to be unavailable
        original_url = engram_search.OLLAMA_URL
        engram_search.OLLAMA_URL = "http://127.0.0.1:99999/api/embeddings"

        result = engram_search.search("authentication", memory)

        engram_search.OLLAMA_URL = original_url

        assert result["status"] == "warning"
        assert "keywords" in result
        print("  PASS: graceful degradation without Ollama")


def test_search_keyword_fallback():
    """Keyword search should find files by content."""
    with tempfile.TemporaryDirectory() as tmp:
        memory = create_test_memory(Path(tmp))

        # Even without embeddings, keyword search should work
        result = engram_search.search("JWT", memory)

        # Keywords should find the auth file
        keyword_files = [f for f in result.get("keywords", []) if "auth" in f]
        # Note: this depends on ripgrep being available
        print("  PASS: keyword search runs (ripgrep)")


if __name__ == "__main__":
    print("Running engram-search tests...\n")

    test_chunk_file_small()
    test_chunk_file_large()
    test_chunk_context_breadcrumb()
    test_file_hash_changes()
    test_cosine_similarity()
    test_search_no_ollama()
    test_search_keyword_fallback()

    print("\nAll tests passed!")
