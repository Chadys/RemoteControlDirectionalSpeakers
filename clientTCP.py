import socket
import TCP_socket_attributes as tcpAttr


s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
# s.connect((tcpAttr.leap_server_attributes['TCP_IP'], tcpAttr.leap_server_attributes['TCP_PORT']))
s.connect((tcpAttr.middleware_server_attributes['TCP_IP'], tcpAttr.middleware_server_attributes['TCP_PORT']))
# s.send(tcpAttr.master_client_attributes['HANDSHAKE_MESSAGE'][0].encode('utf-8'))
# s.send(tcpAttr.master_client_attributes['HANDSHAKE_MESSAGE'][0].encode('utf-8'))
while True:
    data = s.recv(tcpAttr.master_client_attributes['BUFFER_SIZE'])
    if not data:
        break
    print(data)
# data = s.recv(tcpAttr.master_client_attributes['BUFFER_SIZE'])
# print(data)
# s.send("{}".encode('utf-8'))
# data = s.recv(tcpAttr.master_client_attributes['BUFFER_SIZE'])
# print(data)
# data = s.recv(tcpAttr.master_client_attributes['BUFFER_SIZE'])
# print(data)
s.close()
