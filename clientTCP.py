import socket
import TCP_socket_attributes as tcpAttr


s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.connect(('0.0.0.0', 6543))  #8888 #6543
s.send(tcpAttr.module_directory_attributes['HANDSHAKE_MESSAGE'][0].encode('utf-8'))
s.send(tcpAttr.module_directory_attributes['HANDSHAKE_MESSAGE'][0].encode('utf-8'))
data = s.recv(tcpAttr.module_directory_attributes['BUFFER_SIZE'])
print(data)
data = s.recv(tcpAttr.module_directory_attributes['BUFFER_SIZE'])
print(data)
s.send(tcpAttr.module_directory_attributes['HANDSHAKE_MESSAGE'][1].encode('utf-8'))
data = s.recv(tcpAttr.module_directory_attributes['BUFFER_SIZE'])
print(data)
data = s.recv(tcpAttr.module_directory_attributes['BUFFER_SIZE'])
print(data)
s.close()
