"""Proved piecewise-constant RGB LUTs and finite-domain vertex alignment.

Lower-cell hold is encoded with geometry-derived one-hot Q16 coordinates in
the existing authoritative axis tables. No source colours are stored in those
coordinates: they are zero except for the endpoint selector at input 255.
"""
from __future__ import annotations

import hashlib

import numpy as np

from . import interp, io


def _check_table(table, m):
    if (table.shape != io.FULL_SHAPE or table.dtype != np.uint8 or not isinstance(m, (int, np.integer))
            or isinstance(m, bool) or not 17 <= m <= 33):
        raise ValueError("expected a complete RGB8 LUT and 17<=m<=33")


def _filled_axis(required, m):
    values = sorted({0, 255, *(int(v) for v in required)})
    if len(values) > m:
        return None
    while len(values) < m:
        gap = int(np.argmax(np.diff(values)))
        if values[gap + 1] - values[gap] < 2:
            raise ValueError("not enough distinct integer grid positions")
        values.insert(gap + 1, (values[gap] + values[gap + 1]) // 2)
    return np.asarray(values, dtype=np.float64)


def exact_lower_hold(table, m, *, diagnostics=None):
    """Prove complete constant-slice partitions before constructing a hold LUT.

    Every adjacent input slice is checked in all other coordinates/channels.
    Within each resulting interval, changing that axis cannot change the LUT.
    Replacing three coordinates by lower endpoints therefore preserves every
    table byte. Unsuccessful detection makes no separability/exactness claim.
    """
    _check_table(table, m)
    report = {} if diagnostics is None else diagnostics
    axes, boundaries = [], []
    for axis in range(3):
        cuts = {0, 255}
        for position in range(1, 256):
            before = [slice(None)] * 4
            after = [slice(None)] * 4
            before[axis], after[axis] = position - 1, position
            if not np.array_equal(table[tuple(before)], table[tuple(after)]):
                cuts.add(position)
                if len(cuts) > m:
                    report.update(proved=False, rejected_axis=axis, required_knots_lower_bound=len(cuts))
                    return None
        boundaries.append(sorted(cuts))
        axes.append(_filled_axis(cuts, m))
    grid = np.stack(axes)
    integer_axes = [axis.astype(np.intp) for axis in grid]
    nodes = np.ascontiguousarray(table[np.ix_(*integer_axes)])
    index, _ = io.axis_tables(grid)
    fraction = np.zeros((3, 256), dtype=np.uint32)
    fraction[:, 255] = io.ONE
    model = io.SparseLut(grid, nodes, index, fraction)
    io.validate_sparse(model, competition=True)
    report.update(proved=True, verified_source_colors=256 ** 3, partition_knots=boundaries,
        grid=grid.astype(int).tolist(), axis_policy="lower_cell_hold_with_endpoint_selector",
        guarantee="exact own-LUT output on every RGB8 input; no final-chain equality claim",
        axis_coordinates="geometry-only Q16 values 0 or 65536; no target-colour information")
    return model


def is_one_hot(model):
    """All Q16 coordinates are endpoints, so every output is one stored vertex."""
    _, fraction = model.tables()
    return bool(np.all((fraction == 0) | (fraction == io.ONE)))


def aligned_vertices(table, m, input_palette, *, diagnostics=None):
    """Sample own-LUT labels at knots containing every supplied input colour.

    Exactness is conditional on the supplied palette covering actual inputs.
    The cascade constructs such a superset from a one-hot preceding stage and
    propagates it through subsequent actual sparse operators.
    """
    _check_table(table, m)
    report = {} if diagnostics is None else diagnostics
    if input_palette is None:
        report.update(proved=False, reason="no proved finite prefix-output palette")
        return None
    palette = np.asarray(input_palette)
    if palette.dtype != np.uint8 or palette.ndim != 2 or palette.shape[1] != 3 or len(palette) == 0:
        raise ValueError("reachable palette must be a nonempty (N,3) RGB8 array")
    required = [np.unique(palette[:, axis]) for axis in range(3)]
    axes = [_filled_axis(values, m) for values in required]
    report["component_value_counts"] = [len(values) for values in required]
    if any(axis is None for axis in axes):
        report.update(proved=False, reason="palette components and endpoints exceed m")
        return None
    grid = np.stack(axes)
    nodes = np.ascontiguousarray(table[np.ix_(*(axis.astype(np.intp) for axis in grid))])
    model = io.SparseLut(grid, nodes)
    io.validate_sparse(model, competition=True)
    prediction = interp.apply_tetra_q16(model, palette)
    truth = io.apply_full(table, palette)
    if not np.array_equal(prediction, truth):
        raise RuntimeError("vertex-aligned palette failed its complete own-LUT check")
    report.update(proved=True, verified_palette_entries=len(palette),
        input_palette_sha256=hashlib.sha256(palette.tobytes()).hexdigest(),
        grid=grid.astype(int).tolist(), axis_policy="canonical_geometric_q16",
        guarantee="exact own-LUT output on the supplied complete prefix-output superset")
    return model


def next_palette(model, incoming, *, diagnostics=None):
    """Maintain a bounded, proved superset of all possible prefix outputs."""
    report = {} if diagnostics is None else diagnostics
    if is_one_hot(model):
        palette = model.nodes.reshape(-1, 3).copy()
        proof = "one-hot weights select a stored vertex on every RGB input"
    elif incoming is not None:
        palette = interp.apply_tetra_q16(model, incoming)
        proof = "pointwise propagation of the proved incoming superset"
    else:
        report.update(proved=False, reason="no finite output-superset proof")
        return None
    palette = np.ascontiguousarray(palette)
    palette.setflags(write=False)
    report.update(proved=True, entries=len(palette), sha256=hashlib.sha256(palette.tobytes()).hexdigest(), proof=proof)
    return palette
