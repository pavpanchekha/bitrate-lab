import socket
import sys
import random

UDP_IP = sys.argv[1]
UDP_PORT = 5001
MESSAGE_LEN = 1500 - 64

print("Spewing to {}:{}, {} bytes per packet".format(UDP_IP, UDP_PORT,
                                                     MESSAGE_LEN))

sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

i = 0
while True:
    PREFIX = "Seq {}\n".format(i).encode("utf-8")
    MESSAGE = PREFIX + bytes(random.randint(0, 255) for i in range(MESSAGE_LEN - len(PREFIX)))
    sock.sendto(MESSAGE, (UDP_IP, UDP_PORT))
    i += 1
