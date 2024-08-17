from textual.app import App, ComposeResult
from textual.widgets import Input, Footer, RichLog
from textual.binding import Binding
from textual import on


class Application(App):
    BINDINGS = [
        Binding(key="q", action="quit", description="Quit the app"),
        Binding(
            key="question_mark",
            action="help",
            description="Show help screen",
            key_display="?",
        ),
    ]

    def compose(self) -> ComposeResult:
        self.richLog = RichLog()
        self.input = Input(placeholder="Input command", type="text")
        yield self.richLog
        yield self.input
        yield Footer()

    def on_input_submitted(self, message: Input.Submitted):
        self.richLog.write(message.value)
        self.input.clear()


if __name__ == "__main__":
    app = Application()
    app.run()
