"""本机色彩工作台：复用现有拟合与整数映射，不需要前端构建工具。"""
from __future__ import annotations

import argparse
from datetime import datetime, timezone
import hashlib
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
import json
import math
import mimetypes
import os
from pathlib import Path
import platform
import secrets
import threading
import time
import traceback
from urllib.parse import parse_qs, urlsplit
import uuid
import webbrowser
import zipfile

ROOT = Path(__file__).resolve().parents[2]
WEB = Path(__file__).with_name("gui_web")
MAX_UPLOAD = 64 * 1024 * 1024
MAX_PIXELS = 4_000_000
PRESETS = {
    "warm": ("自然暖调", ("曝光与色阶", "暖色校正", "柔和对比", "蓝绿平衡")),
    "cool": ("冷青电影", ("暗部抬升", "冷青偏移", "电影对比", "高光收敛")),
    "identity": ("恒等校验", ("恒等 01", "恒等 02", "恒等 03", "恒等 04")),
}


def digest(path):
    with Path(path).open("rb") as stream:
        return hashlib.file_digest(stream, "sha256").hexdigest()


def demo_transform(rgb, preset, stage):
    """示例定义逐级 RGB8 完整映射；不作为真实摄影色彩空间。"""
    import numpy as np
    x = rgb.astype(np.float64) / 255
    if preset == "identity":
        return rgb.copy()
    if stage == 0:
        x = x ** (.94 if preset == "warm" else .98)
    elif stage == 1:
        x = x * ([1.035, 1.005, .95] if preset == "warm" else [.955, 1.015, 1.04])
    elif stage == 2:
        x = x + (.14 if preset == "warm" else .22) * (x - .5) * x * (1 - x)
    else:
        x = .985 * x + ([.008, .004, .009] if preset == "warm" else [.004, .009, .012])
    return np.clip(np.floor(x * 255 + .5), 0, 255).astype(np.uint8)


def summary(predicted, reference, threshold):
    """仅统计当前完整图片，沿用 RGB 欧氏距离定义。"""
    import numpy as np
    from . import metrics
    error = metrics.delta_e_map(predicted, reference)
    result = metrics.summarize_delta_e(error)
    flat = error.ravel().astype(np.float64)
    count = max(1, math.ceil(len(flat) * .01))
    result.update(cvar_1pct=float(np.partition(flat, len(flat) - count)[-count:].mean()),
                  fraction_ge_threshold=float(np.mean(flat >= threshold)), threshold=threshold,
                  worst_xy=list(reversed([int(v) for v in np.unravel_index(error.argmax(), error.shape)])))
    return result, error


class Workbench:
    """每次启动隔离产物；输入通过不透明 ID 访问，任务串行执行。"""

    def __init__(self, directory, executable=None):
        self.directory = Path(directory).resolve() / uuid.uuid4().hex
        self.directory.mkdir(parents=True)
        self.executable = executable
        self.token = secrets.token_urlsafe(32)
        self.lock = threading.RLock()
        self.assets = {}
        self.jobs = {}
        self.active = None
        self.photos = []
        self.thumbnails = {}
        for listing in [ROOT / "assets/photos/eval.txt"]:
            if listing.is_file():
                for line in listing.read_text(encoding="utf-8").splitlines():
                    path = (ROOT / line.strip()).resolve()
                    if line.strip() and path.is_relative_to(ROOT) and path.is_file():
                        key = "photo-" + hashlib.sha256(line.encode()).hexdigest()[:16]
                        asset = {"id": key, "kind": "image", "name": path.stem, "path": path}
                        self.assets[key] = asset
                        self.photos.append({"id": key, "name": path.stem,
                                            "url": f"/asset/{key}", "group": path.parts[-3]})

    def bootstrap(self):
        with self.lock:
            return {"photos": self.photos, "native": self.executable is not None,
                    "presets": [{"id": f"demo:{key}:{i}", "name": name}
                                for key, (_, names) in PRESETS.items() for i, name in enumerate(names)],
                    "uploads": [{k: v for k, v in a.items() if k not in ("path", "uploaded")}
                                for a in self.assets.values() if a.get("uploaded")],
                    "history": [{"id": j["id"], "result": j["result"]}
                                for j in reversed(list(self.jobs.values())) if j["status"] == "done"],
                    "active": {"id": self.active, "request": self.jobs[self.active]["request"]} if self.active else None,
                    "limits": {"upload_mb": 64, "image_pixels": MAX_PIXELS},
                    "session": self.directory.name[:8]}

    def upload(self, stream, length, name, kind):
        from PIL import Image, ImageOps
        from . import io
        if kind not in ("image", "lut") or not 0 < length <= MAX_UPLOAD:
            raise ValueError("文件类型或大小不符合要求；每份文件最大 64 MiB")
        with self.lock:
            if sum(a.get("uploaded", False) for a in self.assets.values()) >= 32:
                raise ValueError("本次会话已上传 32 份文件，请重新启动工作台后继续")
        suffix = Path(name).suffix.lower()
        if kind == "lut" and suffix not in (".slut", ".lut256"):
            raise ValueError("LUT 请使用项目格式 .slut 或 .lut256")
        key = uuid.uuid4().hex
        path = self.directory / (key + (suffix if kind == "lut" else ".upload"))
        try:
            with path.open("xb") as output:
                remaining = length
                while remaining:
                    part = stream.read(min(1024 * 1024, remaining))
                    if not part:
                        raise ValueError("上传中断，文件未登记")
                    output.write(part)
                    remaining -= len(part)
            detail = {}
            if kind == "image":
                with Image.open(path) as image:
                    if image.width * image.height > MAX_PIXELS:
                        raise ValueError("图片最多 400 万像素；建议使用 1024×768 RGB8")
                    normalized = ImageOps.exif_transpose(image).convert("RGB")
                    target = path.with_suffix(".png")
                    normalized.save(target)
                    detail = {"width": normalized.width, "height": normalized.height}
                path.unlink()
                path = target
            elif suffix == ".slut":
                model = io.load_sparse(path, competition=True)
                detail["m"] = model.m
            elif length != io.FULL_NBYTES:
                raise ValueError(f"完整 LUT 必须恰好包含 {io.FULL_NBYTES} 个 RGB8 字节")
            asset = {"id": key, "name": Path(name.replace("\\", "/")).name[:160],
                     "kind": "image" if kind == "image" else ("sparse" if suffix == ".slut" else "full"),
                     "path": path, "sha256": digest(path), "uploaded": True, **detail}
            with self.lock:
                self.assets[key] = asset
            return {k: v for k, v in asset.items() if k not in ("path", "uploaded")} | {"url": f"/asset/{key}"}
        except Exception as error:
            path.unlink(missing_ok=True)
            if isinstance(error, Image.DecompressionBombError):
                raise ValueError("图片超过尺寸限制；最多允许 400 万像素") from error
            raise

    def submit(self, request):
        if not isinstance(request, dict):
            raise ValueError("任务参数必须为对象")
        m, threshold = request.get("m", 17), request.get("threshold", 3)
        if type(m) is not int or not 17 <= m <= 33:
            raise ValueError("网格边长必须是 17 到 33 的整数")
        if type(threshold) not in (float, int) or not math.isfinite(threshold) or threshold <= 0:
            raise ValueError("自定义阈值必须是有限正数")
        if request.get("method") not in ("sample", "ls_tetra_int", "ls_tetra_jitter"):
            raise ValueError("不支持的拟合方法")
        if request.get("grid") not in ("uniform", "curvature"):
            raise ValueError("不支持的网格布局")
        if request.get("backend") not in ("numpy", "native"):
            raise ValueError("不支持的映射后端")
        if request["backend"] == "native" and self.executable is None:
            raise ValueError("未找到原生运行时，请指定 --executable 或 JSHC_BIN")
        sources = request.get("sources")
        if not isinstance(sources, list) or len(sources) != 4:
            raise ValueError("请按顺序配置四级 LUT")
        with self.lock:
            if request.get("image") not in self.assets or self.assets[request["image"]]["kind"] != "image":
                raise ValueError("请先选择或上传图片")
            for source in sources:
                if not isinstance(source, str):
                    raise ValueError("LUT 标识无效")
                if source.startswith("demo:"):
                    if source not in {f"demo:{key}:{i}" for key in PRESETS for i in range(4)}:
                        raise ValueError("示例 LUT 不存在")
                elif source not in self.assets or self.assets[source]["kind"] not in ("sparse", "full"):
                    raise ValueError("LUT 不存在或类型不匹配")
            if self.active is not None:
                raise ValueError("已有任务正在运行，请完成后再提交")
            if len(self.jobs) >= 50:
                raise ValueError("本次会话已达到 50 个任务，请重新启动后继续")
            key = uuid.uuid4().hex
            self.jobs[key] = {"id": key, "status": "running", "progress": 0,
                              "message": "正在准备图片", "request": request.copy(), "files": {}}
            self.active = key
        threading.Thread(target=self._run, args=(key, request.copy()), daemon=True).start()
        return {"id": key}

    def job(self, key):
        with self.lock:
            job = self.jobs[key]
            return {k: v for k, v in job.items() if k != "files"}

    def update(self, key, **values):
        with self.lock:
            self.jobs[key].update(values)

    def _run(self, key, request):
        started = time.perf_counter()
        directory = self.directory / key
        try:
            import numpy as np
            from . import fit, interp, io, reportio
            directory.mkdir()
            with self.lock:
                image_asset = self.assets[request["image"]].copy()
                sources = [self.assets[s].copy() if not s.startswith("demo:") else s for s in request["sources"]]
            image = io.load_image(image_asset["path"])
            if image.shape[0] * image.shape[1] > MAX_PIXELS:
                raise ValueError("图片超过 400 万像素限制")
            io.save_image(directory / "input.png", image)
            reference = image.copy()
            has_reference = all(isinstance(s, str) or s["kind"] == "full" for s in sources)
            models, stages = [], []
            for index, source in enumerate(sources):
                self.update(key, progress=8 + index * 17, message=f"正在准备第 {index + 1}/4 级 LUT")
                grid = io.uniform_grid(request["m"])
                if isinstance(source, str):
                    _, preset, number = source.split(":")
                    number = int(number)
                    name = PRESETS[preset][1][number]
                    if request["method"] == "sample" and request["grid"] == "uniform":
                        axes = [np.clip(np.round(g), 0, 255).astype(np.uint8) for g in grid]
                        points = np.stack(np.meshgrid(*axes, indexing="ij"), -1)
                        model = io.SparseLut(grid, demo_transform(points, preset, number))
                    else:
                        table = np.empty(io.FULL_SHAPE, np.uint8)
                        for r in range(256):
                            table[r] = demo_transform(np.stack(np.meshgrid([r], range(256), range(256), indexing="ij"), -1)[0], preset, number)
                        if request["grid"] == "curvature":
                            grid = fit.adaptive_grid(table, request["m"])
                        model, _ = fit.fit_model(table, request["m"], request["method"], grid=grid)
                        del table
                    if has_reference:
                        reference = demo_transform(reference, preset, number)
                    provenance = {"kind": "synthetic_demo", "definition": source}
                elif source["kind"] == "sparse":
                    name = source["name"]
                    if digest(source["path"]) != source["sha256"]:
                        raise ValueError("上传模型已改变，任务终止")
                    model = io.load_sparse(source["path"], competition=True)
                    provenance = {"kind": "imported_sparse", "sha256": source["sha256"]}
                else:
                    name = source["name"]
                    if digest(source["path"]) != source["sha256"]:
                        raise ValueError("完整源 LUT 已改变，任务终止")
                    table = io.load_full(source["path"], mmap=True)
                    if request["grid"] == "curvature":
                        grid = fit.adaptive_grid(table, request["m"])
                    model, _ = fit.fit_model(table, request["m"], request["method"], grid=grid)
                    if has_reference:
                        reference = io.apply_full(table, reference)
                    del table
                    provenance = {"kind": "raw_rgb8_full", "sha256": source["sha256"]}
                if isinstance(source, dict) and digest(source["path"]) != source["sha256"]:
                    raise ValueError("源文件在处理过程中改变，未发布结果")
                path = directory / f"stage-{index + 1}.slut"
                io.save_sparse(path, model)
                # 映射使用发布后的实际 Q16 表，不从 float32 网格重新推导。
                models.append(io.load_sparse(path, competition=True))
                positions = np.unique(np.linspace(0, model.m - 1, 5).astype(int))
                points = [{"xyz": [float(model.grid[a, n] / 255) for a, n in enumerate((r, g, b))],
                           "rgb": model.nodes[r, g, b].tolist()}
                          for r in positions for g in positions for b in positions]
                stages.append({"name": name, "m": model.m, "bytes": path.stat().st_size,
                               "node_bytes": model.nodes.nbytes, "sha256": digest(path),
                               "source": provenance, "points": points})
            self.update(key, progress=80, message="正在执行四级整数映射")
            native_record = None
            if request["backend"] == "native":
                from . import runtime
                native_record = runtime.apply([directory / f"stage-{i}.slut" for i in range(1, 5)],
                    directory / "input.png", directory / "output.png", executable=self.executable,
                    kernel="auto", threads=4, competition=False)
                output = io.load_image(directory / "output.png")
            else:
                output = image.copy()
                for model in models:
                    flat = output.reshape(-1, 3)
                    mapped = np.empty_like(flat)
                    for start in range(0, len(flat), 65536):
                        mapped[start:start + 65536] = interp.apply_tetra_q16(model, flat[start:start + 65536])
                    output = mapped.reshape(image.shape)
                io.save_image(directory / "output.png", output)
            self.update(key, progress=92, message="正在统计误差与打包结果")
            scores = None
            if has_reference:
                io.save_image(directory / "reference.png", reference)
                scores, error = summary(output, reference, request["threshold"])
                scale = max(float(error.max()), 1.)
                ramp = np.array([[17, 25, 53], [40, 76, 166], [41, 193, 191], [248, 212, 92], [237, 77, 112]])
                value = np.clip(error / scale, 0, 1)
                heat = np.stack([np.interp(value, np.linspace(0, 1, len(ramp)), ramp[:, c]) for c in range(3)], -1)
                io.save_image(directory / "heatmap.png", heat.astype(np.uint8))
            from . import cache
            result = {"schema": "lutlab_gui_image_v1", "created_utc": datetime.now(timezone.utc).isoformat(),
                      "image": {"name": image_asset["name"], "width": image.shape[1], "height": image.shape[0],
                                "sha256": digest(directory / "input.png"), "competition_size": image.shape[:2] == (768, 1024)},
                      "parameters": request, "stages": stages, "metrics": scores,
                      "reference": "逐级完整 RGB8 映射" if has_reference else "未提供全部完整 LUT，未计算近似误差",
                      "metric": "RGB码值欧氏距离，非CIEDE2000；仅当前图片，非全色域或官方验收",
                      "backend": "NumPy Q16 四面体" if native_record is None else "原生 CPU / auto / 4线程",
                      "native_execution": native_record,
                      "environment": {"python": platform.python_version(), "numpy": np.__version__,
                                      "platform": platform.platform()},
                      "algorithm_source_sha256": cache.source_fingerprint() | {"gui.py": digest(Path(__file__))},
                      "task_seconds": time.perf_counter() - started,
                      "timing_scope": "一次交互任务，含图片读取、拟合、映射、指标与图片写出，不是性能基准",
                      "node_bytes": sum(s["node_bytes"] for s in stages),
                      "serialized_bytes": sum(s["bytes"] for s in stages),
                      "official_threshold_known": False}
            reportio.write_report(directory / "result.json", result)
            names = ["input.png", "output.png", "result.json", *[f"stage-{i}.slut" for i in range(1, 5)]]
            if has_reference:
                names += ["reference.png", "heatmap.png"]
            with zipfile.ZipFile(directory / "results.zip", "w", zipfile.ZIP_DEFLATED) as archive:
                for name in names:
                    archive.write(directory / name, name)
            names.append("results.zip")
            files = {name: directory / name for name in names}
            result["urls"] = {name: f"/result/{key}/{name}" for name in names}
            self.update(key, status="done", progress=100, message="四级映射完成", result=result, files=files)
        except Exception as error:
            try:
                (directory / "error.log").write_text(traceback.format_exc(), encoding="utf-8")
            except OSError:
                pass
            self.update(key, status="failed", message=str(error), progress=0)
        finally:
            with self.lock:
                self.active = None


def make_server(workbench, port=8765):
    class Handler(BaseHTTPRequestHandler):
        def setup(self):
            super().setup()
            self.connection.settimeout(30)

        def log_message(self, *_):
            pass

        def send(self, payload, status=200, content_type="application/json; charset=utf-8"):
            if not isinstance(payload, bytes):
                payload = json.dumps(payload, ensure_ascii=False, allow_nan=False).encode()
            self.send_response(status)
            self.send_header("Content-Type", content_type)
            self.send_header("Content-Length", str(len(payload)))
            self.send_header("Cache-Control", "no-store")
            self.send_header("X-Content-Type-Options", "nosniff")
            self.send_header("Content-Security-Policy", "default-src 'self'; img-src 'self' blob: data:; style-src 'self' 'unsafe-inline'; frame-ancestors 'none'; base-uri 'none'")
            self.end_headers()
            self.wfile.write(payload)

        def trusted(self):
            hosts = (f"127.0.0.1:{self.server.server_port}", f"localhost:{self.server.server_port}")
            return self.headers.get("Host") in hosts

        def do_GET(self):
            if not self.trusted():
                return self.send({"error": "只允许本机访问"}, 403)
            path = urlsplit(self.path).path
            try:
                if path == "/api/bootstrap":
                    return self.send(workbench.bootstrap())
                if path.startswith("/api/job/"):
                    return self.send(workbench.job(path.rsplit("/", 1)[1]))
                if path in ("/", "/app.js", "/app.css"):
                    name = "index.html" if path == "/" else path[1:]
                    payload = (WEB / name).read_bytes()
                    if name == "index.html":
                        payload = payload.replace(b"__SESSION_TOKEN__", workbench.token.encode())
                    return self.send(payload, content_type={"index.html": "text/html; charset=utf-8", "app.js": "text/javascript; charset=utf-8", "app.css": "text/css; charset=utf-8"}[name])
                if path.startswith("/asset/"):
                    with workbench.lock:
                        asset = workbench.assets[path.rsplit("/", 1)[1]].copy()
                    if asset["kind"] != "image":
                        raise KeyError(path)
                    if parse_qs(urlsplit(self.path).query).get("thumbnail") == ["1"]:
                        from PIL import Image
                        import io as bytes_io
                        with workbench.lock:
                            thumbnail = workbench.thumbnails.get(asset["id"])
                        if thumbnail is None:
                            with Image.open(asset["path"]) as image:
                                image.thumbnail((320, 240))
                                stream = bytes_io.BytesIO()
                                image.convert("RGB").save(stream, format="JPEG", quality=80)
                                thumbnail = stream.getvalue()
                            with workbench.lock:
                                workbench.thumbnails[asset["id"]] = thumbnail
                        return self.send(thumbnail, content_type="image/jpeg")
                    return self.send(asset["path"].read_bytes(), content_type="image/png")
                if path.startswith("/result/"):
                    _, _, key, name = path.split("/")
                    with workbench.lock:
                        file = workbench.jobs[key]["files"][name]
                    return self.send(file.read_bytes(), content_type=mimetypes.guess_type(name)[0] or "application/octet-stream")
                raise KeyError(path)
            except (KeyError, ValueError, OSError):
                self.send({"error": "内容不存在或尚未生成"}, 404)

        def do_POST(self):
            origin = self.headers.get("Origin")
            if (not self.trusted() or self.headers.get("X-Lutlab-Token") != workbench.token
                    or (origin is not None and origin not in (f"http://127.0.0.1:{self.server.server_port}", f"http://localhost:{self.server.server_port}"))):
                return self.send({"error": "本机会话校验失败，请刷新页面"}, 403)
            try:
                length = int(self.headers.get("Content-Length", "0"))
                target = urlsplit(self.path)
                if target.path == "/api/upload":
                    params = parse_qs(target.query)
                    result = workbench.upload(self.rfile, length, params.get("name", [""])[0], params.get("kind", [""])[0])
                elif target.path == "/api/run":
                    if not 0 < length <= 16384:
                        raise ValueError("任务参数大小无效")
                    result = workbench.submit(json.loads(self.rfile.read(length)))
                else:
                    return self.send({"error": "接口不存在"}, 404)
                self.send(result)
            except (ValueError, OSError, KeyError, TypeError) as error:
                self.close_connection = True
                self.send({"error": str(error)}, 400)

    server = ThreadingHTTPServer(("127.0.0.1", port), Handler)
    server.daemon_threads = True
    return server


def main(argv=None):
    parser = argparse.ArgumentParser(prog="python -m lutlab gui", description=__doc__)
    parser.add_argument("--port", type=int, default=8765, help="本机端口，0 表示自动选择")
    parser.add_argument("--output", type=Path, default=ROOT / "artifacts/gui", help="会话产物目录")
    parser.add_argument("--executable", type=Path, help="可选 jshc 原生 CPU 运行时")
    parser.add_argument("--no-browser", action="store_true", help="仅启动服务，不自动打开浏览器")
    args = parser.parse_args(argv)
    if not 0 <= args.port <= 65535:
        parser.error("端口必须在 0 到 65535 之间")
    from . import runtime
    executable = args.executable or os.environ.get("JSHC_BIN")
    if executable is not None:
        executable = runtime.resolve_backend("cpu", executable)
    else:
        try:
            executable = runtime.resolve_backend()
        except FileNotFoundError:
            pass
    workbench = Workbench(args.output, executable)
    server = make_server(workbench, args.port)
    url = f"http://127.0.0.1:{server.server_port}"
    print(f"色彩工作台已启动：{url}\n产物目录：{workbench.directory}\n按 Ctrl+C 停止。", flush=True)
    if not args.no_browser:
        webbrowser.open(url)
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        pass
    finally:
        server.server_close()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
