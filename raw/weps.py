import socket
import sys
import random

UDP_IP = sys.argv[1]
UDP_PORT = 5001


print("Spewing to {}:{}, {} bytes per packet".format(UDP_IP, UDP_PORT,
                                                     MESSAGE_LEN))

sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
sock.bind(UDP_IP, UDP_PORT)

while True:
    data, addr = sock.recvfrom(1024)
    print("recieved message ", data)
