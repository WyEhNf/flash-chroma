"""Freeze the completed R20 audit and current source into a small review archive."""
from __future__ import annotations

import hashlib
import csv
import json
from pathlib import Path
import subprocess
import zipfile

ROOT = Path(__file__).resolve().parents[1]
ARTIFACTS = ROOT / "artifacts/r20-validation"
OUTPUT = ROOT / "report/data/r20"


def record(payload):
    return {"bytes": len(payload), "sha256": hashlib.sha256(payload).hexdigest()}


def main():
    audit = json.loads((ARTIFACTS / "audit.json").read_text(encoding="utf-8"))
    if not audit.get("correctness_audit_pass") or not audit.get("finished_utc"):
        raise RuntimeError("archive requires a completed successful correctness audit")
    for name, digest in audit["source_sha256"].items():
        if record((ROOT / name).read_bytes())["sha256"] != digest:
            raise RuntimeError(f"audited source changed before archival: {name}")
    source_paths = subprocess.check_output(
        ["git", "ls-files", "--cached", "--others", "--exclude-standard", "-z"], cwd=ROOT
    ).decode("utf-8").split("\0")
    source_records = {}
    snapshot = ARTIFACTS / "source-snapshot.zip"
    with zipfile.ZipFile(snapshot, "w", zipfile.ZIP_DEFLATED) as archive:
        for name in sorted(set(source_paths)):
            if not name or name.startswith("report/data/"):
                continue
            path = ROOT / name
            if not path.is_file():
                continue
            payload = path.read_bytes()
            source_records[name] = record(payload)
            archive.writestr(name, payload)
    (ARTIFACTS / "source-manifest.json").write_text(json.dumps({
        "git_base": subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=ROOT, text=True).strip(),
        "snapshot_scope": "current tracked and untracked non-ignored source, excluding report/data",
        "source_files": source_records, "snapshot": record(snapshot.read_bytes()),
    }, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")

    OUTPUT.mkdir(parents=True, exist_ok=True)
    with (OUTPUT / "accuracy-summary.csv").open("w", encoding="utf-8", newline="") as stream:
        fields = ["scenario", "m", "additional_candidate", "cube_mean", "cube_p99", "cube_max",
                  "worst_image_mean", "local_mean_gate_pass", "native_images_and_cube_equal"]
        writer = csv.DictWriter(stream, fieldnames=fields, extrasaction="ignore")
        writer.writeheader()
        writer.writerows(audit["cases"])
    target = OUTPUT / "r20-evidence.zip"
    entries = {}
    with zipfile.ZipFile(target, "w", zipfile.ZIP_DEFLATED) as archive:
        for path in sorted(ARTIFACTS.rglob("*")):
            if path.is_file() and (path.suffix.lower() in (".json", ".log", ".txt", ".slut") or path == snapshot):
                name = path.relative_to(ROOT).as_posix()
                payload = path.read_bytes()
                entries[name] = record(payload)
                archive.writestr(name, payload)
    with zipfile.ZipFile(target) as archive:
        for name, expected in entries.items():
            if record(archive.read(name)) != expected:
                raise RuntimeError(f"archive readback failed: {name}")
    index = {"archive": target.name, **record(target.read_bytes()),
             "files": entries, "verified": True,
             "excludes": "original full LUTs, images and executable binaries; R19 SHA-bound sources are reused"}
    (OUTPUT / "evidence-index.json").write_text(json.dumps(index, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(json.dumps({"archive": str(target), "files": len(entries), "bytes": index["bytes"],
                      "verified": True}, ensure_ascii=False))


if __name__ == "__main__":
    main()
