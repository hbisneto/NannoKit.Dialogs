# dialogs/messagebox/api.py

from __future__ import annotations

from typing import Callable

from dialogs.core.manager import DialogManager
from dialogs.messagebox.dialog import MessageDialog
from dialogs.messagebox.buttons import Buttons
from dialogs.messagebox.types import Types


class MessageBoxAPI:
    """
    Public API for displaying message dialogs inside the SuperNanno App.

    The dialog is created dynamically on each call and pushed onto the
    App's screen stack via push_screen — no separate App() or event loop.

    Usage:
        messagebox.show(
            "Deseja sobrescrever o arquivo?",
            "Aviso",
            messagebox.buttons.RETRY_CANCEL,
            type=messagebox.type.SUCCESS,
            callback=resposta
        )

    The App must be registered first:
        from dialogs.core.manager import DialogManager
        DialogManager.attach(self)

    Prepared for future async support:
        result = await app.push_screen_wait(MessageDialog(...))
    """

    buttons = Buttons
    type = Types

    @staticmethod
    def show(
        message: str,
        title: str = "Message",
        buttons: list[str] | None = None,
        type: str = "info",
        callback: Callable[[str], None] | None = None,
    ) -> None:
        """
        Push a MessageDialog onto the main App's screen stack.

        Args:
            message:  Body text of the dialog.
            title:    Title bar text.
            buttons:  List of button labels. Defaults to ["OK"].
            type:     Dialog type — "info", "warning", "error", "success".
            callback: Optional callable receiving the clicked button label.
        """

        if buttons is None:
            buttons = ["OK"]

        app = DialogManager.get_app()

        app.push_screen(
            MessageDialog(
                message=message,
                title=title,
                buttons=buttons,
                dialog_type=type,
                callback=callback,
            )
        )
