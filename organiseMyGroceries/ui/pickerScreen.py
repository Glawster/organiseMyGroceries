"""List picker: choose which shopping list to edit, or create a new one."""

from pathlib import Path

from organiseMyProjects.logUtils import getLogger
from textual.app import ComposeResult
from textual.binding import Binding
from textual.containers import Horizontal, Vertical
from textual.screen import Screen
from textual.widgets import Button, DataTable, Footer, Header, Static

from organiseMyGroceries.listDocument import listDocumentLoad
from organiseMyGroceries.listLibrary import (
    listCreate,
    listNameValidate,
    listSummarise,
)
from organiseMyGroceries.ui.listScreen import ListScreen
from organiseMyGroceries.ui.nameDialog import NameDialog

logger = getLogger()

COLUMNS = (("name", "List"), ("items", "Items"), ("active", "Active"))
# Each button id is the name of the screen action it runs.
BUTTON_ACTIONS = frozenset({"open", "create", "close"})


class PickerScreen(Screen[None]):
    """Show the lists in one directory and open the chosen one."""

    BINDINGS = [
        Binding("o", "open", "Open"),
        Binding("n", "create", "New list"),
        Binding("q", "close", "Quit"),
    ]

    def __init__(self, directory: Path) -> None:
        super().__init__()
        self.directory = directory

    ## layout

    def compose(self) -> ComposeResult:
        """Header, the list table with its buttons, status line, footer."""

        yield Header()
        with Vertical(id="content"):
            yield DataTable(id="lists", cursor_type="row")
            with Horizontal(classes="button-group"):
                yield Button("Open", id="open", variant="primary")
                yield Button("New list", id="create")
                yield Button("Quit", id="close")
        yield Static(id="status")
        yield Footer()

    def on_mount(self) -> None:
        """Fill the table once the widgets exist."""

        table = self.query_one("#lists", DataTable)
        for key, caption in COLUMNS:
            table.add_column(caption, key=key)
        self.tableRefresh()
        table.focus()

    def on_screen_resume(self) -> None:
        """Counts may have changed while a list was open."""

        self.tableRefresh(self._cursorName())

    ## actions

    def action_close(self) -> None:
        """Quit the application."""

        self.app.exit()

    def action_create(self) -> None:
        """Ask for a name, create an empty list, and open it."""

        def _nameCheck(name: str) -> None:
            listNameValidate(name)
            if (self.directory / f"{name}.json").exists():
                raise ValueError(f"a list called '{name}' already exists")

        def _nameChosen(name: str | None) -> None:
            if name is None:
                return
            try:
                path = listCreate(name, self.directory)
            except (OSError, ValueError) as error:
                self.notify(str(error), title="Not created", severity="error")
                return
            logger.value("created list", path)
            self._listOpen(path)

        self.app.push_screen(NameDialog("New list", _nameCheck), _nameChosen)

    def action_open(self) -> None:
        """Open the highlighted list."""

        name = self._cursorName()
        if name is None:
            self.notify("There are no lists yet", severity="warning")
            return
        self._listOpen(self.directory / f"{name}.json")

    ## events

    async def on_button_pressed(self, event: Button.Pressed) -> None:
        """Buttons run the same actions as their key bindings."""

        if event.button.id in BUTTON_ACTIONS:
            await self.run_action(event.button.id)

    def on_data_table_row_selected(self, _event: DataTable.RowSelected) -> None:
        """Enter on a row opens it."""

        self.action_open()

    ## utilities

    def tableRefresh(self, selectName: str | None = None) -> None:
        """Rebuild the table from the lists currently on disk."""

        table = self.query_one("#lists", DataTable)
        table.clear()
        summaries = listSummarise(self.directory)
        for summary in summaries:
            table.add_row(
                summary.name,
                str(summary.items),
                str(summary.active),
                key=summary.name,
            )
        if selectName is not None and selectName in table.rows:
            table.move_cursor(row=table.get_row_index(selectName))
        status = self.query_one("#status", Static)
        if summaries:
            status.update(f"{len(summaries)} lists in {self.directory}/")
        else:
            status.update(
                f"No lists in {self.directory}/ yet: press n to create one, "
                "or import a text list with 'groceries list import'"
            )

    def _cursorName(self) -> str | None:
        """Return the highlighted list's name, or None when there are none."""

        table = self.query_one("#lists", DataTable)
        if table.row_count == 0:
            return None
        rowKey, _columnKey = table.coordinate_to_cell_key(table.cursor_coordinate)
        return str(rowKey.value)

    def _listOpen(self, path: Path) -> None:
        """Load one list and show it; closing it comes back here."""

        try:
            records = listDocumentLoad(path)
        except (OSError, ValueError) as error:
            self.notify(str(error), title="Cannot open", severity="error")
            return
        logger.value("opened list", path)
        self.app.sub_title = str(path)
        self.app.push_screen(ListScreen(path, records), self._listClosed)

    def _listClosed(self, _result: None) -> None:
        """Back at the picker after a list is closed."""

        self.app.sub_title = str(self.directory)
