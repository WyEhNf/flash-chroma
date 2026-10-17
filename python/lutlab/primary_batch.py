"""冻结状态内收集真实可行主改，有限比较不相交双/三节点块并重新确认。"""
import itertools
import numpy as np
from . import full_domain_guard as fg


def validate(config):
    if (not isinstance(config,dict) or type(config.get("feasible_limit")) is not int
            or not 1 <= config["feasible_limit"] <= 8 or type(config.get("max_order")) is not int
            or config["max_order"] not in (2,3)):
        raise ValueError("主改批次必须冻结1至8个可行单改及2或3阶组合")


def select(model,ranked,evaluate,single_trace,*,before_loss,feasible_limit,max_order):
    validate({"feasible_limit":feasible_limit,"max_order":max_order})
    info = {"feasible_limit":feasible_limit,"max_order":max_order,"feasible_singles":[],
        "trials":[],"confirmation":[],"overlapping_blocks_skipped":0,"generated_blocks":0,
        "best_single_loss":None,"selected_loss":None,"selected_node_count":0,
        "scope":"同一冻结状态内前若干真实可行主改；双/三节点仅枚举两两支撑不相交者，单改损失相加只排序，全部组合真实重放；回执可行不等于已提交"}
    feasible,seen = [],set()
    signature = fg.signature([model])
    for score,move in ranked:
        if move in seen:continue
        seen.add(move)
        result = evaluate(move,single_trace,score,"single")
        if result is None:continue
        loss = result[0].loss
        feasible.append((loss,move))
        info["feasible_singles"].append({"node":move.node,"value":list(move.value),"loss":loss,"lower_bound_delta":score})
        if len(feasible) == feasible_limit:break
    if not feasible:return None,info
    info["best_single_loss"] = min(loss for loss,move in feasible)
    offers = [(loss,1,(move,)) for loss,move in feasible]
    candidates = []
    for size in range(2,max_order+1):
        for subset in itertools.combinations(feasible,size):
            moves = tuple(sorted(move for loss,move in subset))
            coordinates = [np.array(np.unravel_index(move.node,(model.m,)*3)) for move in moves]
            if not all(np.any(np.abs(a-b) > 1) for a,b in itertools.combinations(coordinates,2)):
                info["overlapping_blocks_skipped"] += 1
                continue
            candidates.append((sum(loss-before_loss for loss,move in subset),size,moves))
    candidates.sort()
    info["generated_blocks"] = len(candidates)
    for proxy,size,moves in candidates:
        result = evaluate(fg.combine(moves),info["trials"],None,"block")
        info["trials"][-1]["sum_single_loss_delta"] = proxy
        if result is not None:offers.append((result[0].loss,size,moves))
    loss,size,moves = min(offers)
    if fg.signature([model]) != signature:raise AssertionError("批次试探期间模型被修改，不能确认旧选择")
    move = fg.combine(moves)
    result = evaluate(move,info["confirmation"],None,"confirmation")
    if result is None or result[0].loss != loss:raise AssertionError("批次选择重新确认与冻结试探不同")
    info.update(selected_loss=loss,selected_node_count=size,selected_nodes=[m.node for m in moves],
        selected_better_than_best_single=loss < info["best_single_loss"],pairwise_disjoint_support_certificate=True)
    return (move,*result),info
