"""nannokit.dialogs.filedialogs.open_file"""

from __future__ import annotations
from pathlib import Path
from typing import Callable, Union
from .base import FileSystemDialogBase

#: ``Path`` normally, or ``list[Path]`` when ``multiselect=True``.
OpenFileResult = Union[Path, list[Path], None]

class OpenFile(FileSystemDialogBase):
    """File picker, equivalent to .NET's ``OpenFileDialog``.

    Examples:
        >>> from nannokit.dialogs import OpenFile
        >>>
        >>> def on_path(path: Path | None) -> None:
        ...     if path is not None:
        ...         self.notify(f"Opening {path}")
        >>>
        >>> OpenFile.show(
        ...     initial_directory=".",
        ...     filters=["*.py", "*.toml"],
        ...     callback=on_path,
        ... )

        Multiple files (mirrors ``OpenFileDialog.Multiselect``)::

        >>> def on_paths(paths: list[Path] | None) -> None:
        ...     ...
        >>>
        >>> OpenFile.show(multiselect=True, callback=on_paths)
    """

    @classmethod
    def show(
        cls,
        initial_directory: str | Path | None = None,
        default_filename: str = "",
        *,
        title: str | None = None,
        multiselect: bool = False,
        must_exist: bool = True,
        show_hidden: bool = False,
        filters: list[str] | None = None,
        callback: Callable[[OpenFileResult], None] | None = None,
    ) -> None:
        """Show an Open File dialog.

        Args:
            initial_directory: Folder the dialog opens in. Defaults
                to the current working directory; falls back to it
                automatically if the given path doesn't exist.
            default_filename: Pre-filled value of the filename field.
                Ignored when ``multiselect=True``.
            title: Dialog title. Defaults to ``"Open File"``.
            multiselect: When ``True``, the user can mark multiple
                files (press ``M``) and ``callback`` receives a
                ``list[Path]`` instead of a single ``Path``.
            must_exist: When ``True`` (the default - mirrors
                ``OpenFileDialog.CheckFileExists``), the dialog
                refuses to close with a path that doesn't exist on
                disk and shows an inline error instead.
            show_hidden: Show dotfiles/dotdirs. Defaults to ``False``.
            filters: Optional list of glob patterns (e.g.
                ``["*.py", "*.md"]``) restricting which files are
                shown, mirroring ``OpenFileDialog.Filter``.
            callback: Called with the selected ``Path`` (or
                ``list[Path]`` if ``multiselect``), or ``None`` if the
                dialog was cancelled.
        """
        instance = cls(
            location=initial_directory or ".",
            title=title or "Open File",
            select_label="Open File...",
            show_filename_input=not multiselect,
            default_filename=default_filename,
            only_directories=False,
            must_exist=must_exist,
            multiselect=multiselect,
            show_hidden=show_hidden,
            accept_files=True,
            accept_directories=False,
            glob_filters=filters,
            callback=callback,
        )
        cls._present(instance)
