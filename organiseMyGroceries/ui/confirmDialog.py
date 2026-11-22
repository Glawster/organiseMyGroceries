"""Modal yes/no confirmation for destructive or irreversible UI actions."""

from textual.app import ComposeResult
from textual.binding import Binding
from textual.containers import Horizontal, Vertical
from textual.screen import ModalScreen
from textual.widgets import Button, Label


class ConfirmDialog(ModalScreen[bool]):
    """Ask one question; dismiss with True for yes and False otherwise."""

    BINDINGS = [
        Binding("y", "answer(True)", "Yes"),
        Binding("n,escape", "answer(False)", "No"),
    ]

    def __init__(self, question: str) -> None:
        super().__init__()
        self.question = question

    def compose(self) -> ComposeResult:
        """The question and its two answers."""

        with Vertical(id="confirm-box", classes="surface"):
            yield Label(self.question)
            with Horizontal(classes="button-group"):
                yield Button("Yes", id="yes", variant="error")
                yield Button("No", id="no", variant="primary")

    def on_mount(self) -> None:
        """Default to the safe answer."""

        self.query_one("#no", Button).focus()

    def action_answer(self, answer: bool) -> None:
        """Close with the chosen answer."""

        self.dismiss(answer)

    def on_button_pressed(self, event: Button.Pressed) -> None:
        """Answer from the buttons."""

        self.dismiss(event.button.id == "yes")
