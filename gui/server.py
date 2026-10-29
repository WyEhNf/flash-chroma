"""仅监听本机的照片调色工作台与真实RAW任务服务。"""
from __future__ import annotations

import argparse
from collections import OrderedDict
import hashlib
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
import io
import json
import mimetypes
import os
from pathlib import Path
import re
import secrets
import shutil
import subprocess
import sys
import threading
import time
from urllib.parse import parse_qs, urlparse
import webbrowser

import numpy as np
from PIL import Image

if __package__:
    from .studio import StudioService, StudioUnavailable, StudioBusy, API_VERSION
else:
    from studio import StudioService, StudioUnavailable, StudioBusy, API_VERSION

ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT / "artifacts/camera-raw-workflow-v1"
JOBS = ROOT / "artifacts/gui-jobs"
STATIC = Path(__file__).with_name("static")
POLICY = ROOT / "experiments/camera-raw-workflow-v1.json"
TOKEN = secrets.token_urlsafe(32)
STUDIO = None
SERVER_SOURCE_SHA256 = hashlib.sha256(Path(__file__).read_bytes()).hexdigest()
LOCK = threading.RLock()
SAMPLES = {}
TASKS = {}
CACHE = OrderedDict()
BRANDS = {"arri": ("ARRI", "ALEXA XT · ARRIRAW", ".ari"),
          "red": ("RED", "EPIC DRAGON · R3D", ".r3d"),
          "blackmagic": ("Blackmagic", "Pocket Cinema Camera 6K · BRAW", ".braw")}
RUNS = {"arri": "run-arri-v1", "red": "run-red-v1", "blackmagic": "run-blackmagic-stream-v1"}
VIDEOS = {"arri": "video-arri-v2", "red": "video-red-v2", "blackmagic": "video-blackmagic-v1"}


def read_json(path):
    return json.loads(Path(path).read_text(encoding="utf-8"))


def write_json(path, value):
    path = Path(path)
    temporary = path.with_name(path.name + ".tmp")
    temporary.write_text(json.dumps(value, ensure_ascii=False, indent=2), encoding="utf-8")
    temporary.replace(path)


def linux_path(path):
    path = str(Path(path).resolve())
    if os.name == "nt":
        drive, rest = os.path.splitdrive(path)
        if not drive or len(drive) != 2:
            raise ValueError("当前工作流只支持本地磁盘路径")
        return "/mnt/" + drive[0].lower() + rest.replace("\\", "/")
    return path


def metrics(data):
    out = {}
    for target in ("sdr", "hdr"):
        branches = [r["branches"][target] for r in data["frames"]]
        n = sum(b["runtime_error"]["channels"] for b in branches)
        out[target] = {"mae": sum(b["runtime_error"]["sum_absolute"] for b in branches) / n * 255,
                       "max": max(b["runtime_error"]["max_normalized"] for b in branches) * 255,
                       "scalar_equal": all(b["scalar_equal"] for b in branches)}
    return out


def public_job(job):
    return {k: v for k, v in job.items() if not k.startswith("_")}


def update_job(job, **changes):
    with LOCK:
        job.update(changes)
        write_json(JOBS / job["id"] / "job-state.json", public_job(job))


def log_job(job, line):
    with LOCK:
        job["logs"] = (job["logs"] + [line.rstrip()])[-160:]
        update_job(job)


def init_catalog():
    JOBS.mkdir(parents=True, exist_ok=True)
    policy = read_json(POLICY)
    for camera, (brand, model, _) in BRANDS.items():
        descriptor = dict(policy["cameras"][camera])
        if camera == "red":
            if (BASE / "red-camera.json").exists():
                descriptor.update(read_json(BASE / "red-camera.json"))
            else:
                published = read_json(ROOT / "report/data/camera-raw-workflow-v1/summary.json")["cameras"]["red"]
                descriptor.update(raw="artifacts/camera-raw-workflow-v1/raw/red/F099_C001_0317IH.R3D", width=published["dimensions"][0], height=published["dimensions"][1], frames=published["frames"], fps=published["fps"])
        raw = ROOT / descriptor["raw"]
        data = read_json(BASE / RUNS[camera] / "results.json") if (BASE / RUNS[camera] / "results.json").exists() else None
        SAMPLES[camera] = {"id": camera, "brand": brand, "camera": camera, "name": raw.name,
            "model": model, "width": descriptor.get("width", 0), "height": descriptor.get("height", 0),
            "frames": descriptor.get("frames", 0), "fps": descriptor.get("fps", 0),
            "input_space": descriptor["input_space"], "raw": str(raw), "available": raw.is_file(),
            "run": "baseline:" + camera if data else None, "metrics": metrics(data) if data else {},
            "outputs_ready": bool(data and data.get("complete"))}
    catalog = JOBS / "imports.json"
    if catalog.exists():
        for sample in read_json(catalog):
            sample["available"] = Path(sample["raw"]).is_file()
            SAMPLES[sample["id"]] = sample
    for path in JOBS.glob("*/job-state.json"):
        try:
            job = read_json(path)
        except (ValueError, OSError):
            print("保留但跳过损坏的旧任务记录：" + str(path), flush=True)
            continue
        if job["status"] in ("running", "queued"):
            job.update(status="failed", message="上次服务已中断；输出保留，可重新创建任务")
        TASKS[job["id"]] = job


def execution_warning():
    renders = sorted((j for j in TASKS.values() if j["action"] == "render"), key=lambda j: j["created"], reverse=True)
    if renders and renders[0]["status"] == "failed":
        message = (renders[0]["message"] + "\n".join(renders[0]["logs"])).replace("\x00", "")
        if "WSL未能启动" in message or "Wsl/Service" in message:
            return "WSL启动异常：新RAW任务暂不可用；已有结果预览和Windows导出可继续使用。"
    return ""


def resolve_run(run):
    if run.startswith("baseline:"):
        camera = run.split(":", 1)[1]
        if camera not in RUNS:
            raise ValueError("未知素材")
        return BASE / RUNS[camera]
    if run.startswith("job:"):
        job_id = run.split(":", 1)[1]
        if job_id not in TASKS or TASKS[job_id]["action"] != "render":
            raise ValueError("未知处理结果")
        return JOBS / job_id / "render"
    raise ValueError("未知结果标识")


def report(run):
    directory = resolve_run(run)
    data = read_json(directory / "results.json")
    return {"camera": data["camera"], "width": data["width"], "height": data["height"],
            "frames": len(data["frames"]), "fps": data["fps"], "fps_scope": data.get("fps_scope"), "metrics": metrics(data),
            "runtime": data["runtime"], "source": str(directory), "scope": data["scope"],
            "preview": "SDR画面转sRGB预览；HDR经PQ解码、Rec2020→709及固定Reinhard映射。预览不参与误差统计。"}


def preview(run, target, frame, kind):
    if target not in ("sdr", "hdr") or kind not in ("reference", "runtime", "difference"):
        raise ValueError("未知预览模式")
    directory = resolve_run(run)
    results = directory / "results.json"
    stamp = results.stat().st_mtime_ns
    key = (run, target, frame, kind, stamp)
    with LOCK:
        if key in CACHE:
            CACHE.move_to_end(key)
            return CACHE[key]
    data = read_json(results)
    if not 0 <= frame < len(data["frames"]):
        raise ValueError("帧索引超出范围")
    w, h = data["width"], data["height"]
    stride = max(1, int(np.ceil(w / 1280)))

    def load(label, dtype, denominator):
        path = directory / (target + "-" + label) / f"frame-{frame:06d}.rgb"
        expected = w * h * 3 * np.dtype(dtype).itemsize
        if path.stat().st_size != expected:
            raise ValueError("帧长度不符，拒绝展示截断结果")
        mapped = np.memmap(path, dtype=dtype, mode="r", shape=(h, w, 3))
        value = mapped[::stride, ::stride].astype(np.float32) / denominator
        del mapped
        return value

    actual = load("runtime8", "u1", 255) if kind != "reference" else None
    reference = load("reference16", "<u2", 65535) if kind != "runtime" else None
    if kind == "difference":
        # 仅可视化导出RGB的8倍差异；数值指标仍使用整帧未裁剪参考台账。
        image = np.clip(np.abs(actual - reference) * 8, 0, 1)
    else:
        image = actual if kind == "runtime" else reference
        if target == "hdr":
            # ST2084常数与D65原色矩阵见阶段说明；固定映射仅用于SDR屏预览。
            q = np.clip(image, 0, 1) ** (1 / (2523 / 4096 * 128))
            nits = 10000 * (np.maximum(q - 3424 / 4096, 0) / np.maximum(2413 / 4096 * 32 - 2392 / 4096 * 32 * q, 1e-8)) ** (1 / (2610 / 4096 / 4))
            matrix = np.array([[1.660491, -0.587641, -0.072850], [-0.124550, 1.132900, -0.008349], [-0.018151, -0.100579, 1.118730]])
            linear = np.maximum(nits @ matrix.T, 0) / 100
            luminance = linear @ np.array([0.2126, 0.7152, 0.0722])
            mapped = luminance * (1 + luminance / 100) / (1 + luminance)
            linear *= (mapped / np.maximum(luminance, 1e-8))[..., None]
        else:
            linear = np.clip(image, 0, 1) ** 2.4
        image = np.where(linear <= 0.0031308, linear * 12.92, 1.055 * np.maximum(linear, 0) ** (1 / 2.4) - 0.055)
    rgb = np.floor(np.clip(image, 0, 1) * 255 + 0.5).astype(np.uint8)
    output = io.BytesIO()
    Image.fromarray(rgb).save(output, format="PNG", compress_level=2)
    payload = output.getvalue()
    with LOCK:
        CACHE[key] = payload
        while len(CACHE) > 40:
            CACHE.popitem(last=False)
    return payload


def run_process(job, command, cwd=ROOT):
    log_job(job, "$ " + subprocess.list2cmdline([str(x) for x in command]))
    with LOCK:
        if job.get("_cancel"):
            raise InterruptedError("任务已取消")
        process = subprocess.Popen(command, cwd=cwd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
            creationflags=subprocess.CREATE_NO_WINDOW if os.name == "nt" else 0)
        job["_process"] = process
        job["_worker_group"] = "setsid" in command
        job.pop("_pgid", None)
    for raw_line in process.stdout:
        # wsl.exe本身的Windows错误是UTF16，Linux工作进程正常输出为UTF8。
        if b"\x00" in raw_line[:100]:
            raw_line += process.stdout.read()
            line = raw_line.decode("utf-16-le", errors="replace")
        else:
            line = raw_line.decode("utf-8", errors="replace")
        log_job(job, line)
        try:
            event = json.loads(line)
            if event.get("event") == "worker" and job["_worker_group"] and int(event["pid"]) > 1:
                job["_pgid"] = int(event["pid"])
                if job.get("_cancel"):
                    cancel(job)
            if "stage" in event:
                update_job(job, stage=event["stage"], progress=event.get("progress", job["progress"]), message=event.get("message", event["stage"]))
        except (ValueError, TypeError):
            pass
    code = process.wait()
    job.pop("_process", None)
    if job.get("_cancel"):
        raise InterruptedError("任务已取消，已写入文件保留")
    if code:
        if job.get("_worker_group") and not job.get("_pgid"):
            raise RuntimeError("WSL未能启动，RAW处理尚未执行；请恢复WSL服务后重试。已有结果浏览和Windows导出仍可使用。")
        raise RuntimeError(f"处理进程退出（{code}），请查看任务日志")


def execute(job, config):
    try:
        update_job(job, status="running", stage="准备", message="检查本地工具和输入", progress=1)
        directory = JOBS / job["id"]
        shutil.copyfile(Path(__file__), directory / "server-source.py")
        if job["action"] == "render":
            shutil.copyfile(ROOT / "gui/worker.py", directory / "worker-source.py")
            if config["camera"] == "arri":
                tool = BASE / "tools/arri-art-cmd-win/bin/art-cmd.exe"
                if not tool.is_file() or os.name != "nt":
                    raise ValueError("需要本地Windows官方ART CMD；当前仅支持单帧.ari")
                decoded = directory / "decoded.exr"
                update_job(job, stage="RAW 解码", message="ART CPU → AWG3 scene-linear EXR", progress=5)
                run_process(job, [str(tool), "process", config["raw_windows"], "--render-platform", "cpu", "--target-colorspace", "AWG3/D65/linear", "--video-codec", "exr_zip/f32", "--output", str(decoded)], cwd=directory)
                if not decoded.is_file():
                    raise RuntimeError("ART未生成EXR，不能以退出码代替实际输出")
                config["decoded_exr"] = linux_path(decoded)
            config_file = directory / "input.json"
            write_json(config_file, config)
            command = ["setsid", "--wait", "python3", "-u", linux_path(ROOT / "gui/worker.py"), "--job", linux_path(config_file)]
            if os.name == "nt":
                command = ["wsl.exe", "--cd", linux_path(ROOT), "--exec"] + command
            run_process(job, command)
            data = read_json(directory / "render/results.json")
            if not data.get("complete"):
                raise ValueError("处理回执未完整完成")
            update_job(job, run="job:" + job["id"], width=data["width"], height=data["height"], frames=len(data["frames"]), fps=data["fps"])
            with LOCK:
                sample = SAMPLES[config["sample"]]
                if sample["id"].startswith("import-"):
                    sample.update(run=job["run"], width=data["width"], height=data["height"], frames=data["source_frames"],
                                  fps=data["fps"], model="导入素材 · 已解码", metrics=metrics(data), outputs_ready=True)
                    write_json(JOBS / "imports.json", [s for s in SAMPLES.values() if s["id"].startswith("import-")])
        else:
            ffmpeg = ROOT / "artifacts/camera-raw-env-v1/Lib/site-packages/imageio_ffmpeg/binaries/ffmpeg-win-x86_64-v7.1.exe"
            if not ffmpeg.is_file():
                raise ValueError("本地Windows FFmpeg未找到，请参阅GUI说明")
            source = resolve_run(config["run"])
            info = read_json(source / "results.json")
            version = 4 if info["width"] * info["height"] > 16_000_000 else 3
            update_job(job, stage="导出与回读", message=f"FFV1 v{version}，四份输出逐字节验证", progress=None)
            run_process(job, [sys.executable, "-X", "utf8", str(ROOT / "experiments/camera-raw-workflow/encode_outputs.py"), "--run", str(source), "--ffmpeg", str(ffmpeg), "--threads", "1", "--context", "0", "--ffv1-version", str(version), "--output", str(directory / "video")])
            if not read_json(directory / "video/results.json").get("complete"):
                raise ValueError("视频回读验证未通过")
        update_job(job, status="completed", stage="完成", progress=100, message="处理与逐字节核对完成")
    except InterruptedError as exc:
        update_job(job, status="cancelled", stage="已取消", message=str(exc), progress=None)
    except Exception as exc:
        log_job(job, str(exc))
        update_job(job, status="failed", stage="失败", message=str(exc), progress=None)


def create_job(action, data):
    with LOCK:
        if any(j["status"] in ("queued", "running") for j in TASKS.values()):
            raise ValueError("已有任务运行，请等待完成或取消后再开始")
        if action == "render":
            sample = SAMPLES[data["sample"]]
            if not Path(sample["raw"]).is_file():
                raise ValueError("RAW文件不存在，请先恢复素材或导入新文件")
            scope = data.get("scope", "first")
            if scope not in ("first", "all"):
                raise ValueError("未知处理范围")
            count = 1 if scope == "first" else max(1, sample["frames"])
            estimate = sample["width"] * sample["height"] * count * 38 + 512 * 1024**2
            if shutil.disk_usage(JOBS).free < estimate:
                raise ValueError(f"空间不足：本任务预计至少需要{estimate / 1024**3:.1f} GiB；已有完整结果仍可直接查看")
            config = {"sample": sample["id"], "camera": sample["camera"], "scope": scope,
                      "raw_windows": sample["raw"], "raw": linux_path(sample["raw"])}
        else:
            source = resolve_run(data["run"])
            info = read_json(source / "results.json")
            if not info.get("complete"):
                raise ValueError("结果尚未完整完成")
            estimate = info["width"] * info["height"] * len(info["frames"]) * 20
            if shutil.disk_usage(JOBS).free < estimate:
                raise ValueError(f"导出空间不足，预计需要{estimate / 1024**3:.1f} GiB")
            config = {"run": data["run"], "sample": data["run"].split(":", 1)[1] if data["run"].startswith("baseline:") else TASKS[data["run"].split(":", 1)[1]]["sample"]}
        job_id = time.strftime("%Y%m%d-%H%M%S-") + secrets.token_hex(3)
        directory = JOBS / job_id
        directory.mkdir()
        config["output"] = linux_path(directory)
        job = {"id": job_id, "sample": config.get("sample", ""), "action": action, "status": "queued",
               "progress": 0, "stage": "准备", "message": "任务已创建", "logs": [], "run": data.get("run"), "created": time.time()}
        TASKS[job_id] = job
        update_job(job)
        threading.Thread(target=execute, args=(job, config), daemon=True).start()
        return public_job(job)


def cancel(job):
    with LOCK:
        if job["status"] not in ("queued", "running"):
            return
        job["_cancel"] = True
        process = job.get("_process")
        pgid = job.get("_pgid")
        worker_group = job.get("_worker_group")
    if pgid:
        command = ["/bin/kill", "-TERM", "--", "-" + str(pgid)]
        if os.name == "nt":
            command = ["wsl.exe", "--exec"] + command
        subprocess.run(command, capture_output=True, timeout=15)
    elif process and process.poll() is None and not worker_group:
        if os.name == "nt":
            subprocess.run(["taskkill", "/PID", str(process.pid), "/T", "/F"], capture_output=True, timeout=15)
        else:
            process.terminate()


class Handler(BaseHTTPRequestHandler):
    def log_message(self, *_):
        pass

    def send(self, status, content, mime="application/json; charset=utf-8", headers=None):
        if not isinstance(content, bytes):
            content = json.dumps(content, ensure_ascii=False).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", mime)
        self.send_header("Content-Length", str(len(content)))
        self.send_header("X-Content-Type-Options", "nosniff")
        self.send_header("Cache-Control", "no-store" if mime.startswith("application/json") else "private, max-age=60")
        for key, value in (headers or {}).items():
            self.send_header(key, value)
        self.end_headers()
        self.wfile.write(content)

    def do_GET(self):
        try:
            if self.headers.get("Host") not in (f"127.0.0.1:{self.server.server_port}", f"localhost:{self.server.server_port}"):
                return self.send(403, {"message": "仅允许本机地址访问"})
            parsed = urlparse(self.path)
            query = {k: v[0] for k, v in parse_qs(parsed.query).items()}
            if parsed.path == "/api/state":
                with LOCK:
                    return self.send(200, {"samples": list(SAMPLES.values()), "execution_warning": execution_warning(), "jobs": [public_job(j) for j in sorted(TASKS.values(), key=lambda j: j["created"], reverse=True)][:30]})
            if parsed.path == "/api/health":
                return self.send(200, {"root": str(ROOT), "status": "ready", "application": "flash-chroma-studio",
                    "api_version": API_VERSION, "studio_api_version": API_VERSION,
                    "engine": STUDIO.engine_info(), "server_source_sha256": SERVER_SOURCE_SHA256,
                    "studio_source_sha256": STUDIO.source_sha256, "studio_catalog_sha256": STUDIO.catalog_sha256})
            if parsed.path == "/api/studio/catalog":
                return self.send(200, STUDIO.catalog())
            if parsed.path == "/api/studio/photo":
                size = query.get("size", "preview")
                return self.send(200, STUDIO.photo(query["id"], size), "image/png" if size == "full" else "image/jpeg")
            if parsed.path == "/api/studio/look":
                return self.send(200, STUDIO.look(query["photo"], query["preset"]), "image/jpeg")
            if parsed.path == "/api/studio/result":
                kind = query.get("kind", "output")
                payload, filename = STUDIO.result(query["id"], kind)
                headers = {"Content-Disposition": f'attachment; filename="{filename}"'} if kind == "download" else None
                return self.send(200, payload, "image/png", headers)
            if parsed.path == "/api/frame":
                return self.send(200, preview(query["run"], query.get("target", "sdr"), int(query.get("frame", 0)), query.get("kind", "runtime")), "image/png")
            if parsed.path == "/api/report":
                return self.send(200, report(query["run"]))
            if parsed.path == "/api/browse":
                path = Path(query.get("path") or BASE / "raw").resolve()
                if not path.is_relative_to(ROOT) or not path.is_dir():
                    raise ValueError("文件浏览限定在当前工程，工程外文件请粘贴完整路径")
                entries = sorted(path.iterdir(), key=lambda p: (not p.is_dir(), p.name.lower()))
                return self.send(200, {"path": str(path), "parent": str(path.parent) if path != ROOT else None,
                    "dirs": [{"name": p.name, "path": str(p)} for p in entries if p.is_dir() and not p.name.startswith(".")],
                    "files": [{"name": p.name, "path": str(p)} for p in entries if p.is_file() and p.suffix.lower() in (".ari", ".r3d", ".braw")]})
            pages = {"/": "studio.html", "/studio": "studio.html", "/studio/": "studio.html",
                     "/raw": "index.html", "/raw/": "index.html"}
            relative = pages.get(parsed.path, parsed.path.lstrip("/").removeprefix("static/"))
            path = (STATIC / relative).resolve()
            if not path.is_relative_to(STATIC) or not path.is_file():
                return self.send(404, {"message": "文件不存在"})
            payload = path.read_bytes()
            if path.name in ("index.html", "studio.html"):
                payload = payload.replace(b"__APP_TOKEN__", TOKEN.encode("ascii"))
            return self.send(200, payload, mimetypes.guess_type(path.name)[0] or "application/octet-stream")
        except StudioUnavailable as exc:
            self.send(503, {"message": str(exc)})
        except StudioBusy as exc:
            self.send(429, {"message": str(exc)})
        except RuntimeError as exc:
            self.send(503, {"message": str(exc)})
        except (ValueError, KeyError, FileNotFoundError, IndexError) as exc:
            self.send(400, {"message": str(exc)})
        except (BrokenPipeError, ConnectionResetError, ConnectionAbortedError):
            pass

    def do_POST(self):
        try:
            hosts = (f"127.0.0.1:{self.server.server_port}", f"localhost:{self.server.server_port}")
            if self.headers.get("Host") not in hosts or (self.headers.get("Origin") and self.headers["Origin"] not in tuple("http://" + h for h in hosts)):
                return self.send(403, {"message": "仅允许本地界面操作"})
            if self.headers.get("X-App-Token") != TOKEN:
                return self.send(403, {"message": "会话已过期，请刷新本地界面"})
            length = int(self.headers.get("Content-Length", 0))
            if not 0 < length <= 16_384:
                raise ValueError("请求长度不合法")
            data = json.loads(self.rfile.read(length))
            if not isinstance(data, dict):
                raise ValueError("请求须为JSON对象")
            if self.path == "/api/studio/render":
                result, _ = STUDIO.render(data)
                return self.send(200, result)
            if self.path in ("/api/run", "/api/export"):
                return self.send(202, {"job": create_job("render" if self.path == "/api/run" else "export", data)})
            if self.path == "/api/cancel":
                cancel(TASKS[data["job"]])
                return self.send(200, {"message": "已请求停止，已写入文件保留"})
            if self.path == "/api/import":
                path = Path(data["path"]).expanduser().resolve()
                camera = data["brand"]
                if camera not in BRANDS or not path.is_file() or path.suffix.lower() != BRANDS[camera][2]:
                    raise ValueError("请选择与品牌匹配的.ari、.R3D或.braw文件")
                ident = "import-" + hashlib.sha256(str(path).encode()).hexdigest()[:12]
                with LOCK:
                    SAMPLES[ident] = {"id": ident, "camera": camera, "brand": BRANDS[camera][0], "model": "导入素材 · 解码后读取参数", "name": path.name,
                        "width": 0, "height": 0, "frames": 0, "fps": 0, "input_space": read_json(POLICY)["cameras"][camera]["input_space"],
                        "raw": str(path), "available": True, "run": None, "metrics": {}, "outputs_ready": False}
                    write_json(JOBS / "imports.json", [s for s in SAMPLES.values() if s["id"].startswith("import-")])
                return self.send(200, {"sample": SAMPLES[ident]})
            if self.path == "/api/open":
                directory = resolve_run(data["run"])
                path = directory / "results.json" if data.get("kind") == "report" else directory
                if os.name == "nt":
                    os.startfile(path)
                else:
                    subprocess.Popen(["xdg-open", str(path)], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
                return self.send(200, {"message": "已打开", "path": str(path)})
            self.send(404, {"message": "未知操作"})
        except StudioUnavailable as exc:
            self.send(503, {"message": str(exc)})
        except StudioBusy as exc:
            self.send(429, {"message": str(exc)})
        except RuntimeError as exc:
            self.send(503, {"message": str(exc)})
        except (ValueError, KeyError, FileNotFoundError, OSError) as exc:
            self.send(400, {"message": str(exc)})


def main():
    global STUDIO
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--port", type=int, default=8765)
    parser.add_argument("--open", action="store_true")
    parser.add_argument("--studio-library", type=Path, help="当前单头运行库完整路径")
    args = parser.parse_args()
    STUDIO = StudioService(ROOT, library=args.studio_library)
    init_catalog()
    try:
        server = ThreadingHTTPServer(("127.0.0.1", args.port), Handler)
    except OSError:
        server = ThreadingHTTPServer(("127.0.0.1", 0), Handler)
    url = f"http://127.0.0.1:{server.server_port}/"
    write_json(JOBS / "server.json", {"url": url, "pid": os.getpid(), "root": str(ROOT)})
    print(url, flush=True)
    if args.open:
        webbrowser.open(url)
    try:
        server.serve_forever(poll_interval=0.25)
    except KeyboardInterrupt:
        pass
    finally:
        for job in list(TASKS.values()):
            cancel(job)
        STUDIO.close()
        server.server_close()


if __name__ == "__main__":
    main()
