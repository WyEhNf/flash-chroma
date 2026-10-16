"""全颜色截断下界对独立加权像素展开，以及真实热点覆盖盲区合同。"""
import numpy as np
import pytest
pytest.importorskip("numba",reason="全节点分位排序研究使用可选Numba环境")
from lutlab import io,interp,tail_repair as tr,full_domain_guard as fg,quantile_constraints as qc,quantile_global as qg,quantile_repair as qr


def test_global_scores_match_expanded_frozen_trim_and_bound_true_loss():
    rng = np.random.default_rng(2026101702)
    model = io.SparseLut(io.uniform_grid(3),rng.integers(0,256,(3,3,3,3),dtype=np.uint8))
    points = rng.integers(0,256,(31,3),dtype=np.uint8)
    prediction = interp.apply_tetra_q16(model,points)
    truth = np.clip(prediction.astype(np.int32)+rng.integers(-3,4,(31,3)),0,255).astype(np.uint8)
    domain = fg.DomainGuard([model],points,truth)
    keys = np.tile(np.arange(31,dtype=np.uint32),2)
    groups = np.repeat(np.arange(2,dtype=np.uint8),31)
    counts = rng.integers(1,4,len(keys),dtype=np.uint32)
    inverse = qc.invert(keys,groups,counts,31,2)
    original = np.maximum(domain.squared-2,0)
    photos = qc.GroupState(inverse,2,original,domain.squared,[[0,1]])
    ranked,info = qg.ranked(model,domain,photos,chunk=7)
    actual = {move:score for score,move in ranked}
    expected = {}
    for node in range(model.m**3):
        for channel in range(3):
            for sign in (-1,1):
                value = model.nodes.reshape(-1,3)[node].astype(np.int32)
                value[channel] += sign
                if not 0 <= value[channel] <= 255:continue
                candidate = io.SparseLut(model.grid.copy(),model.nodes.copy(),*(a.copy() for a in model.tables()))
                candidate.nodes.reshape(-1,3)[node] = value
                new = interp.apply_tetra_q16(candidate,points)
                squared = np.sum((new.astype(np.int32)-truth)**2,axis=1)
                score = 0
                for g in range(2):
                    for row,weight in enumerate(counts[g*31:(g+1)*31]):
                        for t,b,u in zip(photos.thresholds[g],photos.budgets[g],photos.cutoffs[g]-photos.thresholds[g]):
                            if b >= 0:score += int(weight)*(min(max(int(squared[row])-int(t),0),int(u))-min(max(int(domain.squared[row])-int(t),0),int(u)))
                if score < 0:
                    move = tr.Move(0,node,tuple(map(int,value)))
                    expected[move] = score
                    trial = photos.trial(np.arange(31),domain.squared,squared)
                    assert trial.loss-photos.loss >= score
    assert expected and actual == expected and info["anchor_loss"] == photos.loss


def test_global_candidates_fix_colour_outside_hotspot_support():
    model = io.SparseLut(io.uniform_grid(2),np.full((2,2,2,3),100,np.uint8))
    points = np.array([[0,0,0],[127,0,0],[255,255,255]],np.uint8)
    truth = np.array([[101,100,100],[100,100,100],[101,100,100]],np.uint8)
    domain = fg.DomainGuard([model],points,truth)
    inverse = qc.invert(np.arange(3,dtype=np.uint32),np.arange(3,dtype=np.uint8),np.array([10,100,1],np.uint32),3,3)
    photos = qc.GroupState(inverse,3,np.zeros(3,np.int32),domain.squared,[[0,1,2]])
    baseline = qr.repair(model,[],domain,photos,steps=1,focus_count=1,trial_limit=32,pair_nodes=0)
    assert not baseline["accepted"] and photos.loss == 11
    result = qr.repair(model,[],domain,photos,steps=1,focus_count=1,trial_limit=32,pair_nodes=0,
        global_search={"rounds":1,"max_array_bytes":1 << 28})
    assert photos.loss == 10 and result["accepted"][0]["proposal_source"] == "global_single"
    assert result["accepted"][0]["moves"][0]["node"] == 7
    assert result["global_rounds"][0]["trials"][0]["photo_failed"]
    np.testing.assert_array_equal(domain.prediction,interp.apply_tetra_q16(model,points))
