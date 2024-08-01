import socket
import asyncio

from poker import Game

game = Game(5)

client_count = 0

async def establish_client():
    reader, writer = await asyncio.open_connection('127.0.0.1', 8888)
    
    data = await reader.read(4096)
    if data.decode() == 'ESTABLISH CONNECTION':
        writer.write('ESTABLISH CONNECTION'.encode())
        await writer.drain()



