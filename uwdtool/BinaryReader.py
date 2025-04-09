import struct


class BinaryReader:
    def __init__(self, path):
        self.file = open(path, "rb")

    def read_string(self, size=None):
        if size is None:
            pass
        else:
            return self.file.read(size).decode('utf-8')

    def read_int(self):
        return struct.unpack("<I", self.file.read(4))[0]

    def tell(self):
        return self.file.tell()

    def seek(self, pos):
        self.file.seek(pos)

    def read_bin(self, size=1):
        return self.file.read(size)

    def close(self):
        self.file.close()