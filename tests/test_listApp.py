"""Headless tests for the shopping-list terminal UI."""

import asyncio
import json
from pathlib import Path
from typing import Any, Awaitable, Callable

from textual.pilot import Pilot
from textual.widgets import DataTable, Input

from organiseMyGroceries.ui.confirmDialog import ConfirmDialog
from organiseMyGroceries.ui.itemDialog import ItemDialog
from organiseMyGroceries.ui.listApp import ListApp


def _listWrite(tmp_path: Path) -> Path:
    path = tmp_path / "shoppingList.json"
    path.write_text(
        json.dumps(
            [{"id": "item-1", "name": "Milk"}, {"id": "item-2", "name": "Bread"}]
        )
    )
    return path


def _appRun(listPath: Path, scenario: Callable[[ListApp, Pilot], Awaitable[Any]]):
    """Run one UI scenario headlessly at a typical terminal size."""

    async def _run() -> Any:
        app = ListApp(listPath)
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
