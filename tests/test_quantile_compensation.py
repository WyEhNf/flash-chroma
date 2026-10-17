"""补偿矩对独立稠密代数，以及焦点外节点解除RMS停滞的真实整数合同。"""
import numpy as np
import pytest
pytest.importorskip("numba",reason="分位补偿研究使用可选Numba环境")
from lutlab import io,interp,full_domain_guard as fg,quantile_constraints as qc,quantile_compensation as cm,quantile_repair as qr


def setup():
    model = io.SparseLut(io.uniform_grid(2),np.full((2,2,2,3),100,np.uint8))
    points = np.array([[0,0,0],[127,0,0],[255,255,255]],np.uint8)
    truth = np.array([[101,100,100],[100,100,100],[101,100,100]],np.uint8)
    inverse = qc.invert(np.array([0,1,2],np.uint32),np.array([0,1,1],np.uint8),np.array([1,2,3],np.uint32),3,2)
    domain = fg.DomainGuard([model],points,truth)
    photos = qc.GroupState(inverse,2,np.array([0,0,1],np.int32),domain.squared,[[0,1]],bins=64)
    return model,points,truth,domain,photos


def test_compensation_moments_match_dense_weighted_design():
    model,points,truth,domain,photos = setup()
    gradient,diagonal = cm.moments(model,domain,photos,chunk=2)
    indices,weights = interp.tetra_index_weights_q(points,*model.tables(),2)
    A = np.zeros((3,8),np.int64)
    for r in range(3):
        for node,w in zip(indices[r],weights[r]):A[r,node] += int(w)
    error = domain.prediction.astype(np.int64)-truth
    for g,frequency in enumerate(([1,0,0],[0,2,3],[1,1,1])):
        w = np.asarray(frequency,np.int64)
        np.testing.assert_array_equal(gradient[:,g],A.T @ (w[:,None]*error))
        np.testing.assert_array_equal(diagonal[:,g],(A*A).T @ w)


def test_global_helper_repairs_tail_without_relaxing_rms_guard():
    model,points,truth,domain,photos = setup()
    baseline = qr.repair(model,[],domain,photos,steps=1,focus_count=1,trial_limit=32,pair_nodes=0)
    assert not baseline["accepted"] and photos.loss == 1
    # 只有节点0有尾部缺口，但它的R+1会伤害图片1的多数像素；节点7在焦点支撑之外。
    result = qr.repair(model,[],domain,photos,steps=1,focus_count=1,trial_limit=32,pair_nodes=0,
        compensation={"rounds":1,"primary_limit":4,"helper_limit":8,"max_array_bytes":1 << 28})
    assert result["accepted"] and photos.loss == 0 and result["compensation_rounds"][0]["accepted"]
    assert result["accepted"][0]["compensation"]["helper_node"] == 7
    report = photos.report()
    assert report["guards_accepted"] and report["groups"][0]["metrics"]["mean"] == 0
    np.testing.assert_array_equal(domain.prediction,interp.apply_tetra_q16(model,points))
    np.testing.assert_array_equal(photos.current,domain.squared)
