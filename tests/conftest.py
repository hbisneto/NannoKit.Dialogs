"""Shared fixtures for the nannokit.dialogs test suite."""

from __future__ import annotations

from textual.app import App, ComposeResult
from textual.widgets import Label

from nannokit.dialogs.core import DialogManager, DialogQueue


class HostApp(App):
    """A minimal App standing in for SuperNanno's main App in tests."""

    def compose(self) -> ComposeResult:
        yield Label("host")

    def on_unmount(self) -> None:
        # Don't let one test's attached app / dialog bookkeeping leak
        # into the next.
        DialogManager.detach()
        DialogQueue.reset()
