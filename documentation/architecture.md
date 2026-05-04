# Architecture

## Responsibilities

`main.py` owns application logging, argument parsing, safe preview behaviour,
and process exit status. It delegates to two package modules:

```text
CLI input
  -> main.py orchestration
  -> shoppingList.py validation and transformation
  -> tesco.py browser boundary (confirmed add only)
  -> Tesco website
```

`shoppingList.py` has no Playwright dependency and can be tested using local
files. `tesco.py` is the external-system adapter and is the only module that
knows browser selectors or manual login flow.

## Data boundaries

Source lists are user-owned inputs. Derived JSON and text files are written
only beneath the ignored root `output/` directory. Application logs are managed
by `organiseMyProjects.logUtils` beneath the user's local state directory.

## Operational constraints

The Tesco website is an external interface and its selectors can change.
Authentication is deliberately manual. The automation chooses the first Add
button returned for a search; users should review their Tesco basket before
checkout.
