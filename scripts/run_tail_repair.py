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
    metadata["identity_sha256"] = study_provenance.identity_digest(metadata["identity"])
    study_provenance.claim_run(out / "run.json", metadata)
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
    models, active, rounds = tr.clone(initial), np.empty(0, np.int64), []
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
            steps=plan["steps_per_round"], focus_count=plan["focus_count"])
        bad, separation = scan(models, keys, caps, truth)
        rounds.append({"round": iteration+1, "active_colours": len(active), "search": detail, "full_training_scan": separation})
        write_json(out / f"round{iteration+1}.json", rounds[-1])
        print(f"约束分离第{iteration+1}轮：接受{len(detail['accepted'])}次节点选择；剩余{len(bad)}个超限颜色", flush=True)
        if not detail["accepted"]:
            break
    feasible = not len(bad)
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
