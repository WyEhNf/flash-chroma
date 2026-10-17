"""Freeze a deterministic extension source image and verify an existing cache ID.

No numerical fit or pixel mapping is rerun. Every raw source byte is indexed;
the public fitter must find the previously measured R33 stress batch unchanged.
"""
from __future__ import annotations

import hashlib
import json
import os
from pathlib import Path
import subprocess
import sys
import zipfile

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "python"))
from lutlab import casebook, corpus, reportio


def main():
    names = [path.relative_to(ROOT).as_posix() for path in (ROOT / "python").rglob("*.py")]
    names += ["scripts/r36_strategy_extension.py", "scripts/r36_freeze_source.py", "scripts/r33_axis_bins_study.py",
              "scripts/r29_strategy_matrix.py", "cpp/src/full_normals.cpp", "cpp/include/jshc/full_normals.h", "pixi.lock"]
    payloads = {name: (ROOT / name).read_bytes() for name in sorted(set(names))}
    hashes = {name: hashlib.sha256(value).hexdigest() for name, value in payloads.items()}
    epoch = hashlib.sha256(corpus.canonical(hashes)).hexdigest()
    base = ROOT / "artifacts/r36-frozen-source"
    base.mkdir(exist_ok=True)
    archive = base / ("source-" + epoch + ".zip")
    if not archive.exists():
        with zipfile.ZipFile(archive, "w", zipfile.ZIP_DEFLATED) as target:
            for name, value in payloads.items():
                info = zipfile.ZipInfo(name, (1980, 1, 1, 0, 0, 0))
                info.compress_type = zipfile.ZIP_DEFLATED
                target.writestr(info, value)
    destination = base / epoch[:20]
    destination.mkdir(exist_ok=True)
    with zipfile.ZipFile(archive) as source:
        if set(source.namelist()) != set(hashes): raise RuntimeError("source bundle inventory differs")
        for name, digest in hashes.items():
            value = source.read(name)
            if hashlib.sha256(value).hexdigest() != digest: raise RuntimeError("source archive differs")
            path = destination / name
            path.resolve().relative_to(destination.resolve())
            if path.exists():
                if path.read_bytes() != value: raise RuntimeError("existing numerical image was edited")
            else:
                path.parent.mkdir(parents=True, exist_ok=True)
                path.write_bytes(value)
    pilot = reportio.read_json(ROOT / "artifacts/r33-axis-bins/study.json")
    row = next(row for row in pilot["cases"] if row["case_id"] == "legacy-stress-13" and row["profile"] == "lookahead_bins")
    batch = reportio.read_json(Path(row["models"][0]).parent / "manifest.json")
    old = reportio.read_json(ROOT / "artifacts/r27-step/acceptance-stress-13-m33-adaptive.json")
    params = dict(scenario="legacy-stress-13", mode="seq", method="lookahead_bins", m=33, grid="dp", adaptive=False,
                  inputs=[str(casebook._path(source["path"])) for source in old["sources"]],
                  model_dir=str(ROOT / "artifacts/r33-axis-bins/models/legacy-stress-13/lookahead_bins-m33"),
                  allow_composite=False, allow_residual=False)
    code = ("import sys,json;from pathlib import Path;from types import SimpleNamespace;from lutlab import cli;"
            "v=json.loads(sys.argv[1]);v['inputs']=[Path(x) for x in v['inputs']];"
            "e=cli.model_entry(SimpleNamespace(**v),existing_only=True);assert e is not None;print(e.manifest['identity_sha256'])")
    environment = {**os.environ, "PYTHONPATH": str(destination / "python"), "GIT_CEILING_DIRECTORIES": str(ROOT),
                   "JSHC_FULL_FIT_LIB": str(ROOT / "build-fit/libjshc_full_fit.dll"),
                   "OPENBLAS_NUM_THREADS": "1", "MKL_NUM_THREADS": "1", "OMP_NUM_THREADS": "1"}
    result = subprocess.run([sys.executable, "-c", code, json.dumps(params)], cwd=destination, env=environment,
                            capture_output=True, text=True, encoding="utf-8", errors="replace")
    if result.returncode or result.stdout.strip() != batch["identity_sha256"]:
        raise RuntimeError("frozen public cache identity differs: " + result.stdout + result.stderr)
    marker = {"schema": 1, "pass": True, "epoch_sha256": epoch, "archive": str(archive),
              "archive_sha256": corpus.digest_file(archive), "source_root": str(destination), "source_sha256": hashes,
              "public_cache_identity_probe": batch["identity_sha256"], "probe_is_fit": False, "probe_maps_pixels": False}
    reportio.write_report(destination / "frozen-source.json", marker)
    reportio.write_report(base / "latest.json", marker)
    print(json.dumps({"pass": True, "source_root": str(destination), "preserved_cache_identity": batch["identity_sha256"]}))


if __name__ == "__main__":
    main()
