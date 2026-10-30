"""低内存整段回放；像素变换与pipeline.py相同，四路结果逐块落盘。"""
from __future__ import annotations

import argparse
from concurrent.futures import ThreadPoolExecutor
import hashlib
import json
import math
from pathlib import Path
import platform
import sys
import time

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "artifacts/camera-raw-workflow-v1/linux-site"))
import numpy as np
import PyOpenColorIO as ocio
import pipeline
from runtime_bridge import Runtime

pipeline.np, pipeline.ocio = np, ocio
TILE = 262144


def add_metric(total, current):
    for key in ("channels", "sum_absolute", "sum_square"):
        total[key] = total.get(key, 0) + current[key]
    total["max_normalized"] = max(total.get("max_normalized", 0), current["max_normalized"])


def finish_metric(total):
    total["mae_normalized"] = total["sum_absolute"] / total["channels"]
    total["rmse_normalized"] = math.sqrt(total["sum_square"] / total["channels"])
    total["mae_8bit_codes"] = total["mae_normalized"] * 255
    total["max_8bit_codes"] = total["max_normalized"] * 255


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--models", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--resume", action="store_true", help="核验完整检查点后续跑，保留中断片段")
    parser.add_argument("--camera", choices=["blackmagic", "red"], default="blackmagic")
    parser.add_argument("--camera-manifest", type=Path)
    args = parser.parse_args()
    policy_path = ROOT / "experiments/camera-raw-workflow-v1.json"
    policy = json.loads(policy_path.read_text(encoding="utf-8"))
    camera = dict(policy["cameras"][args.camera])
    if args.camera_manifest:
        descriptor = json.loads(args.camera_manifest.read_text(encoding="utf-8"))
        if descriptor["input_space"] != camera["input_space"]:
            raise ValueError("摄影机Log色彩标记与冻结变换不符")
        for key in ("raw", "raw_sha256", "decoded", "decoded_space", "frames", "width", "height", "fps", "decoder"):
            if key in descriptor:
                camera[key] = descriptor[key]
    manifest = json.loads((args.models / "manifest.json").read_text())
    if manifest["policy_sha256"] != pipeline.sha(policy_path):
        raise ValueError("策略与模型身份不符")
    config, _, processors = pipeline.graph(policy)
    if hashlib.sha256(config.serialize().encode()).hexdigest() != manifest["config_sha256"]:
        raise ValueError("参考配置身份不符")
    for model in manifest["models"].values():
        for key in ("slut", "cube"):
            if pipeline.sha(model[key]) != model[key + "_sha256"]:
                raise ValueError("模型身份不符")
    names = [f"{args.camera}-input", "balance", "look"]
    log_processor = (config.getProcessor(camera["decoded_space"], camera["input_space"]).getDefaultCPUProcessor()
                     if camera["decoded_space"] != camera["input_space"] else None)
    lut_processors = {name: config.getProcessor(ocio.FileTransform(src=manifest["models"][name]["cube"],
                        interpolation=ocio.INTERP_TETRAHEDRAL)).getDefaultCPUProcessor() for name in names + ["sdr", "hdr"]}
    inputs = sorted((ROOT / camera["decoded"]).glob("frame-*.rgbf32"))
    expected_bytes = camera["width"] * camera["height"] * 12
    if len(inputs) != camera["frames"] or any(p.stat().st_size != expected_bytes for p in inputs):
        raise ValueError("完整帧数或单帧字节数不符")
    args.output.mkdir(parents=True, exist_ok=args.resume)
    result = {"camera": args.camera, "policy_sha256": pipeline.sha(policy_path), "script_sha256": pipeline.sha(__file__),
              "graph_script_sha256": pipeline.sha(pipeline.__file__), "bridge_sha256": pipeline.sha(Path(__file__).with_name("runtime_bridge.py")),
              "model_manifest_sha256": pipeline.sha(args.models / "manifest.json"), "raw_sha256": pipeline.sha(ROOT / camera["raw"]),
              "width": camera["width"], "height": camera["height"], "fps": camera["fps"], "python": sys.version,
              "platform": platform.platform(), "numpy": np.__version__, "ocio": ocio.__version__,
              "tile_pixels": TILE, "reference_threads": 4,
              "scope": f"全部{camera['frames']}帧全部像素，分块调用；单次诊断，不作旧照片A/A或ABBA性能排名", "runtime": {}, "frames": []}
    if camera.get("raw_sha256") and camera["raw_sha256"] != result["raw_sha256"]:
        raise ValueError("摄影机RAW来源哈希不符")
    if args.camera_manifest:
        result["camera_manifest_sha256"] = pipeline.sha(args.camera_manifest)
    resume_count = 0
    if args.resume:
        previous_path = args.output / "progress.json"
        previous = json.loads(previous_path.read_text())
        for key in ("camera", "policy_sha256", "graph_script_sha256", "bridge_sha256", "model_manifest_sha256",
                    "raw_sha256", "width", "height", "fps", "tile_pixels", "reference_threads"):
            if previous[key] != result[key]:
                raise ValueError("续跑身份不符：" + key)
        resume_count = len(previous["frames"])
        if not 0 < resume_count < len(inputs) or [r["index"] for r in previous["frames"]] != list(range(resume_count)):
            raise ValueError("检查点不是连续的未完成前缀")
        for row in previous["frames"]:
            if pipeline.sha(inputs[row["index"]]) != row["decoded_sha256"]:
                raise ValueError("已完成帧的解码输入改变")
            for target in ("sdr", "hdr"):
                for kind, digest_key, pixel_bytes in (("reference16", "reference16_sha256", 6), ("runtime8", "runtime_sha256", 3)):
                    path = args.output / f"{target}-{kind}" / f'frame-{row["index"]:06d}.rgb'
                    if path.stat().st_size != camera["width"] * camera["height"] * pixel_bytes or pipeline.sha(path) != row["branches"][target][digest_key]:
                        raise ValueError("已完成帧输出改变")
            print(json.dumps({"stage": "resume_verified", "frame": row["index"] + 1}), flush=True)
        history = args.output / f"resume-{len(previous.get('resumptions', [])) + 1:03d}"
        history.mkdir()
        (history / "original-progress.json").write_bytes(previous_path.read_bytes())
        moved = []
        for target in ("sdr", "hdr"):
            for kind in ("reference16", "runtime8"):
                directory = args.output / f"{target}-{kind}"
                for path in directory.glob("frame-*.rgb"):
                    if int(path.stem.split("-")[-1]) >= resume_count:
                        destination = history / directory.name / path.name
                        destination.parent.mkdir(exist_ok=True)
                        if not path.resolve().is_relative_to(args.output.resolve()) or not destination.resolve().is_relative_to(args.output.resolve()):
                            raise ValueError("中断帧归档路径越界")
                        path.rename(destination)
                        moved.append(str(destination))
        previous.setdefault("resumptions", []).append({"completed_prefix_frames": resume_count,
            "resume_script_sha256": result["script_sha256"], "original_progress_sha256": pipeline.sha(history / "original-progress.json"),
            "preserved_incomplete_files": moved, "reason": "用户继续指令后的恢复；未重复已完成像素"})
        result = previous
    runtimes = {}
    with ThreadPoolExecutor(max_workers=4) as pool:
        pipeline.REFERENCE_POOL, pipeline.REFERENCE_THREADS = pool, 4
        try:
            probe = np.random.default_rng(20261023).uniform(-0.05, 1.05, (TILE, 3)).astype(np.float32)
            for name, processor in processors.items():
                sequential, parallel = probe.copy(), probe.copy()
                processor.applyRGB(sequential); pipeline.apply(processor, parallel)
                if sequential.tobytes() != parallel.tobytes():
                    raise AssertionError("参考分片float32不一致：" + name)
            result["reference_thread_preflight"] = {"pixels_per_transform": TILE, "float32_byte_equal": list(processors)}
            del probe, sequential, parallel
            for target in ("sdr", "hdr"):
                paths = [Path(manifest["models"][name]["slut"]) for name in names + [target]]
                runtimes[target] = Runtime(ROOT / policy["runtime"]["library"], paths, 4)
                runtime_info = {"info": runtimes[target].info, "prepare_seconds": runtimes[target].prepare_seconds}
                if args.resume:
                    result["resumptions"][-1].setdefault("runtime", {})[target] = runtime_info
                else:
                    result["runtime"][target] = runtime_info
                for kind in ("reference16", "runtime8"):
                    (args.output / f"{target}-{kind}").mkdir(exist_ok=args.resume)
            print(json.dumps({"stage": "preflight", "frames": len(inputs), "tile_pixels": TILE}), flush=True)
            for index, path in enumerate(inputs):
                if index < resume_count:
                    continue
                start = time.perf_counter()
                row = {"index": index, "stages": {}, "branches": {}, "tiles": 0, "log_encoding_seconds": 0.0}
                decoded_hash, input_hash = hashlib.sha256(), hashlib.sha256()
                streams, digests = {}, {}
                try:
                    for target in ("sdr", "hdr"):
                        row["branches"][target] = {"runtime_apply_seconds": 0.0, "scalar_check_seconds": 0.0,
                            "reference_stage4_seconds": 0.0, "float_lut_stage4_seconds": 0.0,
                            "runtime_error": {}, "float33_error": {}, "runtime_vs_export16_error": {},
                            "reference_below_zero": 0, "reference_above_one": 0, "scalar_equal": True}
                        for kind in ("reference16", "runtime8"):
                            key = f"{target}-{kind}"
                            streams[key] = (args.output / key / f"frame-{index:06d}.rgb").open("xb")
                            digests[key] = hashlib.sha256()
                    with path.open("rb") as source_file:
                        while raw := source_file.read(TILE * 12):
                            if len(raw) % 12:
                                raise ValueError("截断浮点RGB帧")
                            decoded_hash.update(raw)
                            source = np.frombuffer(raw, dtype="<f4").reshape(-1, 3).copy()
                            if not np.isfinite(source).all():
                                raise ValueError("解码帧包含非有限数")
                            if log_processor:
                                row["log_encoding_seconds"] += pipeline.apply(log_processor, source)
                            payload = np.floor(np.clip(source, 0, 1) * 255 + 0.5).astype(np.uint8).tobytes()
                            input_hash.update(payload)
                            precise, sampled = source, source.copy()
                            for name in names:
                                seconds = pipeline.apply(processors[name], precise)
                                lut_seconds = pipeline.apply(lut_processors[name], sampled)
                                stage = row["stages"].setdefault(name, {"reference_seconds": 0.0, "float_lut_seconds": 0.0,
                                    "minimum": float("inf"), "maximum": -float("inf"), "below_zero": 0, "above_one": 0})
                                stage["reference_seconds"] += seconds; stage["float_lut_seconds"] += lut_seconds
                                stage["minimum"] = min(stage["minimum"], float(precise.min()))
                                stage["maximum"] = max(stage["maximum"], float(precise.max()))
                                stage["below_zero"] += int(np.count_nonzero(precise < 0)); stage["above_one"] += int(np.count_nonzero(precise > 1))
                            for target in ("sdr", "hdr"):
                                reference, sampled_output = precise.copy(), sampled.copy()
                                branch = row["branches"][target]
                                branch["reference_stage4_seconds"] += pipeline.apply(processors[target], reference)
                                branch["float_lut_stage4_seconds"] += pipeline.apply(lut_processors[target], sampled_output)
                                native, seconds = runtimes[target].apply(payload)
                                branch["runtime_apply_seconds"] += seconds
                                branch["scalar_check_seconds"] += runtimes[target].check_scalar(payload, native)
                                native_float = np.frombuffer(native, dtype=np.uint8).reshape(-1, 3).astype(np.float32) / 255
                                add_metric(branch["runtime_error"], pipeline.error_metrics(native_float, reference))
                                add_metric(branch["float33_error"], pipeline.error_metrics(sampled_output, reference))
                                rgb16 = np.floor(np.clip(reference, 0, 1) * 65535 + 0.5).astype("<u2")
                                add_metric(branch["runtime_vs_export16_error"], pipeline.error_metrics(native_float, rgb16.astype(np.float32) / 65535))
                                branch["reference_below_zero"] += int(np.count_nonzero(reference < 0))
                                branch["reference_above_one"] += int(np.count_nonzero(reference > 1))
                                for kind, data in (("reference16", rgb16.tobytes()), ("runtime8", native)):
                                    key = f"{target}-{kind}"
                                    streams[key].write(data); digests[key].update(data)
                            row["tiles"] += 1
                    for target in ("sdr", "hdr"):
                        branch = row["branches"][target]
                        for metric in ("runtime_error", "float33_error", "runtime_vs_export16_error"):
                            finish_metric(branch[metric])
                        branch["runtime_sha256"] = digests[f"{target}-runtime8"].hexdigest()
                        branch["reference16_sha256"] = digests[f"{target}-reference16"].hexdigest()
                finally:
                    for stream in streams.values(): stream.close()
                row["decoded_sha256"], row["input_rgb8_sha256"] = decoded_hash.hexdigest(), input_hash.hexdigest()
                row["wall_seconds_including_checks_and_io"] = time.perf_counter() - start
                result["frames"].append(row)
                pipeline.dump(args.output / "progress.json", result)
                print(json.dumps({"frame": index + 1, "total": len(inputs), "tiles": row["tiles"],
                                  "seconds": row["wall_seconds_including_checks_and_io"]}), flush=True)
            result["complete"] = True
            pipeline.dump(args.output / "results.json", result)
        finally:
            for runtime in runtimes.values(): runtime.close()


if __name__ == "__main__":
    main()
