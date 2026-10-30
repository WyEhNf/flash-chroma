"""GUI的隔离CPU任务：官方RAW解码、固定四级变换和全像素验证。"""
from __future__ import annotations

import argparse
from concurrent.futures import ThreadPoolExecutor
import hashlib
import json
import os
from pathlib import Path
import re
import shutil
import subprocess
import sys
import time

ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT / "artifacts/camera-raw-workflow-v1"
sys.path.insert(0, str(BASE / "linux-site"))
sys.path.insert(0, str(ROOT / "experiments/camera-raw-workflow"))
if __name__ == "__main__":
    # 在载入扩展前公布独立进程组，取消可覆盖初始化阶段。
    print(json.dumps({"event": "worker", "pid": os.getpid()}), flush=True)
import numpy as np
import OpenEXR
import PyOpenColorIO as ocio
import pipeline
from runtime_bridge import Runtime
from stream_pipeline import add_metric, finish_metric

pipeline.np, pipeline.ocio = np, ocio
TILE = 262144


def emit(stage, progress=None, **kwargs):
    print(json.dumps({"stage": stage, "progress": progress, **kwargs}, ensure_ascii=False), flush=True)


def invoke(command, directory, name, cwd=ROOT, env=None, allowed_codes=(0,)):
    log = directory / (name + ".log")
    with log.open("x", encoding="utf-8") as stream:
        process = subprocess.Popen([str(v) for v in command], cwd=cwd, env=env, stdout=subprocess.PIPE,
                                   stderr=subprocess.STDOUT, text=True, encoding="utf-8", errors="replace")
        for line in process.stdout:
            stream.write(line)
            stream.flush()
        code = process.wait()
    record = {"command": [str(v) for v in command], "cwd": str(cwd), "returncode": code,
              "log": str(log), "log_sha256": pipeline.sha(log)}
    pipeline.dump(directory / (name + "-invocation.json"), record)
    if code not in allowed_codes:
        raise RuntimeError(f"官方解码失败({code})，日志：{log}")
    return log.read_text(encoding="utf-8")


def check_space(directory, width, height, count, bytes_per_pixel):
    needed = int(width * height * count * bytes_per_pixel * 1.15) + 256 * 1024**2
    if shutil.disk_usage(directory).free < needed:
        raise RuntimeError(f"空间不足：实际尺寸预计还需{needed / 1024**3:.1f} GiB，未继续解码")


def decode(config, directory):
    camera, raw = config["camera"], Path(config["raw"])
    if camera == "arri":
        path = Path(config["decoded_exr"])
        with OpenEXR.File(str(path)) as exr:
            shape = exr.channels()["RGB"].pixels.shape
            if len(shape) != 3 or shape[2] != 3:
                raise ValueError("ARRI EXR不是RGB")
        # .ari导入明确为单帧；不从未知元数据补造帧率。
        fps = 24 if raw.name == "L001C028_140110_R6MS.0018267.ari" else "未知"
        return {"width": shape[1], "height": shape[0], "frames": 1, "source_frames": 1, "fps": fps,
                "decoded_space": "Linear ARRI Wide Gamut 3", "paths": [str(path)],
                "decoder": "ART CMD 1.0.0 Windows CPU / AWG3/D65/linear EXR32"}
    if camera == "blackmagic":
        tool = BASE / "tools/braw-api-3.3"
        env = os.environ.copy()
        env["LD_LIBRARY_PATH"] = ":".join(str(p) for p in (tool, BASE / "tools/llvm-runtime/usr/lib/llvm-18/lib", BASE / "tools/llvm-runtime/usr/lib/x86_64-linux-gnu"))
        binary = tool / "decode_braw_cpu"
        metadata = json.loads(invoke([binary, raw, directory / "braw-log", "0"], directory, "braw-inspect", cwd=tool, env=env))
        count = 1 if config["scope"] == "first" else int(metadata["frames"])
        check_space(directory, metadata["width"], metadata["height"], count, 30)
        decoded = json.loads(invoke([binary, raw, directory / "braw-log", str(count)], directory, "braw-decode", cwd=tool, env=env))
        if decoded["decoded_frames"] != count or decoded["post_lut"] != "Disabled" or decoded["color_science_gen"] != 5:
            raise ValueError("BRAW解码帧数或Gen5/关闭post LUT契约不符")
        paths = sorted((directory / "braw-log").glob("frame-*.rgbf32"))
        return {"width": decoded["width"], "height": decoded["height"], "frames": count,
                "source_frames": int(metadata["frames"]), "fps": decoded["fps"], "decoded_space": "BMDFilm WideGamut Gen5",
                "paths": [str(p) for p in paths], "decoder": "官方BRAW API3.3 / CPU AVX2 4线程 / Gen5 Film float32"}
    tool = BASE / "tools/redline-linux"
    env = os.environ.copy()
    env["LD_LIBRARY_PATH"] = "."
    # REDline的纯元数据查询在本版本可返回1；必须再核对实际字段，像素解码仍只接受0。
    metadata_text = invoke(["../bin/REDline", "--i", raw, "--printMeta", "1"], directory, "red-metadata", cwd=tool / "libs", env=env, allowed_codes=(0, 1))
    metadata = dict(line.split(":\t", 1) for line in metadata_text.splitlines() if ":\t" in line)
    width, height, total = (int(metadata[k].strip()) for k in ("Frame Width", "Frame Height", "Total Frames"))
    if min(width, height, total) <= 0:
        raise ValueError("RED元数据没有有效的尺寸和帧数")
    count = 1 if config["scope"] == "first" else total
    check_space(directory, width, height, count, 36)
    tiff_dir = directory / "red-tiff"
    tiff_dir.mkdir()
    text = invoke(["../bin/REDline", "--i", raw, "--o", tiff_dir / "frame.tif", "--format", "1", "--start", "0",
        "--end", str(count - 1), "--res", "1", "--gpuPlatform", "0", "--decodeThreads", "4", "--useMeta",
        "--colorSpace", "25", "--gammaCurve", "34", "--verbose"], directory, "red-decode", cwd=tool / "libs", env=env)
    if "Gpu Decoding: Disabled" not in text or "Gamma Curve: Log3G10" not in text or "ColorSpace: REDWideGamutRGB" not in text:
        raise ValueError("RED CPU/RWG/Log3G10日志契约不符")
    tiffs = sorted(tiff_dir.glob("*.tif"))
    if len(tiffs) != count:
        raise ValueError(f"RED实际TIFF帧数{len(tiffs)}，预期{count}")
    import tifffile
    decoded_dir = directory / "red-log"
    decoded_dir.mkdir()
    paths = []
    for index, path in enumerate(tiffs):
        values = tifffile.memmap(path, mode="r")
        if values.dtype != np.uint16 or values.shape != (height, width, 3):
            raise ValueError("RED TIFF实际维度/类型不符")
        target = decoded_dir / f"frame-{index:06d}.rgbf32"
        with target.open("xb") as stream:
            for y in range(0, height, 32):
                integers = values[y:y + 32]
                floating = integers.astype("<f4") / np.float32(65535)
                if not np.array_equal(np.floor(floating * np.float32(65535) + .5).astype(np.uint16), integers):
                    raise ValueError("TIFF16归一化代码值往返失败")
                stream.write(floating.tobytes())
        del values
        paths.append(str(target))
    return {"width": width, "height": height, "frames": count, "source_frames": total, "fps": metadata.get("FPS", "未知").strip(),
            "decoded_space": "Log3G10 REDWideGamutRGB", "paths": paths,
            "decoder": "官方REDline65.0.22 / CPU4线程 / 元数据色彩科学 / RWG Log3G10 TIFF16归一化float32；非原生float32"}


def render(config, decoded, directory):
    policy_path = ROOT / "experiments/camera-raw-workflow-v1.json"
    policy = json.loads(policy_path.read_text(encoding="utf-8"))
    model_dir = BASE / "models-v2"
    manifest = json.loads((model_dir / "manifest.json").read_text(encoding="utf-8"))
    if pipeline.sha(policy_path) != manifest["policy_sha256"]:
        raise ValueError("固定策略与模型身份不符")
    color_config, _, processors = pipeline.graph(policy)
    if hashlib.sha256(color_config.serialize().encode()).hexdigest() != manifest["config_sha256"]:
        raise ValueError("实际OCIO配置与已验模型不符")
    models = {}
    for name, entry in manifest["models"].items():
        models[name] = {extension: model_dir / (name + "." + extension) for extension in ("slut", "cube")}
        for extension, path in models[name].items():
            if pipeline.sha(path) != entry[extension + "_sha256"]:
                raise ValueError("固定模型哈希不符")
    camera = config["camera"]
    names = [camera + "-input", "balance", "look"]
    lut_processors = {name: color_config.getProcessor(ocio.FileTransform(src=str(models[name]["cube"]), interpolation=ocio.INTERP_TETRAHEDRAL)).getDefaultCPUProcessor() for name in names + ["sdr", "hdr"]}
    source_space = policy["cameras"][camera]["input_space"]
    log_processor = color_config.getProcessor(decoded["decoded_space"], source_space).getDefaultCPUProcessor() if decoded["decoded_space"] != source_space else None
    output = directory / "render"
    output.mkdir()
    for target in ("sdr", "hdr"):
        for kind in ("reference16", "runtime8"):
            (output / f"{target}-{kind}").mkdir()
    width, height = decoded["width"], decoded["height"]
    result = {"camera": camera, "width": width, "height": height, "fps": decoded["fps"],
        "scope": ("首帧验证" if config["scope"] == "first" else "完整素材") + f'：实际{decoded["frames"]}/{decoded["source_frames"]}帧；单次GUI任务，不是性能门禁',
        "source_frames": decoded["source_frames"], "policy_sha256": pipeline.sha(policy_path),
        "raw_sha256": pipeline.sha(config["raw"]), "script_sha256": pipeline.sha(__file__),
        "graph_script_sha256": pipeline.sha(pipeline.__file__), "bridge_sha256": pipeline.sha(ROOT / "experiments/camera-raw-workflow/runtime_bridge.py"),
        "model_manifest_sha256": pipeline.sha(model_dir / "manifest.json"), "decoder": decoded["decoder"],
        "ocio": ocio.__version__, "numpy": np.__version__, "tile_pixels": TILE, "reference_threads": 4, "frames": [], "runtime": {}}
    if result["fps"] == "未知":
        result["fps"] = 24
        result["fps_scope"] = "源帧率未知；24fps仅作为单帧导出时间基，不是源元数据"
    runtime = {}
    with ThreadPoolExecutor(max_workers=4) as pool:
        pipeline.REFERENCE_POOL, pipeline.REFERENCE_THREADS = pool, 4
        try:
            for target in ("sdr", "hdr"):
                runtime[target] = Runtime(ROOT / policy["runtime"]["library"], [models[name]["slut"] for name in names + [target]], 4)
                result["runtime"][target] = {"info": runtime[target].info, "prepare_seconds": runtime[target].prepare_seconds}
            if len(decoded["paths"]) != decoded["frames"]:
                raise ValueError("解码文件数量不符")
            for index, path_text in enumerate(decoded["paths"]):
                path = Path(path_text)
                start = time.perf_counter()
                if camera == "arri":
                    with OpenEXR.File(str(path)) as exr:
                        source = exr.channels()["RGB"].pixels.copy().reshape(-1, 3)
                else:
                    if path.stat().st_size != width * height * 12:
                        raise ValueError("解码float帧长度不符")
                    source = np.memmap(path, dtype="<f4", mode="r", shape=(width * height, 3))
                row = {"index": index, "stages": {}, "branches": {}, "tiles": 0, "decoded_sha256": pipeline.sha(path)}
                handles, digests = {}, {}
                for target in ("sdr", "hdr"):
                    row["branches"][target] = {"runtime_apply_seconds": 0., "scalar_check_seconds": 0., "scalar_equal": True,
                        "runtime_error": {}, "float33_error": {}, "runtime_vs_export16_error": {}, "reference_above_one": 0, "reference_below_zero": 0}
                    for kind in ("reference16", "runtime8"):
                        key = target + "-" + kind
                        handles[key] = (output / key / f"frame-{index:06d}.rgb").open("xb")
                        digests[key] = hashlib.sha256()
                try:
                    for begin in range(0, width * height, TILE):
                        precise = source[begin:begin + TILE].copy()
                        if not np.isfinite(precise).all():
                            raise ValueError("解码值含NaN/Inf")
                        if log_processor:
                            pipeline.apply(log_processor, precise)
                        payload = np.floor(np.clip(precise, 0, 1) * 255 + .5).astype(np.uint8).tobytes()
                        sampled = precise.copy()
                        for name in names:
                            pipeline.apply(processors[name], precise)
                            pipeline.apply(lut_processors[name], sampled)
                        for target in ("sdr", "hdr"):
                            reference, floating = precise.copy(), sampled.copy()
                            pipeline.apply(processors[target], reference)
                            pipeline.apply(lut_processors[target], floating)
                            native, seconds = runtime[target].apply(payload)
                            branch = row["branches"][target]
                            branch["runtime_apply_seconds"] += seconds
                            branch["scalar_check_seconds"] += runtime[target].check_scalar(payload, native)
                            actual = np.frombuffer(native, dtype=np.uint8).reshape(-1, 3).astype(np.float32) / 255
                            rgb16 = np.floor(np.clip(reference, 0, 1) * 65535 + .5).astype("<u2")
                            for name, expected in (("runtime_error", reference), ("float33_error", reference), ("runtime_vs_export16_error", rgb16.astype(np.float32) / 65535)):
                                add_metric(branch[name], pipeline.error_metrics(floating if name == "float33_error" else actual, expected))
                            branch["reference_above_one"] += int(np.count_nonzero(reference > 1))
                            branch["reference_below_zero"] += int(np.count_nonzero(reference < 0))
                            for kind, data in (("reference16", rgb16.tobytes()), ("runtime8", native)):
                                key = target + "-" + kind
                                handles[key].write(data)
                                digests[key].update(data)
                        row["tiles"] += 1
                        emit("四级 LUT 与全像素核对", 25 + 70 * (index + min(begin + TILE, width * height) / (width * height)) / decoded["frames"], message=f'第{index + 1}/{decoded["frames"]}帧 · CPU 4线程')
                    for target in ("sdr", "hdr"):
                        for metric in ("runtime_error", "float33_error", "runtime_vs_export16_error"):
                            finish_metric(row["branches"][target][metric])
                        row["branches"][target]["runtime_sha256"] = digests[target + "-runtime8"].hexdigest()
                        row["branches"][target]["reference16_sha256"] = digests[target + "-reference16"].hexdigest()
                finally:
                    for handle in handles.values():
                        handle.close()
                del source
                row["wall_seconds_including_checks_and_io"] = time.perf_counter() - start
                result["frames"].append(row)
                pipeline.dump(output / "progress.json", result)
            result["complete"] = True
            pipeline.dump(output / "results.json", result)
        finally:
            for handle in runtime.values():
                handle.close()


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--job", type=Path, required=True)
    args = parser.parse_args()
    config = json.loads(args.job.read_text(encoding="utf-8"))
    directory = Path(config["output"])
    if ocio.__version__ != "2.6.0":
        raise ValueError("需要本次已验OCIO2.6.0")
    emit("RAW 解码", 8, message="官方CPU工具，完整分辨率")
    decoded = decode(config, directory)
    pipeline.dump(directory / "decoded.json", decoded)
    check_space(directory, decoded["width"], decoded["height"], decoded["frames"], 18)
    emit("Log 与模型核验", 23, message=decoded["decoder"])
    render(config, decoded, directory)
    emit("完成", 100, message="所有处理像素的原生/标量结果逐字节一致；浮点参考误差已另列")


if __name__ == "__main__":
    main()
