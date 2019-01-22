import os
import sys
import inspect
import socket
import select
import threading

import TCP_socket_attributes as tcpAttr
import master_server_communication

src_dir = os.path.dirname(inspect.getfile(inspect.currentframe()))

# Windows and Linux
# arch_dir = '../lib/x64' if sys.maxsize > 2**32 else '../lib/x86'
# Mac
arch_dir = os.path.abspath(os.path.join(src_dir, './lib'))

sys.path.insert(0, os.path.abspath(os.path.join(src_dir, arch_dir)))

import Leap


def main():
    master_server_communication.init_connection()
    master_server_communication.send_man()
    listener = LeapVolumeControlSocketServer()
    controller = Leap.Controller()
    controller.add_listener(listener)

    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.bind((tcpAttr.leap_server_attributes['TCP_IP'], tcpAttr.leap_server_attributes['TCP_PORT']))
    s.listen(tcpAttr.leap_server_attributes['MAX_QUEUED_CONNECTION'])
    t_accept = threading.Thread(target=LeapVolumeControlSocketServer.server_socket_worker, args=(listener, s,))
    t_send = threading.Thread(target=LeapVolumeControlSocketServer.send_to_client_worker, args=(listener,))

    try:
        t_accept.start()
        t_send.start()
        t_accept.join()
        t_send.join()
    except KeyboardInterrupt:
        pass
    finally:
        master_server_communication.close_connection()
        s.close()


class LeapVolumeControlSocketServer(Leap.Listener):

    def __init__(self):
        self.volumePercent = 50
        self.previousVolumePercent = self.volumePercent
        self.volumeStep = 5
        self.previous_circle_progress = 0
        self.connected_sockets = []
        self.message_to_send_condition = threading.Condition()
        self.message_to_send = ""
        Leap.Listener.__init__(self)

    def on_init(self, controller):
        print("Initialized")
        Leap.Listener.on_init(self, controller)

    def on_exit(self, _):
        print("Exited")
        # Leap.Listener.on_exit(self, controller) # causes segfault

    def on_connect(self, controller):
        print("connect")
        controller.enable_gesture(Leap.Gesture.TYPE_CIRCLE)
        # controller.config.set("Attribut-Voulu", valeur)
        # controller.config.save()
        Leap.Listener.on_connect(self, controller)

    def on_disconnect(self, controller):
        print("disconnect")
        for s in self.connected_sockets:
            s.close()
        Leap.Listener.on_disconnect(self, controller)

    def on_frame(self, controller):
        # print("Frame available")
        frame = controller.frame()
        for gesture in frame.gestures():
            if gesture.type is not Leap.Gesture.TYPE_CIRCLE:
                continue
            if gesture.state is Leap.Gesture.STATE_STOP:
                self.previous_circle_progress = 0
                continue

            circle = Leap.CircleGesture(gesture)
            clockwise = circle.pointable.direction.angle_to(circle.normal) <= Leap.PI/2
            value = self.volumeStep if clockwise else -self.volumeStep
            coef = circle.progress - self.previous_circle_progress
            value *= abs(coef)

            self.previous_circle_progress = circle.progress
            self.volumePercent += value

            if self.volumePercent < 0:
                self.volumePercent = 0
            elif self.volumePercent > 100:
                self.volumePercent = 100

            # print("Volume = {} %".format(self.volumePercent))
            if self.volumePercent != self.previousVolumePercent:
                self.send_to_client()
                self.previousVolumePercent = self.volumePercent
        Leap.Listener.on_frame(self, controller)

    def send_to_client(self):
        with self.message_to_send_condition:
            self.message_to_send = '{{"volume": {}}}'.format(self.volumePercent).encode()
            self.message_to_send_condition.notifyAll()

    def send_to_client_worker(self):
        while True:
            with self.message_to_send_condition:
                self.message_to_send_condition.wait()
                _, writable, exceptional = select.select([], self.connected_sockets, self.connected_sockets, 0.01)
                for s in writable:
                    try:
                        s.sendall(self.message_to_send)
                    except socket.error:
                        exceptional.append(s)
            for s in exceptional:
                self.connected_sockets.remove(s)
                print("closed socket {}".format(s))
                s.close()

    def server_socket_worker(self, server_socket):
        while True:
            conn, addr = server_socket.accept()
            print("connected socket {}, {}".format(conn, addr))
            conn.setblocking(False)
            self.connected_sockets.append(conn)


if __name__ == "__main__":
    main()
