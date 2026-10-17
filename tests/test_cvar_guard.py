"""覆盖尾部计数、保留补偿材料、无提交候选及普通热点路径的CVaR门禁。"""
import math
import runpy
from pathlib import Path
import numpy as np
import pytest
pytest.importorskip("numba",reason="CVaR提交门禁使用可选Numba研究环境")
from lutlab import cvar_guard as cg,full_domain_guard as fg,interp,io,quantile_constraints as qc,quantile_repair as qr
from lutlab.stability import Stability


def test_top_fraction_ties_and_identical_tail_with_changed_body():
    hist = np.zeros(20,np.int64)
    hist[[0,1,2,10,17]] = [101,93,3,3,1]
    result = cg.tail_summary(hist)
    assert result["n"] == 201 and result["tail_count"] == 3 and result["tail_histogram"] == [[10,2],[17,1]]
    lower = 2*math.isqrt(10 << 48)+math.isqrt(17 << 48)
    assert int(result["sum_lower_q24"]) == lower and int(result["sum_upper_q24"]) == lower+3
    independent = runpy.run_path(str(Path(__file__).resolve().parents[1] / "scripts/verify_cvar_guard.py"))
    assert independent["tail_summary"]([[int(d),int(hist[d])] for d in np.flatnonzero(hist)]) == result
    guard = cg.CvarGuard(hist,"固定模型")
    hist[0] -= 1
    hist[1] += 1
    proof = guard.certify(hist)
    assert proof["accepted"] and proof["same_tail_histogram"]
    assert independent["verify_certificate"](guard.reference,[[int(d),int(hist[d])] for d in np.flatnonzero(hist)],proof)
    hist[0] += 1
    with pytest.raises(ValueError):guard.certify(hist)


def fixture(mode="both"):
    points = [[0,0,0],[31,0,0],[255,0,0],[239,0,0]]+[[255,g,0] for g in range(1,7)]+[[255,255,255],[239,255,255],[128,128,128]]
    points += [[128,g,b] for g in range(19) for b in range(100,110)][:188]
    points = np.asarray(points,np.uint8)
    truth = np.full(points.shape,100,np.uint8)
    truth[[0,2,*range(4,10),10],0] = 101
    truth[3,0],truth[11,0],truth[12,0] = 98,102,103
    model = io.SparseLut(io.uniform_grid(5),np.full((5,5,5,3),100,np.uint8))
    domain = fg.DomainGuard([model],points,truth)
    indices,counts = ([0,1,2,10],[1000,10000,10,6]) if mode == "both" else ([0,1,2],[1000,10000,10]) if mode == "only_a" else ([2],[10])
    inverse = qc.invert(np.asarray(indices,np.uint32),np.arange(len(indices),dtype=np.uint8),np.asarray(counts,np.uint32),len(points),len(indices))
    photos = qc.GroupState(inverse,len(indices),np.zeros(len(points),np.int32),domain.squared,[list(range(len(indices)))])
    photos.stability = Stability(photos,domain,tail_ranking=False)
    return model,domain,photos,points


def run(model,domain,photos,guard,global_search=True):
    config = {"method":"primary_budget","ordering":"constraints","rounds":1,"max_array_bytes":1 << 28,
        "batch":{"feasible_limit":8,"max_order":3}} if global_search else None
    return qr.repair(model,[],domain,photos,steps=1,focus_count=1,trial_limit=32,pair_nodes=0,global_search=config,cvar_guard=guard)


def test_risky_single_retained_as_seed_but_only_compensated_block_commits():
    model,domain,photos,points = fixture()
    guard = cg.CvarGuard(domain.hist,domain.model_signature)
    assert guard.reference["sum_lower_q24"] == str(7 << 24)
    result = run(model,domain,photos,guard)
    batch = result["global_rounds"][0]["batch_search"]
    assert len(batch["feasible_singles"]) == 2
    assert sorted(s["commit_eligible"] for s in batch["feasible_singles"]) == [False,True]
    singles = result["global_rounds"][0]["trials"]
    assert any(t["decision"] == "seed_only_cvar" and not t["accepted"] and t["seed_eligible"] for t in singles)
    assert photos.loss == 1000 and batch["selected_node_count"] == 2
    assert batch["best_commit_single_loss"] == 1010 and result["accepted"][0]["cvar"]["accepted"]
    assert guard.certify(domain.hist)["accepted"] and photos.stability.certificate(photos,domain.hist)["accepted"]
    np.testing.assert_array_equal(domain.prediction,interp.apply_tetra_q16(model,points))


def test_nonempty_material_pool_without_commit_candidate_preserves_model():
    model,domain,photos,points = fixture("only_a")
    signature = domain.model_signature
    guard = cg.CvarGuard(domain.hist,signature)
    result = run(model,domain,photos,guard)
    batch = result["global_rounds"][0]["batch_search"]
    assert batch["feasible_singles"] and batch["no_commit_eligible_offer"] and not batch["confirmation"]
    assert not result["accepted"] and photos.loss == 1010 and fg.signature([model]) == signature
    assert guard.certify(domain.hist)["accepted"]


def test_hotspot_path_also_requires_tail_guard():
    losses = {}
    for enabled in (False,True):
        model,domain,photos,points = fixture("hotspot")
        guard = cg.CvarGuard(domain.hist,domain.model_signature) if enabled else None
        result = run(model,domain,photos,guard,global_search=False)
        losses[enabled] = photos.loss
        if enabled:
            assert not result["accepted"] and result["rejections"]["cvar.mean_bound"] > 0
            assert guard.certify(domain.hist)["accepted"]
    assert losses[False] == 0 and losses[True] == 10
