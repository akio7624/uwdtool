import os
from typing import Optional

from Common import print_err
from UnityWebData import UnityWebData


class UnPacker:
    def __init__(self, input_path: Optional[str], output_path: Optional[str]):
        if input_path is None:
            print_err(f"input path is None")
        elif output_path is None:
            print_err(f"output path is None")
        elif not os.path.isfile(input_path):
            print_err(f"input path '{input_path}' is not a file")
        elif not os.path.isdir(output_path):
            print_err(f"output path '{output_path}' is not a directory")

        self.INPUT_PATH: str = input_path
        self.OUTPUT_PATH: str = output_path

    def unpack(self):
        print("Start unpacking...")

        uwd = UnityWebData()
        file = uwd.load(self.INPUT_PATH)

        if self.OUTPUT_PATH is None:
            self.OUTPUT_PATH = os.path.join(os.getcwd(), "output")
        os.makedirs(self.OUTPUT_PATH, exist_ok=True)
        print(f"Extract {self.INPUT_PATH} to {self.OUTPUT_PATH}")

        for info in uwd.FILE_INFO:
            offset = info["offset"]
            length = info["length"]
            name = info["name"]

            file.seek(offset)
            data = file.read_bytes(length)

            file_output_path = os.path.join(self.OUTPUT_PATH, name)
            os.makedirs(os.path.dirname(file_output_path), exist_ok=True)

            with open(file_output_path, "wb") as f:
                print(f"Extract {name}...", end="")
                f.write(data)
                print("ok")

        file.close()
        print("Extract end")