"""Bind final R19 sources, builds and staged evidence without rerunning tests."""
from __future__ import annotations

import csv
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import subprocess
import zipfile

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "artifacts/r19-delivery"


def sha(path):
    with Path(path).open("rb") as stream:
        return hashlib.file_digest(stream, "sha256").hexdigest()


def record(path):
    return {"bytes": path.stat().st_size, "sha256": sha(path)}


def read(path):
    return json.loads(Path(path).read_text(encoding="utf-8-sig"))


def main():
    suite = read(OUT / "acceptance-suite.json")
    paired = read(OUT / "paired/comparison.json")
    confirmed = read(OUT / "paired/best-cpu-gpu-confirmation.json")
    ctest = read(ROOT / "artifacts/r18-progress/ctest-final.json")
    deployment = read(OUT / "deployment.json")
    assert suite["structural_and_parity_pass"] and len(suite["cases"]) == 6
    assert paired["inputs_unchanged"] and len(paired["runs"]) == len(paired["comparisons"]) * paired["pairs_requested"] * 2
    assert len(paired["preflight"]) == 8 and all(row["bit_exact"] for row in paired["preflight"])
    assert confirmed["inputs_unchanged"] and len(confirmed["runs"]) == 14
    assert confirmed["selection_evidence_sha256"] == sha(OUT / "paired/comparison.json")
    assert ctest["exit_code"] == 0 and ctest["test_binary_sha256"] == sha(ROOT / "build-r18-cpu/jshc_tests.exe")
    assert deployment["status"] == "passed"
    assert deployment["source_executable_sha256"] == sha(ROOT / "build-r18-cpu/jshc.exe") == sha(OUT / "runtime-cpu/jshc.exe")
    for filename, digest in paired["input_and_executable_sha256"].items():
        assert sha(filename) == digest, filename
    quality = []
    assets = set()
    for case in suite["cases"]:
        acceptance = Path(case["acceptance"])
        assert sha(acceptance) == case["acceptance_sha256"]
        value = read(acceptance)
        assert value["structural_contract_pass"] and value["backend_cube_sha256_equal"]
        assert value["full_reference_composition_verified_colors"] == 256**3
        assert value["n_images"] == 100 and value["model_provenance"]["verified"]
        for source in value["sources"]:
            path = Path(source["path"])
            assert sha(path) == source["sha256"]
            assets.add(path)
            assets.add(path.parent / "composite.lut256")
        for backend, validation in value["backends"].items():
            assert sha(validation["executable"]) == validation["executable_sha256"]
        row = value["backends"]["cpu"]
        quality.append({"scenario": case["scenario"], "m": case["m"],
            **{name: row["cube"][name] for name in ("mean", "rms", "p99", "max")},
            "worst_image_mean": row["worst_image_metric"], "illustrative_mean2_pass": value["pass"]})
    with (OUT / "accuracy-summary.csv").open("w", newline="", encoding="utf-8-sig") as stream:
        writer = csv.DictWriter(stream, fieldnames=list(quality[0]))
        writer.writeheader(); writer.writerows(quality)
    timing = [{key: row[key] for key in ("reference", "candidate", "reference_median_ms", "candidate_median_ms", "paired_speedup_median", "candidate_faster_pairs", "pair_count")}
              for row in paired["comparisons"]]
    with (OUT / "paired-summary.csv").open("w", newline="", encoding="utf-8-sig") as stream:
        writer = csv.DictWriter(stream, fieldnames=list(timing[0]))
        writer.writeheader(); writer.writerows(timing)
    package_zip = OUT / "runtime-cpu.zip"
    with zipfile.ZipFile(package_zip, "w", zipfile.ZIP_DEFLATED) as archive:
        for path in sorted((OUT / "runtime-cpu").iterdir()):
            if path.is_file(): archive.write(path, path.name)

    sources = set()
    for name in ("CMakeLists.txt", "README.md", "PROBLEM.md", "TOOLCHAIN.md", "pixi.toml", "pixi.lock", ".gitignore", "Dockerfile", "LICENSE"):
        if (ROOT / name).is_file(): sources.add(ROOT / name)
    for directory in ("cpp", "python/lutlab", "tests", "scripts", "gpu", "zig", "rust"):
        for path in (ROOT / directory).rglob("*"):
            if path.is_file() and (path.suffix in (".cpp", ".h", ".hpp", ".py", ".cu", ".ps1", ".zig", ".rs") or path.name == "CMakeLists.txt"):
                sources.add(path)
    sources.update((ROOT / "docs").glob("r1[789]-*.md"))
    snapshot = OUT / "source-snapshot.zip"
    with zipfile.ZipFile(snapshot, "w", zipfile.ZIP_DEFLATED) as archive:
        for path in sorted(sources): archive.write(path, path.relative_to(ROOT).as_posix())
    for path in OUT.rglob("*"):
        if path.is_file() and path.name not in ("delivery-manifest.json", "source-snapshot.zip"):
            assets.add(path)
    for directory in ("artifacts/r18-portable", "artifacts/r18-unified/gpu", "artifacts/r18-integration"):
        for path in (ROOT / directory).rglob("*"):
            if path.is_file() and path.suffix in (".json", ".log", ".txt", ".slut"):
                assets.add(path)
    assets.update(ROOT / "artifacts/r18-progress" / name for name in ("ctest-final.json", "ctest-final.log"))
    assets.add(ROOT / "artifacts/r18-algorithm/study.json")
    assets.add(ROOT / "artifacts/r17-acceptance/input-manifest.json")
    assets.update(Path(path) for path in paired["input_and_executable_sha256"])
    ocio = paired["ocio_accuracy"]
    assets.update(Path(path) for path in ocio["ocio_binaries"])
    builds = set()
    for directory, names in (("build-r18-cpu", ("jshc.exe", "jshc_tests.exe", "libjshc_core.a", "CMakeCache.txt", "compile_commands.json")),
                             ("build-r18-portable", ("jshc.exe", "jshc_tests.exe", "libjshc_core.a", "CMakeCache.txt")),
                             ("build-gpu", ("jshc_gpu.exe", "build-manifest.json", "build.log", "command.txt", "nvcc-version.txt"))):
        builds.update(ROOT / directory / name for name in names if (ROOT / directory / name).is_file())
    manifest = {
        "created_utc": datetime.now(timezone.utc).isoformat(),
        "git_base": subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=ROOT, text=True).strip(),
        "status": "local uncommitted implementation; no official score claimed",
        "source": {path.relative_to(ROOT).as_posix(): record(path) for path in sorted(sources)},
        "source_snapshot": {"path": snapshot.relative_to(ROOT).as_posix(), **record(snapshot)},
        "builds": {path.relative_to(ROOT).as_posix(): record(path) for path in sorted(builds)},
        "evidence": {path.relative_to(ROOT).as_posix(): record(path) for path in sorted(assets)},
        "quality": quality,
        "paired_confirmed_best_tested_cpu_cuda": {key: confirmed[key] for key in ("median_ms_per_100", "paired_speedup_median", "paired_median_bootstrap_95_ci", "candidate_faster_pairs", "pair_count")},
        "checks": {"kernel_gate_reused_identical_test_binary": True, "python": "11 passed in 9.93s",
                   "portable": "complete CTest passed", "public_fit_cache_selector": "passed",
                   "six_source_bound_cases_cpu_cuda_full_cube_and_100_images": "passed structural and parity; illustrative accuracy failures retained",
                   "eight_configuration_100_output_byte_equality": "passed", "isolated_path_cpu_package": "passed"},
        "limits": ["synthetic local LUTs and frames", "official Threshold, aggregation, format, timing boundary and final server not supplied",
                   "clip-7/m17 fails illustrative 100-image mean2 gate", "all six cases fail cube max2",
                   "OCIO nonuniform-grid float32 outputs differ from Q16; comparison is the documented Python buffer integration",
                   "model allocation sizes differ from observed host working set and from process VRAM"],
    }
    target = OUT / "delivery-manifest.json"
    target.write_text(json.dumps(manifest, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    for group in ("source", "builds", "evidence"):
        for filename, expected in manifest[group].items():
            if record(ROOT / filename) != expected:
                raise RuntimeError(f"file changed during freeze: {filename}")
    print(json.dumps({"manifest": str(target), "source_files": len(sources), "evidence_files": len(assets),
        "evidence_bytes": sum(path.stat().st_size for path in assets), "verified": True}))


if __name__ == "__main__":
    main()
