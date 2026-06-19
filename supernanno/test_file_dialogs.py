#!/usr/bin/env python3
"""
Teste rápido dos novos dialogs OpenFile e OpenFolder
Execute com: python test_file_dialogs.py
"""

from pathlib import Path
from textual.app import App, ComposeResult
from textual.widgets import Button, Footer, Header, Label

# Importando os dialogs que você vai adicionar ao pacote
# (copie os arquivos que eu gerei antes para supernanno/dialogs/filedialogs/)
# from supernanno.dialogs import OpenFile, OpenFolder
from dialogs.filedialogs import OpenFile, OpenFolder
import os


class TestDialogsApp(App):
    """App de teste para OpenFile e OpenFolder."""

    TITLE = "Teste SuperNanno.Dialogs - File & Folder"

    def compose(self) -> ComposeResult:
        yield Header()
        yield Label(
            "Pressione:\n"
            "• F → OpenFile\n"
            "• D → OpenFolder\n"
            "• Q → Sair",
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
        """Teste OpenFile."""

        def callback(path: Path | None):
            if path:
                if path.is_file():
                    self.notify(f"✅ Selected file:\n{path}", timeout=8)
                else:
                    self.notify(f"⚠️ The selected path is not a file:\n{path}", timeout=10)
            else:
                self.notify("❌ Operation cancelled")
        self.push_screen(OpenFile(location=".", callback=callback))

    def action_open_folder(self) -> None:
        """Teste OpenFolder."""

        def callback(path: Path | None):
            if path:
                caminho_absoluto = path.resolve()
                
                # 2. Diagnóstico: Mostra no terminal o que o Python realmente está avaliando
                self.notify(f"--- DEBUG ---")
                self.notify(f"Caminho recebido: {path}")
                self.notify(f"Caminho absoluto resolvido: {caminho_absoluto}")
                self.notify(f"Existe no sistema? {caminho_absoluto.exists()}")
                self.notify(f"É um arquivo? {caminho_absoluto.is_file()}")
                self.notify(f"É uma pasta? {caminho_absoluto.is_dir()}")
                self.notify(f"-------------")
                if caminho_absoluto.is_dir():
                    self.notify(f"📁 Selected folder:\n{path}\nisDir: {caminho_absoluto}", timeout=8)
                else:
                    self.notify(f"⚠️ The selected path is not a folder:\n{path}", timeout=10)
            else:
                self.notify("❌ Operation cancelled")
        self.push_screen(OpenFolder(location=".", callback=callback))


if __name__ == "__main__":
    app = TestDialogsApp()
    app.run()