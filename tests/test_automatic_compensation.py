"""条件排序、必要第二辅助及局部状态覆盖的真实整数映射合同。"""
import numpy as np
import pytest
from lutlab import automatic_compensation as ac,interp,io


def state(model,points,target,allowed=None):
    old = np.sum((interp.apply_tetra_q16(model,points).astype(int)-target)**2,axis=1)
    groups = [{"histogram":[[int(d),1]],"constraints":[{"threshold_squared":int(d),"allowed_tail_pixels":0}],"costs":[0]} for d in old]
    return ac.ConditionalScorer(model,points,target,np.eye(len(points),dtype=np.int64),{"groups":groups,"loss":0},
        ac.pairs(np.bincount(old)),list(range(model.m**3)) if allowed is None else allowed)


def test_conditional_ranking_selects_safe_helper_instead_of_larger_single_gain():
    model = io.SparseLut(io.uniform_grid(2),np.full((2,2,2,3),100,np.uint8))
    points = np.array([[0,0,0],[0,0,64],[0,0,128],[0,0,255]],np.uint8)
    target = np.full(points.shape,100,np.uint8)
    target[:,2] = [98,100,100,102]
    frame = state(model,points,target)
    primary = ac.clone(model)
    primary.nodes[0,0,0,2] = 99
    ranked = ac.ranked_helpers(model,primary,frame,ac.neighbors(model,[0]),deltas=(-2,-1,1,2))
    best = ranked[0]
    assert best["helper"] == {"node":1,"channel":2,"delta":1} and not best["score"]["fixed_failed"]
    larger = next(r for r in ranked if r["helper"] == {"node":1,"channel":2,"delta":2})
    assert larger["score"]["fixed_failed"] and best["rank_key"] < larger["rank_key"]
    assert frame.score(primary)["fixed_failed"] and np.all(model.nodes == 100)
    model.nodes[0,0,0,2] = 101
    with pytest.raises(ValueError,match="签名"):ac.ranked_helpers(model,primary,frame,[1])


def test_second_helper_is_scored_on_real_conditional_three_node_block():
    model = io.SparseLut(io.uniform_grid(2),np.full((2,2,2,3),100,np.uint8))
    points = np.array([[0,0,0],[127,0,0],[0,127,0]],np.uint8)
    target = np.full(points.shape,100,np.uint8)
    target[0,0] = 101
    frame = state(model,points,target)
    primary = ac.clone(model)
    primary.nodes[0,0,0,0] = 101
    pool = ac.neighbors(model,[0])
    first = ac.ranked_helpers(model,primary,frame,pool,deltas=(-1,1))[0]
    pair = ac.apply_helper(primary,model,first["helper"])
    assert first["score"]["fixed_failed"]
    second = ac.ranked_helpers(model,pair,frame,pool,deltas=(-1,1))[0]
    triple = ac.apply_helper(pair,model,second["helper"])
    assert {first["helper"]["node"],second["helper"]["node"]} == {2,4}
    assert not second["score"]["fixed_failed"] and second["score"]["max_squared"] == 0
    np.testing.assert_array_equal(interp.apply_tetra_q16(triple,points),target)


def test_channel_aware_primary_and_uncovered_node_refusal():
    pytest.importorskip("scipy",reason="主改整数求解使用可选SciPy")
    from lutlab.local_minimax import minimum_change
    model = io.SparseLut(io.uniform_grid(3),np.full((3,3,3,3),100,np.uint8))
    points = np.array([[0,0,0]],np.uint8)
    target = np.array([[98,100,100]],np.uint8)
    candidate,info = minimum_change(model,points,target,rgb_max=1,max_delta=2,channel=0)
    assert info["success"] and candidate.nodes[0,0,0].tolist() == [99,100,100]
    frame = state(model,points,target,allowed=[0])
    candidate.nodes[-1,-1,-1,0] = 99
    with pytest.raises(ValueError,match="支撑之外"):frame.score(candidate)
