from dataclasses import dataclass

from BinaryReader import BinaryReader
from Common import print_err


@dataclass
class FILE:
    offset: int
    length: int
    name_size: int
    name: str


class UnityWebData:
    def __init__(self):
        self.SIGNATURE: str = ""
        self.BEGINNING_OFFSET: int = -1
        self.FILE_INFO: list[FILE] = list()

    def load(self, path):
        file: BinaryReader = BinaryReader(path)

        self.SIGNATURE = file.read_string(16)
        if self.SIGNATURE != "UnityWebData1.0\0":
            print_err("File is not a UnityWebData file")

        self.BEGINNING_OFFSET = file.read_uint32()

        while file.tell() < self.BEGINNING_OFFSET:
            offset = file.read_uint32()
            length = file.read_uint32()
            name_length = file.read_uint32()
            name = file.read_string(name_length)

            self.FILE_INFO.append(FILE(
                offset=offset,
                length=length,
                name_size=name_length,
                name=name
            ))

        return file
