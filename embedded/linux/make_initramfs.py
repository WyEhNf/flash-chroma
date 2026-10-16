"""生成确定性的 newc initramfs，仅包含静态 AArch64 init 和控制台节点。"""
from pathlib import Path
import stat
import sys


def build(elf: bytes) -> bytes:
    if elf[:6] != b"\x7fELF\x02\x01" or elf[18:20] != b"\xb7\x00":
        raise ValueError("init 必须为 little-endian AArch64 ELF64")
    archive = bytearray()

    def entry(name, mode, payload=b"", major=0, minor=0):
        encoded = name.encode() + b"\0"
        fields = (1, mode, 0, 0, 1, 0, len(payload), 0, 0, major, minor, len(encoded), 0)
        archive.extend(b"070701" + b"".join(f"{field:08x}".encode() for field in fields))
        archive.extend(encoded)
        archive.extend(b"\0" * (-len(archive) % 4))
        archive.extend(payload)
        archive.extend(b"\0" * (-len(archive) % 4))

    entry("dev", stat.S_IFDIR | 0o755)
    entry("dev/console", stat.S_IFCHR | 0o600, major=5, minor=1)
    entry("init", stat.S_IFREG | 0o755, elf)
    entry("TRAILER!!!", 0)
    return bytes(archive)


if __name__ == "__main__":
    Path(sys.argv[2]).write_bytes(build(Path(sys.argv[1]).read_bytes()))
