# 003: User Shopping Lists

## Status

InProgress

## Objective

Allow each person to keep their own shopping list, created from a plain-text
list and maintained in a terminal user interface, while the shared grocery
catalogue remains available as common product data.

## Requirements

### List documents

* A shopping list is a JSON document: a list of item records with `id`,
  `name`, `tescoSearch`, `preferredProduct`, `quantity`, `unit`, `category`,
  `notes` and `active`.
* Each user has an independent list document; editing or saving one list must
  never modify another.
* Lists persist between sessions. JSON storage is acceptable initially, and the
  load/edit/save operations sit behind one domain module so storage can later
  move to SQLite without rewriting the UI.
* Loading tolerates hand-written lists: missing optional fields receive
  defaults, missing identifiers are allocated, and unknown keys are preserved.
* Saving validates every record and writes atomically.

### Import

* `groceries list import --source <list>.txt` creates
  `output/<list>.json` from a one-item-per-line text file.
* Import is a preview unless `--confirm` is given.
* Import never overwrites an existing JSON list, because it may contain edits.

### Terminal user interface

* `groceries --ui [<list>.json]` opens the list in a Textual terminal UI; the
  default list is `output/shoppingList.json`.
* The UI supports adding, editing, activating/deactivating and removing items,
  and saving the list.
* Removing an item and quitting with unsaved changes both ask for confirmation.
* Invalid input (for example an empty name or a quantity below 1) is rejected
  with a message and leaves the list unchanged.
* The UI uses the shared OMP theme `myStyles.css` for all colour, as described
  in `documentation/tuiStyling.md`; application stylesheets contain layout only.
* List rules live in the domain module; the UI only orchestrates them.

## Deferred: catalogue-linked lists

The original model, in which list entries reference shared catalogue items by
`catalogueId` with a per-user `selected` state, is deferred. It will be
revisited as a change to this requirement or as a new requirement before the
web application (004):

```json
{
  "profile": "exampleUser",
  "displayName": "Example User",
  "items": [
    {
      "catalogueId": "item-001",
      "selected": true,
      "quantity": 1,
      "notes": ""
    }
  ]
}
```

## Acceptance criteria

* A text list can be previewed and then imported into a JSON list under
  `output/`, and a second import cannot overwrite it.
* Two users' list documents can hold different items, and saving one does not
  modify the other.
* Items can be added, edited, deactivated, reactivated and removed in the
  terminal UI, and the changes survive save and reload.
* Removal and quitting with unsaved changes require confirmation.
* Invalid edits are rejected without changing the list.
* List loading, modification and saving are tested without a UI, and the UI is
  tested headlessly.

## Verification

* `pytest`, including `tests/test_listDocument.py` and `tests/test_listApp.py`
* `runLinter` and `runLinter --markup`
* `black --check organiseMyGroceries tests`
* `manageProject check`

## Change history

* 2026-11-22: name corrected to follow documentation/requirementsManagement.md.
* 2026-11-22: scope changed to imported JSON lists edited in a Textual terminal
  UI launched with `groceries --ui`; catalogue-linked lists deferred.
