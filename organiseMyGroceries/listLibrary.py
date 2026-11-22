"""Named shopping lists kept as JSON documents beneath output/.

A list can be referred to by a short name such as ``weekly``, which means
``output/weekly.json``, or by an explicit path. This module resolves names,
summarises the lists available to choose from, and creates new empty lists.
"""

import re
from dataclasses import dataclass
from pathlib import Path

from organiseMyGroceries.listDocument import listDocumentLoad, listDocumentSave

LIST_DIRECTORY = Path("output")
LIST_SUFFIXES = {".json", ".txt"}
NAME_PATTERN = re.compile(r"^[A-Za-z0-9][A-Za-z0-9_-]*$")


@dataclass(frozen=True)
class ListSummary:
    """One list offered by the list picker."""

    name: str
    path: Path
    items: int
    active: int


## public workflow


def listCreate(name: str, directory: Path = LIST_DIRECTORY) -> Path:
    """Create a new empty named list and return its path."""

    listNameValidate(name)
    target = directory / f"{name}.json"
    if target.exists():
        raise ValueError(f"a list called '{name}' already exists")
    directory.mkdir(parents=True, exist_ok=True)
    return listDocumentSave(target, [])


def listPathResolve(reference: Path | str, directory: Path = LIST_DIRECTORY) -> Path:
    """Turn a list name or path into a path.

    A bare name with no directory and no .json/.txt suffix names a list under
    ``directory``; anything else is used as the path it already is.
    """

    path = Path(reference)
    if len(path.parts) == 1 and path.suffix.lower() not in LIST_SUFFIXES:
        return directory / f"{path.name}.json"
    return path


def listSummarise(directory: Path = LIST_DIRECTORY) -> list[ListSummary]:
    """Return every readable shopping list in a directory, sorted by name.

    Other JSON files kept beside the lists, such as the catalogue, are not
    shopping lists and are left out rather than reported as errors.
    """

    if not directory.is_dir():
        return []
    summaries: list[ListSummary] = []
    for path in sorted(directory.glob("*.json"), key=lambda each: each.stem.lower()):
        if path.name.startswith("."):
            continue
        try:
            records = listDocumentLoad(path)
        except (OSError, ValueError):
            continue
        active = sum(1 for record in records if record["active"])
        summaries.append(ListSummary(path.stem, path, len(records), active))
    return summaries


## names


def listNameValidate(name: str) -> str:
    """Accept a list name made of letters, digits, '-' and '_'."""

    if not NAME_PATTERN.fullmatch(name):
        raise ValueError(
            f"list name '{name}' must start with a letter or digit and use "
            "only letters, digits, '-' and '_'"
        )
    return name
