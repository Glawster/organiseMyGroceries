# User guide

## Command shape

Commands are `organiseMyGroceries <object> <action>`. Discover them with
`--help` at every level. Preview is the default; `-y` / `--confirm` executes.

```text
organiseMyGroceries catalogue import --source groceries.txt
organiseMyGroceries list import --source weekly.txt
organiseMyGroceries list send --source weekly
organiseMyGroceries list export --source weekly
organiseMyGroceries --ui
```

You can keep as many lists as you like. Each list is a JSON file in `lists/`,
and commands accept a list's name instead of its path: `weekly` means
`lists/weekly.json`. A value with a directory or a `.json`/`.txt` suffix is
used as a path. List names use letters, digits, `-` and `_`.

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
default. The list is named after the text file unless you give `--name`:

```bash
organiseMyGroceries list import --source weekly.txt              # preview
organiseMyGroceries list import --source weekly.txt --confirm    # lists/weekly.json
organiseMyGroceries list import --source list.txt --name party --confirm  # lists/party.json
```

Import never overwrites an existing list, because it may contain edits made in
the terminal UI. Edit the existing list instead, or import under another name
with `--name`.

## Edit a list in the terminal UI

Open the terminal UI without a list to choose one, or name the list to open it
directly:

```bash
organiseMyGroceries --ui           # choose from the lists in lists/
organiseMyGroceries --ui weekly    # open lists/weekly.json
```

### Choose a list

The list picker shows each list in `lists/` with its item and active counts and
when it was last used (opened, saved or sent). Other JSON files there are not
shown.

| Key | Action |
| --- | --- |
| `Enter` or `o` | Open the highlighted list |
| `n` | Create a new empty list and open it |
| `r` | Rename the highlighted list |
| `d` or `Delete` | Remove the highlighted list (asks first) |
| `q` | Quit |

Removing a list never deletes it. It is moved to `lists/quarantine/` with the
date and time added to its name, for example `weekly-20261122-143000.json`. To
bring it back, move it into `lists/` and give it a `.json` name that is not
already used.

Closing a list returns to the picker. A list named on the command line closes
straight back to the terminal.

### Edit the items

The table shows every item. Use the keys or the buttons beneath the table:

| Key | Action |
| --- | --- |
| `a` | Add an item |
| `e` or `Enter` | Edit the highlighted item |
| `space` | Switch the item between active and inactive |
| `s` | Sort by aisle, or back to the list's own order |
| `d` or `Delete` | Remove the item (asks first) |
| `Ctrl+S` | Save the list |
| `q` | Close the list (asks first if there are unsaved changes) |

The item form has the item name, quantity, unit, aisle, store search,
preferred product and notes. The name is required and the quantity must be a
whole number of at least 1. An empty store search uses the item name.

The aisle is free text such as `4` or `Bakery`. Sorting by aisle puts numbered
aisles in number order (`2` before `10`), then named aisles, then items with no
aisle, which helps you walk the shop in order. Sorting changes only the view;
the saved list keeps its own order. Lists saved before aisles existed show
their old category as the aisle.

Changes are kept in memory until you save. Saving validates the whole list and
replaces the file in one step. Inactive items stay on the list but are not sent
to the store. Each list is its own file; editing one never changes another.

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
organiseMyGroceries list send --source weekly
organiseMyGroceries list send --source weekly.txt
```

`list send` always needs `--source`, because sending changes a real store
basket and should never pick a list for you.

Use `--confirm` to execute. The current store adapter opens Chromium at Tesco,
waits for manual login, searches each active term, and selects the first
available Add button.

```bash
organiseMyGroceries list send --source weekly --confirm
```

Confirmed text-list input is also imported to `lists/<source-name>.json`
unless that list already exists. Generated files never overwrite the source.

## Export a list

Export active JSON entries to `lists/<list-name>.txt`:

```bash
organiseMyGroceries list export --source weekly
organiseMyGroceries list export --source weekly --confirm
```

The first command previews the operation. Only the confirmed command writes the
file.

## Failures and recovery

Missing files, unsupported extensions, malformed JSON, non-list JSON roots, and
active records without a usable name produce a clear error and non-zero exit
status. Correct the source and rerun the command. Browser failures propagate;
the browser is still closed by the application.
