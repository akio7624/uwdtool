import hashlib
import os
import struct
from glob import glob
from pathlib import Path

from Common import print_err
from Inspector import Inspector


class Packer:
    input_path = None
    output_path = None

    def pack(self, input_path, output_path):
        print("Start packing...")
        self.input_path = input_path
        self.output_path = output_path

        if self.input_path is None:
            print_err(f"input path is None")
        if not os.path.isdir(self.input_path):
            print_err(f"input path {self.input_path} is not a directory")
        if self.output_path is None:
            print_err(f"output path is None")

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