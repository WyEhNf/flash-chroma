"""整理冻结误差实验的指标、反例、模型和科学图；不重新拟合或测速。"""
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
from lutlab import error_analysis as ea, io


def write_json(path, value):
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2, allow_nan=False) + "\n", encoding="utf-8", newline="\n")


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
    out = args.output
    out.mkdir(parents=True, exist_ok=True)
    study = json.loads((args.input / "results.json").read_text(encoding="utf-8"))
    explanations = json.loads((args.input / "explanations-with-parity.json").read_text(encoding="utf-8"))
    by_case = {r["case"]: r for r in explanations["cases"]}
    write_json(out / "results.json", study)
    write_json(out / "explanations.json", explanations)
    shutil.copyfile(args.input / "run.json", out / "environment.json")
    shutil.copyfile(ROOT / "experiments/chain-error-study-v1.json", out / "plan.json")
    summary, stages, candidates, photos, parity, archive = [], [], [], [], [], []
    for case in study["cases"]:
        cid = case["case"]["id"]
        folder = args.input / cid
        for variant, record in case["final"].items():
            summary.append({"case": cid, "stages": len(case["sources"]), "variant": variant,
                **{"cube_"+k: record["cube"][k] for k in ("mean", "rms", "p99", "max", "cvar_1pct", "fraction_ge_1", "fraction_ge_2", "fraction_ge_3", "fraction_ge_5")},
                **{"photos_"+k: record["photos"][k] for k in ("mean", "rms", "worst_image_p99", "max")}})
            photos.extend({"case": cid, "variant": variant, **row} for row in record["photos"]["per_image"])
        for row in case["attribution"]["stages"]:
            stages.append({"case": cid, "stage": row["stage"],
                **{k: row[k] for k in ("sse_local", "sse_propagated", "sse_interaction", "sse_total", "replacement_gain_mean", "replacement_gain_cvar")}})
        for name, value in case["candidate_measurements"].items():
            candidates.append({"case": cid, "variant": name, "selected_stage": case["selected_stage"],
                "guard_eligible": value["guard_eligible"], "selected": name == case["winner"],
                **{"guard_"+k: value["guard"][k] for k in ("mean", "rms", "p99", "max")},
                "stage_sha256": value["stage_sha256"]})
        parity.extend({"case": cid, **row} for row in case["native_parity"])
        parity.extend({"case": cid, "variant": "existing_control", **row} for row in by_case[cid]["control_native_parity"])
        model_paths = sorted(folder.glob("*.slut"))
        rgb = np.asarray([r["rgb"] for r in case["final"]["baseline"]["cube"]["hotspots"]], np.uint8)
        frame = np.repeat(np.repeat(rgb.reshape(8, 16, 3), 96, axis=0), 64, axis=1)
        tables = [io.load_full(ROOT / r["path"].replace("\\", "/"), mmap=True) for r in case["sources"]]
        base = [io.load_sparse(folder / f"baseline-stage{k+1}.slut") for k in range(len(tables))]
        selected = [io.load_sparse(folder / f"{case['winner']}-native-stage{k+1}.slut") for k in range(len(tables))]
        images = {"input": frame, "reference": ea.exact_chain(tables, frame.reshape(-1, 3)).reshape(frame.shape),
            "baseline": ea.Operator(base)(frame.reshape(-1, 3)).reshape(frame.shape),
            "selected": ea.Operator(selected)(frame.reshape(-1, 3)).reshape(frame.shape)}
        image_paths = []
        for label, data in images.items():
            path = folder / f"hotspots-{label}.png"
            Image.fromarray(data).save(path)
            image_paths.append(path)
        for path in model_paths + image_paths + [folder / "selection.json"]:
            archive.append((path, f"{cid}/{path.name}"))
    write_csv(out / "case-summary.csv", summary)
    write_csv(out / "stage-attribution.csv", stages)
    write_csv(out / "candidate-guard.csv", candidates)
    write_csv(out / "photos-per-image.csv", photos)
    write_json(out / "native-parity.json", parity)
    archive_index = {name: hashlib.sha256(path.read_bytes()).hexdigest() for path, name in archive}
    with zipfile.ZipFile(out / "models-and-counterexamples.zip", "w", compression=zipfile.ZIP_DEFLATED) as bundle:
        for path, name in archive:
            bundle.write(path, name)
    write_json(out / "archive-index.json", archive_index)
    plt.rcParams.update({"font.family": "Microsoft YaHei", "axes.unicode_minus": False, "font.size": 10})
    chains = [case for case in study["cases"] if len(case["sources"]) == 4]
    fig, axes = plt.subplots(2, 2, figsize=(12, 7.5), constrained_layout=True)
    for row_index, case in enumerate(chains):
        positions = np.arange(4)
        rows = case["attribution"]["stages"]
        for offset, key, label in ((-.24, "local_own_lut_error", "本级拟合"),
                                  (0, "propagated_input_error", "传入偏差经当前原表"),
                                  (.24, "total_prefix_error", "实际总误差")):
            axes[row_index, 0].bar(positions + offset, [r[key]["rms"] for r in rows], width=.24, label=label)
        axes[row_index, 0].set(xticks=positions, xticklabels=["第1级", "第2级", "第3级", "第4级"],
            ylabel="RGB 距离 RMS", title=case["case"]["id"]+"：误差分解（范数不可相加）")
        axes[row_index, 0].legend(fontsize=8)
        allocation = by_case[case["case"]["id"]]["mse_shapley_allocation"]
        axes[row_index, 1].bar(positions, allocation, color=["#2e7d76" if x >= 0 else "#bd4b45" for x in allocation])
        axes[row_index, 1].axhline(0, color="black", linewidth=.7)
        axes[row_index, 1].set(xticks=positions, xticklabels=["第1级", "第2级", "第3级", "第4级"],
            ylabel="MSE 干预分配", title="全部16种精确/稀疏干预；负值表示抵消")
    fig.savefig(out / "stage-error-attribution.png", dpi=160)
    plt.close(fig)
    fig, axes = plt.subplots(2, 3, figsize=(12, 7), constrained_layout=True)
    for row_index, case in enumerate(study["cases"][:2]):
        cid = case["case"]["id"]
        folder = args.input / cid
        fixed_b = case["final"]["baseline"]["cube"]["hotspots"][0]["rgb"][2]
        r, g = np.meshgrid(np.arange(256), np.arange(256))
        points = np.stack((r.ravel(), g.ravel(), np.full(256**2, fixed_b)), axis=1).astype(np.uint8)
        table = io.load_full(ROOT / case["sources"][0]["path"].replace("\\", "/"), mmap=True)
        truth = ea.source_apply(table, points)
        base = io.load_sparse(folder / "baseline-stage1.slut")
        chosen = io.load_sparse(folder / f"{case['winner']}-native-stage1.slut")
        errors = [np.linalg.norm(ea.Operator([model])(points).astype(float)-truth, axis=1).reshape(256,256)
                  for model in (base, chosen)]
        for column in range(2):
            drawing = axes[row_index, column].imshow(errors[column], origin="lower", vmin=0, vmax=max(float(errors[0].max()), 1), cmap="magma")
            axes[row_index, column].set(title=f"{cid} / {'基线' if column == 0 else '选中候选'} / B={fixed_b}", xlabel="输入 R", ylabel="输入 G")
            fig.colorbar(drawing, ax=axes[row_index, column], label="RGB 距离")
        drawing = axes[row_index, 2].imshow(truth[:,2].reshape(256,256), origin="lower", vmin=0, vmax=255, cmap="viridis")
        axes[row_index, 2].set(title="原始完整参考的 B 输出", xlabel="输入 R", ylabel="输入 G")
        fig.colorbar(drawing, ax=axes[row_index, 2], label="RGB8 码值")
    fig.savefig(out / "hotspot-slices.png", dpi=160)
    plt.close(fig)
    print(json.dumps({"cases": len(study["cases"]), "summary_rows": len(summary), "candidate_rows": len(candidates),
        "photo_rows": len(photos), "native_streams": len(parity), "archived_files": len(archive)}, ensure_ascii=False))


if __name__ == "__main__":
    main()
