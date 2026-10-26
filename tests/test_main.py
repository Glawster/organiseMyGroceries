"""Tests for command parsing and packaged CLI orchestration."""

import json
from pathlib import Path

import pytest

from organiseMyGroceries import __main__ as moduleMain
from organiseMyGroceries import main


def testModuleEntryPointUsesPackageMain() -> None:
    """`python -m organiseMyGroceries` delegates to the package main module."""

    assert moduleMain.main is main.main


def testCliBuildParserSupportsListAdd() -> None:
    """List add exposes source and safe confirmation options."""

    args = main.cliBuildParser().parse_args(
        ["list", "add", "--source", "items.json", "--confirm"]
    )

    assert args.object == "list"
    assert args.action == "add"
    assert args.source == Path("items.json")
    assert args.confirm is True


def testCliBuildParserSupportsListExport() -> None:
    """List export uses --source and defaults to preview."""

    args = main.cliBuildParser().parse_args(
        ["list", "export", "--source", "items.json"]
    )

    assert args.object == "list"
    assert args.action == "export"
    assert args.source == Path("items.json")
    assert args.confirm is False


def testCliBuildParserListAddDefaultsSource() -> None:
    """List add keeps the historical default shopping-list path."""

    args = main.cliBuildParser().parse_args(["list", "add"])

    assert args.source == Path("shoppingList.json")
    assert args.confirm is False


def testCliBuildParserRejectsLegacyTopLevelAdd() -> None:
    """Actions belong under an object; the old top-level add command is gone."""

    with pytest.raises(SystemExit):
        main.cliBuildParser().parse_args(["add", "--source", "items.json"])


def testCliRunDryRunDoesNotOpenStore(tmp_path, monkeypatch) -> None:
    """The default list add workflow previews data without starting a browser."""

    source = tmp_path / "items.json"
    source.write_text('[{"name": "Milk"}]')
    opened = False

    def _basketAdd(_items):
        nonlocal opened
        opened = True

    monkeypatch.setattr(main, "basketAdd", _basketAdd)

    status = main.cliRun(["list", "add", "--source", str(source)])

    assert status == 0
    assert opened is False


def testCliRunReturnsFailureForMissingSource(tmp_path) -> None:
    """Input validation failures become a non-zero CLI status."""

    status = main.cliRun(["list", "add", "--source", str(tmp_path / "missing.json")])

    assert status == 1


def testCliBuildParserSupportsCatalogueImport() -> None:
    """The catalogue import command is nested and safe by default."""

    args = main.cliBuildParser().parse_args(
        ["catalogue", "import", "--source", "groceries.txt"]
    )

    assert args.object == "catalogue"
    assert args.action == "import"
    assert args.source == Path("groceries.txt")
    assert args.confirm is False


def testCliRunCatalogueImportDryRunDoesNotWrite(tmp_path, monkeypatch) -> None:
    """Preview catalogue import validates source text without writing JSON."""

    monkeypatch.chdir(tmp_path)
    source = tmp_path / "groceries.txt"
    source.write_text("Apples\n")

    status = main.cliRun(["catalogue", "import", "--source", str(source)])

    assert status == 0
    assert not (tmp_path / "output" / "catalogue.json").exists()


def testCliRunCatalogueImportConfirmedWritesCatalogue(tmp_path, monkeypatch) -> None:
    """The production CLI path writes a validated catalogue under output/."""

    monkeypatch.chdir(tmp_path)
    source = tmp_path / "groceries.txt"
    source.write_text("Apples\nApples\nMilk\n")

    status = main.cliRun(["catalogue", "import", "--source", str(source), "--confirm"])

    document = json.loads((tmp_path / "output" / "catalogue.json").read_text())
    assert status == 0
    assert [item["name"] for item in document["items"]] == ["Apples", "Milk"]
    assert document["items"][0]["id"] == "item-001"
    assert "quantity" not in document["items"][0]


def testCliRunCatalogueImportReturnsFailureForMissingSource(
    tmp_path, monkeypatch
) -> None:
    """Catalogue import failures become a non-zero CLI status."""

    monkeypatch.chdir(tmp_path)

    status = main.cliRun(
        ["catalogue", "import", "--source", str(tmp_path / "missing.txt")]
    )

    assert status == 1


def testCliRunListExportConfirmedWritesText(tmp_path, monkeypatch) -> None:
    """List export writes active names under output/ when confirmed."""

    monkeypatch.chdir(tmp_path)
    source = tmp_path / "items.json"
    source.write_text('[{"name": "Milk", "active": true}]')

    status = main.cliRun(["list", "export", "--source", str(source), "--confirm"])

    assert status == 0
    assert (tmp_path / "output" / "items.txt").read_text() == "Milk\n"
