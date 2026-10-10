---
name: plan-execution
description: Executes an existing implementation plan in Claude Code: the session startup routine, model and effort choice per phase, when to fan out subagents or worktrees, test-integrity and evidence rules, checking tasks off with deviations, the verification phase, and the hand-off. Use whenever the user asks to execute, continue, resume, or pick up an implementation plan or one of its phases ("run the plan", "do phase 3", "continue where the last session left off", "the plan at the repo root"), whenever a session opens with a `*_implementation_plan.md` to act on, and when the user asks which model, effort, or how many agents a phase should use. Pairs with the architecture-codesign skill, which writes the plan; this skill reads it. Not for designing the plan, and not for one-off tasks that have no plan.
---

# Plan execution

An implementation plan is the state of the work: a later session reads it cold and continues without the conversation that produced it.
This skill is how a session turns that file into landed, verified work and leaves the file truthful for the next session.
The plan's shape is defined by the architecture-codesign skill; its skeleton is in [../architecture-codesign/references/implementation-plan-template.md](../architecture-codesign/references/implementation-plan-template.md), and reading it once makes every section name below concrete.

## When this applies

- A plan exists, normally `<descriptive_name>_implementation_plan.md` at the repository root, gitignored.
- If no plan exists and the change can be described in one sentence, do the change; if it cannot, the architecture-codesign skill comes first.
- If the user names a phase or a task, start there; otherwise the next unchecked item in order.

## Session startup, every time

Do these before touching code, in this order, because each one has caught a session acting on a stale picture:

1. Read the plan's Design decisions, Hand-off, ADR-gate findings, and conventions block.
   The design decisions are settled; do not re-open one unless the user does.
2. Run `git status` and the recent log and compare them with the hand-off's description of the tree.
   The author or a peer session may have moved it; if there are unstaged changes the hand-off does not mention, read that diff before anything else and build on it rather than redoing it.
3. Run the repo's setup or smoke recipe, then the suites the plan's Phase 0 baseline names (the fast lane when the full run is slow), and note the counts; a regression later is only recognisable against this.
4. Claim the task: mark it in progress in the plan before starting, which is also how parallel sessions avoid colliding on a parallel-safe task.
5. Say in one line what the next task is and which model and effort fit it (table below), so the user can switch the session model before the work starts.

## Model and effort

The agent cannot change the session's model; it recommends and the user switches with `/model`.
The agent does choose models for subagents through the Agent tool's `model` parameter.
Judge cost per completed task, not per request: a cheaper model that needs a retry and a review round is the expensive one.

| Work in the phase | Session model | Effort | Why |
|---|---|---|---|
| ADR-gate findings, the riskiest-assumption spike, a re-plan checkpoint, anything that touches a design decision | Fable | `xhigh`, `max` when correctness outranks cost | Judgement work; mistakes here cascade into every later phase |
| Concurrency, real-time or device-facing code, clock and alignment logic, a failing phase being debugged | Fable | `xhigh` | The hardest reasoning per line; Fable's long turns are the point here |
| Feature code with a clear spec and tests in place | Opus | `xhigh` | The default executor; Opus defaults to `medium` effort, so set it explicitly |
| Scaffolding, mechanical migrations, renames, docs, test cleanup, config | Opus, `/fast` for long mechanical runs | `high` | Volume over depth; fast mode is Opus with faster output at a higher per-token price that still sits under Fable |
| The convergence audit and the fresh-eyes verifier | At least the writer's model | `xhigh` | A verifier weaker than the writer misses what the writer missed |

Subagents, through the Agent tool:

| Errand | Model | Effort |
|---|---|---|
| Research fan-out with a narrow brief and a required output shape | Sonnet | `high` |
| Codebase mapping that writes findings to a file (read-only explore) | Sonnet | `medium` |
| File inventories, log triage, bulk classification | Haiku | `low` |
| Verifying another agent's work against the evidence contract | Opus or Fable, never below the writer | `xhigh` |

Model-specific facts worth knowing while executing:

- Fable's single turns on hard tasks can run minutes; that is normal, not a hang, and instructions written for earlier models are often too prescriptive for it, so keep prompts to subagents short and outcome-shaped.
- On Fable, a fresh-context verifier beats self-critique; on Opus, do not spawn subagents to double-check your own work, because it verifies as it goes and over-verifies when told to.
- Effort is set with `/effort <level>`; `xhigh` is the recommended setting for most coding work, `max` for hard debugging or architecture decisions, `low` for a subagent errand.

Revise this section after a model release; it encodes assumptions about model limits that go stale within a generation.

## Parallelism

Review capacity, not generation, is the limit, so parallel work is for what lands as a summary or on independent files.

Fan out when:

- Research threads are independent and each returns a short structured report.
- Codebase mapping would flood the main context; a read-only subagent writes findings to a file.
- A hard task is worth scouting in a scratch worktree without keeping the code.
- Tasks are marked parallel-safe in the plan, which means they touch files no other open task touches.
- Verification needs eyes that did not write the code.

Keep it sequential when:

- Tasks share files or depend on each other's results.
- The work needs the design context that only the main thread holds.
- The user cannot review the output faster than it arrives; keep one landing lane and let the human land one significant change at a time.

Mechanics, as of October 2026:

- A subagent that edits code gets its own worktree (`isolation: worktree` on the Agent tool) and returns one hand-off, not a running commentary.
- Parallel sessions use `claude --worktree <name>`; coordination state lives in the plan file (claimed tasks, in-progress markers), not in commits that trigger CI.
- `/batch` fans one instruction out across many worktree subagents for a large set of similar changes.
- The Workflow tool runs only when the user opts in (the `ultracode` keyword or an explicit ask), and earns its coordination cost on audits, cross-checked reviews, or a plan drafted from several angles, not on ordinary coding.
- Agent teams are experimental and off by default; do not plan around them.
- Many subagents returning detailed results consume the main context; ask each for a bounded summary.

## Execution rules

- Work in small, verified increments: finish a task, run the tests that cover it, check it off with its one-line record, and move on.
  Do not leave a phase half-done without saying so in the plan.
- Treat tests as the contract.
  Tests are there to verify correctness, not to define the solution; never weaken, special-case, skip, or delete one to get green.
  If a test is wrong, or the task as specified cannot be done well, say so in the plan and let the user decide rather than working around it.
  After a few failed attempts at a general fix, stop and report; the special-casing instinct appears exactly there.
- Keep changes and tests to what the task asks for: roughly one focused test per stated behaviour, sized like the neighbouring tests, and no scratch checks promoted to permanent test files.
  Do not add comments, docstrings, type annotations, error handling, or helpers to code the task did not touch.
- Reuse what the plan names under "Reuses" and what the repository already has; search for an existing helper before writing one, because duplication is the most common structural debt agents add.
- Finish any migration a phase starts before the phase closes; a half-migrated codebase confuses humans and agents alike.
- Ground every status claim in a tool result from this session; report only work you can point to evidence for, and say explicitly what is not yet verified.
- Watch for the three derailment signs: looping on the same failure, functionality nobody asked for, and anything that touches a test to make it pass.
  Any of them means stop and report, not push through.
- Queue, do not block.
  Pause only for a destructive or irreversible action, a real scope change, or input only the user can provide; otherwise write the ask under Awaiting the author with everything they need, and continue with what does not depend on it.
- Follow the repo's agent rules as the plan's conventions block restates them: one sentence per line in markdown, no mention of the plan in anything committed, short "why" comments, no commits or pushes, no time estimates.

## Checking off, deviations, and re-planning

- A checked task carries one line under it: what landed, and any deliberate deviation from the task as written, with the reason.
- A decision that changed mid-implementation is updated in Design decisions, not left to drift; the deviation is also listed in the hand-off.
- The riskiest-assumption spike in Phase 0 is a re-plan checkpoint: if it fails, amend the plan before the phase that depended on it, and say what changed.
- A phase the author chose to skip is marked as such with the date, never deleted; a later session may pick it up.
- The plan is the review surface: when it is wrong, fix the plan and rerun rather than patching the code around it.

## ADRs

- The ADR review gate is the first checkbox and is not checked off until the named ADRs have been read; the findings go inline under it.
- Status decides weight: an accepted ADR is binding, a proposed one is context, a superseded one is history.
  When the task and an accepted ADR conflict, stop and raise the choice between changing the task and amending the ADR; do not layer a workaround that keeps both technically true.
- Every phase ends with the ADR check; a change to an accepted decision becomes a dated addendum, a new decision becomes a new ADR with Status: Proposed, numbered at write time after re-reading the index.
- The record carries no agent attribution, and it stays a suggestion until the author has read every line and changed what does not match their reasoning; queue it under Awaiting the author and never move its status.
- Details, including the minimal template and the mistakes to avoid, are in [../architecture-codesign/references/adr-practice.md](../architecture-codesign/references/adr-practice.md).

## Recurring checks

- Run the end-of-phase static-analysis check with the exact tools and commands the plan names: lint and type check as distinct passes, pre-existing errors in touched files cleared too, and the security scan when the phase touches input handling, logging, auth, or crypto.
- Do not suppress a finding to get past the check; if a pre-existing error genuinely should not be fixed here, note why inline.
- Run the suites the phase names and compare with the Phase 0 counts before checking the phase off.

## The verification phase

Green tests are necessary, not sufficient; the plan's verification phase shows the behaviour the design decisions were about.
How to execute it, tool by app type, is in [../architecture-codesign/references/verification.md](../architecture-codesign/references/verification.md); read it when the phase starts.

- Execute the evidence contract as written: the deterministic gate first (the verify recipe that exits non-zero on failure), then the walkthrough as a user with screenshots after each post-condition is reached, then profiles when a hot path changed.
- Drive the walkthrough through the repository's `verify-<app>` skill at `.claude/skills/verify-<app>/`: its Launch, Doctor, Drive, Evidence, and Cleanup sections are the harness, and `features/<feature>.md` is the recipe for each changed journey.
  When none exists, the plan's Phase 0 task creates one with the sibling `create-verification-skill` before the phase continues, and the docs phase updates the feature file of every feature the plan changed.
- Run the convergence audit against Design decisions and append each gap as a task, classified missing, partial, contradicting, or unrequested, rather than fixing it silently.
- Spawn the fresh-eyes verifier with the diff, the evidence contract, and the evidence folder, on a model at least as capable as the writer, told to flag only gaps that affect correctness or the stated requirements, and forbidden from editing code or tests.
- Write the human test into the hand-off last: one to three commands, each with what to expect and the single observation that means it passed, and say what the agent could not verify.

## Unattended runs

Most execution is interactive; when a phase runs without a human watching, bound it:

- Turn the phase's "unattended run condition" into a `/goal`: one measurable end state, the check that shows it, and the constraints that matter (for example "no other test file is modified"), with a turn cap.
  The goal's evaluator reads the transcript, not the disk, so pair it with the verify recipe as the real gate.
- A Stop hook that runs the verify recipe is the deterministic version; use it for anything that must be true on disk.
- Headless runs use `claude -p`; not `--bare`, which skips skills, hooks, and CLAUDE.md.
- List which steps need a screen (a browser extension, computer use, a Windows window capture) and leave those for an interactive session.

## Context hygiene

- Prefer a fresh session per phase over a long compacted one; the plan and the tree are the state, and a fresh session rediscovers them reliably.
- After two failed corrections on the same issue, `/clear` and restart with a more specific prompt rather than a third correction.
- If compaction happens, the summary must keep the modified files, the test commands, the decisions stated exactly, what was tried and set aside, and the open items.
- Add a line to a rules file (AGENTS.md, CLAUDE.md) only for a bad behaviour actually observed, as a proposal under Awaiting the author, and turn anything that must always happen into a hook or a lint rule rather than a sentence.
- Keep subagent returns short and in the shape you asked for; verbose returns are the main way a planning context fills.

## Ending the session

Leave the tree runnable and the plan truthful:

- Rewrite the Hand-off section to the current state: the branch and what is uncommitted, what must be rebuilt before the next session can run the code, the evidence index when verification ran, the human test, the author's manual checks with expected outcomes, Awaiting the author (approvals, commits, hardware), deviations, and harness notes.
- Harness notes record what the agent got wrong this session and which guide or sensor would have caught it, so the next session starts from a better harness.
- Update the memory file for this work if one exists: the settled design, the progress, and a "how to apply" line naming what a later session must not re-open.
- No commits or pushes; the author commits, and any file that belongs in its own commit (a lockfile, a generated artifact) is named in the hand-off.
- End the turn with what was done, what was verified, and what is queued, in that order, and nothing promised for later.

## Anti-patterns

- Starting to code before reading the hand-off and running `git status`.
- Re-opening a design decision the plan records as settled.
- Checking a task off without its one-line record, or without running the tests that cover it.
- A green suite reached by editing a test, skipping one, or special-casing an input.
- Tests or helpers added for cases the task did not ask for.
- Fanning out subagents for sequential, same-file, or design-dependent work.
- Verifying your own work with a subagent on Opus, or skipping the fresh-eyes verifier on Fable.
- A status report with claims that no tool result in the session supports.
- Blocking on an approval that could have been queued.
- A hand-off that describes the tree as it was at the start of the session.
- Any commit or push.

## Reference files

All live in the architecture-codesign skill, which writes the plans this skill executes:

- [../architecture-codesign/references/implementation-plan-template.md](../architecture-codesign/references/implementation-plan-template.md): the plan skeleton; read once per session to know the sections.
- [../architecture-codesign/references/adr-practice.md](../architecture-codesign/references/adr-practice.md): the gate, addenda, numbering, status, and the no-attribution rule; read at the gate and at every ADR check.
- [../architecture-codesign/references/verification.md](../architecture-codesign/references/verification.md): tools per app type, evidence conventions, the fresh-eyes brief, the human test; read when the verification phase starts.
- [../architecture-codesign/references/diagrams.md](../architecture-codesign/references/diagrams.md): read when a phase moves a diagram into a doc.
- The sibling `create-verification-skill`: generates the `verify-<app>` skill and feature map the verification phase drives through; invoke it when a plan's Phase 0 finds none.

## Maintaining this skill

The model and effort table and the parallelism mechanics are the parts that go stale first.
Revisit both after a model release and every few months against the current Claude Code docs, remove what the model now does unprompted, and keep the table as the single place model choice is written down.
