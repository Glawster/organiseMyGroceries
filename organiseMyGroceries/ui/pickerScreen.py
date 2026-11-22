"""List picker: choose, create, rename, or remove shopping lists."""

from pathlib import Path

from organiseMyProjects.logUtils import getLogger
from textual.app import ComposeResult
from textual.binding import Binding
from textual.containers import Horizontal, Vertical
from textual.screen import Screen
from textual.widgets import Button, DataTable, Footer, Header, Static

from organiseMyGroceries.listDocument import listDocumentLoad
from organiseMyGroceries.listLibrary import (
    QUARANTINE_DIRECTORY_NAME,
    listCreate,
    listNameValidate,
    listQuarantine,
    listRename,
    listSummarise,
    listTouch,
)
from organiseMyGroceries.ui.confirmDialog import ConfirmDialog
from organiseMyGroceries.ui.listScreen import ListScreen
from organiseMyGroceries.ui.nameDialog import NameDialog

logger = getLogger()

COLUMNS = (
    ("name", "List"),
    ("items", "Items"),
    ("active", "Active"),
    ("lastUsed", "Last used"),
)
LAST_USED_FORMAT = "%a %d %b %Y %H:%M"
# Each button id is the name of the screen action it runs.
BUTTON_ACTIONS = frozenset({"open", "create", "rename", "remove", "close"})


class PickerScreen(Screen[None]):
    """Show the lists in one directory and open the chosen one."""

    BINDINGS = [
        Binding("o", "open", "Open"),
        Binding("n", "create", "New list"),
        Binding("r", "rename", "Rename"),
        Binding("d,delete", "remove", "Remove"),
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
                yield Button("Rename", id="rename")
                yield Button("Remove", id="remove")
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

        self.app.push_screen(NameDialog("New list", self._nameCheck), _nameChosen)

    def action_open(self) -> None:
        """Open the highlighted list."""

        name = self._cursorName(warn=True)
        if name is not None:
            self._listOpen(self.directory / f"{name}.json")

    def action_remove(self) -> None:
        """Move the highlighted list to quarantine after confirmation."""

        name = self._cursorName(warn=True)
        if name is None:
            return

        def _removeConfirmed(confirmed: bool | None) -> None:
            if not confirmed:
                return
            try:
                target = listQuarantine(name, self.directory)
            except (OSError, ValueError) as error:
                self.notify(str(error), title="Not removed", severity="error")
                return
            logger.value("quarantined list", target)
            self.tableRefresh()
            self.notify(
                f"'{name}' moved to {self.directory}/{QUARANTINE_DIRECTORY_NAME}/",
                title="Removed",
            )

        self.app.push_screen(
            ConfirmDialog(
                f"Remove '{name}'? It is moved to "
                f"{self.directory}/{QUARANTINE_DIRECTORY_NAME}/, not deleted."
            ),
            _removeConfirmed,
        )

    def action_rename(self) -> None:
        """Ask for a new name for the highlighted list."""

        name = self._cursorName(warn=True)
        if name is None:
            return

        def _renameCheck(newName: str) -> None:
            if newName != name:
                self._nameCheck(newName)

        def _nameChosen(newName: str | None) -> None:
            if newName is None or newName == name:
                return
            try:
                target = listRename(name, newName, self.directory)
            except (OSError, ValueError) as error:
                self.notify(str(error), title="Not renamed", severity="error")
                return
            logger.value("renamed list", target)
            self.tableRefresh(newName)

        self.app.push_screen(
            NameDialog("Rename list", _renameCheck, name, "Rename"), _nameChosen
        )

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
                summary.lastUsed.strftime(LAST_USED_FORMAT),
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

    def _cursorName(self, warn: bool = False) -> str | None:
        """Return the highlighted list's name, or None when there are none."""

        table = self.query_one("#lists", DataTable)
        if table.row_count == 0:
            if warn:
                self.notify("There are no lists yet", severity="warning")
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
        listTouch(path)
        logger.value("opened list", path)
        self.app.sub_title = str(path)
        self.app.push_screen(ListScreen(path, records), self._listClosed)

    def _nameCheck(self, name: str) -> None:
        """Reject a name that is malformed or already used by a list."""

        listNameValidate(name)
        if (self.directory / f"{name}.json").exists():
            raise ValueError(f"a list called '{name}' already exists")

    def _listClosed(self, _result: None) -> None:
        """Back at the picker after a list is closed."""

        self.app.sub_title = str(self.directory)
