import asyncio
import json
from enum import Enum, auto

import TCP_socket_attributes as tcpAttr
import master_server_communication
from SkeletonDirectionGetter import SkeletonDirectionGetter


_ID_SKELETON_KINECT_SERVICE = 0
_ID_SKELETON_KINECT_SERVICE2 = 1
_ID_WEB_APPSERVICE = 2
_ID_JOYSTICK_SERVICE = 3


class DirectionType(Enum):
    Joystick = auto(),
    Kinect = auto(),
    DoubleKinect = auto(),
    WebApp = auto(),
    Unknown = auto()


async def convert_and_retransfer_joystick_data(reader, writer):
    await retransfer_direction_data(reader, writer)


async def convert_and_retransfer_double_kinect_data(reader, writer, reader2, writer2):
    skeleton_direction_getter = SkeletonDirectionGetter()
    while not reader.at_eof() and not reader2.at_eof() and not broadcast_data_direction.cancelled():
        try:
            body = await asyncio.wait_for(reader.read(8192), timeout=2)
            body2 = await asyncio.wait_for(reader2.read(8192), timeout=2)
            direction = skeleton_direction_getter.get_direction_from_skeleton(body, body2)
            print(direction)
            if direction is not None:
                broadcast(direction)
        except:
            break
    writer.close()
    writer2.close()


async def convert_and_retransfer_kinect_data(reader, writer):
    acc = 0
    skeleton_direction_getter = SkeletonDirectionGetter()
    while not reader.at_eof() and not broadcast_data_direction.cancelled():
        try:
            body = await asyncio.wait_for(reader.read(8192), timeout=2)
            direction = skeleton_direction_getter.get_direction_from_skeleton(body, 'None')
            print(direction)
            if direction is not None:
                broadcast(direction)
            acc += 1
            if acc > 4:
                break
        except:
            break
    writer.close()


async def convert_and_retransfer_web_app_data(reader, writer):
    await retransfer_direction_data(reader, writer)


async def retransfer_direction_data(reader, writer):
    while not reader.at_eof() and not broadcast_data_direction.cancelled():
        message = await reader.read(100)
        data = json.loads(message)
        res = data['direction']
        print(res)
        broadcast(res)
    writer.close()


async def get_port_and_type_from_direction_service():
    man = json.loads(master_server.get_man())
    deps = []
    services_ip_port = {}
    for dep in self_man['deps']:
        deps.append(dep['name'])

    try:
        for server in man:
            try:  # this try to prevent manifest which doesnt contains services
                for service in server['services']:
                    if service['name'] in deps:
                        services_ip_port[service['name']] = server['ip'], service['port']
            except:
                pass
    except:
        pass

    if deps[_ID_SKELETON_KINECT_SERVICE] in services_ip_port and deps[_ID_SKELETON_KINECT_SERVICE2] in services_ip_port:
        ip, port = services_ip_port[deps[_ID_SKELETON_KINECT_SERVICE]]
        ip2, port2 = services_ip_port[deps[_ID_SKELETON_KINECT_SERVICE2]]
        return [ip, ip2], [port, port2], DirectionType.DoubleKinect
    elif deps[_ID_SKELETON_KINECT_SERVICE] in services_ip_port:
        ip, port = services_ip_port[deps[_ID_SKELETON_KINECT_SERVICE]]
        return ip, port, DirectionType.Kinect
    elif deps[_ID_SKELETON_KINECT_SERVICE2] in services_ip_port:
        ip, port = services_ip_port[deps[_ID_SKELETON_KINECT_SERVICE2]]
        return ip, port, DirectionType.Kinect
    elif deps[_ID_WEB_APPSERVICE] in services_ip_port:
        ip, port = services_ip_port[deps[_ID_WEB_APPSERVICE]]
        return ip, port, DirectionType.WebApp
    elif deps[_ID_JOYSTICK_SERVICE] in services_ip_port:
        ip, port = services_ip_port[deps[_ID_JOYSTICK_SERVICE]]
        return ip, port, DirectionType.Joystick
    return None, None, None


async def connect_to_any_direction_output():
    while not broadcast_data_direction.cancelled():
        ip, port, direction_type = await get_port_and_type_from_direction_service()
        if ip is None and port is None and direction_type is None:
            continue
        if direction_type == DirectionType.DoubleKinect:
            reader, writer = await asyncio.open_connection(ip[0], port[0], loop=loop)
            reader2, writer2 = await asyncio.open_connection(ip[1], port[1], loop=loop)
            await convert_and_retransfer_double_kinect_data(reader, writer, reader2, writer2)
        else:
            reader, writer = await asyncio.open_connection(ip, port, loop=loop)

        if direction_type == DirectionType.Kinect:
            await convert_and_retransfer_kinect_data(reader, writer)
        elif direction_type == DirectionType.Joystick:
            await convert_and_retransfer_joystick_data(reader, writer)
        elif direction_type == DirectionType.WebApp:
            await convert_and_retransfer_web_app_data(reader, writer)
        elif direction_type == DirectionType.Unknown:
            await retransfer_direction_data(reader, writer)
        else:
            continue


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
self_man = master_server.get_self_man()
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
