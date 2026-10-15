"""Input fixtures shared by the native runtime and validation acceptance."""
import struct
import zlib

import pytest


@pytest.fixture
def rgb16_png(tmp_path):
    # Pillow exposes RGB16 PNG as mode RGB after an implicit 8-bit decode.
    # Preserve a real 16-bit container to exercise the native source-depth gate.
    def chunk(kind, payload):
        return struct.pack(">I", len(payload)) + kind + payload + struct.pack(">I", zlib.crc32(kind + payload))

    header = struct.pack(">IIBBBBB", 1024, 768, 16, 2, 0, 0, 0)
    rows = (b"\0" + b"\x12\x34\xab\xcd\xff\xff" * 1024) * 768
    path = tmp_path / "rgb16.png"
    path.write_bytes(b"\x89PNG\r\n\x1a\n" + chunk(b"IHDR", header)
                     + chunk(b"IDAT", zlib.compress(rows)) + chunk(b"IEND", b""))
    return path
