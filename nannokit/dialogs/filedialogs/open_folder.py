"""nannokit.dialogs.filedialogs.open_folder"""

from __future__ import annotations
from pathlib import Path
from typing import Callable
from .base import FileSystemDialogBase

class OpenFolder(FileSystemDialogBase):
    """Folder picker, equivalent to .NET's ``FolderBrowserDialog``.

    Examples:
        >>> from nannokit.dialogs import OpenFolder
        >>>
        >>> def on_folder(folder: Path | None) -> None:
        ...     if folder is not None:
        ...         self.notify(f"Project root set to {folder}")
        >>>
        >>> OpenFolder.show(initial_directory=".", callback=on_folder)
    """

    @classmethod
    def show(
        cls,
        initial_directory: str | Path | None = None,
        *,
        title: str | None = None,
        must_exist: bool = True,
        show_hidden: bool = False,
        callback: Callable[[Path | None], None] | None = None,
        priority: int | None = None,
    ) -> None:
        """Show a Select Folder dialog.

        Args:
            initial_directory: Folder the dialog opens in. Defaults
                to the current working directory; falls back to it
                automatically if the given path doesn't exist.
            title: Dialog title. Defaults to ``"Select Folder"``.
            must_exist: When ``True`` (the default, mirrors
                ``FolderBrowserDialog``'s implicit behaviour), the
                selected folder must exist on disk. There's normally
                no reason to set this to ``False`` here - use
                :class:`~nannokit.dialogs.filedialogs.SaveFile` for
                "pick a place to create something new" workflows.
            show_hidden: Show dotdirs. Defaults to ``False``.
            callback: Called with the selected ``Path``, or ``None``
                if the dialog was cancelled.
            priority: Optional explicit priority override (see
                :class:`~nannokit.dialogs.core.DialogPriority`).
                Defaults to ``DialogPriority.MEDIUM``.

        Note:
            Unlike :class:`OpenFile`, this dialog does not support
            ``multiselect`` - .NET's own ``FolderBrowserDialog``
            doesn't either, since "select several unrelated folders
            at once" maps poorly to a single destination path.
        """
        instance = cls(
            location=initial_directory or ".",
            title=title or "Select Folder",
            select_label="Select Folder...",
            show_filename_input=False,
            only_directories=True,
            must_exist=must_exist,
            multiselect=False,
            show_hidden=show_hidden,
            accept_files=False,
            accept_directories=True,
            glob_filters=None,
            callback=callback,  # type: ignore[arg-type]  # OpenFolder never multiselects; see class docstring.
            priority=priority,
        )
        cls._present(instance)

    @classmethod
    def show_with_priority(cls, priority: int, *args, **kwargs) -> None:
        """Convenience wrapper for :meth:`show` with an explicit priority."""
        cls.show(*args, priority=priority, **kwargs)
