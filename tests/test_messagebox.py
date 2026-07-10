"""End-to-end tests for the `messagebox` API."""

from __future__ import annotations

import pytest

from nannokit.dialogs import messagebox
from nannokit.dialogs.messagebox import MessageDialog

from .conftest import HostApp


@pytest.mark.asyncio
async def test_show_pushes_dialog_and_default_ok_button_works():
    results: list[str | None] = []

    class DemoApp(HostApp):
        def on_key(self, event) -> None:
            if event.key == "d":
                messagebox.show(
                    "Something happened.",
                    title="Heads up",
                    callback=results.append,
                )

    app = DemoApp()
    async with app.run_test() as pilot:
        await pilot.press("d")
        await pilot.pause()
        assert isinstance(app.screen, MessageDialog)

        await pilot.press("enter")  # OK is focused by default
        await pilot.pause()

    assert results == ["OK"]


@pytest.mark.asyncio
async def test_escape_cancels_with_none():
    results: list[str | None] = []

    class DemoApp(HostApp):
        def on_key(self, event) -> None:
            if event.key == "d":
                messagebox.show(
                    "Discard changes?",
                    buttons=messagebox.buttons.YES_NO,
                    callback=results.append,
                )

    app = DemoApp()
    async with app.run_test() as pilot:
        await pilot.press("d")
        await pilot.pause()
        await pilot.press("escape")
        await pilot.pause()

    assert results == [None]


@pytest.mark.asyncio
async def test_custom_buttons_round_trip_the_clicked_label():
    results: list[str | None] = []

    class DemoApp(HostApp):
        def on_key(self, event) -> None:
            if event.key == "d":
                messagebox.show(
                    "Retry the operation?",
                    buttons=messagebox.buttons.RETRY_CANCEL,
                    type=messagebox.type.ERROR,
                    callback=results.append,
                )

    app = DemoApp()
    async with app.run_test() as pilot:
        await pilot.press("d")
        await pilot.pause()
        await pilot.click("#cancel")
        await pilot.pause()

    assert results == ["Cancel"]
