"""End-to-end tests for OpenFile, OpenFolder, and SaveFile."""

from __future__ import annotations

from pathlib import Path

import pytest
from textual.widgets import Input

from nannokit.dialogs import OpenFile, OpenFolder, SaveFile
from nannokit.dialogs.filedialogs import FileSystemDialogBase
from nannokit.dialogs.filedialogs.tree import FilterableDirectoryTree
from nannokit.dialogs.messagebox import MessageDialog

from .conftest import HostApp


def _make_app(action: callable) -> type[HostApp]:
    """Build a HostApp subclass that runs `action(app)` on pressing 'd'."""

    class DemoApp(HostApp):
        def on_key(self, event) -> None:
            if event.key == "d":
                action(self)

    return DemoApp


# -- OpenFile ------------------------------------------------------------


@pytest.mark.asyncio
async def test_open_file_accepts_an_existing_file(tmp_path: Path):
    target = tmp_path / "notes.txt"
    target.write_text("hello")
    results: list = []

    App = _make_app(
        lambda app: OpenFile.show(
            initial_directory=tmp_path,
            default_filename="notes.txt",
            callback=results.append,
        )
    )
    app = App()
    async with app.run_test() as pilot:
        await pilot.press("d")
        await pilot.pause()
        assert isinstance(app.screen, FileSystemDialogBase)

        await pilot.click("#filedialogs-select")
        await pilot.pause()

    assert results == [target.resolve()]


@pytest.mark.asyncio
async def test_open_file_must_exist_blocks_a_missing_file(tmp_path: Path):
    results: list = []

    App = _make_app(
        lambda app: OpenFile.show(
            initial_directory=tmp_path,
            default_filename="does-not-exist.txt",
            callback=results.append,
        )
    )
    app = App()
    async with app.run_test() as pilot:
        await pilot.press("d")
        await pilot.pause()

        await pilot.click("#filedialogs-select")
        await pilot.pause()

        # Invalid selection -> dialog stays open, callback not invoked.
        assert isinstance(app.screen, FileSystemDialogBase)
        assert results == []
        status = app.screen.query_one("#filedialogs-status")
        assert "does not exist" in str(status.content)


@pytest.mark.asyncio
async def test_open_file_escape_cancels_with_none(tmp_path: Path):
    results: list = []
    App = _make_app(
        lambda app: OpenFile.show(initial_directory=tmp_path, callback=results.append)
    )
    app = App()
    async with app.run_test() as pilot:
        await pilot.press("d")
        await pilot.pause()
        await pilot.press("escape")
        await pilot.pause()

    assert results == [None]


@pytest.mark.asyncio
async def test_open_file_multiselect_returns_sorted_paths(tmp_path: Path):
    a = tmp_path / "a.txt"
    b = tmp_path / "b.txt"
    a.write_text("a")
    b.write_text("b")
    results: list = []

    App = _make_app(
        lambda app: OpenFile.show(
            initial_directory=tmp_path,
            multiselect=True,
            callback=results.append,
        )
    )
    app = App()
    async with app.run_test() as pilot:
        await pilot.press("d")
        await pilot.pause()
        screen = app.screen
        assert isinstance(screen, FileSystemDialogBase)

        # Mark both files directly (exercising the same `_toggle_selected`
        # path that pressing "M" on a tree node uses), keeping this test
        # independent of DirectoryTree's async node-loading timing.
        screen._toggle_selected(a.resolve())
        screen._toggle_selected(b.resolve())

        await pilot.click("#filedialogs-select")
        await pilot.pause()

    assert results == [sorted([a.resolve(), b.resolve()])]


# -- OpenFolder ------------------------------------------------------------


@pytest.mark.asyncio
async def test_open_folder_returns_the_initial_directory_by_default(tmp_path: Path):
    results: list = []
    App = _make_app(
        lambda app: OpenFolder.show(initial_directory=tmp_path, callback=results.append)
    )
    app = App()
    async with app.run_test() as pilot:
        await pilot.press("d")
        await pilot.pause()

        await pilot.click("#filedialogs-select")
        await pilot.pause()

    assert results == [tmp_path.resolve()]


@pytest.mark.asyncio
async def test_open_folder_has_no_filename_input(tmp_path: Path):
    App = _make_app(lambda app: OpenFolder.show(initial_directory=tmp_path))
    app = App()
    async with app.run_test() as pilot:
        await pilot.press("d")
        await pilot.pause()
        assert len(app.screen.query("#filedialogs-filename_input")) == 0


# -- Path navigation --------------------------------------------------------


@pytest.mark.asyncio
async def test_typing_a_path_navigates_the_tree(tmp_path: Path):
    subdir = tmp_path / "subdir"
    subdir.mkdir()

    App = _make_app(lambda app: OpenFolder.show(initial_directory=tmp_path))
    app = App()
    async with app.run_test() as pilot:
        await pilot.press("d")
        await pilot.pause()
        screen = app.screen

        path_input = screen.query_one("#filedialogs-path_input", Input)
        screen.post_message(Input.Submitted(path_input, str(subdir)))
        await pilot.pause()

        assert screen.location == subdir.resolve()
        assert str(screen.query_one("#filedialogs-tree", FilterableDirectoryTree).path) == str(subdir)


# -- SaveFile ---------------------------------------------------------------


@pytest.mark.asyncio
async def test_save_file_no_prompt_for_a_new_filename(tmp_path: Path):
    results: list = []
    App = _make_app(
        lambda app: SaveFile.show(
            initial_directory=tmp_path,
            default_filename="new-file.txt",
            callback=results.append,
        )
    )
    app = App()
    async with app.run_test() as pilot:
        await pilot.press("d")
        await pilot.pause()

        await pilot.click("#filedialogs-select")
        await pilot.pause()

    assert results == [(tmp_path / "new-file.txt").resolve()]


@pytest.mark.asyncio
async def test_save_file_overwrite_prompt_accept(tmp_path: Path):
    existing = tmp_path / "existing.txt"
    existing.write_text("old")
    results: list = []

    App = _make_app(
        lambda app: SaveFile.show(
            initial_directory=tmp_path,
            default_filename="existing.txt",
            callback=results.append,
        )
    )
    app = App()
    async with app.run_test() as pilot:
        await pilot.press("d")
        await pilot.pause()

        await pilot.click("#filedialogs-select")
        await pilot.pause()

        # The overwrite confirmation is its own MessageDialog, on top.
        assert isinstance(app.screen, MessageDialog)

        await pilot.click("#yes")
        await pilot.pause()

    assert results == [existing.resolve()]


@pytest.mark.asyncio
async def test_save_file_overwrite_prompt_decline_keeps_dialog_open(tmp_path: Path):
    existing = tmp_path / "existing.txt"
    existing.write_text("old")
    results: list = []

    App = _make_app(
        lambda app: SaveFile.show(
            initial_directory=tmp_path,
            default_filename="existing.txt",
            callback=results.append,
        )
    )
    app = App()
    async with app.run_test() as pilot:
        await pilot.press("d")
        await pilot.pause()
        await pilot.click("#filedialogs-select")
        await pilot.pause()

        await pilot.click("#no")
        await pilot.pause()

        assert isinstance(app.screen, FileSystemDialogBase)

    assert results == []


# -- FilterableDirectoryTree (pure logic, no App needed) --------------------


def test_filter_paths_hides_dotfiles_by_default(tmp_path: Path):
    visible = tmp_path / "visible.txt"
    hidden = tmp_path / ".hidden.txt"
    visible.touch()
    hidden.touch()

    tree = FilterableDirectoryTree(tmp_path)
    result = set(tree.filter_paths([visible, hidden]))
    assert result == {visible}


def test_filter_paths_applies_glob_filters_to_files_only(tmp_path: Path):
    py_file = tmp_path / "main.py"
    txt_file = tmp_path / "notes.txt"
    sub_dir = tmp_path / "subdir"
    py_file.touch()
    txt_file.touch()
    sub_dir.mkdir()

    tree = FilterableDirectoryTree(tmp_path, glob_filters=["*.py"])
    result = set(tree.filter_paths([py_file, txt_file, sub_dir]))
    # Directories always pass through; only files are matched against the filter.
    assert result == {py_file, sub_dir}
