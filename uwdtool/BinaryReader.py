import gzip
import io
import struct

import brotli

from uwdtool.Common import print_err, check_compression


class BinaryReader:
    def __init__(self, path: str, compression: str):
        if compression == "auto":
            compression = check_compression(path)
            print(f"Compression detected: {compression}")

        if compression == "none":
            self.file = open(path, "rb")
        elif compression == "gzip":
            with gzip.open(path, "rb") as f:
                decompressed = f.read()
            self.file = io.BytesIO(decompressed)
        elif compression == "brotli":
            with open(path, 'rb') as f:
                decompressed = brotli.decompress(f.read())
            self.file = io.BytesIO(decompressed)
        else:
            print_err(f"Unknown compression: {compression}")

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
