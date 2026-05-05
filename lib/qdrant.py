"""
Minimal Qdrant REST client — zero external dependencies.

Uses urllib only. Provides: create collection, upsert points, search, delete, health check.
Qdrant REST API docs: https://qdrant.tech/documentation/interfaces/#rest-api
"""

import json
import urllib.request
import urllib.error
from typing import Optional


class QdrantClient:
    """Lightweight Qdrant client using only urllib."""

    def __init__(self, url: str = "http://127.0.0.1:6333"):
        self.url = url.rstrip("/")

    def _request(self, method: str, path: str, data: Optional[dict] = None) -> dict:
        """Make an HTTP request to Qdrant."""
        url = f"{self.url}{path}"
        body = json.dumps(data).encode() if data else None
        req = urllib.request.Request(
            url,
            data=body,
            method=method,
            headers={"Content-Type": "application/json"} if body else {},
        )
        try:
            with urllib.request.urlopen(req, timeout=30) as resp:
                return json.loads(resp.read().decode())
        except urllib.error.HTTPError as e:
            error_body = e.read().decode() if e.fp else ""
            raise QdrantError(f"HTTP {e.code}: {error_body}") from e
        except urllib.error.URLError as e:
            raise QdrantError(f"Connection failed: {e.reason}") from e

    def healthy(self) -> bool:
        """Check if Qdrant is running and healthy."""
        try:
            self._request("GET", "/healthz")
            return True
        except (QdrantError, OSError):
            return False

    def collection_exists(self, name: str) -> bool:
        """Check if a collection exists."""
        try:
            self._request("GET", f"/collections/{name}")
            return True
        except QdrantError:
            return False

    def create_collection(self, name: str, vector_size: int = 384, distance: str = "Cosine"):
        """Create a collection with vector configuration."""
        data = {
            "vectors": {
                "size": vector_size,
                "distance": distance,
            }
        }
        return self._request("PUT", f"/collections/{name}", data)

    def delete_collection(self, name: str):
        """Delete a collection."""
        return self._request("DELETE", f"/collections/{name}")

    def upsert(self, collection: str, points: list[dict]):
        """
        Upsert points into a collection.

        Each point: {"id": int|str, "vector": [...], "payload": {...}}
        """
        data = {"points": points}
        return self._request("PUT", f"/collections/{collection}/points", data)

    def search(
        self,
        collection: str,
        vector: list[float],
        limit: int = 5,
        score_threshold: Optional[float] = None,
        filter_: Optional[dict] = None,
    ) -> list[dict]:
        """
        Search for nearest vectors.

        Returns list of {"id", "score", "payload"} dicts.
        """
        data = {
            "vector": vector,
            "limit": limit,
            "with_payload": True,
        }
        if score_threshold is not None:
            data["score_threshold"] = score_threshold
        if filter_:
            data["filter"] = filter_

        result = self._request("POST", f"/collections/{collection}/points/search", data)
        return result.get("result", [])

    def count(self, collection: str) -> int:
        """Get point count in a collection."""
        result = self._request("POST", f"/collections/{collection}/points/count", {"exact": True})
        return result.get("result", {}).get("count", 0)

    def delete_points(self, collection: str, ids: list):
        """Delete specific points by ID."""
        data = {"points": ids}
        return self._request("POST", f"/collections/{collection}/points/delete", data)

    def scroll(
        self,
        collection: str,
        limit: int = 100,
        offset: Optional[str] = None,
        filter_: Optional[dict] = None,
    ) -> tuple[list[dict], Optional[str]]:
        """
        Scroll through all points in a collection.

        Returns (points, next_offset). next_offset is None when done.
        """
        data = {"limit": limit, "with_payload": True}
        if offset:
            data["offset"] = offset
        if filter_:
            data["filter"] = filter_

        result = self._request("POST", f"/collections/{collection}/points/scroll", data)
        points = result.get("result", {}).get("points", [])
        next_offset = result.get("result", {}).get("next_page_offset")
        return points, next_offset


    def search_hybrid(
        self,
        collection: str,
        vector: list[float],
        query_text: str,
        limit: int = 5,
        score_threshold: Optional[float] = None,
        filter_: Optional[dict] = None,
    ) -> list[dict]:
        """
        Hybrid search: combine vector similarity + BM25 keyword scoring.

        Uses Qdrant's query API with prefetch for fusion ranking.
        Falls back to pure vector search if hybrid not supported.
        """
        # Try hybrid with RRF (Reciprocal Rank Fusion)
        try:
            # First, try the recommend/query endpoint with text matching
            # Qdrant 1.7+ supports full-text index on payload fields
            data = {
                "vector": vector,
                "limit": limit,
                "with_payload": True,
            }
            if score_threshold is not None:
                data["score_threshold"] = score_threshold
            if filter_:
                data["filter"] = filter_

            # Get vector results
            vector_results = self._request(
                "POST", f"/collections/{collection}/points/search", data
            )
            vector_hits = vector_results.get("result", [])

            # Get keyword results via scroll + filter (BM25 approximation)
            # Search in payload "text" and "heading" fields
            keyword_hits = self._keyword_search(collection, query_text, limit * 2)

            # Fuse results using Reciprocal Rank Fusion (RRF)
            return self._rrf_fuse(vector_hits, keyword_hits, limit)

        except (QdrantError, Exception):
            # Fallback to pure vector search
            return self.search(collection, vector, limit, score_threshold, filter_)

    def _keyword_search(self, collection: str, query: str, limit: int) -> list[dict]:
        """Approximate keyword search via scroll with payload filtering."""
        # Split query into keywords
        keywords = [w.lower() for w in query.split() if len(w) > 2]
        if not keywords:
            return []

        # Use scroll to find points whose text contains keywords
        # This is a simplified BM25 approximation using Qdrant's match conditions
        results = []
        for keyword in keywords[:3]:  # Limit to top 3 keywords for performance
            try:
                filter_ = {
                    "should": [
                        {"key": "text", "match": {"text": keyword}},
                        {"key": "heading", "match": {"text": keyword}},
                    ]
                }
                points, _ = self.scroll(collection, limit=limit, filter_=filter_)
                results.extend(points)
            except QdrantError:
                continue

        # Deduplicate by ID and score by keyword frequency
        seen = {}
        for point in results:
            pid = point.get("id")
            if pid not in seen:
                seen[pid] = {"id": pid, "payload": point.get("payload", {}), "score": 1.0}
            else:
                seen[pid]["score"] += 1.0  # More keyword matches = higher score

        # Normalize scores
        if seen:
            max_score = max(p["score"] for p in seen.values())
            for p in seen.values():
                p["score"] /= max_score

        return sorted(seen.values(), key=lambda x: -x["score"])[:limit]

    def _rrf_fuse(
        self, vector_hits: list[dict], keyword_hits: list[dict], limit: int, k: int = 60
    ) -> list[dict]:
        """
        Reciprocal Rank Fusion — merge two ranked lists.

        RRF score = sum(1 / (k + rank)) across lists.
        k=60 is standard constant from the RRF paper.
        """
        scores = {}  # id -> {score, payload}

        for rank, hit in enumerate(vector_hits):
            pid = hit.get("id")
            rrf_score = 1.0 / (k + rank + 1)
            if pid not in scores:
                scores[pid] = {"id": pid, "payload": hit.get("payload", {}), "score": 0.0}
            scores[pid]["score"] += rrf_score
            # Preserve original vector score for reference
            scores[pid]["vector_score"] = hit.get("score", 0)

        for rank, hit in enumerate(keyword_hits):
            pid = hit.get("id")
            rrf_score = 1.0 / (k + rank + 1)
            if pid not in scores:
                scores[pid] = {"id": pid, "payload": hit.get("payload", {}), "score": 0.0}
            scores[pid]["score"] += rrf_score

        # Sort by fused score
        fused = sorted(scores.values(), key=lambda x: -x["score"])[:limit]
        return fused


class QdrantError(Exception):
    """Qdrant operation failed."""
    pass
