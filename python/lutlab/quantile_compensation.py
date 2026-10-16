"""由图片/完整域RMS线性代理寻找补偿节点；实际接受仍用精确像素约束。"""
import hashlib
import numpy as np
from numba import njit
from . import full_domain_guard as fg, interp, io, tail_repair as tr


@njit(cache=True)
def _accumulate(start,indices,weights,errors,offsets,groups,counts,gradient,diagonal):
    global_group = gradient.shape[1]-1
    for row in range(len(indices)):
        colour = start+row
        for v in range(4):
            w = np.int64(weights[row,v])
            if w == 0:continue
            node = indices[row,v]
            diagonal[node,global_group] += w*w
            for c in range(3):gradient[node,global_group,c] += w*errors[row,c]
            for p in range(offsets[colour],offsets[colour+1]):
                group,count = groups[p],np.int64(counts[p])
                diagonal[node,group] += count*w*w
                for c in range(3):gradient[node,group,c] += count*w*errors[row,c]


def moments(model,domain,photos,chunk=1 << 18):
    """精确整数Aq^T(频数*当前RGB8残差)、平方权重；不是舍入模型的精确导数。"""
    n_groups = len(photos.hist)+1
    gradient = np.zeros((model.m**3,n_groups,3),np.int64)
    diagonal = np.zeros((model.m**3,n_groups),np.int64)
    for start in range(0,len(domain.points),chunk):
        stop = min(len(domain.points),start+chunk)
        indices,weights = interp.tetra_index_weights_q(domain.points[start:stop],*model.tables(),model.m)
        errors = domain.prediction[start:stop].astype(np.int32)-domain.truth[start:stop]
        _accumulate(start,indices,weights,errors,*photos.offsets_groups_counts,gradient,diagonal)
    return gradient,diagonal


def pairs(model,domain,photos,ranked,*,primary_limit=8,helper_limit=16,trial_limit=128,max_array_bytes=2684354560):
    primaries = []
    for proxy,move in ranked[:trial_limit]:
        trial = domain.trial([model],move)
        photo = photos.trial(trial["rows"],domain.squared[trial["rows"]],trial["squared"])
        if photo.loss < photos.loss:
            primaries.append((photo.loss,proxy,move,photo.failed))
    primaries = sorted(primaries)[:primary_limit]
    if not primaries:return [],{"primaries":0,"pairs":0,"moment_array_bytes":0}
    gradient,diagonal = moments(model,domain,photos)
    moment_bytes = gradient.nbytes+diagonal.nbytes
    persistent = domain.cache_bytes+sum(a.nbytes for a in vars(photos).values() if isinstance(a,np.ndarray))+sum(g.nbytes for g in photos.aggregate_groups)
    if persistent+moment_bytes > max_array_bytes:raise MemoryError("补偿矩与既有数组超过冻结预算")
    data_hash = hashlib.sha256(gradient.tobytes()+diagonal.tobytes()).hexdigest()
    nodes = model.nodes.reshape(-1,3).astype(np.int64)
    n_groups = len(photos.hist)
    generated,seen = [],set()
    for loss,proxy,primary,failed in primaries:
        critical = {(n_groups,)}
        for key in failed:
            if key.startswith("group"):critical.add((int(key.split(".")[0][5:]),))
            elif key.startswith("aggregate"):
                critical.add(tuple(map(int,photos.aggregate_groups[int(key.split(".")[0][9:])])))
        critical = sorted(critical)
        statistics = []
        for groups in critical:
            if groups == (n_groups,):
                population = len(domain.points)
            else:population = int(photos.hist[list(groups)].sum())
            statistics.append((gradient[:,groups,:].sum(axis=1).astype(np.float64),
                diagonal[:,groups].sum(axis=1).astype(np.float64),population))
        scores = []
        for channel in range(3):
            for sign in (-1,1):
                rates = [(2*io.ONE*sign*g[:,channel]+d)/(io.ONE**2*n) for g,d,n in statistics]
                worst,total = np.maximum.reduce(rates),np.sum(rates,axis=0)
                valid = (nodes[:,channel]+sign >= 0)&(nodes[:,channel]+sign <= 255)
                valid[primary.node] = False
                ids = np.flatnonzero(valid)
                order = np.lexsort((ids,total[ids],worst[ids]))[:helper_limit]
                for node in ids[order]:
                    value = nodes[node].copy()
                    value[channel] += sign
                    scores.append((float(worst[node]),float(total[node]),tr.Move(0,int(node),tuple(map(int,value)))))
        for worst,total,helper in sorted(scores)[:helper_limit]:
            combined = tuple(sorted((primary,helper)))
            if combined in seen:continue
            seen.add(combined)
            generated.append(((loss,worst,total,combined),combined,{"primary_node":primary.node,"helper_node":helper.node,"critical_groups":[list(g) for g in critical]}))
    generated.sort(key=lambda value:value[0])
    return [(moves,info) for _,moves,info in generated],{"primaries":len(primaries),"pairs":len(generated),
        "moment_array_bytes":moment_bytes,"moments_sha256":data_hash,"model_signature":fg.signature([model]),
        "scope":"当前RGB8残差的连续SSE代理，仅用于补偿排序；全节点±1、整对真实重算与原保护条件决定接受，不以残差作节点标签"}
