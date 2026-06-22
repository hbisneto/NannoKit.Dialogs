"""
nannokit.dialogs.core.manager
================================

``DialogManager`` is the single point of truth used by every dialog in
this package (``messagebox``, ``OpenFile``, ``OpenFolder``, ``SaveFile``,
and any future dialog) to find *which* :class:`textual.app.App` it
should be pushed onto.

Why this exists
----------------
A C# developer calling ``new OpenFileDialog().ShowDialog()`` never has to
say *which* application is showing the dialog - there is only ever one,
and the runtime already knows about it. We want the same feeling here:

    OpenFile.show(callback=on_path)

should "just work" from inside any handler of any Textual ``App``,
with no boilerplate.

Resolution order
----------------
1. **Explicitly attached app** - set once via :meth:`DialogManager.attach`,
   normally in ``App.on_mount``. This is the recommended setup for
   SuperNanno itself, and is *required* for code that calls a dialog
   from outside of the App's running context (a background thread, a
   module-level startup script, etc.), because Textual's own context
   var (see below) is only populated while a message/handler from that
   App is actively executing.
2. **Textual's ``active_app`` context var** - Textual sets this
   automatically for the duration of any event handler, action,
   binding callback, or worker that belongs to a running App. This
   means that in the overwhelmingly common case - calling
   ``OpenFile.show(...)`` from a key binding, a button handler, or an
   ``action_*`` method - this package needs **zero setup**. This is
   the standalone, "just import and call" experience the project asks
   for.

If neither source yields an app, a clear :class:`RuntimeError` is
raised explaining exactly what to do, instead of failing with an
obscure ``AttributeError`` deep inside Textual.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from textual.app import App


class DialogManager:
    """Resolves the currently active :class:`textual.app.App`.

    Examples:
        Recommended setup, once, inside your main App::

            from nannokit.dialogs.core import DialogManager

            class MyApp(App):
                def on_mount(self) -> None:
                    DialogManager.attach(self)

        After that (or even without it, see module docstring), any
        dialog's ``.show()`` classmethod can be called from anywhere
        inside the running App.
    """

    _app: "App | None" = None

    # -- registration --------------------------------------------------

    @classmethod
    def attach(cls, app: "App") -> None:
        """Register ``app`` as the App every dialog should attach to.

        Safe to call multiple times (e.g. if the App is recreated in
        tests); the most recent call wins.
        """
        cls._app = app

    @classmethod
    def detach(cls) -> None:
        """Forget the explicitly-attached App, if any.

        Useful for test teardown so state doesn't leak between tests,
        and for clean shutdown of long-lived processes that host more
        than one App over their lifetime.
        """
        cls._app = None

    @classmethod
    def is_attached(cls) -> bool:
        """Return ``True`` if an App was explicitly attached via :meth:`attach`."""
        return cls._app is not None

    # -- resolution -----------------------------------------------------

    @classmethod
    def resolve_app(cls) -> "App":
        """Return the App that dialogs should be pushed onto.

        Raises:
            RuntimeError: if no App was attached *and* no App is
                currently active (i.e. this was called from outside
                any running App context).
        """
        if cls._app is not None:
            return cls._app

        try:
            # Populated by Textual itself for the duration of any
            # event handler / action / worker belonging to a running
            # App. No import-time cost for users who never hit this
            # path, and no hard dependency on a specific Textual
            # internal beyond a documented, long-standing ContextVar.
            from textual.app import active_app

            return active_app.get()
        except LookupError:
            pass

        raise RuntimeError(
            "nannokit.dialogs could not find a running Textual App.\n\n"
            "This dialog must be shown either:\n"
            "  1) From inside an App event handler, action, binding, "
            "or worker (the common case - no setup needed), or\n"
            "  2) After registering the App once, e.g. in on_mount:\n\n"
            "       from nannokit.dialogs.core import DialogManager\n\n"
            "       class MyApp(App):\n"
            "           def on_mount(self) -> None:\n"
            "               DialogManager.attach(self)\n"
        )

    @classmethod
    def get_app(cls) -> "App":
        """Backwards-compatible alias for :meth:`resolve_app`."""
        return cls.resolve_app()
