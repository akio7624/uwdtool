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
