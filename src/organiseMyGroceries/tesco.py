"""Tesco browser automation adapter."""

from collections.abc import Sequence

from organiseMyProjects.logUtils import getLogger
from playwright.sync_api import sync_playwright

logger = getLogger()


## basket


def basketAdd(items: Sequence[str]) -> None:
    """Open Tesco and add the first search result for each supplied item."""

    if not items:
        logger.info("shopping list has no active items")
        return

    # Login remains manual because authentication credentials must never be
    # stored by this project.
    with sync_playwright() as playwright:
        browser = playwright.chromium.launch(headless=False)
        try:
            page = browser.new_page()
            logger.doing("navigating to Tesco")
            page.goto("https://www.tesco.com/groceries/en-GB")
            input("Log in manually, then press Enter...")

            for item in items:
                logger.action("adding item")
                logger.value("item", item)
                page.fill('input[type="search"]', item)
                page.keyboard.press("Enter")
                page.wait_for_timeout(2000)
                buttons = page.locator('button:has-text("Add")')
                if buttons.count() == 0:
                    logger.warning("no add button found for item")
                    logger.value("item", item)
                    continue
                buttons.first.click()
                logger.done("adding item")

            input("Press Enter to close...")
        finally:
            browser.close()
