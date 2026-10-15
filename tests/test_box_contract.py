"""One independent active-set oracle and an exact rational integer guard check."""
from fractions import Fraction
from itertools import product

import numpy as np
import pytest
import scipy.sparse as sp

from lutlab import box


def test_box_kkt_matches_exhaustive_active_sets_and_exact_integer_selection():
    matrix = np.array([[4., 1., .5, 0.], [1., 3., .25, .5], [.5, .25, 2., .75], [0., .5, .75, 2.5]])
    assert np.linalg.eigvalsh(matrix).min() > 0
    H = sp.csr_matrix(matrix)
    raw = np.array([[-50., 100., 350.], [120., -80., 145.], [30., 260., -20.], [300., 230., 10.]])
    b = matrix @ raw
    start = np.asfortranarray(np.full((4, 3), 127.))  # exercise physical-bound snapping independent of layout
    saved = start.copy()
    info = {}
    actual = box.solve_box(H, b, start, diagnostics=info)
    assert np.array_equal(start, saved)
    assert info["status"] == "converged_by_kkt" and info["feasible"]
    assert np.all((actual >= 0) & (actual <= 255))
    for channel in range(3):
        best = None
        # Independently enumerate lower/free/upper assignments and solve each
        # free linear system. The feasible minimum is the convex global optimum.
        for assignment in product((-1, 0, 1), repeat=4):
            state = np.asarray(assignment)
            free = state == 0
            x = np.where(state == 1, 255., 0.)
            if np.any(free):
                x[free] = np.linalg.solve(matrix[np.ix_(free, free)],
                    b[free, channel] - matrix[np.ix_(free, ~free)] @ x[~free])
            if np.any(x < 0) or np.any(x > 255):
                continue
            value = .5 * x @ matrix @ x - b[:, channel] @ x
            if best is None or value < best[0]:
                best = value, x
        assert np.max(abs(actual[:, channel] - best[1])) < 1e-4
    interior = np.array([[45., 100., 85.], [120., 20., 145.], [30., 60., 210.], [80., 230., 10.]])
    with pytest.raises(box.BoxConvergenceError) as failure:
        box.solve_box(H, matrix @ interior, maxiter=1)
    assert failure.value.diagnostics["status"] == "failed"
    with pytest.raises(box.BoxConvergenceError):
        box.solve_box(H, b, np.full((4, 3), -1.))

    # This comparison can exceed uint64 even though each row product is safe.
    # Fraction is an independent oracle for the full quadratic difference.
    old = np.array([[255, 128, 0], [20, 255, 90], [5, 70, 255], [200, 1, 30]], np.uint8)
    new = np.array([[0, 127, 5], [23, 254, 85], [8, 71, 250], [199, 7, 31]], np.uint8)
    large = H * 4096
    rhs = np.array([[100., 200., 30.], [30., 200., 50.], [100., 90., 20.], [10., 60., 0.]])
    numerator = box.integer_sse_change_numerator(large, rhs, old, new)
    reference = Fraction(0)
    dense = large.toarray()
    for c in range(3):
        for i in range(4):
            reference -= 2 * Fraction.from_float(rhs[i, c]) * (int(new[i, c]) - int(old[i, c]))
            for j in range(4):
                reference += Fraction.from_float(dense[i, j]) * (
                    int(new[i, c]) * int(new[j, c]) - int(old[i, c]) * int(old[j, c]))
    assert Fraction(numerator, 2 ** 38) == reference
    assert abs(numerator) > 2 ** 64
    assert box.integer_sse_change_numerator(large, rhs, new, old) == -numerator
    assert box.integer_sse_change_numerator(large, rhs, old, old) == 0
    with pytest.raises(ValueError, match="exactly representable"):
        box.integer_sse_change_numerator(H * 2 ** 20, rhs, old, new)
