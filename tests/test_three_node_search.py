"""三节点跨级重放与有限候选内必须两辅的真实整数合同。"""
import numpy as np
import pytest
pytest.importorskip("numba",reason="三节点联合搜索使用可选Numba环境")
from lutlab import io,interp,tail_repair as tr,full_domain_guard as fg,quantile_constraints as qc,quantile_repair as qr


def test_three_stage_block_replays_new_support_and_commits_exactly():
    grid = io.uniform_grid(3)
    levels = np.array([0,128,255],np.uint8)
    identity = np.stack(np.meshgrid(levels,levels,levels,indexing="ij"),-1)
    models = [io.SparseLut(grid,np.zeros((3,3,3,3),np.uint8))]+[io.SparseLut(grid,identity.copy()) for _ in range(3)]
    moves = (tr.Move(0,26,(255,255,255)),tr.Move(1,26,(200,210,220)),tr.Move(2,26,(17,32,53)))
    with pytest.raises(ValueError):fg.TripleMove((moves[0],moves[0],moves[1]))
    with pytest.raises(ValueError):fg.JointMove(moves)
    changed = tr.clone(models)
    for move in moves:changed[move.stage].nodes.reshape(-1,3)[move.node] = move.value
    points = np.stack(np.meshgrid(*([np.array([0,255],np.uint8)]*3),indexing="ij"),-1).reshape(-1,3)
    truth = points.copy()
    for model in changed:truth = interp.apply_tetra_q16(model,truth)
    domain = fg.DomainGuard(models,points,truth)
    assert not len(domain.affected(models,moves[1])) and not len(domain.affected(models,moves[2]))
    block = fg.combine(moves)
    trial = domain.trial(models,block)
    actual = domain.prediction.copy()
    actual[trial["rows"]] = trial["prediction"]
    np.testing.assert_array_equal(actual,truth)
    assert domain.consider(models,block)["accepted"]
    for a,b in zip(models,changed):a.nodes[:] = b.nodes
    domain.commit(models,block)
    current = points.copy()
    for stage,model in enumerate(models):
        np.testing.assert_array_equal(domain.inputs[stage],current)
        current = interp.apply_tetra_q16(model,current)
    np.testing.assert_array_equal(domain.prediction,current)
    with pytest.raises(ValueError):domain.commit(models,block)


def test_three_nodes_release_rms_when_every_proper_subset_fails():
    model = io.SparseLut(io.uniform_grid(2),np.full((2,2,2,3),100,np.uint8))
    points = np.array([[0,0,0],[63,0,0],[0,255,0],[255,0,255]],np.uint8)
    truth = np.array([[101,100,100],[100,100,100],[101,100,100],[101,100,100]],np.uint8)
    inverse = qc.invert(np.arange(4,dtype=np.uint32),np.array([0,1,1,1],np.uint8),np.array([1,3,2,2],np.uint32),4,2)
    domain = fg.DomainGuard([model],points,truth)
    photos = qc.GroupState(inverse,2,np.array([0,0,1,1],np.int32),domain.squared,[[0,1]],bins=64)
    config = dict(method="rounded",rounds=1,primary_limit=4,helper_limit=8,max_array_bytes=1 << 28)
    baseline = qr.repair(model,[],domain,photos,steps=1,focus_count=1,trial_limit=32,pair_nodes=0,compensation=config)
    assert not baseline["accepted"] and photos.loss == 1
    result = qr.repair(model,[],domain,photos,steps=2,focus_count=1,trial_limit=32,pair_nodes=0,
        compensation={**config,"block_order":3,"first_helpers":4,"second_helpers":4})
    record = result["accepted"][0]
    assert photos.loss == 0 and record["proposal_source"] == "hotspot_three_node" and len(record["moves"]) == 3
    assert record["compensation"]["all_proper_subsets_rejected"]
    assert result["proper_subset_trials"] == 6 and photos.report()["guards_accepted"]
    assert all(not r["accepted"] for r in result["compensation_rounds"][0]["block_search"]["subset_trials"])
    np.testing.assert_array_equal(domain.prediction,interp.apply_tetra_q16(model,points))
    np.testing.assert_array_equal(photos.current,domain.squared)
