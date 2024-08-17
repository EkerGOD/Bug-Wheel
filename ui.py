from textual.app import App, ComposeResult
from textual.widgets import Input, Footer, RichLog
from textual.binding import Binding
from textual import on
from base import System
import csv
import io
from rich.table import Table


class Application(App, System):
    def __init__(self):
        super().__init__()
        self.commandController = None

    def binding(self):
        self.commandController = self.systemStore.get('commandController')

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
        self.commandController.parse(message.value)
        # self.richLog.write(message.value)
        self.input.clear()

    def write(self, message: str, mode="text"):
        if mode == "text":
            self.richLog.write(message)
        elif mode == "table":
            rows = iter(csv.reader(io.StringIO(message)))
            table = Table(*next(rows))
            for row in rows:
                table.add_row(*row)
            self.richLog.write(table)
        else:
            self.richLog.write("RichLog未识别输出模式")



if __name__ == "__main__":
    app = Application()
    app.run()
