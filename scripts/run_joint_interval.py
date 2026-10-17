"""在反例导出的有限节点箱联合求解；复用已验证频数，只对一个新终态完整验收。"""
import argparse
import csv
import hashlib
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
from lutlab import automatic_compensation as ac,cvar_guard as cg,error_analysis as ea,interp,io,joint_interval as ji,study_provenance,tail_repair as tr
from local_study_snapshot import snapshot
from run_extreme_cell import assess,digest,load,write
from verify_quantile_constraints import verify_groups


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--plan",type=Path,default=ROOT / "experiments/joint-interval-v1.json")
    parser.add_argument("--output",type=Path,required=True)
    parser.add_argument("--executable",type=Path,default=ROOT / "build-engineering-alignment/jshc.exe")
    args = parser.parse_args()
    if args.output.exists():raise ValueError("不覆盖联合区间实验")
    plan = load(args.plan)
    quality = bool(plan.get("joint_minimax"))
    working = bool(plan.get("working_set"))
    if working and not quality:raise ValueError("工作集比较必须使用同一质量目标")
    warm,evidence = [ROOT / plan[k] for k in ("warm_run","evidence_run")]
    frame = snapshot(warm,plan["case"])
    case,photos,domain = [frame[k] for k in ("case","photos","domain")]
    for folder in (warm,evidence):
        proof = load(folder / "verification.json")
        if not proof["verified"] or proof["input_result_sha256"] != digest(folder / "results.json"):raise ValueError("父测量未绑定独立复核")
    if working:
        for name,h in plan["parent_evidence_sha256"].items():
            if digest(warm / name) != h:raise ValueError("父工作集已发布证据变化")
    diagnosis_path = ROOT / plan["diagnosis"]
    diagnosis = load(diagnosis_path)
    if (not diagnosis["verified"] or diagnosis["result_sha256"] != digest(evidence / "results.json") or
            diagnosis["verification_sha256"] != digest(evidence / "verification.json") or diagnosis["trace_sha256"] != digest(evidence / "automatic.json")):
        raise ValueError("颜色反例没有绑定父候选/完整复核")
    if digest(frame["model_path"]) != plan["model_sha256"] or digest(ROOT / "assets/photos/manifest.json") != frame["manifest_sha256"]:
        raise ValueError("当前起点模型/图片清单不同")
    check = verify_groups(photos)
    if check["loss"] != case["final_loss"] or not check["guards_accepted"]:raise ValueError("起点历史目标或保护不同")
    numba.set_num_threads(plan["threads"])
    environment = study_provenance.environment_fingerprint()
    if any(frame["run"]["identity"]["environment"][k] != v for k,v in environment.items()):raise ValueError("数值环境与已测终态不同")
    cache_run = load(evidence / "run.json")
    if cache_run["identity"]["environment"] != environment:raise ValueError("照片频数环境不同")
    table_path = ROOT / case["sources"][0]["path"]
    if digest(table_path) != case["sources"][0]["table_sha256"] or digest(frame["stream_path"]) != case["final"]["cube"]["prediction_sha256"]:
        raise ValueError("参考表/旧完整流不同")
    cached_model = evidence / "reference" / plan["case"] / "repaired.slut"
    model = io.load_sparse(frame["model_path"])
    if quality:
        cached = io.load_sparse(cached_model)
        if cached.m != model.m or not all(np.array_equal(a,b) for a,b in zip(cached.tables(),model.tables())):raise ValueError("频数缓存的几何与新起点不同")
    elif digest(cached_model) != plan["model_sha256"]:raise ValueError("复用频数绑定的模型不同")
    scripts = ("run_joint_interval","verify_joint_interval","local_study_snapshot","run_extreme_cell","verify_extreme_cell","verify_automatic_compensation",
        "verify_stability","verify_quantile_constraints","verify_full_domain_guard","verify_cvar_guard","diagnose_three_node","diagnose_quantile_bounds",
        "run_tail_repair","run_chain_error_study","run_joint_box_study")
    sources = ["scripts/"+n+".py" for n in scripts]+["python/lutlab/"+n+".py" for n in
        ("joint_interval","automatic_compensation","histogram_delta","interp","io","cvar_guard","full_domain_guard","error_analysis","tail_repair","study_provenance","runtime")]
    if quality:sources += ["python/lutlab/joint_minimax.py","scripts/audit_hald_reference.py"]
    if working:sources += ["python/lutlab/working_set.py","scripts/verify_working_set.py"]
    refs = [warm / n for n in ("results.json","run.json","verification.json","certificate.json")]+[frame["model_path"],frame["stream_path"],table_path,diagnosis_path,
        evidence / "results.json",evidence / "verification.json",evidence / "automatic.json",evidence / "cell.json",evidence / "certificate.json",cached_model,ROOT / "assets/photos/manifest.json"]
    refs += [warm / "reference" / n for n in ("results.json","run.json","photo-inventory.json","photo-partition.json",plan["case"]+"/final-groups.json",plan["case"]+"/full-domain.json")]
    if quality:
        source_spec = case["sources"][0]["source"]
        source_image = ROOT / source_spec["path"]
        if source_spec["format"] != "hald_tiff" or digest(source_image) != source_spec["sha256"]:raise ValueError("源Hald格式/SHA不同")
        refs += [source_image,warm / "joint-search.json"]
    if working:refs += [warm / "source-audit.json"]
    identity = {"environment":environment,"image_manifest_sha256":frame["manifest_sha256"],"plan_sha256":digest(args.plan),"source_sha256":{n:digest(ROOT / n) for n in sources},
        "parent_files":{str(p.relative_to(ROOT)):digest(p) for p in refs},"frequency_cache":{str((evidence / n).relative_to(ROOT)):digest(evidence / n) for n in
            ("run.json","support.json","frequencies.csv")},"executable_sha256":digest(args.executable)}
    metadata = {"identity":identity,"identity_sha256":study_provenance.identity_digest(identity),"git_commit":subprocess.check_output(["git","rev-parse","HEAD"],cwd=ROOT,text=True).strip(),
        "purpose":plan["purpose"],"backend":"NumPy整数区间分支定界，Numba4仅新终态完整验收；非性能比较"}
    if working:metadata["reused_source_audit"] = {"path":str((warm / "source-audit.json").relative_to(ROOT)),"sha256":digest(warm / "source-audit.json")}
    study_provenance.claim_run(args.output / "run.json",metadata)
    shutil.copyfile(args.plan,args.output / "plan.json")
    ref = args.output / "reference"
    (ref / plan["case"]).mkdir(parents=True)
    for name,value in (("results.json",{"cases":[case]}),("run.json",frame["run"]),("photo-inventory.json",frame["inventory"]),("photo-partition.json",frame["partition"]),
            (plan["case"]+"/final-groups.json",photos),(plan["case"]+"/full-domain.json",domain)):write(ref / name,value)
    shutil.copyfile(frame["model_path"],ref / plan["case"] / "repaired.slut")
    if working:shutil.copyfile(warm / "results.json",args.output / "warm-results.json")
    with zipfile.ZipFile(args.output / "measured-source.zip","w",zipfile.ZIP_DEFLATED) as z:
        for name in sources:z.write(ROOT / name,name)
    for name in ("support.json","frequencies.csv","cell.json","certificate.json"):shutil.copyfile(evidence / name,args.output / name)
    for name in ("results.json","verification.json","automatic.json"):shutil.copyfile(evidence / name,args.output / ("prior-"+name))
    shutil.copyfile(diagnosis_path,args.output / "prior-diagnosis.json")
    old_result = load(evidence / "results.json")
    if old_result["selection"]["selected"] is not None or not old_result["final"]["reused"]:raise ValueError("本阶段只接收父有限搜索全拒绝的反例")
    by_name = {r["name"]:r for r in old_result["records"]}
    closest = diagnosis["closest_record"]
    regressions = [x for item in diagnosis["conflicts"] if item["candidate"] == closest for x in item["top_regressions"]]
    node_evidence = {"primary_moves":by_name["primary"]["moves"],"closest_moves":by_name[closest]["moves"],"regressions":regressions,
        "diagnosis_sha256":digest(diagnosis_path),"prior_result_sha256":digest(evidence / "results.json")}
    write(args.output / "node-evidence.json",node_evidence)
    model = io.load_sparse(frame["model_path"])
    nodes = ji.derive_nodes(model,node_evidence["primary_moves"],node_evidence["closest_moves"],regressions,plan["max_nodes"])
    support_record = load(args.output / "support.json")
    if not set(nodes) <= set(support_record["nodes"]):raise ValueError("联合节点超出已验证完整支撑")
    support = np.asarray(support_record["points"],np.uint8)
    keys = tr.encode(support)
    prediction = interp.apply_tetra_q16(model,support)
    if quality:
        if hashlib.sha256(interp.apply_tetra_q16(cached,support).tobytes()).hexdigest() != support_record["baseline_sha256"]:raise ValueError("原频数支撑的旧基线字节不同")
        support_record["baseline_sha256"] = hashlib.sha256(prediction.tobytes()).hexdigest()
        write(args.output / "support.json",support_record)
        cell = load(args.output / "cell.json")
        cell["baseline"] = interp.apply_tetra_q16(model,np.asarray(cell["points"],np.uint8)).tolist()
        write(args.output / "cell.json",cell)
        parent_search = load(warm / "joint-search.json")
        if working:nodes = parent_search["nodes"]
        elif nodes != parent_search["nodes"]:raise ValueError("质量优化变量与父联合块不同")
        if not set(nodes) <= set(support_record["nodes"]) or len(nodes) > plan["max_nodes"]:raise ValueError("父工作集超出已验证支撑或节点上限")
        shutil.copyfile(warm / "joint-search.json",args.output / "parent-search.json")
    if hashlib.sha256(prediction.tobytes()).hexdigest() != support_record["baseline_sha256"] or not np.array_equal(prediction,np.memmap(frame["stream_path"],np.uint8,mode="r",shape=(256**3,3))[keys]):
        raise ValueError("复用支撑基线流不同")
    position = {int(k):i for i,k in enumerate(keys)}
    frequency = np.zeros((101,len(keys)),np.int64)
    with (args.output / "frequencies.csv").open(encoding="utf-8",newline="") as f:
        for row in csv.DictReader(f):frequency[int(row["group"]),position[int(row["key"])]] = int(row["count"])
    if hashlib.sha256(frequency.tobytes()).hexdigest() != support_record["frequency_sha256"]:raise ValueError("照片频数矩阵不同")
    table = io.load_full(table_path,mmap=True)
    truth = table.reshape(-1,3)[keys]
    if quality:
        if working:
            source_audit = load(warm / "source-audit.json")
            if (source_audit["source_sha256"] != digest(source_image) or source_audit["table_sha256"] != digest(table_path) or
                    source_audit["verifier_sha256"] != digest(ROOT / "scripts/audit_hald_reference.py")):
                raise ValueError("复用源审计的源/表/代码不同")
        else:
            from audit_hald_reference import audit
            source_audit = audit(source_image,table_path,source_spec["grid_size"],support.tolist(),plan["source_probes"])
        write(args.output / "source-audit.json",source_audit)
        if not source_audit["verified"]:raise ValueError("独立有理数Hald参考审计不一致，停止优化")
    maximum = math.ceil(case["final"]["cube"]["max"]) if quality else math.floor(case["final"]["cube"]["max"])-1
    problem = ji.Problem(model,support,truth,frequency,photos,domain["final"]["histogram"],nodes,max_delta=plan["max_delta"],rgb_max=maximum,
        channel=plan["channel"],max_assignments=plan["max_assignments"])
    old = np.sum((prediction.astype(np.int32)-truth)**2,axis=1)
    hist = np.zeros(3*255**2+1,np.int64)
    for d,n in domain["final"]["histogram"]:hist[d] = n
    guard = cg.CvarGuard(hist,ac.signature(model))
    cell = load(args.output / "cell.json")
    cell_points,cell_truth = np.asarray(cell["points"],np.uint8),np.asarray(cell["targets"],np.uint8)
    records,models,box_label = [],{},"baseline"
    def evaluate(name,candidate,deltas):
        folder = args.output / name
        folder.mkdir()
        io.save_sparse(folder / "model.slut",candidate)
        mapped = interp.apply_tetra_q16(candidate,support)
        current = np.sum((mapped.astype(np.int32)-truth)**2,axis=1)
        assessment = assess(old,current,frequency,photos,domain,guard)
        record = {"name":name,"generated":True,"model_sha256":digest(folder / "model.slut"),"solver":{"deltas":deltas,**({"box":box_label} if working else {})},"assessment":assessment,
            "moves":ac.moves(model,candidate),"cell_metrics":ea.metrics(interp.apply_tetra_q16(candidate,cell_points),cell_truth),"support_sha256":hashlib.sha256(mapped.tobytes()).hexdigest()}
        records.append(record);models[name] = candidate
        write(folder / "result.json",record)
        print(name,"L1",sum(abs(d) for d in deltas),"max",assessment["cube_metrics"]["max"],"失败",len(assessment["failed"]),flush=True)
        return {"record":name,"accepted":assessment["accepted"]}
    if not evaluate("baseline",model,[0]*len(nodes))["accepted"]:raise ValueError("起点空修改未通过保护")
    print("反例联合节点",nodes,"整数赋值",problem.assignments,"一次完整分支定界，目标",maximum,flush=True)
    if quality:
        from lutlab import joint_minimax as jm
        if working:
            from lutlab import working_set as ws
            warm_result = load(warm / "results.json")
            last = next(r for r in warm_result["records"] if r["name"] == warm_result["selection"]["selected"])
            state = ac.ConditionalScorer(model,support,truth,frequency,photos,domain["final"]["histogram"],support_record["nodes"])
            proposal = ws.propose(model,nodes,last["moves"],state,support_record["nodes"],channel=plan["channel"],deltas=tuple(plan["proposal_deltas"]),max_fresh_nodes=plan["max_fresh_nodes"])
            replacement = ji.Problem(model,support,truth,frequency,photos,domain["final"]["histogram"],proposal["replacement_nodes"],max_delta=plan["max_delta"],rgb_max=maximum,
                channel=plan["channel"],max_assignments=plan["max_assignments"])
            searches = {}
            for box_label,current_problem in (("control",problem),("replacement",replacement)):
                print("受控工作集",box_label,current_problem.nodes,flush=True)
                searches[box_label] = jm.solve(current_problem,lambda candidate,deltas:evaluate(f"{box_label}_{len(records):04d}",candidate,deltas))
                write(args.output / (box_label+"-search.json"),searches[box_label])
                print(box_label,"终端",len(searches[box_label]["terminals"]),"覆盖",searches[box_label]["assignments"],"目标",searches[box_label]["incumbent"]["objective"],flush=True)
            winner = min(searches,key=lambda label:(tuple(searches[label]["incumbent"]["objective"]),label))
            search = searches[winner]
            proposal.update(box_records={label:[r["name"] for r in records if r["solver"].get("box") == label] for label in searches},
                comparison={"control":searches["control"]["incumbent"]["objective"],"replacement":searches["replacement"]["incumbent"]["objective"],"winner":winner,
                    "quality_improved_vs_control":tuple(searches["replacement"]["incumbent"]["objective"][:3]) < tuple(searches["control"]["incumbent"]["objective"][:3]),"before_photos":True})
            write(args.output / "working-set.json",proposal)
        else:search = jm.solve(problem,lambda candidate,deltas:evaluate(f"joint_{len(records):04d}",candidate,deltas))
    else:search = ji.solve(problem,lambda candidate,deltas:evaluate(f"joint_{len(records):04d}",candidate,deltas))
    write(args.output / "joint-search.json",search)
    chosen = search["incumbent"]["name"] if search["incumbent"] else None
    if chosen == "baseline":chosen = None
    selection = {"selected":chosen,"before_photos":True,"scope":plan["limits"]}
    write(args.output / "selection-before-photos.json",selection)
    final = {**case["final"],"reused":True}
    if chosen:
        from run_chain_error_study import cube_evaluate,photos_evaluate
        from run_joint_box_study import native_verify
        folder,candidate = args.output / chosen,models[chosen]
        print("冻结质量联合解" if quality else "冻结最小L1联合解",chosen,"；一次完整终验",flush=True)
        cube = cube_evaluate([table],ea.Operator([candidate]),folder / "cube.rgb",128)
        assessed = next(r for r in records if r["name"] == chosen)["assessment"]
        for k in ("mean","rms","p99","max","cvar_1pct"):
            if abs(cube[k]-assessed["cube_metrics"][k]) > 1e-10:raise ValueError("联合解完整分布与局部更新不同")
        native = native_verify([candidate],folder,cube["prediction_sha256"],args.executable)
        actual_photos = photos_evaluate([table],{"selected":ea.Operator([candidate])})["selected"]
        by_id = {r["image"]:r for r in actual_photos["per_image"]}
        for g,meta in enumerate(frame["inventory"]["groups"][:80]):
            for k in ("mean","rms","p99","max"):
                if abs(by_id[meta["image"]][k]-assessed["groups"][g]["metrics"][k]) > 1e-12:raise ValueError("联合解完整照片与频数不同")
        final = {"cube":cube,"photos":actual_photos,"native":native,"reused":False}
    write(args.output / "results.json",{"case":case["case"],"run_identity":metadata["identity_sha256"],"certificate":load(args.output / "certificate.json"),
        "records":records,"interactions":[],"selection":selection,"final":final,"scope":plan["limits"]})
    print("联合分支完成，终端",len(search["terminals"]),"覆盖",sum(t["covered_assignments"] for t in search["terminals"]),"选中",chosen,flush=True)


if __name__ == "__main__":main()
