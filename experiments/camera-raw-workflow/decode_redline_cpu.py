"""以本地官方 REDline 的 CPU 路径解码公开 R3D，保留完整日志与文件身份。"""
from __future__ import annotations

import hashlib
import json
import os
from pathlib import Path
import platform
import resource
import subprocess
import sys
import time

ROOT = Path(__file__).resolve().parents[2]
BASE = ROOT / "artifacts/camera-raw-workflow-v1"


def sha(path):
    value = hashlib.sha256()
    with Path(path).open("rb") as stream:
        for block in iter(lambda: stream.read(8 * 1024 * 1024), b""):
            value.update(block)
    return value.hexdigest()


def main():
    if platform.system() != "Linux":
        raise RuntimeError("本脚本仅对当前解包的 Linux 版 REDline 定义路径")
    raw = BASE / "raw/red/F099_C001_0317IH.R3D"
    if sha(raw) != "084786df236b9a5313ad0bb4ec81f12869af1eb9600ccfe59735171793e69778":
        raise ValueError("R3D 输入身份不符")
    output = BASE / "decoded/red-log3g10"
    output.mkdir(parents=True, exist_ok=False)
    tool = BASE / "tools/redline-linux"
    binary = tool / "bin/REDline"
    command = [str(binary), "--i", str(raw), "--o", "red", "--outDir", str(output),
               "--format", "2", "--res", "1", "--start", "0", "--frameCount", "1",
               "--renum", "0", "--useMeta", "--colorSciVersion", "3", "--primaryDev",
               "--colorSpace", "25", "--gammaCurve", "34", "--exrACES", "0",
               "--exrSoftClamp", "0", "--exrCompression", "3", "--exrMaxWriters", "1",
               "--gpuPlatform", "0", "--decodeThreads", "4", "--numGraphs", "1",
               "--NR", "0", "--cnr", "0", "--flashingPixels", "0", "--noAudio", "--verbose"]
    environment = os.environ.copy()
    environment["LD_LIBRARY_PATH"] = str(tool / "libs")
    result = {"purpose": "真实 R3D 的全分辨率官方 CPU 解码；不评价 LUT 运行时性能或完整色域精度",
              "platform": platform.platform(), "python": sys.version,
              "script_sha256": sha(__file__), "raw": str(raw), "raw_bytes": raw.stat().st_size,
              "raw_sha256": sha(raw), "raw_source": "https://samples.ffmpeg.org/r3d/",
              "source_scope": "公开 FFmpeg 样片，不是本轮从 RED 登录样片页取得；不上传素材或衍生像素",
              "command": command, "cwd": str(tool / "libs"),
              "LD_LIBRARY_PATH": environment["LD_LIBRARY_PATH"],
              "binary_sha256": sha(binary), "settings": {
                  "resolution": "full", "gpuPlatform": 0, "decodeThreads": 4, "numGraphs": 1,
                  "color_science": "IPP2", "primary_development": True,
                  "color_space": "REDWideGamutRGB", "gamma": "Log3G10", "metadata_defaults": True,
                  "exrACES": False, "exrSoftClamp": False, "exrCompression": "ZIP (3)",
                  "noise_reduction": False, "chroma_noise_reduction": False, "flashing_pixel_adjustment": False}}
    (output / "invocation.json").write_text(json.dumps(result, ensure_ascii=False, indent=2), encoding="utf-8")
    start = time.perf_counter()
    with (output / "redline.log").open("wb") as log:
        process = subprocess.run(command, cwd=tool / "libs", env=environment, stdout=log, stderr=subprocess.STDOUT)
    result["wall_seconds_including_startup_and_io"] = time.perf_counter() - start
    result["returncode"] = process.returncode
    result["max_child_rss_kib"] = resource.getrusage(resource.RUSAGE_CHILDREN).ru_maxrss
    result["log_sha256"] = sha(output / "redline.log")
    result["files"] = [{"path": str(path), "bytes": path.stat().st_size, "sha256": sha(path)}
                       for path in sorted(output.glob("*.exr"))]
    (output / "decode-result.json").write_text(json.dumps(result, ensure_ascii=False, indent=2), encoding="utf-8")
    print(json.dumps({"returncode": process.returncode, "output": str(output), "files": len(result["files"]),
                      "wall_seconds": result["wall_seconds_including_startup_and_io"]}), flush=True)
    if process.returncode != 0 or len(result["files"]) != 1:
        raise RuntimeError("官方解码未成功生成唯一 EXR，请保留原始失败证据")


if __name__ == "__main__":
    main()
