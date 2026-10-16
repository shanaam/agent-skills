# Verification: using the built thing as a user

Read this when a plan's verification phase starts, and when writing the verification phase into a plan.
Green tests show the code does what the tests say; the design decisions were about behaviour a user sees, so the verification phase shows that behaviour and leaves evidence a human can check in a minute.
Tool facts below were verified on 2026-10-09; tools in this area change within months, so re-check a tool's docs before relying on a detail that matters.

Contents:

- The verify skill comes first (the self-check, the two tiers, second views, transitions, the environment baseline)
- Evidence conventions
- The evidence contract
- Choosing the journeys
- Tool per app type
- Wait, then capture
- Performance evidence
- Fresh eyes
- The human test (last step)
- Probe before relying on it

## The verify skill comes first

- When the repository has `.claude/skills/verify-<app>/`, it is the harness: its Launch, Doctor, Drive, Evidence, and Cleanup sections replace the tool choice below, and `features/<feature>.md` is the recipe for each changed journey.
- When it does not, the plan's Phase 0 creates it with the sibling `create-verification-skill` (interview, skill, feature map, one proven feature), so the verification phase drives through something that has already worked once on this machine.
- The skill's self-check (`just <app>-verify-check`, `scripts/selfcheck.py`) is the gate on the map itself: it fails when a user-facing source file no feature claims exists, and warns when a feature's sources changed after its last drive.
  Run it in Phase 0 (a stale feature before the plan is not the plan's regression), at the end of the docs phase (every surface the plan added is claimed), and first in the verification phase (the features it still warns about are the drive list).
- A plan that changes or adds a user-facing feature names it in the Design decisions' Verifier impact line and in the phase that changes it, updates that feature's map file in its docs phase (file, `Sources:` line, steps file, suite entry, index, navigation node), and sets the feature's `Status:` back to drafted until the verification phase drives it.
- Two tiers: the fake tier is every recipe the app's fakes can run, driven through the skill's suite; the live tier is the probes under `scripts/live/` and the live recipe, run against the real system only when the author has asked.
  The map's fidelity register decides which tier a journey needs: a change that touches a gap the fake has (a control applied on the next data instead of at once, a clock that restarts, a queue that evicts, a reconnect, a shared port, a service that degrades) is proven on the live tier, because a recipe on the fake passes before and after a bug that lives in a gap; the demo app's four live failures of 2026-10-11 were all of this kind, each proven on the fake the day before.
- Offline tier, when the app or the stack it launches has edges that leave the machine and runs where the network may be absent or half-working: a launch on a machine warmed by an earlier online run, with egress refused rather than absent (a tripwire proxy that logs and refuses every attempt), must reach health and serve the journeys the map names.
  The register carries one row per off-machine edge, and a change that touches the launch path, model loading, a server, a network client, or runtime assets runs this tier and reports it beside the other two; a demo stack lost its intent server to a hub's 500 at startup with every byte of the model on disk, because nothing had ever launched it with the network refused.
- Second views: a state the screen mirrors from a backend is proven by the backend's own reading agreeing (a status endpoint, a pane row, a CLI query), listed in the map's second-views table; the screen's own label is the app's belief and passes on a fake by construction.
- Transitions: the journeys to drive include the feature after the transitions its map file names (after a take, after the device came off, after a reconnect), not only from the baseline, because that is where the live failures sat.
- Environment baseline: a live pass starts with the skill's baseline probes (link cadence, answer latency, queue counters) saved under the evidence folder, so a failure on a degraded link is classified as environment before product; the same code answered a probe in 1.6 s on one connection and 23.9 s on the next.
- Contracts the app consumes (the recipes and endpoints it shells out to or calls at startup) are headless criteria with their exit codes and payload keys, checked from a shell with no app running; a shell boundary (a task runner on Windows reporting exit 3 as 1) is where a fresh reviewer found what the drives had passed over.
- The table below is for choosing the driver when generating a verify skill, and for one-off verification in a repository with no app to map.

## Evidence conventions

- Everything lands under `<descriptive_name>_verification/<YYYY-MM-DD>/`, gitignored (`*_verification/`), beside the plan.
- `before/` holds the Phase 0 baseline (profiles, and screenshots of the old behaviour when they help the comparison); `after/` holds the new build's evidence.
- Screenshots are PNG, named `<nn>_<what-it-shows>.png` in journey order, so the folder reads as a story without the notes.
- `walkthrough.md` sits beside them: one section per journey, one line per screenshot naming the file, what it shows, and what was expected, plus the exact commands or steps that produced it so the human test can repeat any of them.
- A profile is saved in a form that opens without the tool that made it (an SVG flame graph, or a Speedscope JSON), and `walkthrough.md` carries the one-line reading of the before/after pair.
- Evidence is positive and fresh: every artifact is new (modified after the build it claims to show), non-empty, and contains the expected content (the state text, the status code, the widget label), because an empty trace or a skipped step passes a presence check and proves nothing.
- The evidence index records what was built: the commit or tree state, and for native extensions the rebuilt artifact's timestamp, so a stale binary cannot pass as the new one.
- The hand-off section of the plan carries an evidence index: a table of criterion, command, artifact, result, with images embedded and profiles linked.

## The evidence contract

Write it before the code, as part of the plan's verification phase, so the implementer and the verifier read the same definition of done:

- For each acceptance criterion: the command that exercises it, the observable (a text, a status code, a widget, a metric), the artifact path under the evidence folder, and the pass rule.
- Deterministic gates first: every criterion that can be a recipe with a non-zero exit on failure becomes one (`just verify-<feature>` or the repo's equivalent), and that recipe is the gate an unattended run stops on.
  Screenshots are evidence for the human; they are not the gate.
- Say which steps need an interactive desktop (a browser extension, computer use, a Windows window capture) and which run headless (Playwright, the Dart MCP server, profilers), so the headless part can run unattended and the rest is scheduled for a session with a screen.
- Bound the retries: on a failed check the agent fixes and reruns a small number of times, then stops with the failing evidence rather than loosening the check.

## Choosing the journeys

- Start from the design decisions: each decision that changes something a user sees or does is one journey.
- Add the failure paths the decisions named (the refusal, the retry, the empty state), because they are what the old build got wrong.
- Add the transitions into each touched feature that its map file names, and give the journey the tier the fidelity register says; a journey through a fake's gap on the fake tier proves nothing about the change.
- Skip journeys the plan did not touch; evidence for unchanged behaviour buries the signal.

## Tool per app type

Defaults for this stack, with the general rule after the table.

| App type | Default driver | Screenshot or evidence | Profile (before/after) |
|---|---|---|---|
| Flutter Windows desktop | Dart MCP server (`dart mcp-server`) driving a debug-only entry point that calls `enableFlutterDriverExtension()` before `main()`, launched by a `just` recipe with `--print-dtd` | Driver `screenshot` after `waitFor`; fallback: OS-level capture of the window rect (PowerShell `System.Drawing` or pywinauto `capture_as_image`); durable: an `integration_test` run writing `RepaintBoundary` PNGs | DevTools CPU profile export, `devtools_profiler_cli` `compare` for numbers; `--trace-startup` for launch time |
| Flutter macOS desktop | Same Dart MCP path; Claude Code computer use (macOS CLI only) for ad-hoc clicks | Driver `screenshot`; computer-use screenshot as fallback | Same |
| Flutter web | Playwright MCP headless, with `SemanticsBinding.instance.ensureSemantics()` in `main()` so the accessibility snapshot is not empty; Claude in Chrome when interactive | `browser_take_screenshot` with a filename; video via `--caps=devtools` for a flow | Chrome DevTools MCP `performance_start_trace` to a file |
| TypeScript or Vite web app | Playwright MCP headless, or Claude in Chrome interactively | `browser_take_screenshot`; console messages saved to a file | Chrome DevTools MCP trace; `node --cpu-prof` for build scripts |
| Python CLI or tooling | Run the `just` recipe; capture stdout, stderr, and the exit code to a log | The log is the screenshot; a golden diff against a fixture where output is stable | `py-spy record -o x.svg --format speedscope` on the same command |
| Long-running pipeline (Python host, native extension nodes) | Start through the supervised recipe, drive the HTTP or SSE control API with scripted calls, assert statuses and events, stop cleanly | Saved responses, the SSE transcript, the runner log excerpt, the QC report | `py-spy record --pid <host> --native --subprocesses --duration <s>` to SVG and Speedscope JSON, same workload before and after; `samply` for native-only hot spots |
| HTTP or SSE API | Scripted calls in a recipe, refusal paths included (409, 422) | Response bodies saved and diffed against expected JSON | `py-spy` on the server pid |
| Rust crate alone | The repo's Rust test and bench recipes, release builds | Bench table | `cargo flamegraph` (Windows via blondie, Linux via perf) or `samply` |
| Notebooks | Execute headless (`jupyter nbconvert --execute`) and check for error cells | The rendered HTML; PNG export of key figures | `py-spy` on the kernel pid if needed |

General rule for a stack not in the table: prefer the platform's own driver protocol (an accessibility tree, a driver extension, a CDP endpoint) over pixel-and-pointer automation, because it gives the agent state text to assert on; keep pixel capture for the human's eyes.

Driver notes, each verified on the date above:

- **Claude in Chrome** (`claude --chrome`, or `/chrome`): screenshots to disk, GIF recording of a flow, console and network; visible window, shares the logged-in profile; needs a direct claude.ai plan, so it is off under API-key auth, `claude -p`, and WSL.
- **Playwright MCP** (`npx @playwright/mcp@latest`): accessibility snapshot by default, `--headless`, `--output-dir`, `--caps=devtools` for tracing and video; what Anthropic's own evaluator harness used; Chromium, Firefox, and WebKit.
- **Chrome DevTools MCP** (`npx chrome-devtools-mcp@latest`): performance traces to a file, Lighthouse, heap snapshots, screencast; public preview, tool names have changed between releases.
- **Dart MCP server** (`dart mcp-server`, bundled with the SDK, experimental): `flutter_driver_command` with `waitFor`, `tap`, `enter_text`, `get_text`, `waitForTappable`, `screenshot`; the app must enable the driver extension from a debug-only entry point, which changes text-input behaviour and never ships in release.
  Launch the app from a recipe with `--print-dtd` and connect with the `dtd` tool's `connect` command; `launch_app` was not in the SDK 3.12 server's tool list.
  Apps with repeating animations need `set_frame_sync` with `enabled: "false"` first, or every widget command times out waiting for an idle frame.
  A command sent before `runApp()` fails with "No root widget is attached"; `waitUntilFirstFrameRasterized` is the one wait that does not need the root widget.
  `screenshot` returns the PNG inline to the agent, so a PNG on disk comes from a `flutter drive --use-existing-app=<vm service url>` driver script against the running instance, or from a small MCP stdio client that saves the inline image (org-repo's `verify-demo-app` skill ships one as `scripts/drive.py`).
  The printed VM service URL is served by the tool process, not the app, so the app's pid comes from the process tree under the launch recipe.
- **OS-level capture on Windows**: PowerShell `System.Drawing` `CopyFromScreen` over the window rect, or pywinauto with the `uia` backend; both need an interactive, unlocked desktop and a DPI-aware process, and real input events steal focus.
- **Computer use**: macOS only in the Claude Code CLI; a research preview on Windows in the desktop app; interactive only; screenshots are downscaled, so small text is unreadable.
- **WinAppDriver** is deprecated as of October 2026 in favour of the Appium wincore driver; do not start new work on it.
- **Patrol and Maestro** do not support Flutter on Windows desktop.

## Wait, then capture

- Wait for the post-condition before any screenshot: `waitFor` the widget or text (Flutter), a snapshot containing the expected text (web), or a polled API state; a screenshot taken on a timer shows the previous frame.
- Save the state text beside the image so the picture is not the only proof.
- Known stale-capture traps: the Flutter driver screenshot is documented as unreliable (a fixed wait, the raster thread out of step); browser automation cannot see native alert dialogs; Flutter web is invisible to accessibility snapshots without semantics enabled; the old binary still running, a cached page, or a stale native extension are the usual ways a walkthrough passes falsely.

## Performance evidence

- Profile only when a phase changed a hot path (a loop, a decoder, a render path, a query); a flame graph of unchanged code proves nothing.
- Same load before and after: the same input file, the same duration, the same flags, stated in `walkthrough.md`.
- One tool per runtime, release or profile builds only: `py-spy` for Python (with `--native` on x86-64 Windows and Linux to see native extension frames below the Python frames), `samply` or `cargo flamegraph` for Rust, the DevTools CPU profiler export for Dart and Flutter, a Chrome DevTools trace for the browser, `node --cpu-prof` for Node.
- Save an SVG where the tool makes one (it renders inline in markdown) and the Speedscope or tool-native JSON beside it; Speedscope opens most formats but exports no image, so the SVG or a screenshot of the flame chart is what the reader sees.
- Read the pair in one line: which frames shrank or grew, and whether that matches the decision's intent.

## Fresh eyes

- The session or subagent that wrote the code does not grade the evidence; hand the diff, the evidence contract, and the folder to a verifier that did not, with the question "does each artifact show the new behaviour rather than the old, and is the profile reading honest".
- Give the verifier the claim, the evidence, and the criteria, not the task; a verifier that re-solves the task brings its own error chain, and it is forbidden from editing code or tests.
- Tell the verifier to flag only gaps that affect correctness or the stated requirements; a reviewer asked to find problems will report some even when the work is sound, and chasing every finding produces defensive code and tests for cases that cannot happen.
- The two questions the verifier answers, each with the same weight: "the plan asked for X; does this do Y instead?", and "is the code still in a shape a person or an agent can understand and change?".
  The second is a required finding category, not a courtesy: a second way to do what the code already did, an abstraction with one caller, a flag nothing reads, a bridge between two phases that nothing needs now, or a comment that explains how is reported like a correctness gap, because the next session pays for it.
- The verifier reads the hand-off text and any PR description as critically as the code; agents write convincing descriptions of work that was not done.
- The verifier reports mismatches as findings in the plan's hand-off, not as fixes; the fix is a task in the plan like any other.
- Every claim in `walkthrough.md` points at a file or a tool result from the session that produced it; a status line without evidence behind it is removed, not softened.

## The human test (last step)

- One to three commands in the author's shell, in order, each followed by what to expect and the single observation that means it passed.
- The first command re-runs the strongest deterministic gate (the verify recipe); the second gets the author to the new behaviour fastest; the third opens the evidence folder or the flame graph.
- Prefer the repo's own recipes (`just <recipe>`) over raw commands, so the test keeps working when the flags change.
- State the preconditions in one line (which branch, which device powered on, which env var) so the test does not fail for a reason unrelated to the change.
- Say what the agent could not verify (real hardware, a GPU environment, an interactive-only tool unavailable in the run), so the human test targets those gaps instead of repeating the agent's work.
- Keep it under five minutes of the author's time; anything longer belongs back in the deterministic gate.
- Never ask the human to run the full suite as the human test; the agent did that, and the human test is for the eyes.

## Probe before relying on it

Open questions on 2026-10-09, each a ten-minute check before a plan hard-codes the step:

- The Dart MCP driver `screenshot` worked on a Flutter 3.44.4 Windows debug build on 2026-10-09 (a 1084x681 PNG of the window contents); re-check after a Flutter upgrade or a renderer change, and keep the OS-level capture fallback in the plan.
- Whether `binding.takeScreenshot` works on Windows desktop in the current Flutter; the feature request has been open since 2023, so expect the `RepaintBoundary` route instead.
- Where Playwright MCP writes its trace file; set `--output-dir` and list it before relying on the path.
- Whether `py-spy` can attach on Windows to a process started from another terminal without elevation.
