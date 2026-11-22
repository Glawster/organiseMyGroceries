# User guide

## Command shape

Commands are `organiseMyGroceries <object> <action>`. Discover them with
`--help` at every level. Preview is the default; `-y` / `--confirm` executes.

```text
organiseMyGroceries catalogue import --source groceries.txt
organiseMyGroceries list import --source shoppingList.txt
organiseMyGroceries list send --source output/shoppingList.json
organiseMyGroceries list export --source output/shoppingList.json
organiseMyGroceries --ui
```

List commands default to `output/shoppingList.json`, the list created by
importing `shoppingList.txt`.

`list send` is store-neutral. Tesco is the current store adapter; other stores
may be added later without changing the command.

Equivalent entry points:

```bash
organiseMyGroceries --help
python -m organiseMyGroceries --help
```

## Shared grocery catalogue

The catalogue is the master list of groceries that may be selected later. It is
not a shopping list: it has no quantities or per-user selections.

Import a one-item-per-line text file. Preview is the default:

```bash
organiseMyGroceries catalogue import --source groceries.txt
organiseMyGroceries catalogue import --source groceries.txt --confirm
```

Confirmed import writes `output/catalogue.json`. Re-running import against that
file keeps existing identifiers and appends only new unique names. Duplicate
source lines are reported and stored once. Blank lines and extra whitespace are
ignored; product wording such as `Semi Skimmed Milk 2L` is preserved.

See [Grocery catalogue](groceryCatalogue/groceryCatalogueIndex.md) for the document fields.

## Import a list

Create a JSON shopping list from a one-item-per-line text file. Preview is the
default; confirming writes `output/<source-name>.json`:

```bash
organiseMyGroceries list import --source shoppingList.txt
organiseMyGroceries list import --source shoppingList.txt --confirm
```

Import never overwrites an existing JSON list, because it may contain edits
made in the terminal UI. Move the old list aside to import again.

## Edit a list in the terminal UI

Open the list in the terminal UI:

```bash
organiseMyGroceries --ui                          # output/shoppingList.json
organiseMyGroceries --ui output/weeklyShop.json   # another list
```

The table shows every item. Use the keys or the buttons beneath the table:

| Key | Action |
| --- | --- |
| `a` | Add an item |
| `e` or `Enter` | Edit the highlighted item |
| `space` | Switch the item between active and inactive |
| `d` or `Delete` | Remove the item (asks first) |
| `Ctrl+S` | Save the list |
| `q` | Quit (asks first if there are unsaved changes) |

The item form has the item name, quantity, unit, category, store search,
preferred product and notes. The name is required and the quantity must be a
whole number of at least 1. An empty store search uses the item name.

Changes are kept in memory until you save. Saving validates the whole list and
replaces the file in one step. Inactive items stay on the list but are not sent
to the store. Each person can keep their own list file; editing one never
changes another.

The UI uses the shared OMP terminal theme (`myStyles.css`).

## Shopping-list formats

`list send` accepts JSON and plain text. JSON is preferred because it can
disable items and provide store-specific search terms.

```json
[
  {
    "id": "item-135",
    "name": "Soda farl",
    "tescoSearch": "Soda farl",
    "quantity": 1,
    "active": true
  }
]
```

An item is included when `active` is absent or `true`. Its search term is
`tescoSearch` when non-empty and otherwise `name`. Each active item must resolve
to a non-empty string. A text list contains one item per line; blank lines and
surrounding whitespace are ignored.

## Send items to the store

Preview is safe and non-interactive. It validates and counts items but neither
opens a store nor creates output:

```bash
organiseMyGroceries list send --source shoppingList.json
organiseMyGroceries list send --source shoppingList.txt
```

Use `--confirm` to execute. The current store adapter opens Chromium at Tesco,
waits for manual login, searches each active term, and selects the first
available Add button.

```bash
organiseMyGroceries list send --source shoppingList.json --confirm
```

Confirmed text-list input is also imported to `output/<source-name>.json`
unless that list already exists. Generated files never overwrite the source.

## Export a list

Export active JSON entries to `output/<source-name>.txt`:

```bash
organiseMyGroceries list export --source shoppingList.json
organiseMyGroceries list export --source shoppingList.json --confirm
```

The first command previews the operation. Only the confirmed command writes the
file.

## Failures and recovery

Missing files, unsupported extensions, malformed JSON, non-list JSON roots, and
active records without a usable name produce a clear error and non-zero exit
status. Correct the source and rerun the command. Browser failures propagate;
the browser is still closed by the application.
