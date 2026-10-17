"""从已验收终态自动求主改并有限搜索条件辅助，选择后只完整验收一个模型。"""
import argparse
import hashlib
import itertools
import json
import math
from pathlib import Path
import shutil
import subprocess
import sys
import zipfile
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT / "python"))
import numba
import numpy as np
from lutlab import automatic_compensation as ac,cvar_guard as cg,error_analysis as ea,interp,io,local_minimax as lm,study_provenance,tail_repair as tr
from diagnose_quantile_compensation import affected
from diagnose_quantile_bounds import frequency
from local_study_snapshot import snapshot
from run_extreme_cell import assess,digest,load,pairs,write
from verify_quantile_constraints import verify_groups


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--plan",type=Path,default=ROOT / "experiments/automatic-compensation-v1.json")
    parser.add_argument("--output",type=Path,required=True)
    parser.add_argument("--executable",type=Path,default=ROOT / "build-engineering-alignment/jshc.exe")
    args = parser.parse_args()
    if args.output.exists():raise ValueError("不覆盖自动补偿实验")
    plan = load(args.plan)
    source = ROOT / plan["warm_run"]
    frame = snapshot(source,plan["case"])
    case,photos,domain = [frame[k] for k in ("case","photos","domain")]
    warm_verification = load(source / "verification.json")
    if not warm_verification["verified"] or warm_verification["input_result_sha256"] != digest(source / "results.json"):
        raise ValueError("父终态的独立复核与结果未绑定")
    if digest(ROOT / "assets/photos/manifest.json") != frame["manifest_sha256"]:raise ValueError("图片清单与已测起点不同")
    if digest(frame["model_path"]) != plan["model_sha256"] or case["selection"]["model_sha256"] != plan["model_sha256"]:
        raise ValueError("当前已测起点模型不同")
    group_check = verify_groups(photos)
    if group_check["loss"] != case["final_loss"] or not group_check["guards_accepted"]:raise ValueError("父终态状态视图未保持历史目标")
    table_path = ROOT / case["sources"][0]["path"]
    if digest(table_path) != case["sources"][0]["table_sha256"] or digest(frame["stream_path"]) != case["final"]["cube"]["prediction_sha256"]:
        raise ValueError("参考或父完整流不同")
    numba.set_num_threads(plan["threads"])
    environment = study_provenance.environment_fingerprint()
    if any(frame["run"]["identity"]["environment"][k] != v for k,v in environment.items()):raise ValueError("研究数值环境与已测起点不同")
    scripts = ["run_automatic_compensation.py","local_study_snapshot.py","run_extreme_cell.py","verify_extreme_cell.py","verify_automatic_compensation.py",
        "verify_stability.py","verify_quantile_constraints.py","verify_full_domain_guard.py","verify_cvar_guard.py","diagnose_quantile_compensation.py",
        "diagnose_quantile_bounds.py","diagnose_three_node.py","run_tail_repair.py","run_chain_error_study.py","run_joint_box_study.py"]
    sources = ["scripts/"+n for n in scripts]+["python/lutlab/"+n+".py" for n in ("automatic_compensation","local_minimax","histogram_delta","interp","io","cvar_guard",
        "full_domain_guard","error_analysis","tail_repair","study_provenance","runtime")]
    paths = [source / "results.json",source / "run.json",source / "verification.json",source / "certificate.json",frame["model_path"],frame["stream_path"],table_path,
        source / "reference/results.json",source / "reference" / plan["case"] / "final-groups.json",source / "reference" / plan["case"] / "full-domain.json",
        source / "reference/photo-inventory.json",source / "reference/photo-partition.json",ROOT / "assets/photos/manifest.json"]
    identity = {"environment":environment,"image_manifest_sha256":frame["manifest_sha256"],"plan_sha256":digest(args.plan),"source_sha256":{p:digest(ROOT / p) for p in sources},
        "parent_files":{str(p.relative_to(ROOT)):digest(p) for p in paths},"executable_sha256":digest(args.executable)}
    metadata = {"identity":identity,"identity_sha256":study_provenance.identity_digest(identity),"git_commit":subprocess.check_output(["git","rev-parse","HEAD"],cwd=ROOT,text=True).strip(),
        "purpose":plan["purpose"],"backend":"局部NumPy整数条件排序；HiGHS主改；选中后Numba4及单线程标量/AVX2终验；不计时比较"}
    study_provenance.claim_run(args.output / "run.json",metadata)
    shutil.copyfile(args.plan,args.output / "plan.json")
    ref = args.output / "reference"
    (ref / plan["case"]).mkdir(parents=True)
    for name,value in (("results.json",{"cases":[case]}),("photo-inventory.json",frame["inventory"]),("photo-partition.json",frame["partition"]),("run.json",frame["run"]),
            (plan["case"]+"/final-groups.json",photos),(plan["case"]+"/full-domain.json",domain)):
        write(ref / name,value)
    shutil.copyfile(frame["model_path"],ref / plan["case"] / "repaired.slut")
    with zipfile.ZipFile(args.output / "measured-source.zip","w",zipfile.ZIP_DEFLATED) as z:
        for name in sources:z.write(ROOT / name,name)
    certificate = load(source / "certificate.json")
    write(args.output / "certificate.json",certificate)
    model = io.load_sparse(frame["model_path"])
    table = io.load_full(table_path,mmap=True)
    anchor = case["final"]["cube"]["hotspots"][0]["rgb"]
    if anchor != plan["anchor"]:raise ValueError("首个最坏颜色与冻结起点不同")
    axes = model.tables()[0]
    cell = [int(axes[a,anchor[a]]) for a in range(3)]
    ranges = [np.flatnonzero(axes[a] == c).tolist() for a,c in enumerate(cell)]
    if int(np.prod([len(r) for r in ranges])) > plan["max_cell_colours"]:raise ValueError("热点单元超过冻结上限")
    points = np.asarray(list(itertools.product(*ranges)),np.uint8)
    target = table[tuple(points.T)]
    baseline_cell = interp.apply_tetra_q16(model,points)
    write(args.output / "cell.json",{"cell":cell,"axes":ranges,"points":points.tolist(),"targets":target.tolist(),"baseline":baseline_cell.tolist()})
    anchor_prediction = interp.apply_tetra_q16(model,np.asarray([anchor],np.uint8))[0]
    anchor_truth = table[tuple(anchor)]
    channel = int(np.argmax(np.abs(anchor_prediction.astype(int)-anchor_truth.astype(int))))
    maximum = int(math.floor(case["final"]["cube"]["max"]))-1
    print(f"自动主改：热点{anchor}，通道{channel}，完整RGB目标{maximum}",flush=True)
    primary,primary_info = lm.minimum_change(model,points,target,rgb_max=maximum,max_delta=plan["primary_delta"],time_limit=plan["milp_time_limit"],channel=channel)
    if primary is None:raise ValueError("冻结主改问题没有可用整数候选；不扩大参数范围")
    primary_moves = ac.moves(model,primary)
    primary_nodes = [m["node"] for m in primary_moves]
    pool = ac.neighbors(model,primary_nodes,maximum=plan["max_neighbor_nodes"])
    allowed = sorted(set(lm.design(model,points)[0].tolist())|set(primary_nodes)|set(pool))
    support = affected(model,allowed)
    if len(support) > plan["max_support_colours"]:raise ValueError("自动邻域的完整支撑超过冻结范围")
    keys = tr.encode(support)
    prediction = interp.apply_tetra_q16(model,support)
    if not np.array_equal(prediction,np.memmap(frame["stream_path"],np.uint8,mode="r",shape=(256**3,3))[keys]):raise ValueError("自动支撑基线与已测完整流不同")
    truth = table.reshape(-1,3)[keys]
    print(f"主改{len(primary_moves)}节点，辅助池{len(pool)}节点，完整支撑{len(support)}色；一次构建局部频数",flush=True)
    rows = {r["id"]:r for r in load(ROOT / "assets/photos/manifest.json")["images"]}
    weights = frequency(keys,frame["inventory"],frame["partition"],plan,rows)
    import csv
    with (args.output / "frequencies.csv").open("w",encoding="utf-8",newline="") as f:
        writer = csv.writer(f,lineterminator="\n")
        writer.writerow(("group","key","count"))
        for g,k in zip(*np.nonzero(weights)):writer.writerow((int(g),int(keys[k]),int(weights[g,k])))
    write(args.output / "support.json",{"nodes":allowed,"points":support.tolist(),"baseline_sha256":hashlib.sha256(prediction.tobytes()).hexdigest(),"frequency_sha256":hashlib.sha256(weights.tobytes()).hexdigest()})
    state = ac.ConditionalScorer(model,support,truth,weights,photos,domain["final"]["histogram"],allowed)
    old = np.sum((prediction.astype(np.int32)-truth)**2,axis=1)
    hist = np.zeros(3*255**2+1,np.int64)
    for d,n in domain["final"]["histogram"]:hist[d] = n
    guard = cg.CvarGuard(hist,ac.signature(model))
    write(args.output / "cvar-reference.json",guard.reference_report(digest(frame["model_path"])))
    records,models = [],{}
    def evaluate(name,candidate,role,proposal=None):
        folder = args.output / name
        folder.mkdir()
        io.save_sparse(folder / "model.slut",candidate)
        current = interp.apply_tetra_q16(candidate,support)
        new = np.sum((current.astype(np.int32)-truth)**2,axis=1)
        assessment = assess(old,new,weights,photos,domain,guard)
        info = {"role":role,"proposal":proposal}
        record = {"name":name,"generated":True,"model_sha256":digest(folder / "model.slut"),"solver":info,"assessment":assessment,
            "moves":ac.moves(model,candidate),"cell_metrics":ea.metrics(interp.apply_tetra_q16(candidate,points),target),"support_sha256":hashlib.sha256(current.tobytes()).hexdigest()}
        score = state.score(candidate)
        normalized = [v.removeprefix("fixed.").replace(".mean_bound",".mean") for v in assessment["failed"] if v.startswith("fixed.")]
        if "cvar.mean_bound" in assessment["failed"]:normalized.append("full.cvar")
        if "primary_loss" in assessment["failed"]:normalized.append("primary_loss")
        if (set(normalized) != set(score["fixed_failed"]) or score["primary_loss"] != assessment["primary_loss"] or score["full_sse_delta"] != assessment["full_sse_delta"]
                or score["max_squared"] != assessment["full_domain"]["candidate"]["max_squared_error"]):raise AssertionError("快速条件排序与完整保护的共同指标不同")
        write(folder / "result.json",record)
        write(folder / "solver.json",info)
        records.append(record)
        models[name] = candidate
        print(name,"节点",len(record["moves"]),"全域max",assessment["cube_metrics"]["max"],"缺口",assessment["primary_loss"],"失败",len(assessment["failed"]),flush=True)
        return record
    control = evaluate("baseline",model,"control")
    if not control["assessment"]["accepted"] or control["assessment"]["primary_loss"] != case["final_loss"]:raise AssertionError("自动状态空修改未复现起点")
    p = evaluate("primary",primary,"primary",primary_info)
    def feasible(r):return r["assessment"]["accepted"] and r["assessment"]["cube_metrics"]["max"] < case["final"]["cube"]["max"]
    trace = {"anchor":anchor,"channel":channel,"rgb_target":maximum,"primary_solver":primary_info,"primary_moves":primary_moves,"helper_nodes":pool,
        "allowed_nodes":allowed,"state_signature":state.signature,"early_primary_feasible":feasible(p),"first":[],"second":[],"pair_records":[],"triple_records":[]}
    if not feasible(p):
        trace["first"] = ac.ranked_helpers(model,primary,state,pool,deltas=tuple(plan["helper_deltas"]))
        pairs_selected = []
        for i,proposal in enumerate(trace["first"][:plan["pair_limit"]],1):
            name = f"pair_{i:03d}"
            pairs_selected.append(evaluate(name,ac.apply_helper(primary,model,proposal["helper"]),"pair",proposal))
            trace["pair_records"].append(name)
        if not any(feasible(r) for r in pairs_selected):
            seen = set()
            for first in pairs_selected:
                ranking = ac.ranked_helpers(model,models[first["name"]],state,pool,deltas=tuple(plan["helper_deltas"]))
                trace["second"].append({"prefix":first["name"],"proposals":ranking,"records":[]})
                for proposal in ranking[:plan["second_limit"]]:
                    candidate = ac.apply_helper(models[first["name"]],model,proposal["helper"])
                    key = tuple((m["node"],tuple(m["after"])) for m in ac.moves(model,candidate))
                    if key in seen:continue
                    seen.add(key)
                    name = f"triple_{len(trace['triple_records'])+1:03d}"
                    evaluate(name,candidate,"triple",{"prefix":first["name"],**proposal})
                    trace["second"][-1]["records"].append(name)
                    trace["triple_records"].append(name)
    write(args.output / "automatic.json",trace)
    choices = [r for r in records if r["name"] != "baseline" and feasible(r)]
    selected = min(choices,key=lambda r:(r["assessment"]["cube_metrics"]["max"],r["assessment"]["primary_loss"],len(r["moves"]),r["name"])) if choices else None
    selection = {"selected":selected["name"] if selected else None,"before_photos":True,"scope":plan["limits"]}
    write(args.output / "selection-before-photos.json",selection)
    final = {**case["final"],"reused":True}
    if selected:
        from run_chain_error_study import cube_evaluate,photos_evaluate
        from run_joint_box_study import native_verify
        folder = args.output / selected["name"]
        chosen = models[selected["name"]]
        print("冻结自动选择：",selected["name"],"；一次完整终验",flush=True)
        cube = cube_evaluate([table],ea.Operator([chosen]),folder / "cube.rgb",128)
        for k in ("mean","rms","p99","max","cvar_1pct"):
            if abs(cube[k]-selected["assessment"]["cube_metrics"][k]) > 1e-10:raise AssertionError("自动候选完整分布不同")
        native = native_verify([chosen],folder,cube["prediction_sha256"],args.executable)
        actual_photos = photos_evaluate([table],{"selected":ea.Operator([chosen])})["selected"]
        by_id = {r["image"]:r for r in actual_photos["per_image"]}
        for g,meta in enumerate(frame["inventory"]["groups"][:80]):
            for k in ("mean","rms","p99","max"):
                if abs(by_id[meta["image"]][k]-selected["assessment"]["groups"][g]["metrics"][k]) > 1e-12:raise AssertionError("自动候选完整照片不同")
        final = {"cube":cube,"photos":actual_photos,"native":native,"reused":False}
    write(args.output / "results.json",{"case":case["case"],"run_identity":metadata["identity_sha256"],"certificate":certificate,
        "records":records,"interactions":[],"selection":selection,"final":final,"scope":plan["limits"]})
    print("自动条件补偿结束；选择：",selection["selected"],flush=True)


if __name__ == "__main__":main()
