"""冻结阶段参考的四指标充分保护；不替换历史误差阈值或原预算。"""
import numpy as np
from numba import njit
from . import full_domain_guard as fg,quantile_constraints as qc,histogram_delta as hd


def sparse(hist):return [[int(d),int(hist[d])] for d in np.flatnonzero(hist)]


@njit(cache=True)
def update_tails(rows,old,new,offsets,groups,counts,thresholds,budgets,tails):
    for i in range(len(rows)):
        for p in range(offsets[rows[i]],offsets[rows[i]+1]):
            g,count = groups[p],np.int64(counts[p])
            for j in range(3):
                if budgets[g,j] >= 0:
                    t = thresholds[g,j]
                    tails[g,j] += count*(int(new[i] > t)-int(old[i] > t))


@njit(cache=True)
def reduce_tails(rows,old,new,offsets,groups,counts,thresholds,budgets):
    # invert约束所有组总频数<=2^30，每个分量前缀绝对值亦<=2^30，int32不会溢出。
    result = np.zeros(thresholds.shape,np.int32)
    full = len(thresholds)-1
    for i in range(len(rows)):
        for j in range(3):
            if budgets[full,j] >= 0:
                t = thresholds[full,j]
                result[full,j] += int(new[i] > t)-int(old[i] > t)
        for p in range(offsets[rows[i]],offsets[rows[i]+1]):
            g,count = groups[p],np.int64(counts[p])
            for j in range(3):
                if budgets[g,j] >= 0:
                    t = thresholds[g,j]
                    result[g,j] += count*(int(new[i] > t)-int(old[i] > t))
    return result


class Stability:
    def __init__(self,photos,domain,*,tail_ranking):
        if photos.stability is not None:raise ValueError("不得重置已经冻结的稳定性参考")
        if len(domain.points) > 256**3:raise ValueError("稳定性研究限于RGB8完整域或其子集")
        self.reference_hist = photos.hist.copy()
        self.reference_low = photos.low.copy()
        self.reference_sse = photos.sse.copy()
        self.full_hist = domain.hist.copy()
        self.full_reference = fg.summary(self.full_hist)
        self.inverse = photos.offsets_groups_counts
        self.tail_ranking = bool(tail_ranking)
        self.thresholds = np.zeros((len(photos.hist)+1,3),np.int32)
        self.budgets = np.full(self.thresholds.shape,-1,np.int64)
        for g,hist in enumerate([*self.reference_hist,self.full_hist]):
            for j,(threshold,budget) in enumerate(qc.endpoints(hist)):
                self.thresholds[g,j],self.budgets[g,j] = threshold,budget
        self.photo_tails = self.counts(self.reference_hist)
        self.reference_signature = domain.model_signature

    @property
    def cache_array_bytes(self):
        return sum(a.nbytes for a in (self.reference_hist,self.reference_low,self.reference_sse,self.full_hist,
            self.thresholds,self.budgets,self.photo_tails))

    def counts(self,histograms):
        return np.array([[int(hist[t+1:].sum()) if b >= 0 else 0 for t,b in zip(self.thresholds[g],self.budgets[g])]
            for g,hist in enumerate(histograms)],np.int64)

    def current_tails(self,full_hist):
        full = [int(full_hist[t+1:].sum()) if b >= 0 else 0 for t,b in zip(self.thresholds[-1],self.budgets[-1])]
        return np.vstack((self.photo_tails,np.array(full,np.int64)))

    def apply(self,rows,old,new):
        update_tails(rows,old,new,*self.inverse,self.thresholds,self.budgets,self.photo_tails)

    def check_photos(self,hist,low,high,sse,touched):
        failed = []
        for g in np.flatnonzero(touched):
            if sse[g] > self.reference_sse[g]:failed.append(f"stability.group{g}.rms")
            if high[g] > self.reference_low[g] and not hd.mean_difference(sparse(self.reference_hist[g]),sparse(hist[g]))["accepted"]:
                failed.append(f"stability.group{g}.mean_bound")
            for j in range(3):
                if self.budgets[g,j] >= 0 and self.photo_tails[g,j] > self.budgets[g,j]:failed.append(f"stability.group{g}.tail{j}")
        return failed

    def check_full(self,hist,summary):
        failed = []
        ref = self.full_reference
        if int(summary["sum_squared_error"]) > int(ref["sum_squared_error"]):failed.append("stability.full.rms")
        if int(summary["sum_upper_q24"]) > int(ref["sum_lower_q24"]) and not hd.mean_difference(ref["histogram"],summary["histogram"])["accepted"]:
            failed.append("stability.full.mean_bound")
        for j,(t,b) in enumerate(zip(self.thresholds[-1],self.budgets[-1])):
            if b >= 0 and int(hist[t+1:].sum()) > b:failed.append(f"stability.full.tail{j}")
        return failed

    def reference_report(self,model_sha256):
        return {"model_sha256":model_sha256,"model_signature":self.reference_signature,"tail_ranking":self.tail_ranking,
            "histograms":[[[int(d),int(h[d])] for d in np.flatnonzero(h)] for h in self.reference_hist],
            "full":self.full_reference,"thresholds":self.thresholds.tolist(),"budgets":self.budgets.tolist(),
            "cache_array_bytes":self.cache_array_bytes,
            "scope":"固定阶段参考，mean/RMS及p99两个秩端点/max的充分非退化条件；不含20审计反馈；Q24可能保守"}

    def certificate(self,photos,full_hist,full_summary=None):
        if full_summary is None:full_summary = fg.summary(full_hist)
        failed = self.check_photos(photos.hist,photos.low,photos.high,photos.sse,np.ones(len(photos.hist),bool))+self.check_full(full_hist,full_summary)
        return {"accepted":not failed,"failed":failed,"photos":[{"group":g,"sse":str(int(photos.sse[g])),
            "mean_upper_q24":str(int(photos.high[g])),"same_histogram":bool(np.array_equal(photos.hist[g],self.reference_hist[g])),
            "tails":self.photo_tails[g].tolist()} for g in range(len(photos.hist))],"full":full_summary,
            "full_tails":self.current_tails(full_hist)[-1].tolist(),"scope":"固定参考的整数充分证书；终态另对完整直方图独立复核"}

    def recheck(self,photos):
        if not np.array_equal(self.photo_tails,self.counts(photos.hist)):
            raise AssertionError("稳定性尾部增量计数与当前直方图不同")
