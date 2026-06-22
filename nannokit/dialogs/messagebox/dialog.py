"""nannokit.dialogs.messagebox.dialog"""

from __future__ import annotations

from pathlib import Path
from typing import Callable

from textual import on
from textual.containers import Horizontal, Vertical
from textual.widgets import Button, Label

from ..core import DialogScreenBase

# Resolved relative to this file rather than to the process' current
# working directory or to Textual's own relative-CSS_PATH resolution,
# so the stylesheet is always found regardless of where the app that
# imports this package is launched from.
_STYLES_DIR = Path(__file__).resolve().parent.parent / "styles"


class MessageDialog(DialogScreenBase[str | None]):
    """A modal message box, in the spirit of .NET's ``MessageBox``.

    Dismisses with the label of the button the user pressed, or
    ``None`` if the dialog was cancelled (Escape).

    You will normally not instantiate this directly - use the
    :data:`nannokit.dialogs.messagebox` singleton instead, which
    wraps this class with a small, friendlier ``.show(...)`` API.
    """

    CSS_PATH = _STYLES_DIR / "messagebox.tcss"

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
        callback: Callable[[str | None], None] | None = None,
    ) -> None:
        super().__init__()
        self.message = message
        self.dialog_title = title
        self.buttons = buttons
        self.dialog_type = dialog_type
        self.callback = callback

    def compose(self):
        icon = self.ICONS.get(self.dialog_type, "ℹ")

        dialog = Vertical(
            Label(f"{icon}  {self.dialog_title}", id="title"),
            Label(self.message, id="message"),
            Horizontal(
                *(Button(label, id=_slug(label)) for label in self.buttons),
                id="buttons",
            ),
            id="dialog",
        )
        dialog.add_class(self.dialog_type)
        yield dialog

    def on_mount(self) -> None:
        # Sensible default: focus the first button so Enter/Space
        # works immediately, matching desktop message box behaviour.
        if self.buttons:
            self.query_one(f"#{_slug(self.buttons[0])}", Button).focus()

    @on(Button.Pressed)
    def _on_button_pressed(self, event: Button.Pressed) -> None:
        label = str(event.button.label)
        if self.callback:
            self.callback(label)
        self.dismiss(label)

    def _cancel(self) -> None:
        if self.callback:
            self.callback(None)
        self.dismiss(None)


def _slug(label: str) -> str:
    """Turn a button label into a safe widget id (``"OK"`` -> ``"ok"``)."""
    return "".join(ch.lower() if ch.isalnum() else "-" for ch in label).strip("-") or "btn"
