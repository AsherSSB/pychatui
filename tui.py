from textual.app import App
from textual.widgets import Header, Footer, Button, Input, Label
from textual.containers import VerticalGroup, HorizontalGroup, VerticalScroll, Container
import socket
import threading
import sys
import signal
from os import system, name

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


class RoomCreation(Container): 
    def compose(self):
        self.label = Label("Name your room")
        self.input = InputBox()
        yield VerticalGroup(self.label, self.input, id="room-creation")

class ChatApp(App):
    CSS_PATH = "chat.tcss"
    BINDINGS = [
        ("ctrl+d", "toggle_theme", "Toggle Theme"),
        ("ctrl+c", "quit", "quit"),
    ]
    state = "chatting"

    def compose(self):
        yield RoomCreation()

    def action_toggle_theme(self):
        self.theme = "textual-dark" if self.theme == "textual-light" else "textual-light" 


if __name__ == "__main__":
    app = ChatApp()
    app.run()

#HEADER_LENGTH = 10
#IP = "127.0.0.1"
#PORT = 1234
#
#running = True
#

#def take_input(client_socket, my_username):
#    global running
#    global last_input
#    while running:
#        try:
#            message = input(f'{my_username} > ')
#            last_input = message
#            if message and running:
#                message = message.encode('utf-8')
#                message_header = f"{len(message):<{HEADER_LENGTH}}".encode('utf-8')
#                client_socket.send(message_header + message)
#                if message.decode('utf-8') == "CLOSE":
#                    running = False
#                    return
#        except:
#            print("error while transmitting message")
#            running = False
#            return
#
#def receive_messages(client_socket):
#    global running
#    while running:
#        try:
#            username_header = client_socket.recv(HEADER_LENGTH)
#            if not len(username_header):
#                print('Connection closed by the server')
#                running = False
#                return
#            username_length = int(username_header.decode('utf-8').strip())
#            username = client_socket.recv(username_length).decode('utf-8')
#
#            if username == "CLOSING":  # very professional, what could go wrong
#                print('Closing connection.')
#                running = False
#                return
#
#            message_header = client_socket.recv(HEADER_LENGTH)
#            message_length = int(message_header.decode('utf-8').strip())
#            message = client_socket.recv(message_length).decode('utf-8')
#
#            print(f'{username} > {message}')
#        except:
#            if running:
#                print("Lost connection to server")
#            running = False
#            return
#
#def receive_server_message(client_socket):
#    message_header = client_socket.recv(HEADER_LENGTH)
#    message_length = int(message_header.decode('utf-8').strip())
#    server_message = client_socket.recv(message_length).decode('utf-8')
#    return server_message
#
#def handle_user_state(client_socket):
#    input_thread = threading.Thread(target=take_input, args=(client_socket, my_username))
#    input_thread.daemon = True
#    input_thread.start()
#    server_message = receive_server_message(client_socket)
#    # around here using CLOSE causes hang
#    while server_message != "200":
#        if server_message == "CLOSING":
#            print("Closing connection.")
#            sys.exit(0)
#        print("\n"+server_message) 
#        server_message = receive_server_message(client_socket)
#    if last_input == "-1":
#        server_message = receive_server_message(client_socket)
#        print("\n"+server_message)
#
#    receive_thread = threading.Thread(target=receive_messages, args=(client_socket,))
#    receive_thread.daemon = True
#    receive_thread.start()
#
#    while running:
#        input_thread.join(0.1)
#        receive_thread.join(0.1)
#
#def main():
#    global my_username, running
#    print("Type \"CLOSE\" at any point to exit")
#    my_username = input("Username: ")
#    if my_username == "CLOSE":
#        sys.exit(0)
#
#    # TODO: allow user to enter server ip and port
#    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
#    try:
#        client_socket.connect((IP, PORT))
#    except:
#        print("Could not establish connection to server.")
#        sys.exit(0)
#    
#    username = my_username.encode('utf-8')
#    username_header = f"{len(username):<{HEADER_LENGTH}}".encode('utf-8')
#    client_socket.send(username_header + username)
#
#    handle_user_state(client_socket)
#
#if __name__ == "__main__":
#    main()
