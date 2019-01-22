import asyncio
import websockets
import json

import TCP_socket_attributes as tcpAttr
import master_server_communication


async def retransfer(websocket, _, is_volume):
    try:
        async for message in websocket:
            data = json.loads(message)
            print(message)
            broadcast(data, is_volume)

    except websockets.exceptions.ConnectionClosed:
        pass


async def send_to_subscribers(reader, writer, is_volume):
    while not reader.at_eof():
        broadcast_data = broadcast_data_volume if is_volume else broadcast_data_direction
        if broadcast_data.cancelled():
            break
        read_task = loop.create_task(reader.read(100))
        for f in asyncio.as_completed({read_task, broadcast_data}):
            data = await f
            if isinstance(data, dict):
                writer.write(json.dumps(data).encode())
                await writer.drain()
                if not read_task.done():
                    read_task.cancel()
                break
            else:
                if reader.at_eof():
                    break
                message = data.decode().strip()
                print(f'Client sent: {message}')
    writer.close()


def broadcast(data, is_volume):
    global broadcast_data_volume, broadcast_data_direction
    if is_volume:
        broadcast_data_volume.set_result(data)
        broadcast_data_volume = loop.create_future()
    else:
        broadcast_data_direction.set_result(data)
        broadcast_data_direction = loop.create_future()


loop = asyncio.get_event_loop()

broadcast_data_volume = loop.create_future()
broadcast_data_direction = loop.create_future()

websocket_server_volume = websockets.serve(lambda w, p: retransfer(w, p, True),
                                           '', tcpAttr.webapp_server_attributes['WS_VOLUME'], loop=loop)
websocket_server_direction = websockets.serve(lambda w, p: retransfer(w, p, False),
                                              '', tcpAttr.webapp_server_attributes['WS_DIRECTION'], loop=loop)

tcpsocket_server_volume = asyncio.start_server(lambda r, w: send_to_subscribers(r, w, True),
                                               tcpAttr.webapp_server_attributes['TCP_IP_VOLUME'],
                                               tcpAttr.webapp_server_attributes['TCP_PORT_VOLUME'],
                                               loop=loop)
tcpsocket_server_direction = asyncio.start_server(lambda r, w: send_to_subscribers(r, w, False),
                                                  tcpAttr.webapp_server_attributes['TCP_IP_DIRECTION'],
                                                  tcpAttr.webapp_server_attributes['TCP_PORT_DIRECTION'],
                                                  loop=loop)

tasks = websocket_server_volume,\
        websocket_server_direction,\
        tcpsocket_server_volume,\
        tcpsocket_server_direction

try:
    master_server_communication.init_connection()
    master_server_communication.send_man()
    tasks = loop.run_until_complete(asyncio.gather(*tasks))
    loop.run_forever()
except KeyboardInterrupt:
    pass
finally:
    tcpsocket_server_volume.close()
    tcpsocket_server_direction.close()
    broadcast_data_volume.cancel()
    broadcast_data_direction.cancel()
    asyncio.gather(*asyncio.Task.all_tasks()).cancel()
    loop.call_soon(loop.close)
    master_server_communication.close_connection()
