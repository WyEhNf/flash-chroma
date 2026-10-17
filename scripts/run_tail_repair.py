"""从版本化模型出发，以完整训练颜色约束修复单图尾部回归。"""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
import sys
import zipfile

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "python"))
import numba
import numpy as np
from PIL import Image
from lutlab import error_analysis as ea, io, study_provenance, tail_repair as tr
from lutlab.compatibility import environment, write_json
from run_chain_error_study import cube_evaluate, digest, fixed_points, photos_evaluate, source_tables
from run_joint_box_study import native_verify


def read_image(row):
    path = ROOT / row["evaluation"]["path"]
    if digest(path) != row["evaluation"]["sha256"]:
        raise ValueError("照片文件哈希不同")
    with Image.open(path) as image:
        if image.mode != "RGB" or image.size != (1024, 768):
            raise ValueError("照片规格不同")
        pixels = np.asarray(image).reshape(-1, 3).copy()
    if hashlib.sha256(pixels.tobytes()).hexdigest() != row["evaluation"]["pixel_sha256"]:
        raise ValueError("照片解码后的RGB字节哈希不同")
    return pixels


def validate_parent_images(parent):
    """旧逐图上限只能用于同一图片清单；在任何输出发布前拒绝更换输入。"""
    previous = json.loads((parent / "run.json").read_text(encoding="utf-8"))
    if digest(ROOT / "assets/photos/manifest.json") != previous["identity"]["image_manifest"]:
        raise ValueError("图片清单已变化，不能复用旧逐图max上限；请先建立新的基线证据")


def sample(rgb, image_id, plan):
    seed = int.from_bytes(hashlib.sha256((str(plan["pixel_seed"])+":"+image_id).encode()).digest()[:8], "little")
    indices = np.random.default_rng(seed).choice(len(rgb), plan["pixels_per_image"], replace=False)
    return rgb[indices].copy()


def scan(models, keys, caps, truth):
    operator, bad, total_excess, maximum = ea.Operator(models), [], 0, 0
    for start in range(0, len(keys), 1 << 18):
        current = keys[start:start+(1 << 18)]
        prediction = operator(tr.decode(current))
        error = prediction.astype(np.int32)-truth[start:start+len(current)].astype(np.int32)
        squared = np.sum(error*error, axis=1, dtype=np.int32)
        excess = np.maximum(squared.astype(np.int64)-caps[current].astype(np.int64), 0)
        bad.append(current[excess > 0])
        total_excess += int(excess.sum())
        maximum = max(maximum, int(excess.max(initial=0)))
    indices = np.concatenate(bad)
    return indices, {"checked_unique_training_colours": len(keys), "violating_colours": len(indices),
                     "sum_squared_excess": total_excess, "max_squared_excess": maximum}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--plan", type=Path, default=ROOT / "experiments/tail-repair-v1.json")
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--cache", type=Path, default=ROOT / "artifacts/chain-error-cache")
    parser.add_argument("--executable", type=Path, required=True)
    args = parser.parse_args()
    out, cache = args.output.resolve(), args.cache.resolve()
    if out.exists():
        raise ValueError("本阶段不覆盖已有目录；恢复模型用版本化ZIP，重新研究请使用新目录")
    plan = json.loads(args.plan.read_text(encoding="utf-8"))
    parent = ROOT / plan["parent"]
    validate_parent_images(parent)
    integrity = json.loads((parent / "integrity.json").read_text(encoding="utf-8"))
    for name, expected in integrity["files"].items():
        if digest(parent / name) != expected:
            raise ValueError("上阶段版本化证据哈希不同")
    previous = next(r for r in json.loads((parent / "results.json").read_text(encoding="utf-8"))["cases"] if r["case"]["id"] == plan["case"])
    numba.set_num_threads(plan["threads"])
    metadata = environment(argparse.Namespace(sizes=[33], screen_pixels=plan["pixels_per_image"], threads=plan["threads"], reps=0, extended=False))
    metadata["identity"].update(plan_sha256=digest(args.plan), parent_integrity_sha256=digest(parent / "integrity.json"),
        executable_sha256=digest(args.executable), stage_source_sha256={str(p.relative_to(ROOT)): digest(p) for p in
            (Path(__file__), ROOT / "python/lutlab/tail_repair.py", ROOT / "python/lutlab/error_analysis.py",
             ROOT / "scripts/run_chain_error_study.py", ROOT / "scripts/run_joint_box_study.py")})
    if plan.get("full_domain_guard"):
        metadata["identity"]["stage_source_sha256"]["python/lutlab/full_domain_guard.py"] = digest(ROOT / "python/lutlab/full_domain_guard.py")
        metadata["identity"]["negative_control_integrity_sha256"] = digest(ROOT / "report/data/tail-repair-v1/integrity.json")
    if plan.get("paired_search"):
        metadata["identity"]["stage_source_sha256"]["python/lutlab/joint_tail_repair.py"] = digest(ROOT / "python/lutlab/joint_tail_repair.py")
    if plan.get("warm_start"):
        warm = ROOT / plan["warm_start"]
        metadata["identity"]["warm_start_sha256"] = {p.name:digest(p) for p in
            [warm / name for name in ("run.json","selection.json","full-domain.json")] + sorted(warm.glob("repaired-stage*.slut"))}
    metadata["identity_sha256"] = study_provenance.identity_digest(metadata["identity"])
    study_provenance.claim_run(out / "run.json", metadata)
    # 快照绑定实测原始字节；后续仅前置检查/报告修补不冒充重新执行数值代码。
    with zipfile.ZipFile(out / "measured-source.zip", "w", zipfile.ZIP_DEFLATED) as archive:
        for name, expected in sorted({**metadata["identity"]["source_sha256"], **metadata["identity"]["stage_source_sha256"]}.items()):
            raw = (ROOT / name).read_bytes()
            if hashlib.sha256(raw).hexdigest() != expected:
                raise ValueError("发布源码快照时文件已变化")
            archive.writestr(name.replace("\\", "/"), raw)
    model_dir = out / "input-models"
    model_dir.mkdir()
    index = json.loads((parent / "archive-index.json").read_text(encoding="utf-8"))
    with zipfile.ZipFile(parent / "models-and-selection.zip") as archive:
        for name, expected in index.items():
            data = archive.read(name)
            if hashlib.sha256(data).hexdigest() != expected:
                raise ValueError("上阶段模型归档成员哈希不同")
            if name.startswith(plan["case"]+"/") and name.endswith(".slut"):
                (model_dir / Path(name).name).write_bytes(data)
    baseline = [io.load_sparse(model_dir / f"baseline-stage{k+1}.slut", competition=True) for k in range(4)]
    initial = [io.load_sparse(model_dir / f"selected-stage{k+1}.slut", competition=True) for k in range(4)]
    banks = [{name: io.load_sparse(model_dir / f"{name}-stage{k+1}.slut", competition=True)
              for name in ("baseline", "mixed_clip", "mixed_box", "mixed_mean")} for k in range(4)]
    tables, references = source_tables(previous["case"], cache)
    if [r["table_sha256"] for r in references] != [r["table_sha256"] for r in previous["sources"]]:
        raise ValueError("重建的完整参考表与上阶段不同")
    rows = {r["id"]: r for r in json.loads((ROOT / "assets/photos/manifest.json").read_text(encoding="utf-8"))["images"]}
    partition = json.loads((parent / "photo-partition.json").read_text(encoding="utf-8"))
    old_photos = {r["image"]: r for r in previous["baseline"]["photos"]["per_image"]}
    cap_for_image = {name: int(round(r["max"]**2)) for name, r in old_photos.items()}
    caps = np.full(256**3, np.iinfo(np.uint32).max, np.uint32)
    training, train_caps, choosing, choose_caps = [], [], [], []
    for i, item in enumerate(partition["training"]["images"]):
        name = item["id"]
        rgb = read_image(rows[name])
        tr.update_caps(caps, rgb, cap_for_image[name])
        training.append(sample(rgb, name, plan))
        train_caps.append(np.full(plan["pixels_per_image"], cap_for_image[name], np.uint32))
        if (i+1) % 20 == 0:
            print(f"训练颜色上限已建立：{i+1}/60张完整图片", flush=True)
    for item in partition["guard"]["images"]:
        name = item["id"]
        choosing.append(sample(read_image(rows[name]), name, plan))
        choose_caps.append(np.full(plan["pixels_per_image"], cap_for_image[name], np.uint32))
    training, choosing = np.concatenate(training), np.concatenate(choosing)
    keys = np.flatnonzero(caps != np.iinfo(np.uint32).max)
    truth = ea.exact_chain(tables, tr.decode(keys))
    write_json(out / "inventory.json", {"training_images": 60, "unique_colours": len(keys),
        "keys_sha256": hashlib.sha256(keys.astype("<u4").tobytes()).hexdigest(),
        "caps_sha256": hashlib.sha256(caps[keys].astype("<u4").tobytes()).hexdigest(),
        "truth_sha256": hashlib.sha256(truth.tobytes()).hexdigest(), "image_caps_squared": cap_for_image})
    uniform = fixed_points(plan["uniform"], [])
    hot = ea.neighbourhood(np.asarray([r["rgb"] for variant in ("baseline", "selected") for r in previous[variant]["cube"]["hotspots"]], np.uint8))
    cube_cap = int(round(previous["selected"]["cube"]["max"]**2))
    guards = {"uniform": {"points": uniform, "caps": np.full(len(uniform), cube_cap, np.uint32)},
        "train_sample": {"points": training, "caps": np.concatenate(train_caps)},
        "guard_sample": {"points": choosing, "caps": np.concatenate(choose_caps)},
        "hotspot": {"points": hot, "caps": np.full(len(hot), cube_cap, np.uint32)}}
    limits, before = {}, {}
    for name, spec in guards.items():
        spec["truth"] = ea.exact_chain(tables, spec["points"])
        old = ea.metrics(ea.Operator(baseline)(spec["points"]), spec["truth"])
        start = ea.metrics(ea.Operator(initial)(spec["points"]), spec["truth"])
        limits[name] = {key: max(old[key], start[key]) for key in ("mean", "rms", "p99", "max")}
        if name != "hotspot":
            limits[name]["mean"] = start["mean"] * plan["mean_budget_ratio"]
        before[name] = {"baseline": old, "initial": start, "input_sha256": hashlib.sha256(spec["points"].tobytes()).hexdigest()}
    write_json(out / "fixed-guards.json", {"limits": limits, "before": before})
    domain_guard = None
    if plan.get("full_domain_guard"):
        from lutlab import full_domain_guard as fg
        config = plan["full_domain_guard"]
        print("构建完整256³参考、前缀与立方体倒排；仅用于离线优化", flush=True)
        full_points = np.empty((256**3,3),np.uint8)
        full_truth = np.empty_like(full_points)
        for start in range(0,256**3,1 << 18):
            rgb = tr.decode(np.arange(start,start+(1 << 18),dtype=np.int64))
            full_points[start:start+len(rgb)] = rgb
            full_truth[start:start+len(rgb)] = ea.exact_chain(tables,rgb)
        domain_guard = fg.DomainGuard(initial,full_points,full_truth,numerator=config["mean_numerator"],
            denominator=config["mean_denominator"],max_cache_bytes=config["max_cache_bytes"])
        if (hashlib.sha256(full_truth.tobytes()).hexdigest() != previous["selected"]["cube"]["reference_sha256"]
                or hashlib.sha256(domain_guard.prediction.tobytes()).hexdigest() != previous["selected"]["cube"]["prediction_sha256"]):
            raise AssertionError("全域保护的固定参考/初始模型字节与父阶段不同")
        # 一份已知超预算旧模型作为负对照；优先读取绑定SHA的旧流，缺失才重建。
        control_parent = ROOT / "report/data/tail-repair-v1"
        control_meta = json.loads((control_parent / "results.json").read_text(encoding="utf-8"))
        expected = control_meta["final"]["cube"]["prediction_sha256"]
        old_stream = ROOT / "artifacts/tail-repair-v1/repaired.rgb"
        operator = None
        if old_stream.exists():
            if old_stream.stat().st_size != 3*256**3 or digest(old_stream) != expected:
                raise ValueError("负对照旧流字节不同，拒绝混用")
            old_prediction = np.memmap(old_stream,dtype=np.uint8,mode="r",shape=(256**3,3))
        else:
            control_index = json.loads((control_parent / "archive-index.json").read_text(encoding="utf-8"))
            paths = []
            with zipfile.ZipFile(control_parent / "models-and-counterexamples.zip") as archive:
                for stage in range(4):
                    name = f"repaired-stage{stage+1}.slut"
                    raw = archive.read(name)
                    if hashlib.sha256(raw).hexdigest() != control_index[name]:
                        raise ValueError("负对照模型字节不同")
                    path = out / ("control-"+name)
                    path.write_bytes(raw)
                    paths.append(path)
            operator = ea.Operator([io.load_sparse(p,competition=True) for p in paths])
        control_hist = np.zeros(len(ea.ROOT_DISTANCE),np.int64)
        control_hash = hashlib.sha256()
        for start in range(0,256**3,1 << 18):
            rgb = full_points[start:start+(1 << 18)]
            prediction = operator(rgb) if operator is not None else old_prediction[start:start+len(rgb)]
            control_hist += ea.histogram(prediction,full_truth[start:start+len(rgb)])[0]
            control_hash.update(prediction.tobytes())
        if control_hash.hexdigest() != expected:
            raise AssertionError("负对照重放输出不同")
        negative = fg.certify(domain_guard.reference,fg.summary(control_hist),config["mean_numerator"],config["mean_denominator"])
        negative.update(prediction_sha256=expected,provenance="PR15冻结流或版本化模型；本轮重新核对直方图与预算，不改历史结果")
        if negative["accepted"] or "mean" not in negative["failed"]:
            raise AssertionError("全域保护未拒绝已知0.61349%均值超预算模型")
        write_json(out / "negative-control.json",negative)
        print("负对照已因完整mean预算被拒绝，开始带全域保护的节点选择",flush=True)
    models, active, rounds = tr.clone(initial), np.empty(0, np.int64), []
    if plan.get("warm_start"):
        warm = ROOT / plan["warm_start"]
        old_selection = json.loads((warm / "selection.json").read_text(encoding="utf-8"))
        replayed = []
        for record in old_selection["rounds"]:
            for move in record["search"]["accepted"]:
                update = tr.Move(move["stage"]-1,move["node"],tuple(move["after_node"]))
                proof = domain_guard.consider(models,update)
                if not proof["accepted"]:
                    raise AssertionError("冻结前四步未通过同一全域预算，不能热启动")
                models[update.stage].nodes.reshape(-1,3)[update.node] = update.value
                domain_guard.commit(models,update)
                replayed.append(proof)
        for k,expected in enumerate(old_selection["model_sha256"]):
            if digest(warm / f"repaired-stage{k+1}.slut") != expected:
                raise ValueError("热启动冻结模型SHA不同")
            if not np.array_equal(models[k].nodes,io.load_sparse(warm / f"repaired-stage{k+1}.slut").nodes):
                raise AssertionError("热启动节点重放与冻结模型不同")
        old_domain = json.loads((warm / "full-domain.json").read_text(encoding="utf-8"))
        if domain_guard.report()["prediction_sha256"] != old_domain["prediction_sha256"]:
            raise AssertionError("热启动完整流与冻结单节点阶段不同")
        prior_points = json.loads((ROOT / "report/data/tail-repair-v1/training-violations.json").read_text(encoding="utf-8"))["records"]
        active = tr.encode(ea.neighbourhood(np.asarray([r["rgb"] for r in prior_points],np.uint8)))
        active = active[caps[active] != np.iinfo(np.uint32).max]
        write_json(out / "warm-start.json",{"replayed":replayed,"source":plan["warm_start"],"active_colours":len(active)})
    bad, initial_scan = scan(models, keys, caps, truth)
    print(f"完整训练颜色初始超限：{len(bad)}/{len(keys)}", flush=True)
    for iteration in range(plan["separation_rounds"]):
        if not len(bad):
            break
        nearby = tr.encode(ea.neighbourhood(tr.decode(bad)))
        nearby = nearby[caps[nearby] != np.iinfo(np.uint32).max]
        active = np.unique(np.concatenate((active, bad, nearby)))
        points = tr.decode(active)
        hard = {"points": points, "truth": ea.exact_chain(tables, points), "caps": caps[active]}
        models, detail = tr.repair(models, banks, hard, guards, limits,
            steps=plan["steps_per_round"], focus_count=plan["focus_count"], domain_guard=domain_guard)
        paired = None
        if plan.get("paired_search") and tr.State(models,hard["points"],hard["truth"],hard["caps"]).loss()[0] > 0:
            from lutlab import joint_tail_repair
            models,paired = joint_tail_repair.repair_pair(models,banks,hard,guards,limits,domain_guard,
                radius=plan["paired_search"]["radius"],helper_limit=plan["paired_search"]["helper_limit"])
        bad, separation = scan(models, keys, caps, truth)
        rounds.append({"round": iteration+1, "active_colours": len(active), "search": detail,
                       **({"paired_search":paired} if paired is not None else {}), "full_training_scan": separation})
        write_json(out / f"round{iteration+1}.json", rounds[-1])
        paired_count = len(paired["moves"]) if paired is not None and paired["accepted"] else 0
        print(f"约束分离第{iteration+1}轮：接受{len(detail['accepted'])}次单节点选择、{paired_count}个联合节点；剩余{len(bad)}个超限颜色", flush=True)
        if not detail["accepted"] and not (paired is not None and paired["accepted"]):
            break
    feasible = not len(bad)
    if domain_guard is not None:
        import psutil
        domain_result = domain_guard.report()
        memory = psutil.Process().memory_info()
        domain_result["host_memory"] = {"rss_snapshot": memory.rss, "os_peak_working_set": getattr(memory,"peak_wset",None),
            "scope": "整个离线研究进程，包含输入/Numba/缓存；无peak字段时仅为RSS快照，不是运行时内存"}
        if not domain_result["certificate"]["accepted"]:
            raise AssertionError("最后一轮模型的完整域证书不通过")
        write_json(out / "full-domain.json",domain_result)
    final_guards = {name: ea.metrics(ea.Operator(models)(spec["points"]), spec["truth"]) for name, spec in guards.items()}
    if any(value[key] > limits[name][key]+1e-12 for name, value in final_guards.items() for key in limits[name]):
        raise AssertionError("最终保护门禁不通过")
    paths = []
    for k, model in enumerate(models):
        if not all(np.array_equal(a, b) for a, b in zip(model.tables(), initial[k].tables())):
            raise AssertionError("修复改变了权威轴表")
        path = out / f"repaired-stage{k+1}.slut"
        io.save_sparse(path, model)
        paths.append(path)
    write_json(out / "selection.json", {"training_feasible": feasible, "initial_scan": initial_scan,
        "rounds": rounds, "final_guards": final_guards, "model_sha256": [digest(p) for p in paths],
        "limits": limits, "remaining_training_rgb": tr.decode(bad[:128]).tolist(),
        "scope": "全训练颜色证书与固定抽样门禁；在全色域/完整100图评价前冻结，无未知图片保证"})
    final = None
    if feasible:
        print("模型冻结，进入一次完整色域、完整100图与整数后端验收", flush=True)
        cube = cube_evaluate(tables, ea.Operator(models), out / "repaired.rgb", 128)
        if domain_guard is not None and cube["prediction_sha256"] != domain_result["prediction_sha256"]:
            raise AssertionError("冻结后的完整重建与增量全域缓存不同")
        parity = native_verify(models, out, cube["prediction_sha256"], args.executable)
        photos = photos_evaluate(tables, {"repaired": ea.Operator(models)})["repaired"]
        if cube["reference_sha256"] != previous["selected"]["cube"]["reference_sha256"]:
            raise AssertionError("最终完整参考流不同")
        final = {"cube": cube, "photos": photos, "native_parity": parity}
    write_json(out / "results.json", {"run_identity": metadata["identity_sha256"], "case": previous["case"],
        "references": references, "training_feasible": feasible, "initial_scan": initial_scan,
        "rounds": rounds, "final": final, "previous": {name: previous[name] for name in ("baseline", "selected")}})
    print(f"阶段结束：训练约束可行={feasible}", flush=True)


if __name__ == "__main__":
    main()
