from struct import Struct
from typing import NamedTuple


class Req0109(NamedTuple):
    position: int = 4

    struct = Struct('<B')
    len = struct.size

    @classmethod
    def unpack(cls, buffer: bytes):
        body = cls.struct.unpack(buffer)
        return cls.__new__(cls, body[0])

    def pack(self) -> bytes:
        return self.struct.pack(self.position)


types = {
    0x0109: (Req0109, None),
}
