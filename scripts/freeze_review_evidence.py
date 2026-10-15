"""Freeze a completed local study, current source, and small review evidence."""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
import subprocess
import zipfile

ROOT = Path(__file__).resolve().parents[1]


def record(payload):
    return {"bytes": len(payload), "sha256": hashlib.sha256(payload).hexdigest()}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--artifacts", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--result", type=Path, required=True)
    parser.add_argument("--success-field", required=True)
    parser.add_argument("--archive-name", default="evidence.zip")
    args = parser.parse_args()
    artifacts, output = args.artifacts.resolve(), args.output.resolve()
    if artifacts == output or artifacts in output.parents:
        raise ValueError("review output must be outside the artifact tree")
    if Path(args.archive_name).name != args.archive_name:
        raise ValueError("archive name must be a plain filename")
    result = json.loads(args.result.read_text(encoding="utf-8"))
    if not result.get("finished_utc") or result.get(args.success_field) is not True:
        raise RuntimeError("review archive requires the requested completed successful stage")
    for name, digest in result["source_sha256"].items():
        if record((ROOT / name).read_bytes())["sha256"] != digest:
            raise RuntimeError(f"audited source changed before freeze: {name}")
    sources = subprocess.check_output(
        ["git", "ls-files", "--cached", "--others", "--exclude-standard", "-z"], cwd=ROOT
    ).decode("utf-8").split("\0")
    source_records = {}
    snapshot = artifacts / "source-snapshot.zip"
    with zipfile.ZipFile(snapshot, "w", zipfile.ZIP_DEFLATED) as archive:
        for name in sorted(set(sources)):
            path = ROOT / name
            if not name or name.startswith("report/data/") or not path.is_file():
                continue
            payload = path.read_bytes()
            source_records[name] = record(payload)
            archive.writestr(name, payload)
    manifest = {"git_base": subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=ROOT, text=True).strip(),
        "source_files": source_records, "snapshot": record(snapshot.read_bytes()),
        "result_sha256": record(args.result.read_bytes())["sha256"],
        "scope": "current non-ignored source excluding report/data; no commit or push is performed"}
    (artifacts / "source-manifest.json").write_text(json.dumps(manifest, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    output.mkdir(parents=True, exist_ok=True)
    target = output / args.archive_name
    entries = {}
    with zipfile.ZipFile(target, "w", zipfile.ZIP_DEFLATED) as archive:
        for path in sorted(artifacts.rglob("*")):
            if path.is_file() and (path.suffix.lower() in (".json", ".csv", ".log", ".txt", ".slut", ".py") or path == snapshot):
                name = path.relative_to(ROOT).as_posix()
                payload = path.read_bytes()
                entries[name] = record(payload)
                archive.writestr(name, payload)
    with zipfile.ZipFile(target) as archive:
        for name, expected in entries.items():
            if record(archive.read(name)) != expected:
                raise RuntimeError(f"archive readback failed: {name}")
    index = {"archive": target.name, **record(target.read_bytes()), "files": entries, "verified": True,
        "excludes": "full LUTs, original images and native binaries; hashes are preserved in the study records"}
    (output / "evidence-index.json").write_text(json.dumps(index, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(json.dumps({"archive": str(target), "files": len(entries), "bytes": index["bytes"], "verified": True}))


if __name__ == "__main__":
    main()
