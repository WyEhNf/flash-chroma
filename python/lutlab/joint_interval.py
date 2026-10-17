"""用整数输出区间及逐组必要界，对小型节点块作有证书的联合分支定界。"""
from collections import Counter
import math
import numpy as np
from . import automatic_compensation as ac,interp,io


def derive_nodes(model,primary_moves,closest_moves,regressions,maximum=4):
    order = []
    def add(node):
        if node not in order:order.append(int(node))
    for move in primary_moves:add(move["node"])
    for item in regressions:
        indices,weights = interp.tetra_index_weights_q(np.asarray([item["rgb"]],np.uint8),*model.tables(),model.m)
        for n,w in zip(indices[0],weights[0]):
            if w:add(n)
    for move in closest_moves:add(move["node"])
    if not order or len(order) > maximum:raise ValueError("反例导出的联合节点数量超出冻结上限，不截断")
    return order


class Problem:
    def __init__(self,model,points,truth,frequency,photos,full_histogram,nodes,*,max_delta,rgb_max,channel=2,max_assignments=10000):
        io.validate_sparse(model)
        if (type(max_delta) is not int or not 1 <= max_delta <= 8 or type(rgb_max) is not int or rgb_max < 0 or
                type(channel) is not int or channel not in (0,1,2) or not nodes or len(nodes) > 6 or len(set(nodes)) != len(nodes) or
                any(type(n) is not int or not 0 <= n < model.m**3 for n in nodes)):
            raise ValueError("联合节点/通道/范围不是有界整数问题")
        self.model,self.nodes,self.channel = ac.clone(model),list(nodes),channel
        self.points,self.truth = np.asarray(points).copy(),np.asarray(truth).copy()
        frequency = np.asarray(frequency)
        # 共用状态入口检查RGB8、频数及参考多重集；此处另建独立的必要界。
        self.state = ac.ConditionalScorer(model,points,truth,frequency,photos,full_histogram,nodes)
        self.domains = [sorted((d for d in range(-max_delta,max_delta+1) if 0 <= int(model.nodes.reshape(-1,3)[n,channel])+d <= 255),key=lambda d:(abs(d),d)) for n in nodes]
        self.assignments = math.prod(map(len,self.domains))
        if type(max_assignments) is not int or not 1 <= max_assignments <= 1000000 or self.assignments > max_assignments:
            raise ValueError("联合整数箱超过冻结赋值数上限")
        self.rgb_max = rgb_max
        indices,weights = interp.tetra_index_weights_q(points,*model.tables(),model.m)
        values = model.nodes.reshape(-1,3).astype(np.int64)
        self.sums = np.sum(weights[:,:,None].astype(np.int64)*values[indices],axis=1)
        self.matrix = np.stack([np.sum(np.where(indices == n,weights,0),axis=1) for n in nodes],axis=1).astype(np.int64)
        baseline = ((self.sums+32768)//65536).astype(np.int64)
        self.old = np.sum((baseline-self.truth)**2,axis=1)
        other = [c for c in range(3) if c != channel]
        self.other = np.sum((baseline[:,other]-self.truth[:,other])**2,axis=1)
        self.rows = self.state.active+["full"]
        self.counts = np.vstack([frequency[g] for g in self.state.active]+[np.ones(len(points),np.int64)]).astype(np.int64)
        maximum = 3*255**2
        self.root_low = np.array([math.isqrt(d << 48) for d in range(maximum+1)],np.int64)
        self.root_high = self.root_low+np.array([int(int(v)*int(v) != d << 48) for d,v in enumerate(self.root_low)],np.int64)
        self.old_mean_high = self.counts @ self.root_high[self.old]
        self.remaining_low,self.remaining_high = [],[]
        for depth in range(len(nodes)+1):
            self.remaining_low.append(sum((self.matrix[:,j]*min(self.domains[j]) for j in range(depth,len(nodes))),np.zeros(len(points),np.int64)))
            self.remaining_high.append(sum((self.matrix[:,j]*max(self.domains[j]) for j in range(depth,len(nodes))),np.zeros(len(points),np.int64)))
        self.tails = []
        for row,g in enumerate(self.rows):
            histogram = full_histogram if g == "full" else photos["groups"][g]["histogram"]
            for threshold,budget in ac.endpoints(histogram):
                outside = sum(n for d,n in histogram if d > threshold)-int(self.counts[row,self.old > threshold].sum())
                self.tails.append((row,threshold,budget-outside))
        outside = Counter(dict(full_histogram))
        outside.subtract(map(int,self.old))
        self.outside_max = max((d for d,n in outside.items() if n),default=0)

    def lower_squared(self,prefix,total=None):
        if total is None:total = self.matrix[:,:len(prefix)] @ np.asarray(prefix,np.int64)
        depth = len(prefix)
        lower = (self.sums[:,self.channel]+total+self.remaining_low[depth]+32768)//65536
        upper = (self.sums[:,self.channel]+total+self.remaining_high[depth]+32768)//65536
        distance = np.maximum(np.maximum(lower-self.truth[:,self.channel],self.truth[:,self.channel]-upper),0)
        return self.other+distance*distance

    def certificate(self,prefix,total):
        if self.outside_max > self.rgb_max**2:return {"kind":"outside_max","squared":self.outside_max}
        squared = self.lower_squared(prefix,total)
        bad = np.flatnonzero(squared > self.rgb_max**2)
        if len(bad):return {"kind":"rgb_max","point":int(bad[0]),"squared_lower":int(squared[bad[0]])}
        delta = self.counts @ (squared-self.old)
        bad = np.flatnonzero(delta > 0)
        if len(bad):
            row = int(bad[0])
            return {"kind":"rms","group":self.rows[row],"sse_delta_lower":str(int(delta[row]))}
        mean = self.counts @ self.root_low[squared]-self.old_mean_high
        bad = np.flatnonzero(mean > 0)
        if len(bad):
            row = int(bad[0])
            return {"kind":"mean","group":self.rows[row],"sum_delta_lower_q24":str(int(mean[row]))}
        for row,threshold,budget in self.tails:
            count = int(self.counts[row,squared > threshold].sum())
            if count > budget:return {"kind":"tail","group":self.rows[row],"threshold_squared":threshold,"local_budget":budget,"local_count_lower":count}
        return None

    def candidate(self,prefix):
        if len(prefix) != len(self.nodes) or any(d not in domain for d,domain in zip(prefix,self.domains)):raise ValueError("候选没有完整指定冻结整数域")
        result = ac.clone(self.model)
        for n,d in zip(self.nodes,prefix):result.nodes.reshape(-1,3)[n,self.channel] = int(result.nodes.reshape(-1,3)[n,self.channel])+d
        return result


def solve(problem,assess):
    """assess只处理通过固定保护的真实叶子，返回原完整保护的回执名及接受状态。"""
    terminals,incumbent = [],None
    def visit(prefix,total):
        nonlocal incumbent
        cost = sum(abs(d) for d in prefix)
        item = {"deltas":prefix.copy()}
        if incumbent is not None and cost >= incumbent["l1"]:
            item.update(kind="objective",minimum_l1=cost,incumbent=incumbent.copy())
        else:
            proof = problem.certificate(prefix,total)
            if proof is not None:item.update(proof)
            elif len(prefix) == len(problem.nodes):
                candidate = problem.candidate(prefix)
                score = problem.state.score(candidate)
                item.update(kind="leaf",score=score,record=None,accepted=False)
                if not score["fixed_failed"]:
                    receipt = assess(candidate,prefix)
                    item.update(receipt)
                    if receipt["accepted"]:incumbent = {"name":receipt["record"],"l1":cost,"deltas":prefix.copy()}
            else:
                depth = len(prefix)
                for delta in problem.domains[depth]:visit(prefix+[delta],total+problem.matrix[:,depth]*delta)
                return
        item["covered_assignments"] = math.prod(len(d) for d in problem.domains[len(prefix):])
        terminals.append(item)
    visit([],np.zeros(len(problem.points),np.int64))
    if sum(t["covered_assignments"] for t in terminals) != problem.assignments:raise AssertionError("联合搜索证书没有覆盖全部整数域")
    return {"nodes":problem.nodes,"domains":problem.domains,"channel":problem.channel,"rgb_max":problem.rgb_max,"assignments":problem.assignments,
        "terminals":terminals,"incumbent":incumbent,"minimum_l1_proven_within_box":incumbent is not None,
        "scope":"固定节点/轴表/单通道整数箱的完整分支覆盖；输出区间和逐组必要界安全剪枝，真实叶子走固定及原保护；最小L1只在此冻结箱内，不证明全局模型最优"}
