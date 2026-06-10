# supernanno/app.py
#
# Example of how the SuperNanno main App integrates with dialogs.
#
# The App must call DialogManager.attach(self) once — typically in on_mount.
# After that, messagebox.show() works anywhere without passing `app` manually.

from textual.app import App, ComposeResult
from textual.widgets import Label
from dialogs.core.manager import DialogManager
from dialogs import messagebox

class SuperNannoApp(App):
    def on_mount(self) -> None:
        DialogManager.attach(self)

    def compose(self) -> ComposeResult:
        yield Label("SuperNanno — pressione D para abrir um dialog de exemplo")

    def on_key(self, event) -> None:
        if event.key == "d":
            self._demo_dialog()

    def _demo_dialog(self) -> None:
        def resposta(btn: str) -> None:
            self.notify(f"Usuário clicou em: {btn}")

        messagebox.show(
            "You will need to update iTunes to sync with your iPhone. Do you want to download the latest version now?",
            "A new version of iTunes (11.2.6) is available. Would you like to download it now?",
            messagebox.buttons.YESNO,
            type=messagebox.type.INFO,
            callback=resposta,
        )
        # messagebox.show(
        #     "O arquivo já existe. Deseja sobrescrever?",
        #     "Aviso",
        #     messagebox.buttons.RETRY_CANCEL,
        #     type=messagebox.type.WARNING,
        #     callback=resposta,
        # )


if __name__ == "__main__":
    SuperNannoApp().run()
