from textual.app import App, ComposeResult
from textual.widgets import Button, Input


class PreventApp(App):
    """Demonstrates `prevent` context manager."""

    def compose(self) -> ComposeResult:
        yield Input()
        yield Button("Clear", id="clear")

    def on_button_pressed(self) -> None:
        """Clear the text input."""
        input = self.query_one(Input)
        with input.prevent(Input.Changed):
            input.value = ""

    def on_input_changed(self) -> None:
        """Called as the user types."""
        self.bell()


if __name__ == "__main__":
    app = PreventApp()
    app.run()