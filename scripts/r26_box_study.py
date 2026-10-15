"""One serial box-LS qualification on all thirteen frozen R25 model cases.

The native full-domain operator, pixel runtimes and input corpus are unchanged.
The old full-colour COO oracle is reused only after checking its native source,
wrapper, test and library hashes, and the reference assembler's function text.
Every 3D stage must pass KKT and exact integer-objective checks; the reconstructed
R25 baseline nodes and all 1D routes must match the frozen models byte for byte.
"""
from __future__ import annotations

import argparse
import ast
from datetime import datetime, timezone
import hashlib
import json
import os
from pathlib import Path
import sys
import time
import zipfile

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "python"))
from lutlab import box, cache, fullfit, io, metrics, runtime
from lutlab.entry import _write_report
from r21_boundary_study import _accept, _comparison, _fit
from r24_supported_study import _fit_record

CASES = [("isp-0", 18), ("clip-7", 17), ("clip-7", 18), ("clip-7", 33),
         ("warp-7", 18), ("isp-19", 18), ("clip-23", 18), ("film-11", 18), ("stress-13", 33),
         ("isp-29", 18), ("clip-31", 18), ("clip-23", 33), ("clip-31", 33)]


def _function_text(source, name):
    source = source.replace("\r\n", "\n")
    tree = ast.parse(source)
    node = next(n for n in tree.body if isinstance(n, ast.FunctionDef) and n.name == name)
    return ast.get_source_segment(source, node)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--cpu", type=Path, required=True)
    parser.add_argument("--cuda", type=Path, required=True)
    parser.add_argument("--output", type=Path, default=ROOT / "artifacts/r26-box")
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
        raise RuntimeError("requires the completed R25 corpus")
    trainer = fullfit.trainer_fingerprint()
    if trainer != prior["trainer"]:
        raise RuntimeError("native trainer changed; cannot reuse the previous all-colour oracle")
    unchanged = ("python/lutlab/fullfit.py", *fullfit.NATIVE_SOURCES, "tests/test_fullfit_contract.py")
    for name in unchanged:
        if metrics.file_sha256(ROOT / name) != prior["source_sha256"][name]:
            raise RuntimeError(f"full-domain oracle dependency changed: {name}")
    snapshot = ROOT / "artifacts/r25-full/source-snapshot.zip"
    with zipfile.ZipFile(snapshot) as archive:
        reference_source = archive.read("python/lutlab/fit.py").decode("utf-8")
    assembler = _function_text((ROOT / "python/lutlab/fit.py").read_text(encoding="utf-8"), "normal_equations")
    if assembler != _function_text(reference_source, "normal_equations"):
        raise RuntimeError("independent COO assembler changed")
    known = {(c["scenario"], c["m"]): c for c in prior["cases"]}
    known.update({(c["scenario"], c["candidate_m"]): c for c in capacity["cases"]})
    sources = {f"python/lutlab/{name}": digest for name, digest in cache.source_fingerprint().items() if name != "pixi.lock"}
    sources.update({name: metrics.file_sha256(ROOT / name) for name in (
        "pixi.lock", *fullfit.NATIVE_SOURCES, "python/lutlab/validation.py", "python/lutlab/qualification.py",
        "scripts/r21_boundary_study.py", "scripts/r24_supported_study.py", "scripts/r26_box_study.py",
        "tests/test_box_contract.py", "tests/test_cache_contract.py")})
    report = {"started_utc": datetime.now(timezone.utc).isoformat(), "scope": __doc__, "source_sha256": sources,
        "predeclared_cases": CASES, "method": "ls_tetra_full_box", "trainer": trainer,
        "official_score_available": False, "new_data_generated": False,
        "frozen_baselines": {str(p): metrics.file_sha256(p) for p in (prior_path, capacity_path)},
        "reused_native_oracle": {"r25_pytest_returncode": prior["python_acceptance"]["returncode"],
            "unchanged_source_sha256": {name: prior["source_sha256"][name] for name in unchanged},
            "reference_assembler_function_sha256": hashlib.sha256(assembler.encode()).hexdigest(),
            "function_text_normalisation": "CRLF to LF; function text otherwise identical",
            "snapshot_sha256": metrics.file_sha256(snapshot), "library_sha256": trainer["library_sha256"]},
        "executable_sha256": {str(p): metrics.file_sha256(p) for p in (cpu, cuda)}, "fit_executions": [], "cases": []}
    target = output / "study.json"
    _write_report(target, report)
    # The native operator did not change; do not rerun its expensive full COO
    # oracle. The new QP and integer-guard oracle plus integration checks run once.
    command = [sys.executable, "-m", "pytest", "-q", "tests", "--ignore=tests/test_fullfit_contract.py"]
    check = runtime._execute(command)
    (output / "pytest.log").write_text(check["stdout"] + check["stderr"], encoding="utf-8")
    report["python_acceptance"] = {"command": command, **{k: v for k, v in check.items() if k not in ("stdout", "stderr")}}
    _write_report(target, report)
    print(check["stdout"], flush=True)
    if check["returncode"]:
        raise RuntimeError("box solver/oracle acceptance failed")
    for scenario, m in CASES:
        old = known[(scenario, m)]
        path = Path(old["result"])
        if metrics.file_sha256(path) != old["result_sha256"]:
            raise RuntimeError("frozen R25 accuracy result changed")
        baseline = json.loads(path.read_text(encoding="utf-8"))
        source = Path(baseline["sources"][0]["path"]).parent
        old_paths = list(map(Path, old["models"]))
        old_models = [io.load_sparse(p, competition=True) for p in old_paths]
        for name, digest in baseline["backends"]["cpu"]["model_sha256"].items():
            if metrics.file_sha256(name) != digest:
                raise RuntimeError("frozen R25 model changed")
        models = _fit(source, scenario, m, "ls_tetra_full_box", output, report["fit_executions"])
        current = _fit_record(models)
        decisions = []
        for model_path, reference, stage in zip(models, old_models, current["fit"]["stage_info"]):
            model = io.load_sparse(model_path, competition=True)
            if not (model.grid == reference.grid).all() or any(not (a == b).all() for a, b in zip(model.tables(), reference.tables())):
                raise RuntimeError("fixed-grid fitting changed its axes")
            detail = stage["structured"]
            if detail["route"] == "verified_axis_separable":
                if not (model.nodes == reference.nodes).all():
                    raise RuntimeError("unchanged 1D fit changed its frozen node bytes")
            else:
                ls = detail["least_squares"]
                qp, selection = ls["box_solver"], ls["integer_objective_selection"]
                if (qp["status"] != "converged_by_kkt" or not qp["feasible"]
                        or qp["scaled_projected_gradient_inf"] > qp["scaled_kkt_tolerance"]
                        or selection["baseline_node_sha256"] != hashlib.sha256(reference.nodes.tobytes()).hexdigest()
                        or ls["trainer"] != trainer or ls["sample_count"] != 256 ** 3):
                    raise RuntimeError("KKT, source, or R25 reconstruction gate failed")
                numerator = int(selection["candidate_sse_change_numerator"])
                if selection["accepted"] != (numerator < 0):
                    raise RuntimeError("integer-objective selection disagrees with exact numerator")
                if not selection["accepted"] and not (model.nodes == reference.nodes).all():
                    raise RuntimeError("rejected integer candidate did not retain R25 nodes")
                decisions.append(selection)
        candidate, result_path = _accept(models, source, scenario, m, "box", output, cpu, cuda)
        compared = _comparison(baseline, candidate)
        report["cases"].append({"scenario": scenario, "m": m, "models": list(map(str, models)),
            "baseline_models": list(map(str, old_paths)), "result": str(result_path), "result_sha256": metrics.file_sha256(result_path),
            "baseline_result": str(path), "baseline_sha256": old["result_sha256"], "comparison": compared,
            "candidate_fit": current, "integer_selections": decisions})
        _write_report(target, report)
        mean, maximum = compared["cube"]["mean"], compared["cube"]["max"]
        print(f"[box] {scenario}/m{m}: mean {mean['baseline']:.6f}->{mean['candidate']:.6f}; "
              f"max {maximum['baseline']:.6f}->{maximum['candidate']:.6f}", flush=True)
    for name, digest in sources.items():
        if metrics.file_sha256(ROOT / name) != digest:
            raise RuntimeError(f"box study source changed: {name}")
    for name, digest in {**report["executable_sha256"], **report["frozen_baselines"]}.items():
        if metrics.file_sha256(name) != digest:
            raise RuntimeError("box-study runtime or frozen baseline changed")
    if fullfit.trainer_fingerprint() != trainer:
        raise RuntimeError("native trainer changed")
    report.update(finished_utc=datetime.now(timezone.utc).isoformat(), elapsed_seconds=time.perf_counter() - started,
                  structural_parity_kkt_and_integer_guard_pass=True)
    _write_report(target, report)


if __name__ == "__main__":
    main()
