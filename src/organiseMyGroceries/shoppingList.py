"""Read, convert, validate, and export shopping lists."""

import json
from pathlib import Path
from typing import Any

from organiseMyProjects.logUtils import getLogger

logger = getLogger()


## public workflow


def listConvert(sourcePath: Path, outputDirectory: Path, dryRun: bool = False) -> Path:
    """Convert a plain-text shopping list to the standard JSON schema."""

    source = _sourceValidate(sourcePath, {".txt"})
    output = _outputResolve(outputDirectory, source.stem, ".json")
    lines = [line.strip() for line in source.read_text().splitlines() if line.strip()]
    records = [_recordBuild(index, line) for index, line in enumerate(lines, start=1)]

    logger.action("writing converted shopping list")
    logger.value("output", output)
    if not dryRun:
        output.parent.mkdir(parents=True, exist_ok=True)
        output.write_text(json.dumps(records, indent=2) + "\n")
        logger.done("writing converted shopping list")
    return output


def listExport(sourcePath: Path, outputDirectory: Path, dryRun: bool = False) -> Path:
    """Export active JSON shopping-list entries to a plain-text file."""

    source = _sourceValidate(sourcePath, {".json"})
    items = _itemsRead(source)
    output = _outputResolve(outputDirectory, source.stem, ".txt")

    logger.action("writing text shopping list")
    logger.value("output", output)
    if not dryRun:
        output.parent.mkdir(parents=True, exist_ok=True)
        output.write_text("\n".join(items) + ("\n" if items else ""))
        logger.done("writing text shopping list")
    return output


def listLoad(
    sourcePath: Path, outputDirectory: Path, dryRun: bool = False
) -> list[str]:
    """Load active search terms from a JSON or text shopping list."""

    source = _sourceValidate(sourcePath, {".json", ".txt"})
    if source.suffix.lower() == ".txt":
        # Conversion is a user-visible derived artifact, but loading does not
        # depend on writing it, so preview mode remains free of side effects.
        if not dryRun:
            listConvert(source, outputDirectory)
        return [
            line.strip() for line in source.read_text().splitlines() if line.strip()
        ]
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


def _recordBuild(index: int, name: str) -> dict[str, Any]:
    """Build one standard shopping-list record."""

    return {
        "id": f"item-{index}",
        "name": name,
        "tescoSearch": name,
        "preferredProduct": "",
        "quantity": 1,
        "unit": "",
        "category": "",
        "notes": "",
        "active": True,
    }


## paths


def _outputResolve(directory: Path, stem: str, suffix: str) -> Path:
    """Resolve a generated artifact beneath the project output directory."""

    outputRoot = Path("output").resolve()
    directoryPath = directory.resolve()
    if directoryPath != outputRoot:
        raise ValueError(f"output directory must be '{outputRoot}'")
    return directoryPath / f"{stem}{suffix}"


def _sourceValidate(sourcePath: Path, suffixes: set[str]) -> Path:
    """Validate and resolve a user-provided source file."""

    source = sourcePath.expanduser().resolve()
    if not source.is_file():
        raise ValueError(f"source file does not exist: '{sourcePath}'")
    if source.suffix.lower() not in suffixes:
        expected = ", ".join(sorted(suffixes))
        raise ValueError(f"source '{sourcePath}' must use one of: {expected}")
    return source
