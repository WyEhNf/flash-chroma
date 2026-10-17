"""同一全局±1提案库的预算感知排序，保留原尾部下界并共享辅助统计。"""
import hashlib
import numpy as np
from . import full_domain_guard as fg,quantile_global as qg,rounded_budget as rb


def ranked(model,domain,photos,*,ordering,cache,trial_limit=128,max_array_bytes=2684354560):
    if ordering not in ("tail","constraints"):raise ValueError("未知主提案排序模式")
    if cache:raise ValueError("主提案统计缓存必须为空，禁止混用旧模型")
    if photos.stability is None:raise ValueError("预算主提案研究要求先冻结稳定性参照")
    # 先计算并释放下界数组，再分配大统计；两臂主提案库及大数组完全相同。
    proposals,info = qg.ranked(model,domain,photos,max_array_bytes=max_array_bytes)
    cache["track_changes"] = True
    deltas = rb.statistics(model,domain,photos,max_array_bytes=max_array_bytes,tail_cache=cache)
    cache.update(deltas=deltas,model_signature=fg.signature([model]))
    selected,roles = proposals,[]
    if ordering == "constraints":
        allowed = np.zeros(deltas.shape[:2],np.bool_)
        bounds = {}
        for score,move in proposals:
            delta = np.array(move.value,dtype=np.int64)-model.nodes.reshape(-1,3)[move.node]
            channel = int(np.flatnonzero(delta)[0])
            option = 2*channel+int(delta[channel] > 0)
            allowed[move.node,option] = True
            bounds[move] = score
        ranking = rb.rank_helpers(model,domain,photos,deltas,np.zeros(deltas.shape[2:],np.int64),[],trial_limit,
            tail_cache=cache,tail_change=np.zeros(photos.stability.thresholds.shape,np.int64),
            primary_changes=np.zeros(deltas.shape[2],np.bool_),allowed=allowed)
        selected = [(bounds[move],move) for key,move,role in ranking]
        roles = [{"node":move.node,"value":list(move.value),"lower_bound_delta":bounds[move],
            "predicted_rms_failed_count":role["rank_rms_failed_count"],"predicted_mean_failed_count":role["rank_mean_failed_count"]}
            for key,move,role in ranking[:32]]
    raw_top = info.pop("top_proposals")
    return selected,{**info,"method":"primary_budget","ordering":ordering,
        "raw_top_proposals":raw_top,"top_proposals":[{"lower_bound_delta":score,"node":move.node,"value":list(move.value)} for score,move in selected[:32]],
        "top_budget_predictions":roles,"trial_prefix_limit":trial_limit,"statistics_array_bytes":deltas.nbytes,
        "statistics_sha256":hashlib.sha256(memoryview(deltas).cast("B")).hexdigest(),
        "hist_changes_array_bytes":cache["hist_changes"].nbytes,
        "hist_changes_sha256":hashlib.sha256(memoryview(cache["hist_changes"]).cast("B")).hexdigest(),
        "scope":"同一全观测颜色负下界±1提案库；约束臂先按SSE/mean预算失败数及归一化预算排序，下界仍用于真实验收核对；p99/max最终仍真实检查；共享后续辅助统计；无变化声明仅单改或两两支撑不相交时用于排序"}
