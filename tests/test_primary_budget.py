"""预算主提案的覆盖、独立无变化标志、重叠反例及公开缓存复用合同。"""
import numpy as np
import pytest
pytest.importorskip("numba",reason="预算主提案使用可选Numba研究环境")
from lutlab import io,interp,tail_repair as tr,full_domain_guard as fg,quantile_constraints as qc,quantile_repair as qr,rounded_budget as rb
from lutlab.stability import Stability


def state(points,truth,counts,groups,original,n_groups,m=2,tail_ranking=False):
    model = io.SparseLut(io.uniform_grid(m),np.full((m,m,m,3),100,np.uint8))
    domain = fg.DomainGuard([model],points,truth)
    inverse = qc.invert(np.arange(len(points),dtype=np.uint32),np.asarray(groups,np.uint8),np.asarray(counts,np.uint32),len(points),n_groups)
    photos = qc.GroupState(inverse,n_groups,np.asarray(original,np.int32),domain.squared,[list(range(n_groups))])
    photos.stability = Stability(photos,domain,tail_ranking=tail_ranking)
    return model,domain,photos


def test_changed_histogram_flags_match_all_independent_single_outputs():
    rng = np.random.default_rng(2026101705)
    points = np.concatenate((np.array([[0,0,0],[255,255,255]],np.uint8),rng.integers(0,256,(11,3),dtype=np.uint8)))
    truth = np.clip(100+rng.integers(-3,4,points.shape),0,255).astype(np.uint8)
    groups = np.arange(len(points))%3
    model,domain,photos = state(points,truth,np.ones(len(points)),groups,np.zeros(len(points)),3,m=3)
    cache = {"track_changes":True}
    persistent = domain.cache_bytes+photos.report()["cache_array_bytes"]
    old_size = model.m**3*6*4*2*8
    with pytest.raises(MemoryError):rb.statistics(model,domain,photos,tail_cache=cache,max_array_bytes=persistent+old_size)
    rb.statistics(model,domain,photos,tail_cache=cache,chunk=4)
    flags = cache["hist_changes"]
    assert flags.dtype == np.bool_ and flags.shape == (27,6,4)
    for node in range(27):
        for option in range(6):
            candidate = tr.clone([model])[0]
            candidate.nodes.reshape(-1,3)[node,option//2] += 2*(option%2)-1
            prediction = interp.apply_tetra_q16(candidate,points)
            new = np.sum((prediction.astype(np.int32)-truth)**2,axis=1)
            changed = new != domain.squared
            expected = [bool(np.any(changed[groups == g])) for g in range(3)]+[bool(np.any(changed))]
            np.testing.assert_array_equal(flags[node,option],expected)


def test_unchanged_mean_exemption_is_not_added_across_overlapping_rounding():
    points = np.array([[85,170,0]],np.uint8)
    model,domain,photos = state(points,np.array([[99,99,100]],np.uint8),[1],[0],[2],1)
    cache = {"track_changes":True}
    deltas = rb.statistics(model,domain,photos,tail_cache=cache)
    assert not np.any(cache["hist_changes"][[0,2],1])
    allowed = np.zeros((8,6),bool)
    allowed[2,1] = True
    chosen = rb.rank_helpers(model,domain,photos,deltas,np.zeros((2,2),np.int64),[0],1,
        tail_cache=cache,primary_changes=cache["hist_changes"][0,1],allowed=allowed)
    assert not chosen[0][2]["disjoint_cell_support_certificate"]
    assert chosen[0][2]["rank_mean_failed_count"] > 0
    candidate = tr.clone([model])[0]
    candidate.nodes.reshape(-1,3)[[0,2],0] += 1
    new = interp.apply_tetra_q16(candidate,points)
    assert int(np.sum((new.astype(np.int32)-domain.truth)**2)) == 5 > int(domain.squared[0])


@pytest.mark.parametrize("tail_ranking",[False,True])
def test_primary_budget_selects_safe_colour_with_same_one_trial_limit(tail_ranking):
    outcomes = {}
    for ordering in ("tail","constraints"):
        points = np.array([[0,0,0],[127,0,0],[255,255,255]],np.uint8)
        truth = np.array([[101,100,100],[100,100,100],[101,100,100]],np.uint8)
        model,domain,photos = state(points,truth,[10,100,1],[0,1,2],[0,0,0],3,tail_ranking=tail_ranking)
        result = qr.repair(model,[],domain,photos,steps=1,focus_count=1,trial_limit=1,pair_nodes=0,
            global_search={"method":"primary_budget","ordering":ordering,"rounds":1,"max_array_bytes":1 << 28},
            compensation={"method":"rounded","rounds":1,"primary_limit":2,"helper_limit":4,"max_array_bytes":1 << 28,
                "primary_order":"ranked","block_order":3,"first_helpers":2,"second_helpers":2})
        outcomes[ordering] = (photos.loss,result)
        assert photos.stability.certificate(photos,domain.hist)["accepted"]
        np.testing.assert_array_equal(domain.prediction,interp.apply_tetra_q16(model,points))
    assert outcomes["tail"][0] == 11 and not outcomes["tail"][1]["accepted"]
    empty = outcomes["tail"][1]["compensation_rounds"][0]
    assert empty["primaries"] == 0 and empty["block_search"]["triples"] == 0
    assert outcomes["constraints"][0] == 10
    accepted = outcomes["constraints"][1]["accepted"][0]
    assert accepted["proposal_source"] == "global_single" and accepted["moves"][0]["node"] == 7


def test_primary_statistics_reused_by_public_three_node_path():
    points = np.array([[0,0,0],[63,0,0],[0,255,0],[255,0,255]],np.uint8)
    truth = np.array([[101,100,100],[100,100,100],[101,100,100],[101,100,100]],np.uint8)
    model,domain,photos = state(points,truth,[1,3,2,2],[0,1,1,1],[0,0,1,1],2)
    result = qr.repair(model,[],domain,photos,steps=1,focus_count=1,trial_limit=32,pair_nodes=0,
        global_search={"method":"primary_budget","ordering":"constraints","rounds":1,"max_array_bytes":1 << 28},
        compensation={"method":"rounded","rounds":1,"primary_limit":4,"helper_limit":8,"max_array_bytes":1 << 28,
            "primary_order":"ranked","block_order":3,"first_helpers":4,"second_helpers":4})
    assert photos.loss == 0 and len(result["accepted"][0]["moves"]) == 3
    a,b = result["global_rounds"][0],result["compensation_rounds"][0]
    assert b["statistics_reused"] and a["statistics_sha256"] == b["statistics_sha256"]
    assert a["hist_changes_sha256"] == b["hist_changes_sha256"]
    assert result["proper_subset_trials"] == 6 and photos.stability.certificate(photos,domain.hist)["accepted"]
