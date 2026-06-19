from .base import FileSystemDialogBase
from pathlib import Path

class OpenFolder(FileSystemDialogBase):
    """OpenFolderDialog equivalente do C#."""

    def __init__(
        self,
        location: str | Path = ".",
        callback=None,
    ):
        super().__init__(
            location=location,
            title="Select Folder",
            select_label="Select Folder",
            default_filename="",
            callback=callback,
        )