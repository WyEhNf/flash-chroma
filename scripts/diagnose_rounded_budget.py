"""局部拆解冻结的舍入补偿节点对，不新增候选或重新拟合。"""
import argparse
import hashlib
import json
import math
from pathlib import Path
import sys
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT / "python"))
import numpy as np
from lutlab import full_domain_guard as fg,interp,io,tail_repair as tr
from diagnose_quantile_compensation import affected
from diagnose_quantile_bounds import frequency
from report_tail_grid_study import digest,write_json


def load(path):return json.loads(path.read_text(encoding="utf-8"))


def upper(values):
    result = []
    for value in values:
        n = int(value) << 48
        root = math.isqrt(n)
        result.append(root+int(root*root != n))
    return np.array(result,np.int64)


def process(case,source,warm,inventory,partition,plan,rows,out):
    cid = case["case"]["id"]
    search = case["selection"]["search"]
    records = search["accepted"][search["replayed_steps"]:]
    pair_steps = [r["step"] for r in records if r.get("compensation")]
    if not pair_steps:return {"case":cid,"accepted_pairs":0,"scope":"没有接受节点对，不新增局部选择"}
    prefix = [r for r in records if r["step"] <= max(pair_steps)]
    model_path = source / cid / "warm-replayed.slut"
    model = io.load_sparse(model_path)
    points = affected(model,sorted({m["node"] for r in prefix for m in r["moves"]}))
    keys = tr.encode(points)
    weights = frequency(keys,inventory,partition,plan,rows)
    weights = np.concatenate((weights,np.ones((1,len(points)),np.int64)))
    table = ROOT / case["sources"][0]["path"]
    if digest(table) != case["sources"][0]["table_sha256"]:raise ValueError("原完整参考不同")
    truth = io.load_full(table,mmap=True).reshape(-1,3)[keys]
    prediction = interp.apply_tetra_q16(model,points)
    stream = warm / cid / "repaired.rgb"
    expected = load(source / cid / "warm-start.json")["full_prediction_sha256"]
    if digest(stream) != expected or not np.array_equal(prediction,np.memmap(stream,np.uint8,mode="r",shape=(256**3,3))[keys]):
        raise AssertionError("局部初态与冻结v3流不同")
    groups = load(warm / cid / "final-groups.json")
    full = load(warm / cid / "full-domain.json")
    current_sse = np.array([int(g["sse"]) for g in groups["groups"]]+[int(full["final"]["sum_squared_error"])],np.int64)
    current_high = np.array([int(g["mean_sum_upper_q24"]) for g in groups["groups"]]+[int(full["final"]["sum_upper_q24"])],np.int64)
    limits = [([g],int(record["sse_limit"]),f"group{g}") for g,record in enumerate(groups["groups"])]
    limits += [(a["groups"],int(a["initial_sse"]),f"aggregate{k}") for k,a in enumerate(groups["aggregates"])]
    limits += [([101],int(full["reference"]["sum_squared_error"]),"full")]
    result,compensation_index = [],0
    for record in prefix:
        before_squared = np.sum((prediction.astype(np.int32)-truth)**2,axis=1)
        before_high = upper(before_squared)
        roles = record.get("compensation")
        if roles:
            info = search["compensation_rounds"][compensation_index]
            if fg.signature([model]) != info["model_signature"]:raise AssertionError("统计来源模型不同")
            changes = {m["node"]:m for m in record["moves"]}
            helper = changes[roles["helper_node"]]
            difference = np.array(helper["after"])-helper["before"]
            channels = np.flatnonzero(difference)
            if len(channels) != 1 or abs(difference[channels[0]]) != 1:raise ValueError("辅助修改不是单通道±1")
            channel,sign = int(channels[0]),int(difference[channels[0]])
            indices,qweights = interp.tetra_index_weights_q(points,*model.tables(),model.m)
            own = np.where(indices == roles["helper_node"],qweights,0).sum(axis=1,dtype=np.int64)
            residual = prediction[:,channel].astype(np.int64)-truth[:,channel]
            gradient,diagonal = weights @ (own*residual),weights @ (own*own)
            proxy_numerator = [2*65536*sign*int(g)+int(d) for g,d in zip(gradient,diagonal)]
            deltas = {}
            for name,nodes in (("primary",[roles["primary_node"]]),("helper",[roles["helper_node"]]),("pair",list(changes))):
                candidate = tr.clone([model])[0]
                for node in nodes:candidate.nodes.reshape(-1,3)[node] = changes[node]["after"]
                mapped = interp.apply_tetra_q16(candidate,points)
                squared = np.sum((mapped.astype(np.int32)-truth)**2,axis=1)
                deltas[name] = np.stack((weights @ (squared-before_squared),weights @ (upper(squared)-before_high)),axis=1)
            if roles["disjoint_cell_support_certificate"]:
                np.testing.assert_array_equal(deltas["primary"]+deltas["helper"],deltas["pair"])
            if int(deltas["pair"][-1,0]) != int(roles["predicted_full_sse_delta"]) or int(deltas["pair"][-1,1]) != int(roles["predicted_full_mean_upper_q24_delta"]):
                raise AssertionError("局部实际预算与冻结预测不同")
            rows_out = []
            for ids,limit,name in limits:
                current = int(current_sse[ids].sum())
                a,b,c = [int(deltas[key][ids,0].sum()) for key in ("primary","helper","pair")]
                proxy = sum(proxy_numerator[g] for g in ids)
                rows_out.append({"budget":name,"groups":ids,"before_sse":str(current),"limit_sse":str(limit),
                    "primary_delta":str(a),"helper_delta":str(b),"pair_delta":str(c),"room_after_primary":str(limit-current-a),
                    "room_after_pair":str(limit-current-c),"continuous_helper_numerator":str(proxy),"continuous_helper_denominator":65536**2,
                    "continuous_helper_delta":proxy/(65536**2),"continuous_pair_room_numerator":str((limit-current-a)*(65536**2)-proxy)})
            result.append({"step":record["step"],"before_loss":record["before_loss"],"after_loss":record["after_loss"],
                "moves":record["moves"],"roles":roles,"budgets":rows_out,
                "integer_changes":[{"group":g,"primary_sse_delta":str(deltas["primary"][g,0]),"helper_sse_delta":str(deltas["helper"][g,0]),
                    "pair_sse_delta":str(deltas["pair"][g,0]),"primary_mean_upper_q24_delta":str(deltas["primary"][g,1]),
                    "helper_mean_upper_q24_delta":str(deltas["helper"][g,1]),"pair_mean_upper_q24_delta":str(deltas["pair"][g,1])} for g in range(102)]})
            compensation_index += 1
        for part in record["moves"]:
            node = model.nodes.reshape(-1,3)[part["node"]]
            if node.tolist() != part["before"]:raise AssertionError("局部节点前值不同")
            node[:] = part["after"]
        prediction = interp.apply_tetra_q16(model,points)
        squared = np.sum((prediction.astype(np.int32)-truth)**2,axis=1)
        current_sse += weights @ (squared-before_squared)
        current_high += weights @ (upper(squared)-before_high)
        checkpoint = out / f"{cid}-step{record['step']:03d}.slut"
        io.save_sparse(checkpoint,model)
        if digest(checkpoint) != load(source / cid / f"checkpoint{record['step']:03d}.json")["model_sha256"]:raise AssertionError("局部模型SHA不同")
        proof = record["full_domain"]["candidate"]
        if int(current_sse[-1]) != int(proof["sum_squared_error"]) or int(current_high[-1]) != int(proof["sum_upper_q24"]):
            raise AssertionError("局部全域预算归约与证书不同")
    return {"case":cid,"accepted_pairs":len(result),"replayed_prefix_steps":len(prefix),"union_colours":len(points),
        "keys_sha256":hashlib.sha256(keys.astype("<u4").tobytes()).hexdigest(),"frequency_sha256":hashlib.sha256(memoryview(weights).cast("B")).hexdigest(),
        "pairs":result,"scope":"只局部拆分两个已接受节点对；连续值按原Aq残差代理复算，不代表它在旧候选库中的实际排名"}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input",type=Path,required=True)
    parser.add_argument("--warm",type=Path,required=True)
    parser.add_argument("--output",type=Path,required=True)
    args = parser.parse_args()
    if args.output.exists():raise ValueError("不覆盖旧归因")
    result,run = [load(args.input / n) for n in ("results.json","run.json")]
    plan_path = ROOT / "experiments/rounded-budget-exact-v1.json"
    if digest(plan_path) != run["identity"]["plan_sha256"]:raise ValueError("计划变化")
    for n,h in run["identity"]["warm_files"].items():
        if digest(args.warm / n) != h:raise ValueError("热启动来源变化")
    inventory,partition = [load(args.input / n) for n in ("photo-inventory.json","photo-partition.json")]
    rows = {r["id"]:r for r in load(ROOT / "assets/photos/manifest.json")["images"]}
    args.output.mkdir(parents=True)
    records = [process(c,args.input,args.warm,inventory,partition,load(plan_path),rows,args.output) for c in result["cases"]]
    write_json(args.output / "results.json",{"cases":records,"python":sys.version,"numpy":np.__version__,
        "sources_sha256":{n:digest(ROOT / "scripts" / n) for n in ("diagnose_rounded_budget.py","diagnose_quantile_bounds.py","diagnose_quantile_compensation.py")},
        "inputs_sha256":{str(p):digest(p) for p in (args.input / "results.json",args.warm / "results.json",plan_path)},
        "scope":"独立整数根上界与局部RGB8映射，只用80图及固定选择样本，无新搜索/拟合/审计反馈/性能计时"})
    for case in records:
        print(case["case"],[(p["step"],[(b["budget"],b["primary_delta"],b["helper_delta"],b["continuous_helper_delta"],b["room_after_pair"]) for b in p["budgets"] if b["budget"] in ("aggregate0","full")]) for p in case.get("pairs",[])])


if __name__ == "__main__":main()
