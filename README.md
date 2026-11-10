# agent_skills
a collection of curated agent skills for personal workflows

each skill lives in `skills/<name>/SKILL.md`. the repo is also a plugin marketplace (`.claude-plugin/`) that claude.ai syncs from, as the `shanaa` plugin.

# Setup
1. on claude.ai, add this repo (`shanaam/agent-skills`) as a plugin marketplace and install the `shanaa` plugin. Claude Code (mac or Windows) downloads it when a session starts, signed in with the same claude.ai account. Skills run as `/shanaa:<skill>`.

   to release a change, raise `version` in `.claude-plugin/plugin.json` (e.g. 1.0.0 → 1.0.1) in the same push; an unchanged version can be treated as nothing new. After the push, claude.ai pulls the repo (automatically, or with Sync), and the next Claude Code session picks up the change.

2. to edit skills, git clone this repo. To try local edits before pushing, load the working copy for one session (it replaces the synced copy):

   claude --plugin-dir ~/dev/agent-skills

   older setups symlinked ~/.claude/skills into this repo. Remove only the link, and Claude Code recreates the folder:

   mac: `rm ~/.claude/skills`
   Windows: `cmd /c rmdir "%USERPROFILE%\.claude\skills"` (not `Remove-Item -Recurse`, which can delete the repo's files)

3. turn on the pre-commit hook (once per clone). It blocks commits with a skill that claude.ai's marketplace sync would reject, which `claude plugin validate` doesn't catch: invalid frontmatter YAML, a name that doesn't match its folder or contains "claude"/"anthropic", or a description over 1,024 characters or containing `<` / `>`. It also blocks changes to `skills/` unless `version` in `.claude-plugin/plugin.json` is higher than in the last push (one bump per push; `git commit --amend` is fine). Needs ruby (macOS has it built in); without ruby the hook warns and skips the checks.

   git config core.hooksPath .githooks

   To check without committing: `ruby .githooks/check-skills.rb`

# Templates
[templates/](templates/) holds starter files to copy into the root of any new project.
Copy `AGENTS.md` and `CLAUDE.md` together so the `@AGENTS.md` import in `CLAUDE.md` resolves.
`AGENTS.md` is the single source of truth for agent rules shared across agent tools; `CLAUDE.md` is just a pointer that imports it, since Claude Code reads `CLAUDE.md` rather than `AGENTS.md`.
See [templates/README.md](templates/README.md) for details.
