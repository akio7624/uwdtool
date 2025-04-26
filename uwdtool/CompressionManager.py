import gzip
import io
import math
from typing import Final

from .Common import print_err
import uwdtool.brotli.brotli as brotli


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


def compress_gzip(data: bytes) -> bytes:
    buffer = io.BytesIO()
    with gzip.GzipFile(fileobj=buffer, mode="wb") as gz:
        gz.write(data)

    bio = io.BytesIO(buffer.getvalue())
    buffer.close()

    ID1 = bio.read(1)
    ID2 = bio.read(1)
    CM = bio.read(1)
    FLG = int.from_bytes(bio.read(1), byteorder="little")
    bio.seek(4, io.SEEK_CUR)  # skip MTIME
    bio.seek(1, io.SEEK_CUR)  # skip XFL
    bio.seek(1, io.SEEK_CUR)  # skip OS

    if ID1 != b'\x1F' or ID2 != b'\x8B' or CM != b'\x08':
        print_err(f"Error occurred while parsing the gzip header")

    FCOMMENT = False
    comment_start_ofs = 1 + 1 + 1 + 1 + 4 + 1 + 1
    comment_end_ofs = 0

    # Python's gzip data likely has all flags set to 0
    if FLG & 0x02:  # FHCRC is set
        bio.seek(2, io.SEEK_CUR)  # skip FHCRC
        comment_start_ofs += 2
    if FLG & 0x04:  # FEXTRA is set
        length = int.from_bytes(bio.read(2), byteorder="little")
        bio.seek(length, io.SEEK_CUR)  # skip FEXTRA
        comment_start_ofs += 2
        comment_start_ofs += length
    if FLG & 0x08:  # FNAME is set
        while bio.read(1) != b'\x00':  # skip FNAME
            comment_start_ofs += 1
    if FLG & 0x10:  # FCOMMENT is set
        comment_start_ofs = bio.tell()
        while bio.read(1) != b'\x00':  # skip FCOMMENT
            pass
        comment_end_ofs = bio.tell()
        FCOMMENT = True

    editable = bytearray(bio.getvalue())
    bio.close()

    print("Add comment...")
    if not FCOMMENT:
        editable[3] |= 0x10  # set FCOMMENT

    editable[comment_start_ofs:comment_end_ofs] = b"UnityWeb Compressed Content (gzip)\x00"

    return bytes(editable)


def compress_brotli(data: bytes) -> bytes:
    compressed_data = bytes()

    try:
        compressed_data = brotli.compress(
            data,
            comment="UnityWeb Compressed Content (brotli)",
            mode=brotli.MODE_GENERIC,
            quality=5,  # 0-11
            lgwin=22,
            lgblock=0,
            dictionary=b""
        )
    except Exception as e:
        print_err(f"bro.py Error: {e}")

    return compressed_data

