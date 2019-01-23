import json
import socket
import TCP_socket_attributes as tcpAttr


class MasterServer:

    def __init__(self):
        self.s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.init_connection()
        self.send_man()

    def init_connection(self):
        self.s.connect((tcpAttr.master_client_attributes['TCP_IP'], tcpAttr.master_client_attributes['TCP_PORT']))
        data = self.s.recv(tcpAttr.master_client_attributes['BUFFER_SIZE'])
        if not data or data.decode("utf-8") != tcpAttr.master_client_attributes['HANDSHAKE_MESSAGE'][0]:
            raise ConnectionError

    def close_connection(self):
        self.s.close()

    def send_man(self):
        with open('manifest.json', 'r') as manifest:
            man = manifest.read()
        self.s.send(man.encode('utf-8'))
        data = self.s.recv(tcpAttr.master_client_attributes['BUFFER_SIZE'])
        if not data or data.decode("utf-8") != tcpAttr.master_client_attributes['HANDSHAKE_MESSAGE'][1]:
            raise ConnectionError

    def get_man(self):
        self.s.send('man'.encode('utf-8'))
        data = self.s.recv(tcpAttr.master_client_attributes['BUFFER_SIZE'])
        if not data:
            raise ValueError
        return data.decode("utf-8")

    @staticmethod
    def get_self_man():
        with open('manifest.json', 'r') as manifest:
            man = manifest.read()
        return json.loads(man)
