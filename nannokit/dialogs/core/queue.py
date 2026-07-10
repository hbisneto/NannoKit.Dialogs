"""
nannokit.dialogs.core.queue
===============================

``DialogQueue`` is what makes ``messagebox`` and ``filedialogs`` safe
to mix: a single, shared traffic controller that every dialog's
``.show(...)`` goes through on its way to ``App.push_screen``.

Before this existed, every dialog called ``app.push_screen(self)``
directly. Textual happily stacks as many ``ModalScreen``s as you push
onto it, but *nothing* decided *whether* a new dialog should be shown
immediately, shown on top (visually suspending whatever's there), or
made to wait - a ``messagebox.show()`` fired while an ``OpenFile`` was
open, or vice versa, would simply stack on top of it unconditionally,
regardless of how trivial or important either one was.

How it works
------------
Every :class:`~nannokit.dialogs.core.base.DialogScreenBase` carries a
``priority`` (see :mod:`nannokit.dialogs.core.priority`). When a dialog
is requested:

1. If nothing is currently showing, it is pushed immediately - the
   overwhelmingly common case, and free of any behavioural change from
   before this refactor.
2. If something *is* showing and the new dialog's priority is
   **higher**, it is pushed on top right away. Textual's screen stack
   itself keeps the interrupted dialog's widgets/state fully intact
   underneath - ``DialogQueue`` does not need to do anything special
   to "suspend" it.
3. Otherwise (equal or lower priority), the new dialog is placed on an
   internal priority queue instead of being shown. Nothing is pushed,
   so the current dialog is never touched by it.

Whenever the currently-showing dialog is dismissed - for any reason:
its own button, Escape, programmatic ``dismiss()`` - ``DialogQueue``
is notified via the ``callback`` argument of ``App.push_screen``, pops
its bookkeeping for that screen, and then, if anything is waiting on
the queue, pushes the highest-priority pending dialog next. This
repeats until the queue drains.

This module deliberately does not know anything about *what* a dialog
is (``MessageDialog`` vs a file dialog) - only its priority - so a
future dialog (e.g. a ``ColorPicker``) gets correct isolation for free
just by inheriting from ``DialogScreenBase``.
"""

from __future__ import annotations

import heapq
import itertools
from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from textual.app import App


class DialogQueue:
    """Priority-aware scheduler deciding when a dialog actually appears.

    A process-wide singleton, in the same spirit as
    :class:`~nannokit.dialogs.core.manager.DialogManager` - real
    applications only ever have one active dialog stack at a time.
    """

    _app: "App | None" = None
    _shown: list[Any] = []
    _pending: list[tuple[int, int, Any]] = []
    _counter = itertools.count()

    # -- lifecycle --------------------------------------------------------

    @classmethod
    def reset(cls) -> None:
        """Forget all bookkeeping.

        Called automatically when a dialog is requested against a
        different ``App`` than the one the queue was last tracking
        (e.g. a new App instance in a test), and exposed publicly for
        test teardown (mirrors :meth:`DialogManager.detach`).
        """
        cls._app = None
        cls._shown = []
        cls._pending = []
        cls._counter = itertools.count()

    # -- introspection ------------------------------------------------------

    @classmethod
    def is_showing(cls) -> bool:
        """Return ``True`` if any dialog is currently on screen."""
        return bool(cls._shown)

    @classmethod
    def pending_count(cls) -> int:
        """Number of dialogs currently queued (not yet on screen)."""
        return len(cls._pending)

    @classmethod
    def current_priority(cls) -> int | None:
        """Priority of the topmost currently-shown dialog, if any."""
        return cls._shown[-1].priority if cls._shown else None

    # -- scheduling -----------------------------------------------------

    @classmethod
    def request(cls, app: "App", instance: Any) -> None:
        """Ask for ``instance`` to be shown on ``app``.

        Pushes immediately if nothing is showing or if ``instance``
        outranks the current topmost dialog; otherwise queues it to be
        shown once the current dialog is dismissed.
        """
        if cls._app is not app:
            # A different App than the one we were tracking - most
            # likely a fresh App instance (new test, new process),
            # whose screen stack has nothing to do with our old
            # bookkeeping.
            cls.reset()
            cls._app = app

        if not cls._shown:
            cls._push(instance)
            return

        top = cls._shown[-1]
        if instance.priority > top.priority:
            cls._push(instance)
        else:
            heapq.heappush(
                cls._pending,
                (-instance.priority, next(cls._counter), instance),
            )

    @classmethod
    def _push(cls, instance: Any) -> None:
        cls._shown.append(instance)

        def _on_dismiss(_result: Any, _instance: Any = instance) -> None:
            cls._on_screen_dismissed(_instance)

        assert cls._app is not None
        cls._app.push_screen(instance, callback=_on_dismiss)

    @classmethod
    def _on_screen_dismissed(cls, instance: Any) -> None:
        if cls._shown and cls._shown[-1] is instance:
            cls._shown.pop()
        elif instance in cls._shown:
            # Dialogs normally dismiss top-down, so this shouldn't
            # happen in practice - but don't leave stale bookkeeping
            # behind if it ever does.
            cls._shown.remove(instance)

        if cls._pending:
            _, _, next_instance = heapq.heappop(cls._pending)
            cls._push(next_instance)
