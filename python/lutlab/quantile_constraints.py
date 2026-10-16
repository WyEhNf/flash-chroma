"""保留像素频数的逐图尾部预算与事务式局部更新；离线使用。"""
from __future__ import annotations
from dataclasses import dataclass
import numpy as np
from numba import njit
from . import error_analysis as ea, full_domain_guard as fg


def invert(keys,groups,counts,n_colours,n_groups):
    """颜色到图片/频数的稳定倒排，重复像素不能变成等权唯一颜色。"""
    if (keys.dtype != np.uint32 or groups.dtype != np.uint8 or counts.dtype != np.uint32
            or keys.ndim != 1 or groups.shape != keys.shape or counts.shape != keys.shape or not len(keys)
            or not 0 < n_colours <= 256**3 or not 0 < n_groups <= 255
            or np.any(keys >= n_colours) or np.any(groups >= n_groups) or np.any(counts == 0)
            or int(counts.astype(np.uint64).sum()) > 1 << 30 or len(keys) >= 1 << 32):
        raise ValueError("颜色/图片倒排输入或频数范围无效")
    order = np.argsort(keys,kind="stable")
    offsets = np.empty(n_colours+1,np.uint32)
    offsets[0] = 0
    offsets[1:] = np.cumsum(np.bincount(keys.astype(np.int64),minlength=n_colours),dtype=np.uint32)
    return offsets,groups[order].copy(),counts[order].copy()


@njit(cache=True)
def _hist(keys,offsets,groups,counts,errors,n_groups,bins):
    hist = np.zeros((n_groups,bins),np.int64)
    for colour in keys:
        for j in range(offsets[colour],offsets[colour+1]):
            hist[groups[j],errors[colour]] += counts[j]
    return hist


def endpoints(hist):
    """q_k<=t当且仅当count(d²>t)<=N-k-1；两个端点非增是p99非增的充分条件。"""
    n = int(hist.sum())
    if not n:raise ValueError("图片组不能为空")
    lo,rem = divmod(99*(n-1),100)
    ranks = [lo,lo+int(rem > 0)]
    cumulative = np.cumsum(hist)
    values = np.searchsorted(cumulative,ranks,side="right")
    constraints = {int(np.flatnonzero(hist)[-1]):0}
    for rank,value in zip(ranks,values):
        constraints[int(value)] = min(constraints.get(int(value),n),n-rank-1)
    return sorted(constraints.items())


@njit(cache=True)
def _costs(hist,tails,thresholds,budgets):
    costs = np.zeros_like(thresholds)
    cutoffs = thresholds.copy()
    for g in range(len(hist)):
        for j in range(3):
            if budgets[g,j] < 0:continue
            remaining = tails[g,j]-budgets[g,j]
            if remaining <= 0:continue
            for d in range(thresholds[g,j]+1,hist.shape[1]):
                take = min(remaining,hist[g,d])
                costs[g,j] += take*(d-thresholds[g,j])
                remaining -= take
                if remaining == 0:
                    cutoffs[g,j] = d
                    break
    return costs,cutoffs


@njit(cache=True)
def _update(hist,low,high,sse,tails,offsets,groups,counts,rows,old,new,thresholds,budgets,roots_low,roots_high):
    touched = np.zeros(len(hist),np.bool_)
    for i in range(len(rows)):
        a,b = old[i],new[i]
        if a == b:continue
        c = rows[i]
        for k in range(offsets[c],offsets[c+1]):
            g,w = groups[k],np.int64(counts[k])
            hist[g,a] -= w
            hist[g,b] += w
            low[g] += w*(roots_low[b]-roots_low[a])
            high[g] += w*(roots_high[b]-roots_high[a])
            sse[g] += w*(b-a)
            touched[g] = True
            for j in range(3):
                if budgets[g,j] >= 0:
                    t = thresholds[g,j]
                    tails[g,j] += w*(int(b > t)-int(a > t))
    return touched


@njit(cache=True)
def _priorities(keys,errors,offsets,groups,counts,thresholds,budgets,costs,cutoffs):
    priority = np.zeros(len(keys),np.int64)
    for i in range(len(keys)):
        c = keys[i]
        d = errors[c]
        for k in range(offsets[c],offsets[c+1]):
            g = groups[k]
            for j in range(3):
                if budgets[g,j] >= 0 and costs[g,j] > 0 and thresholds[g,j] < d <= cutoffs[g,j]:
                    priority[i] += np.int64(counts[k])*(d-thresholds[g,j])
    return priority


@dataclass(frozen=True)
class Trial:
    generation: int
    rows: np.ndarray
    old: np.ndarray
    new: np.ndarray
    loss: int
    failed: tuple


class GroupState:
    """只更新受影响颜色的图片直方图；所有预算在初态冻结。"""
    def __init__(self,inverse,n_groups,original,current,aggregate_groups,*,numerator=1005,denominator=1000,bins=3*255**2+1):
        self.offsets,self.groups,self.counts = inverse
        if (len(original) != len(self.offsets)-1 or np.shape(original) != np.shape(current)
                or original.dtype.kind not in "iu" or current.dtype.kind not in "iu"
                or np.any(original < 0) or np.any(current < 0) or np.any(original >= bins) or np.any(current >= bins)
                or not 1 <= bins <= 3*255**2+1 or denominator <= 0 or numerator <= denominator):
            raise ValueError("图片状态误差域或冻结预算无效")
        self.keys = np.flatnonzero(np.diff(self.offsets)).astype(np.uint32)
        self.current = np.array(current,np.int32,copy=True)
        self.original_hist = _hist(self.keys,*inverse,original,n_groups,bins)
        self.hist = _hist(self.keys,*inverse,self.current,n_groups,bins)
        self.initial_hist = self.hist.copy()
        self.roots_low,self.roots_high = (r[:bins] for r in fg.root_bounds())
        self.low,self.high = self.hist @ self.roots_low,self.hist @ self.roots_high
        self.sse = self.hist @ np.arange(bins,dtype=np.int64)
        old_low = self.original_hist @ self.roots_low
        old_sse = self.original_hist @ np.arange(bins,dtype=np.int64)
        self.mean_limit_low = np.maximum(old_low,self.low)
        self.sse_limit = np.maximum(old_sse,self.sse)
        self.thresholds = np.zeros((n_groups,3),np.int64)
        self.budgets = np.full((n_groups,3),-1,np.int64)
        self.tails = np.zeros((n_groups,3),np.int64)
        for g in range(n_groups):
            for j,(threshold,budget) in enumerate(endpoints(self.original_hist[g])):
                self.thresholds[g,j],self.budgets[g,j] = threshold,budget
                self.tails[g,j] = self.hist[g,threshold+1:].sum()
        self.costs,self.cutoffs = _costs(self.hist,self.tails,self.thresholds,self.budgets)
        self.aggregate_groups = [np.asarray(g,np.int64) for g in aggregate_groups]
        if any(not len(g) or np.any(g < 0) or np.any(g >= n_groups) or len(np.unique(g)) != len(g) for g in self.aggregate_groups):
            raise ValueError("聚合保护组无效")
        self.aggregate_limits = [(int(self.low[g].sum()),int(self.sse[g].sum())) for g in self.aggregate_groups]
        self.numerator,self.denominator = numerator,denominator
        self.generation = 0

    @property
    def loss(self):return int(self.costs.sum())

    def _guards(self,touched):
        failed = []
        for g in np.flatnonzero(touched):
            if self.sse[g] > self.sse_limit[g]:failed.append(f"group{g}.rms")
            if self.high[g] > self.mean_limit_low[g] and not (np.array_equal(self.hist[g],self.original_hist[g]) or np.array_equal(self.hist[g],self.initial_hist[g])):
                failed.append(f"group{g}.mean")
        for k,(indices,(mean_low,sse_limit)) in enumerate(zip(self.aggregate_groups,self.aggregate_limits)):
            # 先转Python整数，避免跨组/预算交叉乘法在int64中溢出。
            if int(self.high[indices].sum())*self.denominator > mean_low*self.numerator:
                failed.append(f"aggregate{k}.mean")
            if int(self.sse[indices].sum()) > sse_limit:failed.append(f"aggregate{k}.rms")
        return tuple(failed)

    def _apply(self,rows,old,new):
        return _update(self.hist,self.low,self.high,self.sse,self.tails,*self.offsets_groups_counts,
            rows,old,new,self.thresholds,self.budgets,self.roots_low,self.roots_high)

    @property
    def offsets_groups_counts(self):return self.offsets,self.groups,self.counts

    def trial(self,rows,old,new):
        rows,old,new = (np.asarray(a) for a in (rows,old,new))
        if (rows.ndim != 1 or old.shape != rows.shape or new.shape != rows.shape or rows.dtype.kind not in "iu"
                or np.any(rows < 0) or np.any(rows >= len(self.current)) or len(np.unique(rows)) != len(rows)
                or new.dtype.kind not in "iu" or old.dtype.kind not in "iu" or np.any(new < 0) or np.any(new >= self.hist.shape[1])
                or not np.array_equal(self.current[rows],old)):
            raise ValueError("局部试探含重复、越界或陈旧平方误差")
        changed = old != new
        rows,old,new = [np.array(a[changed],dtype=d,copy=True) for a,d in zip((rows,old,new),(np.int32,np.int32,np.int32))]
        try:
            touched = self._apply(rows,old,new)
            costs,_ = _costs(self.hist,self.tails,self.thresholds,self.budgets)
            loss,failed = int(costs.sum()),self._guards(touched)
        finally:
            self._apply(rows,new,old)
        for a in (rows,old,new):a.flags.writeable = False
        return Trial(self.generation,rows,old,new,loss,failed)

    def commit(self,trial):
        if (trial.generation != self.generation or not np.array_equal(self.current[trial.rows],trial.old)
                or trial.failed or trial.loss >= self.loss):
            raise ValueError("图片回执陈旧、未通过保护或没有严格减少尾部缺口")
        touched = self._apply(trial.rows,trial.old,trial.new)
        costs,cutoffs = _costs(self.hist,self.tails,self.thresholds,self.budgets)
        if int(costs.sum()) != trial.loss or self._guards(touched):
            self._apply(trial.rows,trial.new,trial.old)
            raise ValueError("图片提交与试探回执不同")
        self.current[trial.rows] = trial.new
        self.costs,self.cutoffs = costs,cutoffs
        self.generation += 1

    def focus(self,count):
        if not isinstance(count,int) or count <= 0:raise ValueError("热点数量必须为正整数")
        priority = _priorities(self.keys,self.current,*self.offsets_groups_counts,self.thresholds,self.budgets,self.costs,self.cutoffs)
        available = np.flatnonzero(priority > 0)
        if not len(available):return np.empty(0,np.uint32),np.empty(0,np.int64)
        k = min(count,len(available))
        if k < len(available):
            threshold = np.partition(priority[available],len(available)-k)[len(available)-k]
            above = np.flatnonzero(priority > threshold)
            equal = np.flatnonzero(priority == threshold)[:k-len(above)]
            selected = np.concatenate((above,equal))
        else:selected = available
        selected = selected[np.lexsort((self.keys[selected],-priority[selected]))]
        return self.keys[selected],priority[selected]

    def recheck(self):
        rebuilt = _hist(self.keys,*self.offsets_groups_counts,self.current,len(self.hist),self.hist.shape[1])
        if not (np.array_equal(rebuilt,self.hist) and np.array_equal(self.hist @ self.roots_low,self.low)
                and np.array_equal(self.hist @ self.roots_high,self.high)
                and np.array_equal(self.hist @ np.arange(self.hist.shape[1],dtype=np.int64),self.sse)):
            raise AssertionError("图片增量直方图或整数归约与完整重建不同")

    def report(self):
        records = []
        for g,hist in enumerate(self.hist):
            records.append({"group":g,"metrics":ea.hist_metrics(hist),"costs":self.costs[g].tolist(),
                "constraints":[{"threshold_squared":int(t),"allowed_tail_pixels":int(b),"actual_tail_pixels":int(n)}
                    for t,b,n in zip(self.thresholds[g],self.budgets[g],self.tails[g]) if b >= 0],
                "histogram":[[int(d),int(hist[d])] for d in np.flatnonzero(hist)],
                "original_histogram":[[int(d),int(self.original_hist[g,d])] for d in np.flatnonzero(self.original_hist[g])],
                "initial_histogram":[[int(d),int(self.initial_hist[g,d])] for d in np.flatnonzero(self.initial_hist[g])],
                "mean_sum_lower_q24":str(int(self.low[g])),"mean_sum_upper_q24":str(int(self.high[g])),
                "mean_limit_lower_q24":str(int(self.mean_limit_low[g])),
                "sse":str(int(self.sse[g])),"sse_limit":str(int(self.sse_limit[g])),
                "original_metrics":ea.hist_metrics(self.original_hist[g]),"initial_metrics":ea.hist_metrics(self.initial_hist[g])})
        aggregates = [{"groups":g.tolist(),"initial_sum_lower_q24":str(mean),"initial_sse":str(sse),
            "final_sum_upper_q24":str(int(self.high[g].sum())),"final_sse":str(int(self.sse[g].sum()))}
            for g,(mean,sse) in zip(self.aggregate_groups,self.aggregate_limits)]
        return {"loss":self.loss,"feasible":self.loss == 0,"generation":self.generation,"groups":records,
            "aggregate_mean_ratio":[self.numerator,self.denominator],"aggregates":aggregates,
            "guards_accepted":not self._guards(np.ones(len(self.hist),bool)),
            "cache_array_bytes":sum(a.nbytes for a in vars(self).values() if isinstance(a,np.ndarray))+sum(g.nbytes for g in self.aggregate_groups),
            "scope":"给定图片/频数上max及p99两个秩端点的充分约束；mean/RMS保护上限固定，不是未知图片保证"}
