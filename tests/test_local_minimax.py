"""用穷举可证最优的小例验证整数必要界、连续见证和联合最小修改。"""
import itertools
import numpy as np
import pytest
pytest.importorskip("scipy",reason="局部最小最大研究使用可选SciPy/HiGHS环境")
from lutlab import interp,io,local_minimax as lm


def test_integer_certificate_reaches_exhaustive_two_node_optimum():
    model = io.SparseLut(io.uniform_grid(2),np.zeros((2,2,2,3),np.uint8))
    points = np.array([[0,0,0],[127,0,0],[255,0,0]],np.uint8)
    targets = np.array([[0,0,0],[0,0,200],[0,0,0]],np.uint8)
    q = int(model.tables()[1][0,127])
    proof = lm.combination_bound(model,points,targets,[65536-q,-65536,q])
    first,second = np.meshgrid(np.arange(256,dtype=np.int64),np.arange(256,dtype=np.int64),indexing="ij")
    middle = ((65536-q)*first+q*second+32768)//65536
    optimum = int(np.min(np.maximum.reduce([first,second,np.abs(middle-200)])))
    assert optimum == proof["rgb_l2_max_lower_bound"] == 100 and proof["node_coefficients"] == []
    with pytest.raises(ValueError):lm.combination_bound(model,points,targets,[1.,-2.,1.])
    with pytest.raises(ValueError):lm.combination_bound(model,points,targets,[0,0,0])


def test_relaxed_witness_and_joint_integer_changes_use_actual_rgb_rounding():
    points = np.array(list(itertools.product((0,127,255),repeat=3)),np.uint8)
    model = io.SparseLut(io.uniform_grid(2),np.full((2,2,2,3),10,np.uint8))
    model.nodes[...,2] = 100
    targets = np.full(points.shape,10,np.uint8)
    targets[:,2] = 90
    relaxed,info = lm.relaxed_minimax(model,points,targets)
    assert abs(info["continuous_objective"]) < 1e-10 and info["certificate"]["rgb_l2_max_lower_bound"] == 0
    np.testing.assert_array_equal(interp.apply_tetra_q16(relaxed,points),targets)
    integer,info = lm.minimum_change(model,points,targets,rgb_max=9,max_delta=2)
    assert info["success"] and info["l1_change"] == 8 and np.all(integer.nodes[...,2] == 99)
    assert int(np.max(np.sum((interp.apply_tetra_q16(integer,points).astype(int)-targets)**2,axis=1))) == 81
    none,info = lm.minimum_change(model,points,targets,rgb_max=7,max_delta=2)
    assert none is None and not info["success"]
