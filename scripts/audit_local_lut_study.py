"""完成后核对研究产物数量、检查点身份和全部素材/模型哈希。"""
import argparse
import csv
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument("--input", type=Path, required=True)
args = parser.parse_args()
out = args.input.resolve()


def read(path):
    return json.loads(path.read_text(encoding="utf-8"))


def digest(path):
    with path.open("rb") as stream:
        return hashlib.file_digest(stream, "sha256").hexdigest()


def check(path, expected):
    if digest(path) != expected:
        raise ValueError(f"哈希不一致：{path}")


meta = read(out / "run.json")
for path, expected in meta["identity"]["source_sha256"].items():
    check(ROOT / path, expected)
check(ROOT / "assets/LUT/manifest.json", meta["identity"]["lut_manifest"])
check(ROOT / "assets/photos/manifest.json", meta["identity"]["image_manifest"])
images = read(ROOT / "assets/photos/manifest.json")["images"]
for image in images:
    check(ROOT / image["evaluation"]["path"], image["evaluation"]["sha256"])
reports = [read(path) for path in sorted((out / "luts").glob("*/result.json"))]
assert len(reports) == 68 and len(images) == 100
screen_count = full_count = model_count = 0
checked = set()
for report in reports:
    assert report["complete"] and report["screen_complete"]
    assert report["run_identity"] == meta["identity_sha256"]
    source = report["lut"]
    check(ROOT / source["path"], source["sha256"])
    check(out / "references" / (source["sha256"][:12] + ".npy"), report["reference_sha256"])
    for row in report["screen"] + report["full"]:
        assert row["status"] == "ok"
        if row["model"] not in checked:
            check(out / row["model"], row["model_sha256"])
            checked.add(row["model"])
            model_count += 1
    for row in report["full"]:
        assert len(row["per_image"]) == 100
        assert len(row["set_ms"]) == 3
    screen_count += len(report["screen"])
    full_count += len(report["full"])
assert screen_count == 2740 and full_count == 188
chains = read(out / "chains.json")
check(ROOT / "python/lutlab/study_chains.py", chains["source_code_sha256"])
check(out / "run.json", chains["parent_run"])
assert len(chains["rows"]) == 60
for row in chains["rows"]:
    assert row["status"] == "ok" and len(row["per_image"]) == 100
    assert len(row["set_ms"]) == 3
cube = read(out / "cube-finalists.json")
check(ROOT / "scripts/check_full_cube_finalists.py", cube["source_code_sha256"])
assert len(cube["rows"]) == full_count
expected = {(r["lut"]["path"], v["profile"], v["m"], v["model_sha256"]) for r in reports for v in r["full"]}
actual = {(v["lut"], v["profile"], v["m"], v["model_sha256"]) for v in cube["rows"]}
assert expected == actual
counts = {}
for name, required in (("screen-per-image.csv", 274000), ("per-image.csv", 18800),
                       ("compatibility.csv", 2928), ("chains.csv", 60), ("cube-finalists.csv", 188)):
    with (out / name).open(encoding="utf-8-sig", newline="") as stream:
        counts[name] = sum(1 for _ in csv.DictReader(stream))
    assert counts[name] == required, (name, counts[name], required)
for path, expected in read(out / "workflow-code-sha256.json").items():
    check(ROOT / path, expected)
result = {"status": "ok", "luts": len(reports), "images": len(images), "screen": screen_count,
          "full": full_count, "models_checked": model_count, "chains": 60, "full_cube": len(actual), "csv_rows": counts}
(out / "audit.json").write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
print(json.dumps(result, ensure_ascii=False))
