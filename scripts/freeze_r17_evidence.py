"""Freeze source and evidence identities without repeating numerical experiments."""
from __future__ import annotations

import hashlib
import json
from pathlib import Path
import subprocess
import zipfile

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "artifacts" / "r17-acceptance"


def sha(path):
    with path.open("rb") as stream:
        return hashlib.file_digest(stream, "sha256").hexdigest()


def record(path):
    return {"bytes": path.stat().st_size, "sha256": sha(path)}


def main():
    bench = json.loads((OUT / "benchmark.json").read_text(encoding="utf-8"))
    accuracy = json.loads((OUT / "accuracy.json").read_text(encoding="utf-8"))
    binary = ROOT / "build" / "jshc.exe"
    if sha(binary) != bench["executable_sha256"]:
        raise RuntimeError("binary changed after benchmark")
    for row in accuracy["results"]:
        if row["validation"]["executable_sha256"] != sha(binary):
            raise RuntimeError("accuracy and benchmark used different binaries")
        for filename, digest in row["validation"]["model_sha256"].items():
            if sha(Path(filename)) != digest:
                raise RuntimeError(f"validated model changed: {filename}")
    sources = [ROOT / name for name in ("CMakeLists.txt", "README.md", "PROBLEM.md", "pixi.toml", "pixi.lock", ".gitignore")]
    for directory in ("cpp", "python/lutlab", "tests", "scripts"):
        sources += [p for p in (ROOT / directory).rglob("*") if p.suffix in (".cpp", ".h", ".hpp", ".py")]
    sources += list((ROOT / "docs").glob("r17-*.md"))
    sources += list((ROOT / "zig").glob("*.zig")) + list((ROOT / "rust").glob("*.rs"))
    sources = sorted(set(sources))
    snapshot = OUT / "source-snapshot.zip"
    with zipfile.ZipFile(snapshot, "w", zipfile.ZIP_DEFLATED) as archive:
        for path in sources:
            archive.write(path, path.relative_to(ROOT).as_posix())
    # All generated input/model/report bytes are included in the manifest, but
    # large data files are deliberately not duplicated in the source zip.
    assets = []
    for name in ("r17-algorithm", "r17-acceptance", "r17-integration"):
        assets += [p for p in (ROOT / "artifacts" / name).rglob("*") if p.is_file()
                   and p.name not in ("delivery-manifest.json", "source-snapshot.zip")]
    builds = [ROOT / d / file for d in ("build", "build-portable")
              for file in ("jshc.exe", "jshc_tests.exe", "libjshc_core.a", "CMakeCache.txt")]
    for path in (ROOT / "build/compile_commands.json", ROOT / "build/Testing/Temporary/LastTest.log"):
        if path.exists():
            builds.append(path)
    hardware = ROOT.parents[1] / "outputs" / "project16-runtime-2026-10-15"
    manifest = {
        "date": "2026-10-15", "baseline_commit": subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=ROOT, text=True).strip(),
        "status": "local uncommitted implementation; no official score claimed",
        "source": {p.relative_to(ROOT).as_posix(): record(p) for p in sources},
        "source_snapshot": {"path": snapshot.relative_to(ROOT).as_posix(), **record(snapshot)},
        "builds": {p.relative_to(ROOT).as_posix(): record(p) for p in builds},
        "hardware_evidence": {str(p): record(p) for p in hardware.glob("*") if p.suffix in (".json", ".cpp")},
        "artifacts": {p.relative_to(ROOT).as_posix(): record(p) for p in sorted(assets)},
        "artifact_bytes": sum(p.stat().st_size for p in assets),
        "tests": {"cpp_full": "passed; 2^24 colours across 5 lattices, 3 compiled integer backends, mixed 4-stage chain",
                  "portable_sampled": "passed; 65536 colours and chain/boundary controls; no SIMD/OpenMP",
                  "python": "9 passed", "integration": "fit/cache/selector/native pass; initial UTF-8 logging error retained",
                  "logging_repair": "passed targeted UTF-8 log check"},
        "benchmark": bench["summary"],
        "limits": ["synthetic inputs, not official data", "unknown official threshold, format, and timing boundary",
                   "process peak memory and host utilisation were not sampled (psutil unavailable)",
                   "Zig, Rust, ARM, MSVC and Docker not validated in this phase"],
    }
    target = OUT / "delivery-manifest.json"
    target.write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
    # Read-back verification of the final source snapshot and numerical artifacts.
    stored = json.loads(target.read_text(encoding="utf-8"))
    for group in ("source", "builds", "artifacts"):
        for filename, expected in stored[group].items():
            if record(ROOT / filename) != expected:
                raise RuntimeError(f"evidence changed during freeze: {filename}")
    print(json.dumps({"manifest": str(target), "source_files": len(sources), "artifact_files": len(assets),
                      "artifact_bytes": manifest["artifact_bytes"], "source_snapshot": str(snapshot),
                      "verified": True}))


if __name__ == "__main__":
    main()
