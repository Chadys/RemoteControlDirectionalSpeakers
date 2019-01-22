import asyncio
import json
from enum import Enum, auto

import TCP_socket_attributes as tcpAttr
import master_server_communication


class DirectionType(Enum):
    Joystick = auto(),
    Kinect = auto(),
    Launchpad = auto(),
    WebApp = auto(),
    Unknown = auto()


async def convert_and_retransfer_joystick_data(reader, writer):
    # TODO
    await retransfer_direction_data(reader, writer)


async def convert_and_retransfer_kinect_data(reader, writer):
    # TODO
    await retransfer_direction_data(reader, writer)


async def convert_and_retransfer_launchpad_data(reader, writer):
    # TODO
    await retransfer_direction_data(reader, writer)


async def convert_and_retransfer_web_app_data(reader, writer):
    # TODO
    await retransfer_direction_data(reader, writer)


async def retransfer_direction_data(reader, writer):
    while not reader.at_eof() and not broadcast_data_direction.cancelled():
        message = await reader.read(100)
        data = json.loads(message)
        print(message)
        broadcast(data)
    writer.close()


async def get_port_and_type_from_direction_service():
    # TODO
    return 'ip-vincent-ordi-kinect', 'port-vincent-server-tcp-kinect', DirectionType.Kinect


async def connect_to_any_direction_output():
    while not broadcast_data_direction.cancelled():
        ip, port, direction_type = await get_port_and_type_from_direction_service()
        reader, writer = await asyncio.open_connection(ip, port, loop=loop)

        if direction_type == DirectionType.Kinect:  # TODO change so that it takes skeletton from several kinect service
            await convert_and_retransfer_kinect_data(reader, writer)
        elif direction_type == DirectionType.Launchpad:
            await convert_and_retransfer_launchpad_data(reader, writer)
        elif direction_type == DirectionType.Unknown:
            continue
        else:  # DirectionType.WebApp or DirectionType.Joystick
            await retransfer_direction_data(reader, writer)


async def send_to_subscribers(reader, writer):
    while not reader.at_eof() or broadcast_data_direction.cancelled():
        read_task = loop.create_task(reader.read(100))
        for f in asyncio.as_completed({read_task, broadcast_data_direction}):
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
                print('Client sent: ' + message)
    writer.close()


def broadcast(data):
    global broadcast_data_direction
    broadcast_data_direction.set_result(data)
    broadcast_data_direction = loop.create_future()


loop = asyncio.get_event_loop()

broadcast_data_direction = loop.create_future()

tcpsocket_send_server = asyncio.start_server(send_to_subscribers,
                                             tcpAttr.middleware_server_attributes['TCP_IP'],
                                             tcpAttr.middleware_server_attributes['TCP_PORT'],
                                             loop=loop)

tasks = connect_to_any_direction_output(), \
        tcpsocket_send_server

try:
    master_server_communication.init_connection()
    master_server_communication.send_man()

    tasks = loop.run_until_complete(asyncio.gather(*tasks))
except KeyboardInterrupt:
    pass
finally:
    tcpsocket_send_server.close()
    broadcast_data_direction.cancel()
    asyncio.gather(*asyncio.Task.all_tasks()).cancel()
    loop.call_soon(loop.close)
    master_server_communication.close_connection()
