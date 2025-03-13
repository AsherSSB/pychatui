import socket
import asyncio

HEADER_LENGTH = 10

class TuiWiring():
    def __init__(self, ip, port):
        self.client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.client_socket.connect((ip, port))
        self.username:str

    def set_username(self, username):
        self.username = username
        username = username.encode('utf-8')
        username_header = f"{len(username):<{HEADER_LENGTH}}".encode('utf-8')
        self.client_socket.send(username_header + username)

    def receive_server_message(self):
        message_header = self.client_socket.recv(HEADER_LENGTH)
        message_length = int(message_header.decode('utf-8').strip())
        server_message = self.client_socket.recv(message_length).decode('utf-8')
        return server_message
    
    def send_message(self, message):
        message = message.encode('utf-8')
        message_header = f"{len(message):<{HEADER_LENGTH}}".encode('utf-8')
        try:
            self.client_socket.send(message_header + message)
            return True
        except:
            return False

    async def receive_user_message(self):
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(None, self._blocking_receive_user_message)

    def _blocking_receive_user_message(self):
        username_header = self.client_socket.recv(HEADER_LENGTH)

        if not len(username_header):
            print('Connection closed by the server')
            return ""

        username_length = int(username_header.decode('utf-8').strip())
        username = self.client_socket.recv(username_length).decode('utf-8')

        if username == "CLOSING" or username == "BACK":
            return ""

        message_header = self.client_socket.recv(HEADER_LENGTH)
        message_length = int(message_header.decode('utf-8').strip())
        message = self.client_socket.recv(message_length).decode('utf-8')
        return username, message
