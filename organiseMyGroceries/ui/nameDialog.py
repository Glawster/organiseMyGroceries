"""Modal prompt for the name of a new shopping list."""

from typing import Callable

from textual.app import ComposeResult
from textual.binding import Binding
from textual.containers import Horizontal, Vertical
from textual.screen import ModalScreen
from textual.widgets import Button, Input, Label, Static


class NameDialog(ModalScreen[str | None]):
    """Ask for a name; dismiss with it once ``check`` accepts it, or None."""

    BINDINGS = [Binding("escape", "cancel", "Cancel")]

    def __init__(self, title: str, check: Callable[[str], object]) -> None:
        super().__init__()
        self.formTitle = title
        # ``check`` raises ValueError with a message for an unusable name.
        self.check = check

    ## layout

    def compose(self) -> ComposeResult:
        """Title, the name field, an error line, and the buttons."""

        with Vertical(id="name-box", classes="surface"):
            yield Label(self.formTitle, classes="heading")
            yield Input(placeholder="for example weekly", id="list-name")
            yield Static(id="name-error", classes="error")
            with Horizontal(classes="button-group"):
                yield Button("Create", id="create", variant="primary")
                yield Button("Cancel", id="cancel")

    def on_mount(self) -> None:
        """Start typing straight away."""

        self.query_one("#list-name", Input).focus()

    ## actions

    def action_cancel(self) -> None:
        """Close without a name."""

        self.dismiss(None)

    ## events

    def on_button_pressed(self, event: Button.Pressed) -> None:
        """Create or cancel from the buttons."""

        if event.button.id == "create":
            self._nameSubmit()
        else:
            self.dismiss(None)

    def on_input_submitted(self, _event: Input.Submitted) -> None:
        """Enter submits the name."""

        self._nameSubmit()

    ## utilities

    def _nameSubmit(self) -> None:
        """Return the name if it is usable, otherwise explain why not."""

        name = self.query_one("#list-name", Input).value.strip()
        try:
            self.check(name)
        except ValueError as error:
            message = self.query_one("#name-error", Static)
            message.update(str(error)[:1].upper() + str(error)[1:])
            message.add_class("-visible")
            return
        self.dismiss(name)
