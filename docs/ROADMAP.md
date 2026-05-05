# Engram Roadmap

## v0.1.0 — MVP (DONE)

- [x] 5 core scripts (init, start, end, search, sync)
- [x] Unified `engram` CLI
- [x] `engram status` command
- [x] Configurable via `config.toml`
- [x] Template system (`--template`)
- [x] Zero external Python dependencies (urllib fallback)
- [x] Tests passing (11 tests)
- [x] README, architecture docs, MIT license

---

## v0.2.0 — Vector DB Integration (Qdrant)

Add optional Qdrant integration for persistent vector search beyond file-level caching.

### Why?

Current search re-embeds from file cache on every query. A proper vector DB gives:
- Sub-millisecond search across thousands of chunks
- BM25 hybrid search (keyword + semantic in one query)
- Metadata filtering (by layer, date, file type)
- Scales to 100k+ chunks without degradation

### Tasks

- [ ] Add `engram index` command — indexes all memory into Qdrant
- [ ] Add Qdrant as optional dependency (local binary, no Docker needed)
  - Auto-download: `~/.engram/qdrant/` (single binary, ~30MB)
  - Storage: `~/.engram/qdrant_data/` (per-project collections)
  - Start on demand: `engram index` launches if not running
- [ ] Collection per project (named by project path hash)
- [ ] `engram-end` auto-indexes new chunks (background, non-blocking)
- [ ] `engram search` checks Qdrant first if available, falls back to file-based
- [ ] Add `[vector_db]` section to config.toml:
  ```toml
  [vector_db]
  enabled = false          # opt-in
  provider = "qdrant"      # qdrant | chroma | none
  path = "~/.engram/qdrant_data"
  auto_index = true        # index on engram-end
  ```
- [ ] Hybrid search: combine Qdrant semantic + BM25 keyword scoring

### Architecture

```
engram end "summary"
    │
    ├── Write lossless chunk (always)
    │
    └── If vector_db.enabled && vector_db.auto_index:
        └── engram index --incremental
            ├── Find chunks newer than last index timestamp
            ├── Embed new chunks via Ollama
            └── Upsert into Qdrant collection

engram search "query"
    │
    ├── If Qdrant available:
    │   └── Hybrid search (vector + keyword) → ranked results
    │
    └── Fallback: file-based search (current behavior)
```

---

## v0.3.0 — Claude Code Hook Integration

Auto-checkpoint without manual `engram end` calls.

### Tasks

- [ ] Add Claude Code hook: `PostToolUse` → count tool calls, auto-checkpoint at N
- [ ] Add hook: `SessionEnd` → always run `engram end` on session close
- [ ] `engram hooks install` command — adds hooks to `.claude/settings.json`
- [ ] `engram hooks remove` command — clean removal
- [ ] Config:
  ```toml
  [hooks]
  auto_checkpoint = true
  checkpoint_interval = 15    # tool calls between auto-checkpoints
  session_end_checkpoint = true
  ```

---

## v0.4.0 — Template Ecosystem

### Tasks

- [ ] `engram template create <name>` — export current project's semantic + procedural
  - Scrub project-specific paths/names (interactive or regex rules)
  - Generate `seed.toml` with metadata
- [ ] `engram template list` — show installed templates
- [ ] `engram template install <git-url>` — clone template from repo
- [ ] Community template registry (GitHub topic: `engram-template`)
- [ ] Populate built-in templates:
  - [ ] `d365` — D365 F&O domain knowledge (from ~/.claude/d365-knowledge/)
  - [ ] `react` — React/Next.js patterns
  - [ ] `python` — Python best practices, testing patterns
  - [ ] `devops` — CI/CD, Docker, Kubernetes workflows

---

## v0.5.0 — Advanced Search & Recall

### Tasks

- [ ] Temporal decay: weight recent chunks higher (configurable half-life)
- [ ] `engram recall "what did I do last Tuesday"` — date-aware search
- [ ] Cross-project search: `engram search --global "query"` searches all projects
- [ ] `engram similar` — find sessions similar to current work (auto-suggest)
- [ ] Chunk quality scoring: longer, more structured chunks rank higher
- [ ] Support code-block-aware chunking (don't split inside fenced blocks)

---

## v0.6.0 — Distribution & Packaging

### Tasks

- [ ] `pip install engram-memory` (PyPI package)
- [ ] Homebrew tap: `brew install engram`
- [ ] GitHub Actions CI (test on Ubuntu, macOS, Windows/WSL)
- [ ] Release automation (tag → build → publish)
- [ ] `npx engram` option for Node.js users
- [ ] Shell completions (bash, zsh, fish)

---

## v0.7.0 — Multi-Agent Support

### Tasks

- [ ] Per-agent session isolation (agent ID in lossless chunks)
- [ ] Shared read, isolated write for active layer
- [ ] Conflict detection when multiple agents update semantic/procedural
- [ ] `engram lock <file>` / `engram unlock <file>` for write coordination
- [ ] Agent-aware search: "what did agent-X learn about Y?"

---

## Future Ideas (Unscheduled)

- [ ] Web UI for browsing memory (local, read-only)
- [ ] Export to Obsidian/Notion format
- [ ] PII auto-redaction (scan before writing to lossless)
- [ ] Embedding model swapping (OpenAI, Cohere, local transformers)
- [ ] Memory compaction: merge old lossless chunks into summaries
- [ ] `engram diff` — show what changed between two checkpoints
- [ ] `engram forget "topic"` — mark knowledge as superseded
- [ ] Integration with other AI coding tools (Cursor, Copilot, Aider)
