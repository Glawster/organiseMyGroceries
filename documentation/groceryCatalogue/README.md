# Grocery catalogue

The catalogue is the shared master list of groceries that any user may select. It
is independent of an individual shopping list: it does not store who selected an
item, or in what quantity.

## Document format

Catalogue JSON is a versioned document, not a bare array. That distinguishes it
from a user shopping list and leaves room for later persistence changes.

```json
{
  "version": 1,
  "items": [
    {
      "id": "item-001",
      "name": "Apples",
      "tescoSearch": "Apples",
      "category": "",
      "preferredProduct": "",
      "notes": "",
      "active": true
    }
  ]
}
```

Each item must include exactly these fields:

| Field | Meaning |
| --- | --- |
| `id` | Stable identifier of the form `item-001`. |
| `name` | Display name. Meaningful product wording is preserved. |
| `tescoSearch` | Tesco search term; defaults to the display name on import. |
| `category` | Shared classification; empty until maintained. |
| `preferredProduct` | Shared preferred product wording; empty until maintained. |
| `notes` | Shared notes; empty until maintained. |
| `active` | Whether the item remains available for selection. |

User-list fields such as `quantity`, `unit`, `selected`, `profile`, and
`catalogueId` are rejected. Unknown fields are also rejected so the schema stays
explicit.

## Import

Convert a one-item-per-line text grocery list with:

```bash
organiseMyGroceries catalogue import --source groceries.txt
organiseMyGroceries catalogue import --source groceries.txt --confirm
```

Preview is the default and writes nothing. Confirmed import writes
`output/catalogue.json`. If that file already exists, new unique names are
appended and existing identifiers are left unchanged.

Import behaviour:

- Surrounding and internal whitespace is collapsed; empty lines are removed.
- Duplicate names are identified explicitly. Matching is case-insensitive after
  normalisation. The first identity is kept; later repeats are not stored again.
- An ambiguous match against two existing items is an error, not a silent drop.
- Re-running import does not rewrite existing identifiers or overwrite
  category, preferred product, notes, or active state.
- New identifiers continue after the highest existing `item-N` value and are not
  reused to fill gaps.

Real imported catalogues belong under `output/` and must not be committed.
Fictional reviewed examples live in `data/groceryCatalogue/`.

## Loading

`catalogueLoad` reads and validates a catalogue document without a UI. Invalid
JSON, the wrong document shape, duplicate identifiers, duplicate names, missing
fields, and user-list fields all fail with a clear error.
