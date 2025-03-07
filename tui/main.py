from textual import on
from textual.app import App
from textual.screen import Screen
from textual.widgets import Header, Footer, Button, Input, Label
from textual.containers import VerticalGroup, HorizontalGroup, VerticalScroll, Container, Right, Middle
from textual.reactive import reactive
from wiring import TuiWiring


class InputBox(Input):
    def __init__(self, placeholder, id=None):
        super().__init__(placeholder=placeholder, id=id)


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
        self.input = InputBox("type here")

    def compose(self):
        yield self.channel
        yield self.messages
        yield self.input

    def on_input_submitted(self, event):
        self.messages.mount(Label(event.value))
        self.input.value = ""
        self.messages.scroll_end(animate=False)


class ChatRoom(Screen):
    def compose(self):
        self.message_group = MessageGroup()
        self.controls = Controls()
        yield HorizontalGroup(self.controls, self.message_group, id="main_group")
        yield Header()
        yield Footer()


class RoomList(Screen):
    def compose(self):
        self.room_list = VerticalScroll(id="room-list")
        self.back_button = Button(label="Back", variant="error")
        yield Header()
        yield Footer()
        yield self.room_list
        yield HorizontalGroup(self.back_button, InputBox("type here"), id="room-select-controls")


class RoomCreation(Screen): 
    def compose(self):
        self.label = Label("Name your room")
        self.input = InputBox("type here")
        yield VerticalGroup(self.label, self.input, id="room-creation")


class UsernameSelection(Screen):
    def compose(self):
        self.label = Label("Type your username")
        self.input = InputBox("type here")
        yield VerticalGroup(self.label, self.input, id="room-creation")

    @on(Input.Submitted)
    def handle_username_submission(self):
        try:
            self.app.tw.set_username(self.input.value)
            self.app.push_screen("room_list")
        except Exception as e:
            print(e)


class ServerConnect(Screen):
    def compose(self):
        self.ipinput = Right(InputBox("Server IP", id="ip-input"))
        self.portinput = Right(InputBox("Server Port", id="port-input"))
        self.ipgroup = HorizontalGroup(Label("Server IP"), self.ipinput, id="ip-group") 
        self.portgroup = HorizontalGroup(Label("Server Port"), self.portinput, id="port-group") 
        yield VerticalGroup(
            Label("Server Connect", id="server-connect-label"),
            self.ipgroup,
            self.portgroup,
            Right(Button(label="submit", id="server-submit")),
            id="server-group"
        )

    def on_button_pressed(self, event):
        try:
            ip = str(self.query_one("#ip-input").value)
            port = int(self.query_one("#port-input").value)
            print(ip, port)
            self.app.tw = TuiWiring(ip, port)
            self.app.push_screen("username_select")
        except:
            print("lolno bad connection")


class ChatApp(App):
    CSS_PATH = "chat.tcss"
    BINDINGS = [
        ("ctrl+d", "toggle_theme", "Toggle Theme"),
        ("ctrl+c", "quit", "quit"),
    ]
    SCREENS = {
        "server_connect": ServerConnect,
        "username_select": UsernameSelection,
        "room_list": RoomList,
    }

    def on_mount(self):
        self.push_screen("server_connect")

    def action_toggle_theme(self):
        self.theme = "textual-dark" if self.theme == "textual-light" else "textual-light" 


if __name__ == "__main__":
    app = ChatApp()
    app.run()

