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
    try:
        message = input(f'{my_username} > ')
        last_input = message
        message = message.encode('utf-8')
        message_header = f"{len(message):<{HEADER_LENGTH}}".encode('utf-8')
        client_socket.send(message_header + message)
        
        if message.decode('utf-8') == "CLOSE":
            return False
        return True
    except ConnectionError as e:
        print(f"Connection error: {e}")
        return False
    except Exception as e:
        print(f"Error sending message: {e}")
        return False

def receive_chatroom_messages():
    while True:
        try:
            username_header = client_socket.recv(HEADER_LENGTH)
            if not len(username_header):
                print('Connection closed by the server')
                closing = True
                return
            username_length = int(username_header.decode('utf-8').strip())
            username = client_socket.recv(username_length).decode('utf-8')
            if username == "CLOSING":
                print('Closing connection.')
                return 
            if username == "BACK":
                return
            message_header = client_socket.recv(HEADER_LENGTH)
            message_length = int(message_header.decode('utf-8').strip())
            message = client_socket.recv(message_length).decode('utf-8')
            print(f'{username} > {message}')
        except:
            return

def start_chatroom_loop():
    receiving_thread = threading.Thread(target=receive_chatroom_messages)
    receiving_thread.start()
    while True:
        if not send_message():
            return False
        if last_input == "BACK":
            receiving_thread.join()
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
    if server_message == "CLOSING":
        return False
    return True

def select_room(server_message):
    running = True
    while running:
        while server_message != "200":
            if not server_message or server_message == "CLOSING":
                print("Closing connection.")
                return False
            print("\n"+server_message) 
            if not send_message():
                return False
            server_message = receive_server_message()
            if last_input == "BACK":
                return True
        if last_input == "-1":
            if not create_room():
                return False
            if last_input == "BACK":
                server_message = receive_server_message()
                continue
        running = start_chatroom_loop()
        if running:
            server_message = receive_server_message()
    return False

def set_username():
    global my_username
    running = True
    while running:
        my_username = input("Username: ")
        username = my_username.encode('utf-8')
        username_header = f"{len(username):<{HEADER_LENGTH}}".encode('utf-8')
        client_socket.send(username_header + username)
        server_message = receive_server_message()
        if username.decode('utf-8') == "BACK":
            return True
        if server_message == "CLOSING": 
            return False
        running = select_room(server_message)

def connect_to_server():
    global client_socket
    running = True
    while running:
        client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        ip = input("Enter server IP address:")
        if ip == "CLOSE": return
        port = input("Enter server port:")
        if port == "CLOSE": return
        try:
            client_socket.connect((ip, int(port)))
        except Exception as e:
            print(e)
            print("Could not establish connection to server.")
            continue 
        running = set_username()

def main():
    print("Type \"CLOSE\" at any point to exit and \"BACK\" to go back")
    connect_to_server()
    sys.exit(0)

if __name__ == "__main__":
    main()
