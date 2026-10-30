"""真实摄影机四级工作流：冻结模型、逐帧参考、RGB8运行时及误差台账。"""
from __future__ import annotations

import argparse
import hashlib
import json
import math
import platform
import struct
import sys
import time
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
REFERENCE_POOL = None
REFERENCE_THREADS = 1


def sha(path):
    with Path(path).open("rb") as stream:
        return hashlib.file_digest(stream, "sha256").hexdigest()


def dump(path, data):
    Path(path).write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")


def graph(policy):
    config = ocio.Config.CreateFromBuiltinConfig(policy["reference"]["config"])
    transforms = {}
    for name, row in policy["cameras"].items():
        transforms[f"{name}-input"] = ocio.ColorSpaceTransform(src=row["input_space"], dst="ACEScct")
    gain = [math.pow(2, 0.25) * value for value in (1.02, 1, 0.98)]
    transforms["balance"] = ocio.GroupTransform([
        ocio.ColorSpaceTransform(src="ACEScct", dst="ACEScg"),
        ocio.MatrixTransform(matrix=[gain[0], 0, 0, 0, 0, gain[1], 0, 0, 0, 0, gain[2], 0, 0, 0, 0, 1]),
        ocio.ColorSpaceTransform(src="ACEScg", dst="ACEScct"),
    ])
    pivot = 0.4135884024924423
    saturation = ocio.CDLTransform(sat=0.92)
    saturation.setStyle(ocio.CDL_NO_CLAMP)
    transforms["look"] = ocio.GroupTransform([
        ocio.MatrixTransform(matrix=[1.08, 0, 0, 0, 0, 1.08, 0, 0, 0, 0, 1.08, 0, 0, 0, 0, 1],
                             offset=[-0.08 * pivot] * 3 + [0]),
        saturation,
    ])
    for target in ("sdr", "hdr"):
        display, view = policy["reference"][f"stage4_{target}"]
        transforms[target] = ocio.DisplayViewTransform(src="ACEScct", display=display, view=view)
    processors = {name: config.getProcessor(value).getDefaultCPUProcessor() for name, value in transforms.items()}
    return config, transforms, processors


def save_slut(path, nodes):
    # 与python/lutlab/io.py的v1格式相同：R/G/B索引，B最快，权重Q16。
    m = nodes.shape[0]
    grid = np.tile(np.linspace(0, 255, m, dtype=np.float64), (3, 1))
    axis = np.arange(256, dtype=np.float64)
    idx = np.empty((3, 256), dtype=np.uint8)
    frac = np.empty((3, 256), dtype="<u4")
    for a in range(3):
        i = np.clip(np.searchsorted(grid[a], axis, side="right") - 1, 0, m - 2)
        idx[a] = i
        frac[a] = np.floor((axis - grid[a, i]) / (grid[a, i + 1] - grid[a, i]) * 65536 + 0.5).astype("<u4")
    payload = b"SLUT" + struct.pack("<III", 1, m, 0) + grid.astype("<f4").tobytes()
    payload += idx.tobytes() + frac.tobytes() + np.ascontiguousarray(nodes).tobytes()
    Path(path).write_bytes(payload)


def bake(args, policy):
    args.output.mkdir(parents=True, exist_ok=False)
    config, transforms, processors = graph(policy)
    config_path = args.output / "config.ocio"
    config_path.write_text(config.serialize(), encoding="utf-8")
    m = policy["reference"]["lut_cube_size"]
    values = np.linspace(0, 1, m, dtype=np.float32)
    lattice = np.stack(np.meshgrid(values, values, values, indexing="ij"), axis=-1)
    result = {"policy_sha256": sha(args.policy), "script_sha256": sha(__file__), "ocio": ocio.__version__,
              "config_sha256": sha(config_path), "models": {}, "baking": "独立33³直接采样，未做LS精化或完整色域拟合验收"}
    for name, processor in processors.items():
        nodes = lattice.copy()
        processor.applyRGB(nodes.reshape(-1, 3))
        if not np.isfinite(nodes).all():
            raise ValueError("冻结节点包含非有限数")
        cube = args.output / (name + ".cube")
        with cube.open("w", encoding="utf-8", newline="\n") as stream:
            stream.write(f'TITLE "{name}"\nLUT_3D_SIZE {m}\nDOMAIN_MIN 0 0 0\nDOMAIN_MAX 1 1 1\n')
            np.savetxt(stream, nodes.transpose(2, 1, 0, 3).reshape(-1, 3), fmt="%.9g")
        sparse = args.output / (name + ".slut")
        save_slut(sparse, np.floor(np.clip(nodes, 0, 1) * 255 + 0.5).astype(np.uint8))
        restored = config.getProcessor(ocio.FileTransform(src=str(cube), interpolation=ocio.INTERP_TETRAHEDRAL)).getDefaultCPUProcessor()
        check_nodes = lattice.copy()
        restored.applyRGB(check_nodes.reshape(-1, 3))
        error = float(np.max(np.abs(check_nodes - nodes)))
        if error > 2e-6:
            raise ValueError(f"CUBE轴序或节点往返失败：{name}:{error}")
        result["models"][name] = {"cube": str(cube.resolve()), "cube_sha256": sha(cube),
                                  "slut": str(sparse.resolve()), "slut_sha256": sha(sparse),
                                  "bytes": sparse.stat().st_size, "node_roundtrip_max": error,
                                  "node_below_zero": int(np.count_nonzero(nodes < 0)),
                                  "node_above_one": int(np.count_nonzero(nodes > 1))}
    dump(args.output / "manifest.json", result)
    print(json.dumps({"models": len(result["models"]), "manifest": str(args.output / "manifest.json")}), flush=True)


def error_metrics(actual, expected):
    # 全像素统计分块进行，不把抽样最大值或近似分位数写成精确结果。
    actual = actual.reshape(-1, 3)
    expected = expected.reshape(-1, 3)
    absolute = square = 0.0
    maximum = 0.0
    for start in range(0, len(actual), 262144):
        delta = actual[start:start + 262144].astype(np.float64) - expected[start:start + 262144]
        absolute += float(np.abs(delta).sum())
        square += float(np.square(delta).sum())
        maximum = max(maximum, float(np.max(np.abs(delta))))
    count = actual.size
    return {"channels": count, "mae_normalized": absolute / count,
            "rmse_normalized": math.sqrt(square / count), "max_normalized": maximum,
            "mae_8bit_codes": absolute / count * 255, "max_8bit_codes": maximum * 255,
            "sum_absolute": absolute, "sum_square": square}


def apply(processor, array):
    start = time.perf_counter()
    flat = array.reshape(-1, 3)
    if REFERENCE_POOL is not None and len(flat) >= 262144:
        # 每片起点对齐16像素；同一不可变CPUProcessor作用于不重叠的连续缓冲区。
        step = (len(flat) // REFERENCE_THREADS // 16) * 16
        futures = [REFERENCE_POOL.submit(processor.applyRGB, flat[i * step: (i + 1) * step if i + 1 < REFERENCE_THREADS else len(flat)])
                   for i in range(REFERENCE_THREADS)]
        for future in futures:
            future.result()
    else:
        processor.applyRGB(flat)
    if not np.isfinite(array).all():
        raise ValueError("参考处理中出现非有限数")
    return time.perf_counter() - start


def run(args, policy):
    from runtime_bridge import Runtime
    print(json.dumps({"stage": "start", "camera": args.camera, "reference_threads": REFERENCE_THREADS}), flush=True)
    manifest = json.loads((args.models / "manifest.json").read_text())
    if manifest["policy_sha256"] != sha(args.policy):
        raise ValueError("策略与模型身份不一致")
    args.output.mkdir(parents=True, exist_ok=False)
    camera = policy["cameras"][args.camera]
    config, transforms, processors = graph(policy)
    if hashlib.sha256(config.serialize().encode()).hexdigest() != manifest["config_sha256"]:
        raise ValueError("实际参考配置与烘焙配置不一致")
    for row in manifest["models"].values():
        if sha(row["cube"]) != row["cube_sha256"] or sha(row["slut"]) != row["slut_sha256"]:
            raise ValueError("模型哈希不符")
    names = [f"{args.camera}-input", "balance", "look"]
    lut_processors = {name: config.getProcessor(ocio.FileTransform(src=manifest["models"][name]["cube"],
                      interpolation=ocio.INTERP_TETRAHEDRAL)).getDefaultCPUProcessor() for name in names + ["sdr", "hdr"]}
    raw = ROOT / camera["raw"]
    if camera.get("raw_sha256") and sha(raw) != camera["raw_sha256"]:
        raise ValueError("RAW素材哈希不符")
    decoded = ROOT / camera["decoded"]
    if args.camera == "arri":
        if sha(decoded) != camera["decoded_sha256"]:
            raise ValueError("ARRI解码EXR哈希不符")
        inputs = [decoded]
        log_processor = config.getProcessor(camera["decoded_space"], camera["input_space"]).getDefaultCPUProcessor()
    else:
        inputs = sorted(decoded.glob("frame-*.rgbf32"))
        log_processor = None
    if len(inputs) != camera["frames"]:
        raise ValueError("实际帧数不符，不截取样片冒充整段")
    result = {"camera": args.camera, "policy_sha256": sha(args.policy), "script_sha256": sha(__file__),
              "bridge_sha256": sha(Path(__file__).with_name("runtime_bridge.py")), "model_manifest_sha256": sha(args.models / "manifest.json"),
              "python": sys.version, "platform": platform.platform(), "numpy": np.__version__, "ocio": ocio.__version__,
              "raw_sha256": sha(raw), "width": camera["width"], "height": camera["height"], "fps": camera["fps"],
              "scope": "整帧全部像素，单次回放诊断；非旧照片性能门禁或完整RGB色域证明", "frames": [], "runtime": {}}
    result["reference_threads"] = REFERENCE_THREADS
    if REFERENCE_POOL is not None:
        probe = np.random.default_rng(20261023).uniform(-0.05, 1.05, (262144, 3)).astype(np.float32)
        checks = []
        for name, processor in processors.items():
            sequential, parallel = probe.copy(), probe.copy()
            processor.applyRGB(sequential)
            apply(processor, parallel)
            if sequential.tobytes() != parallel.tobytes():
                raise AssertionError("参考分片与单调用float32字节不一致：" + name)
            checks.append(name)
            print(json.dumps({"stage": "reference_thread_preflight", "transform": name, "float32_byte_equal": True}), flush=True)
        result["reference_thread_preflight"] = {"pixels_per_transform": 262144, "float32_byte_equal": checks}
    runtimes = {}
    try:
        for target in ("sdr", "hdr"):
            models = [Path(manifest["models"][name]["slut"]) for name in names + [target]]
            runtimes[target] = Runtime(ROOT / policy["runtime"]["library"], models, policy["runtime"]["threads"])
            result["runtime"][target] = {"info": runtimes[target].info, "prepare_seconds": runtimes[target].prepare_seconds}
            for kind in ("reference16", "runtime8"):
                (args.output / f"{target}-{kind}").mkdir()
        for index, path in enumerate(inputs):
            print(json.dumps({"stage": "frame_start", "index": index}), flush=True)
            wall = time.perf_counter()
            if args.camera == "arri":
                source = OpenEXR.File(str(path)).channels()["RGB"].pixels.copy()
            else:
                source = np.fromfile(path, dtype="<f4").reshape(camera["height"], camera["width"], 3)
            if source.shape != (camera["height"], camera["width"], 3) or not np.isfinite(source).all():
                raise ValueError("解码帧形状或非有限数失败")
            row = {"index": index, "decoded_sha256": sha(path), "stages": {}, "branches": {}}
            row["log_encoding_seconds"] = apply(log_processor, source) if log_processor else 0.0
            payload = np.floor(np.clip(source, 0, 1) * 255 + 0.5).astype(np.uint8).tobytes()
            row["input_rgb8_sha256"] = hashlib.sha256(payload).hexdigest()
            precise, lut_float = source, source.copy()
            for name in names:
                seconds = apply(processors[name], precise)
                lut_seconds = apply(lut_processors[name], lut_float)
                row["stages"][name] = {"reference_seconds": seconds, "float_lut_seconds": lut_seconds,
                    "minimum": float(precise.min()), "maximum": float(precise.max()),
                    "below_zero": int(np.count_nonzero(precise < 0)), "above_one": int(np.count_nonzero(precise > 1))}
            for target in ("sdr", "hdr"):
                reference, sampled = precise.copy(), lut_float.copy()
                seconds = apply(processors[target], reference)
                lut_seconds = apply(lut_processors[target], sampled)
                native, native_seconds = runtimes[target].apply(payload)
                scalar_seconds = runtimes[target].check_scalar(payload, native)
                native_array = np.frombuffer(native, dtype=np.uint8).reshape(source.shape)
                metrics = error_metrics(native_array.astype(np.float32) / 255, reference)
                lut_metrics = error_metrics(sampled, reference)
                branch = {"reference_stage4_seconds": seconds, "float_lut_stage4_seconds": lut_seconds,
                          "runtime_apply_seconds": native_seconds, "scalar_check_seconds": scalar_seconds,
                          "scalar_equal": True, "runtime_sha256": hashlib.sha256(native).hexdigest(),
                          "runtime_error": metrics, "float33_error": lut_metrics,
                          "reference_below_zero": int(np.count_nonzero(reference < 0)),
                          "reference_above_one": int(np.count_nonzero(reference > 1))}
                rgb16 = np.floor(np.clip(reference, 0, 1) * 65535 + 0.5).astype("<u2")
                branch["runtime_vs_export16_error"] = error_metrics(native_array.astype(np.float32) / 255,
                                                                    rgb16.astype(np.float32) / 65535)
                branch["reference16_sha256"] = hashlib.sha256(rgb16).hexdigest()
                rgb16.tofile(args.output / f"{target}-reference16" / f"frame-{index:06d}.rgb")
                (args.output / f"{target}-runtime8" / f"frame-{index:06d}.rgb").write_bytes(native)
                if index == 0:
                    OpenEXR.File({"compression": OpenEXR.ZIP_COMPRESSION, "type": OpenEXR.scanlineimage},
                                 {"RGB": reference}).write(str(args.output / f"{target}-reference-frame0.exr"))
                row["branches"][target] = branch
            row["wall_seconds_including_checks_and_io"] = time.perf_counter() - wall
            result["frames"].append(row)
            dump(args.output / "progress.json", result)
            print(json.dumps({"camera": args.camera, "frame": index + 1, "total": len(inputs),
                              "seconds": row["wall_seconds_including_checks_and_io"]}), flush=True)
        result["complete"] = True
        dump(args.output / "results.json", result)
    finally:
        for runtime in runtimes.values():
            runtime.close()


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("action", choices=["bake", "run"])
    parser.add_argument("--site", type=Path, default=ROOT / "artifacts/camera-raw-workflow-v1/linux-site")
    parser.add_argument("--policy", type=Path, default=ROOT / "experiments/camera-raw-workflow-v1.json")
    parser.add_argument("--models", type=Path)
    parser.add_argument("--camera", choices=["arri", "blackmagic"])
    parser.add_argument("--reference-threads", type=int, choices=[1, 4], default=1)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    sys.path.insert(0, str(args.site.resolve()))
    global np, ocio, OpenEXR
    import numpy as np
    import PyOpenColorIO as ocio
    import OpenEXR
    policy = json.loads(args.policy.read_text(encoding="utf-8"))
    if ocio.__version__ != policy["reference"]["opencolorio"]:
        raise ValueError("参考OCIO版本不符")
    global REFERENCE_POOL, REFERENCE_THREADS
    REFERENCE_THREADS = args.reference_threads
    with ThreadPoolExecutor(max_workers=REFERENCE_THREADS) as pool:
        REFERENCE_POOL = pool if REFERENCE_THREADS > 1 else None
        (bake if args.action == "bake" else run)(args, policy)


if __name__ == "__main__":
    main()
