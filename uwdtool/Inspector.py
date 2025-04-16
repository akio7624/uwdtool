import os
from typing import Optional

from .Common import print_err, to_hex, sizeof_fmt
from .UnityWebData import UnityWebData


class Inspector:
    def __init__(self, path: Optional[str], compression: str):
        if path is None:
            print_err(f"input path is None")

        self.path = path
        self.compression = compression

    def inspect(self):
        if not os.path.isfile(self.path):
            print_err(f"Path '{self.path}' is not a file")

        file = UnityWebData()
        data = file.load(self.path, self.compression)

        print(f"** Dump of '{self.path}'")
        print()
        print(f"File Signature: {file.SIGNATURE.replace('\0', '\\0')}")
        print(f"Beginning Offset: {file.BEGINNING_OFFSET} (" + to_hex(file.BEGINNING_OFFSET, 8) + ")")
        print()

        for idx, info in enumerate(file.FILE_INFO):
            print(f"File #{idx}")
            print(f"Name: {info.name}")
            print(f"Offset: {info.offset} (" + to_hex(info.offset, 8) + ")")
            size_human = sizeof_fmt(info.length)
            print(f"Length: {info.length} ({size_human})")
            print()

        data.close()