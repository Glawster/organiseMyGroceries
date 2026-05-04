# organiseMyGroceries

Safely turns a structured shopping list into Tesco basket actions. Preview mode
is the default; a browser opens only after explicit confirmation.

## Documentation

- [User guide](documentation/userGuide.md)
- [Architecture](documentation/architecture.md)
- [Security and privacy model](documentation/securityModel.md)
- [Testing process](documentation/testingProcess.md)
- [Repository layout](.github/repositoryLayout.md)
- [Requirements process](.github/requirementsManagement.md)
- [Release process](.github/howToRelease.md)

## Quick start

Conda is the preferred environment manager:

```bash
conda env create -f environment.yml
conda activate organiseMyGroceries
playwright install chromium
```

Preview a list without opening a browser:

```bash
python main.py add --source shoppingList.json
```

After reviewing the item count, open Tesco and add the items:

```bash
python main.py add --source shoppingList.json --confirm
```

Authentication remains a manual browser step. See the
[user guide](documentation/userGuide.md) for formats, export commands, and
failure behaviour.

## Development

The reusable implementation is in `src/organiseMyGroceries/`; `main.py` only
initialises logging and orchestrates the CLI. Run the complete local check with:

```bash
pytest
black --check main.py src tests
```

Project state and traceability are maintained under `project/` in accordance
with the [repository layout](.github/repositoryLayout.md).
