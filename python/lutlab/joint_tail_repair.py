"""对已定位的单节点停滞做有限双节点前瞻，不放宽完整域预算。"""
import itertools
import numpy as np
from . import error_analysis as ea, full_domain_guard as fg, tail_repair as tr


def predict(models, moves, points):
    nodes = [models[m.stage].nodes.reshape(-1,3)[m.node] for m in moves]
    old = [n.copy() for n in nodes]
    try:
        for node,m in zip(nodes,moves):
            node[:] = m.value
        return ea.Operator(models)(points)
    finally:
        for node,value in zip(nodes,old):
            node[:] = value


def nearby_moves(state,banks,radius):
    result = set()
    excess = np.maximum(state.squared.astype(np.int64)-state.caps.astype(np.int64),0)
    focus = np.lexsort((np.arange(len(excess)),-excess))[:16]
    focus = focus[excess[focus] > 0]
    for stage,model in enumerate(state.models):
        support = np.unique(state.indices[stage][focus][state.positive[stage][focus]])
        vertices = set()
        m = model.m
        for node in support:
            origin = (int(node)//(m*m),(int(node)//m)%m,int(node)%m)
            for delta in itertools.product(range(-radius,radius+1),repeat=3):
                point = tuple(a+b for a,b in zip(origin,delta))
                if all(0 <= x < m for x in point):
                    vertices.add((point[0]*m+point[1])*m+point[2])
        for node in sorted(vertices):
            current = model.nodes.reshape(-1,3)[node].astype(np.int32)
            for alternate in banks[stage].values():
                value = alternate.nodes.reshape(-1,3)[node].astype(np.int32)
                for divisor in (1,2):
                    mixed = (current*(divisor-1)+value+divisor//2)//divisor
                    if not np.array_equal(current,mixed):
                        result.add(tr.Move(stage,node,tuple(map(int,mixed))))
                        for channel in range(3):
                            partial = current.copy()
                            partial[channel] = mixed[channel]
                            if not np.array_equal(current,partial):
                                result.add(tr.Move(stage,node,tuple(map(int,partial))))
    return sorted(result)


def repair_pair(models,banks,hard,guards,limits,domain_guard,*,radius=1,helper_limit=32):
    """只在单节点停滞后运行：硬约束中性且均匀mean改善的邻接节点作帮手。

    先用旧支撑试探筛帮手，再对整对修改重算所有小集合与完整域，不把两个
    单节点收益相加。每对必须来自两个不同节点，标签/候选库与旧方法相同。
    """
    models = tr.clone(models)
    state = tr.State(models,hard["points"],hard["truth"],hard["caps"])
    before = state.loss()
    if not before[0]:
        return models,{"stop":"already_feasible","accepted":False}
    uniform = guards["uniform"]
    sample = tr.State(models,uniform["points"],uniform["truth"])
    helpers = []
    moves = nearby_moves(state,banks,radius)
    for move in moves:
        rows,_,squared = state.trial(move)
        if state.loss(rows,squared) > before:
            continue
        rows,_,squared = sample.trial(move)
        mean = sample.metrics["mean"]+(float(ea.ROOT_DISTANCE[squared].sum())-float(ea.ROOT_DISTANCE[sample.squared[rows]].sum()))/len(sample.points)
        if mean < sample.metrics["mean"]-1e-12:
            helpers.append((mean,move))
    helpers = sorted(helpers)[:helper_limit]
    primaries = []
    for move in tr.proposals(state,banks,16):
        rows,_,squared = state.trial(move)
        if state.loss(rows,squared) < before:
            primaries.append(move)
    ranked,seen = [],set()
    for primary in primaries:
        for _,helper in helpers:
            if (primary.stage,primary.node) == (helper.stage,helper.node):
                continue
            pair = tuple(sorted((primary,helper)))
            if pair in seen:
                continue
            seen.add(pair)
            prediction = predict(models,pair,state.points)
            squared = ea.histogram(prediction,state.truth)[1]
            loss = state.loss(np.arange(len(squared)),squared)
            if loss >= before:
                continue
            prediction = predict(models,pair,sample.points)
            squared = ea.histogram(prediction,sample.truth)[1]
            mean = float(ea.ROOT_DISTANCE[squared].mean())
            if mean <= limits["uniform"]["mean"]+1e-12:
                ranked.append((loss,mean,pair))
    before_guards = {name: ea.histogram(ea.Operator(models)(spec["points"]),spec["truth"])[1] for name,spec in guards.items()}
    rejected = {}
    for loss,mean,pair in sorted(ranked):
        measurements,failures = {},[]
        for name,spec in guards.items():
            prediction = predict(models,pair,spec["points"])
            hist,squared = ea.histogram(prediction,spec["truth"])
            if spec.get("caps") is not None:
                old_excess = np.maximum(before_guards[name].astype(np.int64)-spec["caps"].astype(np.int64),0)
                new_excess = np.maximum(squared.astype(np.int64)-spec["caps"].astype(np.int64),0)
                if np.any(new_excess > old_excess):
                    failures.append(name+".point_cap")
            measurements[name] = ea.hist_metrics(hist)
            failures.extend(name+"."+k for k,bound in limits[name].items() if measurements[name][k] > bound+1e-12)
            if failures:
                break
        if not failures:
            joint = fg.JointMove(pair)
            proof = domain_guard.consider(models,joint)
            failures.extend("full_domain."+k for k in proof["failed"])
        if failures:
            for key in failures:
                rejected[key] = rejected.get(key,0)+1
            continue
        changes = []
        for move in pair:
            node = models[move.stage].nodes.reshape(-1,3)[move.node]
            changes.append({"stage":move.stage+1,"node":move.node,"before":node.tolist(),"after":list(move.value)})
            node[:] = move.value
        domain_guard.commit(models,joint)
        return models,{"stop":"guarded_pair_accepted","accepted":True,"moves":changes,"before_loss":before,"after_loss":loss,
            "full_domain":proof,"guards":measurements,"neighbor_moves":len(moves),"helpers_retained":len(helpers),
            "primary_moves":len(primaries),"pairs_examined":len(seen),"pairs_ranked":len(ranked),"rejections":rejected}
    return models,{"stop":"no_guarded_pair_found","accepted":False,"neighbor_moves":len(moves),
        "helpers_retained":len(helpers),"primary_moves":len(primaries),"pairs_examined":len(seen),"pairs_ranked":len(ranked),"rejections":rejected}
