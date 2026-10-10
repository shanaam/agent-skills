# Create a note

Status: driven on 2026-10-09 (illustrative; the app is fictional).

Create note lets a user save a titled note from the editor or the CLI, cancel an unfinished draft, and confirm the saved note from a second user-facing view.

## Sub-features

- `create-open` opens a blank editor from each entry point.
- `create-save` persists a title and body.
- `create-cancel` discards an unfinished draft.
- `create-cli` creates the same note shape from the terminal.

## How to get to it (user POV)

- Choose the `New note` button in the list toolbar.
- Press `n` while focus is outside a text field.
- Run `notes create --title <title> --body <body>` in a terminal.

## Driving it with the Dart driver and the notes CLI

Preconditions:

- Notes is healthy per `just notes-doctor`, on the disposable data directory.
- No note is titled `Release checklist`.

- **Open editor.** Choose `New note`.
  Run `tap key:new-note`, then `wait text:"Note editor"`.
  The editor appears with focus in the title field, and `read key:editor-title` is empty.
- **Enter content.** Type the title and body.
  Run `type key:editor-title "Release checklist"` and `type key:editor-body "Tag and publish"`.
  `read key:save-note` reads `Save note` and the button is enabled.
- **Save note.** Choose `Save note`.
  Run `tap key:save-note`, then `wait text:"Note saved"`.
  `read key:note-heading` reads `Release checklist`.
- **Confirm persistence.** Return to the list and reopen the note.
  Run `tap key:nav-all-notes`, `wait text:"Release checklist"`, then `tap text:"Release checklist"`.
  The editor shows both saved values.
- **Cancel draft.** Open a new note, enter `Discard me`, and cancel.
  Run `tap key:new-note`, `type key:editor-title "Discard me"`, `tap key:cancel-note`, then `wait text:"All notes"`.
  `read key:note-list` does not contain `Discard me`.
- **CLI entry.** Create a second note from the terminal.
  Run `just notes -- create --title "CLI note" --body "Created from terminal" --format json`.
  Exit code `0`; stdout contains the new note id and title.
- **Proof.** Show both saved notes in the list.
  Run `tap key:nav-all-notes`, `wait text:"CLI note"`, then `screenshot notes_verification/<date>/create-note/01_list.png` and save `read key:note-list` to `01_list.txt` beside it.
  Both artifacts show `Release checklist` and `CLI note`.

## Gotchas

- Pressing `n` while a text field has focus types the character instead of opening the editor; tap the list background first.
- Titles are trimmed on save; assert the rendered heading, not the draft field.
- A `Note saved` status alone is insufficient proof; reopen the note from the list.
- The driver's `enter_text` replaces the field's text; it does not append.
- Remove `Release checklist` and `CLI note` in cleanup with `just notes -- delete --title <title>`, and keep their proof artifacts.
