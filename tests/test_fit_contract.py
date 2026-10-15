"""Focused contracts for solver failures and exact-Q16 incumbent protection."""
import numpy as np
import pytest
import scipy.sparse as sp

from lutlab import curve, fit, interp, io


def test_supported_measure_is_unbiased_and_contains_a_complete_identity_design():
    # Dense clusters deliberately exhaust some strata; no random draw is
    # possible there. Other strata must exclude vertices without double count.
    grid = np.stack([np.r_[np.arange(32), 255.]] * 3).astype(np.float64)
    key = grid.tobytes()
    points, weights = fit.supported_points(key, 33)
    vertices = np.stack(np.meshgrid(*grid.astype(np.uint8), indexing="ij"), -1).reshape(-1, 3)
    inner = vertices[np.all((vertices > 0) & (vertices < 255), axis=1)]
    boundary_count = 256 ** 3 - 254 ** 3
    random_count = len(points) - boundary_count - len(inner)
    assert random_count < 64 ** 3 and weights.sum() == 64 ** 3
    assert np.array_equal(points[-len(inner):], inner)
    keys = np.ravel_multi_index(points.T, (256,) * 3)
    vertex_keys = np.ravel_multi_index(vertices.T, (256,) * 3)
    order = np.argsort(keys)
    assert np.all(np.diff(keys[order]) > 0)
    positions = order[np.searchsorted(keys[order], vertex_keys)]
    assert np.array_equal(points[positions], vertices)
    assert np.all(weights[positions] == 1 / 64)
    assert not points.flags.writeable and not weights.flags.writeable

    def block_keys(rgb):
        return np.ravel_multi_index((rgb.astype(np.int64) // 4).T, (64,) * 3)
    random = points[:random_count]
    blocks = block_keys(random)
    assert len(np.unique(blocks)) == random_count
    vertex_population = np.bincount(block_keys(inner), minlength=64 ** 3)
    extent = np.where((random // 4 == 0) | (random // 4 == 63), 3, 4)
    assert np.array_equal(weights[:random_count], (np.prod(extent, axis=1) - vertex_population[blocks]) / 64)
    indices, basis = interp.tetra_index_weights_q(vertices, *io.axis_tables(grid), 33)
    assert np.all(np.max(basis, axis=1) == io.ONE)
    assert np.array_equal(indices[np.arange(len(vertices)), np.argmax(basis, axis=1)], np.arange(33 ** 3))
    # The above rows are exactly I/sqrt(64), establishing H >= I/64 for all
    # vectors. Check the assembled system retains this contribution as well.
    H, transpose = fit._supported_system(key, 33, 0x533231)
    assert np.all(H.diagonal() >= 1 / 64)
    x = np.random.default_rng(24).normal(size=(33 ** 3, 3))
    I, W = interp.tetra_weights(points, *io.axis_tables(grid), 33)
    prediction = np.einsum("nk,nkc->nc", W, x[I])
    assert np.isclose(np.sum(x * (H @ x)), np.sum(weights[:, None] * prediction ** 2), rtol=1e-12)
    assert transpose.shape == (33 ** 3, len(points))
    invalid = grid.copy()
    invalid[:, 1] += .25
    with pytest.raises(ValueError, match="integer grid"):
        fit.supported_points(invalid.tobytes(), 33)


def test_integer_curve_matches_exhaustive_optimum_and_verifies_separability():
    grid = np.stack([[0., 80., 255.]] * 3)
    indices, fractions = io.axis_tables(grid)
    all_nodes = np.stack(np.meshgrid(*([np.arange(4)] * 3), indexing="ij"), -1).reshape(-1, 3)
    f = fractions[0].astype(np.int64)
    predictions = ((all_nodes[:, indices[0]] * (io.ONE - f)
                    + all_nodes[:, indices[0].astype(int) + 1] * f + io.ONE // 2) >> io.Q)
    for seed in (21, 22, 23):
        values = np.random.default_rng(seed).integers(0, 4, 256, dtype=np.uint8)
        nodes, certificate = curve.fit_integer_curve(values, indices[0], fractions[0], 3, max_node_value=3)
        errors = predictions - values.astype(np.int64)
        objectives = list(zip(np.max(abs(errors), axis=1), np.sum(errors * errors, axis=1)))
        expected = min(objectives)
        assert (certificate["max_abs_error"], certificate["squared_error_sum"]) == expected
        assert np.any(np.all(all_nodes == nodes, axis=1))

    # An exact channel permutation and constant channel must be recognized,
    # while a single unsampled interior exception must reject the reduction.
    full = np.empty(io.FULL_SHAPE, dtype=np.uint8)
    full[..., 0] = np.arange(256, dtype=np.uint8)[None, None, :]
    full[..., 1] = 17
    full[..., 2] = (255 - np.arange(256, dtype=np.uint8))[:, None, None]
    channels = curve.separable_channels(full)
    assert [axis for axis, _ in channels] == [2, 1, 0]
    info = {}
    fitted = fit.fit_structured_tetra(full, io.uniform_grid(18), diagnostics=info)
    assert info["route"] == "verified_axis_separable"
    assert all(row["max_abs_error"] == 0 for row in info["channels"])
    points = np.random.default_rng(22).integers(0, 256, (1024, 3), dtype=np.uint8)
    assert np.array_equal(interp.apply_tetra_q16(io.SparseLut(io.uniform_grid(18), fitted), points),
                          io.apply_full(full, points))
    full[91, 137, 203, 0] ^= 1
    assert curve.separable_channels(full) is None


def test_boundary_sampling_partitions_full_rgb_measure_without_duplicates():
    points, weights = fit.boundary_complete_points()
    interior_count, boundary_count = 64 ** 3, 256 ** 3 - 254 ** 3
    assert points.dtype == np.uint8 and points.shape == (interior_count + boundary_count, 3)
    interior, boundary = points[:interior_count], points[interior_count:]
    assert np.all((interior > 0) & (interior < 255))
    blocks = interior.astype(np.uint32) // 4
    block_keys = (blocks[:, 0] * 64 + blocks[:, 1]) * 64 + blocks[:, 2]
    assert len(np.unique(block_keys)) == interior_count
    population = np.prod(np.where((blocks == 0) | (blocks == 63), 3, 4), axis=1)
    assert np.array_equal(weights[:interior_count], population / 64)
    assert np.all(np.any((boundary == 0) | (boundary == 255), axis=1))
    boundary32 = boundary.astype(np.uint32)
    keys = (boundary32[:, 0] * 256 + boundary32[:, 1]) * 256 + boundary32[:, 2]
    assert len(np.unique(keys)) == boundary_count  # every possible boundary colour exactly once
    assert np.all(weights[interior_count:] == 1 / 64)
    assert weights.sum() == 64 ** 3
    assert not points.flags.writeable and not weights.flags.writeable

    # Check the assembled operator against its defining weighted quadratic,
    # including the target term, independently of CSR row/transpose assembly.
    grid = io.uniform_grid(18)
    H, transpose = fit._boundary_system(grid.astype(np.float64).tobytes(), 18, 0x533231)
    nodes = np.random.default_rng(21).normal(size=(18 ** 3, 3))
    indices, basis = interp.tetra_weights(points, *io.axis_tables(grid), 18)
    prediction = np.einsum("nk,nkc->nc", basis, nodes[indices])
    target = points.astype(np.float64) / 255 - .5
    assert np.isclose(np.sum(nodes * (H @ nodes)), np.sum(weights[:, None] * prediction ** 2), rtol=1e-12)
    assert np.isclose(np.sum(nodes * (transpose @ target)),
                      np.sum(weights[:, None] * prediction * target), rtol=1e-12)
    assert abs(H - H.T).max() < 1e-12


def test_cg_failure_is_explicit_and_diagnostic():
    # A coupled SPD system needs more than one preconditioned CG iteration.
    H = sp.diags([-np.ones(2), 2 * np.ones(3), -np.ones(2)], [-1, 0, 1]).tocsr()
    b = np.ones((3, 3))
    diagnostic = {}
    with pytest.raises(fit.FitConvergenceError) as failure:
        fit.solve_spd(H, b, maxiter=1, diagnostics=diagnostic)
    assert failure.value.diagnostics is diagnostic
    assert diagnostic["status"] == "failed"
    assert diagnostic["channels"][0]["info"] > 0
    assert not diagnostic["channels"][0]["converged"]

    invalid = b.copy()
    invalid[0, 0] = np.nan
    with pytest.raises(fit.FitConvergenceError) as failure:
        fit.solve_spd(H, invalid)
    assert failure.value.diagnostics["status"] == "invalid_input"


def test_q16_refinement_improves_actual_output_and_rolls_back_guard_regression():
    grid = io.uniform_grid(18)  # integer knots, including both 8-bit endpoints
    nodes = np.ones((18, 18, 18, 3), dtype=np.uint8)
    points = np.array([[0, 0, 0], [15, 30, 45], [255, 255, 255]], dtype=np.uint8)
    target = np.zeros_like(points)
    accepted = {}
    refined = fit.q16_refine(nodes, points, target, grid, sweeps=1, diagnostics=accepted)
    assert accepted["accepted_sweeps"] == 1
    assert accepted["after"]["training"]["mean"] < accepted["before"]["training"]["mean"]
    assert np.array_equal(interp.apply_tetra_q16(io.SparseLut(grid, refined), points), target)
    assert np.all(nodes == 1)  # an incumbent supplied by the caller is never mutated

    # A nearby, previously exact guard colour shares the adjusted corner. It
    # would become worse, so all changes from that sweep must be discarded.
    rejected = {}
    kept = fit.q16_refine(nodes, points, target, grid, sweeps=1,
                          guard_points=np.array([[1, 0, 0]], dtype=np.uint8),
                          guard_targets=np.ones((1, 3), dtype=np.uint8), diagnostics=rejected)
    assert rejected["stop_reason"] == "sample_guard_rollback"
    assert rejected["accepted_sweeps"] == 0
    assert rejected["after"] == rejected["before"]
    assert np.array_equal(kept, nodes)
