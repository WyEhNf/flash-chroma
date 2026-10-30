"""归档本阶段模型和文本证据；排除摄影机像素与第三方二进制。"""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
import zipfile

ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT / "artifacts/camera-raw-workflow-v1"
DEST = ROOT / "report/data/camera-raw-workflow-v1"


def sha(data):
    return hashlib.sha256(data).hexdigest()


def sources():
    selected = list((ROOT / "experiments/camera-raw-workflow").glob("*.py"))
    selected += list((ROOT / "experiments/camera-raw-workflow").glob("*.cpp"))
    selected += [ROOT / "experiments/camera-raw-workflow-v1.json",
                 ROOT / "scripts/fetch_camera_raw_asset.py", Path(__file__).resolve()]
    selected += [p for p in BASE.iterdir() if p.suffix in (".json", ".log", ".txt", ".py")]
    for directory in BASE.iterdir():
        if directory.is_dir() and (directory.name.startswith("run-") or directory.name.startswith("video-")):
            selected += [p for p in directory.rglob("*") if p.suffix in (".json", ".log")]
    selected += list((BASE / "models-v2").iterdir())
    selected += list((BASE / "decoded").rglob("*.json"))
    selected += list((BASE / "decoded").rglob("*.log"))
    selected += [ROOT / "artifacts/camera-raw-env-v1/Lib/site-packages/opencolorio-2.6.0.dist-info/licenses/LICENSE"]
    return sorted({p for p in selected if p.is_file()}, key=lambda p: p.relative_to(ROOT).as_posix())


def verify():
    manifest = json.loads((DEST / "manifest.json").read_text(encoding="utf-8"))
    archive = DEST / "evidence.zip"
    if sha(archive.read_bytes()) != manifest["zip_sha256"]:
        raise AssertionError("ZIP整体哈希不符")
    with zipfile.ZipFile(archive) as zipped:
        if zipped.testzip() is not None:
            raise AssertionError("ZIP CRC失败")
        if sorted(zipped.namelist()) != sorted(row["path"] for row in manifest["files"]):
            raise AssertionError("ZIP成员集合不符")
        for row in manifest["files"]:
            payload = zipped.read(row["path"])
            if len(payload) != row["bytes"] or sha(payload) != row["sha256"]:
                raise AssertionError("归档成员哈希不符：" + row["path"])
    print(json.dumps({"files": len(manifest["files"]), "zip_bytes": archive.stat().st_size,
                      "sha256_and_crc_equal": True}, ensure_ascii=False))


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--verify", action="store_true", help="只读核对归档，无需本地RAW或工具")
    args = parser.parse_args()
    if args.verify:
        verify()
        return
    # 同一目录只创建一次，保留已交付的字节。
    DEST.mkdir(parents=True, exist_ok=False)
    rows = []
    with zipfile.ZipFile(DEST / "evidence.zip", "x", compression=zipfile.ZIP_DEFLATED, compresslevel=9) as zipped:
        for path in sources():
            name = path.relative_to(ROOT).as_posix()
            payload = path.read_bytes()
            info = zipfile.ZipInfo(name, (2026, 10, 23, 0, 0, 0))
            info.compress_type = zipfile.ZIP_DEFLATED
            zipped.writestr(info, payload)
            rows.append({"path": name, "bytes": len(payload), "sha256": sha(payload)})
    manifest = {"purpose": "独立验证归档完整性；不重新执行像素、不证明性能或画质通过",
                "excluded": "RAW、解码/调色像素、MKV、厂商SDK/可执行文件、Python环境均只在本地artifact",
                "files": rows, "zip_sha256": sha((DEST / "evidence.zip").read_bytes())}
    (DEST / "manifest.json").write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    for filename in ("summary.json", "agent-final-audit.json", "source-manifest.json"):
        (DEST / filename).write_bytes((BASE / filename).read_bytes())
    verify()


if __name__ == "__main__":
    main()
