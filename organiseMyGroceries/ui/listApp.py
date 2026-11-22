"""Textual application that edits JSON shopping lists."""

from pathlib import Path

from organiseMyProjects.logUtils import getLogger
from textual.app import App

from organiseMyGroceries.listDocument import listDocumentLoad
from organiseMyGroceries.listLibrary import LIST_DIRECTORY, listTouch
from organiseMyGroceries.ui.listScreen import ListScreen
from organiseMyGroceries.ui.pickerScreen import PickerScreen

logger = getLogger()

UI_DIRECTORY = Path(__file__).resolve().parent
# The shared OMP theme is deployed at the project root and owns all colour;
# the application stylesheet beside this module owns layout only.
THEME_PATH = UI_DIRECTORY.parents[1] / "myStyles.css"
LAYOUT_PATH = UI_DIRECTORY / "listApp.tcss"


class ListApp(App[None]):
    """Edit one named list, or choose from every list in a directory."""

    TITLE = "Shopping list"
    CSS_PATH = [THEME_PATH, LAYOUT_PATH]

    def __init__(
        self, listPath: Path | None = None, directory: Path = LIST_DIRECTORY
    ) -> None:
        # Fail before Textual takes over the terminal so errors stay readable.
        if not THEME_PATH.is_file():
            raise FileNotFoundError(f"shared TUI theme not found: '{THEME_PATH}'")
        self.listPath = listPath
        self.directory = directory
        self.records = listDocumentLoad(listPath) if listPath is not None else None
        super().__init__()

    def on_mount(self) -> None:
        """Show the named list, or the list picker when none was named."""

        if self.listPath is None or self.records is None:
            self.sub_title = str(self.directory)
            self.push_screen(PickerScreen(self.directory))
            return
        self.sub_title = str(self.listPath)
        listTouch(self.listPath)
        # With a single named list, closing it ends the application.
        self.push_screen(
            ListScreen(self.listPath, self.records), lambda _result: self.exit()
        )

    async def action_quit(self) -> None:
        """Route every quit request through the unsaved-changes check."""

        screen = self.screen
        if isinstance(screen, ListScreen):
            screen.action_close(quitApp=True)
        else:
            self.exit()
