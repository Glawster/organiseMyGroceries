import argparse
import json
from pathlib import Path

from organiseMyProjects.logUtils import getLogger, setApplication

thisApplication = Path(__file__).parent.name
setApplication(thisApplication)
logger = getLogger(includeConsole=False)

from playwright.sync_api import sync_playwright


def exportToTxt(jsonPath, dryRun):

    path = Path(jsonPath)
    txtPath = path.with_suffix(".txt")
    with open(path) as f:
        data = json.load(f)

    lines = [
        item.get("tescoSearch") or item["name"]
        for item in data
        if item.get("active", True)
    ]
    logger.action("exporting to txt")
    logger.value("output", txtPath)
    if not dryRun:
        txtPath.write_text("\n".join(lines) + "\n")
        logger.done("exporting to txt")


def convertTxtToJson(txtPath):

    jsonPath = Path(txtPath).with_suffix(".json")
    lines = Path(txtPath).read_text().splitlines()
    data = [
        {
            "id": f"item-{i + 1}",
            "name": line.strip(),
            "tescoSearch": line.strip(),
            "preferredProduct": "",
            "quantity": 1,
            "unit": "",
            "category": "",
            "notes": "",
            "active": True,
        }
        for i, line in enumerate(lines)
        if line.strip()
    ]
    jsonPath.write_text(json.dumps(data, indent=2))
    logger.info("converted txt to json: %s", jsonPath)
    return jsonPath


def loadItems(filePath):

    path = Path(filePath)
    if path.suffix.lower() == ".txt":
        logger.doing("converting txt to json")
        path = convertTxtToJson(path)
        logger.done("converting txt to json")

    with open(path) as f:
        data = json.load(f)

    items = [
        item.get("tescoSearch") or item["name"]
        for item in data
        if item.get("active", True)
    ]
    return items


def addToTesco(items, dryRun):
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)
        page = browser.new_page()

        logger.doing("navigating to Tesco")
        page.goto("https://www.tesco.com/groceries/en-GB")

        input("Log in manually, then press Enter...")

        for item in items:
            logger.action("adding item")
            logger.info("item: %s", item)
            if not dryRun:
                page.fill('input[type="search"]', item)
                page.keyboard.press("Enter")
                page.wait_for_timeout(2000)

                buttons = page.locator('button:has-text("Add")')
                if buttons.count() > 0:
                    buttons.first.click()
                logger.done("adding item")

        if not dryRun:
            input("Press Enter to close...")
        browser.close()


def buildParser():
    parser = argparse.ArgumentParser(description="Add grocery items to Tesco basket")
    parser.add_argument(
        "-y",
        "--confirm",
        dest="confirm",
        action="store_true",
        help="execute changes (default is dry-run)",
    )
    parser.add_argument(
        "-e",
        "--export",
        dest="export",
        action="store_true",
        help="export active items from json to a txt file alongside the source",
    )
    parser.add_argument(
        "-s",
        "--source",
        dest="source",
        default="shoppingList.json",
        help="path to shopping list file (default: shopping.txt)",
    )
    return parser


def main():

    global logger

    parser = buildParser()
    args = parser.parse_args()
    dryRun = not args.confirm

    logger = getLogger(includeConsole=True, dryRun=dryRun)

    logger.doing("starting")
    logger.value("source", args.source)
    logger.value("dryRun", dryRun)

    if args.export:
        exportToTxt(args.source, dryRun)
        return

    items = loadItems(args.source)
    logger.value("items found", len(items))

    addToTesco(items, dryRun)

    logger.done("finished")


if __name__ == "__main__":
    main()
