"""One full-domain independent oracle for the optional native training ABI."""
import ctypes as ct
import os

import numpy as np
import pytest
import scipy.sparse as sp

from lutlab import fit, fullfit, io


@pytest.mark.parametrize("fractional", [False, True])
def test_full_domain_integer_system_matches_coo_and_is_thread_invariant(fractional):
    try:
        library_path = fullfit.resolve_library()
    except FileNotFoundError:
        if os.environ.get("JSHC_FULL_FIT_LIB"):
            raise
        pytest.skip("optional full-domain training library is not built")
    table = np.empty(io.FULL_SHAPE, np.uint8)
    g, b = np.indices((256, 256), dtype=np.uint32)
    for r in range(256):
        table[r, ..., 0] = (37 * r + 19 * g + 11 * b) % 256
        table[r, ..., 1] = (r ^ (g * 3) ^ (b * 7)) % 256
        table[r, ..., 2] = (13 * r + g * g + 23 * b) % 256
    t = np.linspace(0, 1, 17)
    grid = np.stack([255 * t ** p for p in (1.15, .85, 1.05)])
    if not fractional:
        grid = np.round(grid)
    H1, b1, one = fullfit.normal_equations(table, grid, threads=1)
    H4, b4, four = fullfit.normal_equations(table, grid, threads=4)
    assert one["sample_count"] == 256 ** 3 and one["actual_threads"] == 1
    assert 1 <= four["actual_threads"] <= 4
    assert one["integer_system_sha256"] == four["integer_system_sha256"]
    assert np.array_equal(H1.indptr, H4.indptr) and np.array_equal(H1.indices, H4.indices)
    assert np.array_equal(H1.data, H4.data) and np.array_equal(b1, b4)
    assert np.all(H1.diagonal() >= one["data_hessian_eigenvalue_lower_bound"]) and not (H1 - H1.T).nnz
    assert one["support_certificate"]["integer_grid"] == (not fractional)

    # Independent legacy COO assembly covers every colour, all six tetrahedron
    # orders, ties and both endpoints. No stencil index or native grouping is
    # reused in the oracle. Q16 products/sums are dyadic and exactly comparable.
    reference_H = sp.csr_matrix(H1.shape)
    reference_b = np.zeros_like(b1)
    squared = np.zeros(3, np.uint64)
    points = np.empty((4 * 256 ** 2, 3), np.uint8)
    points[:, 1] = np.tile(g.ravel().astype(np.uint8), 4)
    points[:, 2] = np.tile(b.ravel().astype(np.uint8), 4)
    for r in range(0, 256, 4):
        points[:, 0] = np.repeat(np.arange(r, r + 4, dtype=np.uint8), 256 ** 2)
        target = table[r:r + 4].reshape(-1, 3)
        H, rhs = fit.normal_equations(points, target, np.full(len(points), 1 / 64), grid)
        reference_H += H
        reference_b += rhs
        squared += np.sum(target.astype(np.uint32) ** 2, axis=0, dtype=np.uint64)
    reference_H.sort_indices()
    assert not (H1 - reference_H).nnz
    assert np.array_equal(b1, reference_b)
    assert one["target_squared_sum_rgb"] == squared.tolist()

    # A malformed C-ABI length must return an error without touching outputs.
    fingerprint = fullfit.trainer_fingerprint()
    library, _ = fullfit._load(str(library_path), fingerprint["library_sha256"])
    idx, frac = io.axis_tables(grid)
    diag = np.full(17 ** 3, 123, np.uint64)
    upper = np.full((17 ** 3, 7), 123, np.uint64)
    rhs = np.full((17 ** 3, 3), 123, np.uint64)
    metadata, error = np.full(7, 123, np.uint64), ct.create_string_buffer(1024)
    def pointer(array, ctype):
        return array.ctypes.data_as(ct.POINTER(ctype))
    status = library.jshc_full_normals_v1(pointer(table, ct.c_uint8), table.nbytes - 1,
        pointer(idx, ct.c_uint8), pointer(frac, ct.c_uint32), 17, 1,
        pointer(diag, ct.c_uint64), diag.size, pointer(upper, ct.c_uint64), upper.size,
        pointer(rhs, ct.c_uint64), rhs.size, pointer(metadata, ct.c_uint64), metadata.size, error, len(error))
    assert status != 0 and error.value
    assert all(np.all(array == 123) for array in (diag, upper, rhs, metadata))
