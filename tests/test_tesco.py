"""Boundary tests for Tesco browser orchestration."""

from unittest.mock import MagicMock

from organiseMyGroceries import tesco


def testBasketAddHandlesFoundAndMissingProducts(monkeypatch) -> None:
    """The adapter composes a real browser workflow and always closes it."""

    foundButtons = MagicMock()
    foundButtons.count.return_value = 1
    missingButtons = MagicMock()
    missingButtons.count.return_value = 0

    page = MagicMock()
    page.locator.side_effect = [foundButtons, missingButtons]
    browser = MagicMock()
    browser.new_page.return_value = page
    playwright = MagicMock()
    playwright.chromium.launch.return_value = browser
    context = MagicMock()
    context.__enter__.return_value = playwright

    monkeypatch.setattr(tesco, "sync_playwright", lambda: context)
    monkeypatch.setattr("builtins.input", lambda _prompt: "")

    tesco.basketAdd(["Milk", "Unfindable item"])

    assert [call.args[1] for call in page.fill.call_args_list] == [
        "Milk",
        "Unfindable item",
    ]
    foundButtons.first.click.assert_called_once_with()
    missingButtons.first.click.assert_not_called()
    browser.close.assert_called_once_with()


def testBasketAddSkipsBrowserForEmptyList(monkeypatch) -> None:
    """An empty list never crosses the external browser boundary."""

    opened = False

    def browserOpen():
        nonlocal opened
        opened = True

    monkeypatch.setattr(tesco, "sync_playwright", browserOpen)

    tesco.basketAdd([])

    assert opened is False
