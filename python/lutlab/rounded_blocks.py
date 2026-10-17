"""复用单改预算统计，有限枚举一主两辅的三节点组合；不代替真实块验收。"""
import numpy as np
from . import full_domain_guard as fg,rounded_budget as rb


def option(model,move):
    change = np.array(move.value)-model.nodes.reshape(-1,3)[move.node]
    channels = np.flatnonzero(change)
    if len(channels) != 1 or abs(change[channels[0]]) != 1:raise ValueError("辅助节点不是单通道±1")
    return int(channels[0])*2+int(change[channels[0]] > 0)


def triples(model,domain,photos,cache,*,first_limit=4,second_limit=4):
    if not cache:return [],{"triples":0,"scope":"没有改善尾部的主节点，不生成三节点块"}
    if fg.signature([model]) != cache["model_signature"]:raise ValueError("三节点统计缓存已陈旧")
    deltas = cache["deltas"]
    roots_high = fg.root_bounds()[1]
    candidates,seen = [],set()
    for loss,proxy,primary in cache["primaries"]:
        trial = domain.trial([model],primary)
        old = domain.squared[trial["rows"]]
        change = rb._reduce(trial["rows"],trial["squared"]-old,roots_high[trial["squared"]]-roots_high[old],
            *photos.offsets_groups_counts,len(photos.hist))
        tail_change = None
        if "tail_deltas" in cache:
            from .stability import reduce_tails
            tail_change = reduce_tails(trial["rows"],old,trial["squared"],*photos.offsets_groups_counts,
                photos.stability.thresholds,photos.stability.budgets).astype(np.int64)
        for key_a,first,roles_a in rb.rank_helpers(model,domain,photos,deltas,change,[primary.node],first_limit,tail_cache=cache,tail_change=tail_change):
            conditional = change+deltas[first.node,option(model,first)]
            conditional_tail = tail_change+cache["tail_deltas"][first.node,option(model,first)] if tail_change is not None else None
            for key_b,second,roles_b in rb.rank_helpers(model,domain,photos,deltas,conditional,[primary.node,first.node],second_limit,tail_cache=cache,tail_change=conditional_tail):
                moves = tuple(sorted((primary,first,second)))
                if moves in seen:continue
                seen.add(moves)
                disjoint = roles_a["disjoint_cell_support_certificate"] and roles_b["disjoint_cell_support_certificate"]
                roles = {**roles_b,"primary_node":primary.node,"helper_nodes":[first.node,second.node],"proposed_node_count":3,
                    "disjoint_cell_support_certificate":disjoint,"pairwise_disjoint_support_certificate":disjoint}
                key = (loss,key_b[0],key_b[1],key_b[2],not disjoint,key_b[4],key_b[5],moves)
                candidates.append((key,moves,roles))
    candidates.sort(key=lambda v:v[0])
    return [(moves,roles) for key,moves,roles in candidates],{"triples":len(candidates),"primary_candidates":len(cache["primaries"]),
        "maximum_candidates":len(cache["primaries"])*first_limit*second_limit,"first_helpers":first_limit,"second_helpers":second_limit,
        "statistics_reused":True,"model_signature":cache["model_signature"],
        "scope":"冻结主候选×首辅×次辅，去重；预算仅在三者两两支撑不相交时可相加，全部候选仍真实重放"}
