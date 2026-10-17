"""按冻结计划执行少量误差归因与补点研究；不运行性能/方法矩阵。"""
from __future__ import annotations

import argparse
import csv
import hashlib
import io as textio
import inspect
import json
from pathlib import Path
import shutil
import sys
import time
import uuid

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "python"))
import numba
import numpy as np
import scipy.sparse as sp
from PIL import Image

from lutlab import error_analysis as ea
from lutlab import fit, hackextend, hackset, interp, io, runtime, source_lut, study_provenance
from lutlab.compatibility import environment, write_json


def digest(path):
    with Path(path).open("rb") as stream:
        return hashlib.file_digest(stream, "sha256").hexdigest()


def encoded(rgb):
    return rgb.astype(np.int64) @ np.array([65536, 256, 1])


def colours(index):
    return np.stack((index >> 16, (index >> 8) & 255, index & 255), axis=1).astype(np.uint8)


def fixed_points(spec, exclude):
    rng = np.random.default_rng(spec["seed"])
    parts, count = [], 0
    forbidden = set(map(int, exclude))
    while count < spec["count"]:
        drawn = rng.choice(256 ** 3, min(2 * (spec["count"] - count), 256 ** 3), replace=False)
        accepted = [int(value) for value in drawn if int(value) not in forbidden]
        accepted = accepted[:spec["count"] - count]
        forbidden.update(accepted)
        parts.extend(accepted)
        count += len(accepted)
    return colours(np.asarray(parts, np.int64))


def source_tables(case, cache):
    records, tables = [], []
    if case["kind"] == "hack-chain":
        result = hackextend.export_case(case["case_id"], cache / "hack-sources")
        for item in result["stages"]:
            path = cache / "hack-sources" / case["case_id"] / item["path"]
            if digest(path) != item["sha256"]:
                raise ValueError("控制例完整源哈希不同")
            tables.append(io.load_full(path, mmap=True))
            records.append({**item, "path": str(path.relative_to(ROOT))})
        return tables, records
    metadata = json.loads((ROOT / "assets/LUT/manifest.json").read_text(encoding="utf-8"))["assets"]
    for source in case["sources"]:
        row = next(r for r in metadata if r["path"] == source["path"])
        path = ROOT / row["path"]
        if digest(path) != source["sha256"] or row["sha256"] != source["sha256"]:
            raise ValueError("真实LUT来源与冻结计划不符")
        key = study_provenance.identity_digest({"source": source, "adapter": digest(Path(source_lut.__file__)),
            "kernels": digest(ROOT / "python/lutlab/study_kernels.py"),
            "environment": study_provenance.environment_fingerprint()})
        folder = cache / ("source-" + key[:24])
        path = folder / "table.lut256"
        if not (folder / "ready.json").exists():
            temporary = cache / ("source-work-" + uuid.uuid4().hex)
            temporary.mkdir()
            table, policy = source_lut.bake_source(ROOT / row["path"], row)
            table.tofile(temporary / path.name)
            write_json(temporary / "ready.json", {"source": source, "policy": policy,
                "table_sha256": digest(temporary / path.name)})
            temporary.rename(folder)
        ready = json.loads((folder / "ready.json").read_text(encoding="utf-8"))
        if digest(path) != ready["table_sha256"]:
            raise ValueError("完整参考缓存字节变化")
        tables.append(io.load_full(path, mmap=True))
        records.append({**ready, "path": str(path.relative_to(ROOT))})
    return tables, records


def prepare_stage(table, record, grid_mode, m, cache):
    identity = {"table": record.get("table_sha256", record.get("sha256")), "grid": grid_mode, "m": m,
        "preparation_code_sha256": hashlib.sha256(inspect.getsource(prepare_stage).encode()).hexdigest(),
        "method": "ls_tetra_int", "environment": study_provenance.environment_fingerprint(),
        "source_sha256": {name: digest(ROOT / "python/lutlab" / name)
                           for name in ("fit.py", "interp.py", "io.py", "curve.py")}}
    key = study_provenance.identity_digest(identity)
    folder = cache / ("baseline-" + key[:24])
    if not (folder / "ready.json").exists():
        temporary = cache / ("baseline-work-" + uuid.uuid4().hex)
        temporary.mkdir()
        grid = fit.adaptive_grid(table, m) if grid_mode == "curvature" else io.uniform_grid(m)
        tri = fit.fit_ls_sep(table, grid, "hat")
        diagnostics = {}
        raw, H, b = fit.fit_ls_tetra(table, grid, x0=tri.reshape(-1, 3), diagnostics=diagnostics)
        nodes = fit.quantize(fit.int_refine(raw, H, b)).reshape(m, m, m, 3)
        model = io.SparseLut(grid, nodes)
        io.save_sparse(temporary / "model.slut", model)
        np.save(temporary / "grid.npy", grid)
        np.save(temporary / "raw.npy", raw)
        np.save(temporary / "tri.npy", tri)
        np.save(temporary / "rhs.npy", b)
        sp.save_npz(temporary / "normal.npz", H)
        write_json(temporary / "diagnostics.json", {"solver": diagnostics,
            "unsupported_nodes": int(np.count_nonzero(H.diagonal() == 0)),
            "raw_components_outside_box": int(np.count_nonzero((raw < 0) | (raw > 255)))})
        write_json(temporary / "ready.json", {"identity": identity,
            "files": {p.name: digest(p) for p in temporary.iterdir()}})
        temporary.rename(folder)
    ready = json.loads((folder / "ready.json").read_text(encoding="utf-8"))
    if ready["identity"] != identity or any(digest(folder / name) != h for name, h in ready["files"].items()):
        raise ValueError("基础模型缓存身份或字节不一致")
    model = io.load_sparse(folder / "model.slut")
    # 保留拟合时的离线坐标，序列化 idx/frac 仍为运行时权威值。
    model.grid = np.load(folder / "grid.npy")
    regenerated = io.axis_tables(model.grid)
    if not all(np.array_equal(a, b) for a, b in zip(regenerated, model.tables())):
        raise ValueError("优化坐标与权威轴表不一致，拒绝重建权重")
    return model, folder


def cube_evaluate(tables, operator, output, top_k):
    output.parent.mkdir(parents=True, exist_ok=True)
    hist = np.zeros(len(ea.ROOT_DISTANCE), np.int64)
    worst_ids, worst_d2 = np.empty(0, np.int64), np.empty(0, np.int32)
    truth_hash, prediction_hash = hashlib.sha256(), hashlib.sha256()
    with output.open("wb") as stream:
        for start in range(0, 256 ** 3, 1 << 18):
            ids = np.arange(start, start + (1 << 18), dtype=np.int64)
            rgb = colours(ids)
            truth = ea.exact_chain(tables, rgb)
            prediction = operator(rgb)
            block, squared = ea.histogram(prediction, truth)
            hist += block
            truth_hash.update(truth.tobytes())
            prediction_hash.update(prediction.tobytes())
            stream.write(prediction.tobytes())
            top = np.argsort(-squared, kind="stable")[:top_k]
            worst_ids = np.concatenate((worst_ids, ids[top]))
            worst_d2 = np.concatenate((worst_d2, squared[top]))
            select = np.lexsort((worst_ids, -worst_d2))[:top_k]
            worst_ids, worst_d2 = worst_ids[select], worst_d2[select]
    return {**ea.hist_metrics(hist), "prediction_sha256": prediction_hash.hexdigest(),
        "reference_sha256": truth_hash.hexdigest(), "hotspots": [
            {"rgb": rgb.tolist(), "distance": float(np.sqrt(d2))}
            for rgb, d2 in zip(colours(worst_ids), worst_d2)]}


def photos_evaluate(tables, variants):
    rows = json.loads((ROOT / "assets/photos/manifest.json").read_text(encoding="utf-8"))["images"]
    results = {name: [] for name in variants}
    for row in rows:
        path = ROOT / row["evaluation"]["path"]
        if digest(path) != row["evaluation"]["sha256"]:
            raise ValueError("历史照片文件字节变化")
        with Image.open(path) as image:
            if image.mode != "RGB" or image.size != (1024, 768):
                raise ValueError("图片不符合RGB8比赛尺寸")
            rgb = np.asarray(image).reshape(-1, 3)
        truth = ea.exact_chain(tables, rgb)
        for name, operator in variants.items():
            results[name].append({"image": row.get("id", row["evaluation"]["path"]),
                                  **ea.metrics(operator(rgb), truth)})
    return {name: {"n_images": len(values), "mean": float(np.mean([r["mean"] for r in values])),
        "rms": float(np.sqrt(np.mean([r["rms"] ** 2 for r in values]))),
        "worst_image_p99": max(r["p99"] for r in values), "max": max(r["max"] for r in values),
        "per_image": values} for name, values in results.items()}


def process_case(case, plan, output, cache, discovery, guard, evaluation, executable):
    folder = output / case["id"]
    folder.mkdir(exist_ok=True)
    tables, references = source_tables(case, cache)
    print(f"[{case['id']}] 源表就绪，拟合/复用 {len(tables)} 级基线", flush=True)
    prepared = [prepare_stage(t, record, case["grid"], plan["m"], cache) for t, record in zip(tables, references)]
    models = [p[0] for p in prepared]
    model_paths = []
    for k, model in enumerate(models):
        path = folder / f"baseline-stage{k+1}.slut"
        io.save_sparse(path, model)
        model_paths.append(path)
    # 独立整数实现核对后再展开全域；不把浮点研究核当成自己的 oracle。
    for model in models:
        np.testing.assert_array_equal(ea.Operator([model])(guard[:4096]), interp.apply_tetra_q16(model, guard[:4096]))
    operator = ea.Operator(models)
    diagnosis_path = folder / "diagnosis.json"
    if diagnosis_path.exists():
        diagnosis = json.loads(diagnosis_path.read_text(encoding="utf-8"))
        if digest(folder / "baseline.rgb") != diagnosis["baseline_cube"]["prediction_sha256"]:
            raise ValueError("归因检查点的基线输出变化")
        attribution, baseline_cube = diagnosis["attribution"], diagnosis["baseline_cube"]
    else:
        attribution = ea.stage_attribution(tables, models, discovery)
        baseline_cube = cube_evaluate(tables, operator, folder / "baseline.rgb", plan["hotspot_k"])
        write_json(diagnosis_path, {"attribution": attribution, "baseline_cube": baseline_cube})
    selected = max(attribution["stages"], key=lambda r: (r["replacement_gain_cvar"], r["replacement_gain_mean"], -r["stage"]))["stage"] - 1
    print(f"[{case['id']}] 归因选择第 {selected+1} 级，展开一次基线全色域并冻结热点", flush=True)
    own_points = ea.Operator(models[:selected])(discovery)
    own_guard = ea.Operator(models[:selected])(guard)
    own_labels = ea.source_apply(tables[selected], own_points)
    risk = ea.suffix_sensitivity(tables[selected+1:], own_labels)
    weights = np.clip(np.maximum(risk, 1.), 1., plan["sensitivity_weight_cap"])
    stage_folder = prepared[selected][1]
    diagnostics = ea.rounding_diagnostics(tables[selected], models[selected], own_points,
        np.load(stage_folder / "raw.npy"), np.load(stage_folder / "tri.npy"))
    diagnostics["node_support"] = json.loads((stage_folder / "diagnostics.json").read_text(encoding="utf-8"))
    diagnostics["suffix_lsb_response"] = {"mean": float(risk.mean()), "p99": float(np.percentile(risk, 99)),
                                         "max": float(risk.max()), "fraction_gt_1": float(np.mean(risk > 1))}
    H, b = sp.load_npz(stage_folder / "normal.npz"), np.load(stage_folder / "rhs.npy")
    variants = {"baseline": models}
    fit_details = {}
    for name, w in (("distribution_ls", np.ones(len(own_points))), ("sensitive_ls", weights)):
        detail = {}
        changed = ea.weighted_refit(tables[selected], models[selected], own_points, w, H, b, detail)
        variants[name] = [changed if k == selected else model for k, model in enumerate(models)]
        fit_details[name] = detail
    hot_initial = np.asarray([r["rgb"] for r in baseline_cube["hotspots"]], np.uint8)
    diagnostics["hotspot_traces"] = ea.hotspot_traces(tables, models, hot_initial, selected)
    hot_stage = np.unique(np.concatenate((ea.neighbourhood(ea.Operator(models[:selected])(hot_initial)),
        ea.Operator(models[:selected])(ea.neighbourhood(hot_initial)))), axis=0)
    training = np.concatenate((fit._cube_points(), own_points, np.repeat(hot_stage, plan["hotspot_repeats"], axis=0)))
    training_labels = ea.source_apply(tables[selected], training)
    guard_labels = ea.source_apply(tables[selected], own_guard)
    for name, parent in (("hotspot_integer", "baseline"), ("combined", "sensitive_ls")):
        detail = {}
        prior = variants[parent][selected]
        changed = fit.q16_refine_guarded(prior.nodes, training, training_labels, prior.grid,
            sweeps=plan["q16_sweeps"], guard_points=own_guard, guard_targets=guard_labels, diagnostics=detail)
        variants[name] = [io.SparseLut(prior.grid, changed) if k == selected else model for k, model in enumerate(models)]
        fit_details[name] = detail
    guard_truth = ea.exact_chain(tables, guard)
    discovery_truth = ea.exact_chain(tables, discovery)
    measurements = {name: {"guard": ea.metrics(ea.Operator(value)(guard), guard_truth),
        "discovery": ea.metrics(ea.Operator(value)(discovery), discovery_truth)} for name, value in variants.items()}
    eligible = [name for name in variants if ea.promoted(measurements[name]["guard"], measurements["baseline"]["guard"])]
    winner = min(eligible, key=lambda name: tuple(measurements[name]["guard"][k] for k in ("max", "p99", "mean", "rms"))) if eligible else "baseline"
    for name, chain in variants.items():
        path = folder / f"{name}-stage{selected+1}.slut"
        io.save_sparse(path, chain[selected])
        measurements[name]["stage_sha256"] = digest(path)
        measurements[name]["guard_eligible"] = name in eligible
    # 选型在读取 evaluation 颜色和完整照片前冻结。
    write_json(folder / "selection.json", {"selected_stage": selected+1, "winner": winner,
        "candidates": measurements, "hot_stage_colours": len(hot_stage), "training_points": len(training),
        "model_sha256": {name: [digest(folder / f"{name}-stage{selected+1}.slut") if k == selected else digest(model_paths[k])
                               for k in range(len(models))] for name in variants}})
    print(f"[{case['id']}] guard 冻结选择 {winner}；进入最终评价", flush=True)
    final_variants = {"baseline": operator}
    if winner != "baseline":
        final_variants[winner] = ea.Operator(variants[winner])
    evaluation_truth = ea.exact_chain(tables, evaluation)
    final = {name: {"sample": ea.metrics(op(evaluation), evaluation_truth)} for name, op in final_variants.items()}
    final["baseline"]["cube"] = baseline_cube
    if winner != "baseline":
        final[winner]["cube"] = cube_evaluate(tables, final_variants[winner], folder / f"{winner}.rgb", plan["hotspot_k"])
    photos = photos_evaluate(tables, final_variants)
    for name in final:
        final[name]["photos"] = photos[name]
    native = []
    for name, op in final_variants.items():
        # 完整色域独立整数 oracle，以固定块复核研究输出。
        expected_hash = hashlib.sha256()
        for start in range(0, 256 ** 3, 1 << 16):
            rgb = colours(np.arange(start, start + (1 << 16), dtype=np.int64))
            for model in op.models:
                rgb = interp.apply_tetra_q16(model, rgb)
            expected_hash.update(rgb.tobytes())
        if expected_hash.hexdigest() != final[name]["cube"]["prediction_sha256"]:
            raise AssertionError("研究输出与独立整数oracle的完整色域不同")
        paths = []
        for k, model in enumerate(op.models):
            path = folder / f"{name}-native-stage{k+1}.slut"
            io.save_sparse(path, model)
            paths.append(path)
        for kernel in (("tetra_scalar", "tetra_avx2", "tetra_c99") if len(models) == 4 else ("tetra_scalar", "tetra_avx2")):
            destination = folder / "native-check.rgb"
            execution = runtime.cube(paths, destination, executable=executable, kernel=kernel,
                                     threads=1, competition=len(models) == 4)
            actual = digest(destination)
            if actual != expected_hash.hexdigest():
                raise AssertionError(f"{kernel} 的完整输出与独立oracle不同")
            native.append({"variant": name, "kernel": execution["kernel"], "sha256": actual,
                           "executable_sha256": execution["executable_sha256"], "byte_mismatches": 0})
    control = None
    if case.get("existing_control"):
        from lutlab import cascade
        control_models, detail = cascade.fit_cascade_sequential(tables, plan["m"], base_method=case["existing_control"], grid_mode="dp")
        control = {"method": case["existing_control"], "details": detail,
            "cube": cube_evaluate(tables, ea.Operator(control_models), folder / "existing-control.rgb", plan["hotspot_k"])}
        for k, model in enumerate(control_models):
            io.save_sparse(folder / f"existing-control-stage{k+1}.slut", model)
    result = {"case": case, "sources": references, "attribution": attribution,
        "selected_stage": selected+1, "rounding_diagnostics": diagnostics, "candidate_measurements": measurements,
        "fit_details": fit_details, "winner": winner, "final": final, "native_parity": native,
        "existing_control": control, "scope": "固定四例诊断；单级结果不是比赛四级成绩；无官方阈值/性能结论"}
    write_json(folder / "result.json", result)
    print(f"[{case['id']}] 完成：baseline cube mean={baseline_cube['mean']:.6f} max={baseline_cube['max']:.6f}；选择 {winner}", flush=True)
    return result


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--plan", type=Path, default=ROOT / "experiments/chain-error-study-v1.json")
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--cache", type=Path, default=ROOT / "artifacts/chain-error-cache")
    parser.add_argument("--executable", type=Path, required=True)
    args = parser.parse_args()
    plan = json.loads(args.plan.read_text(encoding="utf-8"))
    numba.set_num_threads(plan["threads"])
    metadata = environment(argparse.Namespace(sizes=[plan["m"]], screen_pixels=plan["discovery"]["count"],
        threads=plan["threads"], reps=0, extended=False))
    metadata["identity"].update(plan_sha256=digest(args.plan), executable_sha256=digest(args.executable),
        experiment_source={str(p.relative_to(ROOT)): digest(p) for p in
            (Path(__file__), ROOT / "python/lutlab/error_analysis.py", ROOT / "python/lutlab/hackextend.py",
             ROOT / "python/lutlab/hackset.py")})
    metadata["identity_sha256"] = study_provenance.identity_digest(metadata["identity"])
    args.output.mkdir(parents=True, exist_ok=True)
    args.cache.mkdir(parents=True, exist_ok=True)
    study_provenance.claim_run(args.output / "run.json", metadata)
    discovery = fixed_points(plan["discovery"], [])
    guard = fixed_points(plan["guard"], encoded(discovery))
    evaluation = fixed_points(plan["evaluation"], np.concatenate((encoded(discovery), encoded(guard))))
    for name, points in (("discovery", discovery), ("guard", guard), ("evaluation", evaluation)):
        np.save(args.output / f"{name}.npy", points)
    results = []
    for case in plan["cases"]:
        previous = args.output / case["id"] / "result.json"
        if previous.exists():
            results.append(json.loads(previous.read_text(encoding="utf-8")))
        else:
            results.append(process_case(case, plan, args.output, args.cache, discovery, guard, evaluation, args.executable))
    write_json(args.output / "results.json", {"run_identity": metadata["identity_sha256"], "cases": results})


if __name__ == "__main__":
    main()
