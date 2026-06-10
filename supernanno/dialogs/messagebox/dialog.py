# dialogs/messagebox/dialog.py

from __future__ import annotations

from typing import Callable

from textual.screen import ModalScreen
from textual.containers import Vertical, Horizontal
from textual.widgets import Label, Button
from dialogs.styles import bindings


class MessageDialog(ModalScreen):
    # print(bindings.CSS_FILE)
    CSS_PATH = bindings.CSS_FILE

    # DEFAULT_CSS = """
    # MessageDialog {
    #     align: center middle;
    #     background: rgba(0,0,0,0.55);
    # }

    # #dialog {
    #     width: 60;
    #     height: auto;

    #     background: #202020;

    #     border: round #5f87ff;

    #     padding: 1 2;
    # }

    # #title {
    #     text-style: bold;
    #     margin-bottom: 1;
    # }

    # #message {
    #     margin-bottom: 2;
    # }

    # #buttons {
    #     align-horizontal: right;
    #     height: auto;
    # }

    # Button {
    #     margin-left: 1;
    #     min-width: 12;
    # }

    # .info {
    #     border: round #5f87ff;
    # }

    # .warning {
    #     border: round #ffaf00;
    # }

    # .error {
    #     border: round #ff005f;
    # }

    # .success {
    #     border: round #00af5f;
    # }
    # """

    ICONS: dict[str, str] = {
        "info": "ℹ",
        "warning": "⚠",
        "error": "✖",
        "success": "✔",
    }

    def __init__(
        self,
        message: str,
        title: str,
        buttons: list[str],
        dialog_type: str = "info",
        callback: Callable[[str], None] | None = None,
    ) -> None:
        super().__init__()

        self.message = message
        self.title = title
        self.buttons = buttons
        self.dialog_type = dialog_type
        self.callback = callback

    def compose(self):

        icon = self.ICONS.get(self.dialog_type, "ℹ")

        dialog = Vertical(
            Label(
                f"{icon}  {self.title}",
                id="title",
            ),

            Label(
                self.message,
                id="message",
            ),

            Horizontal(
                *[
                    Button(label, id=label.lower())
                    for label in self.buttons
                ],
                id="buttons",
            ),

            id="dialog",
        )

        dialog.add_class(self.dialog_type)

        yield dialog

    def on_button_pressed(self, event: Button.Pressed) -> None:
        button = str(event.button.label)

        if self.callback:
            self.callback(button)

        self.dismiss(button)
