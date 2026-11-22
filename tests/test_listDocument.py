"""Tests for the shopping-list JSON document model."""

import json
from pathlib import Path

import pytest

from organiseMyGroceries import listDocument


def _listWrite(path: Path, records: list) -> Path:
    path.write_text(json.dumps(records))
    return path


def testListDocumentLoadFillsDefaultsAndKeepsUnknownKeys(tmp_path: Path) -> None:
    """Hand-written records gain defaults and ids without losing extra data."""

    source = _listWrite(
        tmp_path / "list.json",
        [{"name": "Soda farl", "aisle": 4}, {"id": "item-7", "name": "Milk"}],
    )

    records = listDocument.listDocumentLoad(source)

    assert records[0]["id"] == "item-8"
    assert records[0]["tescoSearch"] == "Soda farl"
    assert records[0]["quantity"] == 1
    assert records[0]["active"] is True
    assert records[0]["aisle"] == 4
    assert records[1]["id"] == "item-7"


@pytest.mark.parametrize(
    ("records", "message"),
    [
        ({"name": "Milk"}, "JSON list"),
        (["Milk"], "must be an object"),
        ([{"name": " "}], "needs a name"),
        ([{"name": "Milk", "quantity": 0}], "at least 1"),
        ([{"name": "Milk", "quantity": True}], "whole number"),
        ([{"name": "Milk", "active": "no"}], "true or false"),
        ([{"name": "Milk", "notes": 3}], "must be text"),
        ([{"id": "x", "name": "Milk"}], "invalid identifier"),
        ([{"id": "item-1", "name": "A"}, {"id": "item-1", "name": "B"}], "reuses"),
    ],
)
def testListDocumentLoadRejectsInvalidDocuments(
    tmp_path: Path, records: object, message: str
) -> None:
    """Invalid documents fail with a clear message instead of loading."""

    source = tmp_path / "list.json"
    source.write_text(json.dumps(records))

    with pytest.raises(ValueError, match=message):
        listDocument.listDocumentLoad(source)


def testListDocumentLoadRejectsMalformedJson(tmp_path: Path) -> None:
    """Malformed JSON reports the source."""

    source = tmp_path / "list.json"
    source.write_text("[")

    with pytest.raises(ValueError, match="invalid JSON"):
        listDocument.listDocumentLoad(source)


def testListDocumentSaveRoundTripsEdits(tmp_path: Path) -> None:
    """Add, update, toggle, and remove persist through save and reload."""

    source = _listWrite(
        tmp_path / "list.json",
        [{"id": "item-1", "name": "Milk"}, {"id": "item-2", "name": "Bread"}],
    )
    records = listDocument.listDocumentLoad(source)

    added = listDocument.recordAdd(records, {"name": " Eggs ", "quantity": 12})
    listDocument.recordUpdate(records, "item-1", {"notes": "semi skimmed"})
    listDocument.recordToggle(records, "item-2")
    listDocument.recordRemove(records, "item-2")
    listDocument.listDocumentSave(source, records)

    reloaded = listDocument.listDocumentLoad(source)
    assert added["id"] == "item-3"
    assert [record["name"] for record in reloaded] == ["Milk", "Eggs"]
    assert reloaded[0]["notes"] == "semi skimmed"
    assert reloaded[1]["quantity"] == 12
    assert not (tmp_path / ".list.json.tmp").exists()


def testListDocumentSaveHonoursDryRun(tmp_path: Path) -> None:
    """Dry-run validates but does not write."""

    target = tmp_path / "list.json"

    listDocument.listDocumentSave(
        target, [listDocument.recordBuild("item-1", "Milk")], dryRun=True
    )

    assert not target.exists()


def testListDocumentSaveRejectsBadTargets(tmp_path: Path) -> None:
    """Only .json files in an existing directory can be written."""

    record = listDocument.recordBuild("item-1", "Milk")

    with pytest.raises(ValueError, match=r"\.json"):
        listDocument.listDocumentSave(tmp_path / "list.txt", [record])
    with pytest.raises(ValueError, match="does not exist"):
        listDocument.listDocumentSave(tmp_path / "missing" / "list.json", [record])


def testRecordUpdateRejectsInvalidChangesWithoutPartialEdits() -> None:
    """A rejected edit leaves the record exactly as it was."""

    records = [listDocument.recordBuild("item-1", "Milk")]

    with pytest.raises(ValueError, match="needs a name"):
        listDocument.recordUpdate(records, "item-1", {"name": "", "notes": "x"})
    with pytest.raises(ValueError, match="cannot be edited"):
        listDocument.recordUpdate(records, "item-1", {"id": "item-9"})

    assert records[0] == listDocument.recordBuild("item-1", "Milk")


def testRecordUpdateEmptyStoreSearchFallsBackToName() -> None:
    """Clearing the store search uses the item name."""

    records = [listDocument.recordBuild("item-1", "Milk")]

    listDocument.recordUpdate(records, "item-1", {"tescoSearch": " "})

    assert records[0]["tescoSearch"] == "Milk"


def testRecordFindRejectsUnknownId() -> None:
    """Unknown identifiers fail clearly."""

    with pytest.raises(ValueError, match="no shopping-list item"):
        listDocument.recordFind([], "item-1")


@pytest.mark.parametrize(
    ("text", "expected"), [("1", 1), (" 12 ", 12), ("0", None), ("x", None)]
)
def testQuantityParse(text: str, expected: int | None) -> None:
    """Quantities are whole numbers of at least one."""

    if expected is None:
        with pytest.raises(ValueError):
            listDocument.quantityParse(text)
    else:
        assert listDocument.quantityParse(text) == expected
