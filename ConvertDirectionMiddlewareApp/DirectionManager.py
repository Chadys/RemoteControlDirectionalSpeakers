import asyncio
import json
from enum import Enum, auto

import TCP_socket_attributes as tcpAttr
import master_server_communication
from SkeletonDirectionGetter import SkeletonDirectionGetter


class DirectionType(Enum):
    Joystick = auto(),
    Kinect = auto(),
    DoubleKinect = auto(),
    Launchpad = auto(),
    WebApp = auto(),
    Unknown = auto()


async def convert_and_retransfer_joystick_data(reader, writer):
    # TODO
    await retransfer_direction_data(reader, writer)


async def convert_and_retransfer_double_kinect_data(reader, writer, reader2, writer2):
    skeleton_direction_getter = SkeletonDirectionGetter()
    while not reader.at_eof() and not reader2.at_eof() and not broadcast_data_direction.cancelled():
        body = await asyncio.wait_for(reader.read(8192), timeout=2)
        body2 = await asyncio.wait_for(reader2.read(8192), timeout=2)
        direction = skeleton_direction_getter.get_direction_from_skeleton(body, body2)
        print(direction)
        if direction is not None:
            broadcast(direction)
    writer.close()
    writer2.close()


async def convert_and_retransfer_kinect_data(reader, writer):
    skeleton_direction_getter = SkeletonDirectionGetter()
    while not reader.at_eof() and not broadcast_data_direction.cancelled():
        body = await asyncio.wait_for(reader.read(8192), timeout=2)
        direction = skeleton_direction_getter.get_direction_from_skeleton(body, 'None')
        print(direction)
        if direction is not None:
            broadcast(direction)
    writer.close()


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
    man = json.loads(master_server.get_man())
    skeleton_kinect_service_port = ''
    skeleton_kinect_service_port2 = ''
    coordinate_launchpad_service_port = ''
    direction_webapp_service_port = ''
    direction_joystick_service_port = ''
    ip = ''

    try:
        for server in man:
            ip = server['ip']
            for service in server['services']:
                if service['name'] == 'skeletonKinectService':
                    skeleton_kinect_service_port = service['port']
                elif service['name'] == 'skeletonKinectService2':
                    skeleton_kinect_service_port2 = service['port']
                elif service['name'] == 'coordinateLaunchpadService':
                    coordinate_launchpad_service_port = service['port']
                elif service['name'] == 'directionWebappService':
                    direction_webapp_service_port = service['port']
                elif service['name'] == 'directionJoystickService':
                    direction_joystick_service_port = service['port']
    except:
        pass

    ip = '192.168.0.8'  # TODO tmp line a effacer
    if skeleton_kinect_service_port != '' and skeleton_kinect_service_port2 != '':
        return [ip, skeleton_kinect_service_port], [ip, skeleton_kinect_service_port2], DirectionType.DoubleKinect
    elif skeleton_kinect_service_port != '' or skeleton_kinect_service_port2 != '':
        return ip, skeleton_kinect_service_port, DirectionType.Kinect
    elif coordinate_launchpad_service_port != '':
        return ip, coordinate_launchpad_service_port, DirectionType.Launchpad
    elif direction_webapp_service_port != '':
        return ip, direction_webapp_service_port, DirectionType.WebApp
    elif direction_joystick_service_port != '':
        return ip, direction_joystick_service_port, DirectionType.Joystick
    return None


async def connect_to_any_direction_output():
    while not broadcast_data_direction.cancelled():
        ip, port, direction_type = await get_port_and_type_from_direction_service()
        if direction_type == DirectionType.DoubleKinect:
            reader, writer = await asyncio.open_connection(ip[0], port[0], loop=loop)
            reader2, writer2 = await asyncio.open_connection(ip[1], port[1], loop=loop)
            await convert_and_retransfer_double_kinect_data(reader, writer, reader2, writer2)
        else:
            reader, writer = await asyncio.open_connection(ip, port, loop=loop)

        if direction_type == DirectionType.Kinect:
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

master_server = master_server_communication.MasterServer()
try:
    tasks = loop.run_until_complete(asyncio.gather(*tasks))
except KeyboardInterrupt:
    pass
finally:
    tcpsocket_send_server.close()
    broadcast_data_direction.cancel()
    asyncio.gather(*asyncio.Task.all_tasks()).cancel()
    loop.call_soon(loop.close)
    master_server.close_connection()
