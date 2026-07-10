"""nannokit.dialogs.messagebox.dialog"""

from __future__ import annotations
from pathlib import Path
from typing import Callable
from textual import on
from textual.containers import Horizontal, Vertical
from textual.widgets import Button, Label
from ..core import DialogPriority, DialogScreenBase
from ..filedialogs.tree import FilterableDirectoryTree

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
        "info": "ℹ️",
        "warning": "⚠️",
        "error": "❌",
        "success": "✅",
    }

    #: Dialog types that represent something the user must actively
    #: resolve before anything else continues - a confirmation, a
    #: destructive-action warning, an error. These get
    #: ``DialogPriority.HIGH`` by default so a confirmation is never
    #: silently buried behind (or replaced by) a lower priority dialog
    #: such as an informational messagebox or an already-open file
    #: dialog. Everything else (``info``, ``success``) defaults to
    #: ``DialogPriority.LOW``.
    _CRITICAL_TYPES = {"warning", "error"}

    def __init__(
        self,
        message: str,
        title: str,
        buttons: list[str],
        dialog_type: str = "info",
        callback: Callable[[str | None], None] | None = None,
        priority: int | None = None,
    ) -> None:
        super().__init__()
        self.message = message
        self.dialog_title = title
        self.buttons = buttons
        self.dialog_type = dialog_type
        self.callback = callback
        self.priority = (
            priority
            if priority is not None
            else (
                DialogPriority.HIGH
                if dialog_type in self._CRITICAL_TYPES
                else DialogPriority.LOW
            )
        )

    def compose(self):
        icon = self.ICONS.get(self.dialog_type, "ℹ")

        dialog = Vertical(
            Label(f"{icon}  {self.dialog_title}", id="messagebox-title"),
            Label(self.message, id="messagebox-message"),
            Horizontal(
                *(Button(label, id=_slug(label)) for label in self.buttons),
                id="messagebox-buttons",
            ),
            id="messagebox-dialog",
        )
        # dialog.add_class(self.dialog_type)
        dialog.add_class(f"messagebox-{self.dialog_type}")
        yield dialog

    def on_mount(self) -> None:
        """Foca o DirectoryTree de forma segura (robust para todos os diálogos)."""
        def do_focus() -> None:
            try:
                tree = self.query_one("#filedialogs-tree", FilterableDirectoryTree)
                tree.focus()
            except Exception:  # NoMatches ou DOM ainda não pronto
                # Fallback: tenta focar qualquer widget filho que aceite foco
                try:
                    focusable = self.query("Input, DirectoryTree, Button").first()
                    if focusable:
                        focusable.focus()
                except Exception:
                    pass  # Último recurso: não crashar

        # Usa call_later para dar tempo ao DOM (padrão recomendado no Textual para modais)
        self.call_later(do_focus)

    @on(Button.Pressed)
    def _on_button_pressed(self, event: Button.Pressed) -> None:
        """Garante que o callback rode apenas uma vez e dismiss seja seguro."""
        label = str(event.button.label)

        if self.callback:
            try:
                # Protege contra callback que possa falhar
                self.callback(label)
            except Exception:
                pass  # Nunca deixa o callback quebrar o diálogo

        # Proteção contra double-dismiss / future já resolvido
        try:
            self.dismiss(label)
        except Exception:
            # Se já foi dismissed, ignora silenciosamente
            pass

    def _cancel(self) -> None:
        if self.callback:
            self.callback(None)
        self.dismiss(None)


def _slug(label: str) -> str:
    """Turn a button label into a safe widget id (``"OK"`` -> ``"ok"``)."""
    return "".join(ch.lower() if ch.isalnum() else "-" for ch in label).strip("-") or "btn"
