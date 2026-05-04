"""Tests for command parsing and top-level orchestration."""

from pathlib import Path

import main


def testCliBuildParserSupportsAddCommand() -> None:
    """The add command exposes source and safe confirmation options."""

    args = main.cliBuildParser().parse_args(
        ["add", "--source", "items.json", "--confirm"]
    )

    assert args.action == "add"
    assert args.source == Path("items.json")
    assert args.confirm is True


def testCliBuildParserSupportsExportCommand() -> None:
    """The export command accepts an explicit source."""

    args = main.cliBuildParser().parse_args(["export", "items.json"])

    assert args.action == "export"
    assert args.source == Path("items.json")
    assert args.confirm is False


def testCliRunDryRunDoesNotOpenTesco(tmp_path, monkeypatch) -> None:
    """The default add workflow previews data without starting a browser."""

    source = tmp_path / "items.json"
    source.write_text('[{"name": "Milk"}]')
    opened = False

    def _basketAdd(_items):
        nonlocal opened
        opened = True

    monkeypatch.setattr(main, "basketAdd", _basketAdd)

    status = main.cliRun(["add", "--source", str(source)])

    assert status == 0
    assert opened is False


def testCliRunReturnsFailureForMissingSource(tmp_path) -> None:
    """Input validation failures become a non-zero CLI status."""

    status = main.cliRun(["add", "--source", str(tmp_path / "missing.json")])

    assert status == 1
