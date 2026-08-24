# 002 — Grocery Catalogue

**Status:** ToDo

## Objective

Create a persistent master grocery catalogue from the existing plain-text grocery list.

The catalogue represents groceries that may be selected by any user. It must be independent of an individual user's current shopping list.

## Requirements

* Import the existing one-item-per-line text grocery list.
* Normalise whitespace and remove empty entries.
* Preserve meaningful product descriptions such as:

  * `Semi Skimmed Milk 2L`
  * `Tesco Italian Roast & Ground Coffee`
  * `Heinz No Added Sugar Cream of Tomato Soup`
* Assign every catalogue item a stable identifier.
* Store catalogue data in JSON initially.
* Support at least:

  * stable ID
  * display name
  * Tesco search term
  * category
  * preferred product
  * notes
  * active/inactive state
* Do not store user-specific selection or quantity information in the catalogue.
* Provide a repeatable import/conversion utility rather than requiring manual JSON construction.
* Import must not silently duplicate existing catalogue entries.

## Initial data model

```json
{
  "id": "item-001",
  "name": "Apples",
  "tescoSearch": "Apples",
  "category": "",
  "preferredProduct": "",
  "notes": "",
  "active": true
}
```

## Acceptance criteria

* The supplied grocery text file can be converted into valid catalogue JSON.
* Every non-empty source item appears exactly once unless explicitly identified as a duplicate.
* Every catalogue item has a stable identifier.
* Catalogue loading and validation can be tested without a UI.
* Re-running an import does not unexpectedly change existing stable identifiers.

## Dependencies and decisions

- [ADR-001 — Web application architecture](../../adr/001-webApplicationArchitecture.md)
- [ADR-002 — Grocery catalogue schema](../../adr/002-groceryCatalogueSchema.md)

## Verification

- `pytest`
- `black --check organiseMyGroceries tests`
- Clean-room text import into `output/catalogue.json` via
  `organiseMyGroceries catalogue import --source <file> --confirm`
- Re-import of the same source preserves existing identifiers
- Duplicate source names and invalid catalogue documents fail or report as
  specified

## Traceability

- Implementation: `organiseMyGroceries/catalogue.py`,
  `organiseMyGroceries/files.py`, `organiseMyGroceries/main.py`
- Tests: `tests/test_catalogue.py`, `tests/test_files.py`, `tests/test_main.py`
- Documentation: `documentation/groceryCatalogue/README.md`,
  `documentation/architecture.md`, `documentation/userGuide.md`
- Pull request: pending on `feature/002-grocery-catalogue`
- Agent runs: 2026-08-24 Grok implementation using
  `project/requirements/prompt/002-groceryCatalogue.md`

## Change history

- 2026-08-24: created from the planned catalogue increment.
- 2026-08-24: completed with catalogue import, stable identifiers, and tests.
- 2026-08-24: packaged CLI as `organiseMyGroceries <object> <action>`.
