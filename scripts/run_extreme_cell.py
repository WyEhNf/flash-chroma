"""在一个冻结最坏单元产生两种联合候选，完整重放其有限支撑与原有保护。"""
import argparse
import csv
import hashlib
import itertools
import json
from pathlib import Path
import shutil
import subprocess
import sys
import zipfile
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT / "python"))
import numba
import numpy as np
import psutil
from lutlab import cvar_guard as cg,error_analysis as ea,full_domain_guard as fg,histogram_delta as hd,interp,io,local_minimax as lm,study_provenance,tail_repair as tr
from diagnose_quantile_compensation import affected
from diagnose_quantile_bounds import frequency,trimmed
from diagnose_three_node import replace_hist
from verify_quantile_constraints import summary


def load(path):return json.loads(path.read_text(encoding="utf-8"))
def digest(path):return hashlib.sha256(path.read_bytes()).hexdigest()
def write(path,value):path.write_text(json.dumps(value,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
def pairs(hist):return [[int(d),int(hist[d])] for d in np.flatnonzero(hist)]


def fixed_checks(old,new,prefix):
    before,after = summary(old),summary(new)
    failed = []
    if after["sse"] > before["sse"]:failed.append(prefix+".rms")
    if after["upper"] > before["lower"] and not hd.mean_difference(old,new)["accepted"]:failed.append(prefix+".mean_bound")
    for j,(t,b) in enumerate(before["constraints"]):
        if sum(n for d,n in new if d > t) > b:failed.append(prefix+f".tail{j}")
    return failed


def assess(old,new,weights,photos,domain,guard):
    failed,groups,stats,loss = [],[],[],0
    for g,base in enumerate(photos["groups"]):
        hist = replace_hist(base["histogram"],old,new,weights[g],True)
        bins = pairs(hist)
        value = summary(bins)
        stats.append(value)
        if value["sse"] > int(base["sse_limit"]):failed.append(f"original.group{g}.rms")
        if value["upper"] > int(base["mean_limit_lower_q24"]) and bins not in (base["initial_histogram"],base["original_histogram"]):
            failed.append(f"original.group{g}.mean")
        failed += fixed_checks(base["histogram"],bins,f"fixed.group{g}")
        cost = sum(trimmed(hist,c)[0] for c in base["constraints"])
        loss += cost
        groups.append({"group":g,"histogram":bins,"loss":cost,"metrics":ea.hist_metrics(hist)})
    for k,a in enumerate(photos["aggregates"]):
        if sum(stats[g]["sse"] for g in a["groups"]) > int(a["initial_sse"]):failed.append(f"aggregate{k}.rms")
        if sum(stats[g]["upper"] for g in a["groups"])*1000 > int(a["initial_sum_lower_q24"])*1005:failed.append(f"aggregate{k}.mean")
    hist = replace_hist(domain["final"]["histogram"],old,new,np.ones(len(old),np.int64),True)
    full = fg.summary(hist)
    proof = fg.certify(domain["reference"],full)
    failed += ["original.full."+k for k in proof["failed"]]
    failed += fixed_checks(domain["final"]["histogram"],full["histogram"],"fixed.full")
    cvar = guard.certify(hist)
    failed += cvar["failed"]
    if loss > photos["loss"]:failed.append("primary_loss")
    return {"accepted":not failed,"failed":failed,"primary_loss":loss,"groups":groups,"full_domain":proof,"cvar":cvar,
        "cube_metrics":ea.hist_metrics(hist),"full_sse_delta":str(int(full["sum_squared_error"])-int(domain["final"]["sum_squared_error"]))}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--plan",type=Path,default=ROOT / "experiments/extreme-cell-v1.json")
    parser.add_argument("--output",type=Path,required=True)
    parser.add_argument("--frequency-cache",type=Path)
    parser.add_argument("--executable",type=Path,default=ROOT / "build-engineering-alignment/jshc.exe")
    args = parser.parse_args()
    if args.frequency_cache is not None:args.frequency_cache = args.frequency_cache.resolve()
    if args.output.exists():raise ValueError("不覆盖局部极值研究")
    plan = load(args.plan)
    parent = ROOT / plan["parent"]
    case = next(c for c in load(parent / "results.json")["cases"] if c["case"]["id"] == plan["case"])
    cid = case["case"]["id"]
    source_model = parent / cid / "repaired.slut"
    if digest(source_model) != plan["model_sha256"] or case["selection"]["model_sha256"] != plan["model_sha256"]:raise ValueError("起点模型不同")
    table_path = ROOT / case["sources"][0]["path"]
    if digest(table_path) != case["sources"][0]["table_sha256"]:raise ValueError("完整参考LUT不同")
    numba.set_num_threads(plan["threads"])
    env = study_provenance.environment_fingerprint()
    old_env = load(parent / "run.json")["identity"]["environment"]
    if any(old_env[k] != v for k,v in env.items()):raise ValueError("数值环境与旧起点不同")
    old_identity = load(parent / "run.json")["identity"]
    if digest(ROOT / "assets/photos/manifest.json") != old_identity["image_manifest"]:raise ValueError("图片清单不同")
    sources = ["scripts/run_extreme_cell.py","scripts/verify_extreme_cell.py","scripts/diagnose_quantile_compensation.py","scripts/diagnose_quantile_bounds.py",
        "scripts/diagnose_three_node.py","scripts/run_tail_repair.py","scripts/verify_quantile_constraints.py","scripts/verify_full_domain_guard.py","scripts/verify_cvar_guard.py","scripts/verify_stability.py"]
    sources += ["python/lutlab/"+n+".py" for n in ("local_minimax","interp","io","cvar_guard","full_domain_guard","histogram_delta","stability","error_analysis","tail_repair","study_provenance")]
    if plan.get("local_compensation"):sources += ["python/lutlab/local_compensation.py","scripts/run_chain_error_study.py","scripts/run_joint_box_study.py","python/lutlab/runtime.py"]
    refs = [parent / n for n in ("results.json","run.json","photo-inventory.json","photo-partition.json")]
    refs += [parent / cid / n for n in ("full-domain.json","final-groups.json","repaired.slut","repaired.rgb")]+[table_path]
    identity = {"environment":env,"plan_sha256":digest(args.plan),"source_sha256":{n:digest(ROOT / n) for n in sources},
        "parent_files":{str(p.relative_to(ROOT)):digest(p) for p in refs},"executable_sha256":digest(args.executable)}
    if plan.get("local_compensation"):
        old_local = ROOT / plan["local_compensation"]["reference"]
        identity["local_reference_files"] = {str(p.relative_to(ROOT)):digest(p) for p in
            (old_local / "run.json",old_local / "results.json",old_local / "certificate.json",old_local / "minimum_change/model.slut",old_local / "verification.json")}
    if args.frequency_cache is not None:
        cached_identity = load(args.frequency_cache / "run.json")["identity"]
        for field in ("environment","plan_sha256","parent_files"):
            if cached_identity[field] != identity[field]:raise ValueError("局部频数缓存的环境/计划/输入不同")
        for name in ("scripts/diagnose_quantile_bounds.py","scripts/run_tail_repair.py","python/lutlab/interp.py","python/lutlab/io.py","python/lutlab/tail_repair.py"):
            if cached_identity["source_sha256"][name] != identity["source_sha256"][name]:raise ValueError("频数构建或支撑语义不同")
        identity["frequency_cache"] = {str((args.frequency_cache / n).relative_to(ROOT)):digest(args.frequency_cache / n) for n in ("run.json","support.json","frequencies.csv")}
    metadata = {"identity":identity,"identity_sha256":study_provenance.identity_digest(identity),
        "git_commit":subprocess.check_output(["git","rev-parse","HEAD"],cwd=ROOT,text=True).strip(),"numba_threads":numba.get_num_threads(),
        "ram_bytes":psutil.virtual_memory().total,"backend":("有限块NumPy整数重放；选中后Numba4线程完整终验，非性能实验" if plan.get("local_compensation") else "SciPy绑定的HiGHS LP/MILP；求解器内部线程未独立测量，非性能实验"),
        "purpose":plan["purpose"]}
    study_provenance.claim_run(args.output / "run.json",metadata)
    shutil.copyfile(args.plan,args.output / "plan.json")
    for path in refs:
        if path.suffix == ".json" or path.name == "repaired.slut":
            destination = args.output / "reference" / path.relative_to(parent) if path.is_relative_to(parent) else None
            if destination is not None:
                destination.parent.mkdir(parents=True,exist_ok=True)
                shutil.copyfile(path,destination)
    with zipfile.ZipFile(args.output / "measured-source.zip","w",zipfile.ZIP_DEFLATED) as z:
        for name in sources:z.write(ROOT / name,name)
    model = io.load_sparse(source_model)
    table = io.load_full(table_path,mmap=True)
    axis = model.tables()[0]
    cell = [int(axis[a,plan["anchor"][a]]) for a in range(3)]
    ranges = [np.flatnonzero(axis[a] == c).tolist() for a,c in enumerate(cell)]
    if int(np.prod([len(r) for r in ranges])) > plan["max_cell_colours"]:raise ValueError("单元颜色数超过冻结上限")
    points = np.array(list(itertools.product(*ranges)),np.uint8)
    target = table[tuple(points.T)]
    baseline = interp.apply_tetra_q16(model,points)
    write(args.output / "cell.json",{"cell":cell,"axes":ranges,"points":points.tolist(),"targets":target.tolist(),"baseline":baseline.tolist()})
    if plan.get("local_compensation"):
        from lutlab import local_compensation as lc
        variants = lc.family(model,plan["local_compensation"])
        certificate = load(old_local / "certificate.json")
        print(f"固定单元{cell}，{len(points)}色；两种冻结辅助幅度及单改/联合反事实",flush=True)
    else:
        print(f"固定单元{cell}，{len(points)}色；开始一次连续minimax及一次整数最小修改",flush=True)
        continuous,continuous_info = lm.relaxed_minimax(model,points,target,dual_scale=plan["dual_scale"])
        integer,integer_info = lm.minimum_change(model,points,target,rgb_max=plan["rgb_max"],max_delta=plan["max_delta"],time_limit=plan["milp_time_limit"])
        certificate = continuous_info["certificate"]
        variants = {"baseline":(model,{}),"minimax_rounded":(continuous,continuous_info),"minimum_change":(integer,integer_info)}
    write(args.output / "certificate.json",certificate)
    for name,(candidate,info) in variants.items():
        checkpoint = args.output / name
        checkpoint.mkdir()
        write(checkpoint / "solver.json",info)
        if candidate is not None:io.save_sparse(checkpoint / "model.slut",candidate)
    all_nodes = lm.design(model,points)[0].tolist()
    if plan.get("local_compensation"):
        all_nodes = sorted(set(all_nodes)|{plan["local_compensation"]["primary"]["node"],plan["local_compensation"]["helper"]["node"]})
    support = affected(model,all_nodes)
    if len(support) > plan["max_support_colours"]:raise ValueError("联合变量完整支撑超过冻结上限")
    keys = tr.encode(support)
    prediction = interp.apply_tetra_q16(model,support)
    if not np.array_equal(prediction,np.memmap(parent / cid / "repaired.rgb",np.uint8,mode="r",shape=(256**3,3))[keys]):
        raise ValueError("局部起点映射与已测全流不同")
    truth = table.reshape(-1,3)[keys]
    old = np.sum((prediction.astype(np.int32)-truth)**2,axis=1)
    inventory,partition = [load(parent / n) for n in ("photo-inventory.json","photo-partition.json")]
    rows = {r["id"]:r for r in load(ROOT / "assets/photos/manifest.json")["images"]}
    print(f"全部{len(all_nodes)}个单元节点的完整支撑{len(support)}色；准备101组局部频数",flush=True)
    if args.frequency_cache is None:
        weights = frequency(keys,inventory,partition,plan,rows)
    else:
        cached = load(args.frequency_cache / "support.json")
        if cached["points"] != support.tolist() or cached["nodes"] != all_nodes:raise ValueError("局部频数缓存的颜色支撑不同")
        weights = np.zeros((101,len(keys)),np.int64)
        positions = {int(k):i for i,k in enumerate(keys)}
        with (args.frequency_cache / "frequencies.csv").open(encoding="utf-8",newline="") as f:
            for row in csv.DictReader(f):
                g,k,n = [int(row[v]) for v in ("group","key","count")]
                if not 0 <= g < 101 or k not in positions or n <= 0 or weights[g,positions[k]]:raise ValueError("缓存频数格式错误")
                weights[g,positions[k]] = n
        if hashlib.sha256(weights.tobytes()).hexdigest() != cached["frequency_sha256"]:raise ValueError("缓存频数字节不同")
    write(args.output / "support.json",{"nodes":all_nodes,"points":support.tolist(),"baseline_sha256":hashlib.sha256(prediction.tobytes()).hexdigest(),
        "frequency_sha256":hashlib.sha256(weights.tobytes()).hexdigest()})
    with (args.output / "frequencies.csv").open("w",encoding="utf-8",newline="") as f:
        writer = csv.writer(f,lineterminator="\n")
        writer.writerow(("group","key","count"))
        for g,k in zip(*np.nonzero(weights)):writer.writerow((int(g),int(keys[k]),int(weights[g,k])))
    photos,domain = [load(parent / cid / n) for n in ("final-groups.json","full-domain.json")]
    hist = np.zeros(3*255**2+1,np.int64)
    for d,n in domain["final"]["histogram"]:hist[d] = n
    guard = cg.CvarGuard(hist,fg.signature([model]))
    write(args.output / "cvar-reference.json",guard.reference_report(digest(source_model)))
    records,outputs = [],{}
    for name,(candidate,info) in variants.items():
        folder = args.output / name
        folder.mkdir(exist_ok=True)
        if candidate is None:
            write(folder / "solver.json",info)
            records.append({"name":name,"generated":False,"solver":info})
            continue
        path = folder / "model.slut"
        io.save_sparse(path,candidate)
        current = interp.apply_tetra_q16(candidate,support)
        outputs[name] = current
        new = np.sum((current.astype(np.int32)-truth)**2,axis=1)
        assessment = assess(old,new,weights,photos,domain,guard)
        changes = np.flatnonzero(np.any(candidate.nodes.reshape(-1,3) != model.nodes.reshape(-1,3),axis=1))
        record = {"name":name,"generated":True,"model_sha256":digest(path),"solver":info,"assessment":assessment,
            "moves":[{"node":int(n),"before":model.nodes.reshape(-1,3)[n].tolist(),"after":candidate.nodes.reshape(-1,3)[n].tolist()} for n in changes],
            "cell_metrics":ea.metrics(interp.apply_tetra_q16(candidate,points),target),"support_sha256":hashlib.sha256(current.tobytes()).hexdigest()}
        rechecks = []
        for g,(base,after) in enumerate(zip(photos["groups"],assessment["groups"])):
            if summary(after["histogram"])["upper"] > summary(base["histogram"])["lower"] and after["histogram"] != base["histogram"]:
                proof = hd.mean_difference(base["histogram"],after["histogram"])
                if proof["accepted"]:rechecks.append({"scope":"group","group":g,"proof":proof})
        if int(assessment["full_domain"]["candidate"]["sum_upper_q24"]) > int(domain["final"]["sum_lower_q24"]) and assessment["full_domain"]["candidate"]["histogram"] != domain["final"]["histogram"]:
            proof = hd.mean_difference(domain["final"]["histogram"],assessment["full_domain"]["candidate"]["histogram"])
            if proof["accepted"]:rechecks.append({"scope":"full","proof":proof})
        record["signed_mean_rechecks"] = rechecks
        if plan.get("local_compensation") and name == "primary":
            old_primary = next(r for r in load(old_local / "results.json")["records"] if r["name"] == "minimum_change")
            if record["model_sha256"] != old_primary["model_sha256"] or assessment != old_primary["assessment"]:
                raise AssertionError("固定主改未逐项复现PR28的模型/频数/拒绝")
        write(folder / "result.json",record)
        records.append(record)
        print(name,"单元max",record["cell_metrics"]["max"],"全域max",assessment["cube_metrics"]["max"],"主缺口",assessment["primary_loss"],"保护失败",len(assessment["failed"]),flush=True)
    if not records[0]["assessment"]["accepted"] or records[0]["assessment"]["primary_loss"] != case["final_loss"]:
        raise AssertionError("空修改基线没有通过全部原保护/固定保护")
    interactions = []
    if plan.get("local_compensation"):
        by_name = {r["name"]:r for r in records}
        for i,delta in enumerate(plan["local_compensation"]["helper"]["deltas"],1):
            a,b,j = [by_name[n]["assessment"] for n in ("primary",f"helper_{i}",f"joint_{i}")]
            info = lc.interaction(*(outputs[n] for n in ("baseline","primary",f"helper_{i}",f"joint_{i}")))
            ids,ws = interp.tetra_index_weights_q(support,*model.tables(),model.m)
            overlapping = np.any((ids == plan["local_compensation"]["primary"]["node"]) & (ws > 0),axis=1) & np.any((ids == plan["local_compensation"]["helper"]["node"]) & (ws > 0),axis=1)
            info.update(helper_delta=delta,joint=f"joint_{i}",full_sse_interaction=str(int(j["full_sse_delta"])-int(a["full_sse_delta"])-int(b["full_sse_delta"])),
                overlapping_nonzero_support_colours=int(np.count_nonzero(overlapping)),
                photo_sse_interactions=[{"group":g,"delta":str(sum(d*n for d,n in j["groups"][g]["histogram"])-sum(d*n for d,n in a["groups"][g]["histogram"])
                    -sum(d*n for d,n in b["groups"][g]["histogram"])+sum(d*n for d,n in photos["groups"][g]["histogram"]))} for g in range(101)])
            interactions.append(info)
        write(args.output / "interactions.json",interactions)
    feasible = [r for r in records[1:] if r["generated"] and (not plan.get("local_compensation") or r["solver"]["role"] == "joint")
        and r["assessment"]["accepted"] and r["assessment"]["cube_metrics"]["max"] < case["final"]["cube"]["max"]]
    selected = min(feasible,key=lambda r:(r["assessment"]["cube_metrics"]["max"],r["assessment"]["primary_loss"],len(r["moves"]),r["name"])) if feasible else None
    selection = {"selected":selected["name"] if selected else None,"before_photos":True,"scope":plan["limits"]}
    write(args.output / "selection-before-photos.json",selection)
    final = {**case["final"],"reused":True}
    if selected is not None:
        from run_chain_error_study import cube_evaluate,photos_evaluate
        from run_joint_box_study import native_verify
        folder = args.output / selected["name"]
        chosen = io.load_sparse(folder / "model.slut")
        cube = cube_evaluate([table],ea.Operator([chosen]),folder / "cube.rgb",128)
        for k in ("mean","rms","p99","max","cvar_1pct"):
            if abs(cube[k]-selected["assessment"]["cube_metrics"][k]) > 1e-10:raise AssertionError("完整终验与局部完整频数不同")
        native = native_verify([chosen],folder,cube["prediction_sha256"],args.executable)
        photo_metrics = photos_evaluate([table],{"selected":ea.Operator([chosen])})["selected"]
        actual = {r["image"]:r for r in photo_metrics["per_image"]}
        for g,meta in enumerate(inventory["groups"][:80]):
            for key in ("mean","rms","p99","max"):
                if abs(actual[meta["image"]][key]-selected["assessment"]["groups"][g]["metrics"][key]) > 1e-12:
                    raise AssertionError("完整照片终验与局部完整频数不一致")
        final = {"cube":cube,"native":native,"photos":photo_metrics,"reused":False}
    write(args.output / "results.json",{"case":case["case"],"parent_identity":load(parent / "run.json")["identity_sha256"],
        "run_identity":metadata["identity_sha256"],"certificate":certificate,"records":records,"interactions":interactions,"selection":selection,"final":final,
        "scope":"冻结有限候选/单元/完整局部支撑；拒绝与单改对照同样保存；未选中时只复用同字节PR27终态，不重复完整终验"})
    print("局部极值阶段结束；选择：",selection["selected"],flush=True)


if __name__ == "__main__":main()
