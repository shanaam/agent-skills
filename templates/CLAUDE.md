# CLAUDE.md

The AI-agent conventions for this repo live in [AGENTS.md](AGENTS.md), which is the single source of truth shared across agent tools.
Claude Code reads `CLAUDE.md` (not `AGENTS.md`), so this file imports it.
The line below pulls the full contents of `AGENTS.md` into context at session start:

@AGENTS.md
