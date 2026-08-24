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
