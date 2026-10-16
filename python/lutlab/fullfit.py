"""Optional zero-copy C ABI for exact full-domain integer Q16 LS moments.

The native library is an offline dependency only. No pixel runtime, model file
or ordinary fitting method loads it. A selected library must match this source
tree, ABI and content fingerprint; there is no silent backend fallback.
"""
from __future__ import annotations

import ctypes as ct
from functools import lru_cache
import hashlib
import os
from pathlib import Path
import time

import numpy as np
import scipy.sparse as sp

from . import io, support_certificate

ROOT = Path(__file__).resolve().parents[2]
NATIVE_SOURCES = ("cpp/src/full_normals.cpp", "cpp/include/jshc/full_normals.h")


def _sha(path):
    with Path(path).open("rb") as stream:
        return hashlib.file_digest(stream, "sha256").hexdigest()


def resolve_library():
    supplied = os.environ.get("JSHC_FULL_FIT_LIB")
    if supplied:
        path = Path(supplied).resolve()
        if not path.is_file():
            raise FileNotFoundError(f"configured full-domain fitting library not found: {path}")
        return path
    names = ("jshc_full_fit.dll", "libjshc_full_fit.dll") if os.name == "nt" else (
        "libjshc_full_fit.dylib" if os.sys.platform == "darwin" else "libjshc_full_fit.so",)
    # 默认构建同时生成运行时与拟合库；旧实验目录仅作兼容回退。
    for directory in (ROOT / "build", ROOT / "build" / "Release", ROOT / "build-fit"):
        for name in names:
            path = directory / name
            if path.is_file():
                return path.resolve()
    raise FileNotFoundError("full-domain fit requires a JSHC_ENABLE_FULL_FIT=ON build; set JSHC_FULL_FIT_LIB")


@lru_cache(maxsize=2)
def _load(path: str, digest: str):
    # DLL dependencies are deployed beside the optional library. The directory
    # handle is kept with the CDLL, so the loader does not rely on global PATH.
    directory = os.add_dll_directory(str(Path(path).parent)) if os.name == "nt" else None
    try:
        library = ct.CDLL(path)
        for name in ("jshc_full_normals_abi_v1", "jshc_full_normals_openmp_v1"):
            function = getattr(library, name)
            function.argtypes = []
            function.restype = ct.c_uint32
        library.jshc_full_normals_source_v1.argtypes = []
        library.jshc_full_normals_source_v1.restype = ct.c_char_p
        u8, u32, u64 = (ct.POINTER(t) for t in (ct.c_uint8, ct.c_uint32, ct.c_uint64))
        library.jshc_full_normals_v1.argtypes = [u8, ct.c_uint64, u8, u32, ct.c_uint32, ct.c_uint32,
            u64, ct.c_uint64, u64, ct.c_uint64, u64, ct.c_uint64, u64, ct.c_uint64, ct.POINTER(ct.c_char), ct.c_uint64]
        library.jshc_full_normals_v1.restype = ct.c_int
        if library.jshc_full_normals_abi_v1() != 1 or _sha(path) != digest:
            raise RuntimeError("full-domain library ABI or content changed while loading")
    except BaseException:
        if directory is not None:
            directory.close()
        raise
    return library, directory


def trainer_fingerprint():
    path = resolve_library()
    digest = _sha(path)
    library, _ = _load(str(path), digest)
    sources = {name: _sha(ROOT / name) for name in NATIVE_SOURCES}
    expected = hashlib.sha256(":".join(sources.values()).encode("ascii")).hexdigest()
    embedded = library.jshc_full_normals_source_v1().decode("ascii")
    if embedded != expected:
        raise RuntimeError("full-domain library is stale for this source tree; rebuild jshc_full_fit")
    return {"abi_version": 1, "library_sha256": digest, "native_source_sha256": sources,
            "embedded_source_fingerprint": embedded, "openmp_compiled": bool(library.jshc_full_normals_openmp_v1())}


def normal_equations(table: np.ndarray, grid: np.ndarray, threads: int = 4):
    """Exact all-colour H,b scaled by 1/64; float64 conversion follows uint64 sums."""
    started = time.perf_counter()
    if (table.shape != io.FULL_SHAPE or table.dtype != np.uint8
            or not isinstance(threads, int) or isinstance(threads, bool) or not 1 <= threads <= 256):
        raise ValueError("expected a complete RGB8 LUT and 1..256 fitting threads")
    index, fraction = io.axis_tables(grid)
    m = grid.shape[1]
    if not 17 <= m <= 33 or np.any(grid[:, 0] != 0) or np.any(grid[:, -1] != 255):
        raise ValueError("完整域拟合需要端点0/255、17至33节点的网格")
    # 原生组装只使用idx/frac；小数网格必须先取得同一设计的正定证书。
    support = support_certificate.certify(grid,index,fraction)
    fingerprint = trainer_fingerprint()
    path = resolve_library()
    library, _ = _load(str(path), fingerprint["library_sha256"])
    table = np.ascontiguousarray(table)
    index, fraction = np.ascontiguousarray(index), np.ascontiguousarray(fraction, dtype=np.uint32)
    M = m ** 3
    diagonal, upper, rhs = np.empty(M, np.uint64), np.empty((M, 7), np.uint64), np.empty((M, 3), np.uint64)
    metadata, error = np.empty(7, np.uint64), ct.create_string_buffer(1024)
    def pointer(array, ctype):
        return array.ctypes.data_as(ct.POINTER(ctype))
    status = library.jshc_full_normals_v1(pointer(table, ct.c_uint8), table.nbytes,
        pointer(index, ct.c_uint8), pointer(fraction, ct.c_uint32), m, threads,
        pointer(diagonal, ct.c_uint64), diagonal.size, pointer(upper, ct.c_uint64), upper.size,
        pointer(rhs, ct.c_uint64), rhs.size, pointer(metadata, ct.c_uint64), metadata.size, error, len(error))
    if status:
        raise RuntimeError(f"native full-domain assembly failed ({status}): {error.value.decode('utf-8', errors='replace')}")
    if (metadata[0] != 256 ** 3 or metadata[2] != m - 1 or metadata[3] != 1
            or not 1 <= metadata[1] <= threads):
        raise RuntimeError("native full-domain coverage or ABI metadata failed")
    if trainer_fingerprint() != fingerprint:
        raise RuntimeError("native fitting library or source changed during assembly")
    raw_sha = hashlib.sha256()
    for array in (diagonal, upper, rhs, metadata[4:]):
        raw_sha.update(memoryview(array))
    offsets = np.asarray((1, m, m + 1, m * m, m * m + 1, m * m + m, m * m + m + 1), np.int32)
    rows = np.repeat(np.arange(M, dtype=np.int32), 7)
    cols = rows + np.tile(offsets, M)
    nonzero = upper.ravel() != 0
    if np.any(cols[nonzero] >= M):
        raise RuntimeError("native full-domain stencil has an out-of-range edge")
    values = upper.ravel()[nonzero].astype(np.float64) * 2. ** -38
    positive = sp.coo_matrix((values, (rows[nonzero], cols[nonzero])), shape=(M, M)).tocsr()
    H = (positive + positive.T + sp.diags(diagonal.astype(np.float64) * 2. ** -38)).tocsr()
    H.sort_indices()
    b = rhs.astype(np.float64) * 2. ** -22
    report = {"backend": "native_uint64_full_domain_stencil", "trainer": fingerprint,
        "sample_count": int(metadata[0]), "sample_weight_sum": float(64 ** 3),
        "requested_threads": threads, "actual_threads": int(metadata[1]),
        "r_cell_parity_passes": 2, "integer_accumulator_payload_bytes": diagonal.nbytes + upper.nbytes + rhs.nbytes,
        "integer_system_sha256": raw_sha.hexdigest(), "normal_equations_nnz": int(H.nnz),
        "zero_diagonal_nodes": int(np.count_nonzero(H.diagonal() == 0)), "minimum_diagonal": float(H.diagonal().min()),
        "data_hessian_eigenvalue_lower_bound": support["hessian_eigenvalue_lower_bound"],
        "support_certificate": support, "target_squared_sum_rgb": metadata[4:].tolist(),
        "target_norm_squared_scaled": float(sum(int(v) for v in metadata[4:]) / 64),
        "normalisation": "H = sum(w_q w_q^T) / 2^38; b = sum(w_q y) / 2^22; all 256^3 colours",
        "assembly_seconds": time.perf_counter() - started}
    return H, b, report
