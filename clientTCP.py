import socket


TCP_IP = '37.59.57.203'
TCP_PORT = 55555
BUFFER_SIZE = 1024
MESSAGE = ["EHLO", "HELO"]

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.connect((TCP_IP, TCP_PORT))
s.send(MESSAGE[0])
data = s.recv(BUFFER_SIZE)
print(data)
s.send(MESSAGE[1])
data = s.recv(BUFFER_SIZE)
print(data)
s.close()
