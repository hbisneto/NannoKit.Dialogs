"""
nannokit.dialogs.filedialogs.base
=====================================

Shared screen and behaviour for every filesystem dialog
(:class:`OpenFile`, :class:`OpenFolder`, :class:`SaveFile`, and any
future dialog like a recent-files picker). Mirrors the shape of
.NET's ``FileDialog`` family: a navigable tree, an editable "location"
field, an optional filename field, and a primary action button whose
label varies per concrete dialog ("Open", "Save", "Select Folder"...).

Compared to the original prototype, this version fixes a few concrete
issues found while reviewing it against Textual 0.82.0:

- ``cls.show(...)`` called ``super().show(...)`` from inside a
  ``@classmethod`` - that resolves to the *parent class's* bound
  classmethod, not "the same method on ``cls``", so subclasses calling
  ``super().show(...)`` from their own ``show`` never actually reached
  this class's logic for anything beyond what they passed explicitly.
  Subclasses now build their own instance and call
  :meth:`FileSystemDialogBase._present` directly.
- ``from textual.app import get_app`` does not exist in Textual
  0.82.x (or any released version) - it would always raise
  ``ImportError`` and silently fall through to the next, also-fragile
  branch. App resolution is now centralized in
  :class:`~nannokit.dialogs.core.DialogManager`, validated against
  Textual 0.82.0's real ``active_app`` context var.
- ``self.title = ...`` was shadowing ``Screen.title``, a built-in
  Textual reactive (confirmed via inspection) - harmless today, but a
  foot-gun if a future version places a ``Header`` above one of these
  dialogs. Renamed to ``self.dialog_title`` throughout the package.
- A selection that doesn't exist (a mistyped filename, a path deleted
  between browsing and confirming) used to be returned straight to
  the callback. ``must_exist`` now validates before dismissing, with
  an inline, recoverable error message instead of a result the
  caller has to re-validate itself.
- ``multiselect`` was accepted as a parameter and silently ignored.
  It's now implemented (press ``M`` to mark/unmark a file) and
  changes the callback's result type from ``Path`` to ``list[Path]``.
- Every dialog now carries a ``priority`` (see
  :mod:`nannokit.dialogs.core.priority`) so it can never be silently
  interrupted by, or silently interrupt, a ``messagebox`` - see
  :mod:`nannokit.dialogs.core.queue` for how that's enforced.
"""

from __future__ import annotations

from pathlib import Path
from typing import Callable, Union

from textual import on
from textual.containers import Horizontal, Vertical
from textual.widgets import Button, Input, Label, DirectoryTree

from ..core import DialogPriority, DialogScreenBase
from .tree import FilterableDirectoryTree

_STYLES_DIR = Path(__file__).resolve().parent.parent / "styles"

#: What a filesystem dialog resolves to: a single path, several paths
#: (multiselect), or ``None`` if the user cancelled.
FileDialogResult = Union[Path, list[Path], None]


class FileSystemDialogBase(DialogScreenBase[FileDialogResult]):
    """Shared base screen for filesystem dialogs.

    Concrete dialogs (:class:`OpenFile`, :class:`OpenFolder`,
    :class:`SaveFile`) configure this base via ``__init__`` keyword
    arguments and expose their own narrow, friendly ``show(...)``
    classmethod on top - end users are not expected to construct this
    class directly.
    """

    CSS_PATH = _STYLES_DIR / "filedialog.tcss"

    BINDINGS = [("m", "toggle_mark", "Mark/unmark")]

    def on_directory_tree_file_selected(
        self,
        event: DirectoryTree.FileSelected
    ):
        event.stop()

    def __init__(
        self,
        location: str | Path = ".",
        *,
        title: str = "Open",
        select_label: str = "Select",
        show_filename_input: bool = True,
        default_filename: str = "",
        only_directories: bool = False,
        must_exist: bool = True,
        multiselect: bool = False,
        show_hidden: bool = False,
        accept_files: bool = True,
        accept_directories: bool = False,
        glob_filters: list[str] | None = None,
        callback: Callable[[FileDialogResult], None] | None = None,
        priority: int | None = None,
    ) -> None:
        super().__init__()

        resolved = Path(location).expanduser()
        try:
            resolved = resolved.resolve()
        except OSError:
            resolved = Path.cwd()
        # A starting location that doesn't exist (typo'd
        # initial_directory, a path that was valid at call time but
        # got removed) is not fatal - the dialog still has to open
        # *somewhere* sensible rather than crashing during compose().
        self.location: Path = resolved if resolved.is_dir() else Path.cwd()

        self.dialog_title = title
        self.select_label = select_label
        self.show_filename_input = show_filename_input
        self.default_filename = default_filename
        self.only_directories = only_directories
        self.must_exist = must_exist
        self.multiselect = multiselect
        self.show_hidden = show_hidden
        self.glob_filters = glob_filters
        self.callback = callback
        self.priority = priority if priority is not None else DialogPriority.MEDIUM

        self._selected: set[Path] = set()
        self._current_selection: Path | None = None
        self.accept_files = accept_files
        self.accept_directories = accept_directories

    # -- composition ------------------------------------------------------

    def compose(self):
        with Vertical(id="filedialogs-dialog") as dialog:
            dialog.border_title = self.dialog_title

            yield Label("Location", classes="label")
            yield Input(value=str(self.location), id="filedialogs-path_input")

            yield FilterableDirectoryTree(
                str(self.location),
                id="filedialogs-tree",
                show_hidden=self.show_hidden,
                glob_filters=self.glob_filters,
            )

            if self.show_filename_input:
                yield Label("Filename", classes="label")
                yield Input(
                    value=self.default_filename,
                    id="filedialogs-filename_input",
                    placeholder="filename.ext",
                )

            yield Label("", id="filedialogs-status")

            with Horizontal(id="filedialogs-buttons"):
                yield Button(self.select_label, id="filedialogs-select", variant="primary")
                yield Button("Cancel", id="filedialogs-cancel")

    def on_mount(self) -> None:
        """Foca o DirectoryTree de forma segura (robust para OpenPath e todos os diálogos)."""

        def do_focus() -> None:
            try:
                tree = self.query_one("#filedialogs-tree", FilterableDirectoryTree)
                tree.focus()
            except Exception:  # NoMatches ou DOM ainda não pronto (comum em OpenPath)
                # Fallback seguro: foca o primeiro widget que aceite foco
                try:
                    focusable = self.query("Input, DirectoryTree, Button").first()
                    if focusable:
                        focusable.focus()
                except Exception:
                    pass  # Último recurso: não crashar o diálogo

        # Adia o foco para o próximo ciclo do event loop
        self.call_later(do_focus)

    # -- navigation ------------------------------------------------------

    @on(Input.Submitted, "#filedialogs-path_input")
    def _on_path_submitted(self, event: Input.Submitted) -> None:
        """Let the user type/paste a path and jump straight there."""
        candidate = Path(event.value).expanduser()
        if not candidate.is_absolute():
            candidate = self.location / candidate
        try:
            candidate = candidate.resolve()
        except OSError:
            self._set_status(f"Invalid path: {event.value}", error=True)
            return

        if not candidate.is_dir():
            self._set_status(f"Not a directory: {candidate}", error=True)
            return

        self._navigate_to(candidate)

    def _navigate_to(self, directory: Path) -> None:
        self.location = directory
        self.query_one("#filedialogs-path_input", Input).value = str(directory)
        # Reassigning `.path` is DirectoryTree's own supported way of
        # re-rooting the tree - it triggers a full reset + reload.
        self.query_one("#filedialogs-tree", FilterableDirectoryTree).path = str(directory)
        self._set_status("")

    @on(FilterableDirectoryTree.DirectorySelected)
    def _on_directory_selected(self, event: FilterableDirectoryTree.DirectorySelected) -> None:
        self.location = event.path.resolve()
        self._current_selection = None
        self.query_one("#filedialogs-path_input", Input).value = str(self.location)
        self._set_status("")

    @on(FilterableDirectoryTree.FileSelected)
    def _on_file_selected(self, event):
        path = event.path.resolve()
        self._current_selection = path

        if self.multiselect:
            self._toggle_selected(path)
            return
        if self.show_filename_input:
            self.query_one("#filedialogs-filename_input", Input).value = path.name
        self._set_status("")

    # -- multiselect ------------------------------------------------------

    def action_toggle_mark(self) -> None:
        """Mark/unmark the file under the cursor (multiselect only)."""
        if not self.multiselect:
            return
        tree = self.query_one("#filedialogs-tree", FilterableDirectoryTree)
        node = tree.cursor_node
        if node is None or node.data is None or node.data.path.is_dir():
            return
        self._toggle_selected(node.data.path.resolve())

    def _toggle_selected(self, path: Path) -> None:
        if path in self._selected:
            self._selected.discard(path)
        else:
            self._selected.add(path)
        count = len(self._selected)
        self._set_status(f"{count} file(s) selected" if count else "")

    # -- confirm / cancel --------------------------------------------------

    @on(Button.Pressed, "#filedialogs-select")
    def _on_select_pressed(self) -> None:
        self._confirm()

    def _confirm(self) -> None:
        result = self._resolve_result()
        if self._validation_failed:
            # `_resolve_result` already populated #status with the
            # reason; keep the dialog open so the user can fix it.
            return
        if self.callback:
            self.callback(result)
        self.dismiss(result)

    _validation_failed: bool = False

    def _resolve_result(self) -> FileDialogResult:
        """Compute and validate the dialog's result.

        Sets ``self._validation_failed`` (and an inline status
        message) instead of returning a sentinel, so that "nothing
        selected because the user is choosing a brand-new filename to
        save" (valid) is distinguishable from "the typed filename
        does not exist and ``must_exist`` says it must" (invalid).
        """
        self._validation_failed = False

        if self.multiselect:
            if not self._selected:
                self._set_status("Select at least one file (press M to mark).", error=True)
                self._validation_failed = True
                return None
            if self.must_exist:
                missing = sorted(p for p in self._selected if not p.is_file())
                if missing:
                    self._set_status(f"File no longer exists: {missing[0]}", error=True)
                    self._validation_failed = True
                    return None
            return sorted(self._selected)

        if self._current_selection and self._current_selection.exists():
            candidate = self._current_selection
        elif self.only_directories:
            candidate = self.location
        else:
            filename = ""
            if self.show_filename_input:
                filename = self.query_one("#filedialogs-filename_input", Input).value.strip()

            candidate = (
                self.location / filename
                if filename
                else self.location
            )

        if self.must_exist:
            if self.only_directories:
                exists_ok = candidate.is_dir()

            elif self.accept_files and self.accept_directories:
                exists_ok = candidate.is_file() or candidate.is_dir()

            elif self.accept_files:
                exists_ok = candidate.is_file()

            else:
                exists_ok = candidate.is_dir()
            if not exists_ok:
                kind = "folder" if self.only_directories else "file"
                self._set_status(f"That {kind} does not exist: {candidate}", error=True)
                self._validation_failed = True
                return None

        return candidate

    def _cancel(self) -> None:
        if self.callback:
            self.callback(None)
        self.dismiss(None)

    @on(Button.Pressed, "#filedialogs-cancel")
    def _on_cancel_pressed(self) -> None:
        self._cancel()

    # -- helpers ------------------------------------------------------

    def _set_status(self, text: str, *, error: bool = False) -> None:
        label = self.query_one("#filedialogs-status", Label)
        label.update(text)
        label.set_class(error, "-error")
