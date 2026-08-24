"""Shared grocery catalogue parsing, validation, and persistence."""

import json
import re
from pathlib import Path
from typing import Any, Mapping, NamedTuple, Sequence

from organiseMyProjects.logUtils import getLogger

from organiseMyGroceries.files import outputResolve, sourceValidate, textLinesRead

logger = getLogger()

CATALOGUE_VERSION = 1
CATALOGUE_STEM = "catalogue"
ITEM_FIELDS = (
    "id",
    "name",
    "tescoSearch",
    "category",
    "preferredProduct",
    "notes",
    "active",
)
FORBIDDEN_FIELDS = {
    "catalogueId",
    "profile",
    "quantity",
    "selected",
    "unit",
}
ID_PATTERN = re.compile(r"^item-(\d+)$")


class CatalogueBuildResult(NamedTuple):
    """Result of converting text names into a catalogue document."""

    document: dict[str, Any]
    added: tuple[str, ...]
    duplicates: tuple[str, ...]


## public workflow


def catalogueBuild(
    names: Sequence[str],
    existingItems: Sequence[Mapping[str, Any]] | None = None,
) -> CatalogueBuildResult:
    """Build a catalogue document from display names and existing items.

    Duplicate source names and names already in the catalogue are identified
    explicitly and omitted. Ambiguous matches against more than one existing
    item fail rather than being discarded.
    """

    existing = [dict(item) for item in existingItems or []]
    itemsValidate(existing, "existing catalogue")
    byKey = _itemsIndex(existing, "existing catalogue")
    addedItems: list[dict[str, Any]] = []
    addedNames: list[str] = []
    duplicates: list[str] = []
    seenSource: set[str] = set()

    for rawName in names:
        name = nameNormalise(rawName)
        if not name:
            continue
        key = nameKey(name)
        # Source-internal repeats and matches against the existing catalogue
        # are the same duplicate rule: keep the first identity, report the rest.
        if key in seenSource or key in byKey:
            duplicates.append(name)
            logger.info("identified duplicate catalogue item")
            logger.value("name", name)
            continue
        seenSource.add(key)
        item = itemBuild(idAllocate(existing + addedItems), name)
        addedItems.append(item)
        addedNames.append(name)
        byKey[key] = item

    return CatalogueBuildResult(
        document=documentBuild(existing + addedItems),
        added=tuple(addedNames),
        duplicates=tuple(duplicates),
    )


def catalogueImport(
    sourcePath: Path, outputDirectory: Path, dryRun: bool = False
) -> Path:
    """Import a plain-text grocery list into the shared catalogue JSON."""

    source = sourceValidate(sourcePath, {".txt"})
    output = outputResolve(outputDirectory, CATALOGUE_STEM, ".json")
    existing = _catalogueExisting(output)
    result = catalogueBuild(textLinesRead(source), existing)

    logger.action("writing grocery catalogue")
    logger.value("output", output)
    logger.value("catalogue items", len(result.document["items"]))
    logger.value("items added", len(result.added))
    if not dryRun:
        output.parent.mkdir(parents=True, exist_ok=True)
        output.write_text(json.dumps(result.document, indent=2) + "\n")
        logger.done("writing grocery catalogue")
    return output


def catalogueLoad(sourcePath: Path) -> dict[str, Any]:
    """Load and validate a catalogue JSON document."""

    source = sourceValidate(sourcePath, {".json"})
    return documentParse(source.read_text(), str(sourcePath))


## documents


def documentBuild(items: Sequence[Mapping[str, Any]]) -> dict[str, Any]:
    """Wrap validated catalogue items in the versioned document."""

    materialised = [dict(item) for item in items]
    itemsValidate(materialised, "catalogue")
    return {"version": CATALOGUE_VERSION, "items": materialised}


def documentParse(text: str, sourceLabel: str) -> dict[str, Any]:
    """Parse and validate catalogue JSON text."""

    try:
        data = json.loads(text)
    except json.JSONDecodeError as error:
        raise ValueError(
            f"invalid JSON in source '{sourceLabel}': {error.msg}"
        ) from error
    return documentValidate(data, sourceLabel)


def documentValidate(data: Any, sourceLabel: str) -> dict[str, Any]:
    """Validate a catalogue document mapping."""

    if not isinstance(data, dict):
        raise ValueError(f"source '{sourceLabel}' must be a catalogue document")
    if data.get("version") != CATALOGUE_VERSION:
        raise ValueError(
            f"source '{sourceLabel}' must use catalogue version {CATALOGUE_VERSION}"
        )
    items = data.get("items")
    if not isinstance(items, list):
        raise ValueError(f"source '{sourceLabel}' must contain a catalogue item list")
    itemsValidate(items, sourceLabel)
    return data


## identifiers


def idAllocate(items: Sequence[Mapping[str, Any]]) -> str:
    """Return the next unused item-N identifier without reusing a previous maximum."""

    highest = 0
    for item in items:
        match = ID_PATTERN.fullmatch(str(item.get("id", "")))
        if match:
            highest = max(highest, int(match.group(1)))
    return f"item-{highest + 1:03d}"


## items


def itemBuild(itemId: str, name: str) -> dict[str, Any]:
    """Build one catalogue item with empty shared metadata defaults."""

    return {
        "id": itemId,
        "name": name,
        "tescoSearch": name,
        "category": "",
        "preferredProduct": "",
        "notes": "",
        "active": True,
    }


def itemValidate(item: Any, index: int, sourceLabel: str) -> dict[str, Any]:
    """Validate one catalogue item and reject user-list fields."""

    if not isinstance(item, dict):
        raise ValueError(f"item {index} in '{sourceLabel}' must be an object")
    _itemFieldsCheck(item, index, sourceLabel)
    _itemValuesCheck(item, index, sourceLabel)
    return item


def itemsValidate(items: Sequence[Any], sourceLabel: str) -> list[dict[str, Any]]:
    """Validate catalogue items and require unique ids and names."""

    validated: list[dict[str, Any]] = []
    seenIds: set[str] = set()
    for index, item in enumerate(items, start=1):
        record = itemValidate(item, index, sourceLabel)
        if record["id"] in seenIds:
            raise ValueError(
                f"item {index} in '{sourceLabel}' reuses identifier '{record['id']}'"
            )
        seenIds.add(record["id"])
        validated.append(record)
    _itemsIndex(validated, sourceLabel)
    return validated


## names


def nameKey(name: str) -> str:
    """Return the case-insensitive identity key for duplicate detection."""

    return nameNormalise(name).casefold()


def nameNormalise(name: str) -> str:
    """Collapse surrounding and internal whitespace in a product name."""

    return " ".join(name.split())


## utilities


def _itemFieldsCheck(item: dict[str, Any], index: int, sourceLabel: str) -> None:
    """Reject forbidden, unexpected, or missing catalogue fields."""

    forbidden = sorted(set(item) & FORBIDDEN_FIELDS)
    if forbidden:
        names = ", ".join(forbidden)
        raise ValueError(
            f"item {index} in '{sourceLabel}' must not store user-list fields: {names}"
        )
    unexpected = sorted(set(item) - set(ITEM_FIELDS))
    if unexpected:
        names = ", ".join(unexpected)
        raise ValueError(
            f"item {index} in '{sourceLabel}' has unsupported fields: {names}"
        )
    for field in ITEM_FIELDS:
        if field not in item:
            raise ValueError(
                f"item {index} in '{sourceLabel}' is missing field '{field}'"
            )


def _itemValuesCheck(item: dict[str, Any], index: int, sourceLabel: str) -> None:
    """Check catalogue field types, identifier shape, and non-empty name."""

    for field in ITEM_FIELDS:
        if field == "active":
            continue
        if not isinstance(item[field], str):
            raise ValueError(
                f"item {index} in '{sourceLabel}' field '{field}' must be a string"
            )
    if not isinstance(item["active"], bool):
        raise ValueError(
            f"item {index} in '{sourceLabel}' field 'active' must be a bool"
        )
    if not ID_PATTERN.fullmatch(item["id"]):
        raise ValueError(
            f"item {index} in '{sourceLabel}' has an invalid identifier '{item['id']}'"
        )
    if not nameNormalise(item["name"]):
        raise ValueError(f"item {index} in '{sourceLabel}' needs a name")


def _catalogueExisting(output: Path) -> list[dict[str, Any]]:
    """Load an existing catalogue when the destination already exists."""

    if not output.is_file():
        return []
    return list(catalogueLoad(output)["items"])


def _itemsIndex(
    items: Sequence[Mapping[str, Any]], sourceLabel: str
) -> dict[str, Mapping[str, Any]]:
    """Index items by normalised name and fail on ambiguous collisions."""

    byKey: dict[str, Mapping[str, Any]] = {}
    for item in items:
        key = nameKey(str(item["name"]))
        if key in byKey:
            existing = byKey[key]
            raise ValueError(
                f"ambiguous catalogue name '{item['name']}' in '{sourceLabel}' "
                f"matches {existing['id']} and {item['id']}"
            )
        byKey[key] = item
    return byKey
