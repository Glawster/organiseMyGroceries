"""Headless tests for the shopping-list terminal UI."""

import asyncio
import json
from pathlib import Path
from typing import Any, Awaitable, Callable

from textual.pilot import Pilot
from textual.widgets import DataTable, Input, Static

from organiseMyGroceries.ui.confirmDialog import ConfirmDialog
from organiseMyGroceries.ui.itemDialog import ItemDialog
from organiseMyGroceries.ui.listApp import ListApp
from organiseMyGroceries.ui.listScreen import ListScreen
from organiseMyGroceries.ui.nameDialog import NameDialog
from organiseMyGroceries.ui.pickerScreen import PickerScreen


def _listWrite(tmp_path: Path) -> Path:
    path = tmp_path / "shoppingList.json"
    path.write_text(
        json.dumps(
            [{"id": "item-1", "name": "Milk"}, {"id": "item-2", "name": "Bread"}]
        )
    )
    return path


def _appRun(
    listPath: Path | None,
    scenario: Callable[[ListApp, Pilot], Awaitable[Any]],
    directory: Path | None = None,
):
    """Run one UI scenario headlessly at a typical terminal size."""

    async def _run() -> Any:
        if directory is None:
            app = ListApp(listPath)
        else:
            app = ListApp(listPath, directory)
        async with app.run_test(size=(100, 32)) as pilot:
            await pilot.pause()
            return await scenario(app, pilot)

    return asyncio.run(_run())


def _saved(listPath: Path) -> list[dict[str, Any]]:
    return json.loads(listPath.read_text())


def testListAppShowsEveryItem(tmp_path: Path) -> None:
    """The table lists each item from the JSON file."""

    async def scenario(app: ListApp, pilot: Pilot) -> int:
        return app.screen.query_one("#items", DataTable).row_count

    assert _appRun(_listWrite(tmp_path), scenario) == 2


def testListAppAddsAndSavesItem(tmp_path: Path) -> None:
    """Adding through the form and saving writes the new item."""

    listPath = _listWrite(tmp_path)

    async def scenario(app: ListApp, pilot: Pilot) -> None:
        await pilot.press("a")
        await pilot.pause()
        assert isinstance(app.screen, ItemDialog)
        await pilot.press(*"Eggs")
        app.screen.query_one("#field-quantity", Input).value = "6"
        await pilot.press("enter")
        await pilot.pause()
        await pilot.press("ctrl+s")
        await pilot.pause()

    _appRun(listPath, scenario)

    saved = _saved(listPath)
    assert saved[-1]["name"] == "Eggs"
    assert saved[-1]["quantity"] == 6
    assert saved[-1]["id"] == "item-3"


def testListAppFormRejectsBadQuantity(tmp_path: Path) -> None:
    """The form stays open and nothing changes for an invalid quantity."""

    listPath = _listWrite(tmp_path)

    async def scenario(app: ListApp, pilot: Pilot) -> bool:
        await pilot.press("a")
        await pilot.pause()
        await pilot.press(*"Eggs")
        app.screen.query_one("#field-quantity", Input).value = "0"
        await pilot.press("enter")
        await pilot.pause()
        return isinstance(app.screen, ItemDialog)

    assert _appRun(listPath, scenario) is True
    assert len(_saved(listPath)) == 2


def testListAppEditsTogglesAndRemoves(tmp_path: Path) -> None:
    """Edit, deactivate, and confirmed removal are all saved."""

    listPath = _listWrite(tmp_path)

    async def scenario(app: ListApp, pilot: Pilot) -> None:
        # Edit the first row (Milk) with Enter.
        await pilot.press("enter")
        await pilot.pause()
        app.screen.query_one("#field-notes", Input).value = "semi skimmed"
        await pilot.press("enter")
        await pilot.pause()
        # Deactivate Milk, then remove Bread after confirming.
        await pilot.press("space")
        await pilot.press("down", "d")
        await pilot.pause()
        assert isinstance(app.screen, ConfirmDialog)
        await pilot.press("y")
        await pilot.pause()
        await pilot.press("ctrl+s")
        await pilot.pause()

    _appRun(listPath, scenario)

    saved = _saved(listPath)
    assert [record["name"] for record in saved] == ["Milk"]
    assert saved[0]["notes"] == "semi skimmed"
    assert saved[0]["active"] is False


def testListAppRemoveCancelledKeepsItem(tmp_path: Path) -> None:
    """Answering no to removal changes nothing."""

    listPath = _listWrite(tmp_path)

    async def scenario(app: ListApp, pilot: Pilot) -> int:
        await pilot.press("d")
        await pilot.pause()
        await pilot.press("n")
        await pilot.pause()
        return app.screen.query_one("#items", DataTable).row_count

    assert _appRun(listPath, scenario) == 2


def testListAppQuitAsksBeforeDiscardingChanges(tmp_path: Path) -> None:
    """Quitting with unsaved edits asks first and leaves the file unchanged."""

    listPath = _listWrite(tmp_path)
    before = listPath.read_text()

    async def scenario(app: ListApp, pilot: Pilot) -> tuple[bool, bool]:
        await pilot.press("space", "q")
        await pilot.pause()
        asked = isinstance(app.screen, ConfirmDialog)
        await pilot.press("y")
        await pilot.pause()
        return asked, app.is_running

    asked, running = _appRun(listPath, scenario)

    assert asked is True
    assert running is False
    assert listPath.read_text() == before


def testListAppQuitsImmediatelyWhenSaved(tmp_path: Path) -> None:
    """With nothing to lose, q quits without a prompt."""

    async def scenario(app: ListApp, pilot: Pilot) -> bool:
        await pilot.press("q")
        await pilot.pause()
        return app.is_running

    assert _appRun(_listWrite(tmp_path), scenario) is False


def testListAppButtonsRunTheSameActions(tmp_path: Path) -> None:
    """Clicking Active on/off then Save behaves like the key bindings."""

    listPath = _listWrite(tmp_path)

    async def scenario(app: ListApp, pilot: Pilot) -> None:
        await pilot.click("#toggle")
        await pilot.click("#save")
        await pilot.pause()

    _appRun(listPath, scenario)

    assert _saved(listPath)[0]["active"] is False


## list picker


def _listsWrite(tmp_path: Path) -> Path:
    """Two fictional lists plus a catalogue that the picker must ignore."""

    directory = tmp_path / "output"
    directory.mkdir()
    (directory / "party.json").write_text(json.dumps([{"name": "Crisps"}]))
    _listWrite(directory).rename(directory / "weekly.json")
    (directory / "catalogue.json").write_text(json.dumps({"version": 1, "items": []}))
    return directory


def _pickerRows(app: ListApp) -> list[list[str]]:
    table = app.screen.query_one("#lists", DataTable)
    return [
        [str(cell) for cell in table.get_row_at(row)] for row in range(table.row_count)
    ]


def testPickerShowsListsAndOpensOne(tmp_path: Path) -> None:
    """The picker lists each shopping list; Enter opens it, q comes back."""

    directory = _listsWrite(tmp_path)

    async def scenario(app: ListApp, pilot: Pilot) -> None:
        assert isinstance(app.screen, PickerScreen)
        assert _pickerRows(app) == [["party", "1", "1"], ["weekly", "2", "2"]]
        await pilot.press("down", "enter")
        await pilot.pause()
        assert isinstance(app.screen, ListScreen)
        assert app.screen.listPath == directory / "weekly.json"
        await pilot.press("q")
        await pilot.pause()
        assert isinstance(app.screen, PickerScreen)
        assert app.is_running
        await pilot.press("q")
        await pilot.pause()
        assert not app.is_running

    _appRun(None, scenario, directory)


def testPickerCountsFollowSavedEdits(tmp_path: Path) -> None:
    """Deactivating and saving an item updates the picker's counts."""

    directory = _listsWrite(tmp_path)

    async def scenario(app: ListApp, pilot: Pilot) -> list[list[str]]:
        await pilot.press("down", "enter")
        await pilot.pause()
        await pilot.press("space", "ctrl+s", "q")
        await pilot.pause()
        return _pickerRows(app)

    assert _appRun(None, scenario, directory)[1] == ["weekly", "2", "1"]


def testPickerCloseWithUnsavedChangesAsksFirst(tmp_path: Path) -> None:
    """Closing an edited list asks, then returns to the picker unchanged."""

    directory = _listsWrite(tmp_path)
    before = (directory / "party.json").read_text()

    async def scenario(app: ListApp, pilot: Pilot) -> None:
        await pilot.press("enter")
        await pilot.pause()
        await pilot.press("space", "q")
        await pilot.pause()
        assert isinstance(app.screen, ConfirmDialog)
        await pilot.press("y")
        await pilot.pause()
        assert isinstance(app.screen, PickerScreen)

    _appRun(None, scenario, directory)

    assert (directory / "party.json").read_text() == before


def testPickerCreatesNewList(tmp_path: Path) -> None:
    """n asks for a name, creates an empty list, and opens it."""

    directory = _listsWrite(tmp_path)

    async def scenario(app: ListApp, pilot: Pilot) -> int:
        await pilot.press("n")
        await pilot.pause()
        assert isinstance(app.screen, NameDialog)
        await pilot.press(*"bbq", "enter")
        await pilot.pause()
        assert isinstance(app.screen, ListScreen)
        return app.screen.query_one("#items", DataTable).row_count

    assert _appRun(None, scenario, directory) == 0
    assert json.loads((directory / "bbq.json").read_text()) == []


def testPickerRejectsExistingListName(tmp_path: Path) -> None:
    """A name already in use keeps the dialog open with a message."""

    directory = _listsWrite(tmp_path)

    async def scenario(app: ListApp, pilot: Pilot) -> bool:
        await pilot.press("n")
        await pilot.pause()
        await pilot.press(*"weekly", "enter")
        await pilot.pause()
        return isinstance(app.screen, NameDialog)

    assert _appRun(None, scenario, directory) is True


def testPickerExplainsWhenThereAreNoLists(tmp_path: Path) -> None:
    """An empty or missing output directory shows how to start."""

    async def scenario(app: ListApp, pilot: Pilot) -> str:
        return str(app.screen.query_one("#status", Static).render())

    assert "press n to create one" in _appRun(None, scenario, tmp_path / "output")
