"""Command-line entry point for organiseMyGroceries."""

import argparse
from pathlib import Path
from typing import Any, Sequence

from organiseMyProjects.logUtils import getLogger, setApplication

from organiseMyGroceries import __version__

# Keep the log directory stable regardless of whether the CLI is launched as
# the console script or as `python -m organiseMyGroceries`.
APPLICATION_NAME = "organisemygroceries"
DEFAULT_LIST_SOURCE = Path("shoppingList.json")

setApplication(APPLICATION_NAME)
logger = getLogger(includeConsole=False)

# Application modules are imported only after the logging context is ready.
from organiseMyGroceries.catalogue import catalogueImport
from organiseMyGroceries.shoppingList import listExport, listLoad
from organiseMyGroceries.tesco import basketAdd

## public workflow


def cliBuildParser() -> argparse.ArgumentParser:
    """Build the object/action command parser."""

    parser = argparse.ArgumentParser(
        prog="groceries",
        description="Manage a grocery catalogue and shopping lists",
    )
    parser.add_argument(
        "--version", action="version", version=f"%(prog)s {__version__}"
    )
    objects = parser.add_subparsers(dest="object", required=True)
    _parserAddCatalogue(objects)
    _parserAddList(objects)
    return parser


def cliRun(arguments: Sequence[str] | None = None) -> int:
    """Run the requested command and return a process exit status."""

    global logger

    args = cliBuildParser().parse_args(arguments)
    dryRun = not args.confirm
    logger = getLogger(includeConsole=True, dryRun=dryRun)
    logger.doing("starting")
    logger.value("object", args.object)
    logger.value("action", args.action)
    logger.value("source", args.source)
    logger.value("dryRun", dryRun)

    try:
        _commandDispatch(args, dryRun)
    except (OSError, ValueError) as error:
        logger.error(str(error))
        return 1

    logger.done("finished")
    return 0


def main() -> None:
    """Run the application and exit with its status code."""

    raise SystemExit(cliRun())


## commands


def _commandDispatch(args: argparse.Namespace, dryRun: bool) -> None:
    """Delegate one parsed object/action pair to domain code."""

    if args.object == "catalogue":
        catalogueImport(args.source, Path("output"), dryRun=dryRun)
        return
    if args.action == "export":
        listExport(args.source, Path("output"), dryRun=dryRun)
        return

    items = listLoad(args.source, Path("output"), dryRun=dryRun)
    logger.value("items found", len(items))
    if dryRun:
        logger.info("preview complete; confirmation opens the grocery store")
        return
    # Tesco is the current store adapter; list add stays store-neutral.
    basketAdd(items)


## options


def _optionConfirmAdd(parser: argparse.ArgumentParser, helpText: str) -> None:
    """Add the safe-by-default confirmation flag."""

    parser.add_argument(
        "-y",
        "--confirm",
        action="store_true",
        help=helpText,
    )


def _optionSourceAdd(
    parser: argparse.ArgumentParser,
    helpText: str,
    default: Path | None = None,
    required: bool = False,
) -> None:
    """Add a --source path option."""

    arguments: dict[str, object] = {
        "type": Path,
        "required": required,
        "help": helpText,
    }
    if default is not None:
        arguments["default"] = default
    parser.add_argument("-s", "--source", **arguments)


## parsers


def _parserAddCatalogue(subparsers: Any) -> None:
    """Add the catalogue object and its import action."""

    catalogueParser = subparsers.add_parser(
        "catalogue", help="manage the shared grocery catalogue"
    )
    actions = catalogueParser.add_subparsers(dest="action", required=True)
    importParser = actions.add_parser(
        "import", help="import a text grocery list into the catalogue"
    )
    _optionSourceAdd(
        importParser,
        "one-item-per-line grocery text file",
        required=True,
    )
    _optionConfirmAdd(
        importParser,
        "write output/catalogue.json (default is dry-run)",
    )


def _parserAddList(subparsers: Any) -> None:
    """Add the list object and its add/export actions."""

    listParser = subparsers.add_parser("list", help="work with a shopping list")
    actions = listParser.add_subparsers(dest="action", required=True)

    addParser = actions.add_parser("add", help="add active items to the grocery store")
    _optionSourceAdd(
        addParser,
        "JSON or text shopping-list path (default: shoppingList.json)",
        default=DEFAULT_LIST_SOURCE,
    )
    _optionConfirmAdd(
        addParser,
        "open the grocery store and execute changes (default is dry-run)",
    )

    exportParser = actions.add_parser("export", help="export active JSON items as text")
    _optionSourceAdd(
        exportParser,
        "JSON shopping-list path (default: shoppingList.json)",
        default=DEFAULT_LIST_SOURCE,
    )
    _optionConfirmAdd(
        exportParser,
        "write output/<source-name>.txt (default is dry-run)",
    )
