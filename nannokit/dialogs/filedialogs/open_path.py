"""nannokit.dialogs.filedialogs.open_path"""

from __future__ import annotations
from pathlib import Path
from typing import Callable
from .base import FileSystemDialogBase

class OpenPath(FileSystemDialogBase):
    """
    Generic filesystem picker.
    Allows selecting files or folders.
    Similar to a generic Windows Explorer picker.
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
    ) -> None:

        instance = cls(
        location=initial_directory or ".",
        title=title or "Open",
        select_label="Open...",
        show_filename_input=False,
        only_directories=False,
        accept_files=True,
        accept_directories=True,
        must_exist=must_exist,
        multiselect=False,
        show_hidden=show_hidden,
        glob_filters=None,
        callback=callback,
    )
        cls._present(instance)