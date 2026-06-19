"""Base class for filesystem dialogs in SuperNanno."""

from __future__ import annotations

from pathlib import Path
from typing import Callable

from textual.screen import ModalScreen
from textual.containers import Vertical, Horizontal
from textual.widgets import DirectoryTree, Input, Button, Label
from textual import on


class FileSystemDialogBase(ModalScreen[Path | None]):
    """Base para OpenFile e OpenFolder."""

    CSS_PATH = "../styles/filedialog.tcss"

    def __init__(
        self,
        location: str | Path = ".",
        title: str = "Open",
        select_label: str = "Select",
        default_filename: str = "",
        callback: Callable[[Path | None], None] | None = None,
    ) -> None:
        super().__init__()
        self.location = Path(location).expanduser().resolve()
        self.title = title
        self.select_label = select_label
        self.default_filename = default_filename
        self.callback = callback

    def compose(self):
        with Vertical(id="dialog") as dialog:
            dialog.border_title = self.title

            yield Label("📍 Location:", classes="label")
            yield Input(value=str(self.location), id="path_input", disabled=True)

            yield DirectoryTree(str(self.location), id="tree")

            if self.select_label != "Select Folder":
                yield Label("📄 Filename:", classes="label")
                yield Input(
                    value=self.default_filename,
                    id="filename",
                    placeholder="filename.ext",
                )

            with Horizontal(id="buttons"):
                yield Button(self.select_label, id="select", variant="primary")
                yield Button("Cancel", id="cancel")

    @on(DirectoryTree.FileSelected)
    def on_file_selected(self, event: DirectoryTree.FileSelected) -> None:
        if self.select_label != "Select Folder":
            self.query_one("#filename", Input).value = event.path.name

    @on(Button.Pressed, "#select")
    def action_select(self) -> None:
        filename = ""
        if self.select_label != "Select Folder":
            filename = self.query_one("#filename", Input).value.strip()

        full_path = self.location / filename if filename else self.location

        if self.callback:
            self.callback(full_path)
        self.dismiss(full_path)

    @on(Button.Pressed, "#cancel")
    def action_cancel(self) -> None:
        if self.callback:
            self.callback(None)
        self.dismiss(None)

    def on_mount(self) -> None:
        """Atualiza o DirectoryTree quando o modal é montado."""
        tree = self.query_one("#tree", DirectoryTree)
        tree.path = str(self.location)  # força refresh inicial

    @on(DirectoryTree.DirectorySelected)
    def on_directory_selected(self, event: DirectoryTree.DirectorySelected) -> None:
        """Atualiza a localização atual quando uma pasta é selecionada na árvore."""
        self.location = event.path.resolve()
        # Atualiza o campo de path (readonly)
        self.query_one("#path_input", Input).value = str(self.location)

    @on(DirectoryTree.FileSelected)
    def on_file_selected(self, event: DirectoryTree.FileSelected) -> None:
        """Atualiza o filename apenas para OpenFile."""
        if self.select_label != "Select Folder":
            self.query_one("#filename", Input).value = event.path.name

    @on(Button.Pressed, "#select")
    def action_select(self) -> None:
        """Melhorado: usa o path correto do item selecionado na árvore."""
        tree = self.query_one("#tree", DirectoryTree)
        
        # Tenta pegar o path do item atualmente selecionado (melhor que self.location)
        selected_path: Path | None = None
        if hasattr(tree, "cursor_node") and tree.cursor_node and tree.cursor_node.data:
            selected_path = Path(tree.cursor_node.data.path) if hasattr(tree.cursor_node.data, "path") else tree.cursor_node.data
        else:
            selected_path = self.location

        # Para OpenFolder, sempre prioriza o item selecionado (se for pasta)
        if self.select_label == "Select Folder":
            full_path = selected_path or self.location
        else:
            # Para OpenFile: combina location + filename
            filename = self.query_one("#filename", Input).value.strip()
            full_path = (self.location / filename) if filename else self.location

        if self.callback:
            self.callback(full_path)
        self.dismiss(full_path)