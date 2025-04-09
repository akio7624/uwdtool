import struct
from typing import Optional


class BinaryReader:
    def __init__(self, path: str):
        self.file = open(path, "rb")

    def read_string(self, size: int) -> str:
        return self.file.read(size).decode("utf-8")

    def read_uint32(self) -> int:
        return struct.unpack("<I", self.file.read(4))[0]

    def tell(self) -> int:
        return self.file.tell()

    def seek(self, pos: int):
        self.file.seek(pos)

    def read_bytes(self, size: int = 1) -> bytearray:
        return bytearray(self.file.read(size))

    def close(self):
        self.file.close()
