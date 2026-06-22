"""nannokit.dialogs.messagebox.api"""

from __future__ import annotations

from typing import Callable

from .buttons import Buttons
from .dialog import MessageDialog
from .types import MessageBoxIcon


class MessageBoxAPI:
    """Public, C#-flavoured API for showing message dialogs.

    Mirrors .NET's static ``MessageBox.Show(...)``: a single call,
    fire-and-forget, with an optional callback for the result instead
    of a blocking return value (Textual is async; see the module
    docstring of :mod:`nannokit.dialogs.core.manager` for how the
    target App is resolved automatically).

    Usage:
        >>> from nannokit.dialogs import messagebox
        >>> messagebox.show(
        ...     "Do you want to save changes before closing?",
        ...     title="SuperNanno",
        ...     buttons=messagebox.buttons.YES_NO_CANCEL,
        ...     type=messagebox.type.WARNING,
        ...     callback=on_result,
        ... )

    A ready-to-use singleton is exported as
    ``nannokit.dialogs.messagebox`` - you should not normally need
    to instantiate this class yourself.
    """

    buttons = Buttons
    type = MessageBoxIcon  # noqa: A003 - intentional, mirrors the original `messagebox.type.X` call sites

    @staticmethod
    def show(
        message: str,
        title: str = "Message",
        buttons: list[str] | None = None,
        type: str = MessageBoxIcon.INFO,  # noqa: A002 - matches the public `type=` kwarg used at call sites
        callback: Callable[[str | None], None] | None = None,
    ) -> None:
        """Show a message dialog.

        Args:
            message: Body text of the dialog.
            title: Title bar text.
            buttons: Button labels, e.g. ``messagebox.buttons.YES_NO``.
                Defaults to a single ``["OK"]`` button.
            type: One of ``messagebox.type.INFO`` / ``WARNING`` /
                ``ERROR`` / ``SUCCESS``. Controls the icon and accent
                color.
            callback: Called with the label of the pressed button, or
                ``None`` if the dialog was cancelled (Escape).
        """
        MessageDialog._present(
            MessageDialog(
                message=message,
                title=title,
                buttons=buttons or Buttons.OK,
                dialog_type=type,
                callback=callback,
            )
        )
