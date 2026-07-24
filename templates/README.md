# Templates

Starter files to copy into the root of a new project.

- [AGENTS.md](AGENTS.md): baseline agent rules, the single source of truth shared across agent tools.
- [CLAUDE.md](CLAUDE.md): a pointer file that imports `AGENTS.md`, since Claude Code reads `CLAUDE.md` rather than `AGENTS.md`.

Copy both files together so the `@AGENTS.md` import in `CLAUDE.md` resolves.

## Device-level rules

To apply the same rules to every project on a machine, drop copies into Claude Code's user config directory.
Use the absolute import `@~/.claude/AGENTS.md` in the device-level `CLAUDE.md` (a bare `@AGENTS.md` only resolves relative to a project).

The config directory location depends on the OS:

- Linux / WSL2 / macOS: `~/.claude/` (i.e. `$HOME/.claude/`).
- Windows (native, PowerShell/CMD): `%USERPROFILE%\.claude\` (i.e. `$env:USERPROFILE\.claude\`).

On WSL2 use the Linux path (`~/.claude/`), not the Windows one.
The two environments have separate home directories, so a WSL2 session and a native-Windows session read different config directories even on the same machine.

Then copy the files in:

```sh
# Linux / WSL2 / macOS
mkdir -p ~/.claude
cp AGENTS.md CLAUDE.md ~/.claude/
```

```powershell
# Windows (native)
New-Item -ItemType Directory -Force "$env:USERPROFILE\.claude" | Out-Null
Copy-Item AGENTS.md, CLAUDE.md "$env:USERPROFILE\.claude\"
```

Remember to change the import line in the device-level `CLAUDE.md` to `@~/.claude/AGENTS.md`.
