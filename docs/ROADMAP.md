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

## v0.2.0 — Vector DB Integration (DONE)

- [x] `engram index` command — indexes all memory into Qdrant
- [x] Qdrant as optional dependency (local binary, ~30MB)
- [x] Collection per project (deterministic name from path hash)
- [x] `engram-end` auto-indexes new chunks (background, non-blocking)
- [x] `engram search` checks Qdrant first if available, falls back to file-based
- [x] `[vector_db]` section in config.toml (enabled, provider, auto_index, hybrid_search)
- [x] Hybrid search: BM25 keyword + vector scoring with RRF fusion

---

## v0.3.0 — Claude Code Hook Integration (DONE)

- [x] PostToolUse hook: counts tool calls, auto-checkpoints at N
- [x] Stop (session end) hook: always runs `engram end` on exit
- [x] `engram hooks install` / `remove` / `status` commands
- [x] Configurable interval via config.toml `[hooks]` section
- [x] Counter-based checkpointing with PID-scoped state

---

## v0.4.0 — Template Ecosystem (DONE)

- [x] `engram template create <name>` — export current project knowledge
- [x] `engram template list` — show installed templates
- [x] `engram template install <git-url|path>` — install from repo or directory
- [x] `engram template info <name>` — show template details
- [x] Built-in templates:
  - [x] `react` — React/Next.js patterns, testing, project setup
  - [x] `python` — Python best practices, testing, packaging
  - [x] `devops` — Docker, Kubernetes, CI/CD, deployment

---

## v0.5.0 — Advanced Search & Recall (DONE)

- [x] Temporal decay: weight recent chunks higher (configurable half-life)
- [x] `engram recall "date query"` — date-aware natural language search
- [x] Cross-project search: `engram search --global "query"`
- [x] `engram similar` — find sessions similar to current work (auto-suggest)
- [x] Chunk quality scoring (length, structure, layer bonuses)
- [x] Code-block-aware chunking (don't split inside fenced blocks)

---

## v0.6.0 — Distribution & Packaging (DONE)

- [x] PyPI package (`engram-memory`) with hatchling build
- [x] Homebrew formula (`Formula/engram.rb`)
- [x] GitHub Actions CI (test on Ubuntu, macOS; Python 3.9/3.11/3.12)
- [x] Release automation (`scripts/release.sh`)
- [x] `npx engram-memory` option for Node.js users
- [x] Shell completions (bash, zsh)

---

## v0.7.0 — Multi-Agent Support (DONE)

- [x] Per-agent session isolation (`engram agent start/end <id>`)
- [x] Shared read, isolated write for active layer
- [x] Conflict detection (`engram agent conflicts`)
- [x] `engram lock <file>` / `engram unlock <file>` for write coordination
- [x] Agent-aware search: `engram agent search <id> "query"`

---

## v0.8.0 — Future Features (DONE)

- [x] Web UI for browsing memory (`engram web`, port 9876)
- [x] Export to Obsidian/Notion format (`engram export-obsidian`)
- [x] PII auto-redaction scanner (`engram pii scan/redact`)
- [x] Embedding model swapping (`lib/embeddings.py` — ollama, openai, cohere)
- [x] Memory compaction (`engram compact` — merge old lossless into summaries)
- [x] `engram diff` — show changes between checkpoints
- [x] `engram forget "topic"` — mark knowledge as superseded

---

## Future Ideas (Unscheduled)

- [ ] Fish shell completions
- [ ] `engram ingest <url|file>` — auto-create semantic pages from external sources
- [ ] Integration with Cursor, Copilot, Aider (beyond Claude Code)
- [ ] Team/org shared memory (git-based sync)
- [ ] Memory analytics dashboard (token usage, knowledge growth)
- [ ] Auto-splitting: detect when a file covers 2+ topics and suggest split
- [ ] Knowledge graph visualization (D3.js force layout of cross-references)
