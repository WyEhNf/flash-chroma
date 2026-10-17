"""按冻结计划构建完整图片频数约束，有限修复后只验收最终检查点。"""
import argparse
import hashlib
import json
from pathlib import Path
import sys
import zipfile
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT / "python"))
import numba
import numpy as np
import psutil
from lutlab import error_analysis as ea, fit, full_domain_guard as fg, io, quantile_constraints as qc, quantile_repair as qr, study_provenance, tail_repair as tr
from lutlab.compatibility import environment, write_json
from run_chain_error_study import cube_evaluate,digest,photos_evaluate,source_tables
from run_joint_box_study import native_verify
from run_tail_repair import read_image


def array_sha(array):return hashlib.sha256(array.tobytes()).hexdigest()


def build_groups(rows,partition,plan,out):
    names = [r["id"] for r in partition["training"]["images"]+partition["guard"]["images"]]
    keys,groups,counts,metadata = [],[],[],[]
    samples,sample_info = [],[]
    def append(rgb,g,meta):
        colours,frequency = np.unique(tr.encode(rgb),return_counts=True)
        keys.append(colours.astype(np.uint32))
        groups.append(np.full(len(colours),g,np.uint8))
        counts.append(frequency.astype(np.uint32))
        metadata.append({**meta,"group":g,"pixel_count":len(rgb),"unique_colours":len(colours)})
    for g,name in enumerate(names):
        row = rows[name]
        rgb = read_image(row)
        append(rgb,g,{"image":name,"kind":"full","split":"training" if g < 60 else "selection",**row["evaluation"]})
        if g >= 60:
            seed = int.from_bytes(hashlib.sha256((str(plan["pixel_seed"])+":"+name).encode()).digest()[:8],"little")
            selected = np.random.default_rng(seed).choice(len(rgb),plan["pixels_per_image"],replace=False)
            samples.append(rgb[selected].copy())
            sample_info.append({"id":name,"file_sha256":row["evaluation"]["sha256"],
                "pixel_indices_sha256":array_sha(selected.astype("<u4"))})
        if (g+1) % 20 == 0:print(f"完整图片频数：{g+1}/80",flush=True)
    sample_array = np.concatenate(samples)
    if {"images":sample_info,"samples_sha256":array_sha(sample_array)} != partition["guard"]:
        raise ValueError("分位约束的20图样本与既有选择集不同")
    for k,(rgb,info) in enumerate(zip(samples,sample_info)):
        append(rgb,80+k,{"image":info["id"],"kind":"sample","pixel_indices_sha256":info["pixel_indices_sha256"]})
    append(sample_array,100,{"image":"selection_samples_combined","kind":"sample_aggregate","samples_sha256":array_sha(sample_array)})
    # 审计图只核对输入字节，不用于任何约束或模型选择。
    for name in partition["audit_ids"]:read_image(rows[name])
    inverse = qc.invert(np.concatenate(keys),np.concatenate(groups),np.concatenate(counts),256**3,101)
    inventory = {"groups":metadata,"observed_colour_memberships":len(inverse[1]),
        "inverse_sha256":[array_sha(a) for a in inverse],"inverse_array_bytes":sum(a.nbytes for a in inverse),
        "samples_sha256":array_sha(sample_array),"scope":"80张完整图片、20选择样本及其合并，重复像素保留；20审计不反馈"}
    write_json(out / "photo-inventory.json",inventory)
    return inverse,inventory


def original_errors(model,previous,table,folder):
    path = ROOT / "artifacts/fractional-fit-v1" / previous["case"]["id"] / "historical.rgb"
    expected = previous["bank"]["historical"]["cube"]["prediction_sha256"]
    if not path.exists():
        path = folder / "historical-reference.rgb"
        value = cube_evaluate([table],ea.Operator([model]),path,128)
        if value != previous["bank"]["historical"]["cube"]:
            raise AssertionError("恢复的历史完整流或指标不同")
    if path.stat().st_size != 256**3*3 or digest(path) != expected:
        raise ValueError("历史完整流SHA/长度不同，不重写旧缓存")
    prediction = np.memmap(path,np.uint8,mode="r",shape=(256**3,3))
    target = table.reshape(-1,3)
    result = np.empty(256**3,np.int32)
    for start in range(0,len(result),1 << 18):
        stop = start+(1 << 18)
        difference = prediction[start:stop].astype(np.int32)-target[start:stop]
        result[start:stop] = np.sum(difference*difference,axis=1)
    return result


def process(previous,plan,out,cache,executable,archive,inverse,inventory):
    cid = previous["case"]["id"]
    folder = out / cid
    folder.mkdir()
    models = {}
    for name,member in (("historical",cid+"/historical.slut"),("fractional_full",cid+"/fractional_full/model.slut"),("fractional_mixed",cid+"/fractional_mixed/model.slut")):
        path = folder / (name+".slut")
        path.write_bytes(archive.read(member))
        if digest(path) != previous["bank"][name]["model_sha256"]:raise ValueError("父阶段模型SHA不同")
        models[name] = io.load_sparse(path)
    with archive.open(cid+"/historical-grid.npy") as stream:grid = np.load(stream)
    for model in models.values():
        model.grid = grid.copy()
        if not all(np.array_equal(a,b) for a,b in zip(io.axis_tables(grid),model.tables())):
            raise ValueError("原离线坐标与权威轴表不一致")
    table_list,sources = source_tables(previous["case"],cache)
    table = table_list[0]
    if sources[0]["table_sha256"] != previous["sources"][0]["table_sha256"]:raise ValueError("完整本级参考表不同")
    model = tr.clone([models["fractional_mixed"]])[0]
    points = np.empty((256**3,3),np.uint8)
    for start in range(0,len(points),1 << 18):points[start:start+(1 << 18)] = tr.decode(np.arange(start,start+(1 << 18),dtype=np.int64))
    print(f"[{cid}] 建立完整域状态与101组误差分布",flush=True)
    config = plan["full_domain_guard"]
    domain = fg.DomainGuard([model],points,table.reshape(-1,3),numerator=config["mean_numerator"],denominator=config["mean_denominator"])
    if array_sha(domain.prediction) != previous["bank"]["fractional_mixed"]["cube"]["prediction_sha256"]:
        raise AssertionError("混合初态完整流与父阶段不同")
    errors = original_errors(models["historical"],previous,table,folder)
    photos = qc.GroupState(inverse,101,errors,domain.squared,[list(range(80)),[100]],
        numerator=config["mean_numerator"],denominator=config["mean_denominator"])
    del errors
    initial_report = photos.report()
    for name,field in (("historical","original_metrics"),("fractional_mixed","initial_metrics")):
        old = {r["image"]:r for r in previous["bank"][name]["photos"]["per_image"]}
        for item,meta in zip(initial_report["groups"][:80],inventory["groups"][:80]):
            if any(abs(v-old[meta["image"]][k]) > 1e-12 for k,v in item[field].items()):
                raise AssertionError("完整图片频数重建指标与父阶段不同")
        if any(abs(v-previous["bank"][name]["guard"][k]) > 1e-12 for k,v in initial_report["groups"][100][field].items()):
            raise AssertionError("合并选择像素分布与父阶段不同")
    persistent_bytes = domain.cache_bytes+initial_report["cache_array_bytes"]
    if persistent_bytes > plan["memory_array_budget_bytes"]:raise MemoryError("离线参与数组超过冻结预算")
    write_json(folder / "initial-groups.json",initial_report)
    sample_nodes = fit.quantize(fit.fit_sample(table,grid))
    sampled = io.SparseLut(grid.copy(),sample_nodes,*(a.copy() for a in model.tables()))
    bank = [models["historical"],models["fractional_full"],models["fractional_mixed"],sampled]
    io.save_sparse(folder / "sampled-nodes.slut",sampled)
    replayed,warm_case = [],None
    if plan.get("warm_start"):
        warm = ROOT / plan["warm_start"]
        warm_case = next(c for c in json.loads((warm / "results.json").read_text(encoding="utf-8"))["cases"] if c["case"]["id"] == cid)
        old_initial = json.loads((warm / cid / "initial-groups.json").read_text(encoding="utf-8"))
        if initial_report != old_initial:raise ValueError("热启动初态图片阈值/预算或来源不同")
        for record in warm_case["selection"]["search"]["accepted"]:
            moves = tuple(tr.Move(0,m["node"],tuple(m["after"])) for m in record["moves"])
            move = fg.combine(moves)
            full_trial = domain.trial([model],move)
            photo_trial = photos.trial(full_trial["rows"],domain.squared[full_trial["rows"]],full_trial["squared"])
            if photos.loss != record["before_loss"] or photo_trial.loss != record["after_loss"] or photo_trial.failed:
                raise AssertionError("冻结步骤重放的图片缺口或保护不同")
            if not domain.consider([model],move)["accepted"]:raise AssertionError("冻结步骤重放不通过原完整域预算")
            for part,change in zip(moves,record["moves"]):
                node = model.nodes.reshape(-1,3)[part.node]
                if node.tolist() != change["before"]:raise AssertionError("热启动节点前值不同")
                node[:] = part.value
            domain.commit([model],move)
            photos.commit(photo_trial)
            replayed.append({**record,"replayed":True})
        warm_path = folder / "warm-replayed.slut"
        io.save_sparse(warm_path,model)
        if digest(warm_path) != warm_case["selection"]["model_sha256"] or array_sha(domain.prediction) != warm_case["final"]["cube"]["prediction_sha256"]:
            raise AssertionError("热启动重放模型/完整流与v1不同")
        write_json(folder / "warm-start.json",{"source":plan["warm_start"],"replayed_steps":len(replayed),
            "warm_loss":photos.loss,"model_sha256":digest(warm_path),"full_prediction_sha256":array_sha(domain.prediction)})
    warm_loss = photos.loss
    if plan.get("stability"):
        from lutlab.stability import Stability
        if warm_case is None:raise ValueError("本阶段稳定性比较必须指定已验证热启动")
        photos.stability = Stability(photos,domain,tail_ranking=plan["stability"]["tail_ranking"])
        write_json(folder / "stability-reference.json",photos.stability.reference_report(digest(warm_path)))
        if not photos.stability.certificate(photos,domain.hist)["accepted"]:raise AssertionError("冻结参照本身没有通过稳定性检查")
        persistent_bytes += photos.stability.cache_array_bytes
        if persistent_bytes > plan["memory_array_budget_bytes"]:raise MemoryError("稳定性参照超过冻结数组预算")
    def accepted(record,current):
        record = {**record,"step":record["step"]+len(replayed)}
        path = folder / f"checkpoint{record['step']:03d}.slut"
        io.save_sparse(path,current)
        write_json(path.with_suffix(".json"),{**record,"model_sha256":digest(path),
            "violating_groups":np.flatnonzero(np.any(photos.costs > 0,axis=1)).tolist()})
    print(f"[{cid}] 初始整数缺口{photos.loss}；开始固定预算节点块修复",flush=True)
    prefix_expected = None
    if plan.get("pair_prefix_reference"):
        reference = json.loads((ROOT / plan["pair_prefix_reference"]).read_text(encoding="utf-8"))
        prefix_expected = next(c for c in reference["cases"] if c["case"]["id"] == cid)["selection"]["search"]["compensation_rounds"][0]
    search = qr.repair(model,bank,domain,photos,steps=plan["steps"],focus_count=plan["focus_count"],
        trial_limit=plan["trial_limit"],pair_nodes=plan["pair_nodes"],on_accept=accepted,compensation=plan.get("compensation"),
        global_search=plan.get("global_search"),pair_prefix_expected=prefix_expected)
    new_accepted = len(search["accepted"])
    search["accepted"] = replayed+[{**r,"step":r["step"]+len(replayed)} for r in search["accepted"]]
    search.update(replayed_steps=len(replayed),new_accepted_steps=new_accepted)
    final_groups = photos.report()
    if not final_groups["guards_accepted"]:raise AssertionError("最终照片mean/RMS固定保护失败")
    full = domain.report()
    if not full["certificate"]["accepted"]:raise AssertionError("最终完整域证书失败")
    full["combined_cache_array_bytes"] = persistent_bytes
    memory = psutil.Process().memory_info()
    full["host_memory"] = {"rss_snapshot":memory.rss,"os_peak_working_set":getattr(memory,"peak_wset",None),"scope":"整个离线进程，含构建临时数组和Python对象；不是运行时内存"}
    write_json(folder / "final-groups.json",final_groups)
    write_json(folder / "full-domain.json",full)
    final_path = folder / "repaired.slut"
    io.save_sparse(final_path,model)
    if photos.stability is not None:
        certificate = photos.stability.certificate(photos,domain.hist,full["final"])
        if not certificate["accepted"]:raise AssertionError("最终固定参考稳定性证书失败")
        write_json(folder / "stability-final.json",{**certificate,"model_sha256":digest(final_path)})
    selection = {"search":search,"tail_feasible":photos.loss == 0,"model_sha256":digest(final_path),
        "full_domain_certificate":full["certificate"],"scope":"在最终100图之前冻结；缺口未清零仍如实标为部分修复"}
    write_json(folder / "selection-before-photos.json",selection)
    if new_accepted:
        print(f"[{cid}] 冻结最终检查点，可行={photos.loss == 0}；一次完整终验",flush=True)
        cube = cube_evaluate(table_list,ea.Operator([model]),folder / "repaired.rgb",128)
        if cube["prediction_sha256"] != full["prediction_sha256"]:raise AssertionError("完整重建与增量缓存不同")
        parity = native_verify([model],folder,cube["prediction_sha256"],executable)
        photo_metrics = photos_evaluate(table_list,{"repaired":ea.Operator([model])})["repaired"]
        final = {"cube":cube,"photos":photo_metrics,"native":parity,"reused":False}
        actual = {r["image"]:r for r in photo_metrics["per_image"]}
        for record,meta in zip(final_groups["groups"][:80],inventory["groups"][:80]):
            if any(abs(value-actual[meta["image"]][k]) > 1e-12 for k,value in record["metrics"].items()):
                raise AssertionError("最终完整照片与增量图片直方图不同")
    else:
        old = warm_case["final"] if warm_case is not None else previous["bank"]["fractional_mixed"]
        expected_model = warm_case["selection"]["model_sha256"] if warm_case is not None else old["model_sha256"]
        if digest(final_path) != expected_model:raise AssertionError("无新接受却改变了固定检查点模型")
        final = {"cube":old["cube"],"photos":old["photos"],"native":old["native"],"reused":True}
    result = {"case":previous["case"],"sources":sources,"selection":selection,"initial_loss":initial_report["loss"],
        "warm_loss":warm_loss,"final_loss":photos.loss,"tail_feasible":photos.loss == 0,"final":final,
        "historical":previous["bank"]["historical"],"initial":previous["bank"]["fractional_mixed"],"scope":plan["limits"]}
    write_json(folder / "results.json",result)
    return result


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--plan",type=Path,default=ROOT / "experiments/quantile-tail-v1.json")
    parser.add_argument("--output",type=Path,required=True)
    parser.add_argument("--cache",type=Path,default=ROOT / "artifacts/chain-error-cache")
    parser.add_argument("--executable",type=Path,required=True)
    args = parser.parse_args()
    if args.output.exists():raise ValueError("不覆盖旧研究，复现请使用新目录")
    plan = json.loads(args.plan.read_text(encoding="utf-8"))
    parent = ROOT / plan["parent"]
    previous = json.loads((parent / "results.json").read_text(encoding="utf-8"))
    parent_env = json.loads((parent / "environment.json").read_text(encoding="utf-8"))
    if digest(ROOT / "assets/photos/manifest.json") != parent_env["identity"]["image_manifest"]:raise ValueError("图片清单不同，不能复用阈值")
    partition = json.loads((parent / "photo-partition.json").read_text(encoding="utf-8"))
    rows = {r["id"]:r for r in json.loads((ROOT / "assets/photos/manifest.json").read_text(encoding="utf-8"))["images"]}
    numba.set_num_threads(plan["threads"])
    metadata = environment(argparse.Namespace(sizes=[33],screen_pixels=plan["pixels_per_image"],threads=plan["threads"],reps=0,extended=False))
    extra = [Path(__file__),ROOT / "python/lutlab/quantile_constraints.py",ROOT / "python/lutlab/quantile_repair.py",
        ROOT / "python/lutlab/full_domain_guard.py",ROOT / "python/lutlab/tail_repair.py",ROOT / "python/lutlab/error_analysis.py",
        ROOT / "scripts/run_chain_error_study.py",ROOT / "scripts/run_joint_box_study.py",ROOT / "scripts/run_tail_repair.py"]
    if plan.get("compensation"):extra.append(ROOT / "python/lutlab/quantile_compensation.py")
    if plan.get("compensation",{}).get("method") == "rounded":extra.append(ROOT / "python/lutlab/rounded_budget.py")
    if plan.get("compensation",{}).get("block_order",2) == 3:extra.append(ROOT / "python/lutlab/rounded_blocks.py")
    if plan.get("global_search"):extra.append(ROOT / "python/lutlab/quantile_global.py")
    if plan.get("global_search",{}).get("method") == "primary_budget":extra.append(ROOT / "python/lutlab/primary_budget.py")
    if plan.get("stability"):extra.append(ROOT / "python/lutlab/stability.py")
    metadata["identity"].update(plan_sha256=digest(args.plan),executable_sha256=digest(args.executable),
        stage_source_sha256={str(p.relative_to(ROOT)):digest(p) for p in extra},
        parent_files={n:digest(parent / n) for n in ("results.json","environment.json","photo-partition.json","models-and-selection.zip","archive-index.json")})
    if plan.get("warm_start"):
        warm = ROOT / plan["warm_start"]
        old_run = json.loads((warm / "run.json").read_text(encoding="utf-8"))
        if old_run["identity"]["environment"] != metadata["identity"]["environment"]:
            raise ValueError("热启动数值环境不同，不混用旧来源")
        metadata["identity"]["warm_files"] = {n:digest(warm / n) for n in ("run.json","results.json","photo-inventory.json")}
    if plan.get("replay_reference"):
        metadata["identity"]["replay_reference_sha256"] = digest(ROOT / plan["replay_reference"])
    if plan.get("pair_prefix_reference"):
        metadata["identity"]["pair_prefix_reference_sha256"] = digest(ROOT / plan["pair_prefix_reference"])
    metadata["identity_sha256"] = study_provenance.identity_digest(metadata["identity"])
    metadata.update(backend="Numba研究4线程，标量/AVX2终验单线程",timing_scope="不比较性能",deferred=["硬件加速","官方评分","未知图像泛化"])
    study_provenance.claim_run(args.output / "run.json",metadata)
    write_json(args.output / "photo-partition.json",partition)
    with zipfile.ZipFile(args.output / "measured-source.zip","w",zipfile.ZIP_DEFLATED) as z:
        for name,expected in {**metadata["identity"]["source_sha256"],**metadata["identity"]["stage_source_sha256"]}.items():
            data = (ROOT / name).read_bytes()
            if hashlib.sha256(data).hexdigest() != expected:raise ValueError("源码快照变化")
            z.writestr(name.replace("\\","/"),data)
    inverse,inventory = build_groups(rows,partition,plan,args.output)
    if plan.get("warm_start"):
        old_inventory = json.loads((ROOT / plan["warm_start"] / "photo-inventory.json").read_text(encoding="utf-8"))
        if inventory != old_inventory:raise ValueError("热启动图片倒排和频数输入不同")
    with zipfile.ZipFile(parent / "models-and-selection.zip") as z:
        index = json.loads((parent / "archive-index.json").read_text(encoding="utf-8"))
        if set(index) != set(z.namelist()) or any(hashlib.sha256(z.read(n)).hexdigest() != h for n,h in index.items()):raise ValueError("父归档变化")
        results = [process(next(c for c in previous["cases"] if c["case"]["id"] == cid),plan,args.output.resolve(),
            args.cache.resolve(),args.executable.resolve(),z,inverse,inventory) for cid in plan["cases"]]
    if plan.get("replay_reference"):
        reference = json.loads((ROOT / plan["replay_reference"]).read_text(encoding="utf-8"))
        for current in results:
            old = next(c for c in reference["cases"] if c["case"]["id"] == current["case"]["id"])
            if current["selection"]["model_sha256"] != old["selection"]["model_sha256"] or current["final_loss"] != old["final_loss"]:
                raise AssertionError("只补记回执却改变了冻结模型或缺口")
            a,b = current["selection"]["search"],old["selection"]["search"]
            for field in ("single_trials","pair_trials","compensated_pair_trials","rejections"):
                if a[field] != b[field]:raise AssertionError("诊断复现的原候选判定数量不同")
            if [r["statistics_sha256"] for r in a["compensation_rounds"]] != [r["statistics_sha256"] for r in b["compensation_rounds"]]:
                raise AssertionError("诊断复现的真实舍入统计哈希不同")
    if plan.get("pair_prefix_reference"):
        reference = json.loads((ROOT / plan["pair_prefix_reference"]).read_text(encoding="utf-8"))
        for current in results:
            old = next(c for c in reference["cases"] if c["case"]["id"] == current["case"]["id"])
            a,b = [c["selection"]["search"]["compensation_rounds"][0] for c in (current,old)]
            if a["statistics_sha256"] != b["statistics_sha256"] or a["trials"] != b["trials"]:
                raise AssertionError("三节点扩展前原128对候选/判定或统计SHA已改变")
    write_json(args.output / "results.json",{"run_identity":metadata["identity_sha256"],"cases":results})
    print("分位/最大误差约束阶段结束；不提升默认",flush=True)


if __name__ == "__main__":main()
