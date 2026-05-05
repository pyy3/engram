# Engram Architecture

## Overview

Engram is a 5-layer hierarchical memory system for Claude Code that provides cross-session recall via local semantic embeddings and structured knowledge layers.

```
┌─────────────────────────────────────────────────┐
│  Layer 1: Core Identity (CLAUDE.md)             │  Always active
├─────────────────────────────────────────────────┤
│  Layer 2: Lossless (timestamped chunks)         │  Append-only
├─────────────────────────────────────────────────┤
│  Layer 3: Semantic (distilled facts)            │  Searchable
├─────────────────────────────────────────────────┤
│  Layer 4: Procedural (workflows, how-tos)       │  Searchable
├─────────────────────────────────────────────────┤
│  Layer 5: Active (today's context)              │  Mutable
└─────────────────────────────────────────────────┘
```

## Data Flow

```
Session Start                     During Work                    Session End
─────────────                     ───────────                    ───────────
engram start "topic"              Claude works...                engram end "summary"
       │                                │                              │
       ▼                                ▼                              ▼
┌─────────────┐                 ┌─────────────┐              ┌─────────────┐
│ Embed query │                 │ Update      │              │ Write       │
│ Search mem  │                 │ active/     │              │ lossless    │
│ Write inject│                 │ tasks       │              │ chunk       │
└─────────────┘                 └─────────────┘              └─────────────┘
       │                                │                              │
       ▼                                ▼                              ▼
context-inject.md              current-tasks.md              YYYY-MM-DD_HHMM.md
(auto-loaded by Claude)        (progress tracking)           (permanent record)
```

## Search Algorithm

### Two-Pass Strategy

**Pass 1 — File-level scoring:**
1. Embed query via Ollama (`nomic-embed-text`, 384 dimensions)
2. Compare against cached file-level embeddings (first 2000 chars of each file)
3. Keep files scoring above threshold (default: 0.18 cosine similarity)
4. Sort by score descending

**Pass 2 — Chunk-level drill-down:**
1. For top-5 files over 200 lines: split at `##`/`###`/`####` headings
2. Each chunk includes parent heading context (breadcrumb) for self-contained semantics
3. Embed each chunk and compare against query
4. Keep chunks scoring above threshold (default: 0.25 cosine similarity)
5. Return top-N chunks ranked by score

**Keyword fallback:**
- ripgrep for literal query matches across all `.md` files
- Always runs alongside semantic search
- Catches cases where embeddings miss literal terminology

### Chunking Strategy

Files are split at markdown headings (`##`, `###`, `####`):

```markdown
## Database Setup              ← chunk boundary
Content about database...

### PostgreSQL Configuration   ← chunk boundary (child of "Database Setup")
Specific PostgreSQL content...

## Authentication              ← chunk boundary (new top-level section)
Content about auth...
```

Each chunk gets a **context breadcrumb** from parent headings:
- "Database Setup > PostgreSQL Configuration"

This makes chunks self-contained for embedding — they carry their own context.

### Caching

All embeddings are cached to disk with hash validation:

**File-level cache**: `.cache/_file_embeddings.json`
- Key: relative file path
- Value: `{hash, embedding}`
- Hash: MD5 of (file size + mtime_ns + first 4KB + last 4KB)

**Chunk-level cache**: `.cache/{safe_filename}.chunks.json`
- Contains: `{hash, chunks: [{heading, context, text, line, embedding}, ...]}`
- Invalidated when file hash changes

Cache hit = 0ms. Cache miss = one Ollama API call (~50-200ms per chunk).

## Memory Layers in Detail

### Layer 1: Core Identity (CLAUDE.md)

The project's instruction file. Contains:
- Memory protocol rules
- Retrieval priority
- Update cadence requirements
- Project-specific conventions

Always loaded by Claude Code — no search needed.

### Layer 2: Lossless (Append-Only Transcripts)

**Path**: `memory/lossless/YYYY-MM-DD_HHMM.md`

Each file is a self-contained checkpoint containing:
- Timestamp and summary
- Snapshot of current tasks at that moment
- List of memory files changed since last checkpoint

Never modified after creation. Never deleted.

Use when: you need exact recall of a past session's state or decisions.

### Layer 3: Semantic (Distilled Facts)

**Path**: `memory/semantic/*.md`

Contains facts, patterns, insights, and reference material distilled from work sessions. Examples:
- API endpoint patterns that work
- Error messages and their solutions
- Architecture decisions and rationale
- External service behaviors observed

Files are organized by topic, not by date.

### Layer 4: Procedural (Workflows)

**Path**: `memory/procedural/*.md`

Contains step-by-step processes, standards, and how-to guides. Examples:
- Deployment procedures
- Code review checklist
- Setup guides for development environments
- Testing workflows

Distinct from semantic: procedural = "how to do X", semantic = "what X is / what we know about X".

### Layer 5: Active (Today's Context)

**Path**: `memory/active/`

Mutable working memory:
- `current-tasks.md` — what's done, in progress, and blocked
- `context-inject.md` — auto-populated by `engram start` (the "recall" mechanism)

Overwritten each session. Not meant for long-term storage.

## Knowledge Pools & Sync

Engram supports **shared knowledge pools** — directories of semantic/procedural files that can be synced across multiple projects.

```
~/.engram/pools/
├── web-development/
│   ├── semantic/
│   │   ├── css-patterns.md
│   │   └── api-conventions.md
│   └── procedural/
│       └── deployment-workflow.md
└── data-engineering/
    ├── semantic/
    └── procedural/
```

**Sync rules:**
- New files at source → copied to target
- Newer files at source → overwrite target
- Files only at target → kept (never deletes)
- Cache → invalidated at target (forces rebuild)

## File Sizes & Performance

| Operation | Typical time | Notes |
|-----------|-------------|-------|
| `engram start` | 0.5-2s | Depends on file count + cache state |
| `engram end` | <200ms | File I/O only |
| `engram search` (cached) | <500ms | All embeddings from cache |
| `engram search` (cold) | 5-30s | First run builds all embeddings |
| `engram sync` | 1-10s | Depends on file count |

Typical memory footprint after months of use:
- Markdown files: 1-5 MB
- Embedding cache: 5-30 MB (proportional to file count)
- Total: well under 50 MB for most projects
