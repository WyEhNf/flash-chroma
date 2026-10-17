"""只拆解冻结补偿步骤的局部整数反事实，不重新搜索或选择模型。"""
import argparse
import hashlib
import itertools
import json
import math
from pathlib import Path
import sys
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT / "python"))
import numpy as np
from lutlab import error_analysis as ea, full_domain_guard as fg, interp, io, tail_repair as tr
from run_tail_repair import read_image
from report_tail_grid_study import digest,write_json


def affected(model,nodes):
    idx,_ = model.tables()
    points = []
    for node in nodes:
        coordinates = np.unravel_index(node,(model.m,)*3)
        axes = [np.flatnonzero((idx[a] == c-1)|(idx[a] == c)) for a,c in enumerate(coordinates)]
        points.append(np.array(list(itertools.product(*axes)),np.uint8))
    points = tr.decode(np.unique(tr.encode(np.concatenate(points))))
    indices,weights = interp.tetra_index_weights_q(points,*model.tables(),model.m)
    return points[np.any(np.isin(indices,nodes)&(weights > 0),axis=1)]


def cost(hist,conditions):
    total = 0
    for condition in conditions:
        threshold,budget = condition["threshold_squared"],condition["allowed_tail_pixels"]
        remaining = max(0,int(hist[threshold+1:].sum())-budget)
        for d in np.flatnonzero(hist[threshold+1:])+threshold+1:
            take = min(remaining,int(hist[d]))
            total += take*(int(d)-threshold)
            remaining -= take
            if not remaining:break
    return total


def describe(hist,base):
    low = high = 0
    for d in np.flatnonzero(hist):
        root = math.isqrt(int(d) << 48)
        low += int(hist[d])*root
        high += int(hist[d])*(root+int(root*root != int(d) << 48))
    sse = int(hist @ np.arange(len(hist),dtype=np.int64))
    equal = [[int(d),int(hist[d])] for d in np.flatnonzero(hist)] in (base["original_histogram"],base["initial_histogram"])
    failed = []
    if high > int(base["mean_limit_lower_q24"]) and not equal:failed.append("mean")
    if sse > int(base["sse_limit"]):failed.append("rms")
    return {"metrics":ea.hist_metrics(hist),"loss":cost(hist,base["constraints"]),"mean_lower_q24":str(low),
        "mean_upper_q24":str(high),"sse":str(sse),"failed":failed}


def process(case,first,second,inventory,rows,partition):
    cid = case["case"]["id"]
    record = next(r for r in case["selection"]["search"]["accepted"] if r.get("compensation"))
    warm = json.loads((first / cid / "final-groups.json").read_text(encoding="utf-8"))
    model_path = second / cid / "warm-replayed.slut"
    model = io.load_sparse(model_path)
    changes = {m["node"]:m for m in record["moves"]}
    roles = record["compensation"]
    points = affected(model,list(changes))
    keys = tr.encode(points)
    source = Path(case["sources"][0]["path"])
    if digest(source) != case["sources"][0]["table_sha256"]:raise ValueError("完整参考表不同")
    truth = io.load_full(source,mmap=True).reshape(-1,3)[keys]
    before = interp.apply_tetra_q16(model,points)
    warm_stream = first / cid / "repaired.rgb"
    if not warm_stream.exists():warm_stream = ROOT / "artifacts/fractional-fit-v1" / cid / "fractional_mixed/cube.rgb"
    if digest(warm_stream) != json.loads((second / cid / "warm-start.json").read_text(encoding="utf-8"))["full_prediction_sha256"]:
        raise ValueError("补偿前全流不同")
    if not np.array_equal(before,np.memmap(warm_stream,np.uint8,mode="r",shape=(256**3,3))[keys]):
        raise AssertionError("局部独立整数输出与补偿前流不符")
    frequency = np.zeros((101,len(keys)),np.int64)
    sample_keys = []
    for g,meta in enumerate(inventory["groups"][:80]):
        rgb = read_image(rows[meta["image"]])
        encoded = tr.encode(rgb)
        position = np.searchsorted(keys,encoded)
        found = position < len(keys)
        found[found] &= keys[position[found]] == encoded[found]
        frequency[g] = np.bincount(position[found],minlength=len(keys))
        if g >= 60:
            seed = int.from_bytes(hashlib.sha256(("2026101701:"+meta["image"]).encode()).digest()[:8],"little")
            selected = np.random.default_rng(seed).choice(len(rgb),4096,replace=False)
            expected = partition["guard"]["images"][g-60]
            if hashlib.sha256(selected.astype("<u4").tobytes()).hexdigest() != expected["pixel_indices_sha256"]:
                raise ValueError("局部归因样本索引不同")
            sample_keys.append(encoded[selected])
    for k,encoded in enumerate(sample_keys):
        position = np.searchsorted(keys,encoded)
        found = position < len(keys)
        found[found] &= keys[position[found]] == encoded[found]
        frequency[80+k] = np.bincount(position[found],minlength=len(keys))
    frequency[100] = frequency[80:100].sum(axis=0)
    old_squared = np.sum((before.astype(np.int32)-truth)**2,axis=1)
    full = json.loads((first / cid / "full-domain.json").read_text(encoding="utf-8"))
    variants = {}
    for label,nodes in (("primary",[roles["primary_node"]]),("helper",[roles["helper_node"]]),("pair",list(changes))):
        proposal = tr.clone([model])[0]
        for node in nodes:
            if proposal.nodes.reshape(-1,3)[node].tolist() != changes[node]["before"]:raise AssertionError("补偿前节点值不同")
            proposal.nodes.reshape(-1,3)[node] = changes[node]["after"]
        prediction = interp.apply_tetra_q16(proposal,points)
        squared = np.sum((prediction.astype(np.int32)-truth)**2,axis=1)
        groups,failed = [],[]
        for g,base in enumerate(warm["groups"]):
            hist = np.zeros(3*255**2+1,np.int64)
            for d,n in base["histogram"]:hist[d] = n
            np.add.at(hist,old_squared,-frequency[g])
            np.add.at(hist,squared,frequency[g])
            if np.any(hist < 0):raise AssertionError("局部频数替换不守恒")
            value = describe(hist,base)
            value.update(group=g,image=inventory["groups"][g]["image"],sse_delta=str(int(value["sse"])-int(base["sse"])))
            failed += [f"group{g}.{key}" for key in value["failed"]]
            groups.append(value)
        for k,aggregate in enumerate(warm["aggregates"]):
            ids = aggregate["groups"]
            if sum(int(groups[g]["mean_upper_q24"]) for g in ids)*1000 > int(aggregate["initial_sum_lower_q24"])*1005:
                failed.append(f"aggregate{k}.mean")
            if sum(int(groups[g]["sse"]) for g in ids) > int(aggregate["initial_sse"]):failed.append(f"aggregate{k}.rms")
        hist = np.zeros(3*255**2+1,np.int64)
        for d,n in full["final"]["histogram"]:hist[d] = n
        np.add.at(hist,old_squared,-1)
        np.add.at(hist,squared,1)
        proof = fg.certify(full["reference"],fg.summary(hist))
        loss = sum(g["loss"] for g in groups)
        delta = (squared-old_squared)*frequency[:80].sum(axis=0)
        chosen = list(dict.fromkeys([*np.argsort(delta,kind="stable")[:8].tolist(),*np.argsort(-delta,kind="stable")[:8].tolist()]))
        variants[label] = {"loss":loss,"loss_change":loss-warm["loss"],"photo_failed":failed,
            "full_domain":proof,"full_sse_delta":str(sum(map(int,squared-old_squared))),
            "accepted_by_original_rules":loss < warm["loss"] and not failed and proof["accepted"],"groups":groups,
            "colour_examples":[{"input":points[p].tolist(),"reference":truth[p].tolist(),"before":before[p].tolist(),
                "after":prediction[p].tolist(),"old_squared":int(old_squared[p]),"new_squared":int(squared[p]),
                "count_full80":int(frequency[:80,p].sum()),"weighted_sse_delta":str(int(delta[p]))} for p in chosen]}
    if variants["pair"]["loss"] != record["after_loss"] or not variants["pair"]["accepted_by_original_rules"]:
        raise AssertionError("局部反事实没有复现冻结的联合接受")
    return {"case":cid,"step":record["step"],"before_loss":warm["loss"],"moves":record["moves"],"roles":roles,
        "affected_colour_count":len(keys),"affected_keys_sha256":hashlib.sha256(keys.astype("<u4").tobytes()).hexdigest(),
        "source_table_sha256":digest(source),"warm_model_sha256":digest(model_path),"warm_prediction_sha256":digest(warm_stream),
        "full_sse_interaction":str(int(variants["pair"]["full_sse_delta"])-int(variants["primary"]["full_sse_delta"])-int(variants["helper"]["full_sse_delta"])),
        "variants":variants}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--v1",type=Path,required=True)
    parser.add_argument("--v2",type=Path,required=True)
    parser.add_argument("--output",type=Path,required=True)
    args = parser.parse_args()
    if args.output.exists():raise ValueError("不覆盖旧诊断")
    result = json.loads((args.v2 / "results.json").read_text(encoding="utf-8"))
    inventory = json.loads((args.v2 / "photo-inventory.json").read_text(encoding="utf-8"))
    partition = json.loads((args.v2 / "photo-partition.json").read_text(encoding="utf-8"))
    rows = {r["id"]:r for r in json.loads((ROOT / "assets/photos/manifest.json").read_text(encoding="utf-8"))["images"]}
    records = [process(c,args.v1,args.v2,inventory,rows,partition) for c in result["cases"]]
    write_json(args.output,{"cases":records,"source_sha256":digest(__file__),"python":sys.version,"numpy":np.__version__,
        "run_inputs":{str(p):digest(p) for p in (args.v1 / "results.json",args.v2 / "results.json",args.v2 / "photo-inventory.json")},
        "scope":"完整80图及既定选择样本的局部节点反事实；无审计图反馈，无优化/重新拟合/性能计时；整数输出对冻结流核对"})
    for c in records:print(c["case"],{k:{"loss":v["loss"],"photo_failed":v["photo_failed"],"full_failed":v["full_domain"]["failed"],"accepted":v["accepted_by_original_rules"]} for k,v in c["variants"].items()})


if __name__ == "__main__":main()
