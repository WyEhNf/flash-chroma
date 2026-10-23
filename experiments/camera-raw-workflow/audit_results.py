"""独立复算工作流台账与导出回执，不重新执行原生映射。"""
from __future__ import annotations

import argparse
import hashlib
import json
import math
from pathlib import Path


def file_sha(path):
    with path.open("rb") as stream:
        return hashlib.file_digest(stream, "sha256").hexdigest()


def aggregate(metrics):
    count = sum(m["channels"] for m in metrics)
    absolute = sum(m["sum_absolute"] for m in metrics)
    square = sum(m["sum_square"] for m in metrics)
    maximum = max(m["max_normalized"] for m in metrics)
    for m in metrics:
        expected = {"mae_normalized": m["sum_absolute"] / m["channels"],
                    "rmse_normalized": math.sqrt(m["sum_square"] / m["channels"]),
                    "mae_8bit_codes": m["sum_absolute"] / m["channels"] * 255,
                    "max_8bit_codes": m["max_normalized"] * 255}
        if any(not math.isclose(m[k], v, rel_tol=1e-12, abs_tol=1e-12) for k, v in expected.items()):
            raise AssertionError("单帧误差台账复算不符")
    return {"channels": count, "mae_normalized": absolute / count, "rmse_normalized": math.sqrt(square / count),
            "max_normalized": maximum, "mae_8bit_codes": absolute / count * 255, "max_8bit_codes": maximum * 255}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--run", type=Path, action="append", required=True)
    parser.add_argument("--video", type=Path, action="append", default=[])
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    result = {"purpose": "按完整帧的sum/count独立复算，不声称新的像素或性能执行", "cameras": {}, "video_files": []}
    runs = {}
    for directory in args.run:
        path = directory / "results.json"
        data = json.loads(path.read_text(encoding="utf-8"))
        if not data.get("complete") or not data["frames"]:
            raise ValueError("回放尚未完成")
        count = len(data["frames"])
        camera = data["camera"]
        if camera in result["cameras"]:
            raise ValueError("重复摄影机回放")
        row = {"run_sha256": file_sha(path), "frames": count, "pixels_per_branch": data["width"] * data["height"] * count,
               "dimensions": [data["width"], data["height"]], "fps": data["fps"], "branches": {}, "resume_segments": len(data.get("resumptions", [])) + 1}
        if [r["index"] for r in data["frames"]] != list(range(count)):
            raise AssertionError("帧索引不连续")
        for target in ("sdr", "hdr"):
            branches = [frame["branches"][target] for frame in data["frames"]]
            if any(not b["scalar_equal"] or b["runtime_error"]["channels"] != data["width"] * data["height"] * 3 for b in branches):
                raise AssertionError("原生标量或覆盖数量不符")
            actual = data["runtime"][target]["info"]["actual"]
            row["branches"][target] = {"runtime_error_unclipped_float32": aggregate([b["runtime_error"] for b in branches]),
                "float33_error_unclipped_float32": aggregate([b["float33_error"] for b in branches]),
                "native_scalar_equal": True, "cache_enabled": actual["cache"]["enabled"],
                "direct_enabled": actual["direct"]["enabled"], "andn_split_enabled": actual["andn_split_enabled"],
                "runtime_apply_seconds": sum(b["runtime_apply_seconds"] for b in branches),
                "scalar_validation_seconds": sum(b["scalar_check_seconds"] for b in branches),
                "reference_above_one": sum(b["reference_above_one"] for b in branches),
                "reference_below_zero": sum(b["reference_below_zero"] for b in branches)}
            if all("runtime_vs_export16_error" in b for b in branches):
                row["branches"][target]["runtime_vs_export16_error"] = aggregate([b["runtime_vs_export16_error"] for b in branches])
        result["cameras"][camera] = row
        runs[row["run_sha256"]] = camera
    for directory in args.video:
        video = json.loads((directory / "results.json").read_text(encoding="utf-8"))
        if not video.get("complete") or video["run_sha256"] not in runs or len(video["files"]) != 4:
            raise AssertionError("导出回执绑定不符")
        camera = runs[video["run_sha256"]]
        for entry in video["files"]:
            if not entry["roundtrip_equal"] or entry["frames"] != result["cameras"][camera]["frames"]:
                raise AssertionError("导出帧数或逐字节往返失败")
            result["video_files"].append({"camera": camera, **entry})
    result["total_frames"] = sum(row["frames"] for row in result["cameras"].values())
    result["all_native_scalar_equal"] = True
    result["float_reference_precision_preserved"] = all(branch["runtime_error_unclipped_float32"]["max_normalized"] == 0
        for row in result["cameras"].values() for branch in row["branches"].values())
    args.output.write_text(json.dumps(result, ensure_ascii=False, indent=2), encoding="utf-8")
    print(json.dumps({"cameras": list(result["cameras"]), "frames": result["total_frames"],
                      "videos": len(result["video_files"]), "native_scalar_equal": True,
                      "float_precision_preserved": result["float_reference_precision_preserved"]}, ensure_ascii=False))


if __name__ == "__main__":
    main()
