"""
Tests for cross-module dialog isolation: `messagebox` and
`filedialogs` must never silently interrupt or replace one another,
and `DialogQueue` must resolve concurrent requests strictly by
priority.
"""

from __future__ import annotations

import pytest

from nannokit.dialogs import OpenFolder, messagebox
from nannokit.dialogs.core import DialogPriority, DialogQueue
from nannokit.dialogs.filedialogs import FileSystemDialogBase
from nannokit.dialogs.messagebox import MessageDialog

from .conftest import HostApp


@pytest.mark.asyncio
async def test_high_priority_messagebox_interrupts_an_open_file_dialog(tmp_path):
    results: dict[str, list] = {"folder": [], "choice": []}

    class DemoApp(HostApp):
        def on_key(self, event) -> None:
            if event.key == "o":
                OpenFolder.show(initial_directory=tmp_path, callback=results["folder"].append)
            elif event.key == "w":
                messagebox.show(
                    "Unsaved changes will be lost. Continue?",
                    buttons=messagebox.buttons.YES_NO,
                    type=messagebox.type.WARNING,
                    callback=results["choice"].append,
                )

    app = DemoApp()
    async with app.run_test() as pilot:
        await pilot.press("o")
        await pilot.pause()
        assert isinstance(app.screen, FileSystemDialogBase)

        # A HIGH priority (WARNING) messagebox requested while a
        # MEDIUM priority file dialog is open must take precedence
        # immediately - stacked on top, not queued behind it.
        await pilot.press("w")
        await pilot.pause()
        assert isinstance(app.screen, MessageDialog)

        await pilot.click("#yes")
        await pilot.pause()

        # Answering it reveals the still-open, still-intact file
        # dialog underneath - it was never cancelled by the
        # interruption, and its own callback was never invoked.
        assert isinstance(app.screen, FileSystemDialogBase)
        assert results["choice"] == ["Yes"]
        assert results["folder"] == []


@pytest.mark.asyncio
async def test_low_priority_messagebox_queues_behind_an_open_file_dialog(tmp_path):
    results: dict[str, list] = {"folder": [], "info": []}

    class DemoApp(HostApp):
        def on_key(self, event) -> None:
            if event.key == "o":
                OpenFolder.show(initial_directory=tmp_path, callback=results["folder"].append)
            elif event.key == "i":
                messagebox.show(
                    "Background sync complete.",
                    type=messagebox.type.INFO,
                    callback=results["info"].append,
                )

    app = DemoApp()
    async with app.run_test() as pilot:
        await pilot.press("o")
        await pilot.pause()
        assert isinstance(app.screen, FileSystemDialogBase)

        # An INFO messagebox (LOW priority) must not interrupt an
        # already-open file dialog (MEDIUM priority) - it waits.
        await pilot.press("i")
        await pilot.pause()
        assert isinstance(app.screen, FileSystemDialogBase)
        assert DialogQueue.pending_count() == 1

        await pilot.click("#filedialogs-select")
        await pilot.pause()

        # Once the file dialog resolves, the queued messagebox appears.
        assert isinstance(app.screen, MessageDialog)
        await pilot.press("enter")
        await pilot.pause()

    assert results["folder"] == [tmp_path.resolve()]
    assert results["info"] == ["OK"]


@pytest.mark.asyncio
async def test_equal_priority_file_dialogs_do_not_stack_simultaneously(tmp_path):
    calls: list[str] = []

    class DemoApp(HostApp):
        def on_key(self, event) -> None:
            if event.key == "1":
                OpenFolder.show(initial_directory=tmp_path, callback=lambda p: calls.append("first"))
            elif event.key == "2":
                OpenFolder.show(initial_directory=tmp_path, callback=lambda p: calls.append("second"))

    app = DemoApp()
    async with app.run_test() as pilot:
        await pilot.press("1")
        await pilot.pause()
        first_screen = app.screen

        await pilot.press("2")
        await pilot.pause()
        # Same priority tier - the second request must not silently
        # replace or stack on top of the first; it's queued instead.
        assert app.screen is first_screen
        assert DialogQueue.pending_count() == 1

        await pilot.click("#filedialogs-select")
        await pilot.pause()
        second_screen = app.screen
        assert isinstance(second_screen, FileSystemDialogBase)
        assert second_screen is not first_screen

        await pilot.click("#filedialogs-select")
        await pilot.pause()

    assert calls == ["first", "second"]


@pytest.mark.asyncio
async def test_explicit_priority_override_lets_an_info_box_jump_the_queue(tmp_path):
    """`priority=` lets a caller opt an otherwise-LOW dialog into HIGH."""
    results: dict[str, list] = {"folder": [], "info": []}

    class DemoApp(HostApp):
        def on_key(self, event) -> None:
            if event.key == "o":
                OpenFolder.show(initial_directory=tmp_path, callback=results["folder"].append)
            elif event.key == "i":
                messagebox.show(
                    "Critical background task failed.",
                    type=messagebox.type.INFO,
                    priority=DialogPriority.HIGH,
                    callback=results["info"].append,
                )

    app = DemoApp()
    async with app.run_test() as pilot:
        await pilot.press("o")
        await pilot.pause()
        await pilot.press("i")
        await pilot.pause()

        # Despite being an INFO type (normally LOW), the explicit
        # priority override makes it outrank the open file dialog.
        assert isinstance(app.screen, MessageDialog)
        assert DialogQueue.pending_count() == 0

        await pilot.press("enter")
        await pilot.pause()
        assert isinstance(app.screen, FileSystemDialogBase)


@pytest.mark.asyncio
async def test_save_file_overwrite_prompt_priority_outranks_save_file(tmp_path):
    """SaveFile's internal composition with messagebox keeps working:
    the WARNING overwrite prompt (HIGH) is always shown on top of the
    SaveFile dialog (MEDIUM) that spawned it."""
    from nannokit.dialogs import SaveFile

    existing = tmp_path / "existing.txt"
    existing.write_text("old")
    results: list = []

    class DemoApp(HostApp):
        def on_key(self, event) -> None:
            if event.key == "s":
                SaveFile.show(
                    initial_directory=tmp_path,
                    default_filename="existing.txt",
                    callback=results.append,
                )

    app = DemoApp()
    async with app.run_test() as pilot:
        await pilot.press("s")
        await pilot.pause()
        await pilot.click("#filedialogs-select")
        await pilot.pause()

        assert isinstance(app.screen, MessageDialog)
        assert DialogQueue.current_priority() == DialogPriority.HIGH

        await pilot.click("#yes")
        await pilot.pause()

    assert results == [existing.resolve()]
