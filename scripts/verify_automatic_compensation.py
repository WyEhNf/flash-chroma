"""仅用标准库重算全部条件候选分数、合法集合和两层搜索树。"""
from collections import Counter
import copy
import hashlib
import math
from pathlib import Path
import runpy


HERE = Path(__file__).resolve().parent
MEAN = runpy.run_path(str(HERE / "verify_stability.py"))["signed_mean_upper"]
SUMMARY = runpy.run_path(str(HERE / "verify_quantile_constraints.py"))["summary"]


def patched(base,delta):
    hist = Counter(dict(base))
    hist.update(delta)
    if any(n < 0 for n in hist.values()):raise ValueError("独立条件频数出现负值")
    return [[d,n] for d,n in sorted(hist.items()) if n]


def cost(hist,conditions):
    total = 0
    for c in conditions:
        threshold,budget = c["threshold_squared"],c["allowed_tail_pixels"]
        remaining = max(0,sum(n for d,n in hist if d > threshold)-budget)
        for d,n in hist:
            if d <= threshold:continue
            take = min(remaining,n)
            total += take*(d-threshold)
            remaining -= take
            if not remaining:break
    return total


def tail(hist):
    remaining = (sum(n for d,n in hist)+99)//100
    low,high,selected = 0,0,[]
    for d,n in reversed(hist):
        take = min(remaining,n)
        root = math.isqrt(d << 48)
        low += root*take
        high += (root+int(root*root != d << 48))*take
        selected.append([d,take])
        remaining -= take
        if not remaining:break
    return low,high,selected


def verify_trace(folder,plan,trace,model,source,points,frequencies,photos,domain,records):
    def load(name):
        import json
        return json.loads((folder / name).read_text(encoding="utf-8"))
    def changed(candidate):
        return [(n,list(model.data[model.node_offset+3*n:model.node_offset+3*n+3]),
                    list(candidate.data[model.node_offset+3*n:model.node_offset+3*n+3])) for n in range(model.m**3)
                if model.data[model.node_offset+3*n:model.node_offset+3*n+3] != candidate.data[model.node_offset+3*n:model.node_offset+3*n+3]]
    def candidate(prefix,helper):
        copied = copy.copy(prefix)
        data = bytearray(prefix.data)
        offset = model.node_offset+3*helper["node"]+helper["channel"]
        data[offset] = model.data[offset]+helper["delta"]
        copied.data = bytes(data)
        return copied
    parent = next(c for c in load("reference/results.json")["cases"] if c["case"]["id"] == plan["case"])
    anchor = parent["final"]["cube"]["hotspots"][0]["rgb"]
    offset = ((anchor[0]*256+anchor[1])*256+anchor[2])*3
    target = source[offset:offset+3]
    channel = max(range(3),key=lambda c:abs(model.apply(anchor)[c]-target[c]))
    maximum = math.floor(parent["final"]["cube"]["max"])-1
    if trace["anchor"] != anchor or trace["channel"] != channel or trace["rgb_target"] != maximum or plan["anchor"] != anchor:
        raise ValueError("自动热点/主通道/目标没有来自已测终态")
    primary = type(model)(folder / "primary/model.slut")
    cell = load("cell.json")
    cell_nodes = {n for p in cell["points"] for n,w in zip(*model.weights(p)) if w}
    moves = changed(primary)
    if not moves or any(n not in cell_nodes or any(a != b for c,(a,b) in enumerate(zip(before,after)) if c != channel)
            or not 1 <= abs(after[channel]-before[channel]) <= plan["primary_delta"] for n,before,after in moves):
        raise ValueError("自动主改越过冻结单元/通道/整数幅度")
    expected_moves = [{"node":n,"before":before,"after":after} for n,before,after in moves]
    if trace["primary_moves"] != expected_moves:raise ValueError("主改轨迹与实际模型不同")
    if max(sum((a-b)**2 for a,b in zip(primary.apply(p),t)) for p,t in zip(cell["points"],cell["targets"])) > maximum**2:
        raise ValueError("自动主改没有达到完整单元RGB目标")
    helper_nodes = trace["helper_nodes"]
    expected_allowed = sorted(cell_nodes|{n for n,_,_ in moves}|set(helper_nodes))
    if trace["allowed_nodes"] != expected_allowed:raise ValueError("自动完整支撑节点集合不同")
    h = hashlib.sha256(model.m.to_bytes(4,"little"))
    h.update(model.data[model.node_offset:])
    h.update(model.data[16+12*model.m:model.node_offset])
    if h.hexdigest() != trace["state_signature"]:raise ValueError("条件排序没有绑定原模型/轴表")
    if records["primary"]["solver"]["proposal"] != trace["primary_solver"]:raise ValueError("主改求解回执不同")
    # 直接解析轴表与节点字节构造整数和；各候选只更新其辅助节点的非零支撑。
    weights = [model.weights(p) for p in points]
    keys = [(p[0]*256+p[1])*256+p[2] for p in points]
    targets = [source[3*k:3*k+3] for k in keys]
    baseline = [model.apply(p) for p in points]
    old = [sum((a-b)**2 for a,b in zip(rgb,t)) for rgb,t in zip(baseline,targets)]
    photo_counts = [[(g,frequencies[g,k]) for g in range(101) if (g,k) in frequencies] for k in keys]
    active = sorted({g for counts in photo_counts for g,n in counts})
    support = {n:[] for n in helper_nodes}
    for i,(nodes,values) in enumerate(weights):
        for n,w in zip(nodes,values):
            if w and n in support:support[n].append((i,w))
    full = domain["final"]["histogram"]
    full_sse = sum(d*n for d,n in full)
    old_tail = tail(full)
    scored = 0
    def ranking(prefix):
        nonlocal scored
        prefix_moves = changed(prefix)
        excluded = {n for n,_,_ in prefix_moves}
        l1 = sum(abs(a-b) for _,before,after in prefix_moves for a,b in zip(before,after))
        sums = [[sum(w*prefix.data[model.node_offset+3*n+c] for n,w in zip(nodes,values)) for c in range(3)] for nodes,values in weights]
        rgb = [[(v+32768)//65536 for v in row] for row in sums]
        squared = [sum((a-b)**2 for a,b in zip(row,t)) for row,t in zip(rgb,targets)]
        full_delta,group_delta = Counter(),{g:Counter() for g in active}
        for i,(a,b) in enumerate(zip(old,squared)):
            if a == b:continue
            full_delta[a] -= 1
            full_delta[b] += 1
            for g,n in photo_counts[i]:group_delta[g][a] -= n;group_delta[g][b] += n
        prefix_full = patched(full,full_delta)
        prefix_groups = {g:patched(photos["groups"][g]["histogram"],group_delta[g]) for g in active}
        proposals = []
        for node in helper_nodes:
            if node in excluded:continue
            for c in range(3):
                for delta in plan["helper_deltas"]:
                    if not 0 <= model.data[model.node_offset+3*node+c]+delta <= 255:continue
                    fd,gd = Counter(),{g:Counter() for g in active}
                    for i,w in support[node]:
                        value = (sums[i][c]+delta*w+32768)//65536
                        a = squared[i]
                        b = a-(rgb[i][c]-targets[i][c])**2+(value-targets[i][c])**2
                        if a == b:continue
                        fd[a] -= 1;fd[b] += 1
                        for g,n in photo_counts[i]:gd[g][a] -= n;gd[g][b] += n
                    bins = patched(prefix_full,fd)
                    failed,group_deltas,loss = [],[],photos["loss"]
                    def fixed(before,after,label):
                        s = SUMMARY(before)
                        if sum(d*n for d,n in after) > s["sse"]:failed.append(label+".rms")
                        if MEAN(before,after) > 0:failed.append(label+".mean")
                        for j,(t,b) in enumerate(s["constraints"]):
                            if sum(n for d,n in after if d > t) > b:failed.append(label+f".tail{j}")
                    for g in active:
                        base = photos["groups"][g]
                        current = patched(prefix_groups[g],gd[g])
                        fixed(base["histogram"],current,f"group{g}")
                        loss += cost(current,base["constraints"])-sum(base["costs"])
                        difference = sum(d*n for d,n in current)-sum(d*n for d,n in base["histogram"])
                        if difference:group_deltas.append({"group":g,"sse_delta":str(difference)})
                    fixed(full,bins,"full")
                    low,high,selected = tail(bins)
                    if high > old_tail[0] and selected != old_tail[2]:failed.append("full.cvar")
                    if loss > photos["loss"]:failed.append("primary_loss")
                    score = {"fixed_failed":failed,"primary_loss":loss,"max_squared":bins[-1][0],"full_sse_delta":str(sum(d*n for d,n in bins)-full_sse),
                        "group_sse_deltas":group_deltas,"nonimproving_max":bins[-1][0] >= full[-1][0]}
                    helper = {"node":node,"channel":c,"delta":delta}
                    key = [int(score["nonimproving_max"]),len(failed),bins[-1][0],loss,l1+abs(delta),node,c,delta]
                    proposals.append({"helper":helper,"rank_key":key,"score":score})
        scored += len(proposals)
        return sorted(proposals,key=lambda p:tuple(p["rank_key"]))
    def compare(expected,reported):
        if len(expected) != len(reported):raise ValueError("合法辅助候选清单遗漏或多出")
        for a,b in zip(expected,reported):
            if a["helper"] != b["helper"] or a["rank_key"] != b["rank_key"] or any(b["score"].get(k) != v for k,v in a["score"].items()):
                raise ValueError("独立条件整数评分、顺序或合法候选不同")
    def feasible(name):
        a = records[name]["assessment"]
        return a["accepted"] and a["cube_metrics"]["max"] < parent["final"]["cube"]["max"]
    if trace["early_primary_feasible"] != feasible("primary"):raise ValueError("主改提前结束条件不同")
    expected_names = {"baseline","primary"}
    pairs,triples = [],[]
    if not feasible("primary"):
        first = ranking(primary)
        compare(first,trace["first"])
        for i,proposal in enumerate(first[:plan["pair_limit"]],1):
            name = f"pair_{i:03d}"
            expected_names.add(name);pairs.append(name)
            expected = candidate(primary,proposal["helper"])
            if expected.data != type(model)(folder / name / "model.slut").data or records[name]["solver"]["proposal"] != trace["first"][i-1]:
                raise ValueError("双节点模型未按完整条件排序取前缀")
        if not any(feasible(name) for name in pairs):
            if len(trace["second"]) != len(pairs):raise ValueError("第二辅助层前缀遗漏")
            seen = set()
            for name,entry in zip(pairs,trace["second"]):
                prefix = type(model)(folder / name / "model.slut")
                expected = ranking(prefix)
                compare(expected,entry["proposals"])
                if entry["prefix"] != name:raise ValueError("第二辅助前缀顺序不同")
                local = []
                for j,proposal in enumerate(expected[:plan["second_limit"]]):
                    outcome = candidate(prefix,proposal["helper"])
                    key = tuple((n,tuple(after)) for n,_,after in changed(outcome))
                    if key in seen:continue
                    seen.add(key)
                    label = f"triple_{len(triples)+1:03d}"
                    expected_names.add(label);triples.append(label);local.append(label)
                    reported = {"prefix":name,**entry["proposals"][j]}
                    if outcome.data != type(model)(folder / label / "model.slut").data or records[label]["solver"]["proposal"] != reported:
                        raise ValueError("第二辅助模型未按实际双节点条件排序生成")
                if entry["records"] != local:raise ValueError("第二辅助去重清单不同")
        elif trace["second"]:raise ValueError("已有可行双节点仍扩展第二层")
    elif trace["first"] or trace["second"]:raise ValueError("可行主改仍扩展辅助")
    if pairs != trace["pair_records"] or triples != trace["triple_records"] or set(records) != expected_names:
        raise ValueError("冻结搜索树与所有最终候选不一致")
    return {"tree_complete":True,"scored_proposals":scored,"helper_nodes":len(helper_nodes),"pair_records":len(pairs),"triple_records":len(triples),
        "primary_cell_feasible":True,"scope":"独立核对有限合法集合及全部真实条件评分；主改验证整数可行性，不独立证明MILP最小L1或全局最优"}
