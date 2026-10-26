"""Tests for shared grocery catalogue import, identity, and validation."""

import json
from pathlib import Path

import pytest

from organiseMyGroceries import catalogue

DATA_DIRECTORY = Path(__file__).resolve().parents[1] / "data" / "groceryCatalogue"


def _itemSample(
    name: str, itemId: str = "item-001", **overrides: object
) -> dict[str, object]:
    record = catalogue.itemBuild(itemId, name)
    record.update(overrides)
    return record


## conversion


def testCatalogueBuildAssignsStableIdentifiers() -> None:
    """A clean name list receives sequential zero-padded identifiers."""

    result = catalogue.catalogueBuild(
        ["Semi Skimmed Milk 2L", "Tesco Italian Roast & Ground Coffee"]
    )

    items = result.document["items"]
    assert result.document["version"] == 1
    assert [item["id"] for item in items] == ["item-001", "item-002"]
    assert items[0]["tescoSearch"] == "Semi Skimmed Milk 2L"
    assert "quantity" not in items[0]
    assert items[0]["active"] is True


def testCatalogueBuildNormalisesWhitespaceAndSkipsEmptyNames() -> None:
    """Surrounding and internal whitespace collapse; empty entries disappear."""

    result = catalogue.catalogueBuild(["  Apples  ", "\t", "Semi   Skimmed Milk 2L"])

    assert [item["name"] for item in result.document["items"]] == [
        "Apples",
        "Semi Skimmed Milk 2L",
    ]


def testCatalogueBuildIdentifiesSourceDuplicates() -> None:
    """Repeated source names are reported and stored once."""

    result = catalogue.catalogueBuild(["Apples", "Bananas", "APPLES", "Apples"])

    assert [item["name"] for item in result.document["items"]] == ["Apples", "Bananas"]
    assert result.duplicates == ("APPLES", "Apples")
    assert result.added == ("Apples", "Bananas")


def testCatalogueBuildPreservesExistingIdentifiersAndMetadata() -> None:
    """Re-importing known names keeps ids and does not overwrite enrichment."""

    existing = [_itemSample("Apples", category="fruit", notes="keep me")]

    result = catalogue.catalogueBuild(["Bananas", "Apples"], existing)

    items = result.document["items"]
    assert [item["id"] for item in items] == ["item-001", "item-002"]
    assert items[0]["category"] == "fruit"
    assert items[0]["notes"] == "keep me"
    assert items[1]["name"] == "Bananas"
    assert result.duplicates == ("Apples",)
    assert result.added == ("Bananas",)


def testCatalogueBuildAllocatesAfterHighestExistingIdentifier() -> None:
    """New items continue after the highest existing id rather than filling gaps."""

    existing = [_itemSample("Apples", "item-001"), _itemSample("Milk", "item-004")]

    result = catalogue.catalogueBuild(["Bread"], existing)

    assert [item["id"] for item in result.document["items"]] == [
        "item-001",
        "item-004",
        "item-005",
    ]


def testCatalogueBuildRejectsAmbiguousExistingNames() -> None:
    """Two existing items with the same identity fail instead of dropping one."""

    existing = [_itemSample("Apples", "item-001"), _itemSample("apples", "item-002")]

    with pytest.raises(ValueError, match="ambiguous catalogue name"):
        catalogue.catalogueBuild(["Bananas"], existing)


## import and load


def testCatalogueImportGoldenFixture(tmp_path: Path, monkeypatch) -> None:
    """Reviewed fictional groceries convert to the independently authored catalogue."""

    monkeypatch.chdir(tmp_path)
    source = tmp_path / "groceries.txt"
    source.write_text((DATA_DIRECTORY / "groceries.txt").read_text())
    expected = json.loads((DATA_DIRECTORY / "catalogue.json").read_text())

    output = catalogue.catalogueImport(source, Path("output"))
    document = catalogue.catalogueLoad(output)

    assert output == tmp_path / "output" / "catalogue.json"
    assert document == expected


def testCatalogueImportReRunPreservesStableIdentifiers(
    tmp_path: Path, monkeypatch
) -> None:
    """A second import of the same source must not rewrite existing ids."""

    monkeypatch.chdir(tmp_path)
    source = tmp_path / "groceries.txt"
    source.write_text("Apples\nBananas\n")

    first = catalogue.catalogueLoad(catalogue.catalogueImport(source, Path("output")))
    source.write_text("Bananas\nCarrots\nApples\n")
    second = catalogue.catalogueLoad(catalogue.catalogueImport(source, Path("output")))

    byName = {item["name"]: item["id"] for item in second["items"]}
    assert byName["Apples"] == "item-001"
    assert byName["Bananas"] == "item-002"
    assert byName["Carrots"] == "item-003"
    assert [item["id"] for item in first["items"]] == ["item-001", "item-002"]


def testCatalogueImportCleanRoomFromTextOnly(tmp_path: Path, monkeypatch) -> None:
    """A catalogue can be rebuilt from source text with no prior derived state."""

    monkeypatch.chdir(tmp_path)
    source = tmp_path / "groceries.txt"
    source.write_text("Apples\n\nMilk\n")

    document = catalogue.catalogueLoad(
        catalogue.catalogueImport(source, Path("output"))
    )

    assert [item["name"] for item in document["items"]] == ["Apples", "Milk"]
    assert all(item["id"].startswith("item-") for item in document["items"])


def testCatalogueImportHonoursDryRun(tmp_path: Path, monkeypatch) -> None:
    """Preview reports the destination without creating catalogue output."""

    monkeypatch.chdir(tmp_path)
    source = tmp_path / "groceries.txt"
    source.write_text("Apples\n")

    output = catalogue.catalogueImport(source, Path("output"), dryRun=True)

    assert output == tmp_path / "output" / "catalogue.json"
    assert not output.exists()


def testCatalogueImportRejectsOutputOutsideRoot(tmp_path: Path, monkeypatch) -> None:
    """Generated catalogues cannot escape the approved output directory."""

    monkeypatch.chdir(tmp_path)
    source = tmp_path / "groceries.txt"
    source.write_text("Apples\n")

    with pytest.raises(ValueError, match="output directory must be"):
        catalogue.catalogueImport(source, Path("elsewhere"))


def testCatalogueLoadRejectsMissingSource(tmp_path: Path, monkeypatch) -> None:
    """A missing catalogue path fails before any processing starts."""

    monkeypatch.chdir(tmp_path)

    with pytest.raises(ValueError, match="source file does not exist"):
        catalogue.catalogueLoad(Path("missing.json"))


@pytest.mark.parametrize(
    ("content", "message"),
    [
        ("not json", "invalid JSON"),
        ("[]", "must be a catalogue document"),
        ('{"items": []}', "must use catalogue version"),
        ('{"version": 1, "items": {}}', "must contain a catalogue item list"),
        ('{"version": 1, "items": ["Milk"]}', "item 1.*must be an object"),
    ],
)
def testCatalogueLoadRejectsMalformedDocuments(
    tmp_path: Path, monkeypatch, content: str, message: str
) -> None:
    """Malformed JSON and schema boundaries report their failing stage."""

    monkeypatch.chdir(tmp_path)
    source = tmp_path / "catalogue.json"
    source.write_text(content)

    with pytest.raises(ValueError, match=message):
        catalogue.catalogueLoad(source)


def testCatalogueLoadRejectsUserListFields(tmp_path: Path, monkeypatch) -> None:
    """Quantity and other user-list fields are not valid catalogue data."""

    monkeypatch.chdir(tmp_path)
    source = tmp_path / "catalogue.json"
    item = _itemSample("Apples", quantity=1)
    source.write_text(json.dumps({"version": 1, "items": [item]}))

    with pytest.raises(ValueError, match="must not store user-list fields: quantity"):
        catalogue.catalogueLoad(source)


def testCatalogueLoadRejectsDuplicateIdentifiers(tmp_path: Path, monkeypatch) -> None:
    """Two items may not share a stable identifier."""

    monkeypatch.chdir(tmp_path)
    source = tmp_path / "catalogue.json"
    items = [_itemSample("Apples", "item-001"), _itemSample("Bananas", "item-001")]
    source.write_text(json.dumps({"version": 1, "items": items}))

    with pytest.raises(ValueError, match="reuses identifier"):
        catalogue.catalogueLoad(source)


def testCatalogueLoadRejectsInvalidIdentifier(tmp_path: Path, monkeypatch) -> None:
    """Identifiers must use the item-N shape."""

    monkeypatch.chdir(tmp_path)
    source = tmp_path / "catalogue.json"
    source.write_text(
        json.dumps({"version": 1, "items": [_itemSample("Apples", "apple")]})
    )

    with pytest.raises(ValueError, match="invalid identifier"):
        catalogue.catalogueLoad(source)


def testCatalogueLoadRejectsMissingName(tmp_path: Path, monkeypatch) -> None:
    """A catalogue item without a usable name is invalid."""

    monkeypatch.chdir(tmp_path)
    source = tmp_path / "catalogue.json"
    source.write_text(json.dumps({"version": 1, "items": [_itemSample("   ")]}))

    with pytest.raises(ValueError, match="needs a name"):
        catalogue.catalogueLoad(source)


def testCatalogueLoadRejectsUnsupportedSuffix(tmp_path: Path, monkeypatch) -> None:
    """Existing files with unsupported formats fail validation."""

    monkeypatch.chdir(tmp_path)
    source = tmp_path / "catalogue.txt"
    source.write_text("Apples\n")

    with pytest.raises(ValueError, match="must use one of"):
        catalogue.catalogueLoad(source)


def testCatalogueImportRejectsUnsupportedSuffix(tmp_path: Path, monkeypatch) -> None:
    """Import accepts only a plain-text grocery list."""

    monkeypatch.chdir(tmp_path)
    source = tmp_path / "groceries.json"
    source.write_text("[]")

    with pytest.raises(ValueError, match="must use one of"):
        catalogue.catalogueImport(source, Path("output"))


def testCatalogueLoadRejectsUnsupportedField(tmp_path: Path, monkeypatch) -> None:
    """Unknown item keys are rejected so the schema stays explicit."""

    monkeypatch.chdir(tmp_path)
    source = tmp_path / "catalogue.json"
    source.write_text(
        json.dumps({"version": 1, "items": [_itemSample("Apples", colour="green")]})
    )

    with pytest.raises(ValueError, match="unsupported fields: colour"):
        catalogue.catalogueLoad(source)


def testCatalogueLoadRejectsNonStringName(tmp_path: Path, monkeypatch) -> None:
    """Display names must be strings."""

    monkeypatch.chdir(tmp_path)
    source = tmp_path / "catalogue.json"
    item = _itemSample("Apples")
    item["name"] = 3
    source.write_text(json.dumps({"version": 1, "items": [item]}))

    with pytest.raises(ValueError, match="field 'name' must be a string"):
        catalogue.catalogueLoad(source)


def testCatalogueImportRejectsCorruptExistingCatalogue(
    tmp_path: Path, monkeypatch
) -> None:
    """A corrupt destination catalogue fails instead of being overwritten silently."""

    monkeypatch.chdir(tmp_path)
    source = tmp_path / "groceries.txt"
    source.write_text("Apples\n")
    (tmp_path / "output").mkdir()
    (tmp_path / "output" / "catalogue.json").write_text("[]")

    with pytest.raises(ValueError, match="must be a catalogue document"):
        catalogue.catalogueImport(source, Path("output"))


def testCatalogueLoadRejectsMissingField(tmp_path: Path, monkeypatch) -> None:
    """Every documented catalogue field is required."""

    monkeypatch.chdir(tmp_path)
    source = tmp_path / "catalogue.json"
    item = _itemSample("Apples")
    del item["category"]
    source.write_text(json.dumps({"version": 1, "items": [item]}))

    with pytest.raises(ValueError, match="missing field 'category'"):
        catalogue.catalogueLoad(source)


def testCatalogueLoadRejectsNonBooleanActive(tmp_path: Path, monkeypatch) -> None:
    """Active must be a JSON boolean, not a truthy stand-in."""

    monkeypatch.chdir(tmp_path)
    source = tmp_path / "catalogue.json"
    source.write_text(
        json.dumps({"version": 1, "items": [_itemSample("Apples", active=1)]})
    )

    with pytest.raises(ValueError, match="field 'active' must be a bool"):
        catalogue.catalogueLoad(source)


def testIdAllocateUsesAtLeastThreeDigits() -> None:
    """New identifiers follow the documented item-001 shape."""

    assert catalogue.idAllocate([]) == "item-001"
    assert catalogue.idAllocate([_itemSample("Apples", "item-9")]) == "item-010"
