# Changelog

## 0.1.0 - Architecture refactor

Restructured from the original prototype into an installable, src-layout
package (`pip install nannokit.dialogs`) with a shared `core` module used
by both `messagebox` and `filedialogs`.

### Fixed

- **`OpenFile.show()` / `OpenFolder.show()` could not resolve the running
  App.** The previous implementation tried `from textual.app import
  get_app` (no such function exists in any released Textual, including
  0.82.x - this always raised `ImportError`) and then `App.active_app()`
  (not a valid call either). Both dialogs would raise `RuntimeError` on
  every call. Replaced with `DialogManager`, the same resolution pattern
  `messagebox` already used, now shared by every dialog and verified
  against Textual 0.82.0's real `active_app` context var.
- **`super().show(...)` from inside a `@classmethod`** in `OpenFile.show`
  and `OpenFolder.show` resolved to the *parent class's* bound method
  rather than re-entering shared logic on `cls` - in practice harmless
  here because the parent's `show` did the real work anyway, but a subtle
  trap for the next dialog added the same way. New dialogs build their own
  instance and call `cls._present(instance)` directly.
- **`multiselect` was accepted but silently ignored** in both dialogs.
  Implemented for `OpenFile` (press `M` to mark/unmark files); callback
  receives `list[Path]` instead of `Path` when enabled. Not exposed on
  `OpenFolder`, mirroring `FolderBrowserDialog`'s own lack of multiselect.
- **No validation before closing.** A selection that didn't exist on disk
  (typo, file removed mid-browse) was returned straight to the callback.
  Added `must_exist` (mirrors `OpenFileDialog.CheckFileExists`), with an
  inline, recoverable error message instead of dismissing with a bad path.
- **`self.title = ...` shadowed `Screen.title`**, a built-in Textual
  reactive (confirmed via inspection against 0.82.0). Renamed to
  `self.dialog_title` in both `MessageDialog` and `FileSystemDialogBase`.
- **Relative `CSS_PATH` via a separate `bindings.py` constant module**
  removed; styles are now resolved with `Path(__file__).resolve()`
  directly in each dialog module - one less indirection, and robust
  regardless of the importer's current working directory.

### Added

- `DialogManager.attach()` / `.detach()` / `.resolve_app()`, shared by
  `messagebox` and `filedialogs` (previously `messagebox`-only).
- `DialogScreenBase`, a shared `ModalScreen` base giving every dialog
  Escape-to-cancel for free, with a single `_cancel()` hook subclasses
  override to also notify a user callback.
- `FilterableDirectoryTree`: hidden-file filtering (`show_hidden`) and
  glob-pattern filtering (`filters=["*.py", ...]`), mirroring
  `OpenFileDialog.Filter`.
- An editable location field - type or paste a path and press Enter to
  jump there, instead of only being able to browse via the tree.
- `SaveFile`, a new dialog (equivalent to `SaveFileDialog`) demonstrating
  that a dialog needing genuinely different behaviour (an overwrite
  prompt) only needs to override one method, and that dialogs can compose
  with `messagebox` from inside the package itself.
- `py.typed` marker and a `pyproject.toml` (replacing `setup.py`) using a
  `src/` layout with `supernanno` kept as an implicit PEP 420 namespace
  package, so future sibling extensions can install alongside this one.
- A `pytest` + Textual `Pilot` test suite (`tests/`) exercising the actual
  dialogs end-to-end rather than only import-checking them.
