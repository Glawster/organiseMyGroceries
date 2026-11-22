"""Named shopping lists kept as JSON documents beneath lists/.

A list can be referred to by a short name such as ``weekly``, which means
``lists/weekly.json``, or by an explicit path. This module resolves names,
summarises the lists available to choose from, and creates, renames and
quarantines lists.

Lists are never deleted. Removing a list moves it into ``quarantine/`` inside
the list directory, where it is out of the way but can be restored by moving
the file back.
"""

import os
import re
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path

from organiseMyGroceries.files import LIST_DIRECTORY
from organiseMyGroceries.listDocument import listDocumentLoad, listDocumentSave

LIST_SUFFIXES = {".json", ".txt"}
NAME_PATTERN = re.compile(r"^[A-Za-z0-9][A-Za-z0-9_-]*$")
QUARANTINE_DIRECTORY_NAME = "quarantine"


@dataclass(frozen=True)
class ListSummary:
    """One list offered by the list picker."""

    name: str
    path: Path
    items: int
    active: int
    lastUsed: datetime


## public workflow


def listCreate(name: str, directory: Path = LIST_DIRECTORY) -> Path:
    """Create a new empty named list and return its path."""

    listNameValidate(name)
    target = directory / f"{name}.json"
    if target.exists():
        raise ValueError(f"a list called '{name}' already exists")
    directory.mkdir(parents=True, exist_ok=True)
    return listDocumentSave(target, [])


def listQuarantine(name: str, directory: Path = LIST_DIRECTORY) -> Path:
    """Move a list out of sight into quarantine/ and return its new path.

    The quarantined file is stamped with the time it was removed, so removing
    a later list with the same name never overwrites an earlier one.
    """

    source = _listExisting(name, directory)
    quarantine = directory / QUARANTINE_DIRECTORY_NAME
    quarantine.mkdir(exist_ok=True)
    stamp = datetime.now().strftime("%Y%m%d-%H%M%S")
    target = quarantine / f"{name}-{stamp}.json"
    counter = 1
    while target.exists():
        counter += 1
        target = quarantine / f"{name}-{stamp}-{counter}.json"
    source.rename(target)
    return target


def listTouch(path: Path) -> None:
    """Record that a list was used now: opened, saved, or sent.

    The file's modification time is the list's last-used time, so no extra
    metadata needs storing beside the items.
    """

    os.utime(path)


def listRename(name: str, newName: str, directory: Path = LIST_DIRECTORY) -> Path:
    """Give a list a new name and return its new path."""

    source = _listExisting(name, directory)
    listNameValidate(newName)
    target = directory / f"{newName}.json"
    if target.exists():
        raise ValueError(f"a list called '{newName}' already exists")
    source.rename(target)
    return target


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
        lastUsed = datetime.fromtimestamp(path.stat().st_mtime)
        summaries.append(ListSummary(path.stem, path, len(records), active, lastUsed))
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


## utilities


def _listExisting(name: str, directory: Path) -> Path:
    """Return the path of an existing named list or fail clearly."""

    listNameValidate(name)
    path = directory / f"{name}.json"
    if not path.is_file():
        raise ValueError(f"there is no list called '{name}'")
    return path
