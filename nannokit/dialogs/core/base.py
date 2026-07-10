"""
nannokit.dialogs.core.base
=============================

Shared base class for every dialog *screen* in this package.

This is intentionally small: it does not try to impose any particular
layout or widget composition (``messagebox`` and ``filedialogs`` look
completely different). Its job is the plumbing every dialog needs:

- resolving the active App through :class:`DialogManager`,
- carrying a :class:`~nannokit.dialogs.core.priority.DialogPriority`
  tier so :class:`~nannokit.dialogs.core.queue.DialogQueue` can decide
  whether to show it immediately, stack it on top of what's already
  showing, or queue it, and
- handing the actual presentation off to ``DialogQueue`` instead of
  calling ``App.push_screen`` directly.

so that subclasses' ``show()`` classmethods stay a one-liner and never
duplicate that logic (which is exactly what had gone stale/broken in
the previous ``filedialogs`` implementation, and exactly what made
``messagebox`` and ``filedialogs`` able to stack on top of each other
uncontrolled before this refactor).
"""

from __future__ import annotations

from typing import Generic, TypeVar

from textual.screen import ModalScreen

from .manager import DialogManager
from .priority import DialogPriority
from .queue import DialogQueue

ResultT = TypeVar("ResultT")


class DialogScreenBase(ModalScreen[ResultT], Generic[ResultT]):
    """Common ``ModalScreen`` plumbing for SuperNanno dialogs.

    Subclasses still implement the normal Textual ``ModalScreen`` API
    (``compose()``, message handlers, bindings, etc.) - this class
    only adds:

    - ``priority``: an ``int`` (see :class:`DialogPriority`) that
      subclasses set in their own ``__init__`` - defaults to
      ``DialogPriority.MEDIUM`` if a subclass doesn't set one, so a
      third-party dialog that doesn't know about priorities yet still
      behaves reasonably rather than erroring.
    - :meth:`_present`: "find the running App and ask ``DialogQueue``
      to show me" - identical across every dialog.
    """

    BINDINGS = [("escape", "cancel", "Cancel")]

    #: Default priority tier - concrete dialogs normally set their own
    #: value in ``__init__`` (optionally honouring an explicit
    #: ``priority=`` override from the caller). See
    #: :mod:`nannokit.dialogs.core.priority`.
    priority: int = DialogPriority.MEDIUM

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
        """Resolve the active App and request ``instance`` be shown.

        Presentation itself - whether ``instance`` appears right away,
        on top of an existing dialog, or after a wait - is decided by
        :class:`~nannokit.dialogs.core.queue.DialogQueue` based on
        ``instance.priority`` versus whatever else is currently
        showing. This is what keeps ``messagebox`` and ``filedialogs``
        isolated from one another: neither ever calls
        ``App.push_screen`` directly.

        Raises:
            RuntimeError: see :meth:`DialogManager.resolve_app`.
        """
        app = DialogManager.resolve_app()
        DialogQueue.request(app, instance)
