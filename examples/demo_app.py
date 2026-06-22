#!/usr/bin/env python3
"""
nannokit.dialogs - combined demo
====================================

Run with:

    python examples/demo_app.py

Demonstrates every dialog in the package from a single, minimal host
App - the same shape SuperNanno itself would use to integrate them.
Note that `DialogManager.attach(self)` is called in `on_mount` purely
as the recommended, explicit setup; every dialog below would also work
without it, since they're all triggered from inside key bindings.
"""

from __future__ import annotations

from pathlib import Path

from textual.app import App, ComposeResult
from textual.widgets import Footer, Header, Label

from nannokit.dialogs import OpenFile, OpenFolder, SaveFile, messagebox
from nannokit.dialogs.core import DialogManager


class DemoApp(App):
    """Minimal host App exercising every nannokit.dialogs dialog."""

    TITLE = "nannokit.dialogs - demo"
    CSS = """
    #help {
        padding: 2 4;
    }
    """
    BINDINGS = [
        ("f", "open_file", "Open File"),
        ("shift+f", "open_file_multiselect", "Open File (multi)"),
        ("d", "open_folder", "Open Folder"),
        ("s", "save_file", "Save File"),
        ("m", "show_messagebox", "MessageBox"),
        ("q", "quit", "Quit"),
    ]

    def on_mount(self) -> None:
        # Recommended setup - see the module docstring of
        # `nannokit.dialogs.core.manager` for why this is optional
        # but still a good idea for a real application.
        DialogManager.attach(self)

    def compose(self) -> ComposeResult:
        yield Header()
        yield Label(
            "nannokit.dialogs demo\n\n"
            "  F        OpenFile\n"
            "  Shift+F  OpenFile (multiselect - press M on a file to mark it)\n"
            "  D        OpenFolder\n"
            "  S        SaveFile\n"
            "  M        messagebox\n"
            "  Q        Quit\n",
            id="help",
        )
        yield Footer()

    # -- actions ------------------------------------------------------

    def action_open_file(self) -> None:
        def on_result(path: Path | None) -> None:
            self.notify(f"Opened: {path}" if path else "Cancelled")

        OpenFile.show(
            initial_directory=".",
            filters=["*.py", "*.toml", "*.md"],
            callback=on_result,
        )

    def action_open_file_multiselect(self) -> None:
        def on_result(paths: list[Path] | None) -> None:
            self.notify(f"Opened {len(paths)} file(s)" if paths else "Cancelled")

        OpenFile.show(initial_directory=".", multiselect=True, callback=on_result)

    def action_open_folder(self) -> None:
        def on_result(folder: Path | None) -> None:
            self.notify(f"Folder: {folder}" if folder else "Cancelled")

        OpenFolder.show(initial_directory=".", callback=on_result)

    def action_save_file(self) -> None:
        def on_result(path: Path | None) -> None:
            self.notify(f"Would save to: {path}" if path else "Cancelled")

        SaveFile.show(default_filename="untitled.txt", callback=on_result)

    def action_show_messagebox(self) -> None:
        def on_result(choice: str | None) -> None:
            self.notify(f"You picked: {choice}" if choice else "Cancelled")

        messagebox.show(
            "Save changes before closing?",
            title="SuperNanno",
            buttons=messagebox.buttons.YES_NO_CANCEL,
            type=messagebox.type.WARNING,
            callback=on_result,
        )


if __name__ == "__main__":
    DemoApp().run()
