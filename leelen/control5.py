from datetime import datetime
from struct import Struct
from typing import NamedTuple


class Ack0501(NamedTuple):
    max_len: int = 1200
    version: str = ''

    struct = Struct('<BHB')

    @property
    def len(self) -> int:
        return self.struct.size + len(self.version)

    @classmethod
    def unpack(cls, buffer: bytes):
        body = cls.struct.unpack(buffer[:cls.struct.size])
        if body[2] != len(buffer) - cls.struct.size:
            raise ValueError(
                f'version_len error, expect {len(buffer) - cls.struct.size}, '
                f'got {body[2]}')

        return cls.__new__(cls, body[1], buffer[cls.struct.size:].decode())

    def pack(self) -> bytes:
        return self.struct.pack(1, self.max_len, len(self.version)) + \
               self.version.encode()


class Ack0502(NamedTuple):
    time: datetime

    struct = Struct('<8B')
    len = struct.size

    @classmethod
    def unpack(cls, buffer: bytes):
        body = cls.struct.unpack(buffer)
        return cls.__new__(cls, datetime(
            body[1] * 100 + body[2], body[3], body[4],
            body[5], body[6], body[7]))

    def pack(self) -> bytes:
        dt = self.time
        return self.struct.pack(
            1, *divmod(dt.year, 100), dt.month, dt.day,
            dt.hour, dt.minute, dt.second)


types = {
    0x0501: (None, Ack0501),
    0x0502: (None, Ack0502),
}
