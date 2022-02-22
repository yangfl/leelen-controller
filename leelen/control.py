from enum import Enum
from random import randint
from struct import Struct
from typing import Any, NamedTuple

from .number import Number
from . import control1
from . import control5


__all__ = ['ControlCommand', 'ControlMessage']


# protocol/leelen_interface.h
class ControlCommand(Enum):
    SAVE_SECURITY_RECORD  = 0x0001  # 保存布撤防记录
    REMOTE_ARMING         = 0x0002  # 远程布撤防
    UPLOAD_SECURITY_ALERT = 0x0003  # 防区报警信息上传
    EMERGENCY_HELP        = 0x0004  # 保存求助信息

    DOWNLOAD_CARD          = 0x0101  # 保存单张卡记录
    DELETE_CARD            = 0x0102  # 删除卡
    DELETE_USER_CARDS      = 0x0103  # 删除某户卡
    DELETE_PATROL_CARDS    = 0x0104  # 删除全部保安卡
    DELETE_ALL_CARDS       = 0x0105  # 删除主机所有卡
    UPLOAD_CARD_RECORD     = 0x0106  # 刷卡记录上传
    UPLOAD_PASSWORD_RECORD = 0x0107  # 密码开锁记录上传
    UPLOAD_LOCK_RECORD     = 0x0108  # 门状态信息上传
    REMOTE_UNLOCK          = 0x0109  # 远程开锁
    UPLOAD_PATROL_RECORD   = 0x010a  # 巡更刷卡信息上传

    CALL_LIFT                  = 0x0201  # 呼梯
    CALL_LIFT_WITH_DESTINATION = 0x0202  # 户户互访梯控呼梯
    CALL_LIFT_BY_CARD          = 0x0203  # 刷卡梯控
    GET_SET_LIFT_INFO          = 0x0204  # 获取/设置当前电梯信息状态

    WRITE_TALK_RECORD = 0x0301  # 保存呼叫记录

    FILE_DELETE    = 0x0401  # 删除文件
    FILE_SCAN      = 0x0402  # 文件扫描获取要求路径下所有文件
    FILE_MKDIR     = 0x0403  # 创建目录
    FILE_RENAME    = 0x0404  # 重命名
    FILE_CHECKSIZE = 0x0405  # 检查系统存储空间和内存大小是否满足要求
    FILE_CHECKFILE = 0x0406  # 检查文件是否存在

    GET_SET_VERSION_INFO    = 0x0501  # 获取/设置协议版本等信息
    GET_SET_DATETIME        = 0x0502  # 获取/设置系统时间
    WRITE_DEVICE_RECORD     = 0x0503  # 设备异常报警记录
    WRITE_INFO              = 0x0504  # 收到信息

    READ_WRITE_BIG_DATA = 0x0601  # 读取大数据


class ControlBodyNone(NamedTuple):
    len = 0

    @classmethod
    def unpack(cls, buffer: bytes):
        return cls.__new__(cls)

    def pack(self) -> bytes:
        return b''


# protocol/core/leelen_packet.h
class ControlMessage(NamedTuple):
    protocol_version: int = 0x0301
    command: ControlCommand = None
    id: int = None
    is_ack: bool = False
    is_encrypt: bool = False
    src: Number = None
    dst: Number = None
    body: Any = None

    head_struct = Struct('<3BHHI??I5B5B')
    body_types = control1.types | control5.types
    tail_struct = Struct('<HB')

    @classmethod
    def unpack(cls, buffer: bytes):
        header = cls.head_struct.unpack(buffer[:cls.head_struct.size])
        if header[0] != 0xd1 or header[1] != 0xd2 or header[2] != 0xd5:
            raise ValueError('header error, expect 0xd1d2d5, got 0x' +
                             ''.join(str(i) for i in header[0:3]))
        if header[8] != len(buffer):
            raise ValueError(f'len error, expect {len(buffer)}, '
                             f'got {header[8]}')
        body_types = cls.body_types.get(header[4], None)
        if body_types is None:
            raise ValueError(f'unknown body type error {hex(header[4])}')

        tail = cls.tail_struct.unpack(buffer[-cls.tail_struct.size:])
        cksum = cls.checksum(buffer[:-1])
        if tail[1] != cksum:
            raise ValueError(f'checksum error, expect {hex(cksum)}, '
                             f'got {hex(tail[1])}')

        return cls.__new__(
            cls, header[3], ControlCommand(header[4]), header[5], header[6],
            header[7], Number(header[9:14]), Number(header[14:19]),
            (body_types[header[6]] or ControlBodyNone).unpack(
                buffer[cls.head_struct.size:-cls.tail_struct.size]))

    @property
    def len(self) -> int:
        return self.head_struct.size + self.body.len + self.tail_struct.size

    def _pack(self, reversed=b'\xff\xff') -> bytes:
        return b''.join([self.head_struct.pack(
            0xd1, 0xd2, 0xd5, self.protocol_version, self.command.value,
            self.id, self.is_ack, self.is_encrypt, self.len, *bytes(self.src),
            *bytes(self.dst)
        ), self.body.pack(), reversed])

    @staticmethod
    def checksum(buffer: bytes) -> int:
        return 0x100 - sum(buffer) & 0xff

    def pack(self, reversed=b'\xff\xff') -> bytes:
        data = self._pack(reversed)
        data += bytes([self.checksum(data)])
        return data
