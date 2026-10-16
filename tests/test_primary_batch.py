"""真实整数映射上的有限批次收益、尾部预算共享和空候选公开路径。"""
import numpy as np
import pytest
pytest.importorskip("numba",reason="主改批次使用可选Numba研究环境")
from lutlab import io,interp,full_domain_guard as fg,quantile_constraints as qc,quantile_repair as qr
from lutlab.stability import Stability


def state(points,red,counts,groups,original,n_groups,m=5):
    points = np.asarray(points,np.uint8)
    truth = np.full(points.shape,100,np.uint8)
    truth[:,0] = red
    model = io.SparseLut(io.uniform_grid(m),np.full((m,m,m,3),100,np.uint8))
    domain = fg.DomainGuard([model],points,truth)
    inverse = qc.invert(np.arange(len(points),dtype=np.uint32),np.asarray(groups,np.uint8),np.asarray(counts,np.uint32),len(points),n_groups)
    photos = qc.GroupState(inverse,n_groups,np.asarray(original,np.int32),domain.squared,[list(range(n_groups))])
    photos.stability = Stability(photos,domain,tail_ranking=False)
    return model,domain,photos


def run(model,domain,photos,batch=None,trial_limit=32,compensation=None):
    config = {"method":"primary_budget","ordering":"constraints","rounds":1,"max_array_bytes":1 << 28}
    if batch is not None:config["batch"] = batch
    return qr.repair(model,[],domain,photos,steps=1,focus_count=1,trial_limit=trial_limit,pair_nodes=0,
        global_search=config,compensation=compensation)


@pytest.mark.parametrize("safe_count",[2,3])
def test_public_batch_commits_more_true_gain_than_any_single(safe_count):
    outcomes = {}
    for name,batch in (("first",None),("batch",{"feasible_limit":8,"max_order":3})):
        points = [[0,0,0],[31,0,0],[255,0,0],[255,255,255]]+([[0,255,255]] if safe_count == 3 else [])
        counts = [1000,10000,10,20]+([30] if safe_count == 3 else [])
        model,domain,photos = state(points,[101,100]+[101]*safe_count,counts,range(len(points)),[0]*len(points),len(points))
        result = run(model,domain,photos,batch)
        outcomes[name] = (photos.loss,result)
        assert photos.stability.certificate(photos,domain.hist)["accepted"]
        np.testing.assert_array_equal(domain.prediction,interp.apply_tetra_q16(model,np.asarray(points,np.uint8)))
        photos.recheck()
    assert outcomes["batch"][0] == 1000 < outcomes["first"][0]
    result = outcomes["batch"][1]
    record = result["accepted"][0]
    details = result["global_rounds"][0]["batch_search"]
    assert record["proposal_source"] == "global_batch" and len(record["moves"]) == safe_count
    assert details["selected_better_than_best_single"] and details["selected_loss"] < details["best_single_loss"]
    assert len(details["feasible_singles"]) == safe_count and result["global_batch_confirmations"] == 1
    assert len(details["trials"]) == (1 if safe_count == 2 else 4)


def test_individually_safe_disjoint_moves_can_exhaust_same_p99_budget():
    points = [[0,0,0],[31,0,0],[255,0,0],[255,255,255],
        [239,0,0],[255,16,0],[239,255,255],[255,239,255],[128,128,128],[128,128,0],[128,0,128]]
    model,domain,photos = state(points,[101,100,101,101,99,103,99,103,103,99,100],
        [1000,10000,10,10,1,1,1,1,1,2,394],[0,1,2,3,4,4,4,4,4,4,4],[0,0,0,0,1,9,1,9,9,1,0],5)
    assert photos.loss == 1020
    result = run(model,domain,photos,{"feasible_limit":8,"max_order":3})
    details = result["global_rounds"][0]["batch_search"]
    assert len(details["feasible_singles"]) == 2 and len(details["trials"]) == 1
    combined = details["trials"][0]
    # 两个单改各耗1尾部余量，合改耗2；预算只剩1。单改损失变化相加也不是组合真实损失。
    assert combined["sum_single_loss_delta"] == -20 and combined["loss"] == 1003
    assert combined["decision"] == "photo_guard" and "stability.group4.tail0" in combined["photo_failed"]
    assert photos.loss == 1010 and details["selected_node_count"] == 1 and not details["selected_better_than_best_single"]
    assert photos.stability.certificate(photos,domain.hist)["accepted"]
    np.testing.assert_array_equal(domain.prediction,interp.apply_tetra_q16(model,np.asarray(points,np.uint8)))


def test_no_feasible_batch_retains_empty_helper_fallback_and_validates_limits():
    points = [[0,0,0],[127,0,0],[255,255,255]]
    model,domain,photos = state(points,[101,100,101],[10,100,1],[0,1,2],[0,0,0],3,m=2)
    config = {"method":"primary_budget","ordering":"tail","rounds":1,"max_array_bytes":1 << 28,
        "batch":{"feasible_limit":8,"max_order":3}}
    result = qr.repair(model,[],domain,photos,steps=1,focus_count=1,trial_limit=1,pair_nodes=0,global_search=config,
        compensation={"method":"rounded","rounds":1,"primary_limit":2,"helper_limit":4,"max_array_bytes":1 << 28,
            "primary_order":"ranked","block_order":3,"first_helpers":2,"second_helpers":2})
    assert not result["accepted"] and photos.loss == 11 and result["global_batch_confirmations"] == 0
    assert not result["global_rounds"][0]["batch_search"]["feasible_singles"]
    assert result["compensation_rounds"][0]["block_search"]["triples"] == 0
    with pytest.raises(ValueError):
        qr.repair(model,[],domain,photos,global_search={**config,"batch":{"feasible_limit":8,"max_order":2.0}})
