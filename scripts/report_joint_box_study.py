"""精简归档联合拟合证据；仅整理冻结结果，不重新拟合或选型。"""
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
from lutlab import error_analysis as ea, interp, io, study_provenance


def digest(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def write_json(path, value):
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2, allow_nan=False)+"\n", encoding="utf-8", newline="\n")


def write_csv(path, rows):
    with path.open("w", encoding="utf-8", newline="") as stream:
        writer = csv.DictWriter(stream, list(rows[0]), lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


def photo_max_counterexamples(result, root, splits):
    """从已冻结的全色域流定位单图max回归，不重跑拟合或完整后端。"""
    manifest = json.loads((ROOT / "assets/photos/manifest.json").read_text(encoding="utf-8"))["images"]
    records = []
    for case in result["cases"]:
        cid = case["case"]["id"]
        regressions = [(a, b) for a, b in zip(case["baseline"]["photos"]["per_image"], case["selected"]["photos"]["per_image"])
                       if b["max"] > a["max"]+1e-12]
        if not regressions:
            continue
        new_path = root / cid / "selected.rgb"
        if digest(new_path) != case["selected"]["cube"]["prediction_sha256"]:
            raise ValueError("定位反例的冻结输出流哈希改变")
        new = np.memmap(new_path, dtype=np.uint8, mode="r", shape=(256**3, 3))
        tables = [io.load_full(ROOT / row["path"], mmap=True) for row in case["sources"]]
        chains = {"baseline": [io.load_sparse(root / cid / f"baseline-stage{k+1}.slut") for k in range(len(tables))],
                  "selected": [io.load_sparse(root / cid / f"selected-stage{k+1}.slut") for k in range(len(tables))]}
        for before, after in regressions:
            row = next(row for row in manifest if row["id"] == before["image"])
            path = ROOT / row["evaluation"]["path"]
            if digest(path) != row["evaluation"]["sha256"]:
                raise ValueError("反例照片文件改变")
            with Image.open(path) as image:
                points = np.asarray(image).reshape(-1, 3)
            indices = points.astype(np.int64) @ np.array([65536, 256, 1])
            truth = ea.exact_chain(tables, points)
            squared = np.sum((new[indices].astype(np.int32)-truth.astype(np.int32))**2, axis=1)
            at = int(np.argmax(squared))
            if np.sqrt(squared[at]) != after["max"]:
                raise AssertionError("冻结流中的单图max与已归档值不同")
            trace = {}
            for variant, models in chains.items():
                current, exact = points[at:at+1].copy(), points[at:at+1].copy()
                steps = []
                for table, model in zip(tables, models):
                    own = ea.source_apply(table, current)
                    prediction = interp.apply_tetra_q16(model, current)
                    reference = ea.source_apply(table, exact)
                    steps.append({"input": current[0].tolist(), "own_source": own[0].tolist(),
                                  "prediction": prediction[0].tolist(), "exact_prefix": reference[0].tolist()})
                    current, exact = prediction, reference
                trace[variant] = steps
            records.append({"case": cid, "image": before["image"], "split": next(name for name, ids in splits.items() if before["image"] in ids),
                "image_sha256": digest(path), "pixel_xy": [at % 1024, at // 1024], "rgb": points[at].tolist(),
                "rgb_bytes_sha256": hashlib.sha256(points[at].tobytes()).hexdigest(),
                "image_max_baseline": before["max"], "image_max_selected": after["max"],
                "baseline_at_rgb": trace["baseline"][-1]["prediction"], "selected_at_rgb": new[indices[at]].tolist(),
                "reference_at_rgb": truth[at].tolist(), "trace": trace})
    return {"records": records, "scope": "冻结输出定位最先出现的单图新max；未用这些已观察反例重新选型或调参"}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    out = args.output
    out.mkdir(parents=True, exist_ok=True)
    result = json.loads((args.input / "results.json").read_text(encoding="utf-8"))
    metadata = json.loads((args.input / "run.json").read_text(encoding="utf-8"))
    if metadata["identity_sha256"] != study_provenance.identity_digest(metadata["identity"]):
        raise ValueError("运行身份不完整")
    identity = metadata["identity"]
    for name, expected in {**identity["source_sha256"], **identity["stage_source_sha256"]}.items():
        if digest(ROOT / name) != expected:
            raise ValueError("归档时源文件与实际测量身份不同")
    if digest(ROOT / "experiments/joint-box-study-v1.json") != identity["plan_sha256"]:
        raise ValueError("冻结计划改变")
    for name in ("run.json", "results.json", "photo-partition.json", "sample-hashes.json"):
        shutil.copyfile(args.input / name, out / name)
    shutil.copyfile(ROOT / "experiments/joint-box-study-v1.json", out / "plan.json")
    shutil.copyfile(ROOT / "artifacts/joint-box-contract.log", out / "contract.log")
    shutil.copyfile(ROOT / "artifacts/joint-box-study-v1.log", out / "experiment.log")
    partition = json.loads((args.input / "photo-partition.json").read_text(encoding="utf-8"))
    splits = {"training": [r["id"] for r in partition["training"]["images"]],
              "guard": [r["id"] for r in partition["guard"]["images"]], "audit": partition["audit_ids"]}
    if len(set(sum(splits.values(), []))) != 100:
        raise AssertionError("照片分组重叠或缺少")
    summary, candidates, photos, split_rows, fit_rows, parity, members = [], [], [], [], [], [], []
    plt.rcParams.update({"font.family": "Microsoft YaHei", "axes.unicode_minus": False, "font.size": 10})
    fig, axes = plt.subplots(1, 3, figsize=(14, 4.5), constrained_layout=True)
    for ax, case in zip(axes, result["cases"]):
        cid, folder = case["case"]["id"], args.input / case["case"]["id"]
        receipt = json.loads((folder / "receipt.json").read_text(encoding="utf-8"))
        if any(digest(folder / name) != expected for name, expected in receipt.items()):
            raise ValueError("案例回执哈希不符")
        selection = json.loads((folder / "selection.json").read_text(encoding="utf-8"))
        baseline = next(row for row in selection["measurements"] if all(x == "baseline" for x in row["key"]))
        points_u, points_p = [], []
        for row in selection["measurements"]:
            failures = []
            for measure in ("uniform", "photo", "hotspot"):
                keys = ("mean", "rms", "p99", "max") + (("worst_image_mean", "worst_image_p99") if measure == "photo" else ())
                failures.extend(measure+"."+k for k in keys if row["metrics"][measure][k] > baseline["metrics"][measure][k]+1e-12)
            values = {"case": cid, "key": "|".join(row["key"]), "selected": row["key"] == selection["joint"]["winner"],
                      "eligible": row["key"] in selection["joint"]["eligible"], "regressions": "|".join(failures)}
            values.update({measure+"_"+k: row["metrics"][measure][k] for measure in ("uniform", "photo", "hotspot")
                           for k in ("mean", "rms", "p99", "max")})
            values.update({"photo_"+k: row["metrics"]["photo"][k] for k in ("worst_image_mean", "worst_image_p99")})
            candidates.append(values)
            points_u.append(row["metrics"]["uniform"]["mean"])
            points_p.append(row["metrics"]["photo"]["mean"])
        ax.scatter(points_u, points_p, s=22, alpha=.5, label="固定候选组合")
        ax.scatter([baseline["metrics"]["uniform"]["mean"]], [baseline["metrics"]["photo"]["mean"]], marker="*", s=130, color="black", label="基线")
        selected = next(row for row in selection["measurements"] if row["key"] == selection["joint"]["winner"])
        ax.scatter([selected["metrics"]["uniform"]["mean"]], [selected["metrics"]["photo"]["mean"]], marker="o", s=110, facecolors="none", edgecolors="#d1495b", label="门禁选择")
        ax.set(title=cid, xlabel="均匀选择色 mean", ylabel="照片选择像素 mean")
        ax.legend(fontsize=8)
        for variant in ("baseline", "selected"):
            value = case[variant]
            summary.append({"case": cid, "variant": variant, "choice": "|".join(selection["joint"]["winner"]) if variant == "selected" else "baseline",
                **{"cube_"+k: value["cube"][k] for k in ("mean", "rms", "p99", "max")},
                **{"photos_"+k: value["photos"][k] for k in ("mean", "rms", "worst_image_p99", "max")},
                "cube_provenance": "复用同字节基线" if variant == "baseline" or all(x == "baseline" for x in selection["joint"]["winner"]) else "本轮完整色域"})
            photos.extend({"case": cid, "variant": variant, "split": next(name for name, ids in splits.items() if row["image"] in ids), **row}
                          for row in value["photos"]["per_image"])
            for split, ids in splits.items():
                values = [row for row in value["photos"]["per_image"] if row["image"] in ids]
                split_rows.append({"case": cid, "variant": variant, "split": split, "n": len(values),
                    "mean": float(np.mean([r["mean"] for r in values])), "rms": float(np.sqrt(np.mean([r["rms"]**2 for r in values]))),
                    "worst_image_mean": max(r["mean"] for r in values), "worst_image_p99": max(r["p99"] for r in values), "max": max(r["max"] for r in values)})
        for k, value in enumerate(case["fit_details"]):
            fit_rows.append({"case": cid, "stage": k+1, "raw_outside": value["raw_components_outside_box"],
                "box_outside": value["box_components_outside_box"], "box_objective_change": value["continuous_box_vs_clamped_change"],
                "box_kkt": value["box_solver"]["scaled_projected_gradient_inf"],
                "irls_initial": value["irls"][0]["before"], "irls_final": value["irls"][-1]["after"],
                "irls_worst_kkt": max(r["solver"]["scaled_projected_gradient_inf"] for r in value["irls"])})
        native = case["native_parity"]
        if isinstance(native, list):
            parity.extend({"case": cid, "provenance": "本轮完整色域", **row} for row in native)
        else:
            # 原始字段保留完整历史回执；这里只列实际对应本轮保留基线的记录。
            parity.extend({"case": cid, "provenance": "历史同字节基线，非本轮重新执行", **row}
                          for row in native["reused_baseline"] if row["variant"] == "baseline")
        for path in sorted(folder.glob("*.slut")) + [folder / "selection.json", folder / "result.json", folder / "receipt.json"]:
            members.append((path, cid+"/"+path.name))
    fig.savefig(out / "guard-measures.png", dpi=160)
    plt.close(fig)
    for filename, rows in (("case-summary.csv", summary), ("candidate-guard.csv", candidates), ("photos-per-image.csv", photos),
                           ("photo-split-summary.csv", split_rows), ("fit-diagnostics.csv", fit_rows)):
        write_csv(out / filename, rows)
    write_json(out / "native-parity.json", parity)
    write_json(out / "photo-max-counterexamples.json", photo_max_counterexamples(result, args.input, splits))
    index = {name: digest(path) for path, name in members}
    with zipfile.ZipFile(out / "models-and-selection.zip", "w", zipfile.ZIP_DEFLATED) as archive:
        for path, name in members:
            archive.write(path, name)
    with zipfile.ZipFile(out / "models-and-selection.zip") as archive:
        if set(archive.namelist()) != set(index) or any(hashlib.sha256(archive.read(name)).hexdigest() != value for name, value in index.items()):
            raise AssertionError("ZIP成员字节核对失败")
    write_json(out / "archive-index.json", index)
    write_json(out / "integrity.json", {"run_identity": metadata["identity_sha256"],
        "cases": len(result["cases"]), "candidate_records": len(candidates), "photo_records": len(photos),
        "model_and_selection_members": len(index), "source_hash_verified": True,
        "photo_split_sizes": {name: len(ids) for name, ids in splits.items()},
        "files": {p.name: digest(p) for p in out.iterdir() if p.is_file() and p.name != "integrity.json"},
        "scope": "本轮原始字节、来源、分组及ZIP完整性；不替代数值正确性或泛化验证"})
    print(json.dumps({"cases": len(result["cases"]), "candidates": len(candidates), "photos": len(photos), "archive_members": len(index)}, ensure_ascii=False))


if __name__ == "__main__":
    main()
