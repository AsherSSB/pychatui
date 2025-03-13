from textual import on, work
from textual.app import App
from textual.screen import Screen
from textual.widgets import Header, Footer, Button, Input, Label, ListItem, ListView
from textual.containers import VerticalGroup, HorizontalGroup, VerticalScroll, Container, Right, Middle
from textual.reactive import reactive
from wiring import TuiWiring
import sys


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

    def on_button_pressed(self, event):
        if event.button.id == "back":
            self.app.go_back()
    

class MessagesBox(VerticalScroll):
    def __init__(self):
        super().__init__()
        self.receive_messages()

    def clear_messages(self):
        self.remove_children()
        self.refresh(layout=True)

    @work
    async def receive_messages(self):
        while True:
            try:
                username, message = await self.app.tw.receive_user_message()
                if username:
                    self.mount(Label(f"{username} >> {message}"))
                    self.scroll_end(animate=False)
            except:
                # disconnected
                break


class MessageGroup(VerticalGroup):
    def __init__(self):
        super().__init__(id="message-group")
        self.channel = Label("Room 1")
        self.input = InputBox("type here")
        self.messages = MessagesBox()

    def compose(self):
        yield self.channel
        yield self.messages
        yield self.input

    def on_input_submitted(self, event):
        self.messages.mount(Label(f"{self.app.username} >> {event.value}"))
        self.app.tw.send_message(event.value)
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
        self.back_button = Button(label="Back", variant="error", id="back")
        yield Header()
        yield ListView()
        yield self.back_button
        yield Footer()

    # this WILL be bugged if server changes rooms
    def on_show(self):
        server_message = self.app.tw.receive_server_message()
        index = server_message.find("\n")
        server_message = server_message[index+1:]        
        self.options = server_message.split("\n")
        self.options = self.options[:-1]  # removing empty string
        for i, option in enumerate(self.options):  # remove numbers
            index = option.find(" ")
            self.options[i] = option[index+1:]
        for option in self.options:
            self.query_one("ListView").mount(ListItem(Label(option)))

    def on_list_view_selected(self, event):
        choice = event.list_view.index - 1  # -1 since create new is -1
        self.app.tw.send_message(str(choice))
        if choice == -1:
            self.app.tw.receive_server_message() # clearing buffer of unneeded server message
            self.app.push_screen("room_creation")
        else:
            self.app.tw.receive_server_message()  # clear buffer
            self.app.push_screen("chat_room")

    def on_button_pressed(self, event):
        if event.button.id == "back":
            self.app.go_back()


class RoomCreation(Screen): 
    def compose(self):
        self.label = Label("Name your room")
        self.back_button = Button(label="Back", variant="error", id="creation-back")
        self.input = InputBox("type here")
        yield VerticalGroup(self.label, self.input, self.back_button, id="room-creation")

    def on_show(self):
        self.app.tw.receive_server_message()  # recieving room creation msg

    @on(Input.Submitted)
    def handle_input_sumbission(self):
        name = self.query_one("InputBox").value
        self.app.tw.send_message(name)
        self.app.pop_screen()
        self.app.push_screen("chat_room")

    def on_button_pressed(self, event):
        self.app.go_back()


class UsernameSelection(Screen):
    def compose(self):
        self.label = Label("Type your username")
        self.input = InputBox("type here")
        self.back_button = Button(label="Back", variant="error", id="user-back")
        yield VerticalGroup(self.label, self.input, self.back_button, id="room-creation")

    @on(Input.Submitted)
    def handle_username_submission(self):
        try:
            self.app.tw.set_username(self.input.value)
            self.app.username = self.input.value
            self.app.push_screen("room_list")
        except Exception as e:
            print (e)

    def on_button_pressed(self, event):
        self.app.go_back()
 

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
            self.app.connected = True
            self.app.tw = TuiWiring(ip, port)
            self.app.push_screen("username_select")
        except:
            print("bad connection")


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
        "room_creation": RoomCreation,
        "chat_room": ChatRoom,
    }


    def on_mount(self):
        self.push_screen("server_connect")
        self.connected = False

    def action_quit(self):
        if self.connected and self.tw in locals():
            self.tw.send_message("CLOSE")
        sys.exit(0)

    def action_toggle_theme(self):
        self.theme = "textual-dark" if self.theme == "textual-light" else "textual-light" 

    def go_back(self):
        if self.connected and self.tw:
            self.tw.send_message("BACK")
        self.pop_screen()


if __name__ == "__main__":
    app = ChatApp()
    app.run()

