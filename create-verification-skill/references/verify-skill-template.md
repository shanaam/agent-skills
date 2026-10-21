# Generated verification skill: template

Read this before writing `.claude/skills/verify-<app>/SKILL.md`.
Angle brackets are slots to fill from the interview; everything else is the recommended wording, to be edited where the repository differs.
Lines in italics explain intent and are deleted from the generated file.
Keep the generated SKILL.md under about 150 lines; the per-feature detail lives in `features/`.

Contents:

- Frontmatter notes
- The skeleton (Launch, Self-check, Doctor, Drive with the suite, Live tier, Evidence, Cleanup, Helpers, Feature map, Maintaining)
- Helper placement
- The maintenance section, verbatim

## Frontmatter notes

- `name` must match the directory name, `verify-<app>`.
- `description` is the trigger; name the app, the surface, the launch recipe, and the situations that should load the skill, and tell the reader to open `features/README.md` first.
- Leave `disable-model-invocation` unset so a plan's verification phase can load the skill without the user typing it.
- `paths:` can limit automatic activation to the app's source globs; use it only when the repository has several apps and the skill misfires on the others, because a verification phase for a shared library change also needs it.
- `allowed-tools` applies even in untrusted folders, so list only the helper invocations the skill really needs, with `${CLAUDE_SKILL_DIR}` for script paths.
- Follow the repository's markdown rules (in this family: one sentence per line, no em-dashes, LF endings).

## The skeleton

```markdown
---
name: verify-<app>
description: Drives <app> (<surface>, under <path>) the way a user does and captures evidence: launches it with <recipe>, checks the instance is worth driving, drives features through <harness>, saves screenshots and state text under `<app>_verification/<date>/`, and tears down what it started. Use whenever a change touches <app> or the libraries under it and needs proof, whenever the user asks whether the app still works, for a smoke check, a walkthrough, screenshots, or before/after evidence, and in every implementation plan's verification phase for this app. Read `features/README.md` first; it lists every user-facing feature and how to reach it.
---

# Verify <app>

<One paragraph from the user's side: what the app is, its surfaces, and what this skill can and cannot prove, for example that the emulator stands in for the device and real-device behaviour is the author's check.>

## Launch

- Prepare once: `<build or install command>`.
- Start for verification: `<recipe or command with the flags that make the instance drivable>`.
- Ready when: <the log line, the port answering, the window title, the prompt>; wait for it, never a fixed sleep.
- Isolation: <two instances can run with <ports or data directories> / only one instance can run, so never drive one this run did not start>.
- Dependencies: <the emulator, fake, replay source, or dry-run mode, started first and how>; <what only the real dependency proves>.
- Record at launch what cleanup needs: <the pid, the handle, the data directory, the run id>, in `<run>/launch.json` beside `status`, `git_head`, and `git_dirty_paths`, which the `/verify` orchestrator compares with the range it verifies.
- State outside the app that a drive changes (<saved options, a config file, a profile>) is copied aside by the launch helper and put back when the run ends; the launch record lists what was preserved and what was restored.
- Fresh machine: <the one-time step, such as registering the driver MCP server for the agent, and the doc that holds it>; `<doctor recipe>` then proves the whole path.

_Launch for a short-lived CLI means build once, then run each drive in its own isolated session; there is no server to keep alive._

## Self-check

`python ${CLAUDE_SKILL_DIR}/scripts/selfcheck.py` (recipe `just <app>-verify-check`) says whether the map still matches the app, without launching anything; run it before the first drive of a run, at the end of a plan's docs phase, and whenever a recipe fails on an app that should not have changed.

- It exits 0 when every feature file is indexed and in the four-section shape, every `Proof` bullet names a steps file that exists, every steps file is named somewhere, and every user-facing source file (<the globs>) is claimed by some feature's `Sources:` line.
  A new screen, dialog, or control therefore fails it until a feature file claims the file.
- It warns about features whose claimed sources changed after their `driven on` date and about visible copy no feature file or steps file quotes; `--strict` turns the first into a failure for a maintenance pass.
- `--hook` runs only the deterministic part; the pre-commit hook `<hook id>` runs it when <the app's source globs> or this directory change.
- A failure means the map is behind the app, not that the app is broken: add or update the feature file, then drive it.

## Doctor

One read-only check, run before the first drive and again after any failed drive:

`<command>`, requiring <the expected URL or port>, <the build identity and how it is read>, <the data directory>, <the device or fake connected>.

If it fails, do not drive; fix the launch or report the failure with the output.

The repository's doctor recipe `<just <app>-driver-smoke>` is the full check (build, launch, connect, one wait, one capture to disk, stop); exit codes: <0 the path works / 3 only the capture failed / other the driver could not connect or the screen never appeared>.

_The doctor answers "is this instance worth driving?", so it checks identity and ownership, not features._

## Drive

- Harness: <the driver and how to reach it: the MCP server and tool, the CLI, the endpoint>.
- Stable handles: <widget keys / accessible names / route paths / prompt strings / endpoints>, listed per feature in `features/`; never coordinates or tab order.
- Shorthand used in feature files is defined once in `features/README.md` under Driving conventions.
- Reset to a known state between features: <how>.
- The suite: `python ${CLAUDE_SKILL_DIR}/scripts/suite.py --run <run>` drives every recipe in the order `scripts/steps/suite.txt` gives, with the resets where the recipes' preconditions want them (<the chained pair, or "a reset before each">), writes each feature's `walkthrough.md`, recovers after a failed recipe, and ends with `<run>/suite.md`; `--only <ids>` narrows it, and any run directory works, so the `/verify` orchestrator can point it at a shared evidence folder.
  Use the suite for a maintenance pass and for a plan that touched several features, and the driver alone while iterating on one recipe.
- Interactive-only steps: <list, or "none">; everything else runs headless.

## Live tier

_Only when a fake, emulator, or dry-run stands in for a real system (a device, a pipeline, a service); otherwise delete this section._

- What the fakes stand in for: <the real system and how it is launched for a live check>, with `features/<live-feature>.md` as the recipe and the probes under `scripts/live/` measuring it through its own API (<cadence, latency, counters>), each with the expected numbers and the first measured ones.
- Every live pass starts with the environment baseline (<the probes to run and the healthy numbers>) saved under `<run>/live/baseline/`, so a recipe that fails on a degraded link or a slow service is classified as environment before product.
- The transitions the fidelity register in `features/README.md` sends here (<a take, a reconnect, a stream stopped and resumed>) are driven on the real system, because that is where it and the fake differ.
- A live recipe that acts on the real system (<runs a take, retargets a device>) runs only when the author has asked for a live check.

## Offline tier

_Only when the app, or the stack it launches, has edges that leave the machine and is run where the network may be absent or half-working; otherwise delete this section._

- The edges: <each process on the launch path that opens an off-machine connection, and why>, each a row in the fidelity register.
- Method: a launch on a machine warmed by an earlier online run, with egress refused rather than absent (<the offline flags, a proxy pointed at a tripwire listener that logs and refuses every attempt>), driven through <the suite's launch recipe>; a half-working network is the case to model, so refusal beats disconnection.
- The gate: <the recipe that runs it and exits non-zero> on any logged attempt or on health not reached, with the tripwire's log and the launch log under `<run>/offline/`.
- Mandatory for any change that touches <the launch path, model loading, a server, a network client, runtime assets>, reported beside the fake and live tiers.

## Evidence

- Location: `<app>_verification/<YYYY-MM-DD>/<feature-id>/` when this skill runs alone, or `<run>/<feature-id>/` under the run directory the `/verify` orchestrator passes, both gitignored by `*_verification/`; cleanup never touches it.
- Per step: wait for the post-condition, then capture `<nn>_<what>.png` and the state text beside it as `<nn>_<what>.txt`.
- Per feature: a `walkthrough.md` naming each artifact, what it shows, what was expected, and the exact commands that produced it.
- Record the build: <how the build identity is read> goes into `walkthrough.md` with the date.
- Proof standards: the real user path, not internal setters or test-only endpoints; the action and the resulting state, not only the final screen; side effects checked (<files, rows, messages>) beside what is visible; mocks only at <the production boundary that already isolates the external system>; a dry-run or test mode verified by observing what it skips.
- Second views: a state the screen mirrors from <the backend> is read a second time from the backend's own side (<the status endpoint, a pane row, a CLI query>); `features/README.md` lists the pairs.
  The screen's own label passes on the fake because the fake is the app's idea of the backend.
- Transitions: a feature proven from the baseline says nothing about the same feature after <a take, a reconnect, the device coming off>; the fidelity register names them, each recipe drives at least one the fake can do, and the live tier drives the rest.
- Evidence is positive and fresh: every artifact newer than the build, non-empty, and containing the expected text.

## Cleanup

- Stop what this run started, by the handle recorded at launch: `<command>`.
- Remove scratch state: <the data directory, the temp profile, the seeded rows>.
- Never kill by process name; never delete the evidence folder.
- After cleanup, list the evidence folder and confirm the artifacts are still there.

## Helpers

- `<drivable entry point>`: the debug-only build the driver talks to, launched by `<launch recipe>`; never the release target, and its dependency is declared where it cannot ship.
- `<launch recipe>` and `<doctor recipe>`: in the task runner, documented in `<commands doc>`; the per-machine registration of `<driver server>` for the agent is in `<contributing doc>`.
- `<recipe or script>`: <what it does>, run as `<exact invocation>`. <Why it exists; when it is scaffolding in product code, say so and say what it must never do in a release build.>
- `${CLAUDE_SKILL_DIR}/scripts/suite.py --run <run> [--only <ids>]` with `scripts/steps/suite.txt`: the recipes in their chaining order with the resets between them, one `walkthrough.md` per feature and `<run>/suite.md` at the end.
- `${CLAUDE_SKILL_DIR}/scripts/selfcheck.py [--strict|--hook]` (recipe `just <app>-verify-check`, hook `<hook id>`): the map against the app, as described under Self-check; it reads files and git only.
- `.claude/verifiers.toml`, this skill's entry: the targets it proves, its runtime peers, its live-only globs, its prerequisites, its ports, and its suite and self-check commands, which the `/verify` orchestrator reads to put the skill in scope; `<coverage check recipe>` keeps every target in the repository claimed.

## Feature map

`features/README.md` is the index: baseline preconditions, driving conventions, proof rules, the second views, the fidelity register (what the fakes do not model and the transitions that need the live tier), the navigation diagram, and one line per feature.
Each feature file has four sections in a fixed order: `Sub-features`, `How to get to it (user POV)`, `Driving it with <harness>`, `Gotchas`, and a `Sources:` line under its `Status:` naming the app source that renders it, which the self-check uses to claim every user-facing file and to flag the feature as stale when those files change after its last drive.
A proof that drives one convenient entry point is incomplete when the map lists others.
Add or update a feature file in the same change that adds or changes the feature, with its `Sources:` line and its steps file, add it to `scripts/steps/suite.txt`, reset its `Status:` line to drafted until a run drives it, and run the self-check before handing the change over.

## Maintaining this skill

<the section below, verbatim>
```

## Helper placement

- When the repository has a task runner, the helper is a recipe in it and the skill references the recipe; the recipe keeps the venv, the flags, and the paths right when they change.
- Scripts the skill ships go under `scripts/`, in the language the repository uses for tooling, executable, invoked as shown in the skill body, and referenced as `${CLAUDE_SKILL_DIR}/scripts/<name>` so they resolve from any working directory.
- `scripts/selfcheck.py` starts from [selfcheck-template.py](selfcheck-template.py): fill in the surface globs, the visible-string patterns for the app's UI toolkit, and the driving H2's harness name, keep the exit codes, and give it a recipe and a pre-commit hook (`--hook`, filtered to the app's source and the skill directory, `pass_filenames: false`).
- `scripts/suite.py` with `scripts/steps/suite.txt`: the manifest lists `<feature-id> <steps-file>` lines and `reset` lines; the runner drives them in order through the driver, writes each walkthrough, recovers with the reset recipe after a failure, and writes `<run>/suite.md`.
  The org-repo `verify-demo-app` skill ships one to copy; it depends only on the driver's exit codes (0 pass, 1 a failed step, 2 unreachable) and `result.json`.
- The launch helper copies aside the files a drive changes outside the app and restores them when the run ends, recording both in the launch record.
- The registry entry follows [verifier-contract.md](verifier-contract.md): `proves` from the Surface answer, `runtime_peers` from the Peers at runtime answer, `live_only` from the fidelity register, each `prerequisite` from the build step a changed source needs, `ports` from the Isolate answer, and `suite` and `selfcheck` as the commands the Helpers section names.
- Commands written for the author to run go in the author's shell syntax; in this family that is PowerShell, without `&&`.
- A debug-only entry point that enables a driver extension lives beside the app's `main`, is named for what it is (`main_driver.dart`, `--driver`), and never becomes the release entry point.

## The maintenance section, verbatim

```markdown
## Maintaining this skill

A feature map rots the moment the app changes, so run a maintenance pass when the self-check reports a stale or unclaimed surface, when a feature file's recipe fails on an unchanged app, after a plan that touched several features, after a release, after a live incident the map did not predict, or on a cadence the team chooses.

- Edit scope is this directory and the helpers it owns; never product code during a pass.
  A behaviour the map describes that the app no longer does is either doc drift (fix the map) or a product regression (report it); never paper over a regression in the docs.
- Self-check first: `python ${CLAUDE_SKILL_DIR}/scripts/selfcheck.py --strict` lists the unclaimed surfaces, the stale features, and the unquoted copy; each unclaimed surface becomes a feature file or a `Sources:` line, each stale feature goes on the drive list, and each unquoted string is either a sub-feature the map lacks or copy inside one it has.
- Index hygiene: read `features/README.md`, list its sibling files, and fix missing, extra, duplicate, or dead entries the self-check could not judge.
- Source wave: one read-only subagent per feature file, launched together, each explaining how that user-facing feature works from source and returning a summary, the source entry points, likely drift with citations or none, and one live recipe; subagents never drive the app and never edit files.
- Reconcile: merge overlapping recipes into as few app states as practical, spot-check cited drift, and sweep recent churn for user-facing surfaces missing from the map, requiring a concrete source path before calling one missing.
- After a live incident: name the fake's gap in the fidelity register, add the probe or the transition that would have shown it, and record the measured numbers in the live feature file; a gap the register names is one a plan's verification phase sends to the live tier.
- Live pass, required even when source looks clean: the coordinating session drives every feature at least once under this skill's own Launch model (the suite for the fake tier, then the live tier when the author has asked for a live check), with the doctor before the first drive and after any failed drive, evidence surviving every cleanup at its named location, and residue from failed drives cleaned whether the session is stuck, exited, or shared.
  A feature is `verified-unreachable` only with the concrete prerequisite (auth, entitlement, OS, device, external state) and the route attempted; if the map omitted that prerequisite, that is drift.
- Triage: a wrong or missing user-POV description is doc drift, fix it; working behaviour the harness cannot drive is a harness gap, fix it and re-drive before it ships; app behaviour that is broken is a product gap, record it for the author and keep it out of this change.
- Outcome, stated plainly: `clean` (every feature covered from source and live, nothing to ship), `changed` (one change set of proven corrections, re-read before hand-off, committed by the author), or `blocked` (coverage could not finish or a fix could not ship safely, with exactly what blocked it).
- Keep run notes (features covered, unreachable prerequisites, confirmed drift, outcome) in the evidence folder, not in the skill.
```
