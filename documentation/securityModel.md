# Security and privacy model

## Protected information

Shopping lists reveal personal purchasing information. Tesco credentials and
authenticated browser state are more sensitive and must never be stored by the
application.

## Controls

- Shopping-list filenames and `output/` are ignored by Git.
- Authentication occurs manually in the visible Tesco browser.
- Preview mode performs no browser or file-write side effects.
- Input paths and formats are validated before processing.
- Tests contain fictional grocery data and use temporary directories.
- Logs contain source paths, item counts, and individual search terms; users
  should protect their local application-state directory accordingly.

## Trust boundaries

Playwright and the Tesco website are external dependencies. Users remain
responsible for reviewing basket contents and confirming Tesco's current terms
before checkout. The project does not automate payment or order submission.
