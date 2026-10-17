"""One staged qualification and paired timing gate for the R33 stress candidate.

The predeclared comparisons use the same executable, images, thread count and
batch settings within each pair. All seven AB/BA pairs are retained. Timings
exclude fitting, decoding, allocation and encoding; CUDA includes ordinary host
copies and transfers. This is one known tuning case, not a class survey or an
official score. Full-cube numerical results must reproduce the completed pilot.
"""
from __future__ import annotations

from datetime import datetime, timezone
import json
import os
from pathlib import Path
import statistics
import sys
import tempfile

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "python"))
sys.path.insert(0, str(ROOT))
import numpy as np
from lutlab import casebook, corpus, io, performance, runtime, validation
from lutlab.entry import _write_report
from scripts.r30_portable_stage import Prepared, load_library


def main():
    output = ROOT / "artifacts/r34-candidate"
    output.mkdir(exist_ok=True)
    result = output / "stage.json"
    if result.exists():
        raise RuntimeError("preserve the existing attempt; choose a new epoch before rerunning")
    lease = ROOT / "artifacts/r29-matrix/phase-controller.lock"
    with lease.open("x", encoding="utf-8") as stream:
        json.dump({"pid": os.getpid(), "owner": "R34 exclusive qualification/timing and canonical writer"}, stream)
    try:
        run(output, result)
    finally:
        lease.unlink()


def run(output, result):
    pilot_path = ROOT / "artifacts/r33-axis-bins/study.json"
    pilot = json.loads(pilot_path.read_text(encoding="utf-8"))
    if not pilot["pass"]:
        raise RuntimeError("requires a completed R33 pilot")
    candidate = next(row for row in pilot["cases"] if row["case_id"] == "legacy-stress-13" and row["profile"] == "lookahead_bins")
    models = [casebook._path(path) for path in candidate["models"]]
    old_path = casebook._path(pilot["reused_baseline"]["evidence"])
    old = json.loads(old_path.read_text(encoding="utf-8"))
    if corpus.digest_file(old_path) != pilot["reused_baseline"]["sha256"]:
        raise RuntimeError("historical acceptance evidence changed")
    baseline = [casebook._path(path) for path in old["backends"]["cpu"]["model_sha256"]]
    sources = [casebook._path(row["path"]) for row in old["sources"]]
    truth = sources[0].parent / "composite.lut256"
    listing = ROOT / "data/corpus-v1/benchmark100.txt"
    frames = [Path(line) for line in listing.read_text(encoding="utf-8").splitlines() if line]
    photos_path = ROOT / "datasets/problem16-photos-v1/catalog.json"
    photos = json.loads(photos_path.read_text(encoding="utf-8"))
    photo_paths = [ROOT / row["path"] for row in photos["images"]]
    cpu = ROOT / "build-r32-format-cpu/jshc.exe"
    cuda = ROOT / "build-r32-format-gpu/jshc_gpu.exe"
    portable = ROOT / "build-r30-portable/libjshc_portable.dll"
    source_names = ["scripts/r34_candidate_stage.py", "python/lutlab/runtime.py", "python/lutlab/validation.py",
                    "python/lutlab/performance.py", "python/lutlab/casebook.py", "scripts/r30_portable_stage.py",
                    "portable/src/jshc_portable.c", "portable/include/jshc_portable.h"]
    source_hashes = {name: corpus.digest_file(ROOT / name) for name in source_names}
    format_proof_path = ROOT / "artifacts/r32-formats/stage.json"
    tracked = [pilot_path, old_path, truth, listing, photos_path, format_proof_path, cpu, cuda, portable,
               *models, *baseline, *sources, *frames, *photo_paths]
    hashes = {str(path): corpus.digest_file(path) for path in tracked}
    pilot_observation = json.loads(casebook._path(candidate["observation"]).read_text())
    if ([hashes[str(path)] for path in models] != pilot_observation["model_sha256"]
            or [hashes[str(path)] for path in baseline] != list(old["backends"]["cpu"]["model_sha256"].values())):
        raise RuntimeError("candidate or baseline model bytes differ from measured evidence")
    if len(frames) != 100 or len(set(hashes[str(path)] for path in frames)) != 100:
        raise RuntimeError("requires 100 distinct frozen image contents")
    for row, path in zip(photos["images"], photo_paths):
        if hashes[str(path)] != row["file_sha256"]:
            raise RuntimeError("registered photo bytes changed")
    if hashes[str(truth)] != old["reference_sha256"]:
        raise RuntimeError("truth differs from the frozen source chain")
    parameters = {"OMP_DYNAMIC": "FALSE", "OMP_PROC_BIND": "FALSE", "OMP_THREAD_LIMIT": "32",
                  "OMP_SCHEDULE": "STATIC", "JSHC_BLOCK_PIXELS": "4096", "OPENBLAS_NUM_THREADS": "1",
                  "MKL_NUM_THREADS": "1", "OMP_NUM_THREADS": "1"}
    cleared = ["OMP_PLACES", "GOMP_CPU_AFFINITY"]
    for name in cleared:
        os.environ.pop(name, None)
    os.environ.update(parameters)
    configurations = {
        "baseline_cpu_gather16": (baseline, dict(backend="cpu", executable=cpu, kernel="tetra_avx2_scalar_gather", threads=16, batch=True)),
        "candidate_cpu_gather16": (models, dict(backend="cpu", executable=cpu, kernel="tetra_avx2_scalar_gather", threads=16, batch=True)),
        "baseline_cuda100": (baseline, dict(backend="cuda", executable=cuda, batch=100)),
        "candidate_cuda100": (models, dict(backend="cuda", executable=cuda, batch=100)),
        "candidate_cpu_scalar16": (models, dict(backend="cpu", executable=cpu, kernel="tetra_scalar", threads=16, batch=True)),
    }
    comparisons = [("baseline_cpu_gather16", "candidate_cpu_gather16"),
                   ("baseline_cuda100", "candidate_cuda100"),
                   ("candidate_cpu_scalar16", "candidate_cpu_gather16")]
    report = {"started_utc": datetime.now(timezone.utc).isoformat(), "scope": __doc__, "pass": False,
              "official": False, "class_sweet_zone_proven": False, "source_sha256": source_hashes,
              "input_and_binary_sha256": hashes, "environment": parameters, "cleared_environment": cleared,
              "cpu_capabilities": runtime.capabilities("cpu", cpu), "cuda_capabilities": runtime.capabilities("cuda", cuda),
              "local_threshold": {"value": 2., "metric": "mean", "strict": True, "official": False},
              "error_formula": "sqrt((R_pred-R_true)^2+(G_pred-G_true)^2+(B_pred-B_true)^2), RGB8 units; not CIE Lab Delta E",
              "predeclared_comparisons": comparisons, "pairs": 7, "seed": 2026101634,
              "configurations": {name: {"models": list(map(str, paths)),
                  **{key: str(value) if isinstance(value, Path) else value for key, value in config.items()}}
                  for name, (paths, config) in configurations.items()},
              "timing_scope": "ordinary host RGB8 input to ordinary host RGB8 output; resident decoded images and allocations; CUDA transfers/copies included",
              "timing_excludes": ["fitting", "model load", "decode", "allocation", "encoding", "checksums"],
              "affinity": "OS scheduler, no pinning", "runs": [], "comparisons": []}
    _write_report(result, report)
    acceptance = {"sources": old["sources"], "reference_sha256": old["reference_sha256"],
                  "structural_contract_pass": io.inspect_submission_contract(models, semantics="independent")["pass"],
                  "official": False, "backends": {}, "source_epoch": "R33 fitted models, R32 format-fixed native runtimes"}
    for backend, exe in (("cpu", cpu), ("cuda", cuda)):
        value = validation.validate(models, truth, listing, kernel="tetra_avx2" if backend == "cpu" else "cuda_q16_fused4",
                                    threads=4 if backend == "cpu" else 0, threshold=2., full_cube=True, executable=exe,
                                    constraint_scope="both", competition=True, backend=backend)
        if value["cube"] != candidate["cube"]:
            # The top-k list depends on the configured size; compare complete scalar statistics.
            if any(value["cube"][key] != candidate["cube"][key] for key in ("n_colors", "mean", "rms", "p99", "max", "pixels_at_or_above_threshold")):
                raise RuntimeError("new executable/candidate differs from the completed full-cube pilot")
        if not value["submission_contract_pass"] or not value["image_execution_verified"]:
            raise RuntimeError("image path or structural contract failed")
        acceptance["backends"][backend] = value
        _write_report(output / "acceptance.json", acceptance)
        print(f"[qualification] {backend}: 100 native images, worst mean={value['worst_image_metric']:.9f}", flush=True)
    acceptance["backend_cube_sha256_equal"] = len({value["mapped_cube_sha256"] for value in acceptance["backends"].values()}) == 1
    acceptance["backend_images_sha256_equal"] = len({value["mapped_images_sha256"] for value in acceptance["backends"].values()}) == 1
    if not acceptance["backend_cube_sha256_equal"] or not acceptance["backend_images_sha256_equal"]:
        raise RuntimeError("CPU/CUDA byte equality failed")
    _write_report(output / "acceptance.json", acceptance)
    library = load_library(portable.resolve())
    prepared = Prepared(library, models)
    photo_records = []
    with validation._mapped_full(truth) as reference, tempfile.TemporaryDirectory(prefix="r34-photo-") as temporary:
        for photo, path in zip(photos["images"], photo_paths):
            image = io.load_image(path)
            expected = prepared.apply(image)
            if not np.array_equal(expected, prepared.apply(image, generic=True)):
                raise RuntimeError("portable shortcut and generic outputs differ for new bin geometry")
            row = {"id": photo["id"], "quality": validation._stats(expected, io.apply_full(reference, image))[0],
                   "input_sha256": hashes[str(path)], "portable_optimized_equals_generic": True, "backends": {}}
            for backend, exe in (("cpu", cpu), ("cuda", cuda)):
                destination = Path(temporary) / (backend + ".png")
                value = runtime.apply(models, path, destination, backend=backend, executable=exe, competition=True,
                                      threads=4 if backend == "cpu" else 0)
                if not np.array_equal(io.load_image(destination), expected):
                    raise RuntimeError("natural-photo native and portable output bytes differ")
                row["backends"][backend] = value
            photo_records.append(row)
    report["photos5"] = {"rows": photo_records, "cohort_sha256": photos["cohort_sha256"],
                         "known_family": True, "is_100_image_qualification": False,
                         "portable_stage_paths": list(prepared.chain.path), "portable_effective_one_hot": list(prepared.chain.effective_one_hot)}
    _write_report(result, report)
    print("[qualification] five natural photos: CPU/CUDA/C99 optimized/generic byte equality", flush=True)
    # One preflight per distinct configuration; comparison-specific model errors
    # are allowed, whereas kernel alternatives for the same model must be exact.
    report["preflight"] = []
    with tempfile.TemporaryDirectory(prefix="r34-preflight-") as temporary:
        candidate_hash = acceptance["backends"]["cpu"]["mapped_images_sha256"]
        format_proof = json.loads(format_proof_path.read_text())
        if not format_proof["pass"]:
            raise RuntimeError("baseline image proof was not successful")
        old_hash = format_proof["valid_100_images"]["cpu"]["images_sha256"]
        report["baseline_preflight_proof"] = {"path": "artifacts/r32-formats/stage.json", "sha256": hashes[str(format_proof_path)]}
        for name, (paths, config) in configurations.items():
            raw = Path(temporary) / "output.rgb"
            value = runtime.verify(paths, listing, competition=True, output=raw, **config)
            digest = corpus.digest_file(raw)
            expected = old_hash if name.startswith("baseline") else candidate_hash
            if raw.stat().st_size != 100 * 1024 * 768 * 3 or digest != expected:
                raise RuntimeError("paired timing preflight differs from the qualified model outputs")
            report["preflight"].append({"configuration": name, "output_sha256": digest, "runtime": value})
    _write_report(result, report)
    rng = np.random.default_rng(report["seed"])
    for pair in range(report["pairs"]):
        for comparison_index in rng.permutation(len(comparisons)):
            a, b = comparisons[int(comparison_index)]
            order = [a, b] if (pair + int(comparison_index)) % 2 == 0 else [b, a]
            for name in order:
                paths, config = configurations[name]
                value = runtime.bench(paths, listing, reps=1, competition=True, **config)
                elapsed = value["set_ms_p50_rep"] if config["backend"] == "cpu" else value["set_host_wall_ms_p50"]
                if not np.isfinite(elapsed) or elapsed <= 0:
                    raise RuntimeError("invalid host timing")
                report["runs"].append({"comparison": [a, b], "pair": pair, "order": order,
                                       "configuration": name, "host_to_host_ms": elapsed, "runtime": value})
                _write_report(result, report)
        print(f"[paired] round {pair+1}/7 complete, all observations retained", flush=True)
    for index, (a, b) in enumerate(comparisons):
        rows = [row for row in report["runs"] if row["comparison"] == [a, b]]
        ratios = []
        for pair in range(report["pairs"]):
            values = {row["configuration"]: row["host_to_host_ms"] for row in rows if row["pair"] == pair}
            ratios.append(values[a] / values[b])
        report["comparisons"].append({"reference": a, "candidate": b,
            "reference_median_ms": statistics.median(row["host_to_host_ms"] for row in rows if row["configuration"] == a),
            "candidate_median_ms": statistics.median(row["host_to_host_ms"] for row in rows if row["configuration"] == b),
            **performance._paired_statistics(ratios, report["seed"] + index)})
    for path, digest in hashes.items():
        if corpus.digest_file(Path(path)) != digest:
            raise RuntimeError("frozen input or binary changed")
    for name, digest in source_hashes.items():
        if corpus.digest_file(ROOT / name) != digest:
            raise RuntimeError("gate source changed")
    primary = output / "acceptance.json"
    value = json.loads(casebook._path(candidate["observation"]).read_text())
    cpu_result = acceptance["backends"]["cpu"]
    value.update(cube=cpu_result["cube"], images={"count": 100, "native_verified": True,
        "list_sha256": cpu_result["image_list_sha256"], "worst_mean": cpu_result["worst_image_metric"],
        "illustrative_mean_pass": all(row["mean"] < 2 for row in cpu_result["per_image"]) and cpu_result["cube"]["mean"] < 2,
        "cpu_cuda_byte_equal": True}, evidence=[{"path": str(primary), "sha256": corpus.digest_file(primary)}])
    observation = output / "observation.json"
    _write_report(observation, value)
    book = casebook.Casebook(ROOT / "datasets/problem16-v1/casebook")
    report["qualified_observation_id"] = book.record(observation)
    _write_report(book.root / "summary.json", book.summary())
    report.update(inputs_unchanged=True, pass_=True, finished_utc=datetime.now(timezone.utc).isoformat())
    report["pass"] = report.pop("pass_")
    _write_report(result, report)
    print(json.dumps({"pass": True, "comparisons": report["comparisons"]}), flush=True)


if __name__ == "__main__":
    main()
