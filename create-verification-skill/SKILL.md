---
name: create-verification-skill
description: Generates a project-local verification skill at `.claude/skills/verify-<app>/` that drives an application the way a user does (launch, doctor, drive, evidence, cleanup), installs the harness the app needs (a debug-only driver entry point, launch and doctor recipes, the agent's driver server registration, the setup docs for the next machine), seeds the feature map, then proves the skill by running it once before handing it over. Use whenever a repository has no scripted way to prove UI, desktop, CLI, or service behaviour, whenever the user asks for a verification skill, a verify skill, a feature map, a control skill, an app-driving harness, or "a way for the agent to use the app as a user", and whenever a plan's verification phase finds no `verify-<app>` skill to drive through. Any language or platform. Not for running a verification; that is the generated skill's job, so when `verify-<app>` already exists, use it instead. Adapted from pstack's create-verification-skill by poteto (MIT).
---

# Create a verification skill

Every application a team keeps changing needs a scripted way to drive the real thing and prove behaviour: launch it, exercise a feature the way a user would, and capture evidence a reader can check in a minute.
This skill generates that as a project-local skill tailored to the repository, with a feature map as the maintained list of what the application does from the user's side.
The output is written for the next agent, not for a human: it is read cold, mid-task, by a session that has never seen the application, so every command is literal, every observable is named, and every claim is grounded in what the interview found.

Verification skills are first-class in this skill family.
The architecture-codesign skill writes a verification phase that drives through `verify-<app>` when one exists, the plan-execution skill runs that phase through it, and a plan that changes a user-facing feature updates the feature's map file in its docs phase.
The feature map is therefore the repository's verification source of truth, and the plans keep it current.

## What gets generated

```text
.claude/skills/verify-<app>/
  SKILL.md          launch, doctor, drive, evidence, cleanup, helpers, feature map, maintenance
  features/
    README.md       index, baseline preconditions, driving conventions, proof rules, navigation diagram
    <feature>.md    one per user-facing feature, four fixed sections
  scripts/          helpers the skill ships, when a task-runner recipe is not the better home
```

Beside the skill, the harness it depends on lands in the product repository (step 3): the drivable entry point, the launch and doctor recipes, and the docs for the next machine.

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

## 3. Make the harness exist and reachable

The interview and the probe say what the driver needs; this step puts it in place, because a skill that assumes a harness nobody installed is read cold by an agent that cannot install it mid-task.
"Available to agents" means all of the following, and each one found missing is done here, not deferred to the hand-off:

- **A drivable build in the repository.** When the driver needs an entry point or a build flag (a debug-only `test_driver/app.dart` that enables a driver extension, a dev server started with a debug port, a CLI built with a test flag), it lives in the repository as committed scaffolding, named for what it is, with its dependency declared where it cannot ship (a dev dependency, a test target), so the next machine builds it from a clean clone.
- **A launch recipe and a doctor recipe in the task runner.** The launch recipe starts the drivable build and prints what the agent needs to connect (a tooling-daemon URI, a port, a VM service URL).
  The doctor recipe proves the whole path end to end (build, launch, connect, one wait, one capture to disk, stop) and exits non-zero when it fails, so an agent and a fresh machine have one command that says whether driving is possible.
  Prefer the repository's task runner over a raw command, because the recipe keeps the flags right when they change.
- **The agent's driver tool registered on this machine.** An MCP server (the Dart MCP server, Playwright MCP, Chrome DevTools MCP) or a CLI the skill calls must be reachable from the agent: register it (user scope when it is per machine, project scope only when every teammate should get it), confirm with `claude mcp list` or the tool's own health check, and note platform quirks such as a batch-file wrapper needing `cmd /c` on Windows.
  Record the registration command per OS where the next machine's reader will look, because this step lives outside the repository and is the one most often missing.
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
- **Doctor.** One read-only check that answers "is this instance worth driving?": process up, right build, port owned by this run, auth valid, the fake or device connected.
  An agent runs it first whenever anything looks off, and again after any failed drive.
  The doctor recipe from step 3 is this check's strongest form; the skill names it and says what its exit codes mean.
- **Drive.** The harness recipe with real handles from this repository: widget keys, accessible names, route paths, prompt strings, endpoints, never coordinates or tab order.
- **Evidence.** What to capture for a proof and where it goes, with the proof standards: exercise the real user path, not internal setters or test-only endpoints; capture the action and the resulting state, not only the final screen; verify side effects (files written, rows inserted, messages sent) beside what is visible; mocks only where a production boundary already isolates the external system; a dry-run or test mode is verified by observing what it skips, not by trusting its name.
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

- The README carries the baseline preconditions, the driving conventions (including any shorthand the feature files use for driver calls, defined once), the proof and skip-reporting rules, the feature entry contract, and the index.
- When the app has more than three screens or commands, the README also carries a mermaid navigation diagram: screens or commands as nodes, user entry points as edges, each node naming its feature file, at most twenty-five nodes, drawn per [../architecture-codesign/references/diagrams.md](../architecture-codesign/references/diagrams.md).
  An agent reading the map cold sees where the feature sits before it reads the recipe.
- Each feature file answers, from the user's point of view: what the feature is, how to reach it, how to drive it with the harness, and what observable end state proves it works.
  The four H2s are `Sub-features`, `How to get to it (user POV)`, `Driving it with <harness>`, and `Gotchas`, in that order, because the maintenance pass and the plans rely on the shape.
- Sub-features carry short ids (`search-empty`, `create-cancel`) so evidence and findings can name them.
- Every file starts, under its H1, with `Status: drafted from source, not yet driven`, removed only when a run has driven that file's recipe end to end; the map stays honest about what is proven and what is inferred.
- Keep implementation detail out: user paths, stable handles, required state, commands, and observable proof only.

## 6. Prove it before handing it over

Run the generated skill's own instructions end to end once: launch, doctor, drive one mapped feature (one is enough, the map exists so later runs cover the rest), capture evidence, clean up.
After cleanup, confirm the evidence still exists at the named location; a cleanup that eats the proof fails this step.
Fix what fails, and run the generated cleanup after every failed iteration too, so broken attempts do not strand processes and ports.
The proof run's evidence lands under `<app>_verification/<YYYY-MM-DD>/<feature-id>/` with a `walkthrough.md`, the same conventions a plan's verification phase uses.
Remove the drafted marker from the proven feature only.
When this session has no screen, prove everything that runs headless and list the interactive-only steps under "Not yet proven" in the hand-off with the exact steps, instead of claiming them.
A generated skill that was never executed is a draft, and the hand-off says so.

## 7. Hand over

Tell the user, in one message:

- Where the skill is, which feature is proven, which are drafted, and the harness pieces added to the product repository (entry point, recipes, docs) with the reason, plus what was registered on this machine and is therefore per machine.
- Gaps the interview found that only the author can close: no build identity, no isolation, a step that needs real hardware.
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

## Reference files

- [references/verify-skill-template.md](references/verify-skill-template.md): the skeleton of the generated SKILL.md, section by section; read before writing one.
- [references/feature-map-example/](references/feature-map-example/): a complete feature map for a small fictional app with a desktop UI and a CLI; copy the shape, not the content.
- [../architecture-codesign/references/verification.md](../architecture-codesign/references/verification.md): the driver per app type, evidence conventions, the probe list; read during the interview.
- [../architecture-codesign/references/diagrams.md](../architecture-codesign/references/diagrams.md): read before drawing the navigation diagram.
- [references/pstack-LICENSE.txt](references/pstack-LICENSE.txt): the licence of the original this skill adapts.

## Provenance

Adapted from pstack's `create-verification-skill` and `maintain-verification-skill` and their feature-map example, by poteto (Lauren Tan), MIT licensed, at https://github.com/cursor/plugins/tree/main/pstack.
What changed for this family: Claude Code project-skill paths and loading rules, the evidence conventions shared with the codesign and plan-execution skills, the navigation diagram and drafted markers in the map, the build-identity and hardware interview questions, the maintenance loop folded into the generated skill, and the hand-off's human test.

## Maintaining this skill

- Revisit when Claude Code changes skill discovery or frontmatter, when a driver in the verification reference changes, and after the first real generation on a new stack, folding what the interview had to discover the hard way back into section 1.
- Keep the four feature-file H2s stable; the plans and the maintenance loop depend on the shape.
