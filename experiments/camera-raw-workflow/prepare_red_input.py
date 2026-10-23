"""核验官方 REDline TIFF16 输出，并逐块生成紧密 RGBF32 Log 输入。"""
from __future__ import annotations

import hashlib
import json
from pathlib import Path
import platform
import re
import shlex
import sys
import time

ROOT = Path(__file__).resolve().parents[2]
BASE = ROOT / "artifacts/camera-raw-workflow-v1"
sys.path.insert(0, str(BASE / "linux-site"))
import numpy as np
import tifffile


def sha(path):
    result = hashlib.sha256()
    with Path(path).open("rb") as stream:
        for block in iter(lambda: stream.read(8 * 1024 * 1024), b""):
            result.update(block)
    return result.hexdigest()


def dump(path, value):
    Path(path).write_text(json.dumps(value, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def relative(path):
    return Path(path).relative_to(ROOT).as_posix()


def main():
    source = BASE / "decoded/red-tiff-probe/test.tif.000000.tif"
    log = BASE / "decoded/red-tiff-probe/redline.log"
    output = BASE / "decoded/red-log3g10/frame-000000.rgbf32"
    if output.exists():
        raise FileExistsError("保留既有像素；请勿覆盖输入")
    text = log.read_text(encoding="utf-8")
    for required in ("Output Dimensions: 6144x3160", "Output Transform Settings: ColorSpace: REDWideGamutRGB",
                     "Output Transform Settings: Gamma Curve: Log3G10", "Export Job frame complete. 0",
                     "Batch Job Complete: test.tif", "Gpu Decoding: Disabled"):
        if required not in text:
            raise ValueError("成功日志契约不符：" + required)
    line = next(line for line in text.splitlines() if '"--i"' in line and '"--format"' in line)
    command = shlex.split(line[line.index('"'):])
    if command[command.index("--gpuPlatform") + 1] != "0" or command[command.index("--decodeThreads") + 1] != "4":
        raise ValueError("未采用要求的 CPU/4线程路径")
    metadata = dict(line.split(":\t", 1) for line in (BASE / "redline-metadata-normal.txt").read_text().splitlines() if ":\t" in line)
    if [metadata[k] for k in ("Frame Width", "Frame Height", "Total Frames", "Camera Model", "Sensor Name")] != ["6144", "3160", "1", "EPIC-X", "DRAGON 6K S35"]:
        raise ValueError("官方 SDK 相机/尺寸/帧数身份不符")
    with tifffile.TiffFile(source) as handle:
        if len(handle.pages) != 1:
            raise ValueError("TIFF 不是唯一帧")
        page = handle.pages[0]
        tags = {tag.name: list(tag.value) if isinstance(tag.value, tuple) else int(tag.value)
                for tag in page.tags.values()}
        if page.shape != (3160, 6144, 3) or page.dtype != np.dtype("uint16"):
            raise ValueError("TIFF 的实际维度或位深不符")
        expected = {"BitsPerSample": [16, 16, 16], "Compression": 1, "PhotometricInterpretation": 2,
                    "Orientation": 1, "SamplesPerPixel": 3, "PlanarConfiguration": 1,
                    "StripOffsets": [8], "StripByteCounts": [116490240]}
        if any(tags[k] != v for k, v in expected.items()):
            raise ValueError("TIFF 栅格布局或位深契约不符")
        byteorder = handle.byteorder
    mapped = tifffile.memmap(source, mode="r")
    start = time.perf_counter()
    pixel_hash = hashlib.sha256()
    minimum, maximum = 65535, 0
    pixels = channels = 0
    with output.open("xb") as stream:
        for row in range(0, 3160, 32):
            values = np.ascontiguousarray(mapped[row:row + 32])
            floating = values.astype("<f4") / np.float32(65535)
            restored = np.floor(floating * np.float32(65535) + np.float32(0.5)).astype(np.uint16)
            if not np.isfinite(floating).all() or not np.array_equal(restored, values):
                raise ValueError("RGBF32 归一化损失了 TIFF16 代码值")
            payload = floating.tobytes(order="C")
            stream.write(payload)
            pixel_hash.update(payload)
            minimum, maximum = min(minimum, int(values.min())), max(maximum, int(values.max()))
            channels += values.size
            pixels += values.shape[0] * values.shape[1]
    del mapped
    if output.stat().st_size != 6144 * 3160 * 12 or sha(output) != pixel_hash.hexdigest():
        raise ValueError("RGBF32 落盘长度或哈希不符")
    descriptor = {"raw": relative(BASE / "raw/red/F099_C001_0317IH.R3D"),
                  "raw_sha256": sha(BASE / "raw/red/F099_C001_0317IH.R3D"),
                  "decoded": relative(output.parent), "decoded_sha256": sha(output),
                  "decoded_space": "Log3G10 REDWideGamutRGB", "input_space": "Log3G10 REDWideGamutRGB",
                  "frames": 1, "width": 6144, "height": 3160, "fps": metadata["FPS"],
                  "fps_scope": "官方 SDK/REDline 元数据原文为23.976；仅打印三位小数，未声称已核实24000/1001精确分数",
                  "decoder": "官方REDline65.0.22 / R3DSDK9.1.1，WSL2 CPU4线程，全分辨率TIFF16/RWG/Log3G10；逐块归一化RGBF32，全部原始16bit代码值可无损往返",
                  "camera_model": metadata["Camera Model"], "sensor_name": metadata["Sensor Name"],
                  "tiff": relative(source), "tiff_sha256": sha(source),
                  "precision_scope": "原始解码输出为每通道无符号16bit Log，归一化到float32；不宣称原生float32解码或未量化的scene-linear精度"}
    dump(BASE / "red-camera.json", descriptor)
    results = {"purpose": "数据完整性、格式契约与16bit代码值往返；不是拟合精度、完整RGB色域或LUT速度测试",
               "platform": platform.platform(), "python": sys.version, "numpy": np.__version__, "tifffile": tifffile.__version__,
               "script_sha256": sha(__file__), "camera": descriptor,
               "tiff_byteorder": byteorder, "tiff_tags": tags, "command": command,
               "cwd": relative(BASE / "tools/redline-linux/libs"), "LD_LIBRARY_PATH": ".",
               "log": relative(log), "log_sha256": sha(log),
               "metadata_normal_sha256": sha(BASE / "redline-metadata-normal.txt"),
               "metadata_csv_sha256": sha(BASE / "redline-metadata-v2.txt"),
               "pixels": pixels, "channels": channels, "tiff16_minimum": minimum, "tiff16_maximum": maximum,
               "normalized_minimum": minimum / 65535, "normalized_maximum": maximum / 65535,
               "all_uint16_codes_roundtrip_equal": True, "rgbf32_nonfinite": 0,
               "rgbf32_bytes": output.stat().st_size, "rgbf32_layout": "little-endian RGBRGB float32，行优先，无填充",
               "convert_seconds_including_io_and_checks": time.perf_counter() - start,
               "render_time_scope": "TIFF成功命令未由专门端到端计时器包裹；不报告推断的解码wall性能",
               "native_batch_duration_seconds_from_log": float(re.search(r"Duration: 00:00:([0-9.]+)", text).group(1)),
               "limitations": ["公开FFmpeg R3D样例，只有一帧，不代表整段连续播放性能",
                               "没有获得素材/衍生像素的再发布许可，仅保存在本地artifact",
                               "EXR首次命令returncode=0但没有像素，失败证据保留；未用其替代成功TIFF结果",
                               "本成功命令采用元数据中的FLUT色彩版本2，并显式输出RWG/Log3G10；未称为IPP2解码",
                               "SDK元数据仅打印FPS=23.976，未补造更精确分数"]}
    dump(BASE / "red-input-verification.json", results)
    print(json.dumps({"descriptor": str(BASE / "red-camera.json"), "input": str(output),
                      "sha256": descriptor["decoded_sha256"], "channels_roundtrip_equal": channels}), flush=True)


if __name__ == "__main__":
    main()
