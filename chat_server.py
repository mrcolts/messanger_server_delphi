"""Server for multithreaded (asynchronous) chat application."""
from socket import AF_INET, socket, SOCK_STREAM
from threading import Thread
import json
import urllib.parse


def accept_incoming_connections():
    """Sets up handling for incoming clients."""
    while True:
        client, client_address = SERVER.accept()
        print("%s:%s has connected." % client_address)
        Thread(target=handle_client, args=(client,)).start()


def handle_client(client):  # Takes client socket as argument.
    """Handles a single client connection."""

    data = client.recv(BUFSIZ).decode('cp1251')
    json_data = json.loads(data)

    clients[client] = json_data['username']

    send_welcome(client)
    broadcast(client, 'connect', 'Messanger', f"{json_data['username']} присоединился в чат!")
    
    while True:
        data = client.recv(BUFSIZ).decode('cp1251')
        if not data:
            disconnected(client)
            break
        json_message = json.loads(data)
        username = clients[client]
        broadcast(client, 'new_message', username, json_message['message'])


def broadcast(client, action, username, message):  # prefix is for name identification.
    """Broadcasts a message to all the clients."""
    for sock in clients:
        if (client != sock):
            json_data = json.dumps({'action' : action, 'username' : username, 'message' : message})
            sock.send(str(json_data).encode('utf-8'))

def send_welcome(client, username = 'Messanger'):
    json_data = json.dumps({'action' : 'welcome', 'username' : username ,'message' : f"Добро пожаловать в чат, {clients[client]}!"})
    # print(json_data)
    client.send(str(json_data).encode('utf-8'))

def disconnected(client):
    username = clients[client]
    client.close()
    del clients[client]
    broadcast(client, 'disconnect', 'Messanger', f"{username} покинул чат :(")
        
clients = {}

HOST = ''
PORT = 1234
BUFSIZ = 4098
ADDR = (HOST, PORT)

SERVER = socket(AF_INET, SOCK_STREAM)
# SERVER,(socket.SOL_SOCKET, socket.SO_BROADCAST,1)
SERVER.bind(ADDR)

if __name__ == "__main__":
    SERVER.listen(5)
    print("Waiting for connection...")
    ACCEPT_THREAD = Thread(target=accept_incoming_connections)
    ACCEPT_THREAD.start()
    ACCEPT_THREAD.join()
    SERVER.close()