import socket
import asyncio

client_id = 0

async def establish_connection(server_ip='127.0.0.1', server_port=8888):
    reader, writer = await asyncio.open_connection(server_ip, server_port)

    writer.write('ESTABLISH CONNECTION'.encode())
    await writer.drain()

    data = await reader.read(100)
    client_id = data.decode()

    
