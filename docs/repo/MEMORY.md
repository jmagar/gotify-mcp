# Memory Files — gotify-mcp

Claude Code memory system for persistent knowledge across sessions.

## What is memory

Memory files are persistent, file-based knowledge that Claude Code retains across conversation sessions. They store project decisions, user preferences, external system pointers, and learned corrections.

## Location

Memory files live in the `.claude/memory/` directory at the project root:

```
gotify-mcp/
└── .claude/
    └── memory/
        ├── MEMORY.md              # Index file (pointer list)
        └── *.md                   # Individual memory files
```

## Memory types

| Type | Prefix | Purpose | Example |
| --- | --- | --- | --- |
| `user` | `user_` | User-specific info | Preferences, team context |
| `feedback` | `feedback_` | Corrections and learned behaviors | "Always use uv, not pip" |
| `project` | `project_` | Project decisions and architecture | Dual-token model, FastMCP choice |
| `reference` | `reference_` | External system pointers | Gotify API quirks |

## When to save

Save memory when encountering:

- Project architecture decisions
- External system behavior not documented elsewhere
- Corrections to previous behavior
- Non-obvious conventions

## When NOT to save

- Code patterns visible in the codebase
- Information already in `CLAUDE.md` or documentation
- Temporary debugging state
- Git history facts

## Memory vs other persistence

| Mechanism | Scope | Lifetime | Use for |
| --- | --- | --- | --- |
| Memory files | Project-wide | Permanent | Decisions, preferences |
| `CLAUDE.md` | Project-wide | Permanent | Instructions, conventions |
| Git commits | Project-wide | Permanent | Code history |
| Session context | Single session | Ephemeral | Current task state |
