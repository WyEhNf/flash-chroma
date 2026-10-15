"""Focused contracts for solver failures and exact-Q16 incumbent protection."""
import numpy as np
import pytest
import scipy.sparse as sp

from lutlab import fit, interp, io


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
