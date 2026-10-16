# Agent rules

These rules apply to all AI-agent work on this machine, in every repository.

## Writing style

- Do not use em-dashes.
  Use regular dashes (-) instead.

## Git

- Never commit to git.
  The author will always commit and push themselves.
- Never include the LLM as an author or co-author in commit messages (no "Co-Authored-By: Claude" trailers or similar).
  This applies even when only drafting a commit message for the author to use.

## If this is a Windows machine

The agent's environment says which platform it runs on; this section applies on native Windows only, not on macOS, Linux, or WSL2.

- The author's terminal is Windows PowerShell 5.1.
  Every command written for the author to run goes in PowerShell syntax, never Bash: `$Var = command` to capture output, `foreach ($x in @(...)) { ... }` for loops, `;` to chain, and no `&&`, `||`, `export`, or `$(...)` substitution.
- Quote `--query` and shorthand arguments with double quotes, and pass file arguments as `file://path/with/forward/slashes`.
- Say when a red `NativeCommandError` is only PowerShell echoing a native command's stderr, so the author checks the result instead of retrying.
- Agent tool calls may still use Bash or PowerShell, whichever the tool is; this rule is about what the author is asked to type.

## Markdown files

- When creating ANY markdown file, keep each sentence on its own line.
- The important part: never start a new line mid-sentence.
  Hard-wrapping inside a sentence often leads to ugly rendering.

## Planning

- Never estimate time costs for implementing plans and features.

## Compact Instructions

- When compacting, keep the path of any implementation plan in play, the phase just closed, and the next task.
- Keep the modified files and the branch, the test commands with their last counts, the design decisions stated exactly, what was tried and set aside, and the items awaiting the author.
