"""One process-level CPU/CUDA adapter acceptance, without a performance loop."""
from pathlib import Path
import os
import struct
import zlib

import numpy as np
import pytest

from lutlab import interp, io, runtime


def _rgb16_png(path: Path) -> None:
    def chunk(kind: bytes, payload: bytes) -> bytes:
        return struct.pack(">I", len(payload)) + kind + payload + struct.pack(">I", zlib.crc32(kind + payload))

    header = struct.pack(">IIBBBBB", 1024, 768, 16, 2, 0, 0, 0)
    rows = (b"\0" + b"\x12\x34\xab\xcd\xff\xff" * 1024) * 768
    path.write_bytes(b"\x89PNG\r\n\x1a\n" + chunk(b"IHDR", header) + chunk(b"IDAT", zlib.compress(rows)) + chunk(b"IEND", b""))


def test_runtime_real_backends_and_rgb8_contract(tmp_path: Path):
    # CUDA is optional in a portable deployment; when explicitly configured it
    # must execute and pass rather than silently skipping or falling back.
    backends = [("cpu", runtime.resolve_backend("cpu"))]
    if os.environ.get("JSHC_CUDA_BIN"):
        backends.append(("cuda", runtime.resolve_backend("cuda")))
    rng = np.random.default_rng(2026101519)
    models = []
    for stage, m in enumerate((17, 18, 26, 33), 1):
        t = np.linspace(0, 1, m)
        grid = np.stack((255 * t ** 1.13, 255 * t, 255 * t ** .87))
        grid[:, 0], grid[:, -1] = 0, 255
        path = tmp_path / f"stage{stage}.slut"
        io.save_sparse(path, io.SparseLut(grid, rng.integers(0, 256, (m, m, m, 3), dtype=np.uint8)))
        models.append(path)
    pixels = rng.integers(0, 256, (1, 257, 3), dtype=np.uint8)
    pixels[0, :3] = ((0, 0, 0), (255, 255, 255), (255, 0, 255))
    source = tmp_path / "tail.png"
    io.save_image(source, pixels)
    expected = pixels.copy()
    for path in models:
        expected = interp.apply_tetra_q16(io.load_sparse(path), expected)
    rgb16 = tmp_path / "rgb16.png"
    _rgb16_png(rgb16)

    for backend, executable in backends:
        capabilities = runtime.capabilities(backend, executable)
        assert capabilities["returncode"] == 0 and capabilities["available_kernels"]
        output = tmp_path / f"{backend}.png"
        result = runtime.apply(models, source, output, backend=backend, executable=executable)
        assert np.array_equal(io.load_image(output), expected)
        assert result["backend"] == backend and len(result["models_sha256"]) == 4
        assert len(result["executable_sha256"]) == 64 and result["process_wall_seconds"] > 0

        # Correct dimensions must not hide 16-to-8-bit decoding. A separate
        # valid-RGB8 short image verifies the competition dimension gate.
        for invalid in (rgb16, source):
            rejected = tmp_path / f"rejected-{backend}.png"
            with pytest.raises(runtime.BackendError) as failure:
                runtime.apply(models, invalid, rejected, backend=backend, executable=executable, competition=True)
            assert failure.value.record["returncode"] != 0
            assert failure.value.record["stderr"]
            assert not rejected.exists()

    with pytest.raises(ValueError, match="CUDA supports"):
        runtime.apply(models, source, tmp_path / "wrong.png", backend="cuda", kernel="tri_float")
