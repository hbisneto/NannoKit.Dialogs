"""
C#-flavoured ``MessageBox.Show``-style API for Textual.

    from nannokit.dialogs import messagebox

    messagebox.show(
        "Save changes before closing?",
        title="SuperNanno",
        buttons=messagebox.buttons.YES_NO_CANCEL,
        type=messagebox.type.WARNING,
        callback=on_result,
    )
"""

from .api import MessageBoxAPI
from .buttons import Buttons
from .dialog import MessageDialog
from .types import MessageBoxIcon, Types

#: Ready-to-use singleton - the primary public entry point.
messagebox = MessageBoxAPI()

__all__ = [
    "messagebox",
    "MessageBoxAPI",
    "MessageDialog",
    "Buttons",
    "MessageBoxIcon",
    "Types",
]
