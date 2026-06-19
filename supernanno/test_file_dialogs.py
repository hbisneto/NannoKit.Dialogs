#!/usr/bin/env python3
"""
Teste aprimorado dos dialogs OpenFile e OpenFolder para SuperNanno.
Execute com: python test_file_dialogs.py
"""

from pathlib import Path
from textual.app import App, ComposeResult
from textual.widgets import Button, Footer, Header, Label

# from supernanno.dialogs.filedialogs import OpenFile, OpenFolder
from dialogs.filedialogs import OpenFile, OpenFolder  # ajuste conforme sua estrutura


class TestDialogsApp(App):
    """App de teste para OpenFile e OpenFolder."""

    TITLE = "Teste SuperNanno.Dialogs - File & Folder"
    # CSS = """
    # .center {
    #     text-align: center;
    #     padding: 2 4;
    # }
    # """

    def compose(self) -> ComposeResult:
        yield Header()
        yield Label(
            "Pressione:\n"
            "• F → OpenFile\n"
            "• D → OpenFolder\n"
            "• Q → Sair\n\n"
            "Navegue com as setas / Enter na árvore.",
            classes="center",
        )
        yield Footer()

    def on_key(self, event) -> None:
        if event.key == "f":
            self.action_open_file()
        elif event.key == "d":
            self.action_open_folder()
        elif event.key == "q":
            self.exit()

    def action_open_file(self) -> None:
        def callback(path: Path | None):
            if path:
                if path.is_file():
                    self.notify(f"✅ Selected file:\n{path}", timeout=8)
                else:
                    self.notify(f"⚠️ The selected path is NOT a file:\n{path}\n(is_file: {path.is_file()})", timeout=10)
            else:
                self.notify("❌ Operation cancelled")
        self.push_screen(OpenFile(location=".", callback=callback))

    def action_open_folder(self) -> None:
        def callback(path: Path | None):
            if path:
                abs_path = path.resolve()
                
                self.notify("--- DEBUG INFO ---", timeout=12)
                self.notify(f"Received: {path}")
                self.notify(f"Resolved: {abs_path}")
                self.notify(f"Exists: {abs_path.exists()}")
                self.notify(f"is_file(): {abs_path.is_file()}")
                self.notify(f"is_dir(): {abs_path.is_dir()}")
                self.notify("-----------------")

                if abs_path.is_dir():
                    self.notify(f"📁 Selected folder:\n{path}", timeout=8)
                else:
                    self.notify(f"⚠️ The selected path is NOT a folder:\n{path}", timeout=10)
            else:
                self.notify("❌ Operation cancelled")
        self.push_screen(OpenFolder(location=".", callback=callback))


if __name__ == "__main__":
    app = TestDialogsApp()
    app.run()