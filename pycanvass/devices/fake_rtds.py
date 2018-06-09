import socket
from struct import *
import time
import random

clientsocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
clientsocket.connect(('localhost', 8989))
i = 0   
while i < 120:
    # a = bytes([random.randint(4,11)])
    # b = bytes([random.randint(8,99)])
    a = random.randint(54,91)
    print("RTDS Sending Data: {}".format(a))
    msg_from_rtds = pack("!f",a)
    clientsocket.send(msg_from_rtds)
    time.sleep(2)