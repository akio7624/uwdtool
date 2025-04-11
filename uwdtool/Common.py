UWDT_VERSION = "1.2.0"
HELP_STR = f"""UWDTool v{UWDT_VERSION}"""

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
