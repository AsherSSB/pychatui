from textual.app import App
from textual.widgets import Header, Footer, Button, Input, Label
from textual.containers import VerticalGroup, HorizontalGroup, VerticalScroll


class InputBox(Input):
    def __init__(self):
        super().__init__(placeholder="type here")


class MessageGroup(VerticalGroup):
    def __init__(self):
        super().__init__(id="message-group")
        self.channel = Label("Room 1")
        self.messages = VerticalScroll()
        self.input = InputBox()

    def compose(self):
        yield self.channel
        yield self.messages
        yield self.input

    def on_input_submitted(self, event):
        self.messages.mount(Label(event.value))
        self.input.value = ""
        self.messages.scroll_end(animate=False)


class ChatApp(App):
    BINDINGS = [
                ("ctrl+d", "toggle_theme", "Toggle Theme"),
                ("ctrl+c", "quit", "quit"),
            ]

    def compose(self):
        self.message_group = MessageGroup()
        yield self.message_group
        yield Header()
        yield Footer()

    def action_toggle_theme(self):
        self.theme = "textual-dark" if self.theme == "textual-light" else "textual-light" 

if __name__ == "__main__":
    app = ChatApp()
    app.run()
