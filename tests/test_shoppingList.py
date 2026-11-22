"""Tests for grocery-list parsing and generated artifacts."""

import json
from pathlib import Path

import pytest

from organiseMyGroceries import shoppingList


def _sampleItems() -> list[dict[str, object]]:
    return [
        {"name": "Soda farl", "tescoSearch": "Soda farl", "active": True},
        {"name": "Milk", "tescoSearch": "", "active": True},
        {"name": "Hidden", "tescoSearch": "Hidden", "active": False},
    ]


def testListImportCreatesExpectedSchema(tmp_path: Path, monkeypatch) -> None:
    """A real text source is imported into the documented JSON schema."""

    monkeypatch.chdir(tmp_path)
    source = tmp_path / "shopping.txt"
    source.write_text("Soda farl\n\nMilk\n")

    output = shoppingList.listImport(source, Path("output"))

    data = json.loads(output.read_text())
    assert output == tmp_path / "output" / "shopping.json"
    assert [record["name"] for record in data] == ["Soda farl", "Milk"]
    assert data[0]["id"] == "item-1"
    assert data[0]["active"] is True
    assert data[0]["quantity"] == 1


def testListImportNeverOverwritesExistingList(tmp_path: Path, monkeypatch) -> None:
    """A second import fails rather than discarding edits to the JSON list."""

    monkeypatch.chdir(tmp_path)
    source = tmp_path / "shopping.txt"
    source.write_text("Milk\n")
    output = shoppingList.listImport(source, Path("output"))
    output.write_text('[{"id": "item-1", "name": "Edited"}]')

    with pytest.raises(ValueError, match="already exists"):
        shoppingList.listImport(source, Path("output"))

    assert "Edited" in output.read_text()


def testListImportUsesGivenName(tmp_path: Path, monkeypatch) -> None:
    """An explicit name replaces the text file's name."""

    monkeypatch.chdir(tmp_path)
    source = tmp_path / "list.txt"
    source.write_text("Milk\n")

    output = shoppingList.listImport(source, Path("output"), name="party")

    assert output == (tmp_path / "output" / "party.json").resolve()
    assert output.is_file()


def testListImportRejectsUnusableName(tmp_path: Path, monkeypatch) -> None:
    """A name that is not a plain word cannot escape output/."""

    monkeypatch.chdir(tmp_path)
    source = tmp_path / "list.txt"
    source.write_text("Milk\n")

    with pytest.raises(ValueError, match="list name"):
        shoppingList.listImport(source, Path("output"), name="../escape")


def testListImportHonoursDryRun(tmp_path: Path, monkeypatch) -> None:
    """Preview import creates neither the output directory nor the list."""

    monkeypatch.chdir(tmp_path)
    source = tmp_path / "shopping.txt"
    source.write_text("Milk\n")

    shoppingList.listImport(source, Path("output"), dryRun=True)

    assert not (tmp_path / "output").exists()


def testListLoadTextKeepsExistingImportedList(tmp_path: Path, monkeypatch) -> None:
    """Sending a text list never replaces an existing, possibly edited, JSON list."""

    monkeypatch.chdir(tmp_path)
    source = tmp_path / "shopping.txt"
    source.write_text("Apples\n")
    existing = tmp_path / "output" / "shopping.json"
    existing.parent.mkdir()
    existing.write_text('[{"id": "item-1", "name": "Edited"}]')

    items = shoppingList.listLoad(source, Path("output"), dryRun=False)

    assert items == ["Apples"]
    assert "Edited" in existing.read_text()


def testListExportHonoursDryRun(tmp_path: Path, monkeypatch) -> None:
    """A preview reports its destination without creating output."""

    monkeypatch.chdir(tmp_path)
    source = tmp_path / "shopping.json"
    source.write_text(json.dumps(_sampleItems()))

    output = shoppingList.listExport(source, Path("output"), dryRun=True)

    assert output == tmp_path / "output" / "shopping.txt"
    assert not output.exists()


def testListExportWritesActiveItems(tmp_path: Path, monkeypatch) -> None:
    """The production export path writes active search terms under output."""

    monkeypatch.chdir(tmp_path)
    source = tmp_path / "shopping.json"
    source.write_text(json.dumps(_sampleItems()))

    output = shoppingList.listExport(source, Path("output"))

    assert output.read_text() == "Soda farl\nMilk\n"


def testListLoadRejectsInvalidRecords(tmp_path: Path, monkeypatch) -> None:
    """An active record without a usable name produces a clear failure."""

    monkeypatch.chdir(tmp_path)
    source = tmp_path / "shopping.json"
    source.write_text('[{"active": true}]')

    with pytest.raises(ValueError, match="active item 1.*needs a name"):
        shoppingList.listLoad(source, Path("output"))


def testListLoadRejectsMissingSource(tmp_path: Path, monkeypatch) -> None:
    """A missing input path fails before any processing starts."""

    monkeypatch.chdir(tmp_path)

    with pytest.raises(ValueError, match="source file does not exist"):
        shoppingList.listLoad(Path("missing.json"), Path("output"))


def testListLoadTextPreviewHasNoSideEffects(tmp_path: Path, monkeypatch) -> None:
    """Text input loads in preview mode without writing converted output."""

    monkeypatch.chdir(tmp_path)
    source = tmp_path / "shopping.txt"
    source.write_text(" Apples\nBananas\n")

    items = shoppingList.listLoad(source, Path("output"), dryRun=True)

    assert items == ["Apples", "Bananas"]
    assert not (tmp_path / "output").exists()


def testListLoadTextConfirmedCreatesConvertedOutput(
    tmp_path: Path, monkeypatch
) -> None:
    """Confirmed text loading exercises the real conversion composition."""

    monkeypatch.chdir(tmp_path)
    source = tmp_path / "shopping.txt"
    source.write_text("Apples\n")

    items = shoppingList.listLoad(source, Path("output"), dryRun=False)

    assert items == ["Apples"]
    assert (
        json.loads((tmp_path / "output" / "shopping.json").read_text())[0]["name"]
        == "Apples"
    )


@pytest.mark.parametrize(
    ("content", "message"),
    [
        ("not json", "invalid JSON"),
        ('{"name": "Milk"}', "must contain a JSON list"),
        ('["Milk"]', "item 1.*must be an object"),
    ],
)
def testListLoadRejectsMalformedJsonShapes(
    tmp_path: Path, monkeypatch, content: str, message: str
) -> None:
    """Malformed JSON and schema boundaries report their failing stage."""

    monkeypatch.chdir(tmp_path)
    source = tmp_path / "shopping.json"
    source.write_text(content)

    with pytest.raises(ValueError, match=message):
        shoppingList.listLoad(source, Path("output"))


def testListLoadRejectsUnsupportedSuffix(tmp_path: Path, monkeypatch) -> None:
    """Existing files with unsupported formats fail validation."""

    monkeypatch.chdir(tmp_path)
    source = tmp_path / "shopping.csv"
    source.write_text("Milk\n")

    with pytest.raises(ValueError, match="must use one of"):
        shoppingList.listLoad(source, Path("output"))


def testListExportEmptyListWritesEmptyFile(tmp_path: Path, monkeypatch) -> None:
    """An empty list produces an empty artifact without a phantom blank item."""

    monkeypatch.chdir(tmp_path)
    source = tmp_path / "shopping.json"
    source.write_text("[]")

    output = shoppingList.listExport(source, Path("output"))

    assert output.read_text() == ""


def testListExportRejectsOutputOutsideRoot(tmp_path: Path, monkeypatch) -> None:
    """Generated artifacts cannot escape the approved output directory."""

    monkeypatch.chdir(tmp_path)
    source = tmp_path / "shopping.json"
    source.write_text("[]")

    with pytest.raises(ValueError, match="output directory must be"):
        shoppingList.listExport(source, Path("elsewhere"))
