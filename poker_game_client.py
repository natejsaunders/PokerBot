import socket
import sys
import ast

CLIENT_NAME = input("Enter Name: ")

HOST = '127.0.0.1'
PORT = 8888
try:
    HOST = sys.argv[1]
    PORT = int(sys.argv[2])
except IndexError:
    print(f"No IP or Port set in argv defaulting to: {HOST}:{PORT}")

client_socket = socket.socket()
print('Waiting for connection')
try:
    client_socket.connect((HOST, PORT))
except socket.error as e:
    print(str(e))

# Receiving intial information
connection_response = client_socket.recv(2048)
initial_info = ast.literal_eval(connection_response.decode('utf-8'))
print(initial_info)

resp_initial_info = {
    'client_name': CLIENT_NAME
}
# Sending intial information
client_socket.send(str.encode(str(resp_initial_info)))

while True:
    message = input('Your message: ')
    client_socket.send(str.encode(message))
    reply = client_socket.recv(2048)
    decoded_reply = reply.decode('utf-8')
    
    if message == 'BYE':
      break

    game_info = ast.literal_eval(decoded_reply)
    print(game_info)

