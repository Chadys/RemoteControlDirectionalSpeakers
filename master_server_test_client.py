import socket
import TCP_socket_attributes as tcpAttr


def display_man(s):
    data = s.recv(tcpAttr.master_client_attributes['BUFFER_SIZE'])
    if not data or data.decode("utf-8") != tcpAttr.master_client_attributes['HANDSHAKE_MESSAGE'][0]:
        return
    s.send('{"coucou":2}'.encode('utf-8'))
    data = s.recv(tcpAttr.master_client_attributes['BUFFER_SIZE'])
    if not data or data.decode("utf-8") != tcpAttr.master_client_attributes['HANDSHAKE_MESSAGE'][1]:
        return
    s.send('man'.encode('utf-8'))
    data = s.recv(tcpAttr.master_client_attributes['BUFFER_SIZE'])
    if not data:
        return
    print(data.decode("utf-8"))


s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.connect((tcpAttr.master_client_attributes['TCP_IP'], tcpAttr.master_client_attributes['TCP_PORT']))
display_man(s)
s.close()