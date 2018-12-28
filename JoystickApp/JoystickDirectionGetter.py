import asyncio
import pygame
from pygame.math import Vector2

import TCP_socket_attributes as tcpAttr

PRECISION = 0.01


def is_joystick_center_pos(joy):
    return abs(joy.get_axis(0)) < PRECISION and abs(joy.get_axis(1)) < PRECISION


async def get_joystick_events():
    # buttons = joystick.get_numbuttons()
    # print(f'Number of buttons: {buttons}')
    # axes = joystick.get_numaxes()
    # print(f'Number of axes: {axes}')
    last_angle = 0

    while True:
        for event in pygame.event.get():
            # if event.type == pygame.JOYBUTTONDOWN:
            #     print(f'Joystick button {event.button} pressed.')
            # elif event.type == pygame.JOYBUTTONUP:
            #     print(f'Joystick button {event.button} released.')
            if event.type == pygame.JOYAXISMOTION:
                # print(f'Axis {event.axis} value: {round(joystick.get_axis(event.axis), 3)}')

                if not is_joystick_center_pos(joystick):
                    # convert joystick two axes to 360° angle ; ref :
                    # https://stackoverflow.com/questions/52504266/converting-pygame-2-axis-joystick-float-to-360-angle
                    vec = Vector2(joystick.get_axis(0), joystick.get_axis(1))
                    radius, angle = vec.as_polar()  # angle is between -180 and 180.
                    # Map the angle that as_polar returns to 0-360 with 0 pointing up.
                    adjusted_angle = (angle + 90) % 360
                    if abs(adjusted_angle - last_angle) > PRECISION:
                        last_angle = adjusted_angle
                        broadcast(last_angle)
        await asyncio.sleep(0.5)


async def send_to_subscribers(reader, writer):
    while not reader.at_eof():
        read_task = loop.create_task(reader.read(100))
        for f in asyncio.as_completed({read_task, broadcast_data_direction}):
            data = await f
            if isinstance(data, float):
                writer.write(f'{{"direction": {data}}}'.encode())
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


pygame.init()
pygame.joystick.init()
joysticks = [pygame.joystick.Joystick(x) for x in range(pygame.joystick.get_count())]
if len(joysticks) < 1:
    print('Error : At least one joystick must be connected')
    exit(1)
joystick = joysticks[0]
joystick.init()

loop = asyncio.get_event_loop()

broadcast_data_direction = loop.create_future()

tcpsocket_send_server = asyncio.start_server(send_to_subscribers,
                                             tcpAttr.joystick_server_attributes['TCP_IP'],
                                             tcpAttr.joystick_server_attributes['TCP_PORT'],
                                             loop=loop)

tasks = get_joystick_events(), \
        tcpsocket_send_server

try:
    tasks = loop.run_until_complete(asyncio.gather(*tasks))
except KeyboardInterrupt:
    pass
finally:
    tcpsocket_send_server.close()
    broadcast_data_direction.cancel()
    asyncio.gather(*asyncio.Task.all_tasks()).cancel()
    loop.call_soon(loop.close)

    joystick.quit()
    pygame.joystick.quit()
    pygame.quit()
