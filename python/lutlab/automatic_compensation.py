"""固定局部完整支撑上按真实条件输出排序，有限选择第一/第二辅助。"""
from collections import Counter
import copy
import hashlib
import itertools
import math
import numpy as np
from . import histogram_delta as hd,interp,io


def signature(model):
    h = hashlib.sha256(model.m.to_bytes(4,"little"))
    h.update(model.nodes.tobytes())
    for table in model.tables():h.update(table.tobytes())
    return h.hexdigest()


def clone(model):
    idx,frac = model.tables()
    return io.SparseLut(model.grid.copy(),model.nodes.copy(),idx.copy(),frac.copy())


def moves(before,after):
    a,b = before.nodes.reshape(-1,3),after.nodes.reshape(-1,3)
    return [{"node":int(n),"before":a[n].tolist(),"after":b[n].tolist()} for n in np.flatnonzero(np.any(a != b,axis=1))]


def neighbors(model,primary_nodes,*,radius=1,maximum=64):
    if radius != 1:raise ValueError("本阶段只允许一格邻域")
    nodes = set()
    for node in primary_nodes:
        xyz = (node//model.m**2,node//model.m%model.m,node%model.m)
        for p in itertools.product(*(range(max(0,c-1),min(model.m,c+2)) for c in xyz)):
            nodes.add((p[0]*model.m+p[1])*model.m+p[2])
    nodes -= set(primary_nodes)
    if len(nodes) > maximum:raise ValueError("自动辅助邻域超出冻结上限，不隐式截断")
    return sorted(nodes)


def pairs(hist):return [[int(d),int(hist[d])] for d in np.flatnonzero(hist)]


def update(reference,old,new):
    value = Counter(dict(reference))
    for d,n in old:value[d] -= n
    for d,n in new:value[d] += n
    if any(n < 0 for n in value.values()):raise ValueError("局部频数不是完整参考的子多重集")
    return [[int(d),int(n)] for d,n in sorted(value.items()) if n]


def endpoints(hist):
    n = sum(v for d,v in hist)
    rank,rem = divmod(99*(n-1),100)
    conditions = {hist[-1][0]:0}
    for pos in (rank,rank+int(rem > 0)):
        count = 0
        for d,v in hist:
            count += v
            if count > pos:
                conditions[d] = min(conditions.get(d,n),n-pos-1)
                break
    return sorted(conditions.items())


def cost(hist,conditions):
    loss = 0
    for c in conditions:
        t,b = c["threshold_squared"],c["allowed_tail_pixels"]
        remaining = max(0,sum(n for d,n in hist if d > t)-b)
        for d,n in hist:
            if d <= t:continue
            take = min(remaining,n)
            loss += take*(d-t)
            remaining -= take
            if not remaining:break
    return loss


def cvar(hist):
    k = (sum(n for d,n in hist)+99)//100
    remaining,low,high,selected = k,0,0,[]
    for d,n in reversed(hist):
        take = min(remaining,n)
        root = math.isqrt(d << 48)
        low += take*root
        high += take*(root+int(root*root != d << 48))
        selected.append([d,take])
        remaining -= take
        if not remaining:break
    return low,high,selected


class ConditionalScorer:
    def __init__(self,model,points,truth,frequency,photos,full_histogram,allowed_nodes):
        io.validate_sparse(model)
        self.model = clone(model)
        self.signature = signature(model)
        self.points,self.truth,self.frequency = np.asarray(points).copy(),np.asarray(truth).copy(),np.asarray(frequency).copy()
        if (not len(points) or self.points.dtype != np.uint8 or self.points.ndim != 2 or self.points.shape[1] != 3 or self.truth.dtype != np.uint8 or self.truth.shape != self.points.shape
                or len(np.unique(self.points.astype(np.int64) @ np.array([65536,256,1]))) != len(points)):
            raise ValueError("条件状态必须绑定互异RGB8支撑及同形参考")
        if (self.frequency.shape != (len(photos["groups"]),len(points)) or self.frequency.dtype.kind not in "iu" or np.any(self.frequency < 0)
                or np.any(self.frequency > 1 << 30)):
            raise ValueError("条件状态频数格式或范围无效")
        self.frequency = self.frequency.astype(np.int64)
        self.photos,self.full = copy.deepcopy(photos),copy.deepcopy(full_histogram)
        self.allowed_nodes = set(allowed_nodes)
        self.indices,self.weights = interp.tetra_index_weights_q(self.points,*model.tables(),model.m)
        baseline = interp.apply_tetra_q16(model,points).astype(np.int32)
        self.old = np.sum((baseline-self.truth)**2,axis=1)
        self.local_full = pairs(np.bincount(self.old))
        if any(n > dict(self.full).get(d,0) for d,n in self.local_full):raise ValueError("局部完整域频数不是参考的子集")
        self.active,self.local_photos = [],{}
        for g,base in enumerate(photos["groups"]):
            counts = self.frequency[g]
            if not np.any(counts):continue
            local = pairs(np.bincount(self.old,weights=counts).astype(np.int64))
            if sum(n for d,n in local) > sum(n for d,n in base["histogram"]):raise ValueError("局部照片像素数超过参考")
            if any(n > dict(base["histogram"]).get(d,0) for d,n in local):raise ValueError("局部照片频数不是参考的子集")
            self.active.append(g)
            self.local_photos[g] = local
        self.full_sse = sum(d*n for d,n in self.full)
        self.full_cvar = cvar(self.full)

    def score(self,candidate):
        io.validate_sparse(candidate)
        if candidate.m != self.model.m or not all(np.array_equal(a,b) for a,b in zip(candidate.tables(),self.model.tables())):
            raise ValueError("条件候选轴表与冻结状态不同")
        changed = np.flatnonzero(np.any(candidate.nodes.reshape(-1,3) != self.model.nodes.reshape(-1,3),axis=1))
        if not set(map(int,changed)) <= self.allowed_nodes:raise ValueError("候选修改了完整支撑之外的节点")
        nodes = candidate.nodes.reshape(-1,3).astype(np.int64)
        mapped = ((np.sum(self.weights[:,:,None].astype(np.int64)*nodes[self.indices],axis=1)+32768) >> 16).astype(np.int32)
        squared = np.sum((mapped-self.truth)**2,axis=1)
        full = update(self.full,self.local_full,pairs(np.bincount(squared)))
        failed,group_deltas,loss = [],[],self.photos["loss"]
        def fixed(before,after,prefix):
            if sum(d*n for d,n in after) > sum(d*n for d,n in before):failed.append(prefix+".rms")
            if not hd.mean_difference(before,after)["accepted"]:failed.append(prefix+".mean")
            for i,(t,b) in enumerate(endpoints(before)):
                if sum(n for d,n in after if d > t) > b:failed.append(prefix+f".tail{i}")
        for g in self.active:
            base = self.photos["groups"][g]
            new = pairs(np.bincount(squared,weights=self.frequency[g]).astype(np.int64))
            current = update(base["histogram"],self.local_photos[g],new)
            fixed(base["histogram"],current,f"group{g}")
            loss += cost(current,base["constraints"])-sum(base["costs"])
            delta = sum(d*n for d,n in current)-sum(d*n for d,n in base["histogram"])
            if delta:group_deltas.append({"group":g,"sse_delta":str(delta)})
        fixed(self.full,full,"full")
        low,high,selected = cvar(full)
        if high > self.full_cvar[0] and selected != self.full_cvar[2]:failed.append("full.cvar")
        if loss > self.photos["loss"]:failed.append("primary_loss")
        maximum = full[-1][0]
        return {"fixed_failed":failed,"primary_loss":int(loss),"max_squared":maximum,"full_sse_delta":str(sum(d*n for d,n in full)-self.full_sse),
            "group_sse_deltas":group_deltas,"nonimproving_max":maximum >= self.full[-1][0],
            "scope":"局部完整支撑的真实条件Q16排序；固定指标/历史缺口精确复算，原混合预算及最终选择仍须完整保护验收"}


def ranked_helpers(baseline,prefix,state,helper_nodes,*,deltas=(-2,-1,1,2),exclude=()):
    if not 1 <= len(deltas) <= 8 or len(set(deltas)) != len(deltas) or any(type(d) is not int or not 1 <= abs(d) <= 4 for d in deltas):
        raise ValueError("辅助幅度必须是有限、唯一的非零整数")
    if signature(baseline) != state.signature:raise ValueError("辅助候选起点与条件状态签名不同")
    changed_nodes = {m["node"] for m in moves(baseline,prefix)} | set(exclude)
    ranked = []
    for node in helper_nodes:
        if node in changed_nodes:continue
        for channel in range(3):
            for delta in deltas:
                old = int(baseline.nodes.reshape(-1,3)[node,channel])
                if not 0 <= old+delta <= 255:continue
                candidate = clone(prefix)
                candidate.nodes.reshape(-1,3)[node,channel] = old+delta
                score = state.score(candidate)
                key = (int(score["nonimproving_max"]),len(score["fixed_failed"]),score["max_squared"],score["primary_loss"],
                    sum(sum(abs(a-b) for a,b in zip(m["before"],m["after"])) for m in moves(baseline,candidate)),node,channel,delta)
                ranked.append({"helper":{"node":int(node),"channel":channel,"delta":int(delta)},"rank_key":list(key),"score":score})
    return sorted(ranked,key=lambda r:tuple(r["rank_key"]))


def apply_helper(prefix,baseline,helper):
    result = clone(prefix)
    n,c,d = [helper[k] for k in ("node","channel","delta")]
    result.nodes.reshape(-1,3)[n,c] = int(baseline.nodes.reshape(-1,3)[n,c])+d
    return result
