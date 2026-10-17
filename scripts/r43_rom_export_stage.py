"""One staged ROM export gate: compiled const bytes, full cubes and target objects.

No fitting or speed measurement. Two previously validated four-table models are
exported as C99, built with the unchanged portable core, and exhaustively match
frozen native output. Cross compilation is separate from device execution.
"""
from __future__ import annotations

import argparse
from datetime import datetime, timezone
import json
from pathlib import Path
import sys
import tempfile

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "python"))
from lutlab import casebook, corpus, portable_export, reportio, runtime


def execute(command):
    result = runtime._execute(list(map(str, command)))
    if result["returncode"]:
        raise RuntimeError("ROM verification command failed: " + json.dumps(result, ensure_ascii=True))
    return result


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--resume", action="store_true", help="reuse the two committed cube/ROM proofs; finish only target/metadata checks")
    args = parser.parse_args()
    output = ROOT / "artifacts/r43-rom-export"
    output.mkdir(exist_ok=True)
    target = output / "stage.json"
    if target.exists() and not args.resume:
        raise RuntimeError("preserve this export verification epoch before rerunning")
    source_names = ["scripts/r43_rom_export_stage.py", "python/lutlab/portable_export.py",
                    "portable/tools/verify_exported_rom.c", "portable/src/jshc_portable.c", "portable/include/jshc_portable.h",
                    "python/lutlab/io.py", "python/lutlab/cache.py", "python/lutlab/runtime.py", "python/lutlab/reportio.py"]
    hashes = {name: corpus.digest_file(ROOT / name) for name in source_names}
    native_path = ROOT / "artifacts/r35-structured-runtime/stage.json"
    native_hash = corpus.digest_file(native_path)
    native = reportio.read_json(native_path)
    if not native["pass"]:
        raise RuntimeError("requires frozen native/C99 quality stage")
    report = {"started_utc": datetime.now(timezone.utc).isoformat(), "scope": __doc__, "source_sha256": hashes,
              "native_stage_sha256": native_hash, "pass": False, "cases": [], "cross_compilations": [],
              "new_fits": 0, "new_pixel_cube_executions": 0, "new_speed_measurements": 0,
              "physical_mobile_execution": False, "official": False}
    if args.resume:
        failed = output / "failed-first-stage.json"
        failed_source = output / "failed-first-driver.py"
        prior = reportio.read_json(failed)
        if (prior["pass"] or prior["new_pixel_cube_executions"] != 2 or len(prior["cases"]) != 2
                or prior.get("error", {}).get("type") != "FileNotFoundError"
                or prior["native_stage_sha256"] != native_hash
                or corpus.digest_file(failed_source) != prior["source_sha256"]["scripts/r43_rom_export_stage.py"]):
            raise RuntimeError("cannot resume without the preserved two-cube failure epoch")
        for name, digest in prior["source_sha256"].items():
            if name != "scripts/r43_rom_export_stage.py" and corpus.digest_file(ROOT / name) != digest:
                raise RuntimeError("previously verified export/runtime source changed")
        for row in prior["cases"]:
            proof = next(value for value in native["cases"] if value["name"] == row["case"])
            bundle = casebook._path(row["bundle"])
            if (corpus.digest_file(bundle.parent / "verify-exported.exe") != row["host_binary_sha256"]
                    or row["cube_sha256"] != proof["cube_sha256"] or row["cube_bytes"] != 256 ** 3 * 3
                    or row["cube_execution"]["returncode"] or row["compiled_model_sha256"] != proof["model_sha256"]
                    or [corpus.digest_file(casebook._path(path)) for path in proof["models"]] != proof["model_sha256"]
                    or reportio.read_json(bundle / "portable-model.json") != row["metadata"]):
                raise RuntimeError("committed ROM/full-cube proof changed")
            for name, detail in row["metadata"]["generated_files"].items():
                if corpus.digest_file(bundle / name) != detail["sha256"]:
                    raise RuntimeError("generated ROM source changed after cube verification")
        report.update(prior)
        report.pop("error", None)
        report.pop("finished_utc", None)
        report["source_sha256"] = hashes
        report["repair"] = {"started_utc": datetime.now(timezone.utc).isoformat(),
                            "prior_stage": casebook._portable(failed), "prior_stage_sha256": corpus.digest_file(failed),
                            "prior_source_sha256": corpus.digest_file(failed_source), "new_pixel_cube_executions": 0,
                            "reason": "installed LLVM provides llvm-readobj, not llvm-readelf"}
    for name in ("portable/src/jshc_portable.c", "portable/include/jshc_portable.h"):
        if native["source_sha256"][name] != hashes[name]:
            raise RuntimeError("portable core differs from its frozen validated version")
    report["portable_core_unchanged_from_r35"] = True
    reportio.write_report(target, report)
    try:
        with tempfile.TemporaryDirectory(prefix="r43-rom-") as temporary:
            temporary = Path(temporary)
            for label in (() if args.resume else ("new-bins17-m17", "new-stress-m33")):
                prior = next(row for row in native["cases"] if row["name"] == label)
                models = [casebook._path(path) for path in prior["models"]]
                if [corpus.digest_file(path) for path in models] != prior["model_sha256"]:
                    raise RuntimeError("frozen source models changed")
                folder = output / label
                folder.mkdir()
                bundle = folder / "rom"
                # Exercise the user-facing module CLI, not a separate test exporter.
                command = [sys.executable, "-m", "lutlab.portable_export", "--models", *models, "--output", bundle]
                exported = execute(command)
                metadata = reportio.read_json(bundle / "portable-model.json")
                if metadata["ordered_model_sha256"] != prior["model_sha256"]:
                    raise RuntimeError("export changed serialized models")
                binary = folder / "verify-exported.exe"
                build = execute(["E:/mingw64/bin/gcc.exe", "-std=c99", "-O2", "-Wall", "-Wextra", "-Wpedantic",
                                 "-Wconversion", "-Werror", "-I", ROOT / "portable/include", "-I", bundle,
                                 bundle / "flash_chroma.c", ROOT / "portable/src/jshc_portable.c",
                                 ROOT / "portable/tools/verify_exported_rom.c", "-o", binary])
                dumped = temporary / (label + "-rom.bin")
                dump_execution = execute([binary, "blobs", dumped])
                payload = dumped.read_bytes()
                offset = 0
                compiled_hashes = []
                for size in metadata["ordered_blob_bytes"]:
                    compiled_hashes.append(portable_export.sha(payload[offset:offset+size]))
                    offset += size
                if offset != len(payload) or compiled_hashes != prior["model_sha256"]:
                    raise RuntimeError("compiled const arrays differ from original model bytes")
                cube = temporary / (label + "-cube.rgb")
                cube_execution = execute([binary, "cube", cube])
                report["new_pixel_cube_executions"] += 1
                cube_hash = corpus.digest_file(cube)
                if cube.stat().st_size != 256 ** 3 * 3 or cube_hash != prior["cube_sha256"]:
                    raise RuntimeError("ROM model execution differs from the frozen native complete cube")
                row = {"case": label, "export": exported, "bundle": casebook._portable(bundle), "metadata": metadata,
                       "host_build": build, "host_binary_sha256": corpus.digest_file(binary),
                       "compiled_blob_dump": dump_execution, "compiled_model_sha256": compiled_hashes,
                       "cube_execution": cube_execution, "cube_sha256": cube_hash,
                       "cube_bytes": cube.stat().st_size, "runtime_plan": json.loads(cube_execution["stderr"]),
                       "frozen_reference_sha256": prior["cube_sha256"]}
                report["cases"].append(row)
                reportio.write_report(target, report)
            largest = output / "new-stress-m33/rom"
            for name, options in (
                    ("aarch64-le", ["--target=aarch64-none-elf"]),
                    ("aarch64-be", ["--target=aarch64_be-none-elf"]),
                    ("cortex-m4", ["--target=arm-none-eabi", "-mcpu=cortex-m4", "-mthumb"]),
                    ("riscv32", ["--target=riscv32-none-elf", "-march=rv32im", "-mabi=ilp32"])):
                obj = output / ("rom-" + name + ".o")
                command = ["C:/Program Files/LLVM/bin/clang.exe", *options, "-std=c99", "-O2", "-ffreestanding",
                           "-fno-builtin", "-Wall", "-Wextra", "-Wpedantic", "-Wconversion", "-Werror",
                           "-I", ROOT / "portable/include", "-I", largest, "-c", largest / "flash_chroma.c", "-o", obj]
                compilation = execute(command)
                sections = execute(["C:/Program Files/LLVM/bin/llvm-readobj.exe", "--file-headers", "--sections", obj])
                report["cross_compilations"].append({"target": name, "compile": compilation, "object_sha256": corpus.digest_file(obj),
                                                     "object_bytes": obj.stat().st_size, "sections": sections,
                                                     "execution": False})
            matrix = reportio.read_json(ROOT / "artifacts/r29-matrix/development.json")
            tri = next(item for key, item in matrix["observations"].items() if "/trilinear/m17" in key and item["status"] == "screened")
            tri_value = reportio.read_json(casebook._path(tri["path"]))
            try:
                portable_export.export_models([casebook._path(path) for path in tri_value["models"]], output / "invalid-trilinear")
            except ValueError as error:
                if "tetra_q16 only" not in str(error) or (output / "invalid-trilinear").exists():
                    raise
                report["trilinear_rejected"] = {"message": str(error), "source_observation_sha256": tri["sha256"],
                                                "models_sha256": tri_value["model_sha256"], "output_created": False}
            else:
                raise RuntimeError("trilinear model was silently exported for tetrahedral C99")
        for name, digest in hashes.items():
            if corpus.digest_file(ROOT / name) != digest:
                raise RuntimeError("export/runtime source changed during verification")
        if corpus.digest_file(native_path) != native_hash:
            raise RuntimeError("frozen native quality report changed")
        report.update(pass_=True, finished_utc=datetime.now(timezone.utc).isoformat())
        report["pass"] = report.pop("pass_")
        reportio.write_report(target, report)
        print(json.dumps({"pass": True, "rom_cases": len(report["cases"]), "whole_cubes": report["new_pixel_cube_executions"],
                          "cross_compiled_targets": len(report["cross_compilations"]), "trilinear_rejected": True}))
    except BaseException as error:
        report.update(error={"type": type(error).__name__, "message": str(error)}, finished_utc=datetime.now(timezone.utc).isoformat())
        reportio.write_report(target, report)
        raise


if __name__ == "__main__":
    main()
