"""One serial proof-selected interpolation qualification against frozen R25.

All thirteen prior model cases are fitted. Unchanged complete model bytes reuse
their frozen actual CPU/CUDA full-cube and 100-frame evidence after checking
every input and executable hash. Changed models receive fresh actual acceptance.
A new, independent coupled 3D control must equal its four full LUT composition
on every RGB8 input, on both native backends, including the aligned fourth stage.
"""
from __future__ import annotations

import argparse
from datetime import datetime, timezone
import hashlib
import json
import os
from pathlib import Path
import sys
import time
import zipfile

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "python"))
from lutlab import cache, fit, fullfit, interp, io, metrics, runtime, step
from lutlab.entry import _write_report
from r21_boundary_study import _accept, _comparison, _fit
from r24_supported_study import _fit_record
from r26_box_study import CASES, _function_text


def _coupled_control(output, cpu, cuda):
    directory = output / "coupled-control"
    directory.mkdir(parents=True, exist_ok=True)
    rng = np.random.default_rng(2026101527)
    tables, models, records, palette = [], [], [], None
    for stage_index, m in enumerate((17, 18, 25), 1):
        # Every output channel couples all three input bins. A short component
        # alphabet in stage 3 proves a useful complete input superset for stage 4.
        bins = 8 + stage_index
        axes = [np.r_[0, np.sort(rng.choice(np.arange(1, 255), bins - 1, replace=False))]
                for _ in range(3)]
        alphabet = np.linspace(0, 255, 12 + stage_index).round().astype(np.uint8)
        labels = alphabet[rng.integers(0, len(alphabet), (bins, bins, bins, 3))]
        indices = [np.searchsorted(axis, np.arange(256), side="right") - 1 for axis in axes]
        table = np.ascontiguousarray(labels[np.ix_(*indices)])
        tables.append(table)
        model, info = fit.fit_model(table, m, "adaptive_full", reachable_inputs=palette)
        if info["model_route"] != "exact_lower_hold" or not step.is_one_hot(model):
            raise RuntimeError("coupled constant-cell control was not proved exact")
        # Exactness is tested below by native full-cube execution against an
        # independently composed full LUT, rather than a second weight routine.
        palette = step.next_palette(model, palette, diagnostics=info.setdefault("output_palette", {}))
        models.append(model)
        records.append(info)
    # A genuinely nonconstant, coupled final LUT rules out the hold route. It
    # can still be exact on the complete output set of the first three maps.
    r, g, b = np.ogrid[:256, :256, :256]
    final = np.empty(io.FULL_SHAPE, np.uint8)
    final[..., 0] = (3 * r + 5 * g + 7 * b + 19) % 256
    final[..., 1] = (r + 11 * g + 13 * b + 37) % 256
    final[..., 2] = (17 * r + 19 * g + b + 71) % 256
    tables.append(final)
    aligned, detail = fit.fit_model(final, 33, "adaptive_full", reachable_inputs=palette)
    if detail["model_route"] != "exact_reachable_vertices":
        raise RuntimeError("finite-palette coupled control did not use exact vertex alignment")
    models.append(aligned)
    records.append(detail)
    paths = []
    for index, model in enumerate(models, 1):
        path = directory / f"stage{index}.slut"
        io.save_sparse(path, model)
        restored = io.load_sparse(path, competition=True)
        if any(not np.array_equal(a, b) for a, b in zip(restored.tables(), model.tables())):
            raise RuntimeError("serialization lost authoritative coordinates")
        paths.append(path)
    if len({hashlib.sha256(t.tobytes()).hexdigest() for t in tables}) != 4:
        raise RuntimeError("control requires four distinct original transforms")
    reference = io.compose(tables)
    digest = hashlib.sha256(reference.tobytes()).hexdigest()
    executions = []
    for backend, executable in (("cpu", cpu), ("cuda", cuda)):
        cube = directory / f"{backend}.rgb"
        record = runtime.cube(paths, cube, backend=backend, executable=executable,
            kernel="tetra_avx2" if backend == "cpu" else "auto",
            threads=4 if backend == "cpu" else 0, competition=True)
        if metrics.file_sha256(cube) != digest:
            raise RuntimeError("native coupled control differs from exact four-LUT composition")
        executions.append({"backend": backend, "cube_sha256": digest, "execution": record})
    # Negative proofs are essential: a rich continuous LUT, a palette exceeding
    # the per-axis knot budget, or a missing incoming proof must not claim exactness.
    rejected = {}
    if step.exact_lower_hold(final, 17, diagnostics=rejected) is not None:
        raise RuntimeError("continuous control falsely passed the partition proof")
    if step.aligned_vertices(final, 17, None) is not None:
        raise RuntimeError("alignment accepted an unproved incoming palette")
    rich_palette = np.repeat(np.arange(256, dtype=np.uint8)[:, None], 3, axis=1)
    if step.aligned_vertices(final, 33, rich_palette) is not None:
        raise RuntimeError("alignment exceeded the knot budget")
    for bad in (palette.astype(np.int16), palette[:, :2], palette[:0]):
        try:
            step.aligned_vertices(final, 33, bad)
        except ValueError:
            pass
        else:
            raise RuntimeError("malformed finite palette was accepted")
    try:
        fit.fit(final, 33, "adaptive_full")
    except ValueError as error:
        if "fit_model" not in str(error):
            raise
    else:
        raise RuntimeError("node-only API silently discarded custom axis weights")
    return {"seed": 2026101527, "m": [17, 18, 25, 33], "source_sha256": [
        hashlib.sha256(t.tobytes()).hexdigest() for t in tables], "reference_sha256": digest,
        "colors_per_backend": 256 ** 3, "exact_four_stage_full_reference": True,
        "stages": records, "executions": executions, "negative_partition_control": rejected,
        "negative_alignment_and_model_api_pass": True}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--cpu", type=Path, required=True)
    parser.add_argument("--cuda", type=Path, required=True)
    parser.add_argument("--output", type=Path, default=ROOT / "artifacts/r27-step")
    args = parser.parse_args()
    cpu, cuda, output = args.cpu.resolve(), args.cuda.resolve(), args.output.resolve()
    output.mkdir(parents=True, exist_ok=True)
    os.environ.update(OPENBLAS_NUM_THREADS="1", MKL_NUM_THREADS="1", OMP_NUM_THREADS="1", OMP_DYNAMIC="FALSE",
        OMP_THREAD_LIMIT="32", JSHC_BIN=str(cpu), JSHC_CUDA_BIN=str(cuda), JSHC_FULL_FIT_LIB=str(fullfit.resolve_library()))
    os.environ["PYTHONPATH"] = os.pathsep.join([str(ROOT / "python"), str(ROOT / "artifacts/r18-tools/python")])
    started = time.perf_counter()
    prior_path, capacity_path = ROOT / "artifacts/r25-full/study.json", ROOT / "artifacts/r25-full/capacity/study.json"
    prior = json.loads(prior_path.read_text(encoding="utf-8"))
    capacity = json.loads(capacity_path.read_text(encoding="utf-8"))
    if not prior.get("structural_parity_and_full_domain_pass") or not capacity.get("structural_parity_and_capacity_pass"):
        raise RuntimeError("requires completed R25 accuracy evidence")
    trainer = fullfit.trainer_fingerprint()
    if trainer != prior["trainer"]:
        raise RuntimeError("native trainer changed; cannot reuse R25 operator oracle")
    unchanged = ("python/lutlab/fullfit.py", *fullfit.NATIVE_SOURCES, "tests/test_fullfit_contract.py")
    for name in unchanged:
        if metrics.file_sha256(ROOT / name) != prior["source_sha256"][name]:
            raise RuntimeError(f"full-domain oracle dependency changed: {name}")
    snapshot = ROOT / "artifacts/r25-full/source-snapshot.zip"
    with zipfile.ZipFile(snapshot) as archive:
        reference_source = archive.read("python/lutlab/fit.py").decode("utf-8")
    assembler = _function_text((ROOT / "python/lutlab/fit.py").read_text(encoding="utf-8"), "normal_equations")
    if assembler != _function_text(reference_source, "normal_equations"):
        raise RuntimeError("independent COO oracle changed")
    known = {(c["scenario"], c["m"]): c for c in prior["cases"]}
    known.update({(c["scenario"], c["candidate_m"]): c for c in capacity["cases"]})
    sources = {f"python/lutlab/{name}": digest for name, digest in cache.source_fingerprint().items() if name != "pixi.lock"}
    sources.update({name: metrics.file_sha256(ROOT / name) for name in (
        "pixi.lock", *fullfit.NATIVE_SOURCES, "python/lutlab/validation.py", "python/lutlab/qualification.py",
        "scripts/r21_boundary_study.py", "scripts/r24_supported_study.py", "scripts/r26_box_study.py",
        "scripts/r27_step_study.py", "tests/test_cache_contract.py")})
    report = {"started_utc": datetime.now(timezone.utc).isoformat(), "scope": __doc__, "source_sha256": sources,
        "predeclared_cases": CASES, "method": "adaptive_full", "trainer": trainer, "official_score_available": False,
        "frozen_baselines": {str(p): metrics.file_sha256(p) for p in (prior_path, capacity_path)},
        "reused_native_oracle": {"source_sha256": {name: prior["source_sha256"][name] for name in unchanged},
            "reference_function_sha256": hashlib.sha256(assembler.encode()).hexdigest(),
            "source_snapshot_sha256": metrics.file_sha256(snapshot), "library_sha256": trainer["library_sha256"]},
        "executable_sha256": {str(p): metrics.file_sha256(p) for p in (cpu, cuda)}, "fit_executions": [], "cases": []}
    target = output / "study.json"
    _write_report(target, report)
    check = runtime._execute([sys.executable, "-m", "pytest", "-q", "tests", "--ignore=tests/test_fullfit_contract.py"])
    (output / "pytest.log").write_text(check["stdout"] + check["stderr"], encoding="utf-8")
    report["python_acceptance"] = {k: v for k, v in check.items() if k not in ("stdout", "stderr")}
    _write_report(target, report)
    print(check["stdout"], flush=True)
    if check["returncode"]:
        raise RuntimeError("Python contract stage failed")
    report["coupled_control"] = _coupled_control(output, cpu, cuda)
    _write_report(target, report)
    print("[control] coupled 3D four-stage full LUT equality on CPU and CUDA", flush=True)
    guarded = {}

    def guard(path, digest):
        path = str(path)
        if path in guarded and guarded[path] != digest:
            raise RuntimeError("conflicting frozen source hashes")
        if path not in guarded and metrics.file_sha256(path) != digest:
            raise RuntimeError(f"frozen input changed: {path}")
        guarded[path] = digest

    for scenario, m in CASES:
        old = known[(scenario, m)]
        path = Path(old["result"])
        guard(path, old["result_sha256"])
        baseline = json.loads(path.read_text(encoding="utf-8"))
        for item in baseline["sources"]:
            guard(item["path"], item["sha256"])
        for name, digest in baseline["images"].items():
            guard(name, digest)
        source = Path(baseline["sources"][0]["path"]).parent
        guard(source / "composite.lut256", baseline["reference_sha256"])
        guard(ROOT / "artifacts/r17-acceptance/bench.txt", baseline["image_list_sha256"])
        old_paths = list(map(Path, old["models"]))
        for side in ("cpu", "cuda"):
            evidence = baseline["backends"][side]
            if evidence["executable_sha256"] != report["executable_sha256"][str(cpu if side == "cpu" else cuda)]:
                raise RuntimeError("frozen actual execution used a different executable")
            for name, digest in evidence["model_sha256"].items():
                guard(name, digest)
        models = _fit(source, scenario, m, "adaptive_full", output, report["fit_executions"])
        current = _fit_record(models)
        routes, equal = [], []
        for model_path, reference_path, stage_info in zip(models, old_paths, current["fit"]["stage_info"]):
            route = stage_info["model_route"]
            routes.append(route)
            equal.append(model_path.read_bytes() == reference_path.read_bytes())
            if stage_info["target_semantics"] != "own_original_LUT":
                raise RuntimeError("changed original stage targets")
            if route == "full_domain_fallback" and not equal[-1]:
                raise RuntimeError("unchanged R25 fallback changed complete model bytes")
            if route == "exact_lower_hold" and not stage_info["partition"]["proved"]:
                raise RuntimeError("missing complete partition proof")
            if route == "exact_reachable_vertices" and not stage_info["alignment"]["proved"]:
                raise RuntimeError("missing complete prefix-palette proof")
        if all(equal):
            candidate, result_path = baseline, path
            reuse = "R25 actual CPU/CUDA cube and 100-frame evidence reused by complete model byte equality and all input/executable hashes"
        else:
            candidate, result_path = _accept(models, source, scenario, m, "adaptive", output, cpu, cuda)
            reuse = "fresh actual CPU/CUDA whole-cube and 100-frame acceptance"
        compared = _comparison(baseline, candidate)
        report["cases"].append({"scenario": scenario, "m": m, "models": list(map(str, models)), "routes": routes,
            "model_byte_equal_to_r25": equal, "execution_evidence": reuse,
            "baseline_models": list(map(str, old_paths)), "result": str(result_path), "result_sha256": metrics.file_sha256(result_path),
            "baseline_result": str(path), "baseline_sha256": old["result_sha256"], "candidate_fit": current, "comparison": compared})
        _write_report(target, report)
        mean, maximum = compared["cube"]["mean"], compared["cube"]["max"]
        print(f"[adaptive] {scenario}/m{m}: {routes}; mean {mean['baseline']:.6f}->{mean['candidate']:.6f}; "
            f"max {maximum['baseline']:.6f}->{maximum['candidate']:.6f}; reused={all(equal)}", flush=True)
    for name, digest in {**report["executable_sha256"], **report["frozen_baselines"], **guarded}.items():
        if metrics.file_sha256(name) != digest:
            raise RuntimeError("runtime or input changed during stage")
    for name, digest in sources.items():
        if metrics.file_sha256(ROOT / name) != digest:
            raise RuntimeError(f"study source changed: {name}")
    if fullfit.trainer_fingerprint() != trainer:
        raise RuntimeError("native trainer changed")
    report.update(finished_utc=datetime.now(timezone.utc).isoformat(), elapsed_seconds=time.perf_counter() - started,
        structural_parity_partition_and_palette_pass=True, unchanged_input_sha256=guarded)
    _write_report(target, report)


if __name__ == "__main__":
    main()
