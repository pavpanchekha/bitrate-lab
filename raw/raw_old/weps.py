import socket
import sys
import random

UDP_IP = sys.argv[1]
UDP_PORT = 5001


print("Listening on %r:%r." % (UDP_IP, UDP_PORT))

sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
sock.bind((UDP_IP, UDP_PORT))

while True:
    data, addr = sock.recvfrom(1024)
    print("recieved message ", data)
