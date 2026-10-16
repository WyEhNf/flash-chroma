"""用真实RGB8单节点±1的SSE/Q24上界变化排序联合补偿，实际整对重放决定接受。"""
import hashlib
import numpy as np
from numba import njit
from . import full_domain_guard as fg,interp,tail_repair as tr


@njit(cache=True)
def _accumulate(start,indices,weights,nodes,prediction,truth,squared,offsets,groups,counts,roots_high,deltas,thresholds,budgets,tail_deltas):
    full_group = deltas.shape[2]-1
    acc = np.zeros(3,np.int64)
    for row in range(len(indices)):
        colour = start+row
        acc[:] = 0
        for v in range(4):
            for c in range(3):acc[c] += np.int64(weights[row,v])*np.int64(nodes[indices[row,v],c])
        for channel in range(3):
            residual = np.int64(prediction[colour,channel])-np.int64(truth[colour,channel])
            for sign_index in range(2):
                sign = 2*sign_index-1
                if not 0 <= np.int64(prediction[colour,channel])+sign <= 255:continue
                option = 2*channel+sign_index
                difference = 2*residual*sign+1
                new = squared[colour]+difference
                mean_difference = roots_high[new]-roots_high[squared[colour]]
                for v in range(4):
                    node,w = indices[row,v],np.int64(weights[row,v])
                    if w == 0 or not 0 <= np.int64(nodes[node,channel])+sign <= 255:continue
                    if ((acc[channel]+w*sign+32768) >> 16) == prediction[colour,channel]:continue
                    deltas[node,option,full_group,0] += difference
                    deltas[node,option,full_group,1] += mean_difference
                    if tail_deltas.size:
                        for j in range(3):
                            if budgets[full_group,j] >= 0:
                                t = thresholds[full_group,j]
                                tail_deltas[node,option,full_group,j] += int(new > t)-int(squared[colour] > t)
                    for p in range(offsets[colour],offsets[colour+1]):
                        group,count = groups[p],np.int64(counts[p])
                        deltas[node,option,group,0] += count*difference
                        deltas[node,option,group,1] += count*mean_difference
                        if tail_deltas.size:
                            for j in range(3):
                                if budgets[group,j] >= 0:
                                    t = thresholds[group,j]
                                    tail_deltas[node,option,group,j] += count*(int(new > t)-int(squared[colour] > t))


@njit(cache=True)
def _reduce(rows,sse_delta,mean_delta,offsets,groups,counts,n_groups):
    result = np.zeros((n_groups+1,2),np.int64)
    for i in range(len(rows)):
        result[n_groups,0] += sse_delta[i]
        result[n_groups,1] += mean_delta[i]
        colour = rows[i]
        for p in range(offsets[colour],offsets[colour+1]):
            g,count = groups[p],np.int64(counts[p])
            result[g,0] += count*sse_delta[i]
            result[g,1] += count*mean_delta[i]
    return result


def statistics(model,domain,photos,*,chunk=1 << 18,max_array_bytes=2684354560,tail_cache=None):
    """单修改的精确SSE及距离上界整数和变化；重叠组合不能相加冒充真实变化。"""
    size = model.m**3*6*(len(photos.hist)+1)*2*np.dtype(np.int64).itemsize
    persistent = domain.cache_bytes+sum(a.nbytes for a in vars(photos).values() if isinstance(a,np.ndarray))+sum(g.nbytes for g in photos.aggregate_groups)
    quality = photos.stability
    if quality is not None:persistent += quality.cache_array_bytes
    want_tail = quality is not None and quality.tail_ranking and tail_cache is not None
    tail_size = model.m**3*6*(len(photos.hist)+1)*3*np.dtype(np.int32).itemsize if want_tail else 0
    if persistent+size+tail_size > max_array_bytes:raise MemoryError("舍入预算统计超过冻结数组上限")
    deltas = np.zeros((model.m**3,6,len(photos.hist)+1,2),np.int64)
    tail_deltas = np.zeros((model.m**3,6,len(photos.hist)+1,3),np.int32) if want_tail else np.empty((0,0,0,0),np.int32)
    thresholds = quality.thresholds if want_tail else np.empty((0,3),np.int32)
    budgets = quality.budgets if want_tail else np.empty((0,3),np.int64)
    nodes = model.nodes.reshape(-1,3)
    roots_high = fg.root_bounds()[1]
    for start in range(0,len(domain.points),chunk):
        stop = min(len(domain.points),start+chunk)
        indices,weights = interp.tetra_index_weights_q(domain.points[start:stop],*model.tables(),model.m)
        _accumulate(start,indices,weights,nodes,domain.prediction,domain.truth,domain.squared,
            *photos.offsets_groups_counts,roots_high,deltas,thresholds,budgets,tail_deltas)
    if want_tail:tail_cache.update(tail_deltas=tail_deltas,tail_base=quality.current_tails(domain.hist))
    return deltas


def rank_helpers(model,domain,photos,deltas,change,excluded,helper_limit,*,tail_cache=None,tail_change=None):
    """共用两/三节点辅助排序；未获不相交证书时，预算相加仅作排序。"""
    full = fg.summary(domain.hist)
    nodes = model.nodes.reshape(-1,3).astype(np.int64)
    coordinates = np.array(np.unravel_index(np.arange(len(nodes)),(model.m,)*3)).T
    rms_bad = np.zeros(deltas.shape[:2],np.int16)
    mean_bad = np.zeros_like(rms_bad)
    worst = np.zeros(deltas.shape[:2],np.float64)
    total = np.zeros_like(worst)
    tail_bad = np.zeros_like(rms_bad)
    quality = photos.stability

    def budget(ds,dm,current_sse,current_mean,limit_sse,limit_mean,population):
        nonlocal rms_bad,mean_bad,worst,total
        sse = ds+current_sse-limit_sse
        mean = dm+current_mean-limit_mean
        rms_bad += sse > 0
        mean_bad += mean > 0
        worst = np.maximum(worst,np.maximum(sse/population,mean/(population*(1 << 24))))
        total += ds/population+dm/(population*(1 << 24))

    for g in range(len(photos.hist)):
        sse_limit = int(photos.sse_limit[g])
        mean_limit = int(photos.mean_limit_low[g])
        if quality is not None:
            sse_limit = min(sse_limit,int(quality.reference_sse[g]))
            mean_limit = min(mean_limit,int(quality.reference_low[g]))
        budget(deltas[:,:,g,0]+change[g,0],deltas[:,:,g,1]+change[g,1],int(photos.sse[g]),int(photos.high[g]),
            sse_limit,mean_limit,int(photos.hist[g].sum()))
    for ids,(mean_limit,sse_limit) in zip(photos.aggregate_groups,photos.aggregate_limits):
        # 比例交叉乘法先用Python整数求整除阈值，避免Q24归约在int64中乘1000。
        budget(deltas[:,:,ids,0].sum(axis=2)+int(change[ids,0].sum()),deltas[:,:,ids,1].sum(axis=2)+int(change[ids,1].sum()),
            int(photos.sse[ids].sum()),int(photos.high[ids].sum()),sse_limit,mean_limit*photos.numerator//photos.denominator,
            int(photos.hist[ids].sum()))
    full_sse_limit = int(domain.reference["sum_squared_error"])
    full_mean_limit = int(domain.reference["sum_lower_q24"])*domain.numerator//domain.denominator
    if quality is not None:
        full_sse_limit = min(full_sse_limit,int(quality.full_reference["sum_squared_error"]))
        full_mean_limit = min(full_mean_limit,int(quality.full_reference["sum_lower_q24"]))
    budget(deltas[:,:,-1,0]+change[-1,0],deltas[:,:,-1,1]+change[-1,1],int(full["sum_squared_error"]),int(full["sum_upper_q24"]),
        full_sse_limit,full_mean_limit,len(domain.points))
    if tail_cache is not None and "tail_deltas" in tail_cache:
        for g in range(len(quality.thresholds)):
            for j in range(3):
                if quality.budgets[g,j] < 0:continue
                # 单改压缩存int32，组合估计先提升int64，避免重叠相加的中间值溢出。
                predicted = tail_cache["tail_deltas"][:,:,g,j].astype(np.int64)+int(tail_cache["tail_base"][g,j])+int(tail_change[g,j])
                tail_bad += predicted > quality.budgets[g,j]
    disjoint = np.ones(len(nodes),bool)
    for node in excluded:disjoint &= np.any(np.abs(coordinates-coordinates[node]) > 1,axis=1)
    choices = []
    for option in range(6):
        channel,sign = option//2,2*(option%2)-1
        valid = (nodes[:,channel]+sign >= 0)&(nodes[:,channel]+sign <= 255)
        valid[list(excluded)] = False
        ids = np.flatnonzero(valid)
        order = np.lexsort((ids,total[ids,option],worst[ids,option],~disjoint[ids],mean_bad[ids,option],rms_bad[ids,option],tail_bad[ids,option]))[:helper_limit]
        for node in ids[order]:
            value = nodes[node].copy()
            value[channel] += sign
            helper = tr.Move(0,int(node),tuple(map(int,value)))
            key = (int(tail_bad[node,option]),int(rms_bad[node,option]),int(mean_bad[node,option]),not bool(disjoint[node]),float(worst[node,option]),float(total[node,option]),helper)
            roles = {"helper_node":int(node),"disjoint_cell_support_certificate":bool(disjoint[node]),
                "rank_rms_failed_count":key[1],"rank_mean_failed_count":key[2],
                "predicted_full_sse_delta":str(int(change[-1,0])+int(deltas[node,option,-1,0])),
                "predicted_full_mean_upper_q24_delta":str(int(change[-1,1])+int(deltas[node,option,-1,1]))}
            if quality is not None:roles["rank_stability_tail_failed_count"] = key[0]
            choices.append((key,helper,roles))
    return sorted(choices)[:helper_limit]


def pairs(model,domain,photos,ranked,*,primary_limit=8,helper_limit=16,trial_limit=128,max_array_bytes=2684354560,cache=None):
    primaries = []
    for proxy,move in ranked[:trial_limit]:
        trial = domain.trial([model],move)
        photo = photos.trial(trial["rows"],domain.squared[trial["rows"]],trial["squared"])
        if photo.loss < photos.loss:primaries.append((photo.loss,proxy,move))
    primaries = sorted(primaries)[:primary_limit]
    if not primaries:return [],{"method":"rounded","primaries":0,"pairs":0,"statistics_array_bytes":0}
    stats_cache = cache if cache is not None else {}
    deltas = statistics(model,domain,photos,max_array_bytes=max_array_bytes,tail_cache=stats_cache)
    sha = hashlib.sha256(memoryview(deltas).cast("B")).hexdigest()
    roots_high = fg.root_bounds()[1]
    if cache is not None:cache.update(deltas=deltas,primaries=primaries,model_signature=fg.signature([model]))
    generated,seen = [],set()
    for loss,proxy,primary in primaries:
        trial = domain.trial([model],primary)
        old = domain.squared[trial["rows"]]
        change = _reduce(trial["rows"],trial["squared"]-old,roots_high[trial["squared"]]-roots_high[old],
            *photos.offsets_groups_counts,len(photos.hist))
        tail_change = None
        if "tail_deltas" in stats_cache:
            from .stability import reduce_tails
            tail_change = reduce_tails(trial["rows"],old,trial["squared"],*photos.offsets_groups_counts,
                photos.stability.thresholds,photos.stability.budgets).astype(np.int64)
        for key,helper,roles in rank_helpers(model,domain,photos,deltas,change,[primary.node],helper_limit,tail_cache=stats_cache,tail_change=tail_change):
            roles = {"primary_node":primary.node,**roles}
            combined = tuple(sorted((primary,helper)))
            if combined in seen:continue
            seen.add(combined)
            generated.append(((loss,*key),combined,roles))
    generated.sort(key=lambda v:v[0])
    metadata = {"method":"rounded","primaries":len(primaries),"pairs":len(generated),
        "statistics_array_bytes":deltas.nbytes,"statistics_sha256":sha,"model_signature":fg.signature([model]),
        "scope":"全图片/聚合/全域预算排序；单改SSE和Q24距离上界变化为整数精确，支撑不相交时整对可相加；重叠及均值直方图相等豁免仍真实验收；float64只作排序"}
    if "tail_deltas" in stats_cache:
        metadata.update(stability_tail_array_bytes=stats_cache["tail_deltas"].nbytes,
            stability_tail_sha256=hashlib.sha256(memoryview(stats_cache["tail_deltas"]).cast("B")).hexdigest())
    return [(moves,roles) for key,moves,roles in generated],metadata
