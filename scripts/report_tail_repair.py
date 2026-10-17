"""整理冻结修复结果，保留逐图权衡和完整14色反例，不重新优化。"""
import argparse
import csv
import hashlib
import json
from pathlib import Path
import shutil
import sys
import zipfile

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "python"))
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
from PIL import Image
from lutlab import error_analysis as ea, interp, io, study_provenance, tail_repair as tr
from run_chain_error_study import fixed_points


def digest(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def write_json(path, value):
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2, allow_nan=False)+"\n", encoding="utf-8", newline="\n")


def write_csv(path, rows):
    with path.open("w", encoding="utf-8", newline="") as stream:
        writer = csv.DictWriter(stream, list(rows[0]), lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    out, source = args.output, args.input
    out.mkdir(parents=True, exist_ok=True)
    run = json.loads((source / "run.json").read_text(encoding="utf-8"))
    if run["identity_sha256"] != study_provenance.identity_digest(run["identity"]):
        raise ValueError("运行身份校验失败")
    identity = run["identity"]
    expected_sources = {name.replace("\\", "/"): value for name,value in
                        {**identity["source_sha256"], **identity["stage_source_sha256"]}.items()}
    with zipfile.ZipFile(source / "measured-source.zip") as archive:
        if set(archive.namelist()) != set(expected_sources) or any(hashlib.sha256(archive.read(name)).hexdigest() != h for name,h in expected_sources.items()):
            raise ValueError("实测源码快照与原始运行身份不同")
    current_differences = [name for name,h in expected_sources.items() if digest(ROOT / name) != h]
    parent_run = json.loads((ROOT / "report/data/joint-box-v1/run.json").read_text(encoding="utf-8"))
    if (identity["image_manifest"] != parent_run["identity"]["image_manifest"]
            or digest(ROOT / "assets/photos/manifest.json") != identity["image_manifest"]):
        raise ValueError("本轮图片清单与复用逐图上限的旧清单不同")
    shutil.copyfile(source / "measured-source.zip", out / "measured-source.zip")
    write_json(out / "source-provenance.json", {"measured_git_commit": run["git_commit"],
        "measured_source_sha256": expected_sources, "current_files_different_from_measurement": current_differences,
        "scope": "快照逐文件匹配实测身份；当前后续前置检查修补与实测版本分开记录，不重标旧运行来源"})
    if digest(ROOT / "experiments/tail-repair-v1.json") != identity["plan_sha256"]:
        raise ValueError("冻结计划字节不同")
    result = json.loads((source / "results.json").read_text(encoding="utf-8"))
    if result["final"] is None:
        raise ValueError("本次局部搜索未可行，不能生成成功验收报告；原始失败结果仍保留")
    parent = ROOT / "report/data/joint-box-v1"
    partition = json.loads((parent / "photo-partition.json").read_text(encoding="utf-8"))
    splits = {"training": [r["id"] for r in partition["training"]["images"]],
              "guard": [r["id"] for r in partition["guard"]["images"]], "audit": partition["audit_ids"]}
    variants = {"baseline": result["previous"]["baseline"], "joint": result["previous"]["selected"], "repaired": result["final"]}
    summary, photos, grouped, moves = [], [], [], []
    for name, value in variants.items():
        summary.append({"variant": name, **{"cube_"+k: value["cube"][k] for k in ("mean", "rms", "p99", "max")},
            **{"photos_"+k: value["photos"][k] for k in ("mean", "rms", "worst_image_p99", "max")},
            "scope": "本轮完整验收" if name == "repaired" else "复用同字节模型及输入的历史结果"})
        for row in value["photos"]["per_image"]:
            photos.append({"variant": name, "split": next(k for k, ids in splits.items() if row["image"] in ids), **row})
        for split, ids in splits.items():
            values = [r for r in value["photos"]["per_image"] if r["image"] in ids]
            grouped.append({"variant": name, "split": split, "n": len(values), "mean": float(np.mean([r["mean"] for r in values])),
                "rms": float(np.sqrt(np.mean([r["rms"]**2 for r in values]))), "worst_image_mean": max(r["mean"] for r in values),
                "worst_image_p99": max(r["p99"] for r in values), "max": max(r["max"] for r in values)})
    comparison = {}
    for reference in ("baseline", "joint"):
        old, new = variants[reference]["photos"]["per_image"], variants["repaired"]["photos"]["per_image"]
        comparison[reference] = {k: {"better": sum(a[k] > b[k]+1e-12 for a,b in zip(old,new)),
            "equal": sum(abs(a[k]-b[k]) <= 1e-12 for a,b in zip(old,new)), "worse": sum(a[k] < b[k]-1e-12 for a,b in zip(old,new))}
            for k in ("mean", "rms", "p99", "max")}
    comparison["full_cube_mean_increase_vs_joint_percent"] = 100*(variants["repaired"]["cube"]["mean"]/variants["joint"]["cube"]["mean"]-1)
    comparison["photos_mean_increase_vs_joint_percent"] = 100*(variants["repaired"]["photos"]["mean"]/variants["joint"]["photos"]["mean"]-1)
    comparison["scope"] = "0.5%只约束预先冻结的抽样集合，完整色域增幅可能超过该值；不隐去权衡"
    write_json(out / "comparisons.json", comparison)
    for record in result["rounds"]:
        for move in record["search"]["accepted"]:
            moves.append({"round": record["round"], "step": move["step"], "stage": move["stage"], "node": move["node"],
                "before": str(move["before_node"]), "after": str(move["after_node"]),
                "excess_before": move["before_loss"][0], "excess_after": move["after_loss"][0],
                "violations_before": move["before_loss"][2], "violations_after": move["after_loss"][2]})
    for filename, values in (("case-summary.csv", summary), ("photos-per-image.csv", photos),
                              ("photo-split-summary.csv", grouped), ("node-moves.csv", moves)):
        write_csv(out / filename, values)
    for path in [source / name for name in ("run.json", "results.json", "inventory.json", "selection.json", "fixed-guards.json")] + sorted(source.glob("round*.json")):
        shutil.copyfile(path, out / path.name)
    for name, path in (("plan.json", ROOT / "experiments/tail-repair-v1.json"), ("contract.log", ROOT / "artifacts/tail-repair-contract.log"),
                       ("preflight-contract.log", ROOT / "artifacts/tail-repair-preflight.log"),
                       ("experiment.log", ROOT / "artifacts/tail-repair-v1.log")):
        shutil.copyfile(path, out / name)
    write_json(out / "native-parity.json", result["final"]["native_parity"])
    initial = [io.load_sparse(source / "input-models" / f"selected-stage{k+1}.slut") for k in range(4)]
    repaired = [io.load_sparse(source / f"repaired-stage{k+1}.slut") for k in range(4)]
    models = {"input_archive": "report/data/joint-box-v1/models-and-selection.zip", "input_archive_sha256": digest(parent / "models-and-selection.zip"),
        "input_models": {p.name: digest(p) for p in (source / "input-models").glob("*.slut")},
        "repaired_models": {f"repaired-stage{k+1}.slut": digest(source / f"repaired-stage{k+1}.slut") for k in range(4)},
        "changed_node_components": [int(np.count_nonzero(a.nodes != b.nodes)) for a,b in zip(initial,repaired)],
        "unchanged_axis_tables": all(all(np.array_equal(x,y) for x,y in zip(a.tables(),b.tables())) for a,b in zip(initial,repaired))}
    write_json(out / "model-provenance.json", models)
    # 依据旧逐图完整记录，初始超限颜色必在原四张回归图中；只定位反例，不重新选型。
    manifest = {r["id"]: r for r in json.loads((ROOT / "assets/photos/manifest.json").read_text(encoding="utf-8"))["images"]}
    tables = [io.load_full(ROOT / r["path"], mmap=True) for r in result["references"]]
    examples = {}
    for old, current in zip(variants["baseline"]["photos"]["per_image"], variants["joint"]["photos"]["per_image"]):
        if current["max"] <= old["max"]+1e-12:
            continue
        row = manifest[old["image"]]
        path = ROOT / row["evaluation"]["path"]
        if digest(path) != row["evaluation"]["sha256"]:
            raise ValueError("反例照片哈希不同")
        with Image.open(path) as image:
            points = np.unique(np.asarray(image).reshape(-1, 3), axis=0)
        truth = ea.exact_chain(tables, points)
        prediction = ea.Operator(initial)(points)
        squared = np.sum((prediction.astype(np.int32)-truth.astype(np.int32))**2, axis=1)
        cap = int(round(old["max"]**2))
        for rgb, target, value in zip(points[squared > cap], truth[squared > cap], squared[squared > cap]):
            key = tuple(map(int, rgb))
            if key not in examples:
                examples[key] = {"rgb": list(key), "reference": target.tolist(), "initial_squared_error": int(value), "cap_squared": cap, "images": []}
            examples[key]["cap_squared"] = min(examples[key]["cap_squared"], cap)
            examples[key]["images"].append(old["image"])
    example_rows = [examples[key] for key in sorted(examples)]
    if len(example_rows) != result["initial_scan"]["violating_colours"]:
        raise AssertionError("完整14色反例数量与训练全域分离不符")
    rgb = np.array([r["rgb"] for r in example_rows], np.uint8)
    prediction = rgb.copy()
    for model in repaired:
        prediction = interp.apply_tetra_q16(model, prediction)
    for row, value in zip(example_rows, prediction):
        delta = value.astype(np.int32)-np.array(row["reference"], np.int32)
        row.update(repaired_rgb=value.tolist(), repaired_squared_error=int(delta@delta))
        if row["repaired_squared_error"] > row["cap_squared"]:
            raise AssertionError("冻结反例未被修复")
    write_json(out / "training-violations.json", {"records": example_rows,
        "rgb_bytes_sha256": hashlib.sha256(rgb.tobytes()).hexdigest(), "scope": "全部14个初始训练超限颜色，参考原四图完整记录与训练全域扫描互相核对"})
    # 重放已冻结的5步，量化共享节点对已有均匀保护颜色的波及；不产生新候选。
    plan = json.loads((out / "plan.json").read_text(encoding="utf-8"))
    uniform = fixed_points(plan["uniform"], [])
    fixed = json.loads((source / "fixed-guards.json").read_text(encoding="utf-8"))
    if hashlib.sha256(uniform.tobytes()).hexdigest() != fixed["before"]["uniform"]["input_sha256"]:
        raise AssertionError("节点影响分析的颜色输入不同")
    current = tr.clone(initial)
    uniform_truth = ea.exact_chain(tables, uniform)
    footprint = []
    for round_record in result["rounds"]:
        for record in round_record["search"]["accepted"]:
            state = tr.State(current, uniform, uniform_truth)
            move = tr.Move(record["stage"]-1, record["node"], tuple(record["after_node"]))
            indices, output, squared = state.trial(move)
            after = state.trial_metrics(indices, squared)
            if after != record["guards"]["uniform"]:
                raise AssertionError("冻结节点试探的均匀指标重放不同")
            footprint.append({"stage": record["stage"], "node": record["node"], "uniform_colours": len(uniform),
                "positive_support": len(indices), "changed_final_rgb": int(np.count_nonzero(np.any(output != state.prediction[indices], axis=1))),
                "mean_before": state.metrics["mean"], "mean_after": after["mean"], "max_after": after["max"]})
            current[move.stage].nodes.reshape(-1, 3)[move.node] = move.value
    if any(not np.array_equal(a.nodes,b.nodes) for a,b in zip(current,repaired)):
        raise AssertionError("冻结5步重放与最终模型不同")
    write_json(out / "move-footprint.json", {"records": footprint,
        "scope": "同一65536色选择集上的冻结节点重放；不是额外优化、完整色域归因或性能测试"})
    plt.rcParams.update({"font.family": "Microsoft YaHei", "axes.unicode_minus": False, "font.size": 9})
    fig, axes = plt.subplots(1, 2, figsize=(13.5, 5.1), constrained_layout=True)
    x = np.arange(len(example_rows))
    axes[0].bar(x-.2, [np.sqrt(r["initial_squared_error"]) for r in example_rows], width=.4, label="联合模型")
    axes[0].bar(x+.2, [np.sqrt(r["repaired_squared_error"]) for r in example_rows], width=.4, label="局部修复")
    axes[0].scatter(x, [np.sqrt(r["cap_squared"]) for r in example_rows], marker="_", s=130, color="black", label="原逐图上限")
    axes[0].set(xticks=x, xticklabels=[str(r["rgb"]) for r in example_rows], ylabel="RGB 欧氏距离", title="全部14个初始超限颜色")
    axes[0].tick_params(axis="x", labelrotation=85)
    axes[0].legend()
    old = {r["image"]: r for r in variants["baseline"]["photos"]["per_image"]}
    new = {r["image"]: r for r in variants["repaired"]["photos"]["per_image"]}
    for name, ids in splits.items():
        axes[1].scatter([old[i]["max"] for i in ids], [new[i]["max"] for i in ids], alpha=.6, s=30, label={"training":"训练60图", "guard":"选择20图", "audit":"历史审计20图"}[name])
    axes[1].plot([0, 10], [0, 10], "--", color="gray")
    axes[1].set(xlabel="原始基线单图max", ylabel="修复后单图max", title="完整100图均低于原始基线（非盲测）")
    axes[1].legend()
    fig.savefig(out / "tail-repair.png", dpi=160)
    plt.close(fig)
    members = [(source / f"repaired-stage{k+1}.slut", f"repaired-stage{k+1}.slut") for k in range(4)]
    members += [(out / name, name) for name in ("selection.json", "model-provenance.json", "training-violations.json")]
    archive_index = {name: digest(path) for path,name in members}
    with zipfile.ZipFile(out / "models-and-counterexamples.zip", "w", zipfile.ZIP_DEFLATED) as archive:
        for path,name in members:
            archive.write(path, name)
    with zipfile.ZipFile(out / "models-and-counterexamples.zip") as archive:
        if any(hashlib.sha256(archive.read(name)).hexdigest() != expected for name,expected in archive_index.items()):
            raise AssertionError("归档ZIP成员哈希不同")
    write_json(out / "archive-index.json", archive_index)
    write_json(out / "integrity.json", {"run_identity": run["identity_sha256"], "source_hash_verified": True,
        "photo_records": len(photos), "counterexample_colours": len(example_rows), "archive_members": len(members),
        "files": {p.name: digest(p) for p in out.iterdir() if p.is_file() and p.name != "integrity.json"},
        "scope": "冻结结果和来源完整性；不替代运行时正确性或泛化证明"})
    print(json.dumps({"photos": len(photos), "counterexample_colours": len(example_rows), "moves": len(moves), "archive_members": len(members)}, ensure_ascii=False))


if __name__ == "__main__":
    main()
