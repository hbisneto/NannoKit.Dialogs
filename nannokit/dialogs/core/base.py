"""
nannokit.dialogs.core.base
=============================

Shared base class for every dialog *screen* in this package.

This is intentionally small: it does not try to impose any particular
layout or widget composition (``messagebox`` and ``filedialogs`` look
completely different). Its only job is to provide the one piece of
plumbing every dialog needs - resolving the active App through
:class:`DialogManager` and pushing itself onto it - so that subclasses'
``show()`` classmethods stay a one-liner and never duplicate that
resolution logic (which is exactly what had gone stale/broken in the
previous ``filedialogs`` implementation).
"""

from __future__ import annotations

from typing import Generic, TypeVar

from textual.screen import ModalScreen

from .manager import DialogManager

ResultT = TypeVar("ResultT")


class DialogScreenBase(ModalScreen[ResultT], Generic[ResultT]):
    """Common ``ModalScreen`` plumbing for SuperNanno dialogs.

    Subclasses still implement the normal Textual ``ModalScreen`` API
    (``compose()``, message handlers, bindings, etc.) - this class
    only adds :meth:`_present`, the one piece of logic that's
    identical across every dialog: "find the running App and push me
    onto it".
    """

    BINDINGS = [("escape", "cancel", "Cancel")]

    def action_cancel(self) -> None:
        """Escape-to-cancel, mirroring desktop dialog conventions.

        Delegates to :meth:`_cancel` so that pressing Escape and
        pressing a dialog's own "Cancel" button always run through the
        exact same code path (one place that invokes the user callback
        and dismisses the screen - never two copies that can drift).
        """
        self._cancel()

    def _cancel(self) -> None:
        """Cancellation hook - override in subclasses.

        The base implementation just dismisses with ``None``. Dialogs
        that need to invoke a user-supplied callback on cancellation
        (which is all of them) should override this method to do so
        before calling ``self.dismiss(...)``.
        """
        self.dismiss(None)  # type: ignore[arg-type]

    @classmethod
    def _present(cls, instance: "DialogScreenBase[ResultT]") -> None:
        """Resolve the active App and push ``instance`` onto its screen stack.

        Raises:
            RuntimeError: see :meth:`DialogManager.resolve_app`.
        """
        app = DialogManager.resolve_app()
        app.push_screen(instance)
