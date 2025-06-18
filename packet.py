from enum import IntEnum, auto
import struct


class PacketType(IntEnum):
    PING = auto()
    READ_FILE = auto()
    READ_FILE_RESP = auto()
    MUL = auto()


class Packet():
    def __init__(self, p_type: PacketType):
        self.__ptype = p_type

    @property
    def packet_type(self):
        return self.__ptype

    def pack(self) -> bytes:
        return struct.pack('!B', self.packet_type.value)
    
class PingPacket(Packet):
    def __init__(self):
        super().__init__(PacketType.PING)

class ReadFilePacket(Packet):
    def __init__(self, file_path: str):
        super().__init__(PacketType.READ_FILE)
        self.file_path = file_path

    def pack(self) -> bytes:
        b = super().pack()
        b += struct.pack(f'!I{len(self.file_path)}s', len(self.file_path), self.file_path.encode())
        return b
    
class ReadFileRespPacket(Packet):
    def __init__(self, status: int, data: bytes):
        super().__init__(PacketType.READ_FILE_RESP)
        self.status = status
        self.data = data

    def pack(self) -> bytes:
        b = super().pack()
        b += struct.pack(f'!bI{len(self.data)}s', self.status, len(self.data), self.data)
        return b

class MulPacket(Packet):
    def __init__(self, n: int):
        super().__init__(PacketType.MUL)
        self.n = n
    
    def pack(self) -> bytes:
        return super().pack() + struct.pack('!I', self.n)