# organiseMyGroceries project instructions

## Application boundary

- The packaged CLI entry point is `organiseMyGroceries` (`python -m organiseMyGroceries`).
- Keep `main.py` inside the `organiseMyGroceries/` package.
- Put reusable grocery-list behaviour in `organiseMyGroceries/`.
- Keep browser automation isolated in `organiseMyGroceries/tesco.py`.
- Treat `list add` as store-neutral; Tesco is the current store adapter.
- Treat authentication as a manual user step; never persist Tesco credentials.

## Generated data

- Shopping lists may contain personal purchasing information and must not be
  committed.
- All converted and exported lists belong beneath the root `output/` directory.
- Tests must use fictional shopping-list data and `tmp_path`.
