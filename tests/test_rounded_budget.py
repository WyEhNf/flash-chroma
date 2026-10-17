"""真实舍入预算统计的独立整数展开、重叠反例和公开补偿路径。"""
import math
import numpy as np
import pytest
pytest.importorskip("numba",reason="舍入预算补偿研究使用可选Numba环境")
from lutlab import io,interp,tail_repair as tr,full_domain_guard as fg,quantile_constraints as qc,quantile_repair as qr,rounded_budget as rb


def upper(values):
    result = []
    for value in values:
        n = int(value) << 48
        root = math.isqrt(n)
        result.append(root+int(root*root != n))
    return np.array(result,np.int64)


def test_rounded_statistics_match_all_independent_single_changes():
    rng = np.random.default_rng(2026101703)
    model = io.SparseLut(io.uniform_grid(3),rng.integers(0,256,(3,3,3,3),dtype=np.uint8))
    model.nodes[0,0,0,0] = 0
    model.nodes[-1,-1,-1,2] = 255
    points = np.concatenate((np.array([[0,0,0],[127,128,255],[255,255,255]],np.uint8),rng.integers(0,256,(14,3),dtype=np.uint8)))
    prediction = interp.apply_tetra_q16(model,points)
    truth = np.clip(prediction.astype(np.int32)+rng.integers(-5,6,prediction.shape),0,255).astype(np.uint8)
    domain = fg.DomainGuard([model],points,truth)
    counts = rng.integers(1,4,(2,len(points)),dtype=np.uint32)
    inverse = qc.invert(np.tile(np.arange(len(points),dtype=np.uint32),2),np.repeat(np.arange(2,dtype=np.uint8),len(points)),counts.ravel(),len(points),2)
    photos = qc.GroupState(inverse,2,np.maximum(domain.squared-2,0),domain.squared,[[0,1]])
    with pytest.raises(MemoryError):rb.statistics(model,domain,photos,max_array_bytes=1)
    actual = rb.statistics(model,domain,photos,chunk=5)
    frequency = np.concatenate((counts.astype(np.int64),np.ones((1,len(points)),np.int64)))
    for node in range(model.m**3):
        for option in range(6):
            value = model.nodes.reshape(-1,3)[node].astype(np.int32)
            value[option//2] += 2*(option%2)-1
            if not 0 <= value[option//2] <= 255:
                assert not np.any(actual[node,option])
                continue
            candidate = tr.clone([model])[0]
            candidate.nodes.reshape(-1,3)[node] = value
            mapped = interp.apply_tetra_q16(candidate,points)
            squared = np.sum((mapped.astype(np.int32)-truth)**2,axis=1)
            np.testing.assert_array_equal(actual[node,option,:,0],frequency @ (squared-domain.squared))
            np.testing.assert_array_equal(actual[node,option,:,1],frequency @ (upper(squared)-upper(domain.squared)))


def test_overlapping_rounding_prevents_adding_single_statistics():
    model = io.SparseLut(io.uniform_grid(2),np.full((2,2,2,3),100,np.uint8))
    points = np.array([[85,170,0]],np.uint8)
    domain = fg.DomainGuard([model],points,np.full((1,3),100,np.uint8))
    inverse = qc.invert(np.array([0],np.uint32),np.array([0],np.uint8),np.array([1],np.uint32),1,1)
    photos = qc.GroupState(inverse,1,np.array([0],np.int32),domain.squared,[[0]],bins=64)
    actual = rb.statistics(model,domain,photos)
    assert actual[0,1,-1,0] == 0 and actual[2,1,-1,0] == 0
    candidate = tr.clone([model])[0]
    candidate.nodes.reshape(-1,3)[[0,2],0] += 1
    mapped = interp.apply_tetra_q16(candidate,points)
    assert mapped[0,0] == 101 and np.sum((mapped.astype(np.int32)-100)**2) == 1


def test_rounded_backend_preserves_real_joint_guard_acceptance():
    model = io.SparseLut(io.uniform_grid(2),np.full((2,2,2,3),100,np.uint8))
    points = np.array([[0,0,0],[127,0,0],[255,255,255]],np.uint8)
    truth = np.array([[101,100,100],[100,100,100],[101,100,100]],np.uint8)
    inverse = qc.invert(np.arange(3,dtype=np.uint32),np.array([0,1,1],np.uint8),np.array([1,2,3],np.uint32),3,2)
    domain = fg.DomainGuard([model],points,truth)
    photos = qc.GroupState(inverse,2,np.array([0,0,1],np.int32),domain.squared,[[0,1]],bins=64)
    baseline = qr.repair(model,[],domain,photos,steps=1,focus_count=1,trial_limit=32,pair_nodes=0)
    assert not baseline["accepted"] and photos.loss == 1
    result = qr.repair(model,[],domain,photos,steps=1,focus_count=1,trial_limit=32,pair_nodes=0,
        compensation={"method":"rounded","rounds":1,"primary_limit":4,"helper_limit":8,"max_array_bytes":1 << 28})
    assert photos.loss == 0 and result["compensation_rounds"][0]["method"] == "rounded"
    assert result["accepted"][0]["compensation"]["helper_node"] == 7
    assert photos.report()["guards_accepted"]
    np.testing.assert_array_equal(domain.prediction,interp.apply_tetra_q16(model,points))
