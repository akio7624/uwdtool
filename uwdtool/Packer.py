import hashlib
import io
import os
import struct
from io import BytesIO
from typing import Optional, BinaryIO

from .Common import print_err, sizeof_fmt
from .CompressionManager import compress_gzip


class Packer:
    def __init__(self, input_path: Optional[str], output_path: Optional[str], compression: str):
        if input_path is None:
            print_err(f"input path is None")
        elif not os.path.isdir(input_path):
            print_err(f"input path '{input_path}' is not a directory")

        if output_path is None:
            print_err(f"input path is None")

        self.INPUT_PATH: str = input_path
        self.OUTPUT_PATH: str = output_path
        self.compression = compression

    def pack(self):
        print("Start packing...")

        os.makedirs(os.path.dirname(self.OUTPUT_PATH), exist_ok=True)

        print(f"Pack files in {self.INPUT_PATH} to {self.OUTPUT_PATH}")

        files: list[str] = list()
        for dir_path, dir_names, file_names in os.walk(self.INPUT_PATH):
            files += [os.path.join(dir_path, file_name) for file_name in file_names]

        target_path: list[tuple[str, str]] = list()
        for full_path in files:
            rel_path = os.path.normpath(os.path.relpath(full_path, self.INPUT_PATH)).replace("\\", "/")
            target_path.append((full_path, rel_path))

        header_length = 16 + 4  # length of signature and beginning of file area field

        # calculate file info area
        for _, rel_path in target_path:
            header_length += 4  # length of file offset field
            header_length += 4  # length of file size field
            header_length += 4  # length of file name length field
            header_length += len(rel_path.encode("utf-8"))  # length of file name

        bio: BytesIO = io.BytesIO()
        bio.write(b'UnityWebData1.0\x00')  # write signature bytes
        bio.write(struct.pack("<I", header_length))  # write beginning of file area field

        file_offset = header_length
        for source_path, rel_path in target_path:
            file_size = os.path.getsize(source_path)

            bio.write(struct.pack("<I", file_offset))  # write file offset field
            bio.write(struct.pack("<I", file_size))  # write file size field
            bio.write(struct.pack("<I", len(rel_path.encode("utf-8"))))  # write length of file name field
            bio.write(rel_path.encode("utf-8"))  # write file name field

            file_offset += file_size

        # write real file contents
        for source_path, rel_path in target_path:
            print(f"Add file {rel_path}...", end="")
            with open(source_path, "rb") as f:
                bio.write(f.read())
            print("ok")

        final_data: Optional[bytes]
        if self.compression == "none" or self.compression == "auto":
            print(f"Not compressing")
            final_data = bio.getvalue()
        else:
            print(f"Compress as {self.compression}...")
            if self.compression == "brotli":
                pass  # TODO
            elif self.compression == "gzip":
                final_data = compress_gzip(bio.getvalue())
            else:
                print_err(f"Unsupported compression '{self.compression}'")

        bio.close()

        with open(self.OUTPUT_PATH, "wb") as f:
            f.write(final_data)

        total_size = os.path.getsize(self.OUTPUT_PATH)
        print("Packing ended successfully!")
        print(f"Total Size: {total_size}bytes ({sizeof_fmt(total_size)})")
        md5 = hashlib.md5(open(self.OUTPUT_PATH, "rb").read()).hexdigest()
        print(f"MD5 checksum: {md5}")