"""按冻结计划研究有界拟合、RGB范数与多测度四级联合选择。"""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "python"))
import numba
import numpy as np
import scipy.sparse as sp
from PIL import Image
from lutlab import box, error_analysis as ea, fit, interp, io, joint_fit, runtime, study_provenance
from lutlab.compatibility import environment, write_json
from run_chain_error_study import (colours, cube_evaluate, digest, encoded, fixed_points,
                                   photos_evaluate, prepare_stage, source_tables)


def photo_samples(rows, plan):
    parts, metadata = [], []
    for row in rows:
        path = ROOT / row["evaluation"]["path"]
        if digest(path) != row["evaluation"]["sha256"]:
            raise ValueError("照片输入与清单哈希不同")
        with Image.open(path) as image:
            if image.mode != "RGB" or image.size != (1024, 768):
                raise ValueError("照片不符合1024×768 RGB8契约")
            rgb = np.asarray(image).reshape(-1, 3)
        seed = int.from_bytes(hashlib.sha256((str(plan["pixel_seed"])+":"+row["id"]).encode()).digest()[:8], "little")
        indices = np.random.default_rng(seed).choice(len(rgb), plan["pixels_per_image"], replace=False)
        parts.append(rgb[indices].copy())
        metadata.append({"id": row["id"], "file_sha256": digest(path),
                         "pixel_indices_sha256": hashlib.sha256(indices.astype("<u4").tobytes()).hexdigest()})
    samples = np.concatenate(parts)
    return samples, {"images": metadata, "samples_sha256": hashlib.sha256(samples.tobytes()).hexdigest()}


def uniform_diagnostic(table, model, prepared, points, photo_points):
    normal, rhs = sp.load_npz(prepared / "normal.npz"), np.load(prepared / "rhs.npy")
    start = model.nodes.reshape(-1, 3).astype(float)
    diagonal = 1e-4 * (normal.diagonal()+1)
    system, linear = normal + sp.diags(diagonal), rhs + diagonal[:, None]*start
    info = {}
    raw = fit.solve_spd(normal, rhs, start, diagnostics=info.setdefault("cg", {}))
    bounded = box.solve_box(system, linear, np.clip(raw, 0, 255), diagnostics=info.setdefault("box", {}))
    delta = bounded - np.clip(raw, 0, 255)
    gradient = system @ np.clip(raw, 0, 255) - linear
    info.update(raw_outside=int(np.count_nonzero((raw < 0) | (raw > 255))), bounded_outside=0,
        continuous_box_minus_clamped=float(.5*np.sum(delta*(system@delta))+np.sum(gradient*delta)),
        purpose="同一均匀测度与先验下隔离裁剪；非最终链最优证明", variants={})
    idx, frac = model.tables()
    models = {}
    for name, value in (("uniform_clip", raw), ("uniform_box", bounded)):
        nodes = fit.quantize(fit.int_refine(value, system, linear)).reshape(model.nodes.shape)
        candidate = io.SparseLut(model.grid, nodes, idx, frac)
        models[name] = candidate
        info["variants"][name] = {label: ea.metrics(ea.Operator([candidate])(rgb), ea.source_apply(table, rgb))
            for label, rgb in (("uniform_guard", points), ("photo_guard", photo_points))}
    return info, models


def native_verify(models, folder, expected_sha, executable):
    oracle = hashlib.sha256()
    for start in range(0, 256**3, 1 << 16):
        rgb = colours(np.arange(start, start+(1 << 16), dtype=np.int64))
        for model in models:
            rgb = interp.apply_tetra_q16(model, rgb)
        oracle.update(rgb.tobytes())
    if oracle.hexdigest() != expected_sha:
        raise AssertionError("研究映射与独立整数oracle完整色域不同")
    paths = []
    for k, model in enumerate(models):
        path = folder / f"selected-stage{k+1}.slut"
        io.save_sparse(path, model)
        paths.append(path)
    records = []
    for kernel in (("tetra_scalar", "tetra_avx2", "tetra_c99") if len(models) == 4 else ("tetra_scalar", "tetra_avx2")):
        destination = folder / "native-check.rgb"
        execution = runtime.cube(paths, destination, executable=executable, kernel=kernel,
                                 threads=1, competition=len(models) == 4)
        actual = digest(destination)
        if actual != expected_sha:
            raise AssertionError("原生后端与整数oracle完整色域不同")
        records.append({"kernel": execution["kernel"], "sha256": actual, "byte_mismatches": 0,
                        "executable_sha256": execution["executable_sha256"]})
    return records


def process_case(case, previous, plan, output, cache, train_photo, guard_photo, uniform, guard, evaluation, executable):
    folder = output / case["id"]
    folder.mkdir()
    tables, sources = source_tables(case, cache)
    if [r["table_sha256"] for r in sources] != [r["table_sha256"] for r in previous["sources"]]:
        raise ValueError("参考完整LUT与上一阶段证据不同")
    prepared = [prepare_stage(t, r, case["grid"], plan["m"], cache) for t, r in zip(tables, sources)]
    baseline = [value[0] for value in prepared]
    for k, model in enumerate(baseline):
        path = folder / f"baseline-stage{k+1}.slut"
        io.save_sparse(path, model)
        old = ROOT / "artifacts/chain-error-study-v1" / case["id"] / path.name
        if digest(path) != digest(old):
            raise ValueError("基线模型字节改变，不能复用旧完整色域指标")
    banks, fit_details = [], []
    stage_photo = train_photo
    for k, (table, model) in enumerate(zip(tables, baseline)):
        print(f"[{case['id']}] 第{k+1}级：固定候选拟合", flush=True)
        detail = {}
        bank = {"baseline": model, **joint_fit.fit_bank(table, model, uniform, stage_photo,
            mass=plan["photo_mass"], lam=plan["lambda_prior"], epsilon=plan["irls_epsilon"],
            irls_rounds=plan["irls_rounds"], diagnostics=detail)}
        for name, candidate in bank.items():
            io.save_sparse(folder / f"{name}-stage{k+1}.slut", candidate)
            if not all(np.array_equal(a, b) for a, b in zip(model.tables(), candidate.tables())):
                raise AssertionError("固定网格候选改变了权威轴表")
        banks.append(bank)
        fit_details.append(detail)
        stage_photo = ea.Operator([model])(stage_photo)
    hotspot = ea.neighbourhood(np.asarray([r["rgb"] for r in previous["final"]["baseline"]["cube"]["hotspots"]], np.uint8))
    sample_sets = {"uniform": {"points": guard, "truth": ea.exact_chain(tables, guard)},
        "photo": {"points": guard_photo, "truth": ea.exact_chain(tables, guard_photo), "group_size": plan["pixels_per_image"]},
        "hotspot": {"points": hotspot, "truth": ea.exact_chain(tables, hotspot)}}
    print(f"[{case['id']}] 联合候选库选择：{4**len(banks)}个固定组合", flush=True)
    measurements = joint_fit.enumerate_bank(banks, sample_sets)
    baseline_key = ["baseline"] * len(banks)
    selected = joint_fit.choose(measurements, baseline_key)
    one_stage = joint_fit.choose([r for r in measurements if sum(n != "baseline" for n in r["key"]) <= 1], baseline_key)
    uniform_only = joint_fit.choose(measurements, baseline_key, measures=("uniform",))
    winner = selected["winner"]
    models = [stage[name] for stage, name in zip(banks, winner)]
    selection = {"joint": selected, "one_stage": one_stage, "uniform_only": uniform_only,
        "candidate_count": len(measurements), "measurements": measurements,
        "selected_model_sha256": [digest(folder / f"{name}-stage{k+1}.slut") for k, name in enumerate(winner)],
        "input_sha256": {name: hashlib.sha256(spec["points"].tobytes()).hexdigest() for name, spec in sample_sets.items()}}
    # 在读取完整照片和最终样本指标前写入不可再选型的决策。
    write_json(folder / "selection.json", selection)
    print(f"[{case['id']}] 选择冻结：{winner}；开始阶段验收", flush=True)
    operator = ea.Operator(models)
    if winner == baseline_key:
        cube = previous["final"]["baseline"]["cube"]
        parity = {"reused_baseline": previous["native_parity"], "reason": "模型、完整表和原生程序同字节"}
    else:
        cube = cube_evaluate(tables, operator, folder / "selected.rgb", 128)
        parity = native_verify(models, folder, cube["prediction_sha256"], executable)
    if cube["reference_sha256"] != previous["final"]["baseline"]["cube"]["reference_sha256"]:
        raise AssertionError("最终参考色域与上一阶段不同")
    photos = photos_evaluate(tables, {"baseline": ea.Operator(baseline), "selected": operator})
    # 复算照片基线是配对评价，同时核对旧逐图数据，避免不同解码环境混用。
    old_photos = previous["final"]["baseline"]["photos"]
    if photos["baseline"] != old_photos:
        raise AssertionError("完整照片基线指标与旧证据不同")
    evaluation_truth = ea.exact_chain(tables, evaluation)
    diagnostic, diagnostic_models = ({}, {}) if len(tables) != 1 else uniform_diagnostic(
        tables[0], baseline[0], prepared[0][1], guard, guard_photo)
    for name, model in diagnostic_models.items():
        io.save_sparse(folder / f"{name}-diagnostic.slut", model)
    result = {"case": case, "sources": sources, "selection": {key: value for key, value in selection.items() if key != "measurements"},
        "fit_details": fit_details, "uniform_diagnostic": diagnostic,
        "baseline": {"cube": previous["final"]["baseline"]["cube"], "photos": photos["baseline"],
                     "sample": ea.metrics(ea.Operator(baseline)(evaluation), evaluation_truth)},
        "selected": {"cube": cube, "photos": photos["selected"], "sample": ea.metrics(operator(evaluation), evaluation_truth)},
        "selected_stage_attribution": ea.stage_attribution(tables, models, evaluation), "native_parity": parity,
        "scope": "固定已知案例；无官方精度/性能通过声明；模型和网格格式不变"}
    write_json(folder / "result.json", result)
    write_json(folder / "receipt.json", {p.name: digest(p) for p in folder.iterdir() if p.suffix in (".json", ".slut")})
    print(f"[{case['id']}] 全域mean {result['baseline']['cube']['mean']:.6f} → {cube['mean']:.6f}；"
          f"100图mean {photos['baseline']['mean']:.6f} → {photos['selected']['mean']:.6f}", flush=True)
    return result


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--plan", type=Path, default=ROOT / "experiments/joint-box-study-v1.json")
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--cache", type=Path, default=ROOT / "artifacts/chain-error-cache")
    parser.add_argument("--executable", type=Path, required=True)
    args = parser.parse_args()
    args.output, args.cache, args.executable = args.output.resolve(), args.cache.resolve(), args.executable.resolve()
    plan = json.loads(args.plan.read_text(encoding="utf-8"))
    old_plan_path, old_result_path = ROOT / plan["prior_plan"], ROOT / plan["prior_evidence"]
    old_plan = json.loads(old_plan_path.read_text(encoding="utf-8"))
    previous = {row["case"]["id"]: row for row in json.loads(old_result_path.read_text(encoding="utf-8"))["cases"]}
    numba.set_num_threads(plan["threads"])
    metadata = environment(argparse.Namespace(sizes=[plan["m"]], screen_pixels=plan["pixels_per_image"],
        threads=plan["threads"], reps=0, extended=False))
    metadata["identity"].update(plan_sha256=digest(args.plan), prior_plan_sha256=digest(old_plan_path),
        prior_results_sha256=digest(old_result_path), executable_sha256=digest(args.executable),
        stage_source_sha256={str(p.relative_to(ROOT)): digest(p) for p in (Path(__file__),
            ROOT / "scripts/run_chain_error_study.py", ROOT / "python/lutlab/joint_fit.py",
            ROOT / "python/lutlab/error_analysis.py", ROOT / "python/lutlab/box.py")})
    metadata["identity_sha256"] = study_provenance.identity_digest(metadata["identity"])
    for cid in plan["cases"]:
        for item in previous[cid]["native_parity"]:
            if item["executable_sha256"] != digest(args.executable):
                raise ValueError("原生程序变化，不能复用旧基线正确性")
    study_provenance.claim_run(args.output / "run.json", metadata)
    rows = json.loads((ROOT / "assets/photos/manifest.json").read_text(encoding="utf-8"))["images"]
    rows = sorted(rows, key=lambda r: hashlib.sha256(("joint-box-v1:"+r["id"]).encode()).hexdigest())
    train_end, guard_end = plan["photo_train_count"], plan["photo_train_count"]+plan["photo_guard_count"]
    train_photo, training = photo_samples(rows[:train_end], plan)
    guard_photo, guarding = photo_samples(rows[train_end:guard_end], plan)
    write_json(args.output / "photo-partition.json", {"training": training, "guard": guarding,
        "audit_ids": [r["id"] for r in rows[guard_end:]], "scope": "历史已知照片，审计仅不参与本轮选择；非盲测"})
    uniform = fit._cube_points(4)
    guard = fixed_points(plan["uniform_guard"], encoded(np.concatenate((uniform, train_photo))))
    evaluation = fixed_points(plan["evaluation"], encoded(np.concatenate((uniform, train_photo, guard_photo, guard))))
    write_json(args.output / "sample-hashes.json", {name: hashlib.sha256(points.tobytes()).hexdigest()
        for name, points in (("uniform_fit", uniform), ("uniform_guard", guard), ("evaluation", evaluation))})
    results = []
    for cid in plan["cases"]:
        folder = args.output / cid
        if folder.exists():
            receipt = json.loads((folder / "receipt.json").read_text(encoding="utf-8"))
            if any(digest(folder / name) != expected for name, expected in receipt.items()):
                raise ValueError("已有阶段产物字节改变，拒绝恢复")
            result = json.loads((folder / "result.json").read_text(encoding="utf-8"))
        else:
            case = next(case for case in old_plan["cases"] if case["id"] == cid)
            result = process_case(case, previous[cid], plan, args.output, args.cache, train_photo, guard_photo,
                                  uniform, guard, evaluation, args.executable)
        results.append(result)
    write_json(args.output / "results.json", {"run_identity": metadata["identity_sha256"], "cases": results})


if __name__ == "__main__":
    main()
