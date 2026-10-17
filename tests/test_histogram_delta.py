"""大量共同非平方误差下，精确相等mean不误拒、真实上升不误放。"""
from pathlib import Path
import runpy
import pytest
from lutlab.histogram_delta import mean_difference


def test_equal_integer_distance_change_cancels_common_irrational_mass():
    old = [[2,4094],[400,1],[900,1]]
    new = [[2,4094],[441,1],[841,1]]
    proof = mean_difference(old,new)
    assert proof["accepted"] and proof["delta_lower_q24"] == proof["delta_upper_q24"] == "0"
    assert proof["changed_counts"] == [[400,-1],[441,1],[841,1],[900,-1]]
    bad = mean_difference(old,[[2,4094],[484,1],[841,1]])
    assert not bad["accepted"] and int(bad["delta_lower_q24"]) == 1 << 24
    with pytest.raises(ValueError):mean_difference(old,[[2,4095],[441,1],[841,1]])


def test_public_photo_and_full_stability_match_independent_signed_certificate():
    pytest.importorskip("numba",reason="公开固定保护依赖可选Numba研究环境")
    import numpy as np
    from lutlab import full_domain_guard as fg,io,quantile_constraints as qc
    from lutlab.stability import Stability
    model = io.SparseLut(io.uniform_grid(2),np.full((2,2,2,3),100,np.uint8))
    keys = np.arange(4096,dtype=np.int64)
    points = np.stack((keys >> 16,(keys >> 8) & 255,keys & 255),axis=1).astype(np.uint8)
    truth = np.tile(np.array([101,101,100],np.uint8),(4096,1))
    truth[-2:] = [[120,100,100],[130,100,100]]
    domain = fg.DomainGuard([model],points,truth)
    inverse = qc.invert(np.arange(4096,dtype=np.uint32),np.zeros(4096,np.uint8),np.ones(4096,np.uint32),4096,1)
    photos = qc.GroupState(inverse,1,domain.squared,domain.squared,[[0]])
    photos.stability = quality = Stability(photos,domain,tail_ranking=False)
    new = domain.hist.copy()
    new[[400,900]] -= 1
    new[[441,841]] += 1
    value = fg.summary(new)
    assert int(value["sum_upper_q24"]) > int(quality.full_reference["sum_lower_q24"])
    quality.photo_tails = quality.counts([new])
    assert not quality.check_photos(new[None,:],np.array([int(value["sum_lower_q24"])]),np.array([int(value["sum_upper_q24"])]),
        np.array([int(value["sum_squared_error"])]),np.array([True]))
    assert not quality.check_full(new,value)
    root = Path(__file__).resolve().parents[1]
    summarize = runpy.run_path(str(root / "scripts/verify_quantile_constraints.py"))["summary"]
    independent = runpy.run_path(str(root / "scripts/verify_stability.py"))["checked"]
    proof = independent(quality.full_reference["histogram"],value["histogram"],summarize)
    assert not proof["same_histogram"] and int(proof["sse"]) == int(quality.full_reference["sum_squared_error"])-18
    bad = new.copy()
    bad[441] -= 1
    bad[484] += 1
    assert "stability.full.mean_bound" in quality.check_full(bad,fg.summary(bad))
