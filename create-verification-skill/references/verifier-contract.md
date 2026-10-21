# Verifier contract

Read this at step 3 of the generator, and before changing the interface of any script a generated skill ships.
A repository with more than one verify skill needs one place that says which verifier a change puts in scope, how to run it into a shared evidence folder, and what proves the run happened on the code under review.
That is the job of the `/verify` orchestrator, a skill the product repository keeps beside its verify skills (`.claude/skills/verify/` in org-repo), and this file is the contract between it and every generated skill: the four things the orchestrator reads, and nothing else.
The contract is kept small on purpose, because every generated skill is a copy the generator never revisits; the orchestrator's preflight checks that each registered skill still honours it, which beats keeping copies in sync.

Contents:

- The feature files
- The launch record
- The suite runner
- The registry entry
- What the orchestrator adds, so a generated skill does not
- Changing the contract

## The feature files

Every file under `features/` except the README starts with an H1 and then, within its first lines, carries:

- `Status: drafted from source, not yet driven`, or `Status: driven on <YYYY-MM-DD>` followed by free text.
- `Sources:` followed by one or more globs in backticks, separated by spaces, relative to the repository root, naming the source that renders the feature and never tests.

The orchestrator expands each glob and maps every changed file in a verifier's scope to the features that claim it; those features, through the steps files they name and the suite manifest's ids for them, are the verifier's drive list.
A changed file in scope that no feature claims widens the drive list to the whole suite, because the map cannot say which recipe the change reaches.
The self-check already parses both lines with `STATUS_RE` and `SOURCES_RE` in [selfcheck-template.py](selfcheck-template.py); keep the formats unchanged.

## The launch record

`scripts/launch.py start|wait|status|stop --run <dir>` owns one instance for a run and writes `<run>/launch.json`.
Three of its fields are the contract:

- `status`, which reaches `ready` when the instance is drivable.
- `git_head`, the short sha of `HEAD` at launch.
- `git_dirty_paths`, the paths under the verifier's sources that had uncommitted changes at launch, empty when the tree is clean there.

The orchestrator refuses to stamp a run whose `git_head` is not the top of the range it verifies, or whose `git_dirty_paths` is not empty, because the evidence would show a build the reviewer cannot see.
The other fields (pids, ports, an extension's modification time, what was preserved and restored) are the skill's own.

## The suite runner

`scripts/suite.py --run <dir> [--only <id>,<id>]` drives the recipes in the manifest's order (all of them, or only the comma-separated ids), accepts any run directory, exits 0 only when every recipe passed, writes `<run>/suite.md` with one row per recipe, and writes `<run>/<feature-id>/walkthrough.md` for each feature it drove.
A recipe skipped as unreachable is a row that says so, never a pass.
The orchestrator passes `<parent>/<skill name>/` as the run directory, and `--only` with the drive list when it is narrower than the suite.

## The registry entry

The product repository keeps `.claude/verifiers.toml` at its root, committed and hand-written, with one table per verifier, per headless gate, and per deliberately unverified target.
Targets are directories relative to the repository root at the granularity the repository's dependency declarations use (`projects/<name>`, `libs/<name>` in org-repo).

```toml
[[verifier]]
skill = "verify-demo-app"
proves = ["projects/webapps", "libs/rtp-app-kit", "libs/rtp-client"]
runtime_peers = ["projects/rhythm-demo", "libs/rtp-host"]
live_only = []
ports = [8079]
suite = "uv run --no-sync python .claude/skills/verify-demo-app/scripts/suite.py --run {run}"
selfcheck = "just demo-app-verify-check"

[[verifier]]
skill = "verify-rtp-demo"
proves = ["projects/rhythm-demo", "libs/rtp-host", "libs/rtp-core", "libs/bone-id", "projects/intent-routing", "projects/ml-serving"]
runtime_peers = []
live_only = ["libs/rtp-host/src/libs/rtp_host/pipeline/board_*.py", "libs/rtp-core/rust/rtp-nodes/src/bluetooth.rs"]
ports = [8079, 8088]
suite = "uv run --no-sync python .claude/skills/verify-rtp-demo/scripts/suite.py --run {run}"
selfcheck = "just rtp-demo-verify-check"

[[verifier.prerequisite]]
when = "libs/rtp-core/rust/**"
run = "just rtp-develop --release"

[[gate]]
name = "dc-smoke"
proves = ["projects/data-collections"]
run = "just dc-smoke"

[[unverified]]
target = "projects/webviz"
reason = "transport-only tool with no driver"
```

- `skill`: the directory under `.claude/skills/`.
- `proves`: the targets whose change puts this verifier in scope on its fake tier; a change under a target that reaches one of these through the repository's dependency graph counts too.
- `runtime_peers`: targets the app talks to while it runs without importing them (a pipeline over HTTP, a server, an emulator); a change there puts the verifier in scope on its live tier only, because the fake stands in for the peer.
  The build graph misses these edges: the demo app is coupled to its pipeline only through the API, so without this line an infra change under the pipeline scopes the pipeline's verifier and not the app's.
- `live_only`: globs within the verifier's scope whose change the fidelity register sends to the live tier; the orchestrator lists a change there under Not verified unless the author ran that tier.
- `ports`: the ports the verifier owns or refuses to share; verifiers with a port in common run one at a time.
- `prerequisite`: a command to run before the suite when a changed file matches `when`, such as a native extension rebuild after a change under its sources.
- `suite` and `selfcheck`: the commands the orchestrator runs, with `{run}` replaced by the run directory.
- `gate`: a deterministic recipe with no feature map, run when a target in its `proves` is in scope, passing on exit 0.
- `unverified`: a target no verifier or gate reaches, with the reason, so the orchestrator can say so in the PR body instead of staying silent.

The repository's coverage check (`tools/check_verifiers.py` behind a recipe and a pre-commit hook in org-repo, or the equivalent elsewhere) fails when a target is neither reachable into some `proves` through the dependency graph nor declared `unverified`, when a target is both, and when an entry names a skill directory, suite, or recipe that does not exist.
When the repository has no registry yet, step 3 creates it with this skill's entry and the check, because a verifier missing from the registry is never put in scope.

## What the orchestrator adds, so a generated skill does not

The dependency closure (from the repository's own declarations, `ci-deps.txt` in org-repo), the severity of a change, the choice of the stack range, the shared evidence folder with its index, the PR bodies, and the stamp that ties a PR body to the verified content belong to the orchestrator and to the repository's scope tooling.
A generated skill never computes any of them; it provides the four things above and does its own launch, doctor, drive, evidence, and cleanup.

## Changing the contract

Change this file first, then [verify-skill-template.md](verify-skill-template.md) and [selfcheck-template.py](selfcheck-template.py), then each generated copy, and say in the hand-off which copies still lag.
Keep the `Status:` and `Sources:` formats, the three `launch.json` fields, the suite runner's two options and its exit rule, and the registry keys stable; the orchestrator reads only those.
