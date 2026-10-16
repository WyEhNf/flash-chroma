"""完整颜色频数上的冻结截断下界，给全节点±1提案排序。"""
import hashlib
import numpy as np
from numba import njit
from . import full_domain_guard as fg,interp,tail_repair as tr


@njit(cache=True)
def _anchor(hist,thresholds,budgets,cutoffs):
    value = np.int64(0)
    for g in range(len(hist)):
        for j in range(3):
            if budgets[g,j] < 0:continue
            t,u = thresholds[g,j],cutoffs[g,j]-thresholds[g,j]
            value -= budgets[g,j]*u
            for d in range(t+1,hist.shape[1]):value += hist[g,d]*min(d-t,u)
    return value


@njit(cache=True)
def _accumulate(keys,indices,weights,nodes,prediction,truth,squared,offsets,groups,counts,thresholds,budgets,cutoffs,scores):
    acc = np.zeros(3,np.int64)
    for row in range(len(indices)):
        colour = keys[row]
        acc[:] = 0
        for v in range(4):
            for c in range(3):acc[c] += np.int64(weights[row,v])*np.int64(nodes[indices[row,v],c])
        for channel in range(3):
            residual = np.int64(prediction[colour,channel])-np.int64(truth[colour,channel])
            for sign_index in range(2):
                sign = 2*sign_index-1
                old = squared[colour]
                new = old+2*residual*sign+1
                # 单节点分量±1只会令对应输出分量变化0或±1，先按颜色算一次六种实际变化。
                change = np.int64(0)
                for p in range(offsets[colour],offsets[colour+1]):
                    g,count = groups[p],np.int64(counts[p])
                    for j in range(3):
                        if budgets[g,j] < 0:continue
                        t,u = thresholds[g,j],cutoffs[g,j]-thresholds[g,j]
                        change += count*(min(max(new-t,0),u)-min(max(old-t,0),u))
                if change == 0:continue
                for v in range(4):
                    node,w = indices[row,v],np.int64(weights[row,v])
                    if w == 0 or not 0 <= np.int64(nodes[node,channel])+sign <= 255:continue
                    output = (acc[channel]+w*sign+32768) >> 16
                    if output != prediction[colour,channel]:scores[node,channel,sign_index] += change


def ranked(model,domain,photos,chunk=1 << 18,max_array_bytes=2684354560):
    """当前缺口处紧的候选下界；不保证排名最优候选可行，更不替代真实联合验收。"""
    score_bytes = model.m**3*3*2*np.dtype(np.int64).itemsize
    persistent = domain.cache_bytes+sum(a.nbytes for a in vars(photos).values() if isinstance(a,np.ndarray))+sum(g.nbytes for g in photos.aggregate_groups)
    if photos.stability is not None:persistent += photos.stability.cache_array_bytes
    if persistent+score_bytes > max_array_bytes:raise MemoryError("全节点排序数组超过冻结预算")
    anchor = int(_anchor(photos.hist,photos.thresholds,photos.budgets,photos.cutoffs))
    if anchor != photos.loss:raise AssertionError("冻结截断下界没有在当前缺口处取等")
    scores = np.zeros((model.m**3,3,2),np.int64)
    nodes = model.nodes.reshape(-1,3)
    for start in range(0,len(photos.keys),chunk):
        keys = photos.keys[start:start+chunk]
        indices,weights = interp.tetra_index_weights_q(domain.points[keys],*model.tables(),model.m)
        _accumulate(keys,indices,weights,nodes,domain.prediction,domain.truth,domain.squared,*photos.offsets_groups_counts,
            photos.thresholds,photos.budgets,photos.cutoffs,scores)
    proposals = []
    for node,channel,sign_index in np.argwhere(scores < 0):
        sign = 2*int(sign_index)-1
        if not 0 <= int(nodes[node,channel])+sign <= 255:continue
        value = list(map(int,nodes[node]))
        value[channel] += sign
        proposals.append((int(scores[node,channel,sign_index]),tr.Move(0,int(node),tuple(value))))
    proposals.sort()
    return proposals,{"anchor_loss":anchor,"observed_colours":len(photos.keys),"score_array_bytes":score_bytes,"score_sha256":hashlib.sha256(memoryview(scores).cast("B")).hexdigest(),
        "negative_score_proposals":len(proposals),"model_signature":fg.signature([model]),
        "top_proposals":[{"lower_bound_delta":score,"node":move.node,"value":list(move.value)} for score,move in proposals[:32]],
        "scope":"全观测颜色/频数，固定截断点在当前缺口取等；单通道节点±1的整数下界，不包含mean/RMS保护；双节点代理相加仅排序"}
