"""Tests for DialogManager's app-resolution logic."""

from __future__ import annotations

import pytest

from nannokit.dialogs.core import DialogManager

from .conftest import HostApp


def test_resolve_app_raises_with_no_app_anywhere():
    DialogManager.detach()
    with pytest.raises(RuntimeError, match="could not find a running"):
        DialogManager.resolve_app()


@pytest.mark.asyncio
async def test_attach_makes_resolve_app_succeed_outside_event_context():
    app = HostApp()
    async with app.run_test():
        DialogManager.attach(app)
        # Resolve from completely outside any Textual-managed call -
        # this is exactly the case `active_app` alone cannot cover.
        assert DialogManager.resolve_app() is app
    DialogManager.detach()


@pytest.mark.asyncio
async def test_active_app_resolves_without_explicit_attach():
    """The zero-setup path: no `attach()` call, just a running App."""
    DialogManager.detach()
    resolved: dict[str, object] = {}

    class ProbeApp(HostApp):
        def on_key(self, event) -> None:
            if event.key == "p":
                # Called from inside a real Textual event handler -
                # `active_app` is set for the duration of this call
                # without anyone having called `DialogManager.attach`.
                resolved["app"] = DialogManager.resolve_app()

    app = ProbeApp()
    async with app.run_test() as pilot:
        await pilot.press("p")
        assert resolved["app"] is app


def test_detach_clears_explicit_app():
    app = HostApp()
    DialogManager.attach(app)
    assert DialogManager.is_attached()
    DialogManager.detach()
    assert not DialogManager.is_attached()
