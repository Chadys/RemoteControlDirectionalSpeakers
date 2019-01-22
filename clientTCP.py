import socket
import TCP_socket_attributes as tcpAttr


s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.connect((tcpAttr.joystick_server_attributes['TCP_IP'], tcpAttr.joystick_server_attributes['TCP_PORT']))

while True:
    data = s.recv(tcpAttr.master_client_attributes['BUFFER_SIZE'])
    if not data:
        break
    print(data)
