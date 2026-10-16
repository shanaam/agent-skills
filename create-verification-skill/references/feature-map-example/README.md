# Notes verification map

This directory is the maintained source for verifying the user-facing behaviour of Notes, a fictional Flutter desktop app with a `notes` CLI over the same store.
Read this index before driving the app, then use the matching feature file as the recipe.
The app is invented; copy the shape of this map, not its content.

## Baseline preconditions

- Launch Notes with `just notes-app --driver`, the debug-only entry point that enables the driver extension, with `NOTES_DATA_DIR` set to a disposable directory under `notes_verification/<date>/data/` so runs do not share state.
- The VM service URI is printed on stdout; connect the Dart MCP server to it before the first drive.
- Seed notes titled `Quarterly plan` (body `Draft budget`) and `Grocery list` with `just notes -- seed --dir <data dir>`.
- Run `just notes-doctor` and require the expected data directory and the build id, the git sha shown under Settings > About and by `notes --version`.
- Never drive an instance this run did not start; Notes allows one instance per data directory.

## Driving conventions

- Start every recipe from the baseline state unless its preconditions say otherwise.
- UI actions go through the Dart MCP server's `flutter_driver_command`.
  In recipes, `tap key:<k>` means command `tap` with finder `ByValueKey('<k>')`, `tap text:"<t>"` means `tap` with `ByText('<t>')`, `type key:<k> "<text>"` means `tap` on that key followed by `enter_text`, `wait text:"<t>"` means `waitFor` with `ByText('<t>')`, `read key:<k>` means `get_text`, and `screenshot <path>` means the driver `screenshot` command saved to that path.
- Terminal actions go through `just notes -- <command>`; the recipe keeps the venv and the data directory flag.
- Prefer widget keys and visible text over positions; keys are listed in each feature file and declared in `lib/keys.dart`.
- Treat every command as literal; keep quoted names and flags unchanged.
- Restore seeded data after a mutation; do not remove proof artifacts during cleanup.

## Proof and skip reporting

- Capture the user action and the resulting state, not only the final screen.
- UI proof is a driver screenshot to `notes_verification/<date>/<feature-id>/<nn>_<what>.png`, taken after the `wait` that proves the state, with the `read` text saved beside it as `<nn>_<what>.txt`.
- CLI proof includes the command, stdout, stderr, and the exit code.
- Mutation proof includes a second, read-only view of the stored value: reopen from the list, or `notes show`.
- Record the feature id, the entry point used, and the build id with every artifact in that feature's `walkthrough.md`.
- Report an unreachable path with the attempted command and the unmet precondition.
- Do not report a skipped entry point as verified through a different path.
- A state the screen mirrors from the store or the sync service is proven by its second view agreeing, not by the screen's own label.

## Second views

| On screen | Second view on the fake | Second view on the real system |
|---|---|---|
| The `Synced` badge on a note | none (the fake store never syncs) | `notes status --format json` `pending` is 0 |
| The note list after a save | `notes show <title>` on the data directory | the same, after `notes sync` |

## Fidelity register

What the fakes do not model, and the transition in which the difference shows; a plan whose change touches one of these sends that journey to the real system.

| The fake | The real system | Shows after | Check on the real system |
|---|---|---|---|
| The in-memory store (`NOTES_FAKE_STORE=1`) never fails a write and never reorders | The disk store refuses a write while a sync holds the lock | A save during a sync | `notes sync &` then a save: the editor shows `Saved after sync` |
| No sync service | The service can be offline; the `Synced` badge then lies for up to 30 s | A save with the network down | `notes status --format json` `pending` after an offline save |

## Suite order

`scripts/steps/suite.txt` drives `create-note` then `search` with no reset between them, because search's seeded `Quarterly plan` is what create-note leaves behind; a reset before search would empty the store.

## Feature entry contract

Each feature file starts with an H1 title, a `Status:` line (`drafted from source, not yet driven`, or `driven on <date>`), a `Sources:` line with the globs of the app source that renders the feature, and one paragraph describing the user-visible behaviour.
The self-check uses `Sources:` to claim every user-facing file and to flag a feature as stale when those files change after its last drive.
It then uses exactly four H2 sections in this order.

1. `Sub-features` lists short ids with one line for each behaviour.
2. `How to get to it (user POV)` lists every user entry point and the transitions that lead into the feature (after a sync, after a failed save).
3. `Driving it with <harness>` starts with `Preconditions:` and uses labelled bullets that pair each user action with an exact command and an observable result, ending with a `Proof` bullet.
4. `Gotchas` lists traps that can waste or invalidate a verification run.

Keep implementation details out of the map; name only user paths, stable handles, required state, commands, and observable proof.

## Navigation

```mermaid
flowchart LR
    List["Note list (home)"]
    Editor["Note editor<br/>create-note.md"]
    Search["Search dialog<br/>search.md"]
    Store[("note store")]
    CLI["notes CLI"]
    List -->|New note button, key n| Editor
    List -->|Search button, key /| Search
    Search -->|open result| Editor
    Editor -->|Save, Cancel| List
    CLI -->|notes create| Store
    CLI -->|notes search| Store
    List --- Store
```

## Features

- [Create a note](./create-note.md) covers editor and CLI creation, cancellation, persistence, and cleanup.
- [Search notes](./search.md) covers toolbar, keyboard, and CLI search with matching, empty, and clear states.
