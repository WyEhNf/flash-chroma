"""冻结参照的误差转移拒绝、事务回滚、精确尾部统计和三节点公开路径。"""
import numpy as np
import pytest
pytest.importorskip("numba",reason="冻结参照研究使用可选Numba环境")
from lutlab import io,interp,tail_repair as tr,full_domain_guard as fg,quantile_constraints as qc,quantile_repair as qr,rounded_budget as rb
from lutlab.stability import Stability


def test_stability_rejects_transfer_and_rolls_back_exactly():
    model = io.SparseLut(io.uniform_grid(2),np.full((2,2,2,3),100,np.uint8))
    points = np.array([[0,0,0],[255,255,255]],np.uint8)
    truth = np.array([[101,100,100],[102,100,100]],np.uint8)
    domain = fg.DomainGuard([model],points,truth)
    inverse = qc.invert(np.arange(2,dtype=np.uint32),np.arange(2,dtype=np.uint8),np.ones(2,np.uint32),2,2)
    photos = qc.GroupState(inverse,2,np.array([25,25],np.int32),domain.squared,[[0,1]],bins=64)
    rows,old,new = np.arange(2,dtype=np.int32),domain.squared.copy(),np.array([4,1],np.int32)
    assert not photos.trial(rows,old,new).failed
    photos.stability = quality = Stability(photos,domain,tail_ranking=True)
    before,tails = photos.hist.copy(),quality.photo_tails.copy()
    trial = photos.trial(rows,old,new)
    assert "stability.group0.rms" in trial.failed and "stability.group0.tail0" in trial.failed
    np.testing.assert_array_equal(photos.hist,before)
    np.testing.assert_array_equal(quality.photo_tails,tails)
    photos.recheck()
    with pytest.raises(ValueError):photos.commit(trial)
    with pytest.raises(ValueError):Stability(photos,domain,tail_ranking=True)
    # 同一非平方距离直方图无需误用Q24上下界拒绝自身。
    irrational = np.zeros_like(domain.hist)
    irrational[2] = 2
    quality.full_hist = irrational
    quality.full_reference = fg.summary(irrational)
    quality.thresholds[-1] = 2
    quality.budgets[-1] = 0
    assert not quality.check_full(irrational,fg.summary(irrational))


def test_tail_statistics_match_every_independent_single_change_with_large_counts():
    rng = np.random.default_rng(2026101704)
    model = io.SparseLut(io.uniform_grid(3),rng.integers(1,255,(3,3,3,3),dtype=np.uint8))
    points = np.concatenate((np.array([[0,0,0],[127,128,255],[255,255,255]],np.uint8),rng.integers(0,256,(6,3),dtype=np.uint8)))
    prediction = interp.apply_tetra_q16(model,points)
    truth = np.clip(prediction.astype(np.int32)+rng.integers(-3,4,prediction.shape),0,255).astype(np.uint8)
    domain = fg.DomainGuard([model],points,truth)
    counts = np.ones((2,len(points)),np.uint32)
    counts[0,0] = (1 << 29)-8
    counts[1,-1] = (1 << 29)-8
    inverse = qc.invert(np.tile(np.arange(len(points),dtype=np.uint32),2),np.repeat(np.arange(2,dtype=np.uint8),len(points)),counts.ravel(),len(points),2)
    photos = qc.GroupState(inverse,2,domain.squared,domain.squared,[[0,1]])
    photos.stability = quality = Stability(photos,domain,tail_ranking=True)
    with pytest.raises(MemoryError):rb.statistics(model,domain,photos,max_array_bytes=1,tail_cache={})
    cache = {}
    rb.statistics(model,domain,photos,chunk=4,tail_cache=cache)
    tensor = cache["tail_deltas"]
    assert tensor.dtype == np.int32 and tensor.shape == (27,6,3,3)
    frequency = np.concatenate((counts.astype(np.int64),np.ones((1,len(points)),np.int64)))
    for node in range(27):
        for option in range(6):
            candidate = tr.clone([model])[0]
            candidate.nodes.reshape(-1,3)[node,option//2] += 2*(option%2)-1
            mapped = interp.apply_tetra_q16(candidate,points)
            squared = np.sum((mapped.astype(np.int32)-truth)**2,axis=1)
            for g in range(3):
                for j in range(3):
                    t,b = quality.thresholds[g,j],quality.budgets[g,j]
                    expected = int(frequency[g] @ ((squared > t).astype(np.int64)-(domain.squared > t))) if b >= 0 else 0
                    assert int(tensor[node,option,g,j]) == expected
    # 重叠的三份估计可超过int32；组合必须先升为int64，不能先相加再转换。
    combined = tensor[0,1].astype(np.int64)+tensor[0,1]+tensor[0,1]
    np.testing.assert_array_equal(combined,3*tensor[0,1].astype(np.int64))


def test_stability_accepts_public_three_node_repair_with_tail_ranking():
    model = io.SparseLut(io.uniform_grid(2),np.full((2,2,2,3),100,np.uint8))
    points = np.array([[0,0,0],[63,0,0],[0,255,0],[255,0,255]],np.uint8)
    truth = np.array([[101,100,100],[100,100,100],[101,100,100],[101,100,100]],np.uint8)
    inverse = qc.invert(np.arange(4,dtype=np.uint32),np.array([0,1,1,1],np.uint8),np.array([1,3,2,2],np.uint32),4,2)
    domain = fg.DomainGuard([model],points,truth)
    photos = qc.GroupState(inverse,2,np.array([0,0,1,1],np.int32),domain.squared,[[0,1]],bins=64)
    photos.stability = quality = Stability(photos,domain,tail_ranking=True)
    result = qr.repair(model,[],domain,photos,steps=2,focus_count=1,trial_limit=32,pair_nodes=0,
        compensation=dict(method="rounded",rounds=1,primary_limit=4,helper_limit=8,max_array_bytes=1 << 28,block_order=3,first_helpers=4,second_helpers=4))
    assert photos.loss == 0 and result["accepted"][0]["stability"]["accepted"]
    assert len(result["accepted"][0]["moves"]) == 3
    assert quality.certificate(photos,domain.hist)["accepted"]
    photos.recheck()
    np.testing.assert_array_equal(domain.prediction,interp.apply_tetra_q16(model,points))
