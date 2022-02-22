from .control import *
from .discovery import *
from .number import *

import socket


def control(ip: str, buffer: bytes, timeout: float=0.2) -> bytes:
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
    sock.settimeout(timeout)
    sock.connect((ip, 17722))
    sock.send(buffer)
    return sock.recv(1500)
