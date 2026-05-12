"""
Embedding provider abstraction for engram.

Supports: ollama (default), openai, cohere, local (sentence-transformers)
Configured via config.toml [embedding] section or environment variables.

Usage:
    from lib.embeddings import get_provider
    provider = get_provider()  # reads config or env
    vector = provider.embed("some text")
    vectors = provider.embed_batch(["text1", "text2"])
"""

import json
import os
import urllib.request
import urllib.error
from pathlib import Path
from typing import Optional


class EmbeddingProvider:
    """Base class for embedding providers."""

    name: str = "base"

    def embed(self, text: str) -> list[float]:
        """Embed a single text. Returns embedding vector."""
        raise NotImplementedError

    def embed_batch(self, texts: list[str]) -> list[list[float]]:
        """Embed multiple texts. Returns list of embedding vectors."""
        return [self.embed(t) for t in texts]


class OllamaProvider(EmbeddingProvider):
    """Ollama local embedding provider (default)."""

    name = "ollama"

    def __init__(self, model: str = "nomic-embed-text", url: str = "http://127.0.0.1:11434"):
        self.model = model
        self.url = url.rstrip("/")

    def embed(self, text: str) -> list[float]:
        """Embed text using Ollama API."""
        data = json.dumps({"model": self.model, "prompt": text}).encode()
        req = urllib.request.Request(
            f"{self.url}/api/embeddings",
            data=data,
            method="POST",
            headers={"Content-Type": "application/json"},
        )
        try:
            with urllib.request.urlopen(req, timeout=30) as resp:
                result = json.loads(resp.read().decode())
                return result["embedding"]
        except (urllib.error.URLError, KeyError) as e:
            raise EmbeddingError(f"Ollama embedding failed: {e}") from e

    def embed_batch(self, texts: list[str]) -> list[list[float]]:
        """Ollama doesn't support batch natively, iterate."""
        return [self.embed(t) for t in texts]


class OpenAIProvider(EmbeddingProvider):
    """OpenAI embedding provider."""

    name = "openai"

    def __init__(self, model: str = "text-embedding-3-small", api_key: Optional[str] = None):
        self.model = model
        self.api_key = api_key or os.environ.get("OPENAI_API_KEY")
        if not self.api_key:
            raise EmbeddingError("OPENAI_API_KEY not set")

    def embed(self, text: str) -> list[float]:
        """Embed text using OpenAI API."""
        return self.embed_batch([text])[0]

    def embed_batch(self, texts: list[str]) -> list[list[float]]:
        """Embed batch using OpenAI API."""
        data = json.dumps({"input": texts, "model": self.model}).encode()
        req = urllib.request.Request(
            "https://api.openai.com/v1/embeddings",
            data=data,
            method="POST",
            headers={
                "Content-Type": "application/json",
                "Authorization": f"Bearer {self.api_key}",
            },
        )
        try:
            with urllib.request.urlopen(req, timeout=60) as resp:
                result = json.loads(resp.read().decode())
                # Sort by index to preserve order
                sorted_data = sorted(result["data"], key=lambda x: x["index"])
                return [item["embedding"] for item in sorted_data]
        except (urllib.error.URLError, KeyError) as e:
            raise EmbeddingError(f"OpenAI embedding failed: {e}") from e


class CohereProvider(EmbeddingProvider):
    """Cohere embedding provider."""

    name = "cohere"

    def __init__(self, model: str = "embed-english-v3.0", api_key: Optional[str] = None):
        self.model = model
        self.api_key = api_key or os.environ.get("COHERE_API_KEY")
        if not self.api_key:
            raise EmbeddingError("COHERE_API_KEY not set")

    def embed(self, text: str) -> list[float]:
        """Embed text using Cohere API."""
        return self.embed_batch([text])[0]

    def embed_batch(self, texts: list[str]) -> list[list[float]]:
        """Embed batch using Cohere API."""
        data = json.dumps({
            "texts": texts,
            "model": self.model,
            "input_type": "search_document",
        }).encode()
        req = urllib.request.Request(
            "https://api.cohere.ai/v1/embed",
            data=data,
            method="POST",
            headers={
                "Content-Type": "application/json",
                "Authorization": f"Bearer {self.api_key}",
            },
        )
        try:
            with urllib.request.urlopen(req, timeout=60) as resp:
                result = json.loads(resp.read().decode())
                return result["embeddings"]
        except (urllib.error.URLError, KeyError) as e:
            raise EmbeddingError(f"Cohere embedding failed: {e}") from e


class LocalProvider(EmbeddingProvider):
    """Local sentence-transformers provider (placeholder)."""

    name = "local"

    def __init__(self, model: str = "all-MiniLM-L6-v2"):
        self.model = model

    def embed(self, text: str) -> list[float]:
        raise EmbeddingError(
            "Local provider requires sentence-transformers. "
            "Install with: pip install sentence-transformers"
        )

    def embed_batch(self, texts: list[str]) -> list[list[float]]:
        raise EmbeddingError(
            "Local provider requires sentence-transformers. "
            "Install with: pip install sentence-transformers"
        )


class EmbeddingError(Exception):
    """Embedding operation failed."""
    pass


def cosine_similarity(a: list, b: list) -> float:
    """Compute cosine similarity between two vectors."""
    if not a or not b or len(a) != len(b):
        return 0.0
    dot = sum(x * y for x, y in zip(a, b))
    norm_a = (sum(x * x for x in a) ** 0.5) or 1.0
    norm_b = (sum(x * x for x in b) ** 0.5) or 1.0
    return dot / (norm_a * norm_b)


# Provider registry
PROVIDERS = {
    "ollama": OllamaProvider,
    "openai": OpenAIProvider,
    "cohere": CohereProvider,
    "local": LocalProvider,
}


def _read_config() -> dict:
    """Read embedding config from config.toml (minimal TOML parser)."""
    config_path = Path(os.environ.get(
        "ENGRAM_CONFIG",
        os.path.expanduser("~/.config/engram/config.toml")
    ))
    if not config_path.is_file():
        return {}

    config = {}
    in_embedding = False
    try:
        for line in config_path.read_text(encoding='utf-8').splitlines():
            line = line.strip()
            if line == "[embedding]":
                in_embedding = True
                continue
            elif line.startswith("["):
                in_embedding = False
                continue
            if in_embedding and "=" in line:
                key, value = line.split("=", 1)
                key = key.strip()
                value = value.strip().strip('"').strip("'")
                config[key] = value
    except (OSError, PermissionError):
        pass

    return config


def get_provider(
    provider_name: Optional[str] = None,
    model: Optional[str] = None,
    **kwargs
) -> EmbeddingProvider:
    """
    Get an embedding provider instance.

    Priority: explicit args > environment > config.toml > default (ollama)
    """
    config = _read_config()

    # Determine provider
    name = (
        provider_name
        or os.environ.get("ENGRAM_EMBEDDING_PROVIDER")
        or config.get("provider")
        or "ollama"
    )

    if name not in PROVIDERS:
        raise EmbeddingError(
            f"Unknown provider '{name}'. Available: {', '.join(PROVIDERS.keys())}"
        )

    # Determine model
    model_name = (
        model
        or os.environ.get("ENGRAM_EMBEDDING_MODEL")
        or config.get("model")
    )

    # Build kwargs for provider
    provider_kwargs = {}
    if model_name:
        provider_kwargs["model"] = model_name

    # Provider-specific config
    if name == "ollama":
        url = config.get("url") or os.environ.get("OLLAMA_URL", "http://127.0.0.1:11434")
        provider_kwargs["url"] = url
    elif name == "openai":
        api_key = config.get("api_key") or os.environ.get("OPENAI_API_KEY")
        if api_key:
            provider_kwargs["api_key"] = api_key
    elif name == "cohere":
        api_key = config.get("api_key") or os.environ.get("COHERE_API_KEY")
        if api_key:
            provider_kwargs["api_key"] = api_key

    provider_kwargs.update(kwargs)
    return PROVIDERS[name](**provider_kwargs)
