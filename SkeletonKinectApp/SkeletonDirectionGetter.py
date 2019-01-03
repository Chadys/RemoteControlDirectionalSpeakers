import socket
import TCP_socket_attributes as tcpAttr


def main():
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.connect((tcpAttr.kinect1_server_attributes['TCP_IP_DIRECTION'],
                   tcpAttr.kinect1_server_attributes['TCP_PORT_DIRECTION']))

        while True:
            data = s.recv(tcpAttr.kinect1_server_attributes['BUFFER_SIZE'])
            if not data:
                break
            print(data)
    except KeyboardInterrupt:
        pass
    finally:
        pass


if __name__ == "__main__":
    main()
