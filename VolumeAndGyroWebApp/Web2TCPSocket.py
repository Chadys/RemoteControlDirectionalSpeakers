import asyncio
import websockets
import json


async def retransfer(websocket, _):
    try:
        async for message in websocket:
            # data = json.loads(message)
            print(message)
    except websockets.exceptions.ConnectionClosed:
        pass

start_server = websockets.serve(retransfer, '0.0.0.0', 8765)

asyncio.get_event_loop().run_until_complete(start_server)
asyncio.get_event_loop().run_forever()
