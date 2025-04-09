from BinaryReader import BinaryReader


class UnityWebData:
    SIGNATURE = None
    BEGINNING_OFFSET = None
    FILE_INFO = []

    def load(self, path):
        file = BinaryReader(path)

        self.SIGNATURE = file.read_string(16)
        if self.SIGNATURE != "UnityWebData1.0\0":
            raise UWDTException("File is not a UnityWebData file")

        self.BEGINNING_OFFSET = file.read_uint32()

        while file.tell() < self.BEGINNING_OFFSET:
            offset = file.read_uint32()
            length = file.read_uint32()
            name_length = file.read_uint32()
            name = file.read_string(name_length)

            self.FILE_INFO.append({
                "offset": offset,
                "length": length,
                "name_length": name_length,
                "name": name
            })
        return file
