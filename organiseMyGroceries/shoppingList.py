"""Import, read, validate, and export shopping lists."""

import json
from pathlib import Path

from organiseMyProjects.logUtils import getLogger

from organiseMyGroceries.files import outputResolve, sourceValidate, textLinesRead
from organiseMyGroceries.listDocument import listDocumentSave, recordBuild
from organiseMyGroceries.listLibrary import listNameValidate

logger = getLogger()


## public workflow


def listExport(sourcePath: Path, outputDirectory: Path, dryRun: bool = False) -> Path:
    """Export active JSON shopping-list entries to a plain-text file."""

    source = sourceValidate(sourcePath, {".json"})
    items = _itemsRead(source)
    output = outputResolve(outputDirectory, source.stem, ".txt")

    logger.action("writing text shopping list")
    logger.value("output", output)
    if not dryRun:
        output.parent.mkdir(parents=True, exist_ok=True)
        output.write_text("\n".join(items) + ("\n" if items else ""))
        logger.done("writing text shopping list")
    return output


def listImport(
    sourcePath: Path,
    outputDirectory: Path,
    dryRun: bool = False,
    name: str | None = None,
) -> Path:
    """Import a plain-text shopping list into a new JSON list under output/.

    The list is named after the text file unless ``name`` is given. An
    existing JSON list is never overwritten because it may hold edits made in
    the terminal UI.
    """

    source = sourceValidate(sourcePath, {".txt"})
    listName = listNameValidate(name if name is not None else source.stem)
    output = outputResolve(outputDirectory, listName, ".json")
    if output.exists():
        raise ValueError(
            f"a list called '{listName}' already exists: edit it with "
            f"'groceries --ui {listName}', or import under another name with "
            "--output NAME"
        )
    lines = textLinesRead(source)
    records = [
        recordBuild(f"item-{index}", line) for index, line in enumerate(lines, start=1)
    ]

    logger.value("items imported", len(records))
    if not dryRun:
        output.parent.mkdir(parents=True, exist_ok=True)
    # Saving validates every record and writes atomically (dry-run aware).
    return listDocumentSave(output, records, dryRun=dryRun)


def listLoad(
    sourcePath: Path, outputDirectory: Path, dryRun: bool = False
) -> list[str]:
    """Load active search terms from a JSON or text shopping list."""

    source = sourceValidate(sourcePath, {".json", ".txt"})
    if source.suffix.lower() == ".txt":
        # Importing is a user-visible derived artifact, but loading does not
        # depend on writing it, so preview mode remains free of side effects.
        # An existing JSON list may contain UI edits, so it is left alone.
        output = outputResolve(outputDirectory, source.stem, ".json")
        if not dryRun and not output.exists():
            listImport(source, outputDirectory)
        return textLinesRead(source)
    return _itemsRead(source)


## records


def _itemsRead(sourcePath: Path) -> list[str]:
    """Parse and validate active search terms from JSON."""

    try:
        data = json.loads(sourcePath.read_text())
    except json.JSONDecodeError as error:
        raise ValueError(
            f"invalid JSON in source '{sourcePath}': {error.msg}"
        ) from error
    if not isinstance(data, list):
        raise ValueError(f"source '{sourcePath}' must contain a JSON list")

    items: list[str] = []
    for index, record in enumerate(data, start=1):
        if not isinstance(record, dict):
            raise ValueError(f"item {index} in '{sourcePath}' must be an object")
        if not record.get("active", True):
            continue
        term = record.get("tescoSearch") or record.get("name")
        if not isinstance(term, str) or not term.strip():
            raise ValueError(f"active item {index} in '{sourcePath}' needs a name")
        items.append(term.strip())
    return items
