# Engram

**Persistent 5-layer memory system for Claude Code.** Gives your AI assistant cross-session recall using local semantic embeddings and structured knowledge layers.

```bash
# Install
curl -sSL https://raw.githubusercontent.com/YOUR_USER/engram/main/install.sh | bash

# Initialize in any project
engram init

# Start a session (loads relevant past context)
engram start "implementing auth middleware"

# Checkpoint every 30 minutes (preserves session history)
engram end "added JWT validation and refresh token flow"

# Search past knowledge
engram search "how did we handle rate limiting"
```

## Why Engram?

Claude Code's built-in memory (`MEMORY.md`) is a single flat file limited to 200 lines. Engram replaces it with a **structured, searchable, multi-layer system** that:

- **Remembers across sessions** — semantic search finds relevant past work automatically
- **Never forgets** — lossless session logs preserve every decision and outcome
- **Transfers knowledge** — sync learnings between projects via shared pools
- **Works offline** — runs entirely local with Ollama (no API keys, no cloud)
- **Degrades gracefully** — falls back to keyword search if Ollama is unavailable

## Architecture

```
.claude/memory/
├── active/              # Layer 5: Today's working context (mutable)
│   ├── current-tasks.md
│   └── context-inject.md    ← auto-populated by `engram start`
├── semantic/            # Layer 3: Distilled facts & patterns (searchable)
├── procedural/          # Layer 4: Workflows, standards, how-tos
├── lossless/            # Layer 2: Raw session transcripts (append-only)
└── .cache/              # Embedding cache (auto-managed, gitignored)
```

**Layer 1** is your project's `CLAUDE.md` — always active, highest priority.

### Retrieval Priority

1. **Active** — check today's tasks and auto-injected context first
2. **Semantic** — search distilled facts via embeddings
3. **Procedural** — find workflows and step-by-step guides
4. **Lossless** — dig into raw session history for exact decisions

## Installation

### Prerequisites

- **Required**: Python 3.9+, ripgrep (`rg`)
- **Recommended**: [Ollama](https://ollama.com) with `nomic-embed-text` for semantic search

```bash
# Install Ollama (if you want semantic search)
curl -fsSL https://ollama.com/install.sh | sh
ollama pull nomic-embed-text

# Install Engram
git clone https://github.com/YOUR_USER/engram.git ~/.engram
cd ~/.engram && bash install.sh
```

### What `install.sh` does

1. Symlinks `engram` CLI to `~/.local/bin/engram`
2. Creates `~/.config/engram/config.toml` (if not exists)
3. Verifies dependencies (Python, ripgrep, optionally Ollama)

## Usage

### Initialize a Project

```bash
cd ~/my-project
engram init
```

This creates:
- `.claude/memory/{active,semantic,procedural,lossless}/`
- `.claude/scripts/engram-*` (symlinks to global install)
- Appends Engram protocol to `CLAUDE.md` (if not already present)

### Initialize with a Template

```bash
engram init --template d365    # Seeds D365 F&O knowledge
engram init --template react   # Seeds React patterns (community)
```

Templates pre-populate `semantic/` and `procedural/` with domain knowledge.

### Session Workflow

```bash
# Start of session — loads relevant past context
engram start "topic you're working on"

# ... work with Claude Code ...

# Every 30 minutes — checkpoint your progress
engram end "summary of what was accomplished"

# Search past knowledge anytime
engram search "query" [--chunks] [--json]
```

### Sync Knowledge Between Projects

```bash
# Push learnings to a shared pool
engram sync . ~/.engram/pools/my-domain

# Pull shared knowledge into current project
engram sync ~/.engram/pools/my-domain .

# Preview what would change
engram sync ~/old-project ~/new-project --dry-run
```

### Configuration

```toml
# ~/.config/engram/config.toml

[embedding]
provider = "ollama"              # ollama | none
model = "nomic-embed-text"       # any Ollama embedding model
url = "http://127.0.0.1:11434"   # Ollama API endpoint
max_chars = 1800                 # max text per embedding call

[search]
file_threshold = 0.18            # cosine similarity for file-level matches
chunk_threshold = 0.25           # cosine similarity for chunk-level matches
chunk_lines = 200                # files larger than this get chunked
max_results = 5                  # top N results per category

[session]
checkpoint_minutes = 30          # reminder cadence for engram end
auto_index = false               # auto-index into external vector DB
```

## How Search Works

Engram uses a **two-pass search** strategy:

1. **File-level pass** — embeds each markdown file (first 2000 chars), compares against query embedding. Threshold: 0.18 cosine similarity.

2. **Chunk-level drill-down** — for top-5 files over 200 lines, splits at `##`/`###`/`####` headings and compares each chunk. Threshold: 0.25 cosine similarity.

3. **Keyword fallback** — ripgrep for literal matches across all `.md` files.

All embeddings are **cached on disk** with hash validation (MD5 of file size + mtime + content boundaries). Cache invalidates automatically when files change.

## CLAUDE.md Integration

Engram works by adding a protocol section to your project's `CLAUDE.md` that instructs Claude to:

- Check `active/context-inject.md` at session start
- Update `active/current-tasks.md` every 3-4 tool calls
- Distill learnings into `semantic/` after solving problems
- Document workflows in `procedural/` after first success
- Run `engram end` every 30 minutes (lossless checkpoint)
- Never delete memory files (supersede or append with dates)

## Templates

Templates are directories under `~/.engram/templates/` (or the repo's `templates/`). Each contains:

```
templates/my-template/
├── seed.toml           # Template metadata
├── semantic/           # Pre-populated facts
│   └── domain-patterns.md
├── procedural/         # Pre-populated workflows
│   └── common-tasks.md
└── claude.md.snippet   # Text to append to CLAUDE.md
```

### Creating a Template

```bash
# From an existing project's memory
engram template create my-domain

# This exports semantic/ + procedural/ (scrubbed of project specifics)
# into ~/.engram/templates/my-domain/
```

## FAQ

**Q: Does this replace Claude Code's built-in memory?**
A: It complements it. Claude Code's `MEMORY.md` (200 lines) stays as Layer 1. Engram adds 4 more layers with unlimited storage and semantic search.

**Q: What if Ollama isn't running?**
A: Engram falls back to keyword search (ripgrep). You still get context injection and lossless logging — just without semantic ranking.

**Q: How much disk space does it use?**
A: Embedding caches are ~300KB per 100 files. Memory files themselves are plain markdown. A typical project accumulates 1-5MB after months of use.

**Q: Can I use a different embedding model?**
A: Yes. Set `model` in `config.toml` to any Ollama-compatible embedding model. `nomic-embed-text` is recommended for its 384-dim vectors and good performance on code/docs.

**Q: Is my data sent anywhere?**
A: No. Everything runs locally — Ollama embeddings, ripgrep search, file storage. Zero cloud dependencies.

## License

MIT
