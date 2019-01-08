import TCP_socket_attributes as tcpAttr
import asyncio
import numpy as np
import json
import math
from collections import namedtuple


def angle_body_from_kinect(body):
    xH, yH, zH = (body.Joints.SpineBase.Position.X, body.Joints.SpineBase.Position.Y, body.Joints.SpineBase.Position.Z)
    xP, yP, zP = (body.Joints.WristRight.Position.X, body.Joints.WristRight.Position.Y, body.Joints.WristRight.Position.Z)

    alphaH = ((xH * math.sqrt(math.sqrt(math.pow(xP - xH, 2) + math.pow(zP - zH, 2)))) / xP) * (1 / (1 - (xH / xP)))
    # return np.degrees(np.acos((A * A + B * B - C * C)/(2.0 * A * B)))
    # return body.Joints.WristRight.Position.Z
    # return np.degrees(np.arccos(np.clip(np.dot(v1_u, v2_u, v3_u), -1.0, 1.0)))
    print('ZP = ', zP, "\t", 'ZH = ', zH)
    angle = np.degrees(np.arcsin(xH / alphaH)) * 2
    if zP > zH:
        angle = 100 + (100 - angle)
    return angle


def get_direction(body):
    v1 = (body.Joints.WristRight.Position.X, body.Joints.WristRight.Position.Z, body.Joints.WristRight.Position.Y)
    # v2 = (body.Joints.WristLeft.Position.X, body.Joints.WristLeft.Position.Y, body.Joints.WristLeft.Position.Z)
    v3 = (body.Joints.SpineBase.Position.X, body.Joints.SpineBase.Position.Z, body.Joints.SpineBase.Position.Y)
    angle_1 = angle_between(v1, v3)
    # angle_2 = angle_between(v2, v3)
    return angle_1  # angle_1 if angle_1 > angle_2 else angle_2


def get_higher_joint(skeleton):
    higher_joint = skeleton.Joints[0]
    for joint in skeleton.Joints:
        if joint.Position.Y > higher_joint.Position.Y:
            higher_joint = joint
    return higher_joint


def matching_higher_point(skeleton_a, skeleton_b):
    """
    Return True si les 2 joints le plus haut correspondent,
    sinon sa voudrais dire que les skeletons n'appartiennent pas au meme body
    """
    joint_a = get_higher_joint(skeleton_a)
    joint_b = get_higher_joint(skeleton_b)
    if joint_a.Key == joint_b.Key:
        return True
    else:
        return False


def unit_vector(vector):
    """ Returns the unit vector of the vector.  """
    return vector / np.linalg.norm(vector)


def angle_between(v1, v2):
    """ Returns the angle in radians between vectors 'v1' and 'v2'::
            >>> angle_between((1, 0, 0), (0, 1, 0))
            1.5707963267948966
            >>> angle_between((1, 0, 0), (1, 0, 0))
            0.0
            >>> angle_between((1, 0, 0), (-1, 0, 0))
            3.141592653589793
        https://stackoverflow.com/questions/2827393/angles-between-two-n-dimensional-vectors-in-python/13849249#13849249
    """
    v1_u = unit_vector(v1)
    v2_u = unit_vector(v2)
    return np.degrees(np.arcsin(np.clip(np.dot(v1_u, v2_u), -1.0, 1.0)))


async def attempt_connection(state_reader, state_reader2):
    global reader, writer, reader2, writer2
    try:
        if state_reader is not True:
            reader, writer = await asyncio.open_connection(tcpAttr.kinect1_server_attributes['TCP_IP'],
                                                           tcpAttr.kinect1_server_attributes['TCP_PORT'])
            state_reader = True
    except:
        reader = None
    try:
        if state_reader2 is not True:
            reader2, writer2 = await asyncio.open_connection(tcpAttr.kinect2_server_attributes['TCP_IP'],
                                                             tcpAttr.kinect2_server_attributes['TCP_PORT'])
            state_reader2 = True
    except:
        reader2 = None
    if reader is None and reader2 is None:
        print('No kinect server available. Retrying...')
    return state_reader, state_reader2


async def main():
    try:
        state_reader = False
        state_reader2 = False
        data = None
        data2 = None
        while True:
            state_reader, state_reader2 = await attempt_connection(state_reader, state_reader2)
            if state_reader is True and reader is not None:
                data = await reader.read(tcpAttr.kinect1_server_attributes['BUFFER_SIZE'])
            if state_reader2 is True and reader2 is not None:
                data2 = await reader2.read(tcpAttr.kinect2_server_attributes['BUFFER_SIZE'])

            if data is not None:
                try:
                    body = json.loads(data, object_hook=lambda d: namedtuple('X', d.keys())(*d.values()))
                except:
                    print("Format reçu anormal.")
                    continue
                if type(body) is str:
                    print(body)  # means 'None'
                else:
                    print(angle_body_from_kinect(body))
            if data2 is not None:
                pass
    except KeyboardInterrupt:
        writer.close()
        writer2.close()
        pass


asyncio.run(main())
