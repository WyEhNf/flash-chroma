"""独立展开像素核对预算、频数事务及真实双节点/搜索接入。"""
import numpy as np
import pytest
pytest.importorskip("numba",reason="分位约束研究使用可选Numba环境")
from lutlab import quantile_constraints as qc, quantile_repair as qr, full_domain_guard as fg, interp, io, tail_repair as tr


def state(keys,groups,counts,original,current,n_groups=1):
    inverse = qc.invert(np.array(keys,np.uint32),np.array(groups,np.uint8),np.array(counts,np.uint32),len(original),n_groups)
    return qc.GroupState(inverse,n_groups,np.array(original,np.int32),np.array(current,np.int32),[list(range(n_groups))],bins=64)


def expanded_hist(keys,groups,counts,errors,g,bins=64):
    pixels = [int(errors[c]) for c,group,count in zip(keys,groups,counts) if group == g for _ in range(int(count))]
    return np.bincount(pixels,minlength=bins),pixels


def test_p99_budget_keeps_permitted_outlier_and_matches_expanded_minimal_excess():
    s = state([0,1,2],[0,0,0],[99,1,1],[0,0,25],[0,1,25])
    assert s.loss == 1
    _,pixels = expanded_hist([0,1,2],[0,0,0],[99,1,1],s.current,0)
    for j,(threshold,budget) in enumerate(zip(s.thresholds[0],s.budgets[0])):
        if budget < 0:continue
        excess = sorted(d-threshold for d in pixels if d > threshold)
        assert s.costs[0,j] == sum(excess[:max(0,len(excess)-budget)])
    trial = s.trial(np.array([1]),np.array([1]),np.array([0]))
    assert trial.loss == 0 and not trial.failed
    s.commit(trial)
    assert s.current[2] == 25 and s.loss == 0
    assert np.quantile(np.sqrt(np.array([0]*100+[25])),.99) == 0


def test_weighted_shared_colour_trial_rollback_commit_and_stale_receipt():
    keys,groups,counts = [0,1,0,2],[0,0,1,1],[2,98,3,98]
    s = state(keys,groups,counts,[0,0,0],[9,4,1],2)
    original = [x.copy() for x in (s.hist,s.low,s.high,s.sse,s.tails,s.current)]
    trial = s.trial(np.array([0]),np.array([9]),np.array([4]))
    assert trial.loss < s.loss and not trial.failed
    assert all(np.array_equal(a,b) for a,b in zip(original,(s.hist,s.low,s.high,s.sse,s.tails,s.current)))
    s.commit(trial)
    for g in range(2):
        expected,_ = expanded_hist(keys,groups,counts,s.current,g)
        np.testing.assert_array_equal(s.hist[g],expected)
    s.recheck()
    with pytest.raises(ValueError,match="陈旧"):s.commit(trial)
    with pytest.raises(ValueError,match="陈旧"):s.trial(np.array([0]),np.array([9]),np.array([0]))
    with pytest.raises(ValueError,match="重复"):s.trial(np.array([0,0]),np.array([4,4]),np.array([0,0]))
    rejected = s.trial(np.array([1]),np.array([4]),np.array([25]))
    assert rejected.failed
    s.recheck()


def test_distinct_rank_endpoints_are_sufficient_and_explicitly_conservative():
    s = state([0,1],[0,0],[1,1],[0,4],[1,1])
    assert np.quantile(np.sqrt([1,1]),.99) < np.quantile(np.sqrt([0,4]),.99)
    assert s.loss > 0  # 实际p99较小仍可能不满足逐端点充分条件，不谎称必要条件。
    assert (0,1) in qc.endpoints(np.array([1,0,0,0,1]))
    with pytest.raises(ValueError):qc.invert(np.array([0],np.uint32),np.array([0],np.uint8),np.array([0],np.uint32),2,1)


def test_joint_delta_and_public_search_match_independent_integer_oracle():
    grid = io.uniform_grid(3)
    model = io.SparseLut(grid,np.full((3,3,3,3),100,np.uint8))
    desired = tr.clone([model])[0]
    desired.nodes.reshape(-1,3)[0] = (98,101,100)
    desired.nodes.reshape(-1,3)[1] = (101,100,99)
    points = np.stack(np.meshgrid(*([np.array([0,51,102,153,204,255],np.uint8)]*3),indexing="ij"),-1).reshape(-1,3)
    truth = interp.apply_tetra_q16(desired,points)
    keys = np.tile(np.arange(len(points),dtype=np.uint32),2)
    groups = np.repeat(np.arange(2,dtype=np.uint8),len(points))
    counts = (1+np.arange(len(keys))%5).astype(np.uint32)
    inverse = qc.invert(keys,groups,counts,len(points),2)
    domain = fg.DomainGuard([model],points,truth)
    photos = qc.GroupState(inverse,2,np.zeros(len(points),np.int32),domain.squared,[list(range(2))])
    move = fg.JointMove((tr.Move(0,0,(98,101,100)),tr.Move(0,1,(101,100,99))))
    trial = domain.trial([model],move)
    prediction = domain.prediction.copy()
    prediction[trial["rows"]] = trial["prediction"]
    np.testing.assert_array_equal(prediction,truth)
    photo_trial = photos.trial(trial["rows"],domain.squared[trial["rows"]],trial["squared"])
    assert photo_trial.loss == 0 and not photo_trial.failed
    assert domain.consider([model],move)["accepted"]
    model.nodes[:] = desired.nodes
    domain.commit([model],move)
    photos.commit(photo_trial)
    photos.recheck()
    assert not np.any(photos.current) and photos.loss == 0
    # 另从同一未修复模型经公开搜索入口接受实际提案，核对模型/两层缓存。
    start = io.SparseLut(grid,np.full((3,3,3,3),100,np.uint8))
    domain = fg.DomainGuard([start],points,truth)
    photos = qc.GroupState(inverse,2,np.zeros(len(points),np.int32),domain.squared,[list(range(2))])
    before = photos.loss
    result = qr.repair(start,[desired],domain,photos,steps=2,focus_count=16,trial_limit=32,pair_nodes=4)
    assert result["accepted"] and photos.loss < before
    np.testing.assert_array_equal(domain.prediction,interp.apply_tetra_q16(start,points))
    np.testing.assert_array_equal(domain.squared,photos.current)
    photos.recheck()
