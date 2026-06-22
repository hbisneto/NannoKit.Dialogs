"""nannokit.dialogs.filedialogs.tree"""

from __future__ import annotations

from fnmatch import fnmatch
from pathlib import Path
from typing import Iterable

from textual.widgets import DirectoryTree


class FilterableDirectoryTree(DirectoryTree):
    """A :class:`DirectoryTree` that supports OpenFileDialog-style filters.

    Two independent, optional filters:

    - ``show_hidden``: when ``False`` (the default), dotfiles/dotdirs
      are hidden - the same default Textual's own ``DirectoryTree``
      ships with, made explicit and configurable here.
    - ``glob_filters``: a list of glob patterns (e.g.
      ``["*.py", "*.toml"]``), echoing .NET's
      ``OpenFileDialog.Filter``. Directories always pass through
      regardless of the filter, since you still need to navigate into
      them; only files are matched against the patterns.
    """

    def __init__(
        self,
        path: str | Path,
        *,
        show_hidden: bool = False,
        glob_filters: list[str] | None = None,
        **kwargs,
    ) -> None:
        super().__init__(path, **kwargs)
        self.show_hidden = show_hidden
        self.glob_filters = glob_filters

    def filter_paths(self, paths: Iterable[Path]) -> Iterable[Path]:
        result = paths
        if not self.show_hidden:
            result = (p for p in result if not p.name.startswith("."))
        if self.glob_filters:
            patterns = self.glob_filters
            result = (
                p
                for p in result
                if p.is_dir() or any(fnmatch(p.name, pattern) for pattern in patterns)
            )
        return result
