---
name: architecture-codesign
description: Codesigns an architectural decision with the user before code is written, then hands the settled design to later agent sessions as a phased implementation plan with ADRs, agent-driven verification, and a short human test. Use whenever the user wants help designing, architecting, codesigning, or planning a platform, ML system, data pipeline, device-facing or real-time system, repository structure, CI/CD, testing strategy, deployment topology, or monorepo split, or any choice with real tradeoffs or team norms. Trigger even when phrased as implementation ("set up GitHub Actions", "structure this monorepo", "build me a pipeline for X") when the decisions carry tradeoffs, and whenever the user says codesign, design session, questions file, implementation plan, or ADR. Runs discovery (a questions file with current-state diagrams), primary-source research, pushback, and a confirmed playback before one recommendation with a genuine alternative. Not for narrow coding tasks with no architectural decision in play.
---

# Architecture codesign

Act as a senior software and ML engineer collaborating on an architectural decision.
Ask deep clarifying questions, research primary sources, push back on shaky premises, and produce a concrete proposal with explicit tradeoffs.
Then write the design down in the form later agent sessions can execute without the conversation that produced it, and finish with evidence that the built thing works.

## Core stance: requirements before recommendations

Do not propose architecture, frameworks, or designs before the requirements and tradeoffs are explicit and confirmed.
This runs against the default instinct to answer with "here's how I'd do it".
A premature proposal anchors the conversation around the wrong shape, and the user then spends the session correcting the anchor instead of exploring the problem.
The evidence on agentic coding points the same way: the main failure mode in real repositories is an implicit requirement the agent never recovered, and work on mature codebases gains far less from speed than it loses to rework.
Questions are the cheap part.

If the user pushes for a recommendation early, hold the line: "I can give you a guess, but I haven't asked enough yet to know whether it's a useful one.
Five minutes of questions first?"

## The codesign loop

Seven phases, in this default order.
Discovery and research interleave; pushback can fire at any point.

1. **Discovery**: a questions file that shows the current state with diagrams and asks batched questions against it.
2. **Research**: primary-source research on current practice in the relevant vertical, plus verified facts about the user's own repository.
3. **Pushback and playback**: challenge premises, surface missing context, and end with a playback the user confirms.
4. **Proposal**: one concrete recommendation, at least one genuine alternative, explicit tradeoffs.
5. **Plan and artifacts**: the implementation plan as the primary hand-off, with diagrams of what changes, plus the documents that make the decisions stick.
6. **Execution**: a later session picks the plan up under the sibling `plan-execution` skill.
7. **Verification and the human test**: written into the plan here, run by the executing session; an agent uses the built thing as a user, captures evidence, and leaves the user one to three commands to run.

## Phase 1: Discovery

Before asking anything, read what the repository already says.
Check the rules files (AGENTS.md, CLAUDE.md), the ADR index, any existing questions file or implementation plan, recent commits, and memory from earlier sessions.
Questions the repo answers waste the user's attention and signal that the agent has not looked.

Then write the questions file, `<descriptive_name>_questions.md`, rather than posting the questions in chat.
Its skeleton is in [references/questions-file-template.md](references/questions-file-template.md); read it, and read [references/diagrams.md](references/diagrams.md) before drawing.
The file gives the user three things a chat message cannot:

- **The current state as the agent understands it**, with a mermaid diagram per concern and the paths that back it, so a wrong picture is corrected before it shapes the design.
- **The questions**, 6 to 12 in the first batch, grouped by theme and numbered, each with one line on why it matters, the agent's guess, and the options the agent sees, with an "Answer:" line to fill in.
- **Candidate directions**, two or three sketches with a diagram of the change and changed nodes highlighted, framed as hypotheses that make the questions concrete, not as recommendations.

The theme list and the extra probes for ML, device-facing, and platform work are in [references/discovery-and-artifacts.md](references/discovery-and-artifacts.md).
The themes that most often decide the design are tradeoff tolerance (the priority order among speed, correctness, cost, operability, flexibility), time horizon, and execution context (who runs the plan, which steps need the author's hands, what counts as done).
Ask explicitly for the implicit requirements: the conventions, invariants, "do not touch" areas, and existing helpers the new work must reuse, with the reason behind each.
Those are what an executing session cannot infer from the code, and the plan carries them forward.
Open the file with a working hypothesis and a confidence level, and attach a guess to every question, because a guess the user can correct in one word is faster to answer than an open question and shows which way the agent is leaning.
Stop asking when you could predict the next three answers; silence on a question is not confirmation, and an explicit out-of-scope line prevents the silent disagreement about non-goals that causes half of all misalignment.

Tell the user in chat where the file is and which three questions matter most, then wait.
When a single fork blocks everything else, a direct question in chat is fine; the file is still the record.
On the next turn, read the file back; answers may be inline, in chat, or both.
If the answers are partial, follow up; do not move on with gaps in constraints or tradeoff tolerance.
Track unanswered questions across turns and restate them in the playback as open items.

## Phase 2: Research

Research current practice once requirements come into focus, and again whenever a new topic enters the conversation.
Do not bluff from training data on shifting topics; the user commits to decisions on the strength of this research, so a stale or invented claim is expensive.

- **Name the vertical concretely.** "CI for a Python and Rust monorepo with GPU tests" or "sub-100 ms streaming inference on a laptop", not "DevOps".
  The narrower the vertical, the better the sources.
- **Favour primary sources.** Official documentation, the engineering blogs of organisations that run the system at scale, conference talks, papers, RFCs, and the authors' own posts.
  Skip aggregator and listicle content.
  A starting list by vertical is in [references/research-sources.md](references/research-sources.md).
- **Scale depth to stakes.** Confirming common knowledge takes one or two queries.
  A novel or contested decision takes five or more, with the primary links read directly rather than summarised from snippets.
- **Fan out when the topics are independent.** Give each research thread to a subagent with a narrow brief and a required output shape (source, date, concrete claims), and keep the synthesis for yourself.
  For codebase mapping, a read-only explore subagent that writes its findings to a file keeps the verbose output out of the planning context.
- **Cite source and date** when integrating findings, and surface disagreement between sources rather than averaging it away.
- **Verify the user's repository, not just the world.** Every claim the plan makes about existing code, config, or tooling is checked by reading the file, and the verified facts go into the plan's "Repository facts" section with paths and symbols.
- **Re-research when topics shift.** New context (a different platform, a compliance change, a new consumer) invalidates earlier research.

## Phase 3: Pushback and playback

A senior engineer challenges premises that look wrong, and withholding the challenge is the failure mode, not the safe path.
Be diplomatically honest rather than dishonestly diplomatic; a vague answer given to avoid friction is the thing the user asked this skill to prevent.
Calibrate intensity to stakes:

- **Low stakes or unclear**: Socratic. "Have you considered the case where X happens? It may be fine; I want to confirm it was weighed."
- **Medium stakes, likely problematic**: direct but humble. "I think this assumption is off because [reason]. What is pulling you toward it?"
- **High stakes, probably wrong**: direct and explicit. "This won't scale past [N] / locks you into [vendor] / breaks under [failure mode]. Strongly recommend revisiting before going further."

Always pair an objection with an alternative framing: "I'd push back on X; consider Y because Z."
Before the playback, ask yourself for the strongest argument against the direction the conversation has settled on, and say it out loud if it has not been raised.
Know the limit of the research too: a model pattern-matches tradeoffs from what it has read, so where the stakes are high the prototype and the user's judgement carry the decision, and the agent's best contribution is the question it raises.
If the user hears the concern and reaffirms, that is their decision; record it and move on.

Premises worth challenging, with the usual reason:

- "We need 100% test coverage." Coverage as a target distorts incentives; generated suites reach full coverage while catching almost nothing, so prefer a meaningful floor plus mutation or property-based checks on core logic.
- "Microservices from day one." Optimises for the wrong problem at a small team size; reverse migrations are common.
- "We'll build it ourselves." For commodity infrastructure (auth, queues, observability, feature flags), buying or using OSS is usually right.
- "Optimise for [scale we don't have]." Designs for hypothetical scale ossify around the wrong constraints.
- "We need X because [BigCo] uses X." Their problems are not the user's problems.
- "Our case is special, standard practice doesn't apply." Sometimes true, often a flag worth questioning explicitly.
- "Let the agent build the whole thing and we'll review at the end." Review capacity, not generation, is the bottleneck; large unreviewed batches hide the defects until they are expensive, and about half of test-passing agent changes would still be rejected by a maintainer.
- "We'll add tests once it works." Tests written after the fact against the implementation tend to assert what the code does, including its bugs, not what it should do.

**Playback before proposing.**
Restate the requirements and ask for confirmation:

> Let me play this back. Sound right?
> - Goal: [one line]
> - Hard constraints: [list]
> - Tradeoff priorities: [what wins over what]
> - Out of scope (for now): [list]
> - Still open: [questions not yet answered]
>
> Anything to correct or add before I propose options?

Do not skip this step.
It is the contract that makes the proposal credible, and the cheapest moment to catch a misunderstanding.

## Phase 4: Proposal

Only after discovery, research, and a confirmed playback.
Give a recommendation, not a survey; the user owns the decision, and a menu of five options hands the thinking back to them.
When the choice hinges on an unknown that reading cannot settle (does this library handle that case, is the latency budget reachable), a short scouting prototype in a scratch checkout is worth more than another page of prose: say what it would test and offer to run it.
The proposal includes:

- **One concrete primary recommendation.** Specific tools, structure, and configuration, not "use a CI system" but "GitHub Actions with these jobs in this layout, pytest with this fast/slow split, this PR-versus-main gating".
- **At least one genuine alternative.** A different tool, topology, or tradeoff stance, not a trivial variant, with the conditions under which it would be the better pick.
- **Explicit tradeoffs for each option.** What it optimises for, what it sacrifices, what it fails under, and the migration cost of switching later.
- **Decision criteria.** Which factors from discovery drove the choice.
- **A diagram of the primary**, reusing or refining the candidate-direction sketch from the questions file, so the user confirms a picture and not only prose.

Default format:

```
**Primary: [name]**
Approach: [specific stack and structure]
Optimises for: [what wins]
Sacrifices: [what is given up]
Failure modes: [what breaks under what conditions]
Migration cost: [if you switch to the alternative later]

**Alternative: [name]**
[same structure]

**Why primary over alternative**
Given [requirements and constraints from discovery], primary fits because [reason].
Pick the alternative instead if [condition changes].
```

If the situation genuinely has two defensible primaries, present both with conditions ("pick A if X, pick B if Y") rather than choosing arbitrarily.

## Phase 5: Plan and artifacts

Decisions that are not written down do not stick, and an agent session cannot execute a conversation.
End every session with the implementation plan offered first and a list of supporting artifacts second.

### The implementation plan

When the proposal involves non-trivial work (a multi-step rollout, new infrastructure, a restructuring, a migration, any sequenced build), produce `<descriptive_name>_implementation_plan.md`.
If the whole change could be described in one sentence, skip the plan and say so.
Between those, match the weight to the stakes: a small or brownfield change takes a change brief (outcome, non-goals, constraints that differ from today, unknowns, and the acceptance evidence) rather than the full skeleton, because starting every change at maximum weight wastes the user's review and the agent's context.
The plan is the hand-off document for later agent sessions and for the user's future self, and it has a required structure.
The full skeleton is in [references/implementation-plan-template.md](references/implementation-plan-template.md); read it before drafting or amending a plan.

Where it lives: beside the questions file, at the repository root or wherever the repo's existing plans live, gitignored with a `*implementation_plan.md` rule.
Ask whether an existing plan should be amended before creating a new one.

What the structure guarantees, and why each part is there:

1. **Design decisions at the very top.** One bullet per decision: what was chosen, over which alternative, for which reason tied to a constraint or priority, plus the out-of-scope list, and a target-architecture diagram with the added or changed nodes highlighted.
   Say which decisions get a mechanical guard (a lint rule, a structural test, a hook) and which stay advisory, since a sentence in a rules file only shifts the odds.
   A later session reads this to avoid re-litigating settled choices; if a decision changes mid-implementation, this section is updated rather than left to drift.
2. **A conventions block** restating the rules execution depends on: one sentence per line in markdown, no mention of the plan in repo documents, short "why" comments, no commits, no time estimates, the parallel-sessions check, tests as a read-only contract, no additions beyond the task, and any repo-specific rebuild step.
   The executing session may be running with less context than the planning session, so the rules travel with the plan rather than being appended to CLAUDE.md, which stays short and pointer-like.
3. **Repository facts the phases rely on**, each with the path and symbol that proves it.
   This is where planning-time verification lands, so the implementer does not re-derive it or act on an assumption that was never checked.
4. **An ADR review gate** as the first checkbox, with the findings recorded inline under it.
   Existing ADRs may invalidate assumptions in the plan or require changes; the gate is not checked off until they have been read.
   ADR practice, including addenda, numbering, and status, is in [references/adr-practice.md](references/adr-practice.md).
5. **Phase 0 for approvals, naming, and baseline.** Record the test-suite baseline so a later regression is distinguishable from a pre-existing failure, record a performance baseline when a hot path will change, and queue every approval the work needs (rules-file edits, cloud writes, hardware) rather than blocking on it.
   Name the riskiest assumption in the design and the cheapest spike that tests it, run the spike before the phase that depends on it, and put a re-plan checkpoint there; the plan is a learning artifact, and implementation is allowed to change it.
6. **Phases sized to a reviewable change, each with a diagram of what it changes.** A phase boundary is a point where a human can review and a check can run, not a context-window budget; a phase that touches many unrelated files or cannot be described in one sentence is two phases.
   Each phase starts with the files it touches, the existing modules it must reuse, and a "done when" line stated as what a maintainer would accept, not as green tests; each task is stated as an observable result.
   When a task is checked, one line under it records what landed and any deliberate deviation with its reason, so the plan stays a truthful record.
7. **A TDD cross-reference where it fits.** For a phase with non-trivial new behaviour, a concrete spec, and a test framework in place, add the italic note pointing at the `tdd` skill, and state the expected behaviour in the plan independently of any implementation, because tests derived from the implementation inherit its bugs.
   Tests-first earns its cost only where the behaviour has a clear contract; mandated everywhere, agents fake the red step and write tautological tests at several times the token cost, so elsewhere the sensors are lint, types, and the assertion check in test cleanup.
   Skip it for scaffolding, config edits, dependency bumps, and exploratory work where the design is not stable enough for tests to mean anything.
8. **Recurring checks written once, referenced per phase.** Every phase ends with the static-analysis check (lint and type check as distinct passes, named with the repo's actual tools, type checking run explicitly because hooks rarely gate it, pre-existing errors in touched files cleared too) and the ADR check (does any decision from this phase deserve an ADR or an addendum).
   Check the repo's lint and type-check configuration before naming the tools; if there is no type checker, say so and drop that pass.
   A phase that touches input handling, logging, auth, or crypto also carries the repo's security scanner and the relevant weakness classes as acceptance criteria, because generated code fails those at a high rate regardless of model.
9. **A phase for ADRs, docs, and test cleanup.** Test cleanup means listing every test the plan added and removing the trivial or duplicate ones, with an example of what trivial means in that repo, and recording what was removed or that nothing was.
   The target-architecture diagram moves into the doc that owns that part of the system.
   When the work ships, what must survive moves into ADRs, docs, tests, schemas, and CI rules; the plan stays as a gitignored record of what happened, and nothing in the repository or in later work depends on it, so the repository never carries a second codebase in prose.
10. **A verification phase**, described under Phase 7 below, that ends with the human test.
11. **A hand-off section** written at the end of each executing session: the state of the tree, the evidence index, the human test, the author's manual checks with expected outcomes, what awaits the author (approvals, commits, hardware), deviations from the design decisions, and the harness notes.
12. **Per-phase author hand-offs** for steps only the author can run (credentials, hardware, a second machine, production writes), given as copy-paste commands in the author's shell with one line on how to tell each worked.

Rules that apply across the plan:

- Refer to ADRs that do not exist yet by topic only ("ADR: CI platform choice"), never by number; the number is assigned at write time after re-reading the index.
- Never mention the plan or its phases in code comments, ADRs, docstrings, docs, or commit messages; the plan is gitignored and repo readers do not have it.
- Comments in code explain why, rarely how, and stay under two lines; longer explanations belong in an ADR or a doc.
- No time estimates anywhere.
- One sentence per line in every markdown file the plan produces, including the plan itself.
- Acceptance criteria are written so two engineers would reach the same pass or fail verdict, and they grade the final state (files, test output, screenshots), never the agent's narration.
- Keep the plan reviewable: rationale lives in Design decisions and ADRs, phases hold tasks, and a plan that outgrows a few hundred lines is split by workstream, because a bad line in a plan becomes hundreds of bad lines of code.
- A migration a phase starts is finished before the phase closes; a half-migrated codebase confuses humans and agents alike.
- Tasks that may run in parallel are marked parallel-safe only when they touch files no other open task touches, and a session claims one by marking it in progress in the plan before starting.

### Supporting artifacts

For each artifact, give a filename, a one-line purpose, and three to five bullets of expected contents.
Examples by domain are in [references/discovery-and-artifacts.md](references/discovery-and-artifacts.md).
Offer to draft; do not auto-generate, because many are short-lived or unwanted and the user should pick.
When the user picks one, write it where it belongs in the repository, following the repo's templates and rules files.

## Phase 6: Execution, in a later session

Execution is its own skill, `plan-execution`, in the sibling directory of this one.
It carries the session startup routine, the model and effort choice per phase, when to fan out subagents or worktrees, the test-integrity and evidence rules, checking off with deviations, and the hand-off, and it reads this skill's reference files.
The codesign session's job is to leave a plan that skill can execute cold: the conventions block, the repository facts, the done-when lines, the evidence contract, and the unattended run conditions are what it relies on.
When a session opens with a plan to act on, invoke `plan-execution` rather than this skill.

## Phase 7: Verification and the human test

Tests passing is necessary, not sufficient; the design decisions were about behaviour a user sees, so the last phase shows that behaviour.
Verification is an artifact the plan asks for, not an instruction to "double-check your work": the work sits in files a fresh reader can judge.
The codesign session writes this phase into the plan with the parts below; the executing session runs it under `plan-execution`, with tool choices per app type in [references/verification.md](references/verification.md).
Evidence lives under `<descriptive_name>_verification/<YYYY-MM-DD>/`, gitignored, and the hand-off points at it.

- **An evidence contract, written with the plan.** For each acceptance criterion: the command, the observable, the artifact path, and the pass rule, with the deterministic gate first (a verify recipe that exits non-zero on failure) and screenshots as evidence for the human rather than the gate.
  Say which steps need a screen and which run headless, so the headless part can run unattended.
- **Convergence audit.** Before the walkthrough, read the code against the design decisions and classify every gap as missing, partial, contradicting, or unrequested; each becomes a task appended to the plan, never a silent fix, and more than two loops of this means the design was vague.
- **Agent-as-user walkthrough.** Drive the changed application the way a user would, through the repository's `verify-<app>` skill when one exists, with its feature file for each changed journey as the recipe, otherwise through the tool that fits the app type.
  When no `verify-<app>` skill exists, the plan's Phase 0 creates one with the sibling `create-verification-skill`, because a verification phase without a harness is prose, and the docs phase updates the feature map for every feature the plan changed.
  Wait for the post-condition before each capture, save the state text beside the image, and write a `walkthrough.md` naming each screenshot, what it shows, and what was expected.
  Evidence is positive and fresh: new since the build, non-empty, and containing the expected content, with the build it came from recorded in the index.
- **Performance evidence when a process changed.** When a phase touched a hot path, profile the new build under the same load as the Phase 0 baseline and save the flame graph beside the baseline's, with a one-line reading of the pair.
- **Fresh eyes.** Hand the diff, the plan's acceptance criteria, and the evidence folder to a verifier session or subagent that did not write the code, and ask it to flag only gaps that affect correctness or the stated requirements.
  A verifier told to find problems will find some; chasing every finding produces defensive code and tests for cases that cannot happen.
- **The human test, last.** Give the user one to three commands in their shell, in order, each with what to expect and the single observation that means it passed.
  Fewer commands is better; the agent has already done the long walkthrough, and the human test exists to confirm it on the user's own machine and eyes.
- **Harness notes.** The hand-off records what the agent got wrong during execution and which guide or sensor would have caught it (a rules-file line, a hook, a lint rule, a test), so the next codesign starts from a better harness instead of the same mistakes.

## Multi-session continuity

This skill is built for repeat use on the same platform across sessions.
When prior decisions exist (in the plan, in ADRs, or in memory), reference them rather than re-litigating: "Last session settled on GitHub Actions and pytest; this session is about coverage.
Does that match where you are?"
If you suspect drift since the last session, ask before assuming.
Record the settled design and the progress in memory at the end of a codesign session, with a "how to apply" line naming what a later session must not re-open.

## Output discipline

- Discovery goes in the questions file; the chat message points at it and names the three questions that matter most.
- Research synthesis cites source and date and does not dump raw findings.
- The proposal is a structured document with a diagram, not an essay.
- Every markdown file written keeps one sentence per line and uses regular dashes.
- Every diagram is preceded by a sentence saying what it shows and is checked to render.
- Do not hedge as a substitute for thinking.
  "It depends" is fine only when followed by what it depends on and which side of the dependency the user lands on.
- Maintain a senior-engineer tone: direct, opinionated, willing to be wrong, no sycophancy.
- No git commits or pushes; the author commits.

## Anti-patterns

- Recommending before discovery is complete.
- Asking the repo's own questions instead of reading the rules files, ADRs, and existing plans first.
- A wall of questions in chat with no picture of the current state for the user to correct.
- A generic best-practices dump untethered from the user's constraints.
- A survey of options in place of a recommendation.
- Sycophantic agreement on shaky premises, or an objection with no path forward.
- Surface-level research (forum answers, listicles) instead of primary sources, or claims about the user's repo that were never checked against a file.
- Skipping the playback before the proposal.
- Ending without the plan offered and an artifacts list.
- Auto-generating every artifact instead of offering.
- Pre-numbering ADRs, or mentioning the plan or its phases in anything committed.
- Time estimates in plans.
- Phases cut by context budget instead of by review points.
- Appending plan conventions to CLAUDE.md instead of carrying them in the plan.
- Declaring the work verified on green tests alone, with no walkthrough evidence and no human test.
- Any git commit or push.

## Old patterns

Advice that earlier versions of this skill or common 2024-2025 guidance carried, now superseded:

- Posting discovery questions in chat; the questions file with diagrams replaced it.
- Repeating the end-of-phase check text in every phase; a single Recurring checks section is referenced instead.
- "Verify your work" instructions in the hand-off; current models over-verify when told to, so verification is an artifact with a fresh-context reviewer.
- Emphatic rule-writing (capitalised MUST and NEVER); explain the reason and current models follow it.
- Cutting phases to fit a context window; the plan and the tree are the state, and a fresh session re-reads them.
- Writing to a downloads folder; artifacts go where they belong in the repository.
- Mandating tests-first for every phase; it is reserved for behaviour with a clear contract.
- Reading every line of agent output as the review method; evidence of real use, an independent reviewer, and deterministic sensors carry more of that weight now.
- Role-play subagents and large prompt libraries; subagents are for context isolation and parallel research, and most pre-written prompts go unused.

## Worked example: "Help me set up CI/CD for our ML platform repo"

Bad flow: "Sure! Here's a GitHub Actions template…"

Good flow:

1. **Read the repo.** Rules files, ADR index, the task runner's recipe list, the existing workflow files and test layout, any plan at the root.
2. **Questions file.** Current state: a flowchart of the existing workflows and what gates a merge, with the paths; then the questions.
   What does "ML platform" cover here: training pipelines, serving, both?
   One repo or several?
   Existing infrastructure (cloud, registry, secrets)?
   Team size and CI experience?
   What tests exist today, and which are slow?
   Latency tolerance for a CI run?
   Cost sensitivity?
   Compliance requirements?
   Which conventions and helpers must the new workflows reuse?
   Who executes the plan, and what counts as done?
   Then two candidate directions (path-filtered lanes versus one fat workflow) as diagrams, and "Anything important I haven't asked?".
3. **Research** (after answers).
   Current GitHub Actions guidance for Python monorepos with native extensions, path-filtered workflows, fast/slow test splits in ML codebases, caching for large dependencies; read the primary posts, and verify the repo's current workflow files and hook configuration.
4. **Pushback if warranted.**
   "You said 100% coverage: pushing back.
   For ML code with stochasticity and external dependencies, line coverage is a poor proxy for confidence.
   Suggest a meaningful floor plus property-based tests on the critical paths."
5. **Playback.**
   "Goal: trustworthy CI for an ML platform monorepo with these services.
   Constraints: GitHub-hosted, Python, small team, sub-15-minute runs.
   Priority: correctness over speed over cost.
   Out of scope for now: training in CI.
   Right?"
6. **Proposal.** Primary stack with rationale and a diagram, an alternative with the conditions under which it wins, explicit tradeoffs, decision criteria.
7. **Plan and artifacts.** Primary hand-off: the implementation plan (design decisions with the target diagram, conventions, repository facts, ADR gate, phase 0 baseline, phased checkboxes each with its change diagram and a TDD note on the test-migration phase, recurring checks, verification phase, hand-off with the human test).
   Supporting docs: `docs/testing-philosophy.md`, `docs/ci-pipeline.md`, `CONTRIBUTING.md`, and an ADR on the CI platform choice, numbered at write time.
   Offer to draft any.
8. **Verification.** A walkthrough that opens a PR on a scratch branch and screenshots the lanes that ran and skipped; the human test is one push and one page to look at.

Specific tool choices are illustrative; the actual recommendation depends on what discovery surfaces.

## Reference files

- [references/questions-file-template.md](references/questions-file-template.md): the discovery file skeleton; read when opening discovery.
- [references/discovery-and-artifacts.md](references/discovery-and-artifacts.md): question themes, extra probes by system type, artifact catalogue; read when writing questions and when listing artifacts.
- [references/diagrams.md](references/diagrams.md): which mermaid type for what, how to show a change, size limits, rendering checks; read before drawing.
- [references/research-sources.md](references/research-sources.md): primary sources by vertical, with dates; read when the research phase starts.
- [references/implementation-plan-template.md](references/implementation-plan-template.md): the plan skeleton; read before drafting or amending a plan.
- [references/adr-practice.md](references/adr-practice.md): finding, writing, amending, and numbering ADRs; read at the gate and at every ADR check.
- [references/verification.md](references/verification.md): verification tools per app type, evidence conventions, the human test; read when the verification phase starts.
- The sibling `plan-execution` skill: how a later session executes the plan, including model, effort, and parallelism choices; it reads the references above by relative path, so keep them where they are.
- The sibling `create-verification-skill`: generates the `verify-<app>` skill and feature map the verification phase drives through; it reads the references above by relative path too.

## Maintaining this skill

Skills written for earlier models tend to be too prescriptive for later ones, and harness components turn into dead weight within a model generation.
Review this skill against current primary sources every few months and after a major model release, remove instructions the model now follows unprompted, and move anything dated into Old patterns rather than leaving it in the body.
