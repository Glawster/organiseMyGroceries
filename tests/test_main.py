"""Tests for command parsing and packaged CLI orchestration."""

import json
from pathlib import Path

import pytest

from organiseMyGroceries import __main__ as moduleMain
from organiseMyGroceries import main


def testModuleEntryPointUsesPackageMain() -> None:
    """`python -m organiseMyGroceries` delegates to the package main module."""

    assert moduleMain.main is main.main


def testCliVersionReportsPackageVersion(capsys: pytest.CaptureFixture[str]) -> None:
    """--version reports the single authoritative version."""

    from importlib.metadata import version

    from organiseMyGroceries.version import __version__

    with pytest.raises(SystemExit) as exitInfo:
        main.cliBuildParser().parse_args(["--version"])

    assert exitInfo.value.code == 0
    assert capsys.readouterr().out.strip() == f"groceries {__version__}"
    assert version("groceries") == __version__


def testCliBuildParserSupportsListSend() -> None:
    """List send exposes source and safe confirmation options."""

    args = main.cliBuildParser().parse_args(
        ["list", "send", "--source", "items.json", "--confirm"]
    )

    assert args.object == "list"
    assert args.action == "send"
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


def testCliBuildParserListSendRequiresSource() -> None:
    """List send acts on one specific list, so the list must be named."""

    with pytest.raises(SystemExit):
        main.cliBuildParser().parse_args(["list", "send"])
    with pytest.raises(SystemExit):
        main.cliBuildParser().parse_args(["list", "export"])


def testCliRunListSendResolvesListName(tmp_path, monkeypatch) -> None:
    """A bare list name means output/<name>.json."""

    monkeypatch.chdir(tmp_path)
    (tmp_path / "output").mkdir()
    (tmp_path / "output" / "weekly.json").write_text('[{"name": "Milk"}]')
    loaded: list[Path] = []
    monkeypatch.setattr(
        main, "listLoad", lambda source, *_args, **_kw: loaded.append(source) or []
    )

    assert main.cliRun(["list", "send", "-s", "weekly"]) == 0
    assert loaded == [Path("output/weekly.json")]


def testCliBuildParserRejectsLegacyTopLevelAdd() -> None:
    """Actions belong under an object; the old top-level add command is gone."""

    with pytest.raises(SystemExit):
        main.cliBuildParser().parse_args(["add", "--source", "items.json"])


def testCliBuildParserRejectsListAddForStoreSend() -> None:
    """Sending to a store is list send; list add no longer opens a store."""

    with pytest.raises(SystemExit):
        main.cliBuildParser().parse_args(["list", "add", "--source", "items.json"])


def testCliRunDryRunDoesNotOpenStore(tmp_path, monkeypatch) -> None:
    """The default list send workflow previews data without starting a browser."""

    source = tmp_path / "items.json"
    source.write_text('[{"name": "Milk"}]')
    opened = False

    def _basketAdd(_items):
        nonlocal opened
        opened = True

    monkeypatch.setattr(main, "basketAdd", _basketAdd)

    status = main.cliRun(["list", "send", "--source", str(source)])

    assert status == 0
    assert opened is False


def testCliRunConfirmedSendPassesItemsToStore(tmp_path, monkeypatch) -> None:
    """A confirmed list send hands the active search terms to the store adapter."""

    source = tmp_path / "items.json"
    source.write_text('[{"name": "Milk"}, {"name": "Bread", "active": false}]')
    sent: list[list[str]] = []
    monkeypatch.setattr(main, "basketAdd", lambda items: sent.append(list(items)))

    status = main.cliRun(["list", "send", "--source", str(source), "--confirm"])

    assert status == 0
    assert sent == [["Milk"]]


def testCliRunReturnsFailureForMissingSource(tmp_path) -> None:
    """Input validation failures become a non-zero CLI status."""

    status = main.cliRun(["list", "send", "--source", str(tmp_path / "missing.json")])

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


def testCliBuildParserSupportsListImport() -> None:
    """List import requires a source and defaults to preview."""

    args = main.cliBuildParser().parse_args(["list", "import", "-s", "a.txt"])

    assert args.action == "import"
    assert args.source == Path("a.txt")
    assert args.confirm is False


def testCliRunListImportWritesOnlyWhenConfirmed(tmp_path, monkeypatch) -> None:
    """list import previews by default and writes output/<name>.json on confirm."""

    monkeypatch.chdir(tmp_path)
    source = tmp_path / "weekly.txt"
    source.write_text("Milk\nBread\n")
    output = tmp_path / "output" / "weekly.json"

    assert main.cliRun(["list", "import", "-s", str(source)]) == 0
    assert not output.exists()
    assert main.cliRun(["list", "import", "-s", str(source), "--confirm"]) == 0
    assert [record["name"] for record in json.loads(output.read_text())] == [
        "Milk",
        "Bread",
    ]


def testCliRunListImportUsesOutputName(tmp_path, monkeypatch) -> None:
    """--output names the new list instead of the text file's name."""

    monkeypatch.chdir(tmp_path)
    source = tmp_path / "list.txt"
    source.write_text("Milk\n")

    assert main.cliRun(["list", "import", "-s", str(source), "-o", "party", "-y"]) == 0
    assert (tmp_path / "output" / "party.json").is_file()
    assert not (tmp_path / "output" / "list.json").exists()


def testCliBuildParserUiWithoutListMeansPicker() -> None:
    """--ui alone asks for the list picker rather than a default file."""

    args = main.cliBuildParser().parse_args(["--ui"])

    assert args.ui == ""
    assert args.object is None


def testCliRunUiWithoutListOpensPicker(monkeypatch) -> None:
    """--ui alone runs the app with no list, which shows the picker."""

    from organiseMyGroceries.ui import listApp

    ran: list[object] = []
    monkeypatch.setattr(listApp.ListApp, "run", lambda self: ran.append(self.listPath))

    assert main.cliRun(["--ui"]) == 0
    assert ran == [None]


def testCliRunUiResolvesListName(tmp_path, monkeypatch) -> None:
    """--ui weekly opens output/weekly.json."""

    from organiseMyGroceries.ui import listApp

    monkeypatch.chdir(tmp_path)
    (tmp_path / "output").mkdir()
    (tmp_path / "output" / "weekly.json").write_text('[{"name": "Milk"}]')
    ran: list[object] = []
    monkeypatch.setattr(listApp.ListApp, "run", lambda self: ran.append(self.listPath))

    assert main.cliRun(["--ui", "weekly"]) == 0
    assert ran == [Path("output/weekly.json")]


def testCliRunRequiresCommandOrUi() -> None:
    """With neither a command nor --ui the parser exits with an error."""

    with pytest.raises(SystemExit):
        main.cliRun([])
    with pytest.raises(SystemExit):
        main.cliRun(["--ui", "list.json", "list", "export"])


def testCliRunUiOpensAppOnList(tmp_path, monkeypatch) -> None:
    """--ui loads the named list and runs the terminal app."""

    from organiseMyGroceries.ui import listApp

    listPath = tmp_path / "list.json"
    listPath.write_text('[{"name": "Milk"}]')
    ran: list[Path] = []
    monkeypatch.setattr(listApp.ListApp, "run", lambda self: ran.append(self.listPath))

    assert main.cliRun(["--ui", str(listPath)]) == 0
    assert ran == [listPath]


def testCliRunUiReportsMissingList(tmp_path, capsys) -> None:
    """A missing list fails before the terminal is taken over."""

    status = main.cliRun(["--ui", str(tmp_path / "missing.json")])

    assert status == 1
    assert "does not exist" in capsys.readouterr().out
