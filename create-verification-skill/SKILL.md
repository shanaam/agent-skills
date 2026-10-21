---
name: create-verification-skill
description: Generates a project-local verification skill at `.claude/skills/verify-<app>/` that drives an application the way a user does (launch, doctor, drive, evidence, cleanup), installs the harness the app needs (a debug-only driver entry point, launch and doctor recipes, the agent's driver server registration, the skill's entry in the repository's verifier registry, the setup docs for the next machine), seeds the feature map, then proves the skill by running it once before handing it over. Use whenever a repository has no scripted way to prove UI, desktop, CLI, or service behaviour, whenever the user asks for a verification skill, a verify skill, a feature map, a control skill, an app-driving harness, or "a way for the agent to use the app as a user", and whenever a plan's verification phase finds no `verify-<app>` skill to drive through. Any language or platform. Not for running a verification; that is the generated skill's job, so when `verify-<app>` already exists, use it instead. Adapted from pstack's create-verification-skill by poteto (MIT).
---

# Create a verification skill

Every application a team keeps changing needs a scripted way to drive the real thing and prove behaviour: launch it, exercise a feature the way a user would, and capture evidence a reader can check in a minute.
This skill generates that as a project-local skill tailored to the repository, with a feature map as the maintained list of what the application does from the user's side.
The output is written for the next agent, not for a human: it is read cold, mid-task, by a session that has never seen the application, so every command is literal, every observable is named, and every claim is grounded in what the interview found.

Verification skills are first-class in this skill family.
The architecture-codesign skill writes a verification phase that drives through `verify-<app>` when one exists, the plan-execution skill runs that phase through it, and a plan that changes a user-facing feature updates the feature's map file in its docs phase.
The feature map is therefore the repository's verification source of truth, and the plans keep it current.
The generated skill also checks itself: a self-check script compares the map with the app's source and fails when a user-facing file no feature claims appears, so a plan that lands a screen without its feature file is caught by a recipe and a pre-commit hook rather than by memory.

## What gets generated

```text
.claude/skills/verify-<app>/
  SKILL.md          launch, self-check, doctor, drive (with the suite), evidence, cleanup, helpers, feature map, maintenance
  features/
    README.md       index, baseline preconditions, driving conventions, proof rules, second views,
                    fidelity register (what the fakes do not model), navigation diagram
    <feature>.md    one per user-facing feature, Status and Sources lines, four fixed sections
  scripts/
    selfcheck.py    the map against the app: integrity, claimed surfaces, stale features, unquoted copy
    suite.*         the recipes in their chaining order, with the resets between them
    live/           probes of the real system through its own API, when a fake stands in for one
    ...             the launch, drive, and walkthrough helpers the harness needs
```

Beside the skill, the harness it depends on lands in the product repository (step 3): the drivable entry point, the launch and doctor recipes, and the docs for the next machine.
The skill's entry in the repository's verifier registry (`.claude/verifiers.toml`) lands there too, per [references/verifier-contract.md](references/verifier-contract.md), so the `/verify` orchestrator puts the skill in scope when a change touches what it proves.

One skill per application a user touches; a monorepo with two apps gets `verify-<app-a>` and `verify-<app-b>`, each named the way the team names the app.
Put the skill at the repository root's `.claude/skills/`, not under a subproject: Claude Code loads root project skills at startup and nested ones only after a file in that subtree is read, which is too late for a verification phase that starts by launching the app.

## 1. Interview the repository, not the user

Answer these from the codebase and ask the user only what cannot be observed, batched in one message with your best guess per question, because an agent that asks what it could have read spends the user's attention on nothing.

- **Surface.** What does a user actually touch: a desktop app, a web UI, a CLI or TUI, an API, a mobile app, a library?
  A repository often has several; pick the primary one for this skill and note the rest.
- **Run.** How does the app start locally?
  Prefer the repository's own documented command (task-runner recipes, package scripts, a README quickstart) over a raw invocation, because a recipe keeps working when flags change.
  Note ports, environment variables, seed data, and auth.
- **Drive.** How can an agent interact with it programmatically?
  Existing harnesses first: a driver extension, integration tests, Playwright or similar specs, a control or status API, a debug port, a smoke recipe.
  Only then pick a generic driver for the app type from the table in [../architecture-codesign/references/verification.md](../architecture-codesign/references/verification.md).
- **Observe.** What evidence can be captured: screenshots, state text, terminal transcripts, response bodies, logs, exit codes, files written, rows inserted?
- **Isolate.** Can two instances run side by side (ports, data directories, profiles)?
  If not, the generated skill says so and refuses to drive an instance it did not start; refusing beats corrupting the user's session.
- **Hardware and externals.** Does the app need a device, a board, a cloud service, a model server?
  Find the repository's emulator, fake, replay source, or dry-run mode and record how to launch with it, and name what only the real dependency can prove.
- **Peers at runtime.** Which other targets in the repository does the app talk to while it runs without importing them: a pipeline over HTTP, a server, a device emulator?
  The build graph misses these edges, so an infra change under the peer would scope the peer's verifier and not this one; each peer goes into the registry entry as a runtime peer, proven on the live tier.
  The demo app is coupled to its pipeline only through the API, and its project declares only the Dart libraries it imports.
- **Edges that leave the machine.** Which processes on the launch path open a connection off the machine, and why: a model hub listing, a token refresh, a font or package fetch, a usage report?
  Each is a row in the fidelity register, and when the app is run or demoed where the network may be absent or half-working, the skill gets an offline tier: a launch on a warmed machine with egress refused (a tripwire proxy that logs and refuses every attempt) that must still reach health.
  A demo stack lost its intent server to a hub's 500 at startup with every byte of the model on disk, because nothing had ever launched it with the network refused.
- **Fidelity.** For each fake, emulator, or dry-run the app can run on, what does it not model: timing (a control applied at once where the real system applies it on the next data), loss (a queue that never evicts), clocks (a timeline that never restarts), transitions (no reconnect, no stop and resume of a stream, no device coming off mid-flow), degradation (a service that never goes offline), shared state (a port another app also answers on)?
  Each gap is a row in the map's fidelity register with the transition it shows after and the live check that sees it, because a recipe on the fake passes before and after a bug that lives in a gap.
  The first generation on the demo app proved six features on the fakes, and the author then met four live-only failures in one afternoon (a lost unmute after a take, a stale utterance after the device came off, a probe window shorter than the board's answer, a stuttering stream); every one sat in a gap the fake had and the map had not named.
- **Contracts the app consumes.** Which recipes, commands, and endpoints does the app shell out to or call at startup, with what exit codes and payload shapes?
  Each is a headless check that needs no app running, and the ones that cross a shell boundary are where a fresh reviewer found gaps the drives had passed over (a task runner on Windows reporting exit 3 as 1).
- **State outside the app that a drive touches.** Saved options, config files, profiles, seeded rows: the harness copies them aside at launch and puts them back at the end, because a note under Gotchas asking the reader to copy a file aside was skipped once and the author's saved options were overwritten.
- **Build identity.** How does a running instance show which build it is: a version string, a git sha on an about screen, a status field, a log line at startup?
  If there is none, record it as a gap for the author rather than inferring the build from a window title.
- **Repository conventions.** The task runner, the markdown rules, where evidence goes, and the ignore rules, so the skill directory is committed and the evidence folder is not.

If the checkout does not build or start as-is, fix that first or report it precisely before generating; a skill written against a broken base teaches wrong steps.

Edit scope: the generator writes under the skill's own directory.
The only product-repository edits it makes are verification scaffolding the driver needs: a debug-only entry point that enables a driver extension, a task-runner recipe, a build-identity hook, a missing asset the app refuses to start without.
Each is minimal, named as scaffolding, listed in the generated skill's Helpers section with the reason, and never a change to product behaviour; anything that would ship in a release build waits for the author.

## 2. Pick the driver and probe it

Prefer the platform's own driver protocol (an accessibility tree, a driver extension, a CDP endpoint, a control API) over pixel-and-pointer automation, because it gives the agent state text to assert on and leaves pixel capture for the human's eyes.
Claude Code's own order for a browser is the same: an MCP server first, then scripted calls, then Claude in Chrome when interactive, then computer use last.

Before writing a line of the skill, probe the three things it depends on: the launch readiness signal, one driver action followed by a state read, and one capture written to disk.
A ten-minute probe here saves a skill written against a tool that does not work on this machine; the known traps are listed under "Probe before relying on it" in the verification reference.
Record which steps need an interactive desktop (a window capture, a browser extension, computer use) and which run headless, so a later unattended run knows what it can and cannot prove.

Traps the first generation on a Flutter desktop app met (2026-10-09), each worth a probe on a similar stack:

- The VM service URL `flutter run` prints is served by the tool's own process, so the owner of that port is not the app; the app's pid comes from the process tree under the launch recipe.
- The MCP `screenshot` returns the image inline, so evidence on disk needs a client that saves it; a small Python MCP stdio client running a steps file became the skill's driver, and the same commands remain available by hand.
- Page and caption transitions keep the outgoing widget in the tree while they animate, so a screenshot taken right after a `waitFor` shows both states; wait for the old text to be absent first.
- A widget below the fold of a scrolling pane is found but not tappable; scroll it into view before `waitForTappable`.
- Copy is not uniform: most titles used curly apostrophes and one used a straight one, so a `waitFor` that times out on a title is checked against the source string before anything else.
- A debug-only reset action that returns the app to its baseline from any screen is worth more than any launch flag; find it in the interview and make it the recipe between features.

Traps the same skill met once it was in use (2026-10-11), each now a rule in the template:

- A recipe proven from the baseline says nothing about the feature after a transition: the four live failures were all "after a take", "after the device came off with an utterance open", "after a reconnect".
  Each feature file names the transitions that lead into it, the recipe drives the ones the fake can do, and the fidelity register sends the rest to the live tier.
- A screen that mirrors backend state passes on the fake because the fake is the app's own idea of the backend; what fails is the second view, the backend's own status field read through its API or a pane row.
  The map lists the pairs, and a recipe that proves the screen reads the second view too.
- Recipes chain: one leaves the state the next needs (an enrolled user), so a run order improvised per session put a reset between them twice.
  A suite manifest encodes the order and the resets once, and the suite runner drives it.
- A link can degrade between two runs on the same code (an answer that took 1.6 s on one connection took 23.9 s on the next); a live pass starts with an environment baseline so a failure is classified as environment before product.

## 3. Make the harness exist and reachable

The interview and the probe say what the driver needs; this step puts it in place, because a skill that assumes a harness nobody installed is read cold by an agent that cannot install it mid-task.
"Available to agents" means all of the following, and each one found missing is done here, not deferred to the hand-off:

- **A drivable build in the repository.** When the driver needs an entry point or a build flag (a debug-only `test_driver/app.dart` that enables a driver extension, a dev server started with a debug port, a CLI built with a test flag), it lives in the repository as committed scaffolding, named for what it is, with its dependency declared where it cannot ship (a dev dependency, a test target), so the next machine builds it from a clean clone.
- **A launch recipe and a doctor recipe in the task runner.** The launch recipe starts the drivable build and prints what the agent needs to connect (a tooling-daemon URI, a port, a VM service URL).
  The doctor recipe proves the whole path end to end (build, launch, connect, one wait, one capture to disk, stop) and exits non-zero when it fails, so an agent and a fresh machine have one command that says whether driving is possible.
  Prefer the repository's task runner over a raw command, because the recipe keeps the flags right when they change.
- **The agent's driver tool registered on this machine.** An MCP server (the Dart MCP server, Playwright MCP, Chrome DevTools MCP) or a CLI the skill calls must be reachable from the agent: register it (user scope when it is per machine, project scope only when every teammate should get it), confirm with `claude mcp list` or the tool's own health check, and note platform quirks such as a batch-file wrapper needing `cmd /c` on Windows.
  Record the registration command per OS where the next machine's reader will look, because this step lives outside the repository and is the one most often missing.
- **The self-check recipe and its hook.** `scripts/selfcheck.py` (from [references/selfcheck-template.py](references/selfcheck-template.py), with the surface globs and string patterns filled in for this app) gets a task-runner recipe, `just <app>-verify-check` or the repository's equivalent, and its deterministic part (`--hook`: map integrity and claimed surfaces, no git) becomes a pre-commit hook filtered to the app's source and the skill directory.
  The hook is what makes "update the feature map in the docs phase" a sensor instead of a sentence; keep staleness a warning there, because a hook that fails on "drive it again" blocks every unrelated commit, and keep a dead `Sources:` glob a warning too, because in a stack of commits the map can land before the code and CI runs the hook on every commit's PR.
- **The registry entry.** `.claude/verifiers.toml` at the repository root gains this skill's entry, in the shape [references/verifier-contract.md](references/verifier-contract.md) gives: the targets it proves (from Surface), its runtime peers (from Peers at runtime), the live-only globs (from Fidelity), each prerequisite with the change that triggers it (a native extension rebuild after a change under its sources), the ports it owns or refuses to share (from Isolate), and its suite and self-check commands.
  The repository's coverage check passes once the entry is in; when the repository has no registry yet, create it with this one entry and the check, because the `/verify` orchestrator scopes a change through the registry and a verifier missing from it is never run.
- **The gotchas, where the next agent reads them.** What the probe and the doctor run taught (a frame-sync setting, a startup race, a renderer limit, an inline-only screenshot) goes into the generated skill's Drive section, the feature map's driving conventions, and the repository's commands doc; a gotcha that lives only in a chat transcript is lost.
- **The setup docs, when setup changed.** When the harness adds a per-machine step or a dependency, the contributing guide gains the step and the commands cheatsheet gains the recipes.
  When a rules file (`AGENTS.md` or similar) is the natural home and the repository asks for discussion before editing it, draft the lines and queue them for the author instead of editing.
- **Proof on this machine.** Run the doctor recipe once before writing the skill; its output and artifact are the first evidence, and a harness that has not passed its own doctor is not a harness.

Keep each piece minimal and behaviour-preserving; the edit-scope rule from the interview applies, so nothing changes product behaviour and nothing ships in a release build without the author.

## 4. Write the skill

Follow the skeleton in [references/verify-skill-template.md](references/verify-skill-template.md) and the repository's markdown conventions.
The frontmatter has `name: verify-<app>` and a description that names the app, the surface, and when to reach for it, pushy enough to trigger on "does it still work", "smoke test the app", "take screenshots", and a plan's verification phase; without frontmatter the skill never registers.
Every section is grounded in what the interview found, with no placeholder left:

- **Launch.** The exact command that starts the app for verification and how to tell it is ready (a log line, a port answering, a prompt), plus the teardown, plus the harness prerequisites on a fresh machine (the one-time registration or bootstrap from step 3, and the doc that holds it).
  For a short-lived CLI there is no server to keep alive: launch means build or install once, then start each drive in its own isolated session.
- **Self-check.** The script, its recipe, its hook, when to run it (before the first drive, at the end of a plan's docs phase, when a recipe fails on an app that should not have changed), and what a failure means: the map is behind the app, not the app broken.
- **Doctor.** One read-only check that answers "is this instance worth driving?": process up, right build, port owned by this run, auth valid, the fake or device connected.
  An agent runs it first whenever anything looks off, and again after any failed drive.
  The doctor recipe from step 3 is this check's strongest form; the skill names it and says what its exit codes mean.
- **Drive.** The harness recipe with real handles from this repository: widget keys, accessible names, route paths, prompt strings, endpoints, never coordinates or tab order.
  The suite: a manifest of the recipes in their chaining order with the resets between them, and the runner that drives it, writes each walkthrough, recovers after a failed recipe, and ends with one summary; a maintenance pass and a plan that touched several features use the suite, a session iterating on one recipe uses the driver alone.
- **Live tier**, when a fake stands in for a real system.
  What the fakes stand in for, the probes under `scripts/live/` that measure the real system through its own API with expected numbers, the environment baseline every live pass starts with, and the transitions the fidelity register sends here; the first measured numbers go into the feature file as the reference the next run compares with.
- **Evidence.** What to capture for a proof and where it goes, with the proof standards: exercise the real user path, not internal setters or test-only endpoints; capture the action and the resulting state, not only the final screen; verify side effects (files written, rows inserted, messages sent) beside what is visible; mocks only where a production boundary already isolates the external system; a dry-run or test mode is verified by observing what it skips, not by trusting its name; a state the screen mirrors from a backend is read a second time from the backend's own side; a feature is proven across the transitions that reset a resource, not only from the baseline.
  Evidence is positive and fresh: new since the build, non-empty, and containing the expected content, with the build it came from recorded.
- **Cleanup.** How to tear down what the run created, and nothing else: never kill by process name, kill what you started.
  Cleanup removes instances and scratch state, never the evidence, which survives in the location the skill names.
- **Helpers.** Any script the skill ships is executable and its invocation is shown in the skill body; a helper the reader has to reverse-engineer is not a helper.
  When the repository has a task runner, the helper is a recipe in it, referenced from the skill, so the skill's commands stay valid when flags change.
- **Feature map.** A pointer to `features/README.md` and the rule that a proof which drives one convenient entry point is incomplete when the map lists others.
- **Maintaining this skill.** The upkeep loop, self-contained, so the skill survives without this generator (template has the text).

Keep the generated SKILL.md short; the per-feature detail lives in the feature files.

## 5. Seed the feature map

Create `features/README.md` plus one file per user-facing feature, following the shape in [references/feature-map-example/](references/feature-map-example/).
Aim for the top three to five features to start, found from routes, screens, menus, commands, and docs, in the order a user meets them.

- The README carries the baseline preconditions, the driving conventions (including any shorthand the feature files use for driver calls, defined once), the proof and skip-reporting rules, the second views (each screen state that mirrors a backend, paired with the backend-side reading of it on the fake and on the real system), the fidelity register (a table of what each fake does not model, the transition the difference shows after, and the live check that sees it), the feature entry contract, and the index.
  The fidelity register is written from the interview's fidelity answers before any feature is drafted, because it decides which journeys a plan can prove on the fake and which it must send to the live tier.
- When the app has more than three screens or commands, the README also carries a mermaid navigation diagram: screens or commands as nodes, user entry points as edges, each node naming its feature file, at most twenty-five nodes, drawn per [../architecture-codesign/references/diagrams.md](../architecture-codesign/references/diagrams.md).
  An agent reading the map cold sees where the feature sits before it reads the recipe.
- Each feature file answers, from the user's point of view: what the feature is, how to reach it, how to drive it with the harness, and what observable end state proves it works.
  The four H2s are `Sub-features`, `How to get to it (user POV)`, `Driving it with <harness>`, and `Gotchas`, in that order, because the maintenance pass and the plans rely on the shape.
- Sub-features carry short ids (`search-empty`, `create-cancel`) so evidence and findings can name them.
- Every file starts, under its H1, with `Status: drafted from source, not yet driven`, removed only when a run has driven that file's recipe end to end; the map stays honest about what is proven and what is inferred.
- Under the Status line, a `Sources:` line names the globs of the app source that renders the feature (screens, dialogs, widgets, the backend nodes a live feature measures, never tests).
  The self-check claims every user-facing file through these lines and flags a feature as stale when its sources change after the date it was driven; a surface no feature claims is the signal that a feature file is missing.
- `How to get to it` lists the transitions that lead into the feature as well as the entry points, and the recipe drives at least one that the fake can do; the fidelity register names the ones that need the live tier.
- Keep implementation detail out: user paths, stable handles, required state, commands, and observable proof only.
- Seed the suite manifest with the features in the order a user meets them, a reset wherever the next recipe starts from the baseline, and none where one recipe leaves the state the next needs.

## 6. Prove it before handing it over

Run the self-check first; on a freshly seeded map it must pass, and an unclaimed surface it reports is a feature the seeding missed.
Run the repository's registry coverage check beside it; it passes once this skill's entry is in `.claude/verifiers.toml`, and a target it still names is one the entry's `proves` list missed.
Then run the generated skill's own instructions end to end once: launch, doctor, drive one mapped feature through the suite runner (one is enough, the map exists so later runs cover the rest), capture evidence, clean up, and confirm the harness put back any state outside the app that the drive changed.
After cleanup, confirm the evidence still exists at the named location; a cleanup that eats the proof fails this step.
Fix what fails, and run the generated cleanup after every failed iteration too, so broken attempts do not strand processes and ports.
The proof run's evidence lands under `<app>_verification/<YYYY-MM-DD>/<feature-id>/` with a `walkthrough.md`, the same conventions a plan's verification phase uses.
Remove the drafted marker from the proven feature only.
When this session has no screen, prove everything that runs headless and list the interactive-only steps under "Not yet proven" in the hand-off with the exact steps, instead of claiming them.
A generated skill that was never executed is a draft, and the hand-off says so.

## 7. Hand over

Tell the user, in one message:

- Where the skill is, which feature is proven, which are drafted, and the harness pieces added to the product repository (entry point, recipes, the self-check recipe and hook, the registry entry, docs) with the reason, plus what was registered on this machine and is therefore per machine.
- That `/verify` now puts this skill in scope for a change under the targets its registry entry proves, and on the live tier for a change under its runtime peers.
- Gaps the interview found that only the author can close: no build identity, no isolation, a step that needs real hardware, and the fidelity register's rows that only the real system can exercise.
- A human test of one to three commands in the author's shell: the doctor, then one drive, each with what to expect and the single observation that means it passed.
- That the author commits the skill directory, after checking the ignore rules keep the evidence folder out.
- The maintenance loop in the generated skill's last section; suggest a cadence only if asked.

When a plan is in play, add the feature map update to its docs phase and point its verification phase at the new skill, so the next session finds both.

## Anti-patterns

- Writing the skill from source alone and never launching the app.
- Leaving a placeholder where a real selector, key, route, or command belongs.
- Driving a convenient internal entry point and calling the feature verified.
- Killing by process name, or a cleanup that deletes the evidence.
- Trusting a dry-run's name instead of observing what it skipped.
- A map that describes what the code does rather than what the user sees.
- Prose written for a human reader where the next agent needs a literal command and an observable.
- A mock where no production boundary exists.
- Changing product behaviour so that a feature becomes drivable.
- Marking a feature proven because its sub-features look obvious from source.
- A harness that exists only on this machine: a driver server registered but undocumented, an entry point or recipe that is not in the repository, a doctor that was never run.
- A map with no fidelity register for an app that runs on a fake, so every journey looks provable on it.
- A screen state proven by its own label when the backend it mirrors has a status field nobody read.
- Features proven only from the baseline, never after the transition (a take, a reconnect, a device off) that the real system makes.
- A map whose only guard against drift is the sentence "update it in the docs phase"; the self-check and its hook are the guard.
- A precondition that asks the reader to back up a file the harness could have copied aside.

## Reference files

- [references/verify-skill-template.md](references/verify-skill-template.md): the skeleton of the generated SKILL.md, section by section; read before writing one.
- [references/selfcheck-template.py](references/selfcheck-template.py): the self-check script to copy into `scripts/selfcheck.py` and fill in (the surface globs, the visible-string patterns for the app's UI toolkit, the H2 names); its contract is in the comments at the top.
- [references/verifier-contract.md](references/verifier-contract.md): the four things the `/verify` orchestrator reads from a generated skill (the `Status:` and `Sources:` lines, the launch record, the suite runner, the registry entry) and the registry's schema; read at step 3 and before changing any script's interface.
- [references/feature-map-example/](references/feature-map-example/): a complete feature map for a small fictional app with a desktop UI and a CLI, with a fidelity register, second views, and Sources lines; copy the shape, not the content.
- [../architecture-codesign/references/verification.md](../architecture-codesign/references/verification.md): the driver per app type, evidence conventions, the probe list; read during the interview.
- [../architecture-codesign/references/diagrams.md](../architecture-codesign/references/diagrams.md): read before drawing the navigation diagram.
- [references/pstack-LICENSE.txt](references/pstack-LICENSE.txt): the licence of the original this skill adapts.

## Provenance

Adapted from pstack's `create-verification-skill` and `maintain-verification-skill` and their feature-map example, by poteto (Lauren Tan), MIT licensed, at https://github.com/cursor/plugins/tree/main/pstack.
What changed for this family: Claude Code project-skill paths and loading rules, the evidence conventions shared with the codesign and plan-execution skills, the navigation diagram and drafted markers in the map, the build-identity and hardware interview questions, the maintenance loop folded into the generated skill, the hand-off's human test, and (after the first weeks of use) the fidelity register, the second views, the Sources lines with the self-check and its hook, the suite manifest, the live tier, and the verifier contract with the registry entry that the `/verify` orchestrator scopes a change through.

## Maintaining this skill

- Revisit when Claude Code changes skill discovery or frontmatter, when a driver in the verification reference changes, and after the first real generation on a new stack, folding what the interview had to discover the hard way back into section 1.
- Revisit after a live incident a generated skill did not predict: the gap goes into the interview's fidelity question and the template's register as a row others can recognise, and the probe that would have shown it into the live-tier guidance.
- Keep the four feature-file H2s, the Status and Sources lines, and the self-check's exit codes stable; the plans, the hook, and the maintenance loop depend on them.
- Keep the verifier contract stable too: the `/verify` orchestrator reads only what [references/verifier-contract.md](references/verifier-contract.md) names, and every generated skill is a copy, so a change goes into the contract first, then the templates, then each copy, with the hand-off saying which copies still lag.
