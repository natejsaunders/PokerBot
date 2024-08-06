import socket
import sys
import json

def print_game_info(game_info):
    try:
        print("Community cards:")
        for c in game_info['community']:
            print(f' {c}', end='') 
        print("\nYour hand:")
        for c in game_info['hand']:
            print(f' {c}', end='') 
        print(f"\nCurrent chip count: {game_info['chips']} Money in: {game_info['chips_in']} Pot: {game_info['pot']}\n")
    except KeyError as e:
        print(str(e))
        print("Error formatting game data: ")
        print(game_info)

CLIENT_NAME = 'Bob'#input("Enter Name: ")

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
initial_info = json.loads(connection_response.decode('utf-8'))
print(initial_info)

resp_initial_info = {
    'client_name': CLIENT_NAME
}
# Sending intial information
client_socket.send(json.dumps(resp_initial_info).encode('utf-8'))

while True:
    go = {
        'action': 'FOLD',
        'amount': 0
    }

    message = input('Bet or fold:').lower()
    if message == 'game.info':
        response = message
    elif message.startswith('b'):
        go['action'] = 'BET'
        try:
            amount = int(input('Amount: '))
        except ValueError:
            amount = 0
        
        go['amount'] = amount

        response = json.dumps(go)
    else:
        response = json.dumps(go)

    client_socket.send(response.encode('utf-8'))
    reply = client_socket.recv(2048)
    decoded_reply = reply.decode('utf-8')
    
    if message == 'bye':
      break

    game_info = json.loads(decoded_reply)
    print_game_info(game_info)

