"""在固定保护下直接最小化max/历史缺口/SSE/L1，输出完整整数箱证书。"""
import math
import numpy as np
from . import automatic_compensation as ac


def lower_objective(problem,prefix,squared):
    state = problem.state
    loss = state.photos["loss"]
    for g in state.active:
        base = state.photos["groups"][g]
        local = ac.pairs(np.bincount(squared,weights=state.frequency[g]).astype(np.int64))
        optimistic = ac.update(base["histogram"],state.local_photos[g],local)
        loss += ac.cost(optimistic,base["constraints"])-sum(base["costs"])
    return [max(problem.outside_max,int(squared.max())),int(loss),state.full_sse+int(np.sum(squared-problem.old)),sum(abs(d) for d in prefix)]


def objective(problem,score,deltas):
    return [score["max_squared"],score["primary_loss"],problem.state.full_sse+int(score["full_sse_delta"]),sum(abs(d) for d in deltas)]


def solve(problem,assess):
    state = problem.state
    seed = [state.full[-1][0],state.photos["loss"],state.full_sse,0]
    incumbent = {"name":"baseline","objective":seed,"deltas":[0]*len(problem.nodes)}
    terminals = []
    def visit(prefix,total):
        nonlocal incumbent
        item = {"deltas":prefix.copy()}
        proof = problem.certificate(prefix,total)
        if proof is not None:item.update(proof)
        else:
            squared = problem.lower_squared(prefix,total)
            bound = lower_objective(problem,prefix,squared)
            if tuple(bound) >= tuple(incumbent["objective"]):
                item.update(kind="quality",objective_lower=bound,incumbent={**incumbent})
            elif len(prefix) == len(problem.nodes):
                candidate = problem.candidate(prefix)
                score = state.score(candidate)
                actual = objective(problem,score,prefix)
                if actual != bound:raise AssertionError("完整叶子的目标界不等于实际目标")
                item.update(kind="leaf",objective=actual,score=score,record=None,accepted=False)
                if not score["fixed_failed"]:
                    receipt = assess(candidate,prefix)
                    item.update(receipt)
                    if receipt["accepted"]:incumbent = {"name":receipt["record"],"objective":actual,"deltas":prefix.copy()}
            else:
                depth = len(prefix)
                for delta in problem.domains[depth]:visit(prefix+[delta],total+problem.matrix[:,depth]*delta)
                return
        item["covered_assignments"] = math.prod(len(d) for d in problem.domains[len(prefix):])
        terminals.append(item)
    visit([],np.zeros(len(problem.points),np.int64))
    if sum(t["covered_assignments"] for t in terminals) != problem.assignments:raise AssertionError("质量目标搜索没有覆盖完整整数箱")
    return {"nodes":problem.nodes,"domains":problem.domains,"channel":problem.channel,"rgb_max":problem.rgb_max,"assignments":problem.assignments,
        "objective_schema":["max_squared","historical_loss","full_sse","l1"],"seed_objective":seed,"terminals":terminals,"incumbent":incumbent,
        "objective_optimal_within_box":True,"scope":"完整冻结整数箱内按max/历史缺口/SSE/L1字典序最优；保留全部保护，不推断箱外或其他表示的全局最优"}
