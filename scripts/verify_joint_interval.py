"""纯标准库独立核对节点来源、整数箱覆盖及每个联合剪枝证书。"""
from collections import Counter
import copy
import hashlib
import itertools
import json
import math
from pathlib import Path
import runpy

HERE = Path(__file__).resolve().parent
MEAN = runpy.run_path(str(HERE / "verify_stability.py"))["signed_mean_upper"]
SUMMARY = runpy.run_path(str(HERE / "verify_quantile_constraints.py"))["summary"]
SHARED = runpy.run_path(str(HERE / "verify_automatic_compensation.py"))


def verify(folder,plan,model,source,points,frequencies,photos,domain,records):
    quality = bool(plan.get("joint_minimax"))
    def load(name):return json.loads((folder / name).read_text(encoding="utf-8"))
    def digest(name):return hashlib.sha256((folder / name).read_bytes()).hexdigest()
    search,evidence = load("joint-search.json"),load("node-evidence.json")
    prior,diagnosis = load("prior-results.json"),load("prior-diagnosis.json")
    old_proof = load("prior-verification.json")
    identity = load("run.json")["identity"]
    parents = {k.replace("\\","/"):v for k,v in identity["parent_files"].items()}
    if (digest("prior-results.json") != evidence["prior_result_sha256"] or digest("prior-diagnosis.json") != evidence["diagnosis_sha256"] or
            diagnosis["result_sha256"] != digest("prior-results.json") or diagnosis["verification_sha256"] != digest("prior-verification.json") or
            diagnosis["trace_sha256"] != digest("prior-automatic.json") or not old_proof["verified"] or old_proof["input_result_sha256"] != digest("prior-results.json") or
            parents[plan["diagnosis"]] != digest("prior-diagnosis.json") or parents[plan["evidence_run"]+"/results.json"] != digest("prior-results.json")):
        raise ValueError("联合节点来源未绑定前阶段结果/归因/独立复核")
    old_records = {r["name"]:r for r in prior["records"]}
    if load("prior-automatic.json")["channel"] != plan["channel"] or type(model)(folder / "baseline/model.slut").data != model.data:
        raise ValueError("联合通道或空修改对照不同")
    closest = min((r for r in prior["records"] if r["solver"]["role"] == "triple"),key=lambda r:(len(r["assessment"]["failed"]),r["name"]))
    regressions = [r for item in diagnosis["conflicts"] if item["candidate"] == closest["name"] for r in item["top_regressions"]]
    if evidence["primary_moves"] != old_records["primary"]["moves"] or evidence["closest_moves"] != closest["moves"] or evidence["regressions"] != regressions:
        raise ValueError("联合节点没有从冻结反例完整导出")
    nodes = []
    def add(n):
        if n not in nodes:nodes.append(n)
    for move in evidence["primary_moves"]:add(move["node"])
    for item in regressions:
        for n,w in zip(*model.weights(item["rgb"])):
            if w:add(n)
    for move in evidence["closest_moves"]:add(move["node"])
    channel = plan["channel"]
    domains = [sorted((d for d in range(-plan["max_delta"],plan["max_delta"]+1) if 0 <= model.data[model.node_offset+3*n+channel]+d <= 255),key=lambda d:(abs(d),d)) for n in nodes]
    parent = next(c for c in load("reference/results.json")["cases"] if c["case"]["id"] == plan["case"])
    maximum = math.ceil(parent["final"]["cube"]["max"]) if quality else math.floor(parent["final"]["cube"]["max"])-1
    assignments = math.prod(map(len,domains))
    if (nodes != search["nodes"] or len(nodes) > plan["max_nodes"] or domains != search["domains"] or search["channel"] != channel or
            search["rgb_max"] != maximum or assignments != search["assignments"] or assignments > plan["max_assignments"]):
        raise ValueError("联合整数域/通道/目标或上限不同")
    keys = [(p[0]*256+p[1])*256+p[2] for p in points]
    at = {k:i for i,k in enumerate(keys)}
    targets = [source[3*k:3*k+3] for k in keys]
    old_rgb = [model.apply(p) for p in points]
    old = [sum((a-b)**2 for a,b in zip(rgb,t)) for rgb,t in zip(old_rgb,targets)]
    other = [sum((rgb[c]-t[c])**2 for c in range(3) if c != channel) for rgb,t in zip(old_rgb,targets)]
    sums,matrix = [],[]
    for p in points:
        ids,weights = model.weights(p)
        sums.append(sum(w*model.data[model.node_offset+3*n+channel] for n,w in zip(ids,weights)))
        matrix.append([sum(w for n,w in zip(ids,weights) if n == chosen) for chosen in nodes])
    active = sorted({g for g,k in frequencies})
    rows = {g:[(at[k],n) for (group,k),n in frequencies.items() if group == g] for g in active}
    rows["full"] = list(enumerate([1]*len(points)))
    histograms = {g:photos["groups"][g]["histogram"] for g in active}
    histograms["full"] = domain["final"]["histogram"]
    full_sse = sum(d*n for d,n in histograms["full"])
    outside = Counter(dict(histograms["full"]));outside.subtract(old)
    outside_max = max((d for d,n in outside.items() if n),default=0)
    root_cache = {}
    def roots(d):
        if d not in root_cache:
            r = math.isqrt(d << 48)
            root_cache[d] = (r,r+int(r*r != d << 48))
        return root_cache[d]
    old_mean_upper = {g:sum(n*roots(old[i])[1] for i,n in row) for g,row in rows.items()}
    old_tail = SHARED["tail"](histograms["full"])
    def actual_score(candidate):
        rgb = [candidate.apply(p) for p in points]
        squared = [sum((a-b)**2 for a,b in zip(v,t)) for v,t in zip(rgb,targets)]
        failed,deltas,loss = [],[],photos["loss"]
        current = {}
        def fixed(before,after,label):
            reference = SUMMARY(before)
            if sum(d*n for d,n in after) > reference["sse"]:failed.append(label+".rms")
            if MEAN(before,after) > 0:failed.append(label+".mean")
            for j,(t,b) in enumerate(reference["constraints"]):
                if sum(n for d,n in after if d > t) > b:failed.append(label+f".tail{j}")
        for g,row in rows.items():
            delta = Counter()
            for i,n in row:delta[old[i]] -= n;delta[squared[i]] += n
            current[g] = SHARED["patched"](histograms[g],delta)
            fixed(histograms[g],current[g],"full" if g == "full" else f"group{g}")
            if g == "full":continue
            base = photos["groups"][g]
            loss += SHARED["cost"](current[g],base["constraints"])-sum(base["costs"])
            difference = sum(d*n for d,n in current[g])-sum(d*n for d,n in histograms[g])
            if difference:deltas.append({"group":g,"sse_delta":str(difference)})
        full = current["full"]
        lo,hi,selected = SHARED["tail"](full)
        if hi > old_tail[0] and selected != old_tail[2]:failed.append("full.cvar")
        if loss > photos["loss"]:failed.append("primary_loss")
        return {"fixed_failed":failed,"primary_loss":loss,"max_squared":full[-1][0],"full_sse_delta":str(sum(d*n for d,n in full)-sum(d*n for d,n in histograms["full"])),
            "group_sse_deltas":deltas,"nonimproving_max":full[-1][0] >= histograms["full"][-1][0]}
    seed = [histograms["full"][-1][0],photos["loss"],full_sse,0]
    incumbent = {"name":"baseline","objective":seed,"deltas":[0]*len(nodes)} if quality else None
    if quality:
        if (search["seed_objective"] != seed or search["objective_schema"] != ["max_squared","historical_loss","full_sse","l1"] or
                digest("parent-search.json") != parents[plan["warm_run"]+"/joint-search.json"] or load("parent-search.json")["nodes"] != nodes):
            raise ValueError("质量目标或父联合节点来源不同")
        audit = load("source-audit.json")
        if (not audit["verified"] or audit["byte_mismatches"] or audit["rational_sha256"] != audit["cached_sha256"] or
                audit["table_sha256"] != hashlib.sha256(source).hexdigest() or audit["source_sha256"] != parent["sources"][0]["source"]["sha256"]):
            raise ValueError("独立Hald源审计没有绑定当前参考")
        frozen = sorted(set(points)|set(itertools.product((0,255),repeat=3))|
            {p for rgb in plan["source_probes"] for p in itertools.product(*(range(max(0,v-1),min(256,v+2)) for v in rgb))})
        cached_bytes = bytes(v for p in frozen for v in source[3*((p[0]*256+p[1])*256+p[2]):3*((p[0]*256+p[1])*256+p[2])+3])
        if (audit["points"] != len(frozen) or audit["points_sha256"] != hashlib.sha256(bytes(v for p in frozen for v in p)).hexdigest() or
                audit["cached_sha256"] != hashlib.sha256(cached_bytes).hexdigest() or [w["rgb"] for w in audit["witnesses"]] != plan["source_probes"] or
                audit["verifier_sha256"] != identity["source_sha256"]["scripts/audit_hald_reference.py"]):raise ValueError("源审计范围/流/源码绑定错误")
        for witness in audit["witnesses"]:
            numerator = [0,0,0]
            base = [min(v*(audit["grid_size"]-1)//255,audit["grid_size"]-2) for v in witness["rgb"]]
            fractions = [v*(audit["grid_size"]-1)-255*i for v,i in zip(witness["rgb"],base)]
            if len(witness["corners"]) != 8:raise ValueError("Hald三线性见证没有8角点")
            for bits,corner in zip(itertools.product((0,1),repeat=3),witness["corners"]):
                xyz = corner["node_rgb_index"]
                weight = math.prod(f if bit else 255-f for bit,f in zip(bits,fractions))
                if xyz != [a+b for a,b in zip(base,bits)] or weight != corner["weight_numerator"]:raise ValueError("源见证的有理权重错误")
                linear = xyz[0]+audit["grid_size"]*xyz[1]+audit["grid_size"]**2*xyz[2]
                if corner["pixel_xy"] != [linear%audit["image"]["size"][0],linear//audit["image"]["size"][0]]:raise ValueError("源Hald节点像素顺序错误")
                for c in range(3):numerator[c] += corner["weight_numerator"]*corner["rgb"][c]
            denominator = witness["denominator"]
            if (sum(c["weight_numerator"] for c in witness["corners"]) != 255**3 or denominator != 255**3 or numerator != witness["numerator"] or
                    [(2*v+denominator)//(2*denominator) for v in numerator] != witness["output"]):raise ValueError("Hald有理数见证错误")
            key = (witness["rgb"][0]*256+witness["rgb"][1])*256+witness["rgb"][2]
            if witness["output"] != list(source[3*key:3*key+3]):raise ValueError("源Hald见证与同字节缓存不同")
    seen,order,covered = set(),[],0
    referenced = {"baseline"}
    counts = Counter()
    for terminal in search["terminals"]:
        prefix = tuple(terminal["deltas"])
        if len(prefix) > len(nodes) or any(d not in domain for d,domain in zip(prefix,domains)):raise ValueError("分支前缀越过整数域")
        if any(prefix[:k] in seen for k in range(len(prefix)+1)):raise ValueError("终端分支重复或与祖先重叠")
        seen.add(prefix)
        order.append(tuple(domains[i].index(d) for i,d in enumerate(prefix)))
        count = math.prod(len(d) for d in domains[len(prefix):])
        if terminal["covered_assignments"] != count:raise ValueError("分支覆盖赋值数错误")
        covered += count
        kind = terminal["kind"];counts[kind] += 1
        cost = sum(abs(d) for d in prefix)
        if kind == "objective" and not quality:
            if incumbent is None or cost < incumbent["l1"] or terminal["minimum_l1"] != cost or terminal["incumbent"] != incumbent:
                raise ValueError("目标剪枝没有此前已通过全部保护的更优回执")
            continue
        if kind == "outside_max":
            if outside_max <= maximum**2 or terminal["squared"] != outside_max:raise ValueError("不变域max剪枝错误")
            continue
        lower = []
        for i,row in enumerate(matrix):
            fixed = sums[i]+sum(d*w for d,w in zip(prefix,row))
            lo = (fixed+sum(row[j]*min(domains[j]) for j in range(len(prefix),len(nodes)))+32768)//65536
            hi = (fixed+sum(row[j]*max(domains[j]) for j in range(len(prefix),len(nodes)))+32768)//65536
            distance = max(0,lo-targets[i][channel],targets[i][channel]-hi)
            lower.append(other[i]+distance*distance)
        if kind == "quality" and quality:
            loss = photos["loss"]
            for g in active:
                delta = Counter()
                for i,n in rows[g]:delta[old[i]] -= n;delta[lower[i]] += n
                hist = SHARED["patched"](histograms[g],delta)
                loss += SHARED["cost"](hist,photos["groups"][g]["constraints"])-sum(photos["groups"][g]["costs"])
            bound = [max(outside_max,max(lower)),loss,full_sse+sum(b-a for a,b in zip(old,lower)),cost]
            if (terminal["objective_lower"] != bound or terminal["incumbent"] != incumbent or tuple(bound) < tuple(incumbent["objective"])):
                raise ValueError("质量字典序下界或此前可行解错误")
        elif kind == "rgb_max":
            i = terminal["point"]
            if not 0 <= i < len(points) or lower[i] != terminal["squared_lower"] or lower[i] <= maximum**2:raise ValueError("RGB区间必要界错误")
        elif kind == "rms":
            g = terminal["group"]
            value = sum(n*(lower[i]-old[i]) for i,n in rows[g])
            if value <= 0 or str(value) != terminal["sse_delta_lower"]:raise ValueError("逐组SSE必要界错误")
        elif kind == "mean":
            g = terminal["group"]
            value = sum(n*roots(lower[i])[0] for i,n in rows[g])-old_mean_upper[g]
            if value <= 0 or str(value) != terminal["sum_delta_lower_q24"]:raise ValueError("逐组mean必要界错误")
        elif kind == "tail":
            g,t = terminal["group"],terminal["threshold_squared"]
            conditions = dict(SUMMARY(histograms[g])["constraints"])
            if t not in conditions:raise ValueError("尾部剪枝没有冻结阈值")
            budget = conditions[t]-sum(n for d,n in histograms[g] if d > t)+sum(n for i,n in rows[g] if old[i] > t)
            value = sum(n for i,n in rows[g] if lower[i] > t)
            if budget != terminal["local_budget"] or value != terminal["local_count_lower"] or value <= budget:raise ValueError("尾部计数必要界错误")
        elif kind == "leaf":
            if len(prefix) != len(nodes):raise ValueError("未完整指定节点却声称精确叶子")
            if max(lower) > maximum**2 or outside_max > maximum**2:raise ValueError("叶子没有达到完整域RGB目标")
            candidate = copy.copy(model)
            data = bytearray(model.data)
            for n,d in zip(nodes,prefix):data[model.node_offset+3*n+channel] += d
            candidate.data = bytes(data)
            score = actual_score(candidate)
            if any(terminal["score"].get(k) != v for k,v in score.items()):raise ValueError("精确叶子保护或真实舍入不同")
            name = terminal["record"]
            if score["fixed_failed"]:
                if name is not None or terminal["accepted"]:raise ValueError("固定保护失败的叶子仍提交")
            else:
                if name not in records or name in referenced:raise ValueError("完整保护叶子回执遗漏或重复")
                referenced.add(name)
                if candidate.data != type(model)(folder / name / "model.slut").data or terminal["accepted"] != records[name]["assessment"]["accepted"]:
                    raise ValueError("叶子未消费同字节模型或接受状态不同")
                if terminal["accepted"]:
                    if quality:
                        actual = [score["max_squared"],score["primary_loss"],full_sse+int(score["full_sse_delta"]),cost]
                        if terminal["objective"] != actual or tuple(actual) >= tuple(incumbent["objective"]):raise ValueError("精确质量叶子并未严格改善目标")
                        incumbent = {"name":name,"objective":actual,"deltas":list(prefix)}
                    else:incumbent = {"name":name,"l1":cost,"deltas":list(prefix)}
        else:raise ValueError("未知联合证书类型")
    if order != sorted(order) or covered != assignments or referenced != set(records) or search["incumbent"] != incumbent:
        raise ValueError("完整整数箱覆盖、确定性遍历或最终最小修改回执不同")
    if quality:
        if search["objective_optimal_within_box"] is not True:raise ValueError("质量目标覆盖声明不匹配")
        return {"verified":True,"nodes":nodes,"assignments":assignments,"covered_assignments":covered,"terminals":len(seen),"prune_counts":dict(counts),
            "objective_optimal_within_box":True,"objective":incumbent["objective"],"improved":incumbent["name"] != "baseline","source_witnesses":len(audit["witnesses"]),
            "scope":"独立整数区间/逐组必要界/缺口单调下界及精确叶子，证明冻结箱内质量目标；只复算源审计有理见证，不在隔离环境解码TIFF"}
    if search["minimum_l1_proven_within_box"] != (incumbent is not None):raise ValueError("最小L1声明不匹配")
    return {"verified":True,"nodes":nodes,"assignments":assignments,"covered_assignments":covered,"terminals":len(seen),"prune_counts":dict(counts),
        "minimum_l1":incumbent["l1"] if incumbent else None,"no_feasible_within_box":incumbent is None,
        "scope":"独立整数区间/逐组必要界及精确叶子，验证互斥终端覆盖整个冻结箱和最小L1；不证明箱外/网格外全局最优"}
