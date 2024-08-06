import socket
from _thread import *
import sys
import json

from poker import Game

class Server:
    def __init__(self, host, port):
        self.MAX_CLIENTS = 5
        self.SERVER_NAME = "Nate's Poker Server"

        self.game = Game(self.MAX_CLIENTS)
        self.game.begin_round()
        self.client_count = 0

        self.host = host
        self.port = port

    def client_handler(self, connection):
        this_client_id = self.client_count
        self.game.add_player(this_client_id)
        self.game.begin_round()

        out_initial_info = {
            'server_name': self.SERVER_NAME,
            'client_id': this_client_id
        }
        # Sending intial information
        connection.sendall(json.dumps(out_initial_info).encode('utf-8'))

        # Receiving intial information
        connection_response = connection.recv(2048)
        initial_info = json.loads(connection_response.decode('utf-8'))
        print(f"Connection {this_client_id} established with client: {initial_info['client_name']}")

        while True:
            try:
                data = connection.recv(2048)
                message = data.decode('utf-8')
                print(message)
                if message == 'BYE':
                    print(f"BYE message received on connection {this_client_id}, closing...")
                    reply = 'BYE'
                    connection.sendall(str.encode(reply))
                    self.client_count -= 1
                    break
                elif message == 'init.info':
                    reply = initial_info
                elif message == 'game.info':
                    reply = self.game.info(this_client_id)
                else:
                    go_data = json.loads(message)
                    reply = self.game.action(this_client_id, go_data['action'], go_data['amount'])
                connection.sendall(json.dumps(reply).encode('utf-8'))
            # Excepting all errors i know im a bad boy
            except Exception as e:
                print(f"Error with connection {this_client_id}, closing...")
                print(str(e))
                reply = 'BYE'
                connection.sendall(str.encode(str(reply)))
                self.client_count -= 1
                break
        connection.close()

    def accept_connections(self, server_socket):
        if self.client_count >= self.MAX_CLIENTS: 
            print("Refusing new client connection")
            return

        client, address = server_socket.accept()
        print(f'Connected to: {address[0]}:{str(address[1])}')
        self.client_count += 1
        start_new_thread(self.client_handler, (client, ))

    def start_server(self):
        server_socket = socket.socket()
        try:
            server_socket.bind((self.host, self.port))
        except socket.error as e:
            print(str(e))
        print(f'Server is listing on the port {self.port}...')
        server_socket.listen()

        while True:
            self.accept_connections(server_socket)


HOST = '127.0.0.1'
PORT = 8888
try:
    HOST = sys.argv[1]
    PORT = int(sys.argv[2])
except IndexError:
    print(f"No IP or Port set in argv defaulting to: {HOST}:{PORT}")

server = Server(HOST, PORT)
server.start_server()