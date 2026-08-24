# organiseMyGroceries

organiseMyGroceries is evolving from a local, safe-by-default Tesco shopping-list helper into a browser-accessible family grocery application. The planned product uses a shared grocery catalogue, independent per-user shopping lists, and reviewed Tesco UK search actions. Tesco authentication, payment, and checkout remain outside the application.

The existing CLI remains the current implemented application while requirements 002–007 deliver the multi-user web workflow.

## Documentation

- [User guide](documentation/userGuide.md)
- [Architecture](documentation/architecture.md)
- [Grocery catalogue](documentation/groceryCatalogue/README.md)
- [Security and privacy model](documentation/securityModel.md)
- [Testing process](documentation/testingProcess.md)
- [Current increment](project/currentIncrement.md)
- [Requirements and status](project/requirements/README.md)
- [ADR-001 — Web application architecture](project/adr/001-webApplicatinArchitecture.md)
- [ADR-002 — Grocery catalogue schema](project/adr/002-groceryCatalogueSchema.md)
- [Repository layout](.github/repositoryLayout.md)
- [Requirements process](.github/requirementsManagement.md)
- [Release process](.github/howToRelease.md)

## Current status

Requirements 001 (OMP alignment) and 002 (Grocery Catalogue) are complete. The
shared catalogue can be imported from a plain-text grocery list and loaded
without a UI. Requirement 003 (User Shopping Lists) is the next implementation
increment.

See [Current increment](project/currentIncrement.md) for the active scope and [Requirements and status](project/requirements/README.md) for the full backlog and agent prompts.

## Current CLI quick start

Conda is the preferred environment manager:

```bash
conda env create -f environment.yml
conda activate organiseMyGroceries
playwright install chromium
```

Preview a catalogue import without writing JSON:

```bash
python main.py catalogue import --source groceries.txt
```

Preview a list without opening a browser:

```bash
python main.py add --source shoppingList.json
```

After reviewing the item count, open Tesco and add the items:

```bash
python main.py add --source shoppingList.json --confirm
```

Authentication for the existing Playwright workflow remains a manual browser step. See the [user guide](documentation/userGuide.md) for formats, export commands, and failure behaviour.

## Development

The reusable implementation is in `src/organiseMyGroceries/`; `main.py` only initialises logging and orchestrates the CLI. Run the complete local check with:

```bash
pytest
black --check main.py src tests
```

Project state, architecture decisions, and traceability are maintained under `project/` in accordance with the [repository layout](.github/repositoryLayout.md).
