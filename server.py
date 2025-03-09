import socket
import select
import threading

HEADER_LENGTH = 10
IP = "127.0.0.1"
PORT = 1234

server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
server_socket.bind((IP, PORT))
server_socket.listen()
sockets_list = [server_socket]
clients:dict = {}
rooms:list[dict] = []
roomids = set()

print(f'Listening for connections on {IP}:{PORT}...')

def find_smallest_missing():
    smallest = 0
    while True:
        if smallest not in roomids:
            return smallest
        smallest += 1

def receive_message(client_socket):
    try:
        message_header = client_socket.recv(HEADER_LENGTH)
        if not len(message_header):
            return False
        message_length = int(message_header.decode('utf-8').strip())
        return {'header': message_header, 'data': client_socket.recv(message_length).decode('utf-8')}
    except:
        return False

def handle_new_connection(client_socket):
    user = {}
    user['state'] = "setting_name"
    return user

def handle_name_set(client_socket, header_name_dict):
    clients[client_socket]['data'] = header_name_dict['data']
    clients[client_socket]['header'] = header_name_dict['header']
    clients[client_socket]['state'] = "selecting_room"
    message = "Select a room by typing the corresponding number:\n-1. New Room\n"
    for room in rooms:
        message += f"{room['id']}. {room['name']}, {room['count']} Users\n"
    message = message.encode('utf-8')
    message_header = f"{len(message):<{HEADER_LENGTH}}".encode('utf-8')
    client_socket.send(message_header + message)

def handle_room_selection(client_socket, selection):
    if not selection.isdigit() and selection != '-1':
        message = "Select a room by typing the corresponding number:\n-1. New Room\n"
        for room in rooms:
            message += f"{room['id']}. {room['name']}, {room['count']} Users\n"
        message_header = f"{len(message):<{HEADER_LENGTH}}".encode("utf-8")
        message = message.encode('utf-8')
        client_socket.send(message_header + message)
        return

    selection = int(selection)
    if selection == -1:
        message = "200".encode('utf-8')
        message_header = f"{len(message):<{HEADER_LENGTH}}".encode('utf-8')
        client_socket.send(message_header + message)
        message = "Set name for your room:\n".encode('utf-8')
        message_header = f"{len(message):<{HEADER_LENGTH}}".encode('utf-8')
        client_socket.send(message_header + message)
        clients[client_socket]['state'] = "creating_room"
    elif selection in roomids:
        message = "200".encode('utf-8')
        message_header = f"{len(message):<{HEADER_LENGTH}}".encode('utf-8')
        client_socket.send(message_header + message)
        clients[client_socket]['state'] = "chatting"
        clients[client_socket]['room'] = str(selection)
        for room in rooms:
            if room['id'] == selection:
                room['count'] += 1
    else:
        message = f"Room {selection} does not exist.\n".encode("utf-8")
        message_header = f"{len(message):<{HEADER_LENGTH}}".encode("utf-8")
        client_socket.send(message_header + message)

def handle_room_creation(client_socket, name): 
    roomid = find_smallest_missing()
    room = {
        'id': roomid,
        'name': name,
        'count': 1
    }
    rooms.append(room)
    roomids.add(roomid)
    clients[client_socket]['room'] = str(roomid)
    clients[client_socket]['state'] = "chatting"

while True:
    read_sockets, _, exception_sockets = select.select(sockets_list, [], sockets_list)
    for notified_socket in read_sockets:
        if notified_socket == server_socket:
            client_socket, client_address = server_socket.accept()
            user = handle_new_connection(client_socket)
            if user:
                sockets_list.append(client_socket)
                clients[client_socket] = user
                print(f'Accepted new connection from {client_address}')
        else:
            message = receive_message(notified_socket)
            print(message["data"])
            if message is False or message["data"] == "CLOSE":
                print(f'Closed connection from: {clients[notified_socket]["data"]}')
                message = "CLOSING".encode('utf-8')
                message_header = f"{len(message):<{HEADER_LENGTH}}".encode('utf-8')
                try:
                    notified_socket.send(message_header + message)
                except:
                    print("TUI user exited")  # ctrl+q out of tui closes pipe and causes server exception
                # update room count when user disconnects
                user = clients[notified_socket]
                if 'room' in user:
                    for room in rooms:
                        if room['id'] == int(user['room']):
                            room['count'] -= 1
                            # remove room if empty
                            if room['count'] == 0:
                                rooms.remove(room)
                                roomids.remove(room['id'])
                            break
                sockets_list.remove(notified_socket)
                del clients[notified_socket]
                continue

            client_state = clients[notified_socket]["state"]

            if message["data"] == "BACK":
                if client_state == "setting_name":
                    print(f'Closed connection from: {clients[notified_socket]}')
                    message = "CLOSING".encode('utf-8')
                    message_header = f"{len(message):<{HEADER_LENGTH}}".encode('utf-8')
                    notified_socket.send(message_header + message)
                    sockets_list.remove(notified_socket)
                    del clients[notified_socket]
                elif client_state == "selecting_room":
                    clients[notified_socket]["state"] = "setting_name"
                    message = "BACK".encode('utf-8')
                    message_header = f"{len(message):<{HEADER_LENGTH}}".encode('utf-8')
                    notified_socket.send(message_header + message)
                elif client_state == "creating_room":
                    clients[notified_socket]["state"] = "selecting_room"
                    handle_room_selection(notified_socket, message["data"])
                elif client_state == "chatting":
                    clients[notified_socket]["state"] = "selecting_room"
                    message = "BACK".encode('utf-8')
                    message_header = f"{len(message):<{HEADER_LENGTH}}".encode('utf-8')
                    notified_socket.send(message_header + message)
                    for room in rooms:
                        if room['id'] == int(clients[notified_socket]['room']):
                            room['count'] -= 1
                            if room['count'] == 0:
                                rooms.remove(room)
                                roomids.remove(room['id'])
                    handle_room_selection(notified_socket, "no")
                continue

            if client_state == "setting_name":
                handle_name_set(notified_socket, message)
            elif client_state == "selecting_room":
                handle_room_selection(notified_socket, message["data"])
            elif client_state == "creating_room":
                handle_room_creation(notified_socket, message["data"])
            elif client_state == "chatting":
                user = clients[notified_socket]
                for client_socket in clients:
                    if (client_socket != notified_socket and  # if statement from hell
                    clients[client_socket].get('state') == 'chatting' and 
                    'room' in clients[client_socket] and 
                    clients[client_socket]['room'] == user['room']):
                        user_header = user['header']
                        user_data = user['data'].encode('utf-8')
                        message_header = message['header']
                        message_data = message['data'].encode('utf-8')
                        client_socket.send(user_header + user_data + message_header + message_data)

    for notified_socket in exception_sockets:
        sockets_list.remove(notified_socket)
        del clients[notified_socket]
