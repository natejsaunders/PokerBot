import socket
import sys
import json

import pygame
from pygame.locals import *

pygame.init()
pygame.font.init()

test_game_data = {'community': ['♥3', '♦6', '♣T', '♣6', '♠6'], 'hand': ['♠4', '♥2'], 'chips': 498, 'chips_in': 0, 'pot': 9, 'player_chips': [498, 499, 498, 498, 498], 'player_chips_in': [0, 0, 0, 0, 0]}

# UI CONSTANTS
HEIGHT = 550
WIDTH = 600

displaysurface = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Poker")

# Outdated once UI in use
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

def get_surface_from_card(card, font):
    color = pygame.Color(0,0,0)
    if card[0] == '♥' or card[0] == '♦':
        color = pygame.Color(200,0,0)

    return font.render(card, False, color)
    

def draw_game(game_info, surface: pygame.Surface):

    default_font = pygame.font.SysFont('Times New Roman', 18)

    WIDTH = surface.get_width()
    HEIGHT = surface.get_height()

    # Drawing community
    comm_surface = default_font.render("Community cards:", False, pygame.Color(0,0,0))
    surface.blit(comm_surface, (10, 10))
    x = comm_surface.get_width()
    for card in game_info['community']:
        x += 18 * 2
        surface.blit(get_surface_from_card(card, default_font), (x, 10))

    # Drawing hand
    y_surface = default_font.render("Your cards:", False, pygame.Color(0,0,0))
    surface.blit(y_surface, (10, 80))
    x = y_surface.get_width()
    for card in game_info['hand']:
        x += 18 * 2
        surface.blit(get_surface_from_card(card, default_font), (x, 80))

    # Total chips (top-right)
    surface.blit(default_font.render(f"Chips: {game_info['chips']}", False, pygame.Color(0,0,0)), (400, 10))


    




#exit()

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
    for event in pygame.event.get():
        if event.type == QUIT:
            pygame.quit()
            sys.exit()

    displaysurface.fill((0,150,0))
    
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

    draw_game(game_info, displaysurface)

    pygame.display.update()

