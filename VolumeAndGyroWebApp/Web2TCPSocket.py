import asyncio
import websockets
import json
# import TCP_socket_attributes as tcpAttr


async def retransfer(websocket, _):
    try:
        async for message in websocket:
            data = json.loads(message)
            print(message)
            broadcast(data)

    except websockets.exceptions.ConnectionClosed:
        pass


async def send_to_subscribers(reader, writer):
    while not reader.at_eof():
        read_task = loop.create_task(reader.read(100))
        for f in asyncio.as_completed({read_task, broadcast_data}):
            data = await f
            if isinstance(data, dict):
                writer.write(data.popitem()[1].encode())
                await writer.drain()
                if not read_task.done():
                    read_task.cancel()
                break
            else:
                if reader.at_eof():
                    break
                message = data.decode().strip()
                print('Client sent: ' + message)
    writer.close()


def broadcast(data):
    global broadcast_data
    broadcast_data.set_result(data)
    broadcast_data = loop.create_future()


loop = asyncio.get_event_loop()
broadcast_data = loop.create_future()
websocket_server = websockets.serve(retransfer, '0.0.0.0', 8765, loop=loop)
tcpsocket_server = asyncio.start_server(send_to_subscribers, '', 6543, loop=loop)
websocket_server, tcpsocket_server = loop.run_until_complete(asyncio.gather(
    websocket_server,
    tcpsocket_server
))
try:
    loop.run_forever()
except KeyboardInterrupt:
    pass
finally:
    broadcast_data.cancel()
    tcpsocket_server.close()
    loop.run_until_complete(tcpsocket_server.wait_closed())
    asyncio.gather(*asyncio.Task.all_tasks()).cancel()
    loop.call_soon(loop.close)
