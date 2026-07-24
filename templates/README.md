# Templates

Starter files to copy into the root of a new project.

- [AGENTS.md](AGENTS.md): baseline agent rules, the single source of truth shared across agent tools.
- [CLAUDE.md](CLAUDE.md): a pointer file that imports `AGENTS.md`, since Claude Code reads `CLAUDE.md` rather than `AGENTS.md`.

Copy both files together so the `@AGENTS.md` import in `CLAUDE.md` resolves.
Device-level versions of the same rules live in `~/.claude/` (there the import is `@~/.claude/AGENTS.md`).
