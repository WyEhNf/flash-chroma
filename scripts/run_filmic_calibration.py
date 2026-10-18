"""单独重建Filmic冻结基线、解析校准坐标，并按固定触发执行一次集中验收。"""
from __future__ import annotations

import os
for _name in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS"):
    os.environ[_name] = "1"
os.environ["PYTHONDONTWRITEBYTECODE"] = "1"
import argparse
import csv
import hashlib
import json
from pathlib import Path
import subprocess
import sys
import time
import zipfile

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "python"))
import numba
import numpy as np
from PIL import Image
from lutlab import curve, error_analysis as ea, fit, io, runtime, source_lut, study_provenance
from lutlab.compatibility import write_json


def read(path):
    return json.loads(Path(path).read_text(encoding="utf-8"))


def digest(path):
    with Path(path).open("rb") as stream:
        return hashlib.file_digest(stream, "sha256").hexdigest()


def checked(spec):
    path = ROOT / spec["path"]
    if digest(path) != spec["sha256"]:
        raise ValueError(f"文件SHA不同：{path}")
    return path


def rgb_keys(rgb):
    return np.asarray(rgb, np.int64) @ np.array([65536, 256, 1], np.int64)


def colours(ids):
    return np.column_stack((ids >> 16, (ids >> 8) & 255, ids & 255)).astype(np.uint8)


def numerical_sources(plan_path):
    names = ["fit.py", "curve.py", "source_lut.py", "io.py", "interp.py", "study_kernels.py",
             "error_analysis.py", "runtime.py", "study_provenance.py", "compatibility.py",
             "separable_calibration.py"]
    files = [ROOT / "python/lutlab" / name for name in names] + [Path(__file__), plan_path]
    return {str(path.relative_to(ROOT)).replace("\\", "/"): digest(path) for path in files}


def integer_oracle(model, rgb):
    """独立比较器排序与u64节点累加，不调用interp的权重构造。"""
    idx, frac = model.tables()
    xyz = rgb.astype(np.int64)
    base = ((idx[0, xyz[:, 0]].astype(np.int64)*model.m
             + idx[1, xyz[:, 1]])*model.m + idx[2, xyz[:, 2]])
    fractions = np.column_stack([frac[a, xyz[:, a]] for a in range(3)]).astype(np.int64)
    strides = np.tile(np.array([model.m**2, model.m, 1], np.int64), (len(rgb), 1))
    for left, right in ((0, 1), (1, 2), (0, 1)):
        swap = fractions[:, left] < fractions[:, right]
        fractions[swap, left], fractions[swap, right] = fractions[swap, right].copy(), fractions[swap, left].copy()
        strides[swap, left], strides[swap, right] = strides[swap, right].copy(), strides[swap, left].copy()
    f1, f2, f3 = fractions.T
    weights = np.column_stack((io.ONE-f1, f1-f2, f2-f3, f3)).astype(np.uint64)
    indices = np.column_stack((base, base+strides[:, 0], base+strides[:, :2].sum(axis=1),
                               base+model.m**2+model.m+1))
    nodes = model.nodes.reshape(-1, 3).astype(np.uint64)
    return ((np.sum(nodes[indices]*weights[:, :, None], axis=1, dtype=np.uint64)+io.ONE//2) >> io.Q).astype(np.uint8)


def curve_output(model):
    from lutlab import separable_calibration as sc
    nodes = sc.diagonal_node_curves(model)
    idx, frac = model.tables()
    return np.stack([sc.evaluate_curve(nodes[:, a], idx[a], frac[a]) for a in range(3)], axis=1)


def contracts(models, calibrated, reference_curves):
    """只集中覆盖解析风险；完整输入另由accept负责。"""
    from lutlab import separable_calibration as sc
    tested = 0
    f = np.arange(io.ONE+1, dtype=np.int64)
    for a, b in ((0, 255), (255, 0), (0, 1), (1, 0), (17, 17), (127, 129)):
        outputs = (a*(io.ONE-f)+b*f+io.ONE//2) >> io.Q
        for target in (0, 1, 17, 127, 128, 129, 254, 255):
            lo, hi = sc.rounding_interval(a, b, target)
            predicted = (f >= lo) & (f <= hi)
            if not np.array_equal(predicted, outputs == target):
                raise AssertionError("解析区间与独立全Q16枚举不同")
            tested += 1
    rng = np.random.default_rng(2026101908)
    probes = rng.integers(0, 256, size=(2048, 3), dtype=np.uint8)
    probes = np.concatenate((probes, np.column_stack([np.arange(256, dtype=np.uint8)]*3),
                             np.array([[r, g, b] for r in (0, 255) for g in (0, 255) for b in (0, 255)], np.uint8)))
    model_checks = []
    for size, old in models.items():
        new = calibrated[size]
        if (not np.array_equal(old.nodes, new.nodes) or not np.array_equal(old.grid, new.grid)
                or not np.array_equal(old.tables()[0], new.tables()[0])):
            raise AssertionError("校准改变了固定节点、网格或idx")
        for name, model in (("baseline", old), ("calibrated", new)):
            output = ea.Operator([model])(probes)
            values = curve_output(model)
            closed = np.column_stack([values[probes[:, a], a] for a in range(3)])
            np.testing.assert_array_equal(output, integer_oracle(model, probes))
            np.testing.assert_array_equal(output, closed)
            io.validate_sparse(model, competition=True)
            model_checks.append({"m": size, "variant": name, "pixels": len(probes)})
        if np.any(np.abs(curve_output(new).astype(np.int16)-reference_curves.astype(np.int16))
                  > np.abs(curve_output(old).astype(np.int16)-reference_curves.astype(np.int16))):
            raise AssertionError("逐码最小误差不应劣于保留原frac")
    return {"passed": 3, "interval_cases": tested, "model_checks": model_checks,
            "scope": "独立Q16区间枚举、固定字段/单调证书与RGB整数oracle集中合同；非完整色域/百图"}


def prepare(args, plan):
    from lutlab import separable_calibration as sc
    if args.output.exists():
        raise ValueError("不覆盖已有研究目录")
    checked(plan["source"])
    executable = checked(plan["executable"])
    manifest = checked({"path": plan["photos"]["manifest"], "sha256": plan["photos"]["manifest_sha256"]})
    source_hashes = numerical_sources(args.plan)
    identity = {"plan": plan, "source_sha256": source_hashes,
                "environment": study_provenance.environment_fingerprint(),
                "git_commit": subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=ROOT, text=True).strip(),
                "numba_threads": numba.get_num_threads()}
    study_provenance.claim_run(args.output / "run.json",
        {"identity": identity, "identity_sha256": study_provenance.identity_digest(identity)})
    with zipfile.ZipFile(args.output / "measured-source.zip", "w", zipfile.ZIP_DEFLATED) as archive:
        for name, sha in source_hashes.items():
            if digest(ROOT/name) != sha:
                raise ValueError("冻结源码期间文件改变")
            archive.write(ROOT/name, name)
    # 重建只沿用同一源解释；不尝试多个解释来匹配目标SHA。
    reference, policy = source_lut.bake_source(ROOT/plan["source"]["path"], plan["source"])
    reference_path = args.output/"reference.npy"
    np.save(reference_path, reference)
    channels = curve.separable_channels(reference)
    if channels is None or [axis for axis, _ in channels] != [0, 1, 2]:
        raise ValueError("本阶段只研究经完整验证的同轴可分离Filmic")
    source_curves = np.stack([values for _, values in channels], axis=1)
    np.save(args.output/"source-curves.npy", source_curves)
    expected_reference = plan["historical_reference_file_sha256"]
    records, originals, calibrated = {}, {}, {}
    for size in plan["rebuild"]["sizes"]:
        folder = args.output/f"m{size}"
        folder.mkdir()
        grid_info, node_info = {}, {}
        grid = fit.adaptive_dp_grid(reference, size, probes=plan["rebuild"]["probes"], diagnostics=grid_info)
        nodes = fit.fit_structured_tetra(reference, grid, diagnostics=node_info, general_method="supported")
        if node_info["route"] != plan["rebuild"]["required_route"]:
            raise ValueError("实际拟合分派没有验证为可分离整数DP")
        old = io.SparseLut(grid, nodes)
        old_path = folder/"baseline.slut"
        io.save_sparse(old_path, old)
        old = io.load_sparse(old_path, competition=True)
        new, diagnostic = sc.calibrate(old, source_curves, maximum_shift=plan["calibration"]["maximum_shift"])
        new_path = folder/"calibrated.slut"
        io.save_sparse(new_path, new)
        new = io.load_sparse(new_path, competition=True)
        originals[size], calibrated[size] = old, new
        analytical = {name: sc.cube_metrics(curve_output(model), source_curves)
                      for name, model in (("baseline", old), ("calibrated", new))}
        baseline_sha = digest(old_path)
        match = baseline_sha == plan["historical_models"][str(size)]
        full_eligible = (analytical["calibrated"]["mean"] <= .97*analytical["baseline"]["mean"]
                         and all(analytical["calibrated"][k] <= analytical["baseline"][k]+1e-12
                                 for k in ("rms", "p99", "max")))
        write_json(folder/"analysis.json", diagnostic)
        write_json(folder/"rebuild.json", {"grid": grid_info, "nodes": node_info})
        records[str(size)] = {"baseline_sha256": baseline_sha, "calibrated_sha256": digest(new_path),
            "historical_model_sha256": plan["historical_models"][str(size)], "historical_model_matches": match,
            "baseline_status": "PR41同字节模型" if match else "当前环境重建受控基线；非PR41冻结模型",
            "analytic_cube": analytical, "diagnostic_file_sha256": digest(folder/"analysis.json"),
            "full_eligible": bool(full_eligible)}
        print(json.dumps({"m": size, "historical_sha_matches": match, "analytic": analytical,
                          "full_eligible": bool(full_eligible),
                          "remaining_code_errors": diagnostic["remaining_code_errors"]}, ensure_ascii=False), flush=True)
    verification = contracts(originals, calibrated, source_curves)
    result = {"run_identity": study_provenance.identity_digest(identity), "source_policy": policy,
        "reference_file_sha256": digest(reference_path),
        "historical_reference_matches": digest(reference_path) == expected_reference,
        "reference_raw_sha256": hashlib.sha256(reference.tobytes()).hexdigest(),
        "source_curves_file_sha256": digest(args.output/"source-curves.npy"),
        "photo_manifest_sha256": digest(manifest), "capabilities": runtime.capabilities(executable=executable),
        "contracts": verification, "sizes": records, "full_evaluation_performed": False}
    write_json(args.output/"preparation.json", result)
    print(json.dumps({"contracts": verification, "reference_matches": result["historical_reference_matches"],
                      "scope": "解析与集中合同结束；尚未执行完整验收"}, ensure_ascii=False), flush=True)


def full_cube(model, reference, destination):
    hist = np.zeros(3*255**2+1, np.int64)
    h = hashlib.sha256()
    values, operator = curve_output(model), ea.Operator([model])
    with destination.open("wb") as stream:
        for start in range(0, 256**3, 1 << 18):
            rgb = colours(np.arange(start, start+(1 << 18), dtype=np.int64))
            output = operator(rgb)
            np.testing.assert_array_equal(output, integer_oracle(model, rgb))
            np.testing.assert_array_equal(output, np.column_stack([values[rgb[:, a], a] for a in range(3)]))
            block = reference.reshape(-1, 3)[start:start+len(rgb)]
            hist += ea.histogram(output, block)[0]
            stream.write(output.tobytes())
            h.update(output.tobytes())
    return {**ea.hist_metrics(hist), "prediction_sha256": h.hexdigest(),
            "independent_integer_mismatches": 0, "separable_formula_mismatches": 0}


def accept(args, plan):
    run, prepared = read(args.output/"run.json"), read(args.output/"preparation.json")
    if (run["identity_sha256"] != study_provenance.identity_digest(run["identity"])
            or prepared["run_identity"] != run["identity_sha256"]
            or numerical_sources(args.plan) != run["identity"]["source_sha256"]
            or (args.output/"full-results.json").exists()):
        raise ValueError("来源不同或已有完整结果，拒绝重复验收")
    executable = checked(plan["executable"])
    checked(plan["source"])
    checked({"path": plan["photos"]["manifest"], "sha256": plan["photos"]["manifest_sha256"]})
    if digest(args.output/"reference.npy") != prepared["reference_file_sha256"]:
        raise ValueError("完整参考改变")
    reference = np.load(args.output/"reference.npy", mmap_mode="r")
    rows = read(ROOT/plan["photos"]["manifest"])["images"]
    if len(rows) != plan["photos"]["count"]:
        raise ValueError("照片数不是冻结100张")
    listing = args.output/"photos.txt"
    listing.write_text("\n".join(str(ROOT/row["evaluation"]["path"]) for row in rows)+"\n", encoding="utf-8")
    kernels = [k for k in prepared["capabilities"]["available_kernels"]
               if k.startswith("tetra_") and k not in ("tetra_c99", "tetra_structured_avx2")]
    if not {"tetra_scalar", "tetra_avx2"}.issubset(kernels):
        raise ValueError("缺少计划要求的标量/AVX2")
    model_records, loaded = {}, {}
    for size, record in prepared["sizes"].items():
        if not record["full_eligible"]:
            continue
        folder = args.output/f"m{size}"
        model_records[size] = {}
        loaded[size] = {}
        for variant in ("baseline", "calibrated"):
            path = folder/f"{variant}.slut"
            if digest(path) != record[f"{variant}_sha256"]:
                raise ValueError("冻结模型改变")
            model = io.load_sparse(path, competition=True)
            loaded[size][variant] = model
            cube_path = folder/f"{variant}-cube.rgb"
            cube = full_cube(model, reference, cube_path)
            expected = record["analytic_cube"][variant]
            if any(abs(cube[k]-expected[k]) > 1e-12 for k in ("mean", "rms", "p99", "max")):
                raise AssertionError("完整输出不符合逐码解析统计")
            receipts = []
            for kernel in kernels:
                output = folder/f"{variant}-native.rgb"
                receipt = runtime.cube([path], output, executable=executable, kernel=kernel, threads=1)
                if digest(output) != cube["prediction_sha256"]:
                    raise AssertionError("原生完整色域与整数oracle不同")
                receipts.append({**receipt, "sha256": digest(output), "byte_mismatches": 0})
            model_records[size][variant] = {"cube": cube, "native_cube": receipts, "photos": []}
            print(f"m{size} {variant} 完整色域及{len(receipts)}原生后端一致", flush=True)
    expected_photo_hashes = {size: hashlib.sha256() for size in loaded}
    for row in rows:
        path = checked(row["evaluation"])
        with Image.open(path) as image:
            if image.mode != "RGB" or image.size != tuple(plan["photos"]["size"]):
                raise ValueError("照片不满足冻结RGB8尺寸")
            rgb = np.asarray(image).reshape(-1, 3)
        truth = reference.reshape(-1, 3)[rgb_keys(rgb)]
        for size, variants in loaded.items():
            for variant, model in variants.items():
                output = ea.Operator([model])(rgb)
                saved = np.memmap(args.output/f"m{size}"/f"{variant}-cube.rgb", np.uint8, "r", shape=(256**3, 3))
                np.testing.assert_array_equal(output, saved[rgb_keys(rgb)])
                model_records[size][variant]["photos"].append({"image": row["id"], **ea.metrics(output, truth)})
                if variant == "calibrated":
                    expected_photo_hashes[size].update(output.tobytes())
    for size, variants in model_records.items():
        for variant, result in variants.items():
            per = result["photos"]
            result["photos"] = {"n_images": len(per), "mean": float(np.mean([r["mean"] for r in per])),
                "rms": float(np.sqrt(np.mean([r["rms"]**2 for r in per]))),
                "worst_image_p99": max(r["p99"] for r in per), "max": max(r["max"] for r in per),
                "mean_image_cvar_1pct": float(np.mean([r["cvar_1pct"] for r in per])), "per_image": per}
        folder = args.output/f"m{size}"
        native_photos = folder/"calibrated-native-photos.rgb"
        receipt = runtime.verify([folder/"calibrated.slut"], listing, executable=executable,
                                 kernel="tetra_avx2", threads=1, output=native_photos)
        if digest(native_photos) != expected_photo_hashes[size].hexdigest():
            raise AssertionError("原生100图完整输出与研究输出不同")
        variants["calibrated"]["native_photos"] = {**receipt, "sha256": digest(native_photos), "byte_mismatches": 0}
    result = {"run_identity": run["identity_sha256"], "preparation_sha256": digest(args.output/"preparation.json"),
              "sizes": model_records, "scope": plan["limits"], "default_promoted": False,
              "metrics": "RGB欧氏码值距离；完整域p99与最差逐图p99分开"}
    write_json(args.output/"full-results.json", result)
    print(json.dumps({size: {variant: {"cube_mean": value["cube"]["mean"], "photos_mean": value["photos"]["mean"]}
                            for variant, value in variants.items()} for size, variants in model_records.items()}, ensure_ascii=False), flush=True)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("mode", choices=("prepare", "accept"))
    parser.add_argument("--plan", type=Path, default=ROOT/"experiments/filmic-calibration-v1.json")
    parser.add_argument("--output", type=Path, default=ROOT/"artifacts/filmic-calibration-v1")
    args = parser.parse_args()
    args.plan, args.output = args.plan.resolve(), args.output.resolve()
    numba.set_num_threads(4)
    (prepare if args.mode == "prepare" else accept)(args, read(args.plan))


if __name__ == "__main__":
    main()
