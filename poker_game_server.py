import socket
from _thread import *
import sys
import ast

from poker import Game


class Server:
    def __init__(self, host, port):
        self.game = Game(5)
        self.game.begin_round()
        self.client_count = 0

        self.SERVER_NAME = "Nate's Poker Server"

        self.host = host
        self.port = port

    def client_handler(self, connection):
        this_client_id = self.client_count

        out_initial_info = {
            'server_name': self.SERVER_NAME,
            'client_id': this_client_id
        }
        # Sending intial information
        connection.send(str.encode(str(out_initial_info)))

        # Receiving intial information
        connection_response = connection.recv(2048)
        initial_info = ast.literal_eval(connection_response.decode('utf-8'))
        print(f"Connection {this_client_id} established with client: {initial_info['client_name']}")

        while True:
            try:
                data = connection.recv(2048)
                message = data.decode('utf-8')
                if message == 'BYE':
                    print(f"BYE message received on connection {this_client_id}, closing...")
                    reply = 'BYE'
                    connection.sendall(str.encode(reply))
                    self.client_count -= 1
                    break
                elif message == 'game.info':
                    reply = self.game.info(this_client_id)
                    connection.sendall(str.encode(str(reply)))
                # elif message == 'init.info':
                #     reply = self.game.info(initial_info)
                #     connection.sendall(str.encode(str(reply)))
                reply = out_initial_info
                connection.sendall(str.encode(str(reply)))
            # Excepting all errors i know im a bad boy
            except:
                print(f"Error with connection {this_client_id}, closing...")
                reply = 'BYE'
                connection.sendall(str.encode(str(reply)))
                self.client_count -= 1
                break
        connection.close()

    def accept_connections(self, server_socket):
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