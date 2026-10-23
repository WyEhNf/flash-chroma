"""在WSL内采样内存，在Windows通过真实GUI任务核验固定预算；不降低精度。"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
from pathlib import Path
import re
import subprocess
import sys
import time
import urllib.request

ROOT = Path(__file__).resolve().parents[1]


def sample(destination):
    """每秒记录Linux估算不可回收占用和主要进程RSS；RSS不是PSS。"""
    deadline = time.monotonic() + 600
    with destination.open("x", encoding="utf-8") as stream:
        while time.monotonic() < deadline and not destination.with_suffix(".stop").exists():
            memory = {key: int(value.split()[0]) * 1024 for line in Path("/proc/meminfo").read_text().splitlines()
                      for key, value in [line.split(":", 1)]}
            processes = []
            for directory in Path("/proc").iterdir():
                if not directory.name.isdecimal():
                    continue
                try:
                    fields = dict(line.split(":", 1) for line in (directory / "status").read_text().splitlines() if ":" in line)
                    if fields["Name"].strip() in ("python3", "REDline", "decode_braw_cpu"):
                        processes.append({"pid": int(directory.name), "name": fields["Name"].strip(),
                                          "rss": int(fields.get("VmRSS", "0").split()[0]) * 1024,
                                          "rss_high_water": int(fields.get("VmHWM", "0").split()[0]) * 1024})
                except (OSError, KeyError):
                    pass
            stream.write(json.dumps({"time": time.time(), "memory": memory, "processes": processes}) + "\n")
            stream.flush()
            time.sleep(1)


def linux_path(path):
    path = path.resolve()
    return "/mnt/" + path.drive[0].lower() + path.as_posix()[2:]


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--sample-to", type=Path)
    parser.add_argument("--output", type=Path, default=ROOT / "artifacts/wsl-memory-budget-v1")
    args = parser.parse_args()
    if args.sample_to:
        sample(args.sample_to)
        return
    if os.name != "nt":
        raise SystemExit("任务发起端需要Windows，采样端由WSL运行")
    directory = args.output.resolve()
    directory.mkdir(parents=True, exist_ok=True)
    records = directory / ("samples-" + time.strftime("%Y%m%d-%H%M%S") + ".jsonl")
    html = urllib.request.urlopen("http://127.0.0.1:8765/", timeout=5).read().decode()
    token = re.search(r'window.APP_TOKEN = "([^"]+)"', html).group(1)
    def request(path, payload=None):
        body = json.dumps(payload).encode() if payload is not None else None
        call = urllib.request.Request("http://127.0.0.1:8765" + path, body, {"X-App-Token": token, "Content-Type": "application/json"})
        return json.load(urllib.request.urlopen(call, timeout=15))
    if any(job["status"] in ("queued", "running") for job in request("/api/state")["jobs"]):
        raise SystemExit("GUI已有任务，未继续")
    sampler = subprocess.Popen(["wsl.exe", "-d", "Ubuntu", "-u", "root", "--exec", "python3",
                                linux_path(Path(__file__)), "--sample-to", linux_path(records)],
                               stdout=subprocess.DEVNULL, stderr=(directory / "sampler-stderr.log").open("x"))
    result = {"purpose": "固定预算内真实GUI首帧/取消/导入集成与每秒Linux采样；非52帧或性能验收", "passed": False,
              "wsl_config": (Path.home() / ".wslconfig").read_text(encoding="utf-8-sig")}
    try:
        deadline = time.monotonic() + 30
        while not records.exists():
            if time.monotonic() > deadline or sampler.poll() is not None:
                raise RuntimeError("WSL采样器未能启动")
            time.sleep(.2)
        result["before_state"] = request("/api/state")["execution_warning"]
        job = request("/api/run", {"sample": "arri", "scope": "first"})["job"]
        result["new_arri_job"] = job["id"]
        deadline = time.monotonic() + 180
        previous = None
        while time.monotonic() < deadline:
            current = next(row for row in request("/api/state")["jobs"] if row["id"] == job["id"])
            if (current["status"], current["stage"]) != previous:
                print(json.dumps({"job": current["id"], "status": current["status"], "stage": current["stage"]}, ensure_ascii=False), flush=True)
                previous = current["status"], current["stage"]
            if current["status"] in ("completed", "failed", "cancelled"):
                if current["status"] != "completed":
                    raise RuntimeError(str(current))
                break
            time.sleep(.5)
        else:
            raise TimeoutError("ARRI任务超时，保留现场")
        subprocess.run([sys.executable, "-X", "utf8", str(ROOT / "gui/smoke_test.py"), "--output", str(directory / "gui-integration.json")], check=True)
        # 增补本次ARRI实跑的四路SHA，而非仅沿用历史ARRI任务。
        baseline = ROOT / "artifacts/camera-raw-workflow-v1/run-arri-v1"
        new = ROOT / "artifacts/gui-jobs" / job["id"] / "render"
        result["new_arri_sha_equal"] = []
        for branch in ("sdr-reference16", "sdr-runtime8", "hdr-reference16", "hdr-runtime8"):
            def digest(path):
                with path.open("rb") as stream:
                    return hashlib.file_digest(stream, "sha256").hexdigest()
            assert digest(new / branch / "frame-000000.rgb") == digest(baseline / branch / "frame-000000.rgb")
            result["new_arri_sha_equal"].append(branch)
        result["after_state"] = request("/api/state")["execution_warning"]
        result["passed"] = True
    except Exception as error:
        result["error"] = str(error)
    finally:
        records.with_suffix(".stop").touch()
        try:
            sampler.wait(timeout=10)
        except subprocess.TimeoutExpired:
            result["sampler_stop_timeout"] = True
        if records.exists():
            samples = [json.loads(line) for line in records.read_text().splitlines()]
            result["memory"] = {"sample_seconds": 1, "count": len(samples),
                "guest_used_estimate_peak_bytes": max(s["memory"]["MemTotal"] - s["memory"]["MemAvailable"] for s in samples),
                "swap_used_peak_bytes": max(s["memory"]["SwapTotal"] - s["memory"]["SwapFree"] for s in samples),
                "process_rss_high_water_bytes": {name: max((p["rss_high_water"] for s in samples for p in s["processes"] if p["name"] == name), default=0)
                                                  for name in ("python3", "REDline", "decode_braw_cpu")}}
        (directory / "workload-verification.json").write_text(json.dumps(result, ensure_ascii=False, indent=2), encoding="utf-8")
        print(json.dumps(result, ensure_ascii=False), flush=True)
    if not result["passed"]:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
