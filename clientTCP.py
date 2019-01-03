import socket
import TCP_socket_attributes as tcpAttr


s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.connect((tcpAttr.webapp_server_attributes['TCP_IP_DIRECTION'], tcpAttr.webapp_server_attributes['TCP_PORT_DIRECTION']))

while True:
    data = s.recv(tcpAttr.master_client_attributes['BUFFER_SIZE'])
    if not data:
        break
    print(data)
