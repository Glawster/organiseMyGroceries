# organiseMyGroceries project instructions

## Application boundary

- The packaged CLI entry point is `organiseMyGroceries` (`python -m organiseMyGroceries`).
- Keep `main.py` inside the `organiseMyGroceries/` package.
- Put reusable grocery-list behaviour in `organiseMyGroceries/`.
- Keep browser automation isolated in `organiseMyGroceries/tesco.py`.
- Keep the Textual terminal UI in `organiseMyGroceries/ui/`; it orchestrates
  `organiseMyGroceries/listDocument.py` and holds no list rules itself.
- The TUI loads the shared root `myStyles.css` for colour; `ui/*.tcss` files
  hold layout only.
- Treat `list send` as store-neutral; Tesco is the current store adapter.
- Treat authentication as a manual user step; never persist Tesco credentials.

## Release model

- Follow `documentation/howToRelease.md`: feature branches merge into the
  current release branch (`release/0.2`), not directly into `main`.
- Each feature branch takes its own alpha version in
  `organiseMyGroceries/version.py`, and its merge into the release branch is
  tagged, for example `v0.2a1`.

## Generated data

- Shopping lists may contain personal purchasing information and must not be
  committed.
- Shopping lists (imported, created and exported) belong beneath the root
  `lists/` directory; other generated files, such as the catalogue, belong
  beneath the root `output/` directory. Both are git-ignored.
- The application never deletes a shopping list: removing one moves it to
  `lists/quarantine/`.
- Tests must use fictional shopping-list data and `tmp_path`.
