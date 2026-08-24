# Architecture

## Responsibilities

`main.py` owns application logging, argument parsing, safe preview behaviour,
and process exit status. It delegates to package modules:

```text
CLI input
  -> main.py orchestration
  -> catalogue.py shared catalogue import, identity, and validation
  -> shoppingList.py user-list validation and transformation
  -> tesco.py browser boundary (confirmed add only)
  -> Tesco website
```

`catalogue.py` and `shoppingList.py` have no Playwright or UI dependency and can
be tested using local files. Shared path validation lives in `files.py`.
`tesco.py` is the external-system adapter and is the only module that knows
browser selectors or manual login flow.

The grocery catalogue is shared product data. User shopping lists will reference
stable catalogue identifiers rather than storing a second copy of product
definitions. See [Grocery catalogue](groceryCatalogue/README.md) for the JSON
document, identity, and import rules.

## Data boundaries

Source lists are user-owned inputs. Derived catalogues, JSON, and text files are
written only beneath the ignored root `output/` directory. Fictional catalogue
fixtures used by tests live in `data/groceryCatalogue/`. Application logs are
managed by `organiseMyProjects.logUtils` beneath the user's local state
directory.

## Operational constraints

The Tesco website is an external interface and its selectors can change.
Authentication is deliberately manual. The automation chooses the first Add
button returned for a search; users should review their Tesco basket before
checkout.
