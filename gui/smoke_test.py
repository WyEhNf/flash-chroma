"""对运行中的本地GUI执行真实API集成检查；会创建独立首帧任务。"""
from __future__ import annotations

import argparse
import hashlib
import importlib.util
import io
import json
from pathlib import Path
import re
import shutil
import subprocess
import time
import urllib.error
import urllib.parse
import urllib.request

from PIL import Image

ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT / "artifacts/camera-raw-workflow-v1"
JOBS = ROOT / "artifacts/gui-jobs"


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--url", default="http://127.0.0.1:8765")
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--views-only", action="store_true", help="只查既有结果和接口，不创建RAW任务")
    args = parser.parse_args()
    url = args.url.rstrip("/")
    html = urllib.request.urlopen(url + "/").read().decode("utf-8")
    token = re.search(r'window.APP_TOKEN = "([^"]+)"', html).group(1)
    checks = []

    def request(path, data=None, headers=None, expected=200, binary=False):
        h = {"X-App-Token": token, "Content-Type": "application/json"}
        h.update(headers or {})
        payload = json.dumps(data).encode("utf-8") if data is not None else None
        try:
            response = urllib.request.urlopen(urllib.request.Request(url + path, payload, headers=h), timeout=30)
        except urllib.error.HTTPError as error:
            response = error
        body = response.read()
        assert response.status == expected, (path, response.status, body[:300])
        return body if binary else json.loads(body)

    def wait(job, desired="completed"):
        deadline = time.monotonic() + 150
        while time.monotonic() < deadline:
            current = next(j for j in request("/api/state")["jobs"] if j["id"] == job["id"])
            if current["status"] in ("completed", "failed", "cancelled"):
                assert current["status"] == desired, current
                print(json.dumps({"job": current["id"], "status": current["status"]}), flush=True)
                return current
            time.sleep(.25)
        raise TimeoutError("GUI任务未在150秒内结束")

    state = request("/api/state")
    assert all(s["outputs_ready"] for s in state["samples"] if s["id"] in ("arri", "red", "blackmagic"))
    for camera in ("arri", "red", "blackmagic"):
        for target in ("sdr", "hdr"):
            for kind in ("reference", "runtime", "difference"):
                query = urllib.parse.urlencode({"run": "baseline:" + camera, "target": target, "frame": 0, "kind": kind})
                image = Image.open(io.BytesIO(request("/api/frame?" + query, binary=True)))
                assert image.mode == "RGB" and 0 < image.width <= 1280
                checks.append(f"{camera}/{target}/{kind}真实PNG")
    request("/api/frame?run=baseline:arri&frame=1", expected=400)
    request("/api/run", {"sample": "arri"}, {"X-App-Token": "invalid"}, expected=403)
    request("/api/state", headers={"Host": "invalid.example"}, expected=403)
    request("/api/run", {"sample": "arri"}, {"Origin": "https://invalid.example"}, expected=403)
    request("/%2e%2e/AGENTS.md", expected=404)
    checks += ["非法帧拒绝", "无效会话拒绝", "外部Host拒绝", "外部Origin拒绝", "静态路径越界拒绝"]
    if args.views_only:
        result = {"purpose": "GUI既有真实数据预览与接口边界；不执行新RAW任务", "checks": checks, "all_passed": True}
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(json.dumps(result, ensure_ascii=False, indent=2), encoding="utf-8")
        print(json.dumps({"checks": len(checks), "all_passed": True}), flush=True)
        return

    # 立即取消RED，专门覆盖worker PID尚未公布的启动窗口。
    cancelled = request("/api/run", {"sample": "red", "scope": "first"}, expected=202)["job"]
    request("/api/cancel", {"job": cancelled["id"]})
    cancelled = wait(cancelled, "cancelled")
    worker_events = [json.loads(line) for line in cancelled["logs"] if line.startswith('{"event": "worker"')]
    if worker_events:
        pid = worker_events[-1]["pid"]
        assert subprocess.run(["wsl.exe", "--exec", "/bin/kill", "-0", str(pid)], capture_output=True).returncode != 0
        checks.append("启动窗口取消已终止真实worker，未误报成功")
    else:
        checks.append("取消发生在worker未启动时；不声称验证了Linux进程组终止")

    red = wait(request("/api/run", {"sample": "red", "scope": "first"}, expected=202)["job"])
    catalog_path = JOBS / "imports.json"
    original_catalog = catalog_path.read_bytes() if catalog_path.exists() else b"[]"
    fixture = JOBS / "GUI导入测试-Train.braw"
    if not fixture.exists():
        shutil.copyfile(BASE / "raw/blackmagic/The-End-of-the-World-Train-Original.braw", fixture)
    try:
        imported = request("/api/import", {"path": str(fixture), "brand": "blackmagic"})["sample"]
        braw = wait(request("/api/run", {"sample": imported["id"], "scope": "first"}, expected=202)["job"])
        sample = next(s for s in request("/api/state")["samples"] if s["id"] == imported["id"])
        assert sample["frames"] == 52 and sample["width"] == 6144 and sample["run"] == braw["run"]
        spec = importlib.util.spec_from_file_location("gui_catalog_check", ROOT / "gui/server.py")
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        module.init_catalog()
        assert module.SAMPLES[imported["id"]]["run"] == braw["run"]
        checks.append("新导入首帧结果绑定/总52帧/重新载入目录均正确")
        arri = next(j for j in state["jobs"] if j["sample"] == "arri" and j["action"] == "render" and j["status"] == "completed")
        compare = []
        for camera, job, baseline in (("arri", arri, "run-arri-v1"), ("red", red, "run-red-v1"), ("blackmagic", braw, "run-blackmagic-stream-v1")):
            result = json.loads((JOBS / job["id"] / "render/results.json").read_text(encoding="utf-8"))
            for target in ("sdr", "hdr"):
                assert result["frames"][0]["branches"][target]["scalar_equal"]
                for kind in ("reference16", "runtime8"):
                    def sha(path):
                        with path.open("rb") as stream:
                            return hashlib.file_digest(stream, "sha256").hexdigest()
                    path = JOBS / job["id"] / "render" / f"{target}-{kind}" / "frame-000000.rgb"
                    assert sha(path) == sha(BASE / baseline / f"{target}-{kind}" / "frame-000000.rgb")
                    compare.append(f"{camera}/{target}/{kind}")
        exports = next(j for j in state["jobs"] if j["action"] == "export" and j["status"] == "completed")
        video = json.loads((JOBS / exports["id"] / "video/results.json").read_text(encoding="utf-8"))
        assert video["complete"] and len(video["files"]) == 4 and all(f["roundtrip_equal"] for f in video["files"])
        result = {"purpose": "GUI API真实集成；三家各首帧，不重复完整52帧或性能门禁", "checks": checks,
                  "jobs": {"arri": arri["id"], "red": red["id"], "blackmagic_import": braw["id"], "cancelled": cancelled["id"], "export": exports["id"]},
                  "baseline_first_frame_sha_equal": compare, "export_files_roundtrip_equal": 4,
                  "fixture_catalog_restored_after_test": True, "all_passed": True}
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(json.dumps(result, ensure_ascii=False, indent=2), encoding="utf-8")
        print(json.dumps({"checks": len(checks), "baseline_outputs": len(compare), "all_passed": True}), flush=True)
    finally:
        # 仅恢复本测试增加的目录登记，RAW和结果文件全部保留。
        (JOBS / "integration-imports.json").write_bytes(catalog_path.read_bytes())
        catalog_path.write_bytes(original_catalog)


if __name__ == "__main__":
    main()
