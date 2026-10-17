"""检查双尺寸配对、唯一基线、零基线及两个尺寸的Q16运行时。"""
import copy

import numpy as np
import pytest

pytest.importorskip("numba",reason="双基线研究使用可选Numba环境")
pytest.importorskip("psutil",reason="双基线计时记录可选宿主内存")
pytest.importorskip("tifffile",reason="既有源适配为可选研究依赖")
from lutlab import io, interp, paired_baselines as paired, study_kernels
from lutlab.compatibility import model_args


def row(profile,m,value,scope="full_100_images"):
    return {"lut":"a","source":"fixture","profile":profile,"m":m,"scope":scope,
        "mean":value,"rms":value+1,"worst_image_p99":value+2,"max":value+3,
        "time":float(m),"time_unit":"ms_per_image","node_bytes":3*m**3}


def test_same_size_and_cross_size_are_explicit_and_order_independent():
    rows=[row("sample_tetra",33,2),row("fitted",17,3),row("sample_tetra",17,4),row("fitted",33,1)]
    for order in (rows,list(reversed(rows))):
        same={(r["profile"],r["m"]):r for r in paired.compare(order,"same_size")}
        assert same[("fitted",17)]["reference_m"]==17
        assert same[("fitted",17)]["mean_reduction_percent"]==25
        assert same[("fitted",33)]["mean_reduction_percent"]==50
        cross=next(r for r in paired.compare(order,"small_vs_large_baseline") if r["profile"]=="fitted")
        assert cross["m"]==17 and cross["reference_m"]==33
        assert cross["mean_reduction_percent"]==-50
        size=next(r for r in paired.compare(order,"size_pair") if r["profile"]=="fitted")
        assert size["m"]==33 and size["reference_m"]==17
        assert size["mean_delta"]==-2
        assert size["node_bytes_ratio"]==33**3/17**3


def test_duplicate_or_missing_baseline_is_rejected():
    small=row("sample_tetra",17,4)
    with pytest.raises(ValueError,match="不唯一"):
        paired.compare([small,copy.deepcopy(small)],"same_size")
    with pytest.raises(ValueError,match="缺失"):
        paired.compare([row("fitted",33,1),small],"same_size")
    with pytest.raises(ValueError,match="缺失"):
        paired.compare([row("fitted",33,1),row("sample_tetra",33,2)],"size_pair")


def test_measurement_scopes_cannot_be_mixed():
    with pytest.raises(ValueError,match="不得混合"):
        paired.compare([row("sample_tetra",17,4),row("sample_tetra",33,2,"screen_4096_per_image")],"size_pair")


def test_zero_baseline_keeps_absolute_difference_without_fake_percentage():
    assert paired.percentage_reduction(0,0) is None
    assert paired.percentage_reduction(1,0) is None
    result=paired.compare([row("sample_tetra",17,0),row("fitted",17,1)],"same_size")
    fitted=next(r for r in result if r["profile"]=="fitted")
    assert fitted["mean_delta"]==1 and fitted["mean_reduction_percent"] is None


def test_pair_plan_includes_both_baselines_and_both_selected_sizes():
    records=[{"profile":p,"m":m,"status":"ok"} for p in ("sample_tetra","fitted","not_selected") for m in (17,33)]
    report={"screen":records,"full":[records[3]]}
    index,profiles=paired.select_pairs(report)
    assert profiles==["fitted","sample_tetra"]
    assert len([index[(p,m)] for p in profiles for m in (17,33)])==4
    report["screen"]=records[:-1]
    with pytest.raises(ValueError,match="缺少"):
        paired.select_pairs(report)


@pytest.mark.parametrize("m",[17,33])
def test_both_sizes_match_existing_integer_oracle(m):
    rng=np.random.default_rng(303+m)
    model=io.SparseLut(io.uniform_grid(m),rng.integers(0,256,(m,m,m,3),dtype=np.uint8))
    points=rng.integers(0,256,(8000,3),dtype=np.uint8)
    points[:256]=np.arange(256)[:,None]
    np.testing.assert_array_equal(study_kernels.map_pixels(points,*model_args(model),0),interp.apply_tetra_q16(model,points))
