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


class SkeletonDirectionGetter:
    def __init__(self):
        self.hand = None
        self.angle_kinect2 = 90
        self.kinect_id = 1

    @staticmethod
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

    def init_angle_kinect2(self, angle_to_use, hand, body, body2):
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
                angle_to_use = self.angle_body_from_kinect(body, hand)
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
                angle_to_use = self.angle_body_from_kinect(body2, hand)
                print("Init Angle kinect2 = ", angle_to_use)
        except:
            pass
        return angle_to_use

    def best_angle_body_from_kinect(self, body, body2, hand, angle_kinect2, kinect_id):
        try:
            angle_k1 = self.angle_body_from_kinect(body, hand)
            angle_k2 = self.angle_body_from_kinect(body2, hand)
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
            if angle_k1 > 360:
                angle_k1 = 360
            if angle_k2 > 360:
                angle_k2 = 360
            if body2.HandLeftState == HandState.OPEN.value or body2.HandRightState == HandState.OPEN.value:
                return angle_k2
            else:
                return angle_k1
        except:
            pass

    @staticmethod
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

            angle = np.degrees(np.arcsin(x_h / alpha_h)) * 2 - 10
            if z_p > z_h:
                angle = 90 + (100 - angle)
            return angle
        return None

    @staticmethod
    def transform(data):
        if data is None:
            return None  # "Kinect: server probably down"
        try:
            str_data = data.decode("utf-8")
            if str_data.__contains__('None'):
                return 'None'
            if str_data.count(str_data[0:30]) > 1:
                str_data = str_data[:str_data.rfind(str_data[0:30])]
            return json.loads(str_data, object_hook=lambda d: namedtuple('X', d.keys())(*d.values()))
        except:
            return None  # "Kinect: Format reçu anormal."

    def get_direction_from_skeleton(self, json_body, json_body2):
        try:
            body = self.transform(json_body)
            body2 = self.transform(json_body2)

            self.hand, self.kinect_id = self.init_hand_kinect(self.hand, self.kinect_id, body, body2)
            angle_kinect2 = self.init_angle_kinect2(self.angle_kinect2, self.hand, body, body2)
            return self.best_angle_body_from_kinect(body, body2, self.hand, angle_kinect2, self.kinect_id)
        except:
            print('error happened')
            return None
