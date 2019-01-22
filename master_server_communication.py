import socket
import TCP_socket_attributes as tcpAttr

master_server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)


def init_connection():
    master_server_socket.connect((tcpAttr.master_client_attributes['TCP_IP'], tcpAttr.master_client_attributes['TCP_PORT']))
    data = master_server_socket.recv(tcpAttr.master_client_attributes['BUFFER_SIZE'])
    if not data or data.decode("utf-8") != tcpAttr.master_client_attributes['HANDSHAKE_MESSAGE'][0]:
        raise ConnectionError


def close_connection():
    master_server_socket.close()


def send_man():
    with open('manifest.json', 'r') as manifest:
        man = manifest.read()
    master_server_socket.send(man.encode('utf-8'))
    data = master_server_socket.recv(tcpAttr.master_client_attributes['BUFFER_SIZE'])
    if not data or data.decode("utf-8") != tcpAttr.master_client_attributes['HANDSHAKE_MESSAGE'][1]:
        raise ConnectionError


def get_man():
    master_server_socket.send('man'.encode('utf-8'))
    data = master_server_socket.recv(tcpAttr.master_client_attributes['BUFFER_SIZE'])
    if not data:
        raise ValueError
    return data.decode("utf-8")
