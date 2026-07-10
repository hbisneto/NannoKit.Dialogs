"""
nannokit.dialogs.filedialogs.save_file
==========================================

Bonus dialog, included to demonstrate how cleanly this architecture
extends to a dialog with genuinely *different* behaviour - not just
different labels/flags like :class:`OpenFolder` is to
:class:`~nannokit.dialogs.filedialogs.open_file.OpenFile`.

``SaveFile`` needs an overwrite confirmation step that the other two
don't, so it overrides :meth:`FileSystemDialogBase._confirm` rather
than reusing the base implementation as-is - and along the way shows
how a filesystem dialog can compose with ``messagebox`` from inside
the package itself. Because the overwrite confirmation is a WARNING
messagebox, :class:`~nannokit.dialogs.core.DialogQueue` gives it a
higher priority than the SaveFile dialog it was spawned from, so it
is always stacked on top and answered before SaveFile can proceed -
no extra wiring needed here for that guarantee.
"""

from __future__ import annotations

from pathlib import Path
from typing import Callable

from ..messagebox import messagebox
from .base import FileSystemDialogBase


class _SaveFileScreen(FileSystemDialogBase):
    """The actual screen behind :class:`SaveFile`.

    Same composition as the base dialog; the only behavioural
    difference is in :meth:`_confirm`, where an existing target file
    triggers a Yes/No confirmation (via ``messagebox``) before the
    dialog actually closes - mirroring
    ``SaveFileDialog.OverwritePrompt`` in .NET.
    """

    def __init__(self, *args, confirm_overwrite: bool = True, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        self.confirm_overwrite = confirm_overwrite

    def _confirm(self) -> None:
        result = self._resolve_result()
        if self._validation_failed:
            return
        # SaveFile never multiselects, so `must_exist=False` and
        # `only_directories=False` mean `_resolve_result` always
        # returns a concrete `Path` here, never `None`/`list[Path]`.
        target: Path = result  # type: ignore[assignment]

        if self.confirm_overwrite and target.exists():
            def on_overwrite_decision(button: str | None) -> None:
                if button == "Yes":
                    self._finish(target)
                # "No" / Escape: leave the SaveFile dialog open so the
                # user can pick a different name instead of losing
                # their place.

            messagebox.show(
                f'"{target.name}" already exists. Overwrite it?',
                title="Confirm Save",
                buttons=messagebox.buttons.YES_NO,
                type=messagebox.type.WARNING,
                callback=on_overwrite_decision,
            )
            return

        self._finish(target)

    def _finish(self, result: Path) -> None:
        if self.callback:
            self.callback(result)
        self.dismiss(result)


class SaveFile:
    """File-save picker, equivalent to .NET's ``SaveFileDialog``.

    Unlike :class:`~nannokit.dialogs.filedialogs.open_file.OpenFile`,
    the target file is not required to exist yet - that's the point -
    but if it *does* exist, confirmation is requested before
    overwriting it (configurable via ``confirm_overwrite``).

    Examples:
        >>> from nannokit.dialogs import SaveFile
        >>> SaveFile.show(default_filename="untitled.txt", callback=on_save_path)
    """

    @classmethod
    def show(
        cls,
        initial_directory: str | Path | None = None,
        default_filename: str = "",
        *,
        title: str | None = None,
        confirm_overwrite: bool = True,
        show_hidden: bool = False,
        filters: list[str] | None = None,
        callback: Callable[[Path | None], None] | None = None,
        priority: int | None = None,
    ) -> None:
        """Show a Save File dialog.

        Args:
            initial_directory: Folder the dialog opens in.
            default_filename: Pre-filled filename - almost always
                wanted here, unlike with :class:`OpenFile`.
            title: Dialog title. Defaults to ``"Save File"``.
            confirm_overwrite: Ask before overwriting an existing
                file. Defaults to ``True``.
            show_hidden: Show dotfiles/dotdirs.
            filters: Optional glob patterns restricting which
                existing files are shown while browsing.
            callback: Called with the chosen ``Path``, or ``None`` if
                cancelled.
            priority: Optional explicit priority override for the
                SaveFile dialog itself (see
                :class:`~nannokit.dialogs.core.DialogPriority`).
                Defaults to ``DialogPriority.MEDIUM``. Does not affect
                the overwrite confirmation, which always uses the
                WARNING messagebox default (``HIGH``) so it can never
                be silently skipped.
        """
        instance = _SaveFileScreen(
            location=initial_directory or ".",
            title=title or "Save File",
            select_label="Save",
            show_filename_input=True,
            default_filename=default_filename,
            only_directories=False,
            must_exist=False,
            multiselect=False,
            show_hidden=show_hidden,
            glob_filters=filters,
            callback=callback,
            confirm_overwrite=confirm_overwrite,
            priority=priority,
        )
        _SaveFileScreen._present(instance)

    @classmethod
    def show_with_priority(cls, priority: int, *args, **kwargs) -> None:
        """Convenience wrapper for :meth:`show` with an explicit priority."""
        cls.show(*args, priority=priority, **kwargs)
