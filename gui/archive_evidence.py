"""归档GUI阶段的明确测试任务；只保存文本，不收集用户后续任务或像素。"""
import argparse
import hashlib
import json
from pathlib import Path
import zipfile

ROOT = Path(__file__).resolve().parents[1]
JOBS = ROOT / "artifacts/gui-jobs"
DEST = ROOT / "report/data/camera-workflow-gui-v1"
IDS = ("20261023-181332-4854ed", "20261023-181501-c1d5d7", "20261023-181626-fa5881",
       "20261023-182406-b3eed5", "20261023-182413-01a13f")


def sha(payload):
    return hashlib.sha256(payload).hexdigest()


def verify():
    manifest = json.loads((DEST / "manifest.json").read_text(encoding="utf-8"))
    payload = (DEST / "evidence.zip").read_bytes()
    assert sha(payload) == manifest["zip_sha256"]
    with zipfile.ZipFile(DEST / "evidence.zip") as archive:
        assert archive.testzip() is None
        assert sorted(archive.namelist()) == sorted(r["path"] for r in manifest["files"])
        for row in manifest["files"]:
            data = archive.read(row["path"])
            assert len(data) == row["bytes"] and sha(data) == row["sha256"]
    print(json.dumps({"files": len(manifest["files"]), "zip_sha_crc_equal": True}))


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--verify", action="store_true")
    args = parser.parse_args()
    if args.verify:
        return verify()
    DEST.mkdir(parents=True, exist_ok=False)
    paths = []
    for ident in IDS:
        paths += [p for p in (JOBS / ident).rglob("*") if p.is_file() and p.suffix in (".py", ".json", ".log")]
    paths += [p for p in (JOBS / "gui-stage").rglob("*") if p.is_file() and p.suffix in (".py", ".json", ".txt", ".log")]
    paths += [JOBS / "view-verification.json", JOBS / "arri-verification.json", JOBS / "wsl-startup-failure.json"]
    rows = []
    with zipfile.ZipFile(DEST / "evidence.zip", "x", zipfile.ZIP_DEFLATED, compresslevel=9) as archive:
        for path in sorted(set(paths)):
            payload = path.read_bytes()
            name = path.relative_to(ROOT).as_posix()
            archive.writestr(name, payload)
            rows.append({"path": name, "bytes": len(payload), "sha256": sha(payload)})
    manifest = {"files": rows, "zip_sha256": sha((DEST / "evidence.zip").read_bytes()),
                "scope": "明确的五份开发测试任务及阶段文本；不含第三方素材、像素、截图或用户后续任务"}
    (DEST / "manifest.json").write_text(json.dumps(manifest, ensure_ascii=False, indent=2), encoding="utf-8")
    for name in ("verification.json",):
        (DEST / name).write_bytes((JOBS / "gui-stage" / name).read_bytes())
    verify()


if __name__ == "__main__":
    main()
