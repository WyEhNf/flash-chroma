"""Check the OpenMP-free training library in a fresh process without GCC PATH."""
from __future__ import annotations

import argparse
from datetime import datetime, timezone
import json
import os
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "python"))
from lutlab import fullfit, metrics, runtime
from lutlab.entry import _write_report


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--library", type=Path, default=ROOT / "build-fit-portable/libjshc_full_fit.dll")
    parser.add_argument("--output", type=Path, default=ROOT / "artifacts/r25-full/portable-check.json")
    args = parser.parse_args()
    library = args.library.resolve()
    comparison = ROOT / "artifacts/r25-full/performance.json"
    measured = json.loads(comparison.read_text(encoding="utf-8"))
    if not measured.get("all_assembly_systems_byte_equivalent"):
        raise RuntimeError("complete the native/reference matrix comparison first")
    reference = next(row for row in measured["runs"] if row["mode"] == "assembly_native4")
    paths = [Path(sys.executable).parent, Path(sys.executable).parent / "Library/bin",
             Path(os.environ.get("SystemRoot", "C:/Windows")) / "System32"]
    os.environ.update(PATH=os.pathsep.join(map(str, paths)), JSHC_FULL_FIT_LIB=str(library),
        OPENBLAS_NUM_THREADS="1", MKL_NUM_THREADS="1", OMP_NUM_THREADS="1")
    fingerprint = fullfit.trainer_fingerprint()
    if fingerprint["openmp_compiled"]:
        raise RuntimeError("portable library was compiled with OpenMP")
    files = [comparison, Path(__file__).resolve(), *(library.parent.glob("*.dll")),
             ROOT / "scripts/r25_performance.py", *(ROOT / name for name in fullfit.NATIVE_SOURCES)]
    hashes = {str(path): metrics.file_sha256(path) for path in files}
    process = runtime._execute(reference["command"])
    if process["returncode"]:
        raise RuntimeError(process["stderr"])
    result = json.loads(process["stdout"])
    if (result["canonical_system_sha256"] != reference["result"]["canonical_system_sha256"]
            or result["assembly"]["integer_system_sha256"] != reference["result"]["assembly"]["integer_system_sha256"]
            or result["assembly"]["actual_threads"] != 1 or result["assembly"]["trainer"] != fingerprint):
        raise RuntimeError("OpenMP-free library did not reproduce the complete integer system")
    for name, digest in hashes.items():
        if metrics.file_sha256(name) != digest:
            raise RuntimeError("portable-check source/binary changed")
    _write_report(args.output.resolve(), {"finished_utc": datetime.now(timezone.utc).isoformat(),
        "scope": "Windows x64 C++17 library, OpenMP OFF and AVX2 option OFF; full 256^3 clip-7/m33 matrix and rhs",
        "source_and_binary_sha256": hashes, "isolated_path": list(map(str, paths)), "trainer": fingerprint,
        "command": reference["command"], "process": process, "result": result,
        "without_gcc_path": all("mingw" not in str(path).lower() for path in paths),
        "full_integer_system_matches_openmp_build": True})
    print(json.dumps({"openmp_compiled": False, "actual_threads": result["assembly"]["actual_threads"],
                      "full_integer_system_matches_openmp_build": True}), flush=True)


if __name__ == "__main__":
    main()
