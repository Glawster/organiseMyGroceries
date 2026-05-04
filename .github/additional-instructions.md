# organiseMyGroceries project instructions

## Application boundary

- Keep `main.py` as the standalone application entry point.
- Put reusable grocery-list behaviour in `src/organiseMyGroceries/`.
- Keep browser automation isolated in `src/organiseMyGroceries/tesco.py`.
- Treat authentication as a manual user step; never persist Tesco credentials.

## Generated data

- Shopping lists may contain personal purchasing information and must not be
  committed.
- All converted and exported lists belong beneath the root `output/` directory.
- Tests must use fictional shopping-list data and `tmp_path`.
