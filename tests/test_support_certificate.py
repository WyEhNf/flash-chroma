"""正定见证的整数余量、独立稠密谱界与显式拒绝合同。"""
import numpy as np
import pytest
from lutlab import io, support_certificate as sc


def test_integer_grid_recovers_original_bound_exactly():
    record = sc.certify(np.rint(io.uniform_grid(17)))
    assert record["minimum_twice_symmetric_margin_q16"] == 2*65536
    assert record["hessian_eigenvalue_lower_bound"] == 1/64
    assert record["witness_count"] == 17**3


def test_fractional_witness_margin_matches_independent_dense_matrix():
    grid = np.array([[0,73.37,255],[0,140.49,255],[0,199.6,255]],float)
    idx,frac = io.axis_tables(grid)
    levels = np.rint(grid).astype(int)
    points = np.stack(np.meshgrid(*levels,indexing="ij"),-1).reshape(-1,3)
    matrix = np.zeros((27,27),np.int64)
    # 独立标量排序与节点步长，未调用证书/插值器的四面体权重函数。
    for row,rgb in enumerate(points):
        base = sum(int(idx[a,rgb[a]])*s for a,s in enumerate((9,3,1)))
        fractions = [int(frac[a,rgb[a]]) for a in range(3)]
        order = sorted(range(3),key=lambda a:(-fractions[a],a))
        f = [fractions[a] for a in order]
        weights = [65536-f[0],f[0]-f[1],f[1]-f[2],f[2]]
        nodes = [base]
        for a in order:nodes.append(nodes[-1]+(9,3,1)[a])
        for node,w in zip(nodes,weights):matrix[row,node] += w
    margin = 4*np.diag(matrix)-matrix.sum(axis=0)-matrix.sum(axis=1)
    certificate = sc.certify(grid,idx,frac)
    assert certificate["minimum_twice_symmetric_margin_q16"] == int(margin.min())
    design = matrix/65536
    exact_numeric = np.linalg.eigvalsh(design.T @ design/64)[0]
    assert 0 < certificate["hessian_eigenvalue_lower_bound"] <= exact_numeric+1e-14
    # 证书绑定权威表；不能默默丢弃序列化后的分数。
    changed = frac.copy()
    changed[0,73] += 1
    assert sc.certify(grid,idx,changed)["axis_tables_sha256"] != certificate["axis_tables_sha256"]


def test_failed_witness_is_rejected_without_claiming_rank_deficiency():
    with pytest.raises(ValueError,match="不代表设计必然秩亏"):
        sc.certify(np.tile([0.,.25,255.],(3,1)))
    # 见证互异但对称部分不够占优，也必须显式拒绝，不能只检查正对角。
    with pytest.raises(ValueError,match="整数余量检查"):
        sc.certify(np.tile([0.,1.49,255.],(3,1)))
