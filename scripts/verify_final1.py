"""复核 final1 归档身份、生成来源及逐图/逐轮汇总；不代替运行时数值验收。"""
import argparse
import hashlib
import json
from pathlib import Path
import statistics
import subprocess

from package_final1 import ROOT, DELIVERY, generate, generate_legacy

REPORT = ROOT / "report/data/final1-20261030"


def read(name):
    return json.loads((REPORT / name).read_text(encoding="utf-8-sig"))


def require(value, message):
    if not value:
        raise RuntimeError(message)


def close(a, b):
    require(abs(a - b) <= 1e-10 * max(1, abs(b)), "汇总数值不匹配")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--staged", action="store_true", help="同时校验暂存 Git blob，防止换行转换改变原件")
    args = parser.parse_args()
    manifest = read("manifest.json")
    for name, expected in manifest["files"].items():
        data = (ROOT / name).read_bytes()
        require(hashlib.sha256(data).hexdigest() == expected, "文件 SHA 不匹配：" + name)
        if args.staged:
            data = subprocess.check_output(["git", "show", ":" + name], cwd=ROOT)
            require(hashlib.sha256(data).hexdigest() == expected, "Git blob SHA 不匹配：" + name)
    release = read("release-manifest.json")
    for name, generated in generate_legacy().items():
        require(hashlib.sha256(generated).hexdigest() == release[name], "内嵌来源与原服务器两文件源码不一致：" + name)
    for name, generated in generate().items():
        data = (DELIVERY / name).read_bytes()
        require(data == generated, "模块生成不一致：" + name)
    require(not (DELIVERY / "flash_chroma_framework.hpp").exists(), "单文件交付中不应有额外头文件")
    for name, expected in release.items():
        path = REPORT / name
        if path.is_file():
            require(hashlib.sha256(path.read_bytes()).hexdigest() == expected, "归档原件与发布清单不一致：" + name)
    selected = read("selection.json")
    quality = read("evidence/correctness.json")
    require(quality["model_equal_to_frozen_prefix_nodes"] and quality["all_rgb24_output_equal"], "缺少模型/全域通过回执")
    require(quality["domain"] == selected["domain"], "完整域记录不一致")
    require(len(quality["images"]) == 104, "逐图数量不完整")
    for dataset, count in [("official4", 4), ("photos100", 100)]:
        rows = [row for row in quality["images"] if row["dataset"] == dataset]
        require(sorted(row["image"] for row in rows) == list(range(1, count + 1)), "图像编号不完整")
        means = [row["quality"]["mean"] for row in rows]
        close(statistics.mean(means), selected["photos"][dataset]["mean"])
        close(max(means), selected["photos"][dataset]["worst_image_mean"])
    timing = read("evidence/timing.json")
    require(len(timing["rounds"]) == 5, "计时轮次不完整")
    means = []
    for row in timing["rounds"]:
        require(len(row["per_image_ms"]) == 100, "逐图耗时不完整")
        close(statistics.mean(row["per_image_ms"]), row["mean_ms"])
        means.append(row["mean_ms"])
    close(statistics.median(means), selected["timing"]["median_round_mean_ms"])
    close(statistics.mean(means), selected["timing"]["mean_all_ms"])
    receipt = read("evidence/validation-receipt.json")
    require(receipt["complete"] and receipt["sources_and_inputs_unchanged"], "原验收身份检查未通过")
    require(receipt["sources"]["verify_and_benchmark.cpp"] == hashlib.sha256((ROOT / "experiments/final1/verify_and_benchmark.cpp").read_bytes()).hexdigest(), "验收器来源不一致")
    single = ROOT / "report/data/final1-single-20261030"
    current = json.loads((single / "validation.json").read_text(encoding="utf-8"))
    require(current["complete"] and current["sources_and_inputs_unchanged"], "单文件服务器验收未通过")
    require(current["preprocessed_equal"] and current["binary_equal_to_previous"], "单文件改变了原服务器可执行内容")
    require(current["inputs"] == receipt["inputs"], "两场数据身份不同")
    for name, expected in current["sources"].items():
        path = DELIVERY / name if name == "main.cpp" else ROOT / "experiments/final1" / name
        require(hashlib.sha256(path.read_bytes()).hexdigest() == expected, "单文件实测源不一致：" + name)
    audit = json.loads((single / "function-audit.json").read_text(encoding="utf-8"))
    require(audit["changed"] == ["lut_sparse", "apply_3d_lut", "main"] and len(audit["unchanged"]) == 10, "原函数审计不符合记录")
    require(audit["timed_block_unchanged"] and all(audit["structs_unchanged"].values()), "原计时区或结构体发生修改")
    require(audit["single_main_sha256"] == current["sources"]["main.cpp"], "原函数审计未绑定当前源")
    stage = json.loads((single / "stage-timing.json").read_text(encoding="utf-8"))
    summary = json.loads((single / "stage-summary.json").read_text(encoding="utf-8"))
    require(len(stage["per_image"]) == 100, "分段诊断不足百图")
    close(stage["Start_to_End_seconds"], stage["read_seconds"] + stage["getLut_to_SpareLut_seconds"] + stage["SpareLut_to_End_seconds"])
    for key, value in summary["per_image_mean_ms"].items():
        close(statistics.mean(row[key] for row in stage["per_image"]) * 1000, value)
    close(statistics.mean(row["mean"] for row in stage["per_image"]), selected["photos"]["photos100"]["mean"])
    print(json.dumps({"complete": True, "files": len(manifest["files"]), "staged": args.staged, "images": 104, "timed_images": 500, "median_round_mean_ms": statistics.median(means)}, ensure_ascii=False))


if __name__ == "__main__":
    main()
