"""Main list-editing screen: the item table, actions, and status line."""

from pathlib import Path
from typing import Any

from organiseMyProjects.logUtils import getLogger
from textual.app import ComposeResult
from textual.binding import Binding
from textual.containers import Horizontal, Vertical
from textual.screen import Screen
from textual.widgets import Button, DataTable, Footer, Header, Static

from organiseMyGroceries.listDocument import (
    listDocumentSave,
    recordAdd,
    recordFind,
    recordRemove,
    recordToggle,
    recordUpdate,
)
from organiseMyGroceries.ui.confirmDialog import ConfirmDialog
from organiseMyGroceries.ui.itemDialog import ItemDialog

logger = getLogger()

COLUMNS = (
    ("name", "Item"),
    ("quantity", "Qty"),
    ("unit", "Unit"),
    ("category", "Category"),
    ("tescoSearch", "Store search"),
    ("notes", "Notes"),
    ("active", "Active"),
)
# Each button id is the name of the screen action it runs.
BUTTON_ACTIONS = frozenset({"add", "edit", "toggle", "remove", "save"})


class ListScreen(Screen[None]):
    """Show every item and apply edits to the in-memory list until saved."""

    BINDINGS = [
        Binding("a", "add", "Add"),
        Binding("e", "edit", "Edit"),
        Binding("space", "toggle", "Active"),
        Binding("d,delete", "remove", "Remove"),
        Binding("ctrl+s", "save", "Save"),
        Binding("q", "close", "Close"),
    ]

    def __init__(self, listPath: Path, records: list[dict[str, Any]]) -> None:
        super().__init__()
        self.listPath = listPath
        self.records = records
        self.unsaved = False

    ## layout

    def compose(self) -> ComposeResult:
        """Describe the screen: header, content, status line, footer."""

        yield Header()
        yield from self._createContent()
        yield Static(id="status")
        yield Footer()

    def on_mount(self) -> None:
        """Fill the table once the widgets exist."""

        table = self.query_one("#items", DataTable)
        for key, caption in COLUMNS:
            table.add_column(caption, key=key)
        self._tableRefresh()
        table.focus()

    def _createContent(self) -> ComposeResult:
        """The item table with its action buttons beneath it."""

        with Vertical(id="content"):
            yield DataTable(id="items", cursor_type="row", zebra_stripes=False)
            with Horizontal(classes="button-group"):
                yield Button("Add", id="add", variant="primary")
                yield Button("Edit", id="edit")
                yield Button("Active on/off", id="toggle")
                yield Button("Remove", id="remove")
                yield Button("Save", id="save")

    ## actions

    def action_close(self, quitApp: bool = False) -> None:
        """Close the list, asking first when there are unsaved changes.

        Closing returns to whatever opened the list (the list picker, or an
        exit when the list was named on the command line); ``quitApp`` leaves
        the application entirely.
        """

        def _leave() -> None:
            if quitApp:
                self.app.exit()
            else:
                self.dismiss()

        if not self.unsaved:
            _leave()
            return

        def _closeConfirmed(confirmed: bool | None) -> None:
            if confirmed:
                logger.info("discarded unsaved shopping-list changes")
                _leave()

        self.app.push_screen(
            ConfirmDialog("Discard unsaved changes and close?"), _closeConfirmed
        )

    def action_add(self) -> None:
        """Open an empty item form and append the result."""

        def _itemAdded(fields: dict[str, Any] | None) -> None:
            if fields is None:
                return
            record = self._editApply(lambda: recordAdd(self.records, fields))
            if record is not None:
                self._tableRefresh(record["id"])

        self.app.push_screen(ItemDialog("Add item"), _itemAdded)

    def action_edit(self) -> None:
        """Open the form for the highlighted item and apply the changes."""

        itemId = self._cursorItemId()
        if itemId is None:
            return

        def _itemEdited(fields: dict[str, Any] | None) -> None:
            if fields is None:
                return
            if self._editApply(lambda: recordUpdate(self.records, itemId, fields)):
                self._tableRefresh(itemId)

        record = recordFind(self.records, itemId)
        self.app.push_screen(ItemDialog("Edit item", record), _itemEdited)

    def action_remove(self) -> None:
        """Remove the highlighted item after confirmation."""

        itemId = self._cursorItemId()
        if itemId is None:
            return
        name = recordFind(self.records, itemId)["name"]

        def _removeConfirmed(confirmed: bool | None) -> None:
            if confirmed and self._editApply(
                lambda: recordRemove(self.records, itemId)
            ):
                self._tableRefresh()

        self.app.push_screen(
            ConfirmDialog(f"Remove '{name}' from the list?"), _removeConfirmed
        )

    def action_toggle(self) -> None:
        """Switch the highlighted item between active and inactive."""

        itemId = self._cursorItemId()
        if itemId is not None and self._editApply(
            lambda: recordToggle(self.records, itemId)
        ):
            self._tableRefresh(itemId)

    def action_save(self) -> None:
        """Write the list back to its JSON file."""

        try:
            listDocumentSave(self.listPath, self.records)
        except (OSError, ValueError) as error:
            logger.error(str(error))
            self.notify(str(error), title="Not saved", severity="error")
            return
        self.unsaved = False
        self._statusRefresh()
        self.notify(f"Saved {len(self.records)} items", title="Saved")

    ## events

    async def on_button_pressed(self, event: Button.Pressed) -> None:
        """Buttons run the same actions as their key bindings."""

        if event.button.id in BUTTON_ACTIONS:
            await self.run_action(event.button.id)

    def on_data_table_row_selected(self, _event: DataTable.RowSelected) -> None:
        """Enter on a row edits it."""

        self.action_edit()

    ## utilities

    def _cursorItemId(self) -> str | None:
        """Return the highlighted item's id, or None when the list is empty."""

        table = self.query_one("#items", DataTable)
        if table.row_count == 0:
            self.notify("The list is empty", severity="warning")
            return None
        rowKey, _columnKey = table.coordinate_to_cell_key(table.cursor_coordinate)
        return str(rowKey.value)

    def _editApply(self, edit: Any) -> Any:
        """Run one domain edit, reporting rejected input instead of crashing."""

        try:
            result = edit()
        except ValueError as error:
            self.notify(str(error), title="Not changed", severity="error")
            return None
        self.unsaved = True
        return result

    def _statusRefresh(self) -> None:
        """Show item counts and whether there are unsaved changes."""

        active = sum(1 for record in self.records if record["active"])
        state = "unsaved changes" if self.unsaved else "saved"
        self.query_one("#status", Static).update(
            f"{len(self.records)} items, {active} active · {state}"
        )

    def _tableRefresh(self, selectId: str | None = None) -> None:
        """Rebuild the table, keeping the cursor on a useful row."""

        table = self.query_one("#items", DataTable)
        previousRow = table.cursor_row
        table.clear()
        for record in self.records:
            table.add_row(
                *(_cellText(record, key) for key, _caption in COLUMNS),
                key=record["id"],
            )
        if selectId is not None:
            table.move_cursor(row=table.get_row_index(selectId))
        elif table.row_count:
            table.move_cursor(row=min(previousRow, table.row_count - 1))
        self._statusRefresh()


def _cellText(record: dict[str, Any], key: str) -> str:
    """Format one record field for display."""

    if key == "active":
        return "yes" if record["active"] else "no"
    return str(record[key])
