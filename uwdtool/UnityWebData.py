from dataclasses import dataclass

from .BinaryReader import BinaryReader
from .Common import print_err


@dataclass
class FILE:
    offset: int
    length: int
    name_size: int
    name: str
    data: bytearray


class UnityWebData:
    def __init__(self):
        self.SIGNATURE: str = ""
        self.BEGINNING_OFFSET: int = -1
        self.FILE_INFO: list[FILE] = list()

    def load(self, path: str, compression: str) -> BinaryReader:
        reader: BinaryReader = BinaryReader(path)

        self.SIGNATURE = reader.read_string(16)
        if self.SIGNATURE != "UnityWebData1.0\0":
            print_err("File is not a UnityWebData file")

        self.BEGINNING_OFFSET = reader.read_uint32()

        while reader.tell() < self.BEGINNING_OFFSET:
            offset = reader.read_uint32()
            length = reader.read_uint32()
            name_size = reader.read_uint32()
            name = reader.read_string(name_size)

            self.FILE_INFO.append(FILE(
                offset=offset,
                length=length,
                name_size=name_size,
                name=name,
                data=bytearray()
            ))

        for idx, file in enumerate(self.FILE_INFO):
            reader.seek(file.offset)
            self.FILE_INFO[idx].data = reader.read_bytes(file.length)

        return reader
