# dialogs/core/manager.py

from __future__ import annotations
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from textual.app import App

class DialogManager:
    """
    Stores a reference to the main SuperNanno App instance.

    Usage:
        DialogManager.attach(self)   # inside the App

    After attaching, dialogs can be pushed without passing `app` manually.
    Prepared for future async support via push_screen_wait.
    """

    app: "App | None" = None

    @classmethod
    def attach(cls, app: "App") -> None:
        """Register the main App instance."""
        cls.app = app

    @classmethod
    def detach(cls) -> None:
        """Unregister the App instance (useful on teardown)."""
        cls.app = None

    @classmethod
    def get_app(cls) -> "App":
        """
        Return the attached App, raising a clear error if none is registered.
        """
        if cls.app is None:
            raise RuntimeError(
                "DialogManager has no app attached. "
                "Call DialogManager.attach(self) inside your App."
            )
        return cls.app