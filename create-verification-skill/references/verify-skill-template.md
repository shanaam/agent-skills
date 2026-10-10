# Generated verification skill: template

Read this before writing `.claude/skills/verify-<app>/SKILL.md`.
Angle brackets are slots to fill from the interview; everything else is the recommended wording, to be edited where the repository differs.
Lines in italics explain intent and are deleted from the generated file.
Keep the generated SKILL.md under about 150 lines; the per-feature detail lives in `features/`.

Contents:

- Frontmatter notes
- The skeleton
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
- Record at launch what cleanup needs: <the pid, the handle, the data directory, the run id>.
- Fresh machine: <the one-time step, such as registering the driver MCP server for the agent, and the doc that holds it>; `<doctor recipe>` then proves the whole path.

_Launch for a short-lived CLI means build once, then run each drive in its own isolated session; there is no server to keep alive._

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
- Interactive-only steps: <list, or "none">; everything else runs headless.

## Evidence

- Location: `<app>_verification/<YYYY-MM-DD>/<feature-id>/`, gitignored by `*_verification/`; cleanup never touches it.
- Per step: wait for the post-condition, then capture `<nn>_<what>.png` and the state text beside it as `<nn>_<what>.txt`.
- Per feature: a `walkthrough.md` naming each artifact, what it shows, what was expected, and the exact commands that produced it.
- Record the build: <how the build identity is read> goes into `walkthrough.md` with the date.
- Proof standards: the real user path, not internal setters or test-only endpoints; the action and the resulting state, not only the final screen; side effects checked (<files, rows, messages>) beside what is visible; mocks only at <the production boundary that already isolates the external system>; a dry-run or test mode verified by observing what it skips.
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

## Feature map

`features/README.md` is the index: baseline preconditions, driving conventions, proof rules, the navigation diagram, and one line per feature.
Each feature file has four sections in a fixed order: `Sub-features`, `How to get to it (user POV)`, `Driving it with <harness>`, `Gotchas`.
A proof that drives one convenient entry point is incomplete when the map lists others.
Add or update a feature file in the same change that adds or changes the feature, and reset its `Status:` line to drafted until a run drives it.

## Maintaining this skill

<the section below, verbatim>
```

## Helper placement

- When the repository has a task runner, the helper is a recipe in it and the skill references the recipe; the recipe keeps the venv, the flags, and the paths right when they change.
- Scripts the skill ships go under `scripts/`, in the language the repository uses for tooling, executable, invoked as shown in the skill body, and referenced as `${CLAUDE_SKILL_DIR}/scripts/<name>` so they resolve from any working directory.
- Commands written for the author to run go in the author's shell syntax; in this family that is PowerShell, without `&&`.
- A debug-only entry point that enables a driver extension lives beside the app's `main`, is named for what it is (`main_driver.dart`, `--driver`), and never becomes the release entry point.

## The maintenance section, verbatim

```markdown
## Maintaining this skill

A feature map rots the moment the app changes, so run a maintenance pass when a feature file's recipe fails on an unchanged app, after a plan that touched several features, after a release, or on a cadence the team chooses.

- Edit scope is this directory and the helpers it owns; never product code during a pass.
  A behaviour the map describes that the app no longer does is either doc drift (fix the map) or a product regression (report it); never paper over a regression in the docs.
- Index hygiene first: read `features/README.md`, list its sibling files, and fix missing, extra, duplicate, or dead entries.
- Source wave: one read-only subagent per feature file, launched together, each explaining how that user-facing feature works from source and returning a summary, the source entry points, likely drift with citations or none, and one live recipe; subagents never drive the app and never edit files.
- Reconcile: merge overlapping recipes into as few app states as practical, spot-check cited drift, and sweep recent churn for user-facing surfaces missing from the map, requiring a concrete source path before calling one missing.
- Live pass, required even when source looks clean: the coordinating session drives every feature at least once under this skill's own Launch model, with the doctor before the first drive and after any failed drive, evidence surviving every cleanup at its named location, and residue from failed drives cleaned whether the session is stuck, exited, or shared.
  A feature is `verified-unreachable` only with the concrete prerequisite (auth, entitlement, OS, device, external state) and the route attempted; if the map omitted that prerequisite, that is drift.
- Triage: a wrong or missing user-POV description is doc drift, fix it; working behaviour the harness cannot drive is a harness gap, fix it and re-drive before it ships; app behaviour that is broken is a product gap, record it for the author and keep it out of this change.
- Outcome, stated plainly: `clean` (every feature covered from source and live, nothing to ship), `changed` (one change set of proven corrections, re-read before hand-off, committed by the author), or `blocked` (coverage could not finish or a fix could not ship safely, with exactly what blocked it).
- Keep run notes (features covered, unreachable prerequisites, confirmed drift, outcome) in the evidence folder, not in the skill.
```
