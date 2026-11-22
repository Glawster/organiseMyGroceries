"""Tests for named shopping lists under lists/."""

import json
import os
from datetime import datetime
from pathlib import Path

import pytest

from organiseMyGroceries.listLibrary import (
    listCreate,
    listNameValidate,
    listPathResolve,
    listQuarantine,
    listRename,
    listSummarise,
    listTouch,
)


def testListPathResolveTreatsBareNameAsListName() -> None:
    """A bare name means lists/<name>.json."""

    assert listPathResolve("weekly") == Path("lists/weekly.json")
    assert listPathResolve("weekly", Path("lists")) == Path("lists/weekly.json")


@pytest.mark.parametrize(
    "reference", ["weekly.json", "list.txt", "lists/weekly.json", "/tmp/a.json"]
)
def testListPathResolveKeepsPaths(reference: str) -> None:
    """Anything with a suffix or a directory is already a path."""

    assert listPathResolve(reference) == Path(reference)


def testListSummariseListsOnlyShoppingLists(tmp_path: Path) -> None:
    """Lists are counted and sorted; other JSON files are left out."""

    (tmp_path / "weekly.json").write_text(
        json.dumps([{"name": "Milk"}, {"name": "Tea", "active": False}])
    )
    (tmp_path / "Party.json").write_text(json.dumps([{"name": "Crisps"}]))
    (tmp_path / "catalogue.json").write_text(json.dumps({"version": 1, "items": []}))
    (tmp_path / "broken.json").write_text("{not json")
    (tmp_path / ".weekly.json.tmp").write_text("[]")
    (tmp_path / "notes.txt").write_text("Milk\n")

    summaries = listSummarise(tmp_path)

    assert [(each.name, each.items, each.active) for each in summaries] == [
        ("Party", 1, 1),
        ("weekly", 2, 1),
    ]


def testListSummariseMissingDirectoryIsEmpty(tmp_path: Path) -> None:
    """No lists directory yet simply means no lists."""

    assert listSummarise(tmp_path / "missing") == []


def testListCreateWritesEmptyList(tmp_path: Path) -> None:
    """A new list is an empty JSON list, and its directory is created."""

    path = listCreate("weekly", tmp_path / "lists")

    assert json.loads(path.read_text()) == []
    with pytest.raises(ValueError, match="already exists"):
        listCreate("weekly", tmp_path / "lists")


@pytest.mark.parametrize("name", ["", "-x", "a b", "../up", "a/b", "w.json"])
def testListNameValidateRejectsUnusableNames(name: str) -> None:
    """Names are single words so they always stay inside lists/."""

    with pytest.raises(ValueError, match="list name"):
        listNameValidate(name)


def testListRenameMovesTheFile(tmp_path: Path) -> None:
    """Renaming keeps the contents under the new name."""

    (tmp_path / "weekly.json").write_text('[{"name": "Milk"}]')
    (tmp_path / "party.json").write_text("[]")

    target = listRename("weekly", "monday", tmp_path)

    assert target == tmp_path / "monday.json"
    assert "Milk" in target.read_text()
    assert not (tmp_path / "weekly.json").exists()
    with pytest.raises(ValueError, match="already exists"):
        listRename("monday", "party", tmp_path)
    with pytest.raises(ValueError, match="no list called"):
        listRename("missing", "other", tmp_path)
    with pytest.raises(ValueError, match="list name"):
        listRename("monday", "../up", tmp_path)


def testListQuarantineHidesButKeepsTheList(tmp_path: Path) -> None:
    """A removed list leaves the picker but is kept in quarantine/."""

    (tmp_path / "weekly.json").write_text('[{"name": "Milk"}]')
    first = listQuarantine("weekly", tmp_path)
    (tmp_path / "weekly.json").write_text('[{"name": "Tea"}]')
    second = listQuarantine("weekly", tmp_path)

    assert first.parent == second.parent == tmp_path / "quarantine"
    assert first != second
    assert "Milk" in first.read_text() and "Tea" in second.read_text()
    assert listSummarise(tmp_path) == []
    with pytest.raises(ValueError, match="no list called"):
        listQuarantine("weekly", tmp_path)


def testListTouchSetsLastUsed(tmp_path: Path) -> None:
    """The picker's last-used time follows the list being used."""

    path = tmp_path / "weekly.json"
    path.write_text("[]")
    os.utime(path, (0, 0))
    assert listSummarise(tmp_path)[0].lastUsed == datetime.fromtimestamp(0)

    listTouch(path)

    lastUsed = listSummarise(tmp_path)[0].lastUsed
    assert (datetime.now() - lastUsed).total_seconds() < 60
