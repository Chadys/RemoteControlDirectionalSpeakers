import TCP_socket_attributes as tcpAttr
import asyncio
import numpy as np
import json
import math
from collections import namedtuple
from enum import Enum


class HandState(Enum):
    RIGHT = 0
    LEFT = 1
    OPEN = 2
    CLOSED = 3
    LASSO = 4


def check_hand_state(body, hand, state):
    try:
        if hand == HandState.RIGHT.value:
            if state == HandState.OPEN.value and body.HandRightState == HandState.OPEN.value:
                return True
            if state == HandState.CLOSED.value and body.HandRightState == HandState.CLOSED.value:
                return True
            if state == HandState.LASSO.value and body.HandRightState == HandState.LASSO.value:
                return True
        if hand == HandState.LEFT.value:
            if state == HandState.OPEN.value and body.HandLeftState == HandState.OPEN.value:
                return True
            if state == HandState.CLOSED.value and body.HandLeftState == HandState.CLOSED.value:
                return True
            if state == HandState.LASSO.value and body.HandLeftState == HandState.LASSO.value:
                return True
        return False
    except:
        return False


def init_hand_kinect(hand_to_use, kinect_id, body, body2):
    try:
        if body.HandLeftState == HandState.OPEN.value and body.HandRightState == HandState.CLOSED.value:
            hand_to_use = HandState.RIGHT.value
            kinect_id = 1
            print("Right hand init. Kinect 1")
    except:
        pass
    try:
        if body2.HandLeftState == HandState.OPEN.value and body2.HandRightState == HandState.CLOSED.value:
            hand_to_use = HandState.RIGHT.value
            kinect_id = 2
            print("Right hand init. Kinect 2")
    except:
        pass
    try:
        if body.HandLeftState == HandState.CLOSED.value and body.HandRightState == HandState.OPEN.value:
            hand_to_use = HandState.LEFT.value
            kinect_id = 1
            print("Left hand init. Kinect 1")
    except:
        pass
    try:
        if body2.HandLeftState == HandState.CLOSED.value and body2.HandRightState == HandState.OPEN.value:
            hand_to_use = HandState.LEFT.value
            kinect_id = 2
            print("Left hand init. Kinect 2")
    except:
        pass
    return hand_to_use, kinect_id


def init_angle_kinect2(angle_to_use, hand, body, body2):
    try:
        if (
                hand == HandState.RIGHT.value and
                body.HandRightState == HandState.LASSO.value and
                body.HandLeftState == HandState.OPEN.value
        ) or (
                hand == HandState.LEFT.value and
                body.HandLeftState == HandState.LASSO.value and
                body.HandRightState == HandState.OPEN.value
        ):
            angle_to_use = angle_body_from_kinect(body, hand)
            print("Init Angle kinect2 = ", angle_to_use)
    except:
        pass
    try:
        if (
                hand == HandState.RIGHT.value and
                body2.HandRightState == HandState.LASSO.value and
                body2.HandLeftState == HandState.OPEN.value
        ) or (
                hand == HandState.LEFT.value and
                body2.HandLeftState == HandState.LASSO.value and
                body2.HandRightState == HandState.OPEN.value
        ):
            angle_to_use = angle_body_from_kinect(body2, hand)
            print("Init Angle kinect2 = ", angle_to_use)
    except:
        pass
    return angle_to_use


# def angle_body_from_kinect1(body):
#     x_h, y_h, z_h = (
#         body.Joints.SpineBase.Position.X, body.Joints.SpineBase.Position.Y, body.Joints.SpineBase.Position.Z)
#     x_p, y_p, z_p = (
#         body.Joints.WristRight.Position.X, body.Joints.WristRight.Position.Y, body.Joints.WristRight.Position.Z)
#
#     gamma2 = math.sqrt(math.pow(z_p - z_h, 2) + math.pow(x_p - z_h, 2))
#     gamma1 = (z_h * gamma2) / (z_p - z_h)
#     beta = np.degrees(np.arcsin(z_h / gamma1)) * 2
#
#     angle = 180 - beta, beta
#     # if z_p > z_h:
#     #     angle = 90 + (100 - angle)
#     return angle
#
#
# def angle_body_from_kinect2(body):
#     x_h2, y_h2, z_h2 = (
#         body.Joints.SpineBase.Position.X, body.Joints.SpineBase.Position.Y, body.Joints.SpineBase.Position.Z)
#     x_p2, y_p2, z_p2 = (
#         body.Joints.WristRight.Position.X, body.Joints.WristRight.Position.Y, body.Joints.WristRight.Position.Z)
#
#     gamma4 = math.sqrt(math.pow(z_p2 - z_h2, 2) + math.pow(x_p2 - z_h2, 2))
#     beta = np.degrees(np.arcsin(x_h2 / gamma4)) * 2
#
#     angle = 180 - beta, beta
#     # if z_p > z_h:
#     #     angle = 90 + (100 - angle)
#     return angle


def best_angle_body_from_kinect(body, body2, hand, angle_kinect2, kinect_id):
    try:
        angle_k1 = angle_body_from_kinect(body, hand)
        angle_k2 = angle_body_from_kinect(body2, hand)
        if kinect_id == 2:
            angle_k1 += angle_kinect2
        else:
            angle_k2 += angle_kinect2
        if angle_k1 < 0:
            angle_k1 = 360 + angle_k1
        if angle_k2 < 0:
            angle_k2 = 360 + angle_k2
        # print("K1:", angle_k1, " + ", angle_kinect2, " / ", kinect_id)
        # print("K2:", angle_k2, " + ", angle_kinect2, " / ", kinect_id)
        if body2.HandLeftState == HandState.OPEN.value or body2.HandRightState == HandState.OPEN.value:
            return angle_k2
        else:
            return angle_k1
    except:
        pass


def angle_body_from_kinect(body, hand):
    if body is not None:
        x_h, y_h, z_h = (
            body.Joints.SpineBase.Position.X,
            body.Joints.SpineBase.Position.Y,
            body.Joints.SpineBase.Position.Z)

        if hand == HandState.LEFT.value:
            x_p, y_p, z_p = (
                body.Joints.WristLeft.Position.X,
                body.Joints.WristLeft.Position.Y,
                body.Joints.WristLeft.Position.Z)
        else:
            x_p, y_p, z_p = (
                body.Joints.WristRight.Position.X,
                body.Joints.WristRight.Position.Y,
                body.Joints.WristRight.Position.Z)

        beta = math.sqrt(math.pow(x_p - x_h, 2) + math.pow(z_p - z_h, 2))
        alpha_h = ((x_h * math.sqrt(beta)) / x_p) * (1 / (1 - (x_h / x_p)))

        angle = np.degrees(np.arcsin(x_h / alpha_h)) * 2 - 5
        if z_p > z_h:
            angle = 90 + (100 - angle)
        return angle
    return None


async def attempt_connection_and_data():
    global reader, writer, reader2, writer2, state_reader, state_reader2
    data = None
    data2 = None
    try:
        if state_reader is not True:
            reader, writer = await asyncio.wait_for(
                asyncio.open_connection(tcpAttr.kinect1_server_attributes['TCP_IP'],
                                        tcpAttr.kinect1_server_attributes[
                                            'TCP_PORT']), timeout=2)
            state_reader = True
    except:
        reader = None
    try:
        if state_reader2 is not True:
            reader2, writer2 = await asyncio.wait_for(
                asyncio.open_connection(tcpAttr.kinect2_server_attributes['TCP_IP'],
                                        tcpAttr.kinect2_server_attributes['TCP_PORT']), timeout=2)
            state_reader2 = True
    except:
        reader2 = None
    if reader is None and reader2 is None:
        print('No kinect server available. Retrying...')

    try:
        if state_reader is True and reader is not None:
            data = await asyncio.wait_for(reader.read(tcpAttr.kinect1_server_attributes['BUFFER_SIZE']), timeout=2)
    except:
        reader = None
        state_reader = False
    try:
        if state_reader2 is True and reader2 is not None:
            data2 = await asyncio.wait_for(reader2.read(tcpAttr.kinect2_server_attributes['BUFFER_SIZE']), timeout=2)
    except:
        reader2 = None
        state_reader2 = False
    return data, data2


def transform(data, num):
    if data is None:
        return "Kinect" + num + ": server probably down"
    try:
        str_data = data.decode("utf-8")
        if str_data.__contains__('None'):
            return 'None'
        if str_data.count(str_data[0:30]) > 1:
            str_data = str_data[:str_data.rfind(str_data[0:30])]
        return json.loads(str_data, object_hook=lambda d: namedtuple('X', d.keys())(*d.values()))
    except:
        return "Kinect" + num + ": Format reçu anormal."


async def main():
    hand = None
    angle_kinect2 = 90
    kinect_id = 1
    try:
        while True:
            data, data2 = await attempt_connection_and_data()

            print('\n' * 20)
            body = transform(data, '1')
            body2 = transform(data2, '2')

            try:
                hand, kinect_id = init_hand_kinect(hand, kinect_id, body, body2)
                angle_kinect2 = init_angle_kinect2(angle_kinect2, hand, body, body2)

                print(best_angle_body_from_kinect(body, body2, hand, angle_kinect2, kinect_id))
            except:
                pass
    except KeyboardInterrupt:
        writer.close()
        writer2.close()
        pass


state_reader = False
state_reader2 = False
asyncio.run(main())
