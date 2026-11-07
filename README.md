# agent_skills
a collection of curated agent skills for personal workflows

# Setup
1. git clone this repo

2. symlink /.claude/skills to the repo (destructive, will replace). Windows will need developer mode on.

   Powershell:
   cmd /c mklink /D "$env:USERPROFILE\.claude\skills" "D:\...\agent-skills"

   OR
   
   ln -s ~/dev/agent-skills ~/.claude/skills

3. turn on the pre-commit hook (once per clone). It blocks commits with a skill that claude.ai's marketplace sync would reject, which `claude plugin validate` doesn't catch: invalid frontmatter YAML, a name that doesn't match its folder or contains "claude"/"anthropic", or a description over 1,024 characters or containing `<` / `>`. Needs ruby (macOS has it built in); without ruby the hook warns and skips the check.

   git config core.hooksPath .githooks

   To check without committing: `ruby .githooks/check-skills.rb`

# Templates
[templates/](templates/) holds starter files to copy into the root of any new project.
Copy `AGENTS.md` and `CLAUDE.md` together so the `@AGENTS.md` import in `CLAUDE.md` resolves.
`AGENTS.md` is the single source of truth for agent rules shared across agent tools; `CLAUDE.md` is just a pointer that imports it, since Claude Code reads `CLAUDE.md` rather than `AGENTS.md`.
See [templates/README.md](templates/README.md) for details.
