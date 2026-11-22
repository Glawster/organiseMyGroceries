"""Shopping-list JSON document model: load, validate, edit, and save records.

The document is a JSON list of item records. This module owns the record
schema and every edit operation so the terminal UI, the CLI, and tests share
one implementation and none of them needs a UI framework.
"""

import json
import os
import re
from pathlib import Path
from typing import Any, Mapping, Sequence

from organiseMyProjects.logUtils import getLogger

from organiseMyGroceries.files import sourceValidate

logger = getLogger()

ID_PATTERN = re.compile(r"^item-(\d+)$")
TEXT_FIELDS = (
    "name",
    "tescoSearch",
    "preferredProduct",
    "unit",
    "aisle",
    "notes",
)
# Lists written before aisles existed used "category"; it is read as the aisle.
LEGACY_AISLE_FIELD = "category"
EDITABLE_FIELDS = TEXT_FIELDS + ("quantity",)

## public workflow


def listDocumentLoad(sourcePath: Path) -> list[dict[str, Any]]:
    """Load a shopping-list JSON document and normalise every record.

    Hand-written lists may omit optional fields or identifiers; those are
    filled with defaults so the editor always works on complete records.
    Unknown keys are preserved so saving never discards user data.
    """

    source = sourceValidate(sourcePath, {".json"})
    try:
        data = json.loads(source.read_text())
    except json.JSONDecodeError as error:
        raise ValueError(
            f"invalid JSON in source '{sourcePath}': {error.msg}"
        ) from error
    if not isinstance(data, list):
        raise ValueError(f"source '{sourcePath}' must contain a JSON list")

    records = [
        _recordNormalise(record, index, str(sourcePath))
        for index, record in enumerate(data, start=1)
    ]
    # Identifiers are allocated only after every explicit id is known, so a
    # generated id can never collide with one that appears later in the file.
    for record in records:
        if not record["id"]:
            record["id"] = idAllocate(records)
    _idsCheckUnique(records, str(sourcePath))
    return records


def listDocumentSave(
    targetPath: Path, records: Sequence[Mapping[str, Any]], dryRun: bool = False
) -> Path:
    """Validate and atomically write a shopping-list JSON document."""

    target = targetPath.expanduser().resolve()
    if target.suffix.lower() != ".json":
        raise ValueError(f"target '{targetPath}' must be a .json file")
    # A preview may target a directory a confirmed run would create first.
    if not dryRun and not target.parent.is_dir():
        raise ValueError(f"target directory does not exist: '{target.parent}'")
    materialised = [dict(record) for record in records]
    for index, record in enumerate(materialised, start=1):
        _recordValidate(record, index, str(targetPath))
    _idsCheckUnique(materialised, str(targetPath))

    logger.action("writing shopping list")
    logger.value("output", target)
    if not dryRun:
        # Write beside the target and replace it in one step so an
        # interrupted save never leaves a truncated list behind.
        temporary = target.with_name(f".{target.name}.tmp")
        temporary.write_text(json.dumps(materialised, indent=2) + "\n")
        os.replace(temporary, target)
        logger.done("writing shopping list")
    return target


## identifiers


def idAllocate(records: Sequence[Mapping[str, Any]]) -> str:
    """Return the next unused item-N identifier."""

    highest = 0
    for record in records:
        match = ID_PATTERN.fullmatch(str(record.get("id", "")))
        if match:
            highest = max(highest, int(match.group(1)))
    return f"item-{highest + 1}"


## quantity


def quantityParse(text: str) -> int:
    """Parse a user-entered quantity as a whole number of at least one."""

    try:
        quantity = int(text.strip())
    except ValueError as error:
        raise ValueError("quantity must be a whole number") from error
    if quantity < 1:
        raise ValueError("quantity must be at least 1")
    return quantity


## records


def recordAdd(
    records: list[dict[str, Any]], fields: Mapping[str, Any]
) -> dict[str, Any]:
    """Append a new active record built from editable fields and return it."""

    record = recordBuild(idAllocate(records), str(fields.get("name", "")))
    _fieldsApply(record, fields)
    _recordValidate(record, len(records) + 1, "new item")
    records.append(record)
    return record


def recordBuild(itemId: str, name: str) -> dict[str, Any]:
    """Build one standard shopping-list record with default metadata."""

    return {
        "id": itemId,
        "name": name,
        "tescoSearch": name,
        "preferredProduct": "",
        "quantity": 1,
        "unit": "",
        "aisle": "",
        "notes": "",
        "active": True,
    }


def recordFind(records: Sequence[dict[str, Any]], itemId: str) -> dict[str, Any]:
    """Return the record with an identifier or fail clearly."""

    for record in records:
        if record["id"] == itemId:
            return record
    raise ValueError(f"no shopping-list item with id '{itemId}'")


def recordRemove(records: list[dict[str, Any]], itemId: str) -> dict[str, Any]:
    """Remove a record from the list and return it."""

    record = recordFind(records, itemId)
    records.remove(record)
    return record


def recordToggle(records: Sequence[dict[str, Any]], itemId: str) -> dict[str, Any]:
    """Flip a record between active and inactive and return it."""

    record = recordFind(records, itemId)
    record["active"] = not record["active"]
    return record


def recordUpdate(
    records: Sequence[dict[str, Any]], itemId: str, fields: Mapping[str, Any]
) -> dict[str, Any]:
    """Apply editable field changes to one record, all or nothing."""

    record = recordFind(records, itemId)
    # Validate a copy first so a rejected edit leaves the record untouched.
    candidate = dict(record)
    _fieldsApply(candidate, fields)
    _recordValidate(candidate, records.index(record) + 1, "edited item")
    record.update(candidate)
    return record


## sorting


def recordAisleKey(record: Mapping[str, Any]) -> tuple[Any, ...]:
    """Sort key that walks the shop: aisle order, then item name.

    Aisles are compared naturally, so "2" comes before "10", and items with no
    aisle come last.
    """

    aisle = str(record.get("aisle", "")).strip()
    parts = re.split(r"(\d+)", aisle.lower())
    natural = tuple(
        (0, int(part), "") if part.isdigit() else (1, 0, part) for part in parts if part
    )
    return (not aisle, natural, str(record.get("name", "")).lower())


## utilities


def _fieldsApply(record: dict[str, Any], fields: Mapping[str, Any]) -> None:
    """Copy editable fields onto a record, trimming text values."""

    unknown = sorted(set(fields) - set(EDITABLE_FIELDS))
    if unknown:
        raise ValueError(f"fields cannot be edited: {', '.join(unknown)}")
    for field, value in fields.items():
        record[field] = value.strip() if isinstance(value, str) else value
    # An empty store search falls back to the display name, matching the
    # search-term rule used when a list is sent to a store.
    if "tescoSearch" in fields and not record["tescoSearch"]:
        record["tescoSearch"] = record["name"]


def _idsCheckUnique(records: Sequence[Mapping[str, Any]], sourceLabel: str) -> None:
    """Fail when two records share an identifier."""

    seen: set[str] = set()
    for index, record in enumerate(records, start=1):
        if record["id"] in seen:
            raise ValueError(
                f"item {index} in '{sourceLabel}' reuses identifier '{record['id']}'"
            )
        seen.add(record["id"])


def _recordNormalise(record: Any, index: int, sourceLabel: str) -> dict[str, Any]:
    """Fill missing optional fields on a loaded record and validate it."""

    if not isinstance(record, dict):
        raise ValueError(f"item {index} in '{sourceLabel}' must be an object")
    defaults = recordBuild(str(record.get("id", "")), str(record.get("name", "")))
    normalised = {**defaults, **record}
    if LEGACY_AISLE_FIELD in normalised:
        legacy = normalised.pop(LEGACY_AISLE_FIELD)
        if not normalised["aisle"] and isinstance(legacy, str):
            normalised["aisle"] = legacy
    # Hand-written lists may number aisles; the editor treats them as text.
    aisle = normalised["aisle"]
    if isinstance(aisle, int) and not isinstance(aisle, bool):
        normalised["aisle"] = str(aisle)
    if not normalised.get("tescoSearch"):
        normalised["tescoSearch"] = normalised["name"]
    _recordValidate(normalised, index, sourceLabel, requireId=False)
    return normalised


def _recordValidate(
    record: Mapping[str, Any], index: int, sourceLabel: str, requireId: bool = True
) -> None:
    """Check record field types, name, quantity, and identifier shape."""

    for field in TEXT_FIELDS:
        if not isinstance(record.get(field), str):
            raise ValueError(
                f"item {index} in '{sourceLabel}' field '{field}' must be text"
            )
    if not record["name"].strip():
        raise ValueError(f"item {index} in '{sourceLabel}' needs a name")
    quantity = record.get("quantity")
    # bool is an int subclass, so reject it explicitly.
    if isinstance(quantity, bool) or not isinstance(quantity, int) or quantity < 1:
        raise ValueError(
            f"item {index} in '{sourceLabel}' quantity must be a whole number "
            "of at least 1"
        )
    if not isinstance(record.get("active"), bool):
        raise ValueError(
            f"item {index} in '{sourceLabel}' field 'active' must be true or false"
        )
    itemId = record.get("id")
    if requireId or itemId:
        if not isinstance(itemId, str) or not ID_PATTERN.fullmatch(itemId):
            raise ValueError(
                f"item {index} in '{sourceLabel}' has an invalid identifier "
                f"'{itemId}'"
            )
