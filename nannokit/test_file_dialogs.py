#!/usr/bin/env python3
"""
Teste atualizado dos dialogs OpenFile e OpenFolder usando a nova API .show()
Execute com: python test_file_dialogs.py
"""

from pathlib import Path
from textual.app import App, ComposeResult
from textual.widgets import Button, Footer, Header, Label

# Importação final (quando estiver no pacote)
# from nannokit.dialogs.filedialogs import OpenFile, OpenFolder
from dialogs.filedialogs import OpenFile, OpenFolder  # ajuste temporário


class TestDialogsApp(App):
    """App de teste para a nova API .show()"""

    TITLE = "Teste nannokit.dialogs - .show() API"
    CSS = """
    .center {
        text-align: center;
        padding: 2 4;
    }
    """

    def compose(self) -> ComposeResult:
        yield Header()
        yield Label(
            "Pressione:\n"
            "• F → OpenFile.show()\n"
            "• D → OpenFolder.show()\n"
            "• Q → Sair\n\n"
            "Testando a nova API limpa!",
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
        """Teste com OpenFile.show()"""
        def callback(path: Path | None):
            if path:
                if path.is_file():
                    self.notify(f"✅ Arquivo selecionado:\n{path}", timeout=8)
                else:
                    self.notify(f"⚠️ Não é um arquivo:\n{path}", timeout=10)
            else:
                self.notify("❌ Cancelado")

        OpenFile.show(
            initial_directory=".",
            default_filename="exemplo.txt",
            callback=callback,
            title="Abrir Arquivo - SuperNanno"
        )

    def action_open_folder(self) -> None:
        """Teste com OpenFolder.show()"""
        def callback(path: Path | None):
            if path:
                abs_path = path.resolve()
                if abs_path.is_dir():
                    self.notify(f"📁 Pasta selecionada:\n{path}", timeout=8)
                else:
                    self.notify(f"⚠️ Não é uma pasta:\n{path}", timeout=10)
            else:
                self.notify("❌ Cancelado")

        OpenFolder.show(
            initial_directory=".",
            callback=callback,
            title="Selecionar Pasta - SuperNanno"
        )


if __name__ == "__main__":
    app = TestDialogsApp()
    app.run()