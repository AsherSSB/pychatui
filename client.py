import socket
import threading
import sys
import signal
from os import system, name

HEADER_LENGTH = 10
IP = "127.0.0.1"
PORT = 1234

my_username = None
last_input = None
client_socket = None
closing = False

def send_message():
    global last_input
    message = input(f'{my_username} > ')
    last_input = message
    message = message.encode('utf-8')
    message_header = f"{len(message):<{HEADER_LENGTH}}".encode('utf-8')
    try:
        client_socket.send(message_header + message)
    except:
        return False
    if message.decode('utf-8') == "CLOSE":
        return False
    return True

def receive_chatroom_messages():
    global closing
    while not closing:
        try:
            username_header = client_socket.recv(HEADER_LENGTH)
            if not len(username_header):
                print('Connection closed by the server')
                closing = True
                return
            username_length = int(username_header.decode('utf-8').strip())
            username = client_socket.recv(username_length).decode('utf-8')
            if username == "CLOSING":  # very professional, what could go wrong
                print('Closing connection.')
                closing = True
                return 
            if username == "BACK":
                return
            message_header = client_socket.recv(HEADER_LENGTH)
            message_length = int(message_header.decode('utf-8').strip())
            message = client_socket.recv(message_length).decode('utf-8')
            print(f'{username} > {message}')
        except:
            if not closing:
                print("Lost connection to server")
            closing == True
            return

def start_chatroom_loop():
    receiving_thread = threading.Thread(target=receive_chatroom_messages)
    receiving_thread.start()
    while True:
        if not send_message():
            return False
        if last_input == "BACK":
            return True

def receive_server_message():
    message_header = client_socket.recv(HEADER_LENGTH)
    message_length = int(message_header.decode('utf-8').strip())
    server_message = client_socket.recv(message_length).decode('utf-8')
    return server_message

def create_room():
    server_message = receive_server_message()
    print("\n"+server_message)
    if not send_message():
        return False
    return True

def select_room():
    while True:
        server_message = receive_server_message()
        while server_message != "200":
            if server_message == "CLOSING":
                print("Closing connection.")
                return
            print("\n"+server_message) 
            if not send_message():
                return False
            server_message = receive_server_message()
        if last_input == "-1":
            if not create_room():
                return False
            if last_input == "BACK":
                return True
        if not start_chatroom_loop():
            return False
        if last_input == "BACK":
            return True

def set_username():
    global my_username
    my_username = input("Username: ")
    if my_username == "CLOSE": 
        return False
    if my_username == "BACK":
        return True
    username = my_username.encode('utf-8')
    username_header = f"{len(username):<{HEADER_LENGTH}}".encode('utf-8')
    client_socket.send(username_header + username)
    select_room()

def connect_to_server():
    global client_socket
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    # TODO: allow user to enter server ip and port
    try:
        client_socket.connect((IP, PORT))
        set_username()
    except Exception as e:
        print(e)
        print("Could not establish connection to server.")
        return

def main():
    print("Type \"CLOSE\" at any point to exit")
    connect_to_server()
    sys.exit(0)

if __name__ == "__main__":
    main()
