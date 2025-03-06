from textual.app import App
from textual.widgets import Header, Footer, Button, Input, Label
from textual.containers import VerticalGroup, HorizontalGroup, VerticalScroll, Container


class InputBox(Input):
    def __init__(self):
        super().__init__(placeholder="type here")


class Controls(VerticalGroup):
    def __init__(self):
        super().__init__(id="controls")
        self.user_list = VerticalGroup(id="user-list")
        self.back_button = Button(label="Back", variant="error", id="back")

    def compose(self):
        yield self.user_list
        yield self.back_button


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


class ChatRoom(Container):
    def compose(self):
        self.message_group = MessageGroup()
        self.controls = Controls()
        yield HorizontalGroup(self.controls, self.message_group, id="main_group")
        yield Header()
        yield Footer()


class RoomList(Container):
    def compose(self):
        self.room_list = VerticalScroll(id="room-list")
        self.back_button = Button(label="Back", variant="error")
        yield Header()
        yield Footer()
        yield self.room_list
        yield HorizontalGroup(self.back_button, InputBox(), id="room-select-controls")


class ChatApp(App):
    CSS_PATH = "chat.tcss"
    BINDINGS = [
        ("ctrl+d", "toggle_theme", "Toggle Theme"),
        ("ctrl+c", "quit", "quit"),
    ]
    state = "chatting"

    def compose(self):
        yield RoomList()

    def action_toggle_theme(self):
        self.theme = "textual-dark" if self.theme == "textual-light" else "textual-light" 


if __name__ == "__main__":
    app = ChatApp()
    app.run()
