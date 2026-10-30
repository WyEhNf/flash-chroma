"""只读筛选230色调色板的低成本精确SIMD编码，不调用映射内核或计时。"""
from __future__ import annotations

import argparse
from collections import defaultdict
import hashlib
import json
from pathlib import Path
import platform
import sys

import numpy as np

ROOT = Path(__file__).resolve().parents[2]
GOLD = ROOT / "artifacts/skylake-matrix-cache-gold-v1/cache-gold.u32"
EXPECTED_SHA = "f223e56756ed281372b0ebd858b254110c04ca1f5b2afb6d091c40df3a1ffe90"


def digest(path: Path) -> str:
    with path.open("rb") as stream:
        return hashlib.file_digest(stream, "sha256").hexdigest()


def affine_segments(rgb: np.ndarray, modular: bool) -> dict:
    # dp[e]是在[0,e)上分成互不重叠连续仿射段的精确最小段数。
    n = len(rgb)
    dp = [0] + [n + 1] * n
    previous = [None] * (n + 1)
    for end in range(1, n + 1):
        for start in range(end):
            differences = np.diff(rgb[start:end], axis=0)
            if modular:
                differences = differences & 255
            valid = len(differences) <= 1 or np.all(differences == differences[0])
            if valid and dp[start] + 1 < dp[end]:
                dp[end] = dp[start] + 1
                previous[end] = start
    segments = []
    end = n
    while end:
        start = previous[end]
        segments.append([start, end - 1])
        end = start
    return {"minimum_segments": dp[n], "inclusive_ID_intervals": segments[::-1]}


def analyze() -> dict:
    gold_sha = digest(GOLD)
    if gold_sha != EXPECTED_SHA:
        raise ValueError("后缀金标准SHA不符")
    generation_path = GOLD.with_name("generation.json")
    generation = json.loads(generation_path.read_text(encoding="utf-8"))
    if not generation["generation_completed"] or generation["gold_sha256"] != gold_sha:
        raise ValueError("后缀金标准生成回执不符")
    # 与prepare_palette一致：完整后缀缓存按RGB32数值排序去重，保留230项。
    palette = np.unique(np.fromfile(GOLD, dtype="<u4"))
    if len(palette) != 230:
        raise ValueError("必须使用实际230项缓存调色板，不能缩成221项cube输出排名")
    rgb = np.column_stack((palette & 255, (palette >> 8) & 255, palette >> 16)).astype(np.int32)

    classes = defaultdict(list)
    for r, g, b in rgb:
        classes[(int(g - r), int(b - r))].append(int(r))
    cover = []
    for difference, reds in sorted(classes.items()):
        reds.sort()
        starts = []
        # 每个基数组只允许RGB共同增加0..7；从最小未覆盖R开始的区间覆盖是最优的。
        for red in reds:
            if not starts or red > starts[-1] + 7:
                starts.append(red)
        cover.append({
            "difference_G_R_B_R": list(difference),
            "colours": len(reds),
            "R_values": reds,
            "minimum_length8_intervals": len(starts),
            "interval_starts": starts,
        })

    residuals = [tuple(int(x) for x in row - rgb[(i // 16) * 16]) for i, row in enumerate(rgb)]
    modular_residuals = [tuple(x & 255 for x in row) for row in residuals]
    column_counts = [len({residuals[i] for i in range(column, len(rgb), 16)}) for column in range(16)]
    modular_column_counts = [len({modular_residuals[i] for i in range(column, len(rgb), 16)}) for column in range(16)]
    runtime = ROOT / "experiments/skylake-id-batch4-runtime/channel_runtime.cpp"
    vector_source = ROOT / "experiments/skylake-id-batch4-runtime/channel_avx2.cpp"
    return {
        "purpose": "只读检查230项原调色板能否用少量SIMD整数操作精确恢复RGB，从而消除ID到内存调色板的依赖",
        "environment": {"platform": platform.platform(), "python": sys.version, "numpy": np.__version__},
        "script_sha256": digest(Path(__file__)),
        "inputs": {
            "cache_gold": {"path": str(GOLD), "sha256": gold_sha},
            "generation": {"path": str(generation_path), "sha256": digest(generation_path)},
            "models_from_generation": generation["inputs"],
            "runtime_source": {"path": str(runtime), "sha256": digest(runtime)},
            "vector_source": {"path": str(vector_source), "sha256": digest(vector_source)},
        },
        "palette_derivation": "对已验完整后缀cache-gold.u32做uint32升序去重，与65 prepare_palette的cache排序去重规则相同；没有加载原生库。",
        "palette_entries": len(palette),
        "palette_uint32_bytes_sha256": hashlib.sha256(palette.astype("<u4").tobytes()).hexdigest(),
        "palette_RGB_by_ID": rgb.tolist(),
        "R_unique": int(len(np.unique(rgb[:, 0]))),
        "RGB_difference_classes": len(classes),
        "fixed16_first_colour_base": {
            "distinct_RGB_delta_vectors": len(set(residuals)),
            "per_low_nibble_distinct_delta_counts": column_counts,
            "mod256_distinct_RGB_delta_vectors": len(set(modular_residuals)),
            "mod256_per_low_nibble_distinct_delta_counts": modular_column_counts,
            "required_for_shared_low_nibble_delta_table": "每列差值必须跨所有高4位组一致，即全部列的distinct计数均为1。",
            "eligible": all(x == 1 for x in modular_column_counts),
        },
        "fixed_ID_order_affine": affine_segments(rgb, False),
        "fixed_ID_order_mod256_affine": affine_segments(rgb, True),
        "recode_group5_increment3": {
            "encoding": "code高5位选择RGB基数，低3位同时加到R/G/B，各组覆盖同一(G-R,B-R)类的最多8个连续R值；允许未使用码位。",
            "minimum_groups_needed": sum(row["minimum_length8_intervals"] for row in cover),
            "groups_available": 32,
            "eligible": sum(row["minimum_length8_intervals"] for row in cover) <= 32,
            "difference_classes": cover,
        },
        "decision": "不进入新运行时候选：这些具体低成本精确编码均不成立。保留原ID到内存palette的精确读取，不采用近似。",
        "reasoning": [
            "现有ID顺序不能用少数连续仿射段表示；动态规划给出该指定顺序的精确最少段数。",
            "按16项分组的共同低4位差表不成立；若每组保存独立差表，则仍需选择或加载对应组，不能声称一次PSHUFB即可替代256项任意查表。",
            "允许重新编码的5bit组号加3bit共同增量仍需84组，无法放入32组，不能舍入或合并不等颜色。",
        ],
        "limits": [
            "否定结论仅针对所列编码、现有ID顺序的分段仿射和指定重编码家族，不证明任意8bit整数电路或任意重排都不可能。",
            "230项来自后缀缓存，包含最终完整RGB8输出中未使用的颜色；没有用221项子集替代原运行时调色板。",
            "没有编译或执行新内核，没有计时或Skylake实测；不能由这些结构统计推断精确周期。",
        ],
        "native_calls": 0,
        "performance_calls": 0,
        "existing_files_modified": 0,
        "reproduce": "artifacts/error-study-py312/Scripts/python.exe artifacts/skylake-palette-decode-readonly-v1/analyze.py --output <不存在的新JSON路径>",
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    if args.output is not None and args.output.exists():
        raise ValueError("不得覆盖既有分析")
    result = analyze()
    if args.output is not None:
        with args.output.open("x", encoding="utf-8") as stream:
            json.dump(result, stream, ensure_ascii=False, indent=2)
            stream.write("\n")
    print(json.dumps({
        "palette_entries": result["palette_entries"],
        "R_unique": result["R_unique"],
        "difference_classes": result["RGB_difference_classes"],
        "fixed16": result["fixed16_first_colour_base"],
        "minimum_affine_segments": result["fixed_ID_order_affine"]["minimum_segments"],
        "minimum_mod256_affine_segments": result["fixed_ID_order_mod256_affine"]["minimum_segments"],
        "minimum_8increment_groups": result["recode_group5_increment3"]["minimum_groups_needed"],
    }, ensure_ascii=True))


if __name__ == "__main__":
    main()
