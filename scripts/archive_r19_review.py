"""Publish compact review evidence while retaining the original artifact layout."""
from __future__ import annotations

import hashlib
import json
from pathlib import Path
import shutil
import zipfile

ROOT = Path(__file__).resolve().parents[1]
OUTPUT = ROOT / "report/data/r19"


def sha(path):
    with path.open("rb") as stream:
        return hashlib.file_digest(stream, "sha256").hexdigest()


def main():
    OUTPUT.mkdir(parents=True, exist_ok=True)
    files = {}
    names = ("r17-algorithm", "r17-acceptance", "r17-integration", "r18-algorithm", "r18-cpu",
             "r18-portable", "r18-unified", "r18-integration", "r18-industry", "r18-progress", "r19-delivery")
    for name in names:
        for path in (ROOT / "artifacts" / name).rglob("*"):
            if path.is_file() and (path.suffix in (".json", ".csv", ".log", ".txt", ".slut")
                                   or path.name == "source-snapshot.zip"):
                files[path.relative_to(ROOT).as_posix()] = path
    hardware = ROOT.parents[1] / "outputs/project16-runtime-2026-10-15"
    for path in hardware.glob("*"):
        if path.is_file() and path.suffix in (".json", ".cpp"):
            files["report/data/r19/hardware/" + path.name] = path
    target = OUTPUT / "r17-r19-evidence.zip"
    with zipfile.ZipFile(target, "w", zipfile.ZIP_DEFLATED) as archive:
        for name, path in sorted(files.items()):
            archive.write(path, name)
    index = {"scope": "original small numerical evidence and integer models; large generated input LUTs/images and native binaries are excluded",
             "archive": target.name, "archive_bytes": target.stat().st_size,
             "archive_sha256": sha(target),
             "files": {name: {"bytes": path.stat().st_size, "sha256": sha(path)} for name, path in sorted(files.items())}}
    (OUTPUT / "evidence-index.json").write_text(json.dumps(index, indent=2) + "\n", encoding="utf-8")
    for name in ("accuracy-summary.csv", "paired-summary.csv"):
        shutil.copyfile(ROOT / "artifacts/r19-delivery" / name, OUTPUT / name)
    with zipfile.ZipFile(target) as archive:
        for name, expected in index["files"].items():
            data = archive.read(name)
            if len(data) != expected["bytes"] or hashlib.sha256(data).hexdigest() != expected["sha256"]:
                raise RuntimeError(f"archive verification failed: {name}")
    print(json.dumps({"archive": str(target), "files": len(files), "bytes": target.stat().st_size, "verified": True}))


if __name__ == "__main__":
    main()
