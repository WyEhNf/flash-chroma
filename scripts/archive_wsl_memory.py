"""归档本阶段已执行的文本证据；不包含RAW、像素、视频或交换文件。"""
from pathlib import Path
import argparse
import ast
import hashlib
import json
import re
import zipfile

ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT / "artifacts/wsl-memory-budget-v1"
PUBLIC = ROOT / "report/data/wsl-memory-budget-v1"


def sha(data):
    return hashlib.sha256(data).hexdigest()


def verify():
    manifest = json.loads((PUBLIC / "manifest.json").read_text(encoding="utf-8"))
    archive = PUBLIC / "evidence.zip"
    assert sha(archive.read_bytes()) == manifest["archive_sha256"]
    with zipfile.ZipFile(archive) as source:
        assert source.testzip() is None
        assert set(source.namelist()) == {entry["path"] for entry in manifest["files"]}
        for entry in manifest["files"]:
            assert sha(source.read(entry["path"])) == entry["sha256"]
    print(json.dumps({"archive_files": len(manifest["files"]), "sha_crc_passed": True}))


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--verify", action="store_true")
    args = parser.parse_args()
    if args.verify:
        verify()
        return
    final = json.loads((BASE / "run-1gb/workload-verification.json").read_text(encoding="utf-8"))
    integration = json.loads((BASE / "run-1gb/gui-integration.json").read_text(encoding="utf-8"))
    assert final["passed"] and integration["all_passed"]
    remote = json.loads((BASE / "remote-preflight.json").read_text(encoding="utf-8"))
    previous = json.loads((ROOT / "artifacts/gui-jobs/gui-stage/remote-preflight.json").read_text(encoding="utf-8"))
    old_bodies = {row["issue_number"]: row["body"] for row in previous["all_prs"]["issues"]}
    related = remote["related"][0]["issues"]
    for row in related:
        original = remote["preflight"][0]["body"] if row["issue_number"] == 84 else old_bodies[row["issue_number"]]
        assert row["body"] == original, row["issue_number"]
    summary = {"purpose": "WSL固定预算与GUI真实首帧恢复；不是性能门禁或完整52帧验收",
               "base_commit": "57e935cea832aeef0147c99673e64cf8e11cb564",
               "environment": "Windows11 26200.9711 / Ryzen9 8945HX / WSL2.7.10 / Linux6.18.33.2；Python3.13.12及3.14.4，NumPy2.4.6、OCIO2.6.0、OpenEXR3.5.2；修订78 AVX2普通路径4线程，标量1线程",
               "verification": final, "integration": integration, "output_hashes": [],
               "remote": {"full_related_pr_bodies_compared": [r["issue_number"] for r in related],
                          "unchanged": True, "parent_head": remote["preflight"][0]["head_sha"],
                          "parent_comments_reviews_threads": [remote["preflight"][i] for i in (1,2,3)],
                          "issues": [7,8], "discussion_refresh_gap": True},
               "limits": ["1秒采样可能漏掉短时峰值，RSS不是PSS", "全52帧/长时/性能未重跑", "视频回执复用旧ARRI，不算新编码", "GPU设备禁用未证实", "Windows提交压力仍可能影响其他输入"]}
    for camera in ("arri", "red", "blackmagic_import"):
        directory = ROOT / "artifacts/gui-jobs" / integration["jobs"][camera] / "render"
        result = json.loads((directory / "results.json").read_text(encoding="utf-8"))
        for target in ("sdr", "hdr"):
            for kind in ("reference16", "runtime8"):
                path = directory / f"{target}-{kind}/frame-000000.rgb"
                with path.open("rb") as stream:
                    digest = hashlib.file_digest(stream, "sha256").hexdigest()
                summary["output_hashes"].append({"camera": camera, "branch": f"{target}-{kind}", "bytes": path.stat().st_size, "sha256": digest})
    sources = [ROOT / path for path in ("scripts/configure_wsl_memory.py", "scripts/archive_wsl_memory.py", "gui/measure_wsl_memory.py")]
    for path in sources:
        ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
    PUBLIC.mkdir(parents=True, exist_ok=False)
    summary["static_python_ast"] = len(sources)
    (PUBLIC / "summary.json").write_text(json.dumps(summary, ensure_ascii=False, indent=2), encoding="utf-8")
    selected = sources + [p for p in BASE.rglob("*") if p.is_file() and p.suffix in (".json", ".jsonl", ".log", ".bin")]
    jobs = {integration["jobs"][key] for key in ("arri", "red", "blackmagic_import", "cancelled")} | {"20261023-201344-2baf16"}
    for job in jobs:
        assert re.fullmatch(r"\d{8}-\d{6}-[a-f0-9]{6}", job)
        selected += [path for path in (ROOT / "artifacts/gui-jobs" / job).rglob("*") if path.is_file() and path.suffix in (".py", ".json", ".log")]
    entries = []
    with zipfile.ZipFile(PUBLIC / "evidence.zip", "w", zipfile.ZIP_DEFLATED, compresslevel=9) as archive:
        for path in sorted(set(selected)):
            name = path.relative_to(ROOT).as_posix()
            payload = path.read_bytes()
            payload.decode("utf-8-sig")
            archive.writestr(name, payload)
            entries.append({"path": name, "bytes": len(payload), "sha256": sha(payload)})
    manifest = {"archive_sha256": sha((PUBLIC / "evidence.zip").read_bytes()), "files": entries}
    (PUBLIC / "manifest.json").write_text(json.dumps(manifest, ensure_ascii=False, indent=2), encoding="utf-8")
    verify()


if __name__ == "__main__":
    main()
