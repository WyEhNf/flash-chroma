"""只读比较固定连续/交错分块的ID表行集合，不调用原生内核或计时。"""
from __future__ import annotations

import argparse
import hashlib
import json
import platform
from pathlib import Path
import sys

import numpy as np

ROOT = Path(__file__).resolve().parents[2]
PHOTO_PATH = ROOT / "artifacts/skylake-server-matrix-v1/server-inputs/photos.rgb"
PHOTO_SHA = "e13278cfc91c3411b3c242232239f9ea6fbda3bf5d18c3f17c41a4dedf57defd"
BLOCK_PIXELS = 65536
BLOCKS = 1200
THREADS = 4
LINE_BYTES = 64
TABLE_LINES = (1 << 24) // LINE_BYTES


def sha256(path: Path) -> str:
    with path.open("rb") as stream:
        return hashlib.file_digest(stream, "sha256").hexdigest()


def analyze(photos: Path) -> dict:
    if photos.stat().st_size != BLOCK_PIXELS * BLOCKS * 3:
        raise ValueError("照片大小与冻结100图不符")
    packed = np.empty((BLOCKS, TABLE_LINES // 8), np.uint8)
    counts = np.empty(BLOCKS, np.int64)
    digest = hashlib.sha256()
    with photos.open("rb") as stream:
        for block in range(BLOCKS):
            raw = stream.read(BLOCK_PIXELS * 3)
            if len(raw) != BLOCK_PIXELS * 3:
                raise ValueError("照片被截断")
            digest.update(raw)
            rgb = np.frombuffer(raw, np.uint8).reshape(-1, 3).astype(np.uint32)
            # 40/65的R低布局：地址=R+256G+65536B，行号为地址右移6位。
            line = (rgb[:, 0] >> 6) | (rgb[:, 1] << 2) | (rgb[:, 2] << 10)
            bits = np.zeros(TABLE_LINES, np.uint8)
            bits[line] = 1
            counts[block] = int(bits.sum())
            packed[block] = np.packbits(bits)
        if stream.read(1):
            raise ValueError("照片存在额外字节")
    if digest.hexdigest() != PHOTO_SHA:
        raise ValueError("照片SHA与冻结输入不符")

    popcount = np.unpackbits(np.arange(256, dtype=np.uint8)[:, None], axis=1).sum(axis=1)
    assignments = {
        "contiguous_static": np.arange(BLOCKS).reshape(THREADS, BLOCKS // THREADS).T,
        "cyclic_static_1": np.arange(BLOCKS).reshape(BLOCKS // THREADS, THREADS),
    }
    result = {}
    for name, order in assignments.items():
        sets = packed[order]
        union = popcount[np.bitwise_or.reduce(sets, axis=1)].sum(axis=1)
        intersection = popcount[np.bitwise_and.reduce(sets, axis=1)].sum(axis=1)
        individual_sum = counts[order].sum(axis=1)
        per_thread = counts[order].sum(axis=0)
        result[name] = {
            "mean_4block_union_ID_lines": float(union.mean()),
            "mean_sum_4block_individual_ID_lines": float(individual_sum.mean()),
            "mean_4way_common_ID_lines": float(intersection.mean()),
            "total_individual_ID_lines_by_thread": per_thread.tolist(),
            "max_over_mean_thread_individual_lines": float(per_thread.max() / per_thread.mean()),
            "mean_union_bytes": float(union.mean() * LINE_BYTES),
        }
    result["cyclic_over_contiguous_union_ratio"] = (
        result["cyclic_static_1"]["mean_4block_union_ID_lines"]
        / result["contiguous_static"]["mean_4block_union_ID_lines"]
    )

    measurement_path = ROOT / "artifacts/skylake-chroma-batch4-io-quiet-perf-v1/results.json"
    measurement = json.loads(measurement_path.read_text(encoding="utf-8"))
    four_thread = [row for row in measurement["summary"] if row["requested_threads"] == 4]
    source_paths = [
        "experiments/skylake-id-batch4-runtime/channel_runtime.cpp",
        "experiments/skylake-id-batch4-runtime/channel_avx2.cpp",
        "experiments/skylake-chroma-batch4-io-runtime/reference_to.cpp",
        "experiments/skylake-chroma-batch4-io-runtime/outplace_bench.cpp",
        "scripts/bench_skylake_quiet_pinned_linux.py",
    ]
    return {
        "purpose": "只读分析65536像素块的连续与固定交错分配，评估共享ID工作集与负载差的代理指标",
        "environment": {"platform": platform.platform(), "python": sys.version, "numpy": np.__version__},
        "script_sha256": sha256(Path(__file__)),
        "photo_path": str(photos.resolve()),
        "photo_sha256": digest.hexdigest(),
        "photo_bytes": photos.stat().st_size,
        "block_pixels": BLOCK_PIXELS,
        "block_bytes": BLOCK_PIXELS * 3,
        "blocks": BLOCKS,
        "threads": THREADS,
        "ID_layout": "R低/G中/B高，16MiB u8 ID表，64字节行",
        "method": [
            "每块记录其65536像素访问的ID表行集合，每行在该块只计一次。",
            "连续static的第j组使用块[j,j+300,j+600,j+900]；static,1使用[4j,4j+1,4j+2,4j+3]，j为0至299。",
            "统计每组四块的行并集、交集，以及各线程全部块的块内唯一行数之和。",
            "每张1024×768图恰有12块；连续分配对应每线程连续25张，交错分配使每线程每张图取得3块。",
        ],
        "result": result,
        "existing_measurement_context": {
            "path": str(measurement_path),
            "sha256": sha256(measurement_path),
            "four_thread_summary": four_thread,
            "interpretation": "67候选绝对apply耗时低于outplace；两接口相对23倍数差不能解释成候选原地比输出慢。23真实输出在计时区间内执行整批memcpy，纯apply区间从复制完成后开始。",
            "cache_state_limit": "计时外的memcpy仍会改变缓存状态；未采集足够证据将其归因为具体缓存瓶颈。两库apply均遵守原冻结流程。",
        },
        "read_source_sha256": {name: sha256(ROOT / name) for name in source_paths},
        "single_candidate": "从65仅将原地apply的OpenMP schedule(static)改为schedule(static,1)，保持65536像素块、像素内核及分离输出路径；基准、模型和输出契约不变。",
        "correctness_and_risk": [
            "每块字节范围不变，旧输入读取/预取块界和原地先读后写规则继续适用；小输入、尾部及实际四线程需另行验证。",
            "未对齐输入的跨线程块边界最多各共享一条缓存行；交错可能把跨线程边界从3处增加到1199处。",
            "每块内部192KiB仍顺序访问，但线程跨块跳跃；真实缓存、预取和带宽收益未知。",
        ],
        "limits": [
            "假定四线程同序块同时进行，仅用于集合比较；运行时不增加块间同步，也不保证严格同步。",
            "唯一行数之和不是逐线程耗时或真实未命中数；没有模拟LRU、缓存组映射、缓存层级或时间顺序。",
            "集合改善不能换算为33.46%提速，不能代替当前三倍目标验收。",
            "仅覆盖已见固定100图及R低布局；不外推其他照片、通道差布局或真实Skylake速度。",
        ],
        "native_calls": 0,
        "performance_calls": 0,
        "existing_files_modified": 0,
        "reproduce": "artifacts/error-study-py312/Scripts/python.exe artifacts/skylake-interleaved-readonly-v1/analyze.py --output <不存在的新JSON路径>",
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--photos", type=Path, default=PHOTO_PATH)
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    if args.output is not None and args.output.exists():
        raise ValueError("不得覆盖既有分析")
    value = analyze(args.photos)
    data = json.dumps(value, ensure_ascii=False, indent=2) + "\n"
    if args.output is not None:
        with args.output.open("x", encoding="utf-8") as stream:
            stream.write(data)
    print(json.dumps(value["result"], ensure_ascii=True))


if __name__ == "__main__":
    main()
