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
        priority: int | None = None,
    ) -> None:
        """Show a message dialog.

        Args:
            message: Body text of the dialog.
            title: Title bar text.
            buttons: Button labels, e.g. ``messagebox.buttons.YES_NO``.
                Defaults to a single ``["OK"]`` button.
            type: One of ``messagebox.type.INFO`` / ``WARNING`` /
                ``ERROR`` / ``SUCCESS``. Controls the icon, accent
                color, and (unless ``priority`` is given explicitly)
                the dialog's default priority tier - ``WARNING`` and
                ``ERROR`` default to
                :data:`~nannokit.dialogs.core.DialogPriority.HIGH`,
                ``INFO`` and ``SUCCESS`` to
                :data:`~nannokit.dialogs.core.DialogPriority.LOW`.
            callback: Called with the label of the pressed button, or
                ``None`` if the dialog was cancelled (Escape).
            priority: Optional explicit priority override (see
                :class:`~nannokit.dialogs.core.DialogPriority`). Rarely
                needed - the default derived from ``type`` is right
                for almost every case - but available for the odd
                INFO messagebox that genuinely must interrupt
                something else, or a WARNING that shouldn't.
        """
        MessageDialog._present(
            MessageDialog(
                message=message,
                title=title,
                buttons=buttons or Buttons.OK,
                dialog_type=type,
                callback=callback,
                priority=priority,
            )
        )

    @classmethod
    def show_with_priority(
        cls,
        priority: int,
        message: str,
        title: str = "Message",
        buttons: list[str] | None = None,
        type: str = MessageBoxIcon.INFO,  # noqa: A002
        callback: Callable[[str | None], None] | None = None,
    ) -> None:
        """Convenience wrapper for :meth:`show` with an explicit priority.

        Identical to ``messagebox.show(..., priority=priority)`` -
        provided for callers who find leading with the priority reads
        more clearly at the call site, e.g.::

            messagebox.show_with_priority(
                DialogPriority.HIGH,
                "Disk almost full.",
                type=messagebox.type.WARNING,
            )
        """
        cls.show(message, title, buttons, type=type, callback=callback, priority=priority)
