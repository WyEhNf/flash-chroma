"""标准库独立读取SLUT、证明整数必要界并重放局部完整支撑及已记录照片频数。"""
import argparse
from collections import Counter
import csv
import hashlib
import itertools
import json
import math
from pathlib import Path
import runpy
import struct
import sys

ROOT = Path(__file__).resolve().parents[1]
SIGNED_MEAN_UPPER = runpy.run_path(str(Path(__file__).with_name("verify_stability.py")))["signed_mean_upper"]


def load(path):return json.loads(path.read_text(encoding="utf-8"))
def digest(data):return hashlib.sha256(data).hexdigest()


class Model:
    def __init__(self,path):
        self.data = path.read_bytes()
        if self.data[:4] != b"SLUT" or len(self.data) < 16:raise ValueError("SLUT头部错误")
        version,self.m,reserved = struct.unpack_from("<III",self.data,4)
        self.node_offset = 16+12*self.m+768+3072
        if version != 1 or reserved or not 2 <= self.m <= 256 or len(self.data) != self.node_offset+3*self.m**3:raise ValueError("SLUT格式错误")
        start = 16+12*self.m
        self.idx = [self.data[start+256*a:start+256*(a+1)] for a in range(3)]
        self.frac = [struct.unpack_from("<256I",self.data,start+768+1024*a) for a in range(3)]
        if any(v > self.m-2 for row in self.idx for v in row) or any(v > 65536 for row in self.frac for v in row):raise ValueError("轴表越界")

    def weights(self,p):
        base = self.idx[0][p[0]]*self.m**2+self.idx[1][p[1]]*self.m+self.idx[2][p[2]]
        f = [self.frac[a][p[a]] for a in range(3)]
        largest,smallest = f.index(max(f)),f.index(min(f))
        middle = sum(f)-max(f)-min(f)
        strides = [self.m**2,self.m,1]
        return [base,base+strides[largest],base+sum(strides)-strides[smallest],base+sum(strides)],[65536-max(f),max(f)-middle,middle-min(f),min(f)]

    def apply(self,p):
        nodes,weights = self.weights(p)
        return [(sum(w*self.data[self.node_offset+3*n+c] for n,w in zip(nodes,weights))+32768)//65536 for c in range(3)]


def certificate(model,proof,source):
    coefficients = Counter()
    labels = [0,0,0]
    multipliers = [int(k) for k in proof["multipliers"]]
    if not multipliers or len(multipliers) != len(proof["points"]) or len(multipliers) != len(proof["targets"]):raise ValueError("证书乘子长度错误")
    for point,target,k in zip(proof["points"],proof["targets"],multipliers):
        if any(len(v) != 3 or any(type(x) is not int or not 0 <= x <= 255 for x in v) for v in (point,target)):
            raise ValueError("整数证书的输入/参考不是RGB8")
        offset = ((point[0]*256+point[1])*256+point[2])*3
        if list(source[offset:offset+3]) != target:raise ValueError("证书标签不是同字节完整参考")
        ids,weights = model.weights(point)
        for n,w in zip(ids,weights):coefficients[n] += k*w
        for c in range(3):labels[c] += k*target[c]
    nonzero = sorted((n,c) for n,c in coefficients.items() if c)
    norm = sum(abs(k) for k in multipliers)
    if not norm:raise ValueError("证书乘子全零")
    minimum = sum(255*c for n,c in nonzero if c < 0)
    maximum = sum(255*c for n,c in nonzero if c > 0)
    bounds = []
    for target in labels:
        gap = max(65536*target-maximum,minimum-65536*target)-32768*norm
        bounds.append(max(0,(gap+65536*norm-1)//(65536*norm)))
    expected = {"node_coefficients":[[n,str(c)] for n,c in nonzero],"coefficient_l1":str(norm),"target_q16":[str(65536*t) for t in labels],
        "node_range_q16":[str(minimum),str(maximum)],"rounding_allowance_q16":str(32768*norm),"channel_lower_bounds":bounds,"rgb_l2_max_lower_bound":max(bounds)}
    if any(proof[k] != v for k,v in expected.items()):raise ValueError("必要界与独立整数复算不同")
    return max(bounds)


def fixed(old,new,prefix,summarize):
    a,b = summarize(old),summarize(new)
    failed = []
    if b["sse"] > a["sse"]:failed.append(prefix+".rms")
    if b["upper"] > a["lower"] and SIGNED_MEAN_UPPER(old,new) > 0:failed.append(prefix+".mean_bound")
    for j,(threshold,budget) in enumerate(a["constraints"]):
        if sum(n for d,n in new if d > threshold) > budget:failed.append(prefix+f".tail{j}")
    return failed


def metrics(pairs):
    n = sum(count for d,count in pairs)
    rank = .99*(n-1)
    def at(position):
        count = 0
        for d,c in pairs:
            count += c
            if count > position:return math.sqrt(d)
    lo,hi = at(math.floor(rank)),at(math.ceil(rank))
    remaining,total = (n+99)//100,0.
    for d,count in reversed(pairs):
        take = min(remaining,count)
        total += take*math.sqrt(d)
        remaining -= take
        if not remaining:break
    return {"mean":math.fsum(count*math.sqrt(d) for d,count in pairs)/n,"rms":math.sqrt(sum(d*count for d,count in pairs)/n),
        "p99":lo+(rank-math.floor(rank))*(hi-lo),"max":math.sqrt(pairs[-1][0]),"cvar_1pct":total/((n+99)//100)}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input",type=Path,required=True)
    parser.add_argument("--output",type=Path,required=True)
    args = parser.parse_args()
    if args.output.exists():raise ValueError("不覆盖局部极值独立复核")
    folder = args.input
    result,plan,run = [load(folder / n) for n in ("results.json","plan.json","run.json")]
    cid = plan["case"]
    parent = folder / "reference"
    parent_case = next(c for c in load(parent / "results.json")["cases"] if c["case"]["id"] == cid)
    model = Model(parent / cid / "repaired.slut")
    if digest(model.data) != plan["model_sha256"]:raise ValueError("独立复核起点不同")
    source_path = ROOT / parent_case["sources"][0]["path"]
    source = source_path.read_bytes()
    if len(source) != 3*256**3 or digest(source) != parent_case["sources"][0]["table_sha256"]:raise ValueError("独立复核完整源不同")
    bound = certificate(model,load(folder / "certificate.json"),source)
    if load(folder / "certificate.json") != result["certificate"]:raise ValueError("结果与整数证书不同")
    cell = load(folder / "cell.json")
    expected_axes = [[v for v in range(256) if model.idx[a][v] == model.idx[a][plan["anchor"][a]]] for a in range(3)]
    points = list(itertools.product(*expected_axes))
    if cell["axes"] != expected_axes or cell["points"] != list(map(list,points)):raise ValueError("没有完整覆盖声明的单元")
    truth = [list(source[((p[0]*256+p[1])*256+p[2])*3:((p[0]*256+p[1])*256+p[2])*3+3]) for p in points]
    if cell["targets"] != truth or cell["baseline"] != [model.apply(p) for p in points]:raise ValueError("单元参考或基线oracle不同")
    nodes = sorted({n for p in points for n,w in zip(*model.weights(p)) if w})
    config = plan.get("local_compensation")
    if plan.get("joint_interval"):
        evidence = load(folder / "node-evidence.json")
        primary_nodes = [m["node"] for m in evidence["primary_moves"]]
        neighbors = set()
        for n in primary_nodes:
            xyz = (n//model.m**2,n//model.m%model.m,n%model.m)
            neighbors.update((p[0]*model.m+p[1])*model.m+p[2] for p in itertools.product(*(range(max(0,c-1),min(model.m,c+2)) for c in xyz)))
        nodes = sorted(set(nodes)|neighbors)
    if plan.get("automatic_compensation"):
        automatic = load(folder / "automatic.json")
        primary = Model(folder / "primary/model.slut")
        primary_nodes = [n for n in range(model.m**3) if primary.data[model.node_offset+3*n:model.node_offset+3*n+3] != model.data[model.node_offset+3*n:model.node_offset+3*n+3]]
        helpers = set()
        for n in primary_nodes:
            xyz = (n//model.m**2,n//model.m%model.m,n%model.m)
            helpers.update((p[0]*model.m+p[1])*model.m+p[2] for p in itertools.product(*(range(max(0,c-1),min(model.m,c+2)) for c in xyz)))
        helpers -= set(primary_nodes)
        if sorted(helpers) != automatic["helper_nodes"] or len(helpers) > plan["max_neighbor_nodes"]:raise ValueError("自动邻域不同或超过冻结上限")
        nodes = sorted(set(nodes)|set(primary_nodes)|helpers)
    expected_variants = {}
    if config:
        primary,helper = config["primary"],config["helper"]
        nodes = sorted(set(nodes)|{primary["node"],helper["node"]})
        primary_bytes = bytearray(model.data)
        offset = model.node_offset+primary["node"]*3
        if list(model.data[offset:offset+3]) != primary["before"]:raise ValueError("主改前值与原模型不同")
        primary_bytes[offset:offset+3] = bytes(primary["after"])
        expected_variants = {"baseline":model.data,"primary":bytes(primary_bytes)}
        offset = model.node_offset+helper["node"]*3
        if list(model.data[offset:offset+3]) != helper["before"]:raise ValueError("辅助前值与原模型不同")
        for i,delta in enumerate(helper["deltas"],1):
            for name,data in ((f"helper_{i}",model.data),(f"joint_{i}",primary_bytes)):
                copied = bytearray(data)
                copied[offset+helper["channel"]] += delta
                expected_variants[name] = bytes(copied)
        if set(expected_variants) != {r["name"] for r in result["records"] if r["generated"]}:raise ValueError("补偿反事实清单遗漏或多出候选")
    support = load(folder / "support.json")
    if support["nodes"] != nodes:raise ValueError("单元节点集合不同")
    potential = set()
    for node in nodes:
        coordinates = (node//model.m**2,node//model.m%model.m,node%model.m)
        axes = [[v for v in range(256) if model.idx[a][v] in (c-1,c)] for a,c in enumerate(coordinates)]
        potential.update(itertools.product(*axes))
    relevant = sorted(p for p in potential if any(w and n in nodes for n,w in zip(*model.weights(p))))
    if list(map(list,relevant)) != support["points"]:raise ValueError("联合节点的完整非零支撑有遗漏或额外输入")
    old_rgb = [model.apply(p) for p in relevant]
    if digest(bytes(v for rgb in old_rgb for v in rgb)) != support["baseline_sha256"]:raise ValueError("独立支撑基线流不同")
    labels = [source[((p[0]*256+p[1])*256+p[2])*3:((p[0]*256+p[1])*256+p[2])*3+3] for p in relevant]
    keys = [(p[0]*256+p[1])*256+p[2] for p in relevant]
    location = {k:i for i,k in enumerate(keys)}
    frequencies = {}
    with (folder / "frequencies.csv").open(encoding="utf-8",newline="") as f:
        for row in csv.DictReader(f):
            g,k,n = [int(row[v]) for v in ("group","key","count")]
            if not 0 <= g <= 100 or k not in location or n <= 0 or (g,k) in frequencies:raise ValueError("局部照片频数错误")
            frequencies[g,k] = n
    h = hashlib.sha256()
    for g in range(101):
        for k in keys:h.update(frequencies.get((g,k),0).to_bytes(8,"little",signed=True))
    if h.hexdigest() != support["frequency_sha256"]:raise ValueError("频数矩阵字节不同")
    summarize = runpy.run_path(str(Path(__file__).with_name("verify_quantile_constraints.py")))["summary"]
    verify_full = runpy.run_path(str(Path(__file__).with_name("verify_full_domain_guard.py")))["verify"]
    cvar_module = runpy.run_path(str(Path(__file__).with_name("verify_cvar_guard.py")))
    photos,domain = [load(parent / cid / n) for n in ("final-groups.json","full-domain.json")]
    cvar_reference = cvar_module["tail_summary"](domain["final"]["histogram"])
    old = [sum((a-b)**2 for a,b in zip(rgb,t)) for rgb,t in zip(old_rgb,labels)]
    def replace(base,new,g=None):
        hist = Counter(dict(base))
        for k,a,b in zip(keys,old,new):
            count = 1 if g is None else frequencies.get((g,k),0)
            hist[a] -= count
            hist[b] += count
        if any(n < 0 for n in hist.values()):raise ValueError("更新频数出现负值")
        return [[d,n] for d,n in sorted(hist.items()) if n]
    verified,predictions,records_by_name = [],{},{}
    for record in result["records"]:
        if not record["generated"]:continue
        name = record["name"]
        candidate = Model(folder / name / "model.slut")
        if candidate.data[:model.node_offset] != model.data[:model.node_offset] or digest(candidate.data) != record["model_sha256"]:
            raise ValueError("候选格式/轴表/模型SHA不同")
        if config and candidate.data != expected_variants[name]:raise ValueError("候选没有应用冻结的主/辅节点幅度")
        changed = [{"node":n,"before":list(model.data[model.node_offset+3*n:model.node_offset+3*n+3]),
            "after":list(candidate.data[candidate.node_offset+3*n:candidate.node_offset+3*n+3])} for n in range(model.m**3)
            if candidate.data[candidate.node_offset+3*n:candidate.node_offset+3*n+3] != model.data[model.node_offset+3*n:model.node_offset+3*n+3]]
        if record["moves"] != changed:raise ValueError("候选节点变更回执与实际模型不同")
        actual = [candidate.apply(p) for p in relevant]
        predictions[name],records_by_name[name] = actual,record
        if digest(bytes(v for rgb in actual for v in rgb)) != record["support_sha256"]:raise ValueError("候选局部流与独立oracle不同")
        new = [sum((a-b)**2 for a,b in zip(rgb,t)) for rgb,t in zip(actual,labels)]
        assessment = record["assessment"]
        bins = replace(domain["final"]["histogram"],new)
        if bins != assessment["full_domain"]["candidate"]["histogram"]:raise ValueError("候选完整域频数与独立局部更新不同")
        for key,value in metrics(bins).items():
            if abs(value-assessment["cube_metrics"][key]) > 1e-10:raise ValueError("候选全域描述性指标与整数频数不同")
        verify_full(domain["reference"],assessment["full_domain"])
        cvar_module["verify_certificate"](cvar_reference,bins,assessment["cvar"])
        failed,stats,loss = [],[],0
        for g,base in enumerate(photos["groups"]):
            hist = replace(base["histogram"],new,g)
            if hist != assessment["groups"][g]["histogram"]:raise ValueError("候选照片完整频数复算不同")
            for key,value in metrics(hist).items():
                if abs(value-assessment["groups"][g]["metrics"][key]) > 1e-10:raise ValueError("候选逐组指标与整数频数不同")
            s = summarize(hist)
            stats.append(s)
            if s["sse"] > int(base["sse_limit"]):failed.append(f"original.group{g}.rms")
            if s["upper"] > int(base["mean_limit_lower_q24"]) and hist not in (base["initial_histogram"],base["original_histogram"]):failed.append(f"original.group{g}.mean")
            failed += fixed(base["histogram"],hist,f"fixed.group{g}",summarize)
            group_loss = 0
            for condition in base["constraints"]:
                threshold,budget = condition["threshold_squared"],condition["allowed_tail_pixels"]
                remaining = max(0,sum(n for d,n in hist if d > threshold)-budget)
                for d,n in hist:
                    if d <= threshold:continue
                    take = min(remaining,n)
                    group_loss += take*(d-threshold)
                    remaining -= take
                    if not remaining:break
            if group_loss != assessment["groups"][g]["loss"]:raise ValueError("逐图历史缺口不同")
            loss += group_loss
        for k,a in enumerate(photos["aggregates"]):
            if sum(stats[g]["sse"] for g in a["groups"]) > int(a["initial_sse"]):failed.append(f"aggregate{k}.rms")
            if sum(stats[g]["upper"] for g in a["groups"])*1000 > int(a["initial_sum_lower_q24"])*1005:failed.append(f"aggregate{k}.mean")
        failed += ["original.full."+k for k in assessment["full_domain"]["failed"]]
        failed += fixed(domain["final"]["histogram"],bins,"fixed.full",summarize)
        failed += assessment["cvar"]["failed"]
        if loss > photos["loss"]:failed.append("primary_loss")
        if loss != assessment["primary_loss"] or failed != assessment["failed"] or bool(not failed) != assessment["accepted"]:
            raise ValueError("候选接受/拒绝或主缺口与独立复算不同")
        for item in record.get("signed_mean_rechecks",[]):
            before = photos["groups"][item["group"]]["histogram"] if item["scope"] == "group" else domain["final"]["histogram"]
            after = assessment["groups"][item["group"]]["histogram"] if item["scope"] == "group" else assessment["full_domain"]["candidate"]["histogram"]
            changes = [[d,dict(after).get(d,0)-dict(before).get(d,0)] for d in sorted(dict(before).keys() | dict(after).keys()) if dict(after).get(d,0) != dict(before).get(d,0)]
            proof = item["proof"]
            if (not proof["accepted"] or proof["changed_counts"] != changes or int(proof["delta_upper_q24"]) != SIGNED_MEAN_UPPER(before,after)
                    or int(proof["delta_lower_q24"]) != -SIGNED_MEAN_UPPER(after,before) or proof["n"] != sum(n for d,n in before) or proof["precision_bits"] != 24):
                raise ValueError("有符号mean差值证书没有匹配独立整数重算")
        squared = [sum((a-b)**2 for a,b in zip(candidate.apply(p),t)) for p,t in zip(points,truth)]
        if math.sqrt(max(squared)) != record["cell_metrics"]["max"]:raise ValueError("单元max与独立oracle不同")
        verified.append({"name":name,"accepted":not failed,"primary_loss":loss,"cell_max":math.sqrt(max(squared)),"full_max":math.sqrt(bins[-1][0]),"failed_count":len(failed)})
    interactions_checked = 0
    if config:
        overlap = sum(any(n == config["primary"]["node"] and w for n,w in zip(*model.weights(p))) and
            any(n == config["helper"]["node"] and w for n,w in zip(*model.weights(p))) for p in relevant)
        def sse(hist):return sum(d*n for d,n in hist)
        for i,delta in enumerate(config["helper"]["deltas"],1):
            names = ("baseline","primary",f"helper_{i}",f"joint_{i}")
            arrays = [predictions[n] for n in names]
            residues = [[j[c]-a[c]-b[c]+base[c] for c in range(3)] for base,a,b,j in zip(*arrays)]
            a,b,j = [records_by_name[n]["assessment"] for n in names[1:]]
            item = result["interactions"][i-1]
            expected = {"helper_delta":delta,"joint":names[-1],"overlapping_nonzero_support_colours":overlap,
                "output_additivity_mismatch_colours":sum(any(x for x in r) for r in residues),"output_additivity_max_component":max(abs(x) for r in residues for x in r),
                "full_sse_interaction":str(int(j["full_sse_delta"])-int(a["full_sse_delta"])-int(b["full_sse_delta"])),
                "photo_sse_interactions":[{"group":g,"delta":str(sse(j["groups"][g]["histogram"])-sse(a["groups"][g]["histogram"])-sse(b["groups"][g]["histogram"])+sse(photos["groups"][g]["histogram"]))} for g in range(101)]}
            if any(item.get(key) != value for key,value in expected.items()):raise ValueError("联合舍入或SSE交互与独立重放不同")
            interactions_checked += 1
    eligible = [v for v in verified if v["name"] != "baseline" and (not config or v["name"].startswith("joint_"))
        and v["accepted"] and v["full_max"] < parent_case["final"]["cube"]["max"]]
    if plan.get("joint_interval"):
        chosen = min(eligible,key=lambda v:(sum(sum(abs(a-b) for a,b in zip(m["before"],m["after"])) for m in records_by_name[v["name"]]["moves"]),v["name"])) if eligible else None
    else:chosen = min(eligible,key=lambda v:(v["full_max"],v["primary_loss"],len(records_by_name[v["name"]]["moves"]),v["name"])) if eligible else None
    if result["selection"]["selected"] != (chosen["name"] if chosen else None):raise ValueError("最终选择没有匹配独立重算的完整保护")
    full_stream_checked = False
    if chosen is None:
        if result["final"] != {**parent_case["final"],"reused":True}:raise ValueError("没有选中却改变了复用终态")
    else:
        final = result["final"]
        selected = records_by_name[chosen["name"]]
        if final["reused"]:raise ValueError("新选中模型不能冒用旧指标")
        for key in ("mean","rms","p99","max","cvar_1pct"):
            if abs(final["cube"][key]-selected["assessment"]["cube_metrics"][key]) > 1e-10:raise ValueError("完整终验指标与独立完整频数不同")
        if final["cube"]["reference_sha256"] != digest(source):raise ValueError("终验完整参考SHA不符")
        native = final["native"]
        if ({n["kernel"] for n in native} != {"tetra_scalar","tetra_avx2"} or len(native) != 2 or
                any(n["sha256"] != final["cube"]["prediction_sha256"] or n["byte_mismatches"] or n["executable_sha256"] != run["identity"]["executable_sha256"] for n in native)):
            raise ValueError("完整原生回执的内核/输出/程序绑定不同")
        native_model = Model(folder / chosen["name"] / "selected-stage1.slut")
        if digest(native_model.data) != selected["model_sha256"]:raise ValueError("原生终验没有消费选中模型")
        stream = folder / chosen["name"] / "cube.rgb"
        if stream.exists():
            with stream.open("rb") as f:
                if stream.stat().st_size != 3*256**3 or hashlib.file_digest(f,"sha256").hexdigest() != final["cube"]["prediction_sha256"]:raise ValueError("终验完整流长度/SHA不同")
            full_stream_checked = True
        actual_photos = {p["image"]:p for p in final["photos"]["per_image"]}
        if len(actual_photos) != 100 or set(actual_photos) != {p["image"] for p in parent_case["final"]["photos"]["per_image"]}:raise ValueError("终验100图清单不同")
        inventory = load(parent / "photo-inventory.json")
        for g,meta in enumerate(inventory["groups"][:80]):
            for key in ("mean","rms","p99","max"):
                if abs(actual_photos[meta["image"]][key]-selected["assessment"]["groups"][g]["metrics"][key]) > 1e-10:
                    raise ValueError("完整照片终验与独立101组频数不同")
    output = {"verified":True,"integer_lower_bound":bound,"cell_colours":len(points),"support_colours":len(relevant),"records":verified,
        "interactions_checked":interactions_checked,"selection_checked":True,"selected":result["selection"]["selected"],"full_stream_checked":full_stream_checked,
        "verifier_sha256":digest(Path(__file__).read_bytes()),"run_identity":result["run_identity"],"input_result_sha256":digest((folder / "results.json").read_bytes()),
        "external_dependencies_loaded":any(n in sys.modules for n in ("numpy","scipy","numba")),"python":sys.version,
        "scope":"标准库独立解析SLUT/权重/舍入，证明固定表示必要界，枚举完整非零支撑重放候选与完整频数，复算101组已记录照片频数和全部保护；未独立解码80张照片或重新拟合，不据此证明其他候选不可行"}
    if plan.get("automatic_compensation"):
        helper = Path(__file__).with_name("verify_automatic_compensation.py")
        output["automatic"] = runpy.run_path(str(helper))["verify_trace"](folder,plan,automatic,model,source,relevant,frequencies,photos,domain,records_by_name)
        output["automatic_verifier_sha256"] = digest(helper.read_bytes())
    if plan.get("joint_interval"):
        helper = Path(__file__).with_name("verify_joint_interval.py")
        output["joint_interval"] = runpy.run_path(str(helper))["verify"](folder,plan,model,source,relevant,frequencies,photos,domain,records_by_name)
        output["joint_verifier_sha256"] = digest(helper.read_bytes())
    args.output.write_text(json.dumps(output,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
    print(json.dumps(output,ensure_ascii=True))


if __name__ == "__main__":main()
