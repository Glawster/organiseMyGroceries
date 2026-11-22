"""Textual application that edits one JSON shopping list."""

from pathlib import Path

from organiseMyProjects.logUtils import getLogger
from textual.app import App

from organiseMyGroceries.listDocument import listDocumentLoad
from organiseMyGroceries.ui.listScreen import ListScreen

logger = getLogger()

UI_DIRECTORY = Path(__file__).resolve().parent
# The shared OMP theme is deployed at the project root and owns all colour;
# the application stylesheet beside this module owns layout only.
THEME_PATH = UI_DIRECTORY.parents[1] / "myStyles.css"
LAYOUT_PATH = UI_DIRECTORY / "listApp.tcss"


class ListApp(App[None]):
    """Load a shopping list, then hand editing to the list screen."""

    TITLE = "Shopping list"
    CSS_PATH = [THEME_PATH, LAYOUT_PATH]

    def __init__(self, listPath: Path) -> None:
        # Fail before Textual takes over the terminal so errors stay readable.
        if not THEME_PATH.is_file():
            raise FileNotFoundError(f"shared TUI theme not found: '{THEME_PATH}'")
        self.listPath = listPath
        self.records = listDocumentLoad(listPath)
        super().__init__()

    def on_mount(self) -> None:
        """Show the list editor."""

        self.sub_title = str(self.listPath)
        self.push_screen(ListScreen(self.listPath, self.records))

    async def action_quit(self) -> None:
        """Route every quit request through the unsaved-changes check."""

        screen = self.screen
        if isinstance(screen, ListScreen):
            screen.action_close()
        else:
            self.exit()
