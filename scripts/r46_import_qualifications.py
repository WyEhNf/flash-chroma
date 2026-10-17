"""Import completed image or full-cube records under the sole writer lease.

Run after the active matrix controller releases its lease. Immutable numerical
receipts are validated by Casebook; no fitting, pixels or timing are repeated.
Repeated imports preserve observation IDs and do not invent new measurements.
"""
from __future__ import annotations

import argparse
from datetime import datetime, timezone
import json
import os
from pathlib import Path
import sys
import uuid

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "python"))
from lutlab import casebook, corpus, reportio


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--stage", type=Path, action="append", default=[])
    parser.add_argument("--cube-stage", type=Path, action="append", default=[],
                        help="completed native full-cube stage; no image qualification is inferred")
    args = parser.parse_args()
    image_stages = args.stage or ([] if args.cube_stage else [ROOT / "artifacts/r45-representative-images/stage.json"])
    stages = [(path, True) for path in image_stages] + [(path, False) for path in args.cube_stage]
    lease = ROOT / "artifacts/r29-matrix/phase-controller.lock"
    folder = ROOT / "artifacts/r46-qualified-import" / uuid.uuid4().hex[:12]
    target = folder / "stage.json"
    names = ["scripts/r46_import_qualifications.py", "python/lutlab/casebook.py", "python/lutlab/timingbook.py",
             "python/lutlab/cache.py", "python/lutlab/io.py", "python/lutlab/entry.py", "python/lutlab/reportio.py"]
    source_hashes = {name: corpus.digest_file(ROOT / name) for name in names}
    report = {"started_utc": datetime.now(timezone.utc).isoformat(), "scope": __doc__, "pass": False,
              "source_sha256": source_hashes, "sources": [], "imported": [], "new_pixel_executions": 0}
    with lease.open("x", encoding="utf-8") as stream:
        json.dump({"pid": os.getpid(), "owner": "R46 completed image qualifications canonical import"}, stream)
    try:
        folder.mkdir(parents=True)
        book = casebook.Casebook(ROOT / "datasets/problem16-v1/casebook")
        before = sum(len(row["observations"]) for row in book.index["cases"].values())
        for path, requires_images in stages:
            stage = reportio.read_json(path)
            if not stage["pass"] or not stage["inputs_unchanged"] or not stage.get("finished_utc"):
                raise RuntimeError("only completed, input-bound image stages may be imported")
            report["sources"].append({"path": str(path.resolve()), "sha256": corpus.digest_file(path), "requires_actual_images": requires_images})
            for row in stage["pending_canonical_import"]:
                evidence = casebook._path(row["path"])
                if corpus.digest_file(evidence) != row["sha256"]:
                    raise RuntimeError("qualification observation changed")
                value = reportio.read_json(evidence)
                if requires_images:
                    if not value.get("images") or not value["images"]["native_verified"] or value["images"]["count"] != 100:
                        raise RuntimeError("not an actual 100-image qualification record")
                elif value.get("images") or value["cube"]["n_colors"] != 256 ** 3:
                    raise RuntimeError("cube-only import must not infer actual image qualification")
                if book.record(evidence) != row["observation_id"]:
                    raise RuntimeError("qualification identity differs from isolated validated commit")
                report["imported"].append(row)
                reportio.write_report(target, report)
        after = sum(len(row["observations"]) for row in book.index["cases"].values())
        reportio.write_report(book.root / "summary.json", book.summary())
        for name, digest in source_hashes.items():
            if corpus.digest_file(ROOT / name) != digest:
                raise RuntimeError("import validator changed during publication")
        for row in report["sources"]:
            if corpus.digest_file(Path(row["path"])) != row["sha256"]:
                raise RuntimeError("completed qualification stage changed during import")
        report.update(pass_=True, finished_utc=datetime.now(timezone.utc).isoformat(),
                      newly_added_observations=after - before, canonical_observations=after)
        report["pass"] = report.pop("pass_")
        reportio.write_report(target, report)
        print(json.dumps({"pass": True, "validated_receipts": len(report["imported"]), "newly_added": after - before,
                          "canonical_observations": after}))
    except BaseException as error:
        report.update(error={"type": type(error).__name__, "message": str(error)}, finished_utc=datetime.now(timezone.utc).isoformat())
        reportio.write_report(target, report)
        raise
    finally:
        lease.unlink()


if __name__ == "__main__":
    main()
