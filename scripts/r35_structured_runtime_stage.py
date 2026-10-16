"""Concentrated correctness/deployment gate for the C99/native structured bridge.

Build three feature configurations. Run one complete C++ oracle phase gate in
each of the SIMD and no-SIMD/no-OpenMP builds; the C99-disabled compatibility
build verifies explicit capability rejection. Four frozen real model sets must
match previous full RGB outputs through both new kernels. The new stress model
also consumes the actual 100-image and five-photo paths. No timing here is a
performance benchmark: independent baseline fit workers may be running.
"""
from __future__ import annotations

from datetime import datetime, timezone
import json
from pathlib import Path
import shutil
import sys
import tempfile

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "python"))
import numpy as np
from lutlab import casebook, corpus, io, runtime, validation
from lutlab.entry import _write_report


def main():
    output = ROOT / "artifacts/r35-structured-runtime"
    output.mkdir(exist_ok=True)
    target = output / "stage.json"
    if target.exists():
        raise RuntimeError("preserve the existing attempt; select an explicit new epoch before rerunning")
    names = ["CMakeLists.txt", "cpp/include/jshc/lut.hpp", "cpp/include/jshc/image_contract.hpp",
             "cpp/src/lut.cpp", "cpp/src/lut_simd_avx2.cpp", "cpp/src/lut_simd_avx2.hpp",
             "cpp/src/portable_bridge.cpp", "cpp/src/portable_bridge.hpp", "cpp/src/main.cpp",
             "cpp/src/fit_r14.cpp", "cpp/tests/test_kernels.cpp", "portable/src/jshc_portable.c",
             "portable/include/jshc_portable.h", "python/lutlab/runtime.py", "python/lutlab/entry.py",
             "python/lutlab/io.py", "python/lutlab/validation.py", "scripts/r35_structured_runtime_stage.py"]
    source_hashes = {name: corpus.digest_file(ROOT / name) for name in names}
    r30path = ROOT / "artifacts/r30-portable/stage.json"
    r33path = ROOT / "artifacts/r33-axis-bins/study.json"
    r34path = ROOT / "artifacts/r34-candidate/stage.json"
    r34accept = ROOT / "artifacts/r34-candidate/acceptance.json"
    r30, r33, r34, accepted = [json.loads(path.read_text(encoding="utf-8")) for path in (r30path, r33path, r34path, r34accept)]
    if not all(value["pass"] for value in (r30, r33, r34)):
        raise RuntimeError("requires completed source studies")
    if any(source_hashes[name] != r30["source_sha256"][name] for name in
           ("portable/src/jshc_portable.c", "portable/include/jshc_portable.h")):
        raise RuntimeError("this bridge stage must keep the certified standalone C99 engine unchanged")
    cases = []
    first = r30["historical_cubes"][0]
    cases.append({"name": "historical-clip-m17", "models": list(first["models_sha256"]),
                  "model_sha256": list(first["models_sha256"].values()), "cube_sha256": first["mapped_cube_sha256"],
                  "evidence": first["evidence"], "evidence_sha256": first["evidence_sha256"], "paths": first["paths"]})
    prior = casebook._path(r33["reused_baseline"]["evidence"])
    old = json.loads(prior.read_text(encoding="utf-8"))
    cases.append({"name": "historical-stress-m33", "models": list(old["backends"]["cpu"]["model_sha256"]),
                  "model_sha256": list(old["backends"]["cpu"]["model_sha256"].values()),
                  "cube_sha256": old["backends"]["cpu"]["mapped_cube_sha256"], "evidence": str(prior),
                  "evidence_sha256": r33["reused_baseline"]["sha256"], "paths": [1, 1, 2, 0]})
    selected = [next(row for row in r33["cases"] if row["case_id"] == "legacy-stress-13" and row["profile"] == "lookahead_bins"),
                next(row for row in r33["cases"] if row["case_id"].startswith("axis_bin_capacity-bins17-") and row["profile"] == "adaptive_bins")]
    for row, name in zip(selected, ("new-stress-m33", "new-bins17-m17")):
        observation_path = casebook._path(row["observation"])
        if corpus.digest_file(observation_path) != row["observation_sha256"]:
            raise RuntimeError("R33 normalized measurement changed")
        observation = json.loads(observation_path.read_text())
        primary_path = casebook._path(observation["evidence"][0]["path"])
        if corpus.digest_file(primary_path) != observation["evidence"][0]["sha256"]:
            raise RuntimeError("R33 primary execution changed")
        primary = json.loads(primary_path.read_text())
        cases.append({"name": name, "models": row["models"], "model_sha256": observation["model_sha256"],
                      "cube_sha256": primary["output_sha256"], "evidence": str(primary_path),
                      "evidence_sha256": corpus.digest_file(primary_path), "paths": [1, 1, 2, 0] if name == "new-stress-m33" else None})
    listing = ROOT / "data/corpus-v1/benchmark100.txt"
    frames = [Path(line) for line in listing.read_text(encoding="utf-8").splitlines() if line]
    photos_path = ROOT / "datasets/problem16-photos-v1/catalog.json"
    photos = json.loads(photos_path.read_text(encoding="utf-8"))
    truth_path = casebook._path(accepted["sources"][0]["path"]).parent / "composite.lut256"
    tracked = [r30path, r33path, r34path, r34accept, listing, photos_path, truth_path,
               ROOT / "artifacts/r31-arm-execution/stage.json", *frames, *(ROOT / row["path"] for row in photos["images"])]
    for row in cases:
        row["models"] = [casebook._path(path) for path in row["models"]]
        if [corpus.digest_file(path) for path in row["models"]] != row["model_sha256"]:
            raise RuntimeError("model bytes changed")
        evidence = casebook._path(row["evidence"])
        if corpus.digest_file(evidence) != row["evidence_sha256"]:
            raise RuntimeError("prior execution proof changed")
        tracked.extend([evidence, *row["models"]])
    tracked.extend(ROOT / path for path in ("build-r18-cpu/jshc.exe", "build-r23-gpu/jshc_gpu.exe",
                                          "build-r32-format-cpu/jshc.exe", "build-r32-format-gpu/jshc_gpu.exe"))
    hashes = {str(path): corpus.digest_file(path) for path in tracked}
    if len(frames) != 100 or len({hashes[str(path)] for path in frames}) != 100:
        raise RuntimeError("wrong frozen 100-image cohort")
    if hashes[str(truth_path)] != accepted["reference_sha256"]:
        raise RuntimeError("photo/reference binding changed")
    report = {"started_utc": datetime.now(timezone.utc).isoformat(), "scope": __doc__, "pass": False,
              "source_sha256": source_hashes, "input_and_prior_binary_sha256": hashes,
              "standalone_c_core_unchanged_from_r30": True, "new_arm_execution": False,
              "physical_mobile_performance_measured": False, "timing_is_benchmark": False,
              "official": False, "builds": {}, "cases": []}
    _write_report(target, report)
    def execute(command, name):
        value = {"command": list(map(str, command)), **runtime._execute(list(map(str, command)))}
        (output / (name + ".log")).write_text(value["stdout"] + value["stderr"], encoding="utf-8")
        if value["returncode"]:
            _write_report(output / (name + "-failure.json"), value)
            raise RuntimeError(name + " failed; inspect its preserved log")
        return value
    configs = [("simd", "build-r35-structured", True, True, True),
               ("baseline", "build-r35-baseline", False, False, True),
               ("no_c99", "build-r35-no-c99", False, False, False)]
    for label, folder, avx, omp, c99 in configs:
        directory = ROOT / folder
        command = ["cmake", "-S", str(ROOT), "-B", str(directory), "-G", "MinGW Makefiles",
                   "-DCMAKE_CXX_COMPILER=E:/mingw64/bin/g++.exe", "-DCMAKE_MAKE_PROGRAM=E:/mingw64/bin/mingw32-make.exe",
                   "-DCMAKE_BUILD_TYPE=Release", "-DJSHC_ENABLE_CPP_SIMD=OFF",
                   "-DJSHC_ENABLE_AVX2=" + ("ON" if avx else "OFF"),
                   "-DJSHC_ENABLE_OPENMP=" + ("ON" if omp else "OFF"),
                   "-DJSHC_ENABLE_PORTABLE_C=" + ("ON" if c99 else "OFF")]
        if c99: command.append("-DCMAKE_C_COMPILER=E:/mingw64/bin/gcc.exe")
        record = {"configure": execute(command, label + "-configure")}
        record["build"] = execute(["cmake", "--build", str(directory), "--parallel", "4"], label + "-build")
        binary = directory / "jshc.exe"
        record["binary_sha256"] = corpus.digest_file(binary)
        record["test_binary_sha256"] = corpus.digest_file(directory / "jshc_tests.exe")
        record["info"] = runtime.capabilities("cpu", binary)
        if avx:
            if not {"tetra_c99", "tetra_structured_avx2"}.issubset(record["info"]["available_kernels"]):
                raise RuntimeError("new SIMD build lacks promised kernels")
        elif "tetra_structured_avx2" in record["info"]["available_kernels"] or record["info"]["openmp_enabled"]:
            raise RuntimeError("baseline feature isolation failed")
        if c99:
            record["full_cpp_oracle_gate"] = execute(["ctest", "--test-dir", str(directory), "--output-on-failure"], label + "-ctest")
            shutil.copyfile(directory / "Testing/Temporary/LastTest.log", output / (label + "-cpp-oracle.log"))
        else:
            if "tetra_c99" in record["info"]["available_kernels"]:
                raise RuntimeError("disabled C99 reported available")
            try:
                runtime.plan(cases[2]["models"], executable=binary)
            except runtime.BackendError as error:
                record["explicit_disabled_rejection"] = error.record
            else:
                raise RuntimeError("disabled C99 unexpectedly executed")
        report["builds"][label] = record
        _write_report(target, report)
        print("[build/gate] " + label + " passed", flush=True)
    binary = ROOT / "build-r35-structured/jshc.exe"
    with tempfile.TemporaryDirectory(prefix="r35-native-") as temporary:
        temporary = Path(temporary)
        for row in cases:
            measured = {key: value for key, value in row.items() if key != "models"}
            measured["models"] = list(map(str, row["models"]))
            measured["backends"] = {}
            for kernel in ("tetra_c99", "tetra_structured_avx2"):
                plan = runtime.plan(row["models"], executable=binary, kernel=kernel)
                paths = [stage["path"] for stage in plan["stages"]]
                if row["paths"] is not None and paths != [["tetra", "curve", "vertex", "constant"][code] for code in row["paths"]]:
                    raise RuntimeError("actual native route differs from prior complete-node proof")
                raw = temporary / (row["name"] + "-" + kernel + ".rgb")
                execution = runtime.cube(row["models"], raw, executable=binary, kernel=kernel, threads=4, competition=True)
                if raw.stat().st_size != io.FULL_NBYTES or corpus.digest_file(raw) != row["cube_sha256"]:
                    raise RuntimeError("structured full cube differs from frozen native bytes")
                measured["backends"][kernel] = {"plan": plan, "cube": execution, "cube_sha256": row["cube_sha256"]}
                if row["name"] == "new-stress-m33":
                    image_raw = temporary / "images.rgb"
                    images = runtime.verify(row["models"], listing, executable=binary, kernel=kernel, threads=4,
                                            batch=True, competition=True, output=image_raw)
                    if image_raw.stat().st_size != 100 * 1024 * 768 * 3 or corpus.digest_file(image_raw) != accepted["backends"]["cpu"]["mapped_images_sha256"]:
                        raise RuntimeError("actual 100-image outputs differ from frozen qualification")
                    measured["backends"][kernel]["images100"] = images
                    with validation._mapped_full(raw) as mapped, validation._mapped_full(truth_path) as truth:
                        photo_rows = []
                        for photo in photos["images"]:
                            image = io.load_image(ROOT / photo["path"])
                            destination = temporary / "photo.png"
                            applied = runtime.apply(row["models"], ROOT / photo["path"], destination, executable=binary,
                                                    kernel=kernel, threads=4, competition=True)
                            actual = io.load_image(destination)
                            if not np.array_equal(actual, io.apply_full(mapped, image)):
                                raise RuntimeError("photo image path differs from verified complete cube")
                            quality = validation._stats(actual, io.apply_full(truth, image))[0]
                            frozen_photo = next(value for value in r34["photos5"]["rows"] if value["id"] == photo["id"])
                            if quality != frozen_photo["quality"]:
                                raise RuntimeError("photo statistics differ from R34")
                            photo_rows.append({"id": photo["id"], "quality": quality, "runtime": applied,
                                               "output_rgb_sha256": __import__("hashlib").sha256(actual.tobytes()).hexdigest()})
                    measured["backends"][kernel]["photos5"] = photo_rows
                raw.unlink()
            report["cases"].append(measured)
            _write_report(target, report)
            print("[cube/path] " + row["name"] + ": both new kernels match frozen full RGB bytes", flush=True)
        baseline_raw = temporary / "baseline.rgb"
        report["baseline_cli_full_cube"] = runtime.cube(cases[2]["models"], baseline_raw,
            executable=ROOT / "build-r35-baseline/jshc.exe", kernel="tetra_c99", threads=1, competition=True)
        if corpus.digest_file(baseline_raw) != cases[2]["cube_sha256"]:
            raise RuntimeError("no-SIMD/no-OpenMP CLI differs")
    for path, digest in hashes.items():
        if corpus.digest_file(Path(path)) != digest:
            raise RuntimeError("a frozen input or prior binary changed")
    for name, digest in source_hashes.items():
        if corpus.digest_file(ROOT / name) != digest:
            raise RuntimeError("stage source changed")
    for label, folder, *_ in configs:
        if corpus.digest_file(ROOT / folder / "jshc.exe") != report["builds"][label]["binary_sha256"]:
            raise RuntimeError("built binary changed during validation")
    report.update(pass_=True, inputs_unchanged=True, finished_utc=datetime.now(timezone.utc).isoformat())
    report["pass"] = report.pop("pass_")
    _write_report(target, report)
    print(json.dumps({"pass": True, "full_cpp_oracle_builds": 2, "frozen_real_model_cubes": 9,
                      "actual_images_per_new_kernel": 105, "timing_is_benchmark": False}), flush=True)


if __name__ == "__main__":
    main()
