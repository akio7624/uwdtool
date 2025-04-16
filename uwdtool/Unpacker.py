import os
from typing import Optional

from .Common import print_err
from .UnityWebData import UnityWebData


class Unpacker:
    def __init__(self, input_path: Optional[str], output_path: Optional[str], compression: str):
        if input_path is None:
            print_err(f"input path is None")
        elif not os.path.isfile(input_path):
            print_err(f"input path '{input_path}' is not a file")

        if output_path is None:
            output_path = os.path.join(os.getcwd(), "output")
        elif os.path.isfile(output_path):
            print_err(f"input path '{input_path}' is not a directory")

        self.INPUT_PATH: str = input_path
        self.OUTPUT_PATH: str = output_path
        self.compression = compression

        os.makedirs(self.OUTPUT_PATH, exist_ok=True)

    def unpack(self):
        print("Start unpacking...")

        uwd = UnityWebData()
        reader = uwd.load(self.INPUT_PATH, self.compression)

        print(f"Extract '{self.INPUT_PATH}' to '{self.OUTPUT_PATH}'")

        for idx, info in enumerate(uwd.FILE_INFO):
            name = info.name
            data = info.data

            file_output_path = os.path.join(self.OUTPUT_PATH, name)
            os.makedirs(os.path.dirname(file_output_path), exist_ok=True)

            with open(file_output_path, "wb") as f:
                print(f"Extract {name}...", end="")
                f.write(data)
                print("ok")

        reader.close()
        print("Extract end")