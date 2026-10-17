"""以互异RGB8见证与整数Gershgorin余量证明完整Q16设计的正定下界。"""
from __future__ import annotations
import hashlib
import numpy as np
import scipy.sparse as sp
from . import interp, io


def certify(grid,index=None,fraction=None):
    """充分证书，不覆盖所有可解网格；失败不能当作秩亏证明。

    取每节点最近RGB8输入的方阵A。其对称部分若严格对角占优，
    x^T A x>=delta||x||²，故||Ax||>=delta||x||，完整H>=A^T A/64。
    余量使用权威Q16整数精确计算，不把正对角或浮点特征值当作证明。
    """
    if grid.ndim != 2 or grid.shape[0] != 3 or not 2 <= grid.shape[1] <= 33:
        raise ValueError("支撑证书需要2至33节点的三轴网格")
    # 同时执行网格有效性检查；提供的权威表可以来自SLUT序列化。
    regenerated = io.axis_tables(grid)
    if index is None and fraction is None:
        index,fraction = regenerated
    elif index is None or fraction is None:
        raise ValueError("权威idx/frac必须同时提供")
    m = grid.shape[1]
    if (index.shape != (3,256) or fraction.shape != (3,256) or index.dtype != np.uint8
            or fraction.dtype != np.uint32 or np.any(index > m-2) or np.any(fraction > io.ONE)):
        raise ValueError("权威轴表形状、类型或范围无效")
    levels = np.rint(grid).astype(np.int64)
    if np.any(levels < 0) or np.any(levels > 255) or np.any(np.diff(levels,axis=1) <= 0):
        raise ValueError("最近RGB8见证有重复或越界，无法证明正定；不代表设计必然秩亏")
    points = np.stack(np.meshgrid(*levels,indexing="ij"),-1).reshape(-1,3).astype(np.uint8)
    indices,weights = interp.tetra_index_weights_q(points,index,fraction,m)
    matrix = sp.csr_matrix((weights.astype(np.int64).ravel(),indices.ravel(),
        np.arange(0,4*len(points)+1,4,dtype=np.int32)),shape=(m**3,m**3))
    matrix.sum_duplicates()
    matrix.eliminate_zeros()
    diagonal = matrix.diagonal()
    row = np.asarray(matrix.sum(axis=1)).ravel()
    column = np.asarray(matrix.sum(axis=0)).ravel()
    margin = 4*diagonal-row-column
    minimum = int(margin.min())
    if minimum <= 0:
        raise ValueError("最近RGB8见证的对称部分未通过整数余量检查，无法证明正定；不代表设计必然秩亏")
    numerator,denominator = minimum**2,64*(2*io.ONE)**2
    axis_hash = hashlib.sha256(index.tobytes()+fraction.tobytes()).hexdigest()
    return {"method":"nearest_rgb_symmetric_gershgorin_q16","witness_count":m**3,
        "witness_rgb_sha256":hashlib.sha256(points.tobytes()).hexdigest(),"axis_tables_sha256":axis_hash,
        "minimum_twice_symmetric_margin_q16":minimum,"singular_value_lower_bound_ratio":[minimum,2*io.ONE],
        "hessian_eigenvalue_lower_bound_ratio":[numerator,denominator],
        "hessian_eigenvalue_lower_bound":numerator/denominator,
        "integer_grid":bool(np.all(grid == np.rint(grid))),
        "scope":"互异见证均为完整RGB域子集；H=sum(w*w^T)/64；证书只证明当前权威Q16设计正定，不证明RGB8精度"}
