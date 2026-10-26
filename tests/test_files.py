"""Tests for shared source and output path validation."""

from pathlib import Path

import pytest

from organiseMyGroceries import files


def testSourceValidateResolvesExistingFile(tmp_path: Path) -> None:
    """A readable file with an allowed suffix is resolved."""

    source = tmp_path / "groceries.txt"
    source.write_text("Apples\n")

    assert files.sourceValidate(source, {".txt"}) == source.resolve()


def testTextLinesReadSkipsBlankLines(tmp_path: Path) -> None:
    """Blank lines are dropped and surrounding whitespace is stripped."""

    source = tmp_path / "groceries.txt"
    source.write_text(" Apples\n\nMilk \n")

    assert files.textLinesRead(source) == ["Apples", "Milk"]


def testOutputResolveRejectsNonOutputDirectory(tmp_path, monkeypatch) -> None:
    """Generated artifacts must stay under the project output directory."""

    monkeypatch.chdir(tmp_path)

    with pytest.raises(ValueError, match="output directory must be"):
        files.outputResolve(Path("elsewhere"), "catalogue", ".json")
