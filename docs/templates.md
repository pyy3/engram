# Creating Templates

Templates let you pre-seed projects with domain-specific knowledge.

## Template Structure

```
templates/my-template/
├── seed.toml              # Required: template metadata
├── claude.md.snippet      # Optional: text to append to CLAUDE.md
├── semantic/              # Optional: pre-seeded facts
│   ├── domain-patterns.md
│   └── common-issues.md
└── procedural/            # Optional: pre-seeded workflows
    ├── setup-guide.md
    └── deployment.md
```

## seed.toml Format

```toml
[meta]
name = "my-template"
description = "Brief description of what this template provides"
version = "0.1.0"

[meta.tags]
domain = "web"
language = "typescript"
framework = "nextjs"
```

## Usage

```bash
# Initialize with template
engram init --template my-template

# Templates are searched in:
# 1. ~/.engram/templates/<name>/
# 2. <engram-install>/templates/<name>/
```

## Writing Good Template Knowledge

### Semantic files should contain:
- Patterns that work in this domain (with examples)
- Common pitfalls and their solutions
- Architecture decisions and trade-offs
- Tool/framework behaviors observed empirically

### Procedural files should contain:
- Step-by-step workflows (numbered steps)
- Setup guides with exact commands
- Troubleshooting decision trees
- Checklists for common operations

### Rules for template content:
- Use placeholders for project-specific values: `<PROJECT_NAME>`, `<COMPANY>`, `<API_URL>`
- Keep files focused on one topic each
- Include "last verified" dates for time-sensitive content
- Avoid opinions — state facts and observed behaviors
- Never include secrets, credentials, or PII

## Sharing Templates

Templates can be distributed as:
1. Directories within the engram repo (`templates/`)
2. Standalone git repos (clone into `~/.engram/templates/`)
3. Tarballs (extract into `~/.engram/templates/`)

Community templates welcome via PR to the main repo.
