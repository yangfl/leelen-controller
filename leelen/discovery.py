from enum import Enum
import socket
import threading


__all__ = ['DeviceType', 'Discovery']


# voip/getpeeripthread.h
class DeviceType(Enum):
    UNKNOWN     = 0,
    BASIC       = 1 << 0  # E60/E75
    THIN        = 1 << 1  # E26
    DOORWAY_3_5 = 1 << 2  # 10型
    DOORWAY_10  = 1 << 3  # 1型
    MANCENTER   = 1 << 4  # 管理机
    DOORWAY_8   = 1 << 5  # 8型
    IP_SWITCH   = 1 << 6
    DOORWAY_4   = 1 << 7  # 4型
    DOORWAY_16  = 1 << 8  # 16型


# voip/getpeeripthread.cpp
class Discovery(threading.Thread):
    groupaddr = '224.0.0.1'

    def __init__(self, number, addr, device_type=DeviceType.BASIC,
                 desc='AK01-FJV31001-V0.01-V11.38_20180410', port=6789,
                 timeout=0.2) -> None:
        self.number = number
        self.addr = addr
        self.device_type = device_type
        self.desc = desc

        self.port = port
        self.timeout = timeout
        self.socket = None
        self._stopped = False

        self._last_addr = None
        self._last_addr_got = threading.Condition()

    @property
    def reply(self) -> str:
        return f'{self.addr}?{int(self.device_type)}*{self.desc}'

    def bind(self) -> None:
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.socket.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
        self.socket.bind(('0.0.0.0', self.port))

    def run(self) -> None:
        if self.socket is None:
            self.bind()
        while not self._stopped:
            data, addr = self.socket.recvfrom(1500)
            if not data:
                continue
            if data == bytes(self.number):
                # reply
                self.socket.sendto(self.reply.encode(), addr)
                continue
            msg = data.decode()
            if '?' in msg:
                # save addr
                self._last_addr = msg.split('?', 1)[0]
                with self._last_addr_got:
                    self._last_addr_got.notify()

    def stop(self) -> None:
        self._stopped = True
        self.socket.close()

    def discover(self, number):
        self.socket.sendto(
            str(number).encode(), (self.groupaddr, self.port))
        with self._last_addr_got:
            self._last_addr_got.wait(self.timeout)
        return self._last_addr
