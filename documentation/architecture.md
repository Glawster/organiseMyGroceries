# Architecture

## Responsibilities

`organiseMyGroceries.main` owns application logging, argument parsing, safe
preview behaviour, and process exit status. It is the packaged console script
and `python -m organiseMyGroceries` entry point.

Commands follow `application object action`:

```text
organiseMyGroceries catalogue import
organiseMyGroceries list import
organiseMyGroceries list send
organiseMyGroceries list export
organiseMyGroceries --ui [LIST]
```

`list send` is store-neutral. Tesco is the current store adapter.

```text
CLI input
  -> main.py orchestration
  -> catalogue.py shared catalogue import, identity, and validation
  -> shoppingList.py list import, send terms, and text export
  -> listDocument.py JSON list model: load, validate, edit, atomic save
  -> listLibrary.py named lists under lists/ (name resolution, summaries)
  -> ui/ Textual terminal UI: list picker and list editor (--ui only)
  -> tesco.py store adapter (confirmed list send only)
  -> grocery store website
```

`catalogue.py` and `shoppingList.py` have no Playwright or UI dependency and can
be tested using local files. Shared path validation lives in `files.py`.
`listDocument.py` owns every list edit rule and `listLibrary.py` resolves list
names, so the terminal UI in `ui/` only
orchestrates them. The UI loads the shared OMP theme `myStyles.css` for colour and
`ui/listApp.tcss` for layout, and imports Textual only when `--ui` is used.
`tesco.py` is the external-system adapter and is the only module that knows
browser selectors or manual login flow.

The grocery catalogue is shared product data. Shopping lists are currently
independent JSON documents; linking list entries to catalogue identifiers is
deferred (see requirement 003). See [Grocery catalogue](groceryCatalogue/groceryCatalogueIndex.md) for the JSON
document, identity, and import rules.

## Data boundaries

Source lists are user-owned inputs. Shopping lists (imported, created and
exported) are written only beneath the ignored root `lists/` directory, and other
derived files such as the catalogue beneath the ignored root `output/`. Fictional catalogue
fixtures used by tests live in `data/groceryCatalogue/`. Application logs are
managed by `organiseMyProjects.logUtils` beneath the user's local state
directory.

## Operational constraints

The Tesco website is an external interface and its selectors can change.
Authentication is deliberately manual. The automation chooses the first Add
button returned for a search; users should review their Tesco basket before
checkout.
