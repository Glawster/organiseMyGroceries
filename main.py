"""Command-line entry point for organiseMyGroceries."""

import argparse
import sys
from pathlib import Path
from typing import Any, Sequence

from organiseMyProjects.logUtils import getLogger, setApplication

thisApplication = Path(__file__).parent.name
setApplication(thisApplication)
logger = getLogger(includeConsole=False)

# Keep the root standalone entry point runnable before an editable install.
sys.path.insert(0, str(Path(__file__).parent / "src"))

# Application modules are imported only after the logging context is ready.
from organiseMyGroceries.catalogue import catalogueImport
from organiseMyGroceries.shoppingList import listExport, listLoad
from organiseMyGroceries.tesco import basketAdd

APPLICATION_VERSION = "0.1.0"
DEFAULT_SOURCE = Path("shoppingList.json")


## cli


def cliBuildParser() -> argparse.ArgumentParser:
    """Build the command-line parser."""

    parser = argparse.ArgumentParser(
        description="Manage a grocery catalogue and Tesco shopping lists"
    )
    parser.add_argument(
        "--version", action="version", version=f"%(prog)s {APPLICATION_VERSION}"
    )
    subparsers = parser.add_subparsers(dest="action", required=True)

    _catalogueParserAdd(subparsers)

    addParser = subparsers.add_parser("add", help="add active items to Tesco")
    addParser.add_argument(
        "-s",
        "--source",
        type=Path,
        default=DEFAULT_SOURCE,
        help="JSON or text shopping-list path (default: shoppingList.json)",
    )
    addParser.add_argument(
        "-y",
        "--confirm",
        action="store_true",
        help="open Tesco and execute changes (default is dry-run)",
    )

    exportParser = subparsers.add_parser(
        "export", help="export active JSON items as text"
    )
    exportParser.add_argument("source", type=Path, help="JSON shopping-list path")
    exportParser.add_argument(
        "-y",
        "--confirm",
        action="store_true",
        help="write output/<source-name>.txt (default is dry-run)",
    )
    return parser


def _catalogueParserAdd(subparsers: Any) -> None:
    """Add the catalogue object and its import action."""

    catalogueParser = subparsers.add_parser(
        "catalogue", help="manage the shared grocery catalogue"
    )
    catalogueSubparsers = catalogueParser.add_subparsers(
        dest="catalogueAction", required=True
    )
    importParser = catalogueSubparsers.add_parser(
        "import", help="import a text grocery list into the catalogue"
    )
    importParser.add_argument(
        "-s",
        "--source",
        type=Path,
        required=True,
        help="one-item-per-line grocery text file",
    )
    importParser.add_argument(
        "-y",
        "--confirm",
        action="store_true",
        help="write output/catalogue.json (default is dry-run)",
    )


def cliRun(arguments: Sequence[str] | None = None) -> int:
    """Run the requested command and return a process exit status."""

    global logger

    args = cliBuildParser().parse_args(arguments)
    dryRun = not args.confirm
    logger = getLogger(includeConsole=True, dryRun=dryRun)
    logger.doing("starting")
    logger.value("source", args.source)
    logger.value("dryRun", dryRun)

    try:
        if args.action == "export":
            listExport(args.source, Path("output"), dryRun=dryRun)
        elif args.action == "catalogue":
            catalogueImport(args.source, Path("output"), dryRun=dryRun)
        else:
            items = listLoad(args.source, Path("output"), dryRun=dryRun)
            logger.value("items found", len(items))
            if dryRun:
                logger.info("preview complete; confirmation opens tesco")
            else:
                basketAdd(items)
    except (OSError, ValueError) as error:
        logger.error(str(error))
        return 1

    logger.done("finished")
    return 0


## entry point


def main() -> None:
    """Run the application and exit with its status code."""

    raise SystemExit(cliRun())


if __name__ == "__main__":
    main()
