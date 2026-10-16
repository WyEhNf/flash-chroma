"""全域整数证书与倒排增量重放的阶段合同；不展开真实研究语料。"""
import math
from decimal import Decimal, localcontext
import numpy as np
import pytest
pytest.importorskip("numba", reason="全域保护研究使用可选Numba环境")
from lutlab import error_analysis as ea, full_domain_guard as fg, interp, io, tail_repair as tr


def test_integer_root_bounds_and_large_reduction():
    lower, upper = fg.root_bounds()
    for d,(lo,hi) in enumerate(zip(lower,upper)):
        assert int(lo)**2 <= d << 48 <= int(hi)**2
        assert hi-lo in (0,1)
    hist = np.zeros(len(lower),np.int64)
    hist[2],hist[3] = 2**60,2**59
    result = fg.summary(hist)
    with localcontext() as ctx:
        ctx.prec = 70
        exact = Decimal(2).sqrt()*Decimal(2**60)+Decimal(3).sqrt()*Decimal(2**59)
        assert Decimal(result["sum_lower_q24"])/(1 << 24) <= exact <= Decimal(result["sum_upper_q24"])/(1 << 24)
    assert int(result["sum_upper_q24"]) > 2**64


def test_exact_budget_boundary_and_quantile_equality():
    old = np.zeros(3*255**2+1,np.int64)
    old[100] = 200
    candidate = old.copy()
    candidate[100],candidate[121] = 190,10
    # 单独检查mean边界：p99/max在这个例子中预期退化，不能一起冒称通过。
    proof = fg.certify(fg.summary(old),fg.summary(candidate))
    assert "mean" not in proof["failed"] and "max" in proof["failed"]
    candidate[100],candidate[121] = 189,11
    assert "mean" in fg.certify(fg.summary(old),fg.summary(candidate))["failed"]
    old[:] = 0
    old[27] = 200
    assert fg.certify(fg.summary(old),fg.summary(old))["accepted"]


def test_cell_inverse_local_trial_matches_independent_chain():
    rng = np.random.default_rng(2026101731)
    grid = np.array([[0.,37.125,255.],[0.,148.03,255.],[0.,200.875,255.]])
    models = [io.SparseLut(grid,rng.integers(0,256,(3,3,3,3),dtype=np.uint8)) for _ in range(4)]
    points = rng.integers(0,256,(701,3),dtype=np.uint8)
    guard = fg.DomainGuard(models,points,points)
    for stage in range(4):
        indices,weights = interp.tetra_index_weights_q(guard.inputs[stage],*models[stage].tables(),3)
        move = tr.Move(stage,int(indices[0,0]),(0,255,17))
        trial = guard.trial(models,move)
        expected_rows = np.flatnonzero(np.any((indices == move.node)&(weights > 0),axis=1))
        np.testing.assert_array_equal(np.sort(trial["rows"]),expected_rows)
        changed = tr.clone(models)
        changed[stage].nodes.reshape(-1,3)[move.node] = move.value
        expected = points.copy()
        for model in changed:
            expected = interp.apply_tetra_q16(model,expected)
        actual = guard.prediction.copy()
        actual[trial["rows"]] = trial["prediction"]
        np.testing.assert_array_equal(actual,expected)
        np.testing.assert_array_equal(trial["hist"],ea.histogram(expected,points)[0])
        assert fg.signature(models) == guard.model_signature
    endpoint = fg.DomainGuard([models[0]],np.zeros((1,3),np.uint8),np.zeros((1,3),np.uint8))
    assert not len(endpoint.affected([models[0]],tr.Move(0,13,(1,2,3))))


def test_commit_refreshes_suffix_and_rejects_stale_model():
    grid = np.tile([0.,99.5,255.],(3,1))
    levels = np.array([0,100,255],np.uint8)
    identity = np.stack(np.meshgrid(levels,levels,levels,indexing="ij"),-1)
    models = [io.SparseLut(grid,np.full((3,3,3,3),100,np.uint8))] + [io.SparseLut(grid,identity.copy()) for _ in range(3)]
    points = np.stack(np.meshgrid(*([np.array([0,255],np.uint8)]*3),indexing="ij"),-1).reshape(-1,3)
    truth = np.full_like(points,99)
    guard = fg.DomainGuard(models,points,truth)
    corners = [0,2,6,8,18,20,24,26]
    for node in corners:
        move = tr.Move(0,node,(99,99,99))
        assert guard.consider(models,move)["accepted"]
        models[0].nodes.reshape(-1,3)[node] = move.value
        guard.commit(models,move)
        current = points.copy()
        for stage,model in enumerate(models):
            np.testing.assert_array_equal(guard.inputs[stage],current)
            indices,weights = interp.tetra_index_weights_q(current,*model.tables(),model.m)
            expected_rows = np.flatnonzero(np.any((indices == 0)&(weights > 0),axis=1))
            np.testing.assert_array_equal(np.sort(guard.affected(models,tr.Move(stage,0,(0,0,0)))),expected_rows)
            current = interp.apply_tetra_q16(model,current)
        np.testing.assert_array_equal(guard.prediction,current)
    assert guard.report()["final"]["max_squared_error"] == 0
    bad = tr.clone(models)
    bad[0].nodes.reshape(-1,3)[0] = 97
    with pytest.raises(ValueError,match="陈旧倒排"):
        guard.trial(bad,tr.Move(0,0,(99,99,99)))
    # 同一接入点验证旧小集合搜索确实调用全域回执并提交缓存。
    start = [io.SparseLut(grid,np.full((3,3,3,3),100,np.uint8))] + [io.SparseLut(grid,identity.copy()) for _ in range(3)]
    domain = fg.DomainGuard(start,points,truth)
    result,detail = tr.repair(start,[{"baseline":m} for m in models],dict(points=points,truth=truth,caps=np.zeros(8,np.uint32)),
        {"uniform":dict(points=points,truth=truth)},{"uniform":dict(mean=2.,rms=2.,p99=2.,max=2.)},steps=9,domain_guard=domain)
    assert len(detail["accepted"]) == 8
    assert all(move["full_domain"]["accepted"] for move in detail["accepted"])
    current = points.copy()
    for model in result:
        current = interp.apply_tetra_q16(model,current)
    np.testing.assert_array_equal(domain.prediction,current)
