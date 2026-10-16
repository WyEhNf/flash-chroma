"""固定 Q16 权重与 RGB8 节点约束下的三点误差下界。"""
import numpy as np
from . import interp


def three_point_bound(model, points, targets):
    """只用整数权重给出必要误差，不假定三点落在同一四面体。"""
    points, targets = np.asarray(points), np.asarray(targets)
    if points.shape != (3, 3) or targets.shape != (3, 3) or points.dtype != np.uint8 or targets.dtype != np.uint8:
        raise ValueError("证书需要三个RGB8输入及各自的原表标签")
    indices, weights = interp.tetra_index_weights_q(points, *model.tables(), model.m)
    coefficients = {}
    for row, multiplier in enumerate((1, -2, 1)):
        for node, weight in zip(indices[row], weights[row]):
            coefficients[int(node)] = coefficients.get(int(node), 0) + multiplier * int(weight)
    coefficients = {node: value for node, value in coefficients.items() if value}
    if sum(coefficients.values()) != 0:
        raise AssertionError("Q16权重的二阶差分不守恒")
    # 任意节点 n∈[0,255] 时，|Σalpha*n|≤255*Σalpha_positive。
    curvature_numerator = 255 * sum(value for value in coefficients.values() if value > 0)
    difference = targets.astype(np.int64)[0] - 2 * targets.astype(np.int64)[1] + targets.astype(np.int64)[2]
    # 每次RGB8舍入误差≤1/2，系数绝对值和为4，故二阶差分的舍入余量≤2。
    numerator = np.abs(difference) * 65536 - curvature_numerator - 2 * 65536
    lower = np.maximum(0, (numerator + 4 * 65536 - 1) // (4 * 65536))
    return {"points": points.tolist(), "targets": targets.tolist(),
        "reference_second_difference": difference.tolist(), "node_coefficients": coefficients,
        "model_second_difference_bound_numerator": curvature_numerator,
        "model_second_difference_bound_denominator": 65536,
        "channel_max_absolute_error_lower_bound": lower.tolist(),
        "rgb_l2_max_lower_bound": int(lower.max()),
        "scope": "仅此固定idx/frac与Q16四面体表示；适用于任意合法RGB8节点，不涵盖其他网格/插值器或最终四级误差"}
