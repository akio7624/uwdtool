import argparse
import struct
import os
import hashlib
from glob import glob
from pathlib import Path


UWDT_VERSION = "1.1.0"
HELP_STR = f"""UWDTool v{UWDT_VERSION}"""


class UWDTException(Exception):
    def __init__(self, msg):
        self.msg = msg

    def __str__(self):
        return self.msg


class BinaryReader:
    file = None

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


class UnityWebData:
    SIGNATURE = None
    BEGINNING_OFFSET = None
    FILE_INFO = []

    def load(self, path):
        file = BinaryReader(path)

        self.SIGNATURE = file.read_string(16)
        if self.SIGNATURE != "UnityWebData1.0\0":
            raise UWDTException("File is not a UnityWebData file")

        self.BEGINNING_OFFSET = file.read_int()

        while file.tell() < self.BEGINNING_OFFSET:
            offset = file.read_int()
            length = file.read_int()
            name_length = file.read_int()
            name = file.read_string(name_length)

            self.FILE_INFO.append({
                "offset": offset,
                "length": length,
                "name_length": name_length,
                "name": name
            })
        return file


class Packer:
    input_path = None
    output_path = None

    def pack(self, input_path, output_path):
        print("Start packing...")
        self.input_path = input_path
        self.output_path = output_path

        if self.input_path is None:
            raise UWDTException(f"input path is None")
        if not os.path.isdir(self.input_path):
            raise UWDTException(f"input path {self.input_path} is not a directory")
        if self.output_path is None:
            raise UWDTException(f"output path is None")

        os.makedirs(Path(self.output_path).parent.absolute(), exist_ok=True)

        print(f"Pack files in {self.input_path} to {self.output_path}")

        files = [y for x in os.walk(self.input_path) for y in glob(os.path.join(x[0], '*'))]
        targets_ = [x for x in files if os.path.isfile(x)]
        targets = []
        for target in targets_:
            if self.input_path.endswith("/"):
                targets.append(target[len(self.input_path):].replace("\\", "/"))
            else:
                targets.append(target[len(self.input_path)+1:].replace("\\", "/"))

        OUTPUT = open(self.output_path, "wb")

        OUTPUT.write(bytes("UnityWebData1.0\0", "utf-8"))

        header_length = 0
        for file_name in targets:
            header_length += (4 + 4 + 4 + len(bytes(file_name, "utf-8")))

        OUTPUT.write(struct.pack("<i", 20+header_length))

        file_offset = 20+header_length
        for file_name in targets:
            OUTPUT.write(struct.pack("<i", file_offset))
            file_size = os.path.getsize(os.path.join(self.input_path, file_name))
            file_offset += file_size
            OUTPUT.write(struct.pack("<i", file_size))
            OUTPUT.write(struct.pack("<i", len(bytes(file_name, "utf-8"))))
            OUTPUT.write(bytes(file_name, "utf-8"))

        for file_name in targets:
            print(f"Add file {file_name}...", end="")
            with open(os.path.join(self.input_path, file_name), "rb") as f:
                OUTPUT.write(f.read())
            print("ok")

        OUTPUT.close()

        total_size = os.path.getsize(self.output_path)
        print("Packing ended successfully!")
        print(f"Total Size: {total_size}bytes ({Inspector().sizeof_fmt(total_size)})")
        md5 = hashlib.md5(open(self.output_path, "rb").read()).hexdigest()
        print(f"MD5 checksum: {md5}")


class UnPacker:
    input_path = None
    output_path = None

    def unpack(self, input_path, output_path):
        print("Start unpacking...")
        self.input_path = input_path
        self.output_path = output_path

        if self.input_path is None:
            raise UWDTException(f"input path is None")
        if not os.path.isfile(self.input_path):
            raise UWDTException(f"input path {self.input_path} is not a file")

        uwd = UnityWebData()
        file = uwd.load(self.input_path)

        if self.output_path is None:
            self.output_path = os.path.join(os.getcwd(), "output")
        os.makedirs(self.output_path, exist_ok=True)
        print(f"Extract {self.input_path} to {self.output_path}")

        for info in uwd.FILE_INFO:
            offset = info["offset"]
            length = info["length"]
            name = info["name"]

            file.seek(offset)
            data = file.read_bin(length)

            file_output_path = os.path.join(self.output_path, name)
            os.makedirs(os.path.dirname(file_output_path), exist_ok=True)

            with open(file_output_path, "wb") as f:
                print(f"Extract {name}...", end="")
                f.write(data)
                print("ok")

        file.close()
        print("Extract end")


class Inspector:
    path = None

    def sizeof_fmt(self, num, suffix="B"):
        for unit in ["", "Ki", "Mi", "Gi", "Ti", "Pi", "Ei", "Zi"]:
            if abs(num) < 1024.0:
                return f"{num:3.1f}{unit}{suffix}"
            num /= 1024.0
        return f"{num:.1f}Yi{suffix}"

    def inspect(self, path):
        self.path = path
        file = UnityWebData()
        data = file.load(self.path)

        print(f"** Dump of {self.path}")
        print("")
        print(f"File Signature: {file.SIGNATURE}")
        print(f"Beginning Offset: {file.BEGINNING_OFFSET}")
        print("")

        for idx, info in enumerate(file.FILE_INFO):
            print(f"File #{idx}")
            print(f"Name: {info['name']}")
            print(f"Offset: {info['offset']}")
            size_h = self.sizeof_fmt(info['length'])
            print(f"Length: {info['length']} ({size_h})")
            print("")

        data.close()


def main():
    parser = argparse.ArgumentParser(
                    prog="uwdtool",
                    description=HELP_STR,
                    formatter_class=argparse.RawTextHelpFormatter)
    g = parser.add_mutually_exclusive_group()

    g.add_argument("-p", "--pack", action="store_true", help="packing files in input-path directory")
    g.add_argument("-u", "--unpack", action="store_true", help="unpacking input-path file to output-path directory")
    g.add_argument("-isp", "--inspect", action="store_true", help="show file information list of input-path file")

    parser.add_argument("-i", dest="ARG_INPUT", help="input path")
    parser.add_argument("-o", dest="ARG_OUTPUT", help="output path")
    args = parser.parse_args()

    if args.pack:
        Packer().pack(args.ARG_INPUT, args.ARG_OUTPUT)
    elif args.unpack:
        UnPacker().unpack(args.ARG_INPUT, args.ARG_OUTPUT)
    elif args.inspect:
        if args.ARG_INPUT is None:
            raise UWDTException("input file option is missing")
        else:
            Inspector().inspect(args.ARG_INPUT)
    else:
        raise UWDTException("Unknown Control Option")


if __name__ == "__main__":
    main()
