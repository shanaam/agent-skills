# Search notes

Status: drafted from source, not yet driven.

Search lets a user find notes by title or body text, open a matching note, and tell no matches apart from an unavailable search.

## Sub-features

- `search-open` opens search from each supported entry point.
- `search-match` returns title and body matches without changing note data.
- `search-open-result` opens a result in the note editor.
- `search-empty` shows a complete empty state for a query with no matches.
- `search-clear` removes the query and restores the recent-notes view.
- `search-cli` returns the same matching notes from the terminal.

## How to get to it (user POV)

- Choose the `Search` button in the list toolbar.
- Press `/` while focus is outside a text field.
- Run `notes search <query>` in a terminal.

## Driving it with the Dart driver and the notes CLI

Preconditions:

- Notes is healthy per `just notes-doctor`, on the disposable data directory.
- The data directory contains `Quarterly plan` with body text `Draft budget`.

- **Toolbar entry.** Choose the `Search` button.
  Run `tap key:search-open`, then `wait text:"Search notes"`.
  The search dialog appears with focus in its query field.
- **Keyboard entry.** Close the dialog, focus the list, and press `/`.
  Run `tap key:search-close`, `tap key:note-list`, then `flutter_driver_command` `send_text` `/`, and `wait text:"Search notes"`.
  The same dialog appears and no slash is inserted anywhere.
- **Title match.** Type `quarterly`.
  Run `type key:search-query "quarterly"`, then `wait text:"Quarterly plan"`.
  `read key:search-results` contains `Quarterly plan` and not `Grocery list`.
- **Body match.** Replace the query with `budget`.
  Run `type key:search-query "budget"`, then `wait text:"Quarterly plan"`.
  `read key:search-results` still contains `Quarterly plan` with a body excerpt.
- **Open result.** Choose `Quarterly plan`.
  Run `tap text:"Quarterly plan"`, then `wait text:"Note editor"`.
  The dialog closes and `read key:note-heading` reads `Quarterly plan`.
- **Empty state.** Reopen search and enter `volcano`.
  Run `tap key:search-open`, `type key:search-query "volcano"`, then `wait text:"No matching notes"`.
  `read key:search-results` is empty.
- **Clear query.** Choose `Clear search`.
  Run `tap key:search-clear`, then `wait text:"Recent notes"`.
  `read key:search-query` is empty and the recent-notes region replaces the result list.
- **CLI match.** Search from the terminal.
  Run `just notes -- search "quarterly" --format json`.
  Exit code `0`; stdout contains one object whose title is `Quarterly plan`.
- **CLI miss.** Search for an absent value.
  Run `just notes -- search "volcano" --format json`.
  Exit code `0`; stdout is `[]`.
- **Proof.** Capture the populated result state.
  Run `tap key:search-open`, `type key:search-query "quarterly"`, `wait text:"Quarterly plan"`, then `screenshot notes_verification/<date>/search/01_results.png` and save `read key:search-results` to `01_results.txt` beside it.
  Both artifacts show the query and `Quarterly plan`.

## Gotchas

- Pressing `/` while the editor or the query field has focus inserts text instead of opening search.
- Results update after a short debounce; wait for the result list or the empty status, never a fixed sleep.
- Archived notes are excluded unless the user enables `Include archived`.
- The CLI defaults to human-readable output; use `--format json` for stable assertions.
- Opening a result changes the app state; reopen search before proving another query.
