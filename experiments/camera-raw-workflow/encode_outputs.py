"""单独导出带色彩标记的FFV1文件，并解码核对全部RGB原字节。"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import subprocess
import time
from pathlib import Path


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--run", type=Path, required=True)
    parser.add_argument("--ffmpeg", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--threads", type=int, choices=[1, 2, 4, 8], default=4)
    parser.add_argument("--context", type=int, choices=[0, 1], default=1)
    parser.add_argument("--ffv1-version", type=int, choices=[3, 4], default=3,
                        help="4为实验容器；本机6K的v3最坏包预分配失败时使用，仍须完整往返验证")
    parser.add_argument("--resume", action="store_true", help="保留已有容器，补做完整回读；不覆盖已有编码")
    args = parser.parse_args()
    run = json.loads((args.run / "results.json").read_text(encoding="utf-8"))
    if not run.get("complete"):
        raise ValueError("映射未完整结束，不能导出完整流程结果")
    args.output.mkdir(parents=True, exist_ok=args.resume)
    args.ffmpeg.chmod(args.ffmpeg.stat().st_mode | 0o111)
    version = subprocess.run([str(args.ffmpeg), "-version"], capture_output=True, check=True).stdout.decode()
    result = {"run_sha256": hashlib.sha256((args.run / "results.json").read_bytes()).hexdigest(),
              "script_sha256": hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
              "ffmpeg_sha256": hashlib.sha256(args.ffmpeg.read_bytes()).hexdigest(), "ffmpeg_version": version,
              "scope": "编码在映射计时全部结束后执行；解码逐字节验证不计入生产映射", "files": []}
    previous = {}
    checkpoint = args.output / "progress.json"
    if args.resume and checkpoint.exists():
        data = json.loads(checkpoint.read_text(encoding="utf-8"))
        if data["run_sha256"] != result["run_sha256"]:
            raise ValueError("已有导出检查点不属于本次回放")
        suffix = 1
        while (args.output / f"prior-progress-{suffix}.json").exists():
            suffix += 1
        preserved = args.output / f"prior-progress-{suffix}.json"
        preserved.write_bytes(checkpoint.read_bytes())
        result["continued_from_sha256"] = hashlib.sha256(preserved.read_bytes()).hexdigest()
        previous = {(entry["target"], entry["kind"]): entry for entry in data["files"]}
    for target in ("sdr", "hdr"):
        for kind, pixel_format, width_bytes in (("reference16", "rgb48le", 6), ("runtime8", "rgb24", 3)):
            directory = args.run / f"{target}-{kind}"
            frames = sorted(directory.glob("frame-*.rgb"))
            if len(frames) != len(run["frames"]):
                raise ValueError("输出帧数不符")
            output = args.output / f"{target}-{kind}.mkv"
            command = [str(args.ffmpeg), "-hide_banner", "-nostdin", "-filter_threads", "1", "-filter_complex_threads", "1", "-thread_queue_size", "1", "-f", "rawvideo", "-pixel_format", pixel_format,
                       "-video_size", f'{run["width"]}x{run["height"]}', "-framerate", str(run["fps"]), "-i", "pipe:0",
                       "-an", "-vf", "setparams=range=full:color_primaries=" + ("bt2020:color_trc=smpte2084" if target == "hdr" else "bt709:color_trc=bt709") + ":colorspace=gbr",
                       "-c:v", "ffv1", "-level", str(args.ffv1_version), "-strict", "experimental" if args.ffv1_version == 4 else "normal",
                       "-coder", "1", "-context", str(args.context), "-threads", str(args.threads),
                       "-pix_fmt", "gbrp16le", "-color_range", "pc", "-colorspace", "0",
                       "-color_primaries", "bt2020" if target == "hdr" else "bt709",
                       "-color_trc", "smpte2084" if target == "hdr" else "bt709", "-thread_queue_size", "1", str(output)]
            start = time.perf_counter()
            expected, size = hashlib.sha256(), 0
            reused = output.exists() and args.resume
            if reused:
                for frame in frames:
                    if frame.stat().st_size != run["width"] * run["height"] * width_bytes:
                        raise ValueError("输出帧字节数不符")
                    with frame.open("rb") as stream:
                        while chunk := stream.read(4 * 1024 * 1024):
                            expected.update(chunk); size += len(chunk)
                encode_seconds = None
                verified = previous.get((target, kind))
                if verified:
                    with output.open("rb") as stream:
                        current_sha = hashlib.file_digest(stream, "sha256").hexdigest()
                    if (not verified["roundtrip_equal"] or verified["frames"] != len(frames)
                            or verified["roundtrip_sha256"] != expected.hexdigest()
                            or verified["roundtrip_bytes"] != size or verified["sha256"] != current_sha
                            or verified["bytes"] != output.stat().st_size):
                        raise AssertionError("已有全量验证与当前输入/视频身份不符")
                    row = dict(verified)
                    row["verification_reused_from_sha256"] = result["continued_from_sha256"]
                    result["files"].append(row)
                    checkpoint.write_text(json.dumps(result, ensure_ascii=False, indent=2), encoding="utf-8")
                    print(json.dumps({"target": target, "kind": kind, "frames": len(frames), "verified_checkpoint_identity_equal": True}), flush=True)
                    continue
            else:
              with (args.output / f"{target}-{kind}-encode.log").open("xb") as log:
                process = subprocess.Popen(command, stdin=subprocess.PIPE, stdout=subprocess.DEVNULL, stderr=log)
                try:
                    for frame in frames:
                        if frame.stat().st_size != run["width"] * run["height"] * width_bytes:
                            raise ValueError("输出帧字节数不符")
                        with frame.open("rb") as stream:
                            while chunk := stream.read(4 * 1024 * 1024):
                                expected.update(chunk)
                                size += len(chunk)
                                process.stdin.write(chunk)
                    process.stdin.close()
                    if process.wait() != 0:
                        raise RuntimeError("FFV1编码失败，见原始日志")
                except BaseException:
                    process.kill(); process.wait()
                    raise
              encode_seconds = time.perf_counter() - start
            command_decode = [str(args.ffmpeg), "-hide_banner", "-nostdin", "-filter_threads", "1", "-filter_complex_threads", "1", "-thread_queue_size", "1", "-threads", str(args.threads), "-i", str(output), "-map", "0:v:0",
                              "-an", "-threads", str(args.threads), "-thread_queue_size", "1", "-f", "rawvideo", "-pix_fmt", pixel_format, "pipe:1"]
            start = time.perf_counter()
            actual, decoded_size = hashlib.sha256(), 0
            attempt = 1
            verify_log = args.output / f"{target}-{kind}-verify.log"
            while verify_log.exists():
                attempt += 1
                verify_log = args.output / f"{target}-{kind}-verify-{attempt}.log"
            with verify_log.open("xb") as log:
                process = subprocess.Popen(command_decode, stdout=subprocess.PIPE, stderr=log)
                while chunk := process.stdout.read(4 * 1024 * 1024):
                    actual.update(chunk); decoded_size += len(chunk)
                if process.wait() != 0:
                    raise RuntimeError("FFV1解码失败")
            if decoded_size != size or actual.hexdigest() != expected.hexdigest():
                raise AssertionError("容器往返RGB字节不一致")
            metadata_log = verify_log.read_text(encoding="utf-8", errors="replace")
            required_tags = ("gbrp16le", "pc", "gbr", "bt2020", "smpte2084") if target == "hdr" else ("gbrp16le", "pc", "gbr", "bt709")
            if any(tag not in metadata_log for tag in required_tags):
                raise AssertionError("输出像素格式或HDR传递函数标记未确认")
            with output.open("rb") as stream:
                file_sha = hashlib.file_digest(stream, "sha256").hexdigest()
            row = {"target": target, "kind": kind, "command": command, "decode_command": command_decode,
                   "file": str(output.resolve()), "bytes": output.stat().st_size, "sha256": file_sha,
                   "input_significant_bits": 16 if kind == "reference16" else 8,
                   "ffv1_version": None if reused else args.ffv1_version,
                   "container_experimental": None if reused else args.ffv1_version == 4,
                   "stored_pixel_format": "gbrp16le", "frames": len(frames), "roundtrip_bytes": size,
                   "reused_existing_encode": reused, "verification_log": str(verify_log),
                   "command_executed_this_invocation": not reused,
                   "command_role": "本次编码命令" if not reused else "未执行的备选编码命令；实际已有编码见原始encode.log与冻结的先前脚本",
                   "roundtrip_sha256": actual.hexdigest(), "roundtrip_equal": True,
                   "encode_seconds": encode_seconds, "verification_seconds": time.perf_counter() - start}
            result["files"].append(row)
            (args.output / "progress.json").write_text(json.dumps(result, ensure_ascii=False, indent=2), encoding="utf-8")
            print(json.dumps({k: row[k] for k in ("target", "kind", "frames", "bytes", "roundtrip_equal")}), flush=True)
    result["complete"] = True
    (args.output / "results.json").write_text(json.dumps(result, ensure_ascii=False, indent=2), encoding="utf-8")


if __name__ == "__main__":
    main()
