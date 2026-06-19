from .base import FileSystemDialogBase
from pathlib import Path

class OpenFile(FileSystemDialogBase):
    """OpenFileDialog equivalente do C#."""

    def __init__(
        self,
        location: str | Path = ".",
        default_filename: str = "",
        callback=None,
    ):
        super().__init__(
            location=location,
            title="Open File",
            select_label="Open",
            default_filename=default_filename,
            callback=callback,
        )