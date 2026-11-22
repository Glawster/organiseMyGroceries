"""Modal form for adding or editing one shopping-list item."""

from typing import Any, Mapping

from textual.app import ComposeResult
from textual.binding import Binding
from textual.containers import Horizontal, Vertical, VerticalScroll
from textual.screen import ModalScreen
from textual.widgets import Button, Input, Label, Static

from organiseMyGroceries.listDocument import quantityParse

FIELDS = (
    ("name", "Item"),
    ("quantity", "Quantity"),
    ("unit", "Unit"),
    ("aisle", "Aisle"),
    ("tescoSearch", "Store search"),
    ("preferredProduct", "Preferred product"),
    ("notes", "Notes"),
)


class ItemDialog(ModalScreen[dict[str, Any] | None]):
    """Collect item fields; dismiss with the fields, or None when cancelled."""

    BINDINGS = [Binding("escape", "cancel", "Cancel")]

    def __init__(self, title: str, record: Mapping[str, Any] | None = None) -> None:
        super().__init__()
        self.formTitle = title
        self.record = dict(record or {"quantity": 1})

    ## layout

    def compose(self) -> ComposeResult:
        """Title, one row per field, an error line, and the buttons."""

        with Vertical(id="item-box", classes="surface"):
            yield Label(self.formTitle, classes="heading")
            with VerticalScroll(id="item-fields"):
                for field, caption in FIELDS:
                    with Horizontal(classes="field-row"):
                        yield Label(caption, classes="field-label")
                        yield Input(
                            str(self.record.get(field, "")), id=f"field-{field}"
                        )
            yield Static(id="item-error", classes="error")
            with Horizontal(classes="button-group"):
                yield Button("Save", id="save", variant="primary")
                yield Button("Cancel", id="cancel")

    def on_mount(self) -> None:
        """Start typing in the item name."""

        self.query_one("#field-name", Input).focus()

    ## actions

    def action_cancel(self) -> None:
        """Close without changes."""

        self.dismiss(None)

    ## events

    def on_button_pressed(self, event: Button.Pressed) -> None:
        """Save or cancel from the buttons."""

        if event.button.id == "save":
            self._formSubmit()
        else:
            self.dismiss(None)

    def on_input_submitted(self, _event: Input.Submitted) -> None:
        """Enter in any field saves the form."""

        self._formSubmit()

    ## utilities

    def _formSubmit(self) -> None:
        """Validate what the user typed and return it, or show why not."""

        values = {
            field: self.query_one(f"#field-{field}", Input).value.strip()
            for field, _caption in FIELDS
        }
        # The form keeps the user in place for simple mistakes; the domain
        # model validates the full record again when the edit is applied.
        if not values["name"]:
            self._errorShow("Item name is required")
            return
        try:
            values["quantity"] = quantityParse(values["quantity"] or "1")
        except ValueError as error:
            self._errorShow(str(error).capitalize())
            return
        self.dismiss(values)

    def _errorShow(self, message: str) -> None:
        """Display a validation message inside the form."""

        error = self.query_one("#item-error", Static)
        error.update(message)
        error.add_class("-visible")
