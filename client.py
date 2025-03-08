import socket
import threading
import sys
import signal
from os import system, name

HEADER_LENGTH = 10
IP = "127.0.0.1"
PORT = 1234

running = True
my_username = None
last_input = None
client_socket = None

def take_input(my_username):
    global running
    global last_input
    while running:
        try:
            message = input(f'{my_username} > ')
            last_input = message
            if message and running:
                message = message.encode('utf-8')
                message_header = f"{len(message):<{HEADER_LENGTH}}".encode('utf-8')
                client_socket.send(message_header + message)
                if message.decode('utf-8') == "CLOSE":
                    running = False
                    return
        except:
            print("error while transmitting message")
            running = False
            return

def receive_messages():
    global running
    while running:
        try:
            username_header = client_socket.recv(HEADER_LENGTH)
            if not len(username_header):
                print('Connection closed by the server')
                running = False
                return
            username_length = int(username_header.decode('utf-8').strip())
            username = client_socket.recv(username_length).decode('utf-8')

            if username == "CLOSING" or username == "BACK":  # very professional, what could go wrong
                print('Closing connection.')
                running = False
                return

            message_header = client_socket.recv(HEADER_LENGTH)
            message_length = int(message_header.decode('utf-8').strip())
            message = client_socket.recv(message_length).decode('utf-8')

            print(f'{username} > {message}')
        except:
            if running:
                print("Lost connection to server")
            running = False
            return

def receive_server_message():
    message_header = client_socket.recv(HEADER_LENGTH)
    message_length = int(message_header.decode('utf-8').strip())
    server_message = client_socket.recv(message_length).decode('utf-8')
    return server_message

def handle_user_state():
    input_thread = threading.Thread(target=take_input, args=(my_username,))
    input_thread.daemon = True
    input_thread.start()
    server_message = receive_server_message()
    while server_message != "200":
        if server_message == "CLOSING":
            print("Closing connection.")
            sys.exit(0)
        print("\n"+server_message) 
        server_message = receive_server_message()
    if last_input == "-1":
        server_message = receive_server_message()
        print("\n"+server_message)

    receive_thread = threading.Thread(target=receive_messages)
    receive_thread.daemon = True
    receive_thread.start()

    
    input_thread.join()
    receive_thread.join()

def set_username():
    global my_username
    my_username = input("Username: ")
    if my_username == "CLOSE":
        return
    username = my_username.encode('utf-8')
    username_header = f"{len(username):<{HEADER_LENGTH}}".encode('utf-8')
    client_socket.send(username_header + username)
    handle_user_state()

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
    global running
    print("Type \"CLOSE\" at any point to exit")
    connect_to_server()

if __name__ == "__main__":
    main()
