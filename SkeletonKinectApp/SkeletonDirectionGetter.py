import socket
import TCP_socket_attributes as tcpAttr
import numpy as np
import json
from collections import namedtuple


# def determine_body(bodies):
#     return [body for body in bodies if body.Joints.__contains__(get_higher_joint(body))][0]


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


def main():
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.connect((tcpAttr.kinect1_server_attributes['TCP_IP'],
                   tcpAttr.kinect1_server_attributes['TCP_PORT']))

        while True:
            data = s.recv(tcpAttr.kinect1_server_attributes['BUFFER_SIZE'])
            if not data:
                break
            else:
                body = json.loads(data, object_hook=lambda d: namedtuple('X', d.keys())(*d.values()))
                if type(body) is str:
                    print(body)  # means 'None'
                else:
                    print(get_direction(body))
    except KeyboardInterrupt:
        pass
    finally:
        pass


if __name__ == "__main__":
    main()
