import math
from typing import Final

UWDT_VERSION = "1.2.0"
HELP_STR = f"""
UWDTool v{UWDT_VERSION}

::Release Notes::
  2025.04.12  v1.2.0 Code refactoring
  2023.06.11  v1.1.0 Fixed Windows path backslash issue
  2023.04.22  v1.0.0 Initial release
  
::Path Arguments::
  In Inspector mode, -i must be a UnityWebData 1.0 file, and -o is not required.
  In Pack mode, -i should be a folder containing the files to be packed, and -o is the path where the UnityWebData file will be saved.
  In Unpack mode, -i must be a UnityWebData 1.0 file, and -o is the folder where the unpacked files will be saved.
  If -o is not specified, the files will be saved in a folder named output under the current working directory.
""".strip()


def print_err(msg: str):
    print(msg)
    print(f"exit program...")
    exit(1)


def sizeof_fmt(size: int, suffix="B") -> str:
    for unit in ["", "Ki", "Mi", "Gi", "Ti", "Pi", "Ei", "Zi"]:
        if abs(size) < 1024.0:
            return f"{size:3.1f}{unit}{suffix}"
        size /= 1024.0
    return f"{size:.1f}Yi{suffix}"


def to_hex(n: int, digit: int) -> str:
    return f"0x{n:0{digit}X}"


def _is_gzip(data: bytearray) -> bool:
    commentOffset: int = 10
    expectedComment: Final[str] = "UnityWeb Compressed Content (gzip)"

    if commentOffset > len(data) or data[0] != 0x1F or data[1] != 0x8B:
        return False

    flags: Final[int] = data[3]

    if flags & 0x04:
        if commentOffset + 2 > len(data):
            return False
        commentOffset += 2 + data[commentOffset] + (data[commentOffset + 1] << 8)
        if commentOffset > len(data):
            return False

    if flags & 0x08:
        while commentOffset < len(data) and data[commentOffset]:
            commentOffset += 1
        if commentOffset + 1 > len(data):
            return False
        commentOffset += 1

    real_comment = data[commentOffset:commentOffset + len(expectedComment) + 1].decode("utf-8", errors="ignore")
    return (flags & 0x10) and (real_comment == expectedComment + "\0")


def _is_brotli(data: bytearray) -> bool:
    expectedComment: Final[str] = "UnityWeb Compressed Content (brotli)"

    if not data:
        return False

    WBITS_length: Final[int] = (4 if (data[0] & 0x0E) else 7) if (data[0] & 0x01) else 1
    WBITS: Final[int] = data[0] & ((1 << WBITS_length) - 1)
    MSKIPBYTES: Final[int] = 1 + (int(math.log(len(expectedComment) - 1) / math.log(2)) >> 3)
    commentOffset: Final[int] = (WBITS_length + 1 + 2 + 1 + 2 + (MSKIPBYTES << 3) + 7) >> 3

    if WBITS == 0x11 or commentOffset > len(data):
        return False

    expectedCommentPrefix: int = WBITS + (
                (
                        (3 << 1) +
                        (MSKIPBYTES << 4) +
                        ((len(expectedComment) - 1) << 6)
                ) << WBITS_length
    )

    for i in range(commentOffset):
        if data[i] != (expectedCommentPrefix & 0xFF):
            return False
        expectedCommentPrefix >>= 8

    real_comment = data[commentOffset:commentOffset + len(expectedComment)].decode("utf-8", errors="ignore")
    return real_comment == expectedComment


def check_compression(path: str) -> str:
    with open(path, "rb") as file:
        data = bytearray(file.read())

    if _is_brotli(data):
        return "brotli"
    elif _is_gzip(data):
        return "gzip"
    else:
        return "none"
