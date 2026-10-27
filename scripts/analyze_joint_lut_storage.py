"""分析固定四级 SLUT 的跨级相关性与无损联合存储上界。"""
from __future__ import annotations

import argparse
import hashlib
import json
import lzma
import math
from pathlib import Path
import struct
import zlib

import numpy as np


ROOT = Path(__file__).resolve().parents[1]


def sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def load_slut(path: Path) -> dict:
    data = path.read_bytes()
    if len(data) < 16 or data[:4] != b"SLUT":
        raise ValueError(f"非法 SLUT：{path}")
    version, m, reserved = struct.unpack("<III", data[4:16])
    expected = 16 + 12 * m + 3 * 256 + 3 * 256 * 4 + m**3 * 3
    if version != 1 or reserved != 0 or len(data) != expected:
        raise ValueError(f"SLUT 头部或长度不匹配：{path}")
    offset = 16
    grid_bytes = data[offset : offset + 12 * m]
    offset += 12 * m
    idx_bytes = data[offset : offset + 3 * 256]
    offset += 3 * 256
    frac_bytes = data[offset : offset + 3 * 256 * 4]
    offset += 3 * 256 * 4
    node_bytes = data[offset:]
    nodes = np.frombuffer(node_bytes, np.uint8).reshape(m, m, m, 3).copy()
    return {
        "path": path.as_posix(),
        "m": m,
        "raw": data,
        "header": data[:16],
        "grid": grid_bytes,
        "idx": idx_bytes,
        "frac": frac_bytes,
        "node_bytes": node_bytes,
        "nodes": nodes,
        "sha256": sha256(data),
    }


def compressed_sizes(payload: bytes) -> dict[str, int]:
    return {
        "raw": len(payload),
        "zlib_9": len(zlib.compress(payload, 9)),
        "xz_9": len(lzma.compress(payload, preset=9)),
    }


def residual_cost(base: np.ndarray, targets: list[np.ndarray]) -> dict:
    residuals = np.concatenate([(target.astype(np.int16) - base.astype(np.int16)).ravel()
                                for target in targets])
    escapes = int(np.count_nonzero((residuals < -127) | (residuals > 127)))
    count = int(residuals.size)
    return {
        "values": count,
        "min": int(residuals.min(initial=0)),
        "max": int(residuals.max(initial=0)),
        "zero_fraction": float(np.mean(residuals == 0)),
        "within_int4_fraction": float(np.mean((residuals >= -7) & (residuals <= 7))),
        "within_int5_fraction": float(np.mean((residuals >= -15) & (residuals <= 15))),
        "within_int6_fraction": float(np.mean((residuals >= -31) & (residuals <= 31))),
        "within_int7_fraction": float(np.mean((residuals >= -63) & (residuals <= 63))),
        "within_int8_fraction": float(np.mean((residuals >= -127) & (residuals <= 127))),
        "int8_bitmap_escape_bytes": count + math.ceil(count / 8) + 2 * escapes,
        "packed_9bit_bytes": math.ceil(count * 9 / 8),
        "int16_bytes": count * 2,
        "zlib_int16_bytes": len(zlib.compress(residuals.astype("<i2").tobytes(), 9)),
    }


def profile_stats(name: str, paths: list[Path]) -> dict:
    stages = [load_slut(path) for path in paths]
    if len({stage["m"] for stage in stages}) != 1:
        raise ValueError(f"{name} 的网格尺寸不同，当前节点差分统计不适用")
    arrays = [stage["nodes"] for stage in stages]
    pairwise = []
    for left in range(len(arrays)):
        for right in range(left + 1, len(arrays)):
            delta = arrays[right].astype(np.int16) - arrays[left].astype(np.int16)
            pairwise.append({
                "left": left + 1,
                "right": right + 1,
                "equal_fraction": float(np.mean(delta == 0)),
                "node_rgb_equal_fraction": float(np.mean(np.all(delta == 0, axis=-1))),
                "mean_absolute_delta": float(np.mean(np.abs(delta))),
                "max_absolute_delta": int(np.max(np.abs(delta))),
            })
    median = np.median(np.stack(arrays, axis=0).astype(np.int16), axis=0).astype(np.uint8)
    sequential = residual_cost(arrays[0], arrays[1:2])
    sequential_more = [residual_cost(arrays[index - 1], arrays[index:index + 1])
                       for index in range(1, len(arrays))]
    sequential_total = sum(row["int8_bitmap_escape_bytes"] for row in sequential_more)
    median_cost = residual_cost(median, arrays)
    node_bytes = sum(array.nbytes for array in arrays)
    raw = b"".join(stage["raw"] for stage in stages)
    component_dedupe = {}
    for component in ("header", "grid", "idx", "frac", "node_bytes"):
        values = [stage[component] for stage in stages]
        component_dedupe[component] = {
            "raw_bytes": sum(map(len, values)),
            "unique_bytes": sum(len(value) for digest, value in
                                {sha256(value): value for value in values}.items()),
            "unique_objects": len({sha256(value) for value in values}),
        }
    return {
        "name": name,
        "m": stages[0]["m"],
        "files": [{"path": stage["path"], "bytes": len(stage["raw"]),
                   "sha256": stage["sha256"]} for stage in stages],
        "pairwise_nodes": pairwise,
        "component_dedupe": component_dedupe,
        "four_files": compressed_sizes(raw),
        "node_payload_bytes": node_bytes,
        "sequential_delta": {
            "base_bytes": arrays[0].nbytes,
            "edges": sequential_more,
            "exact_total_bytes": arrays[0].nbytes + sequential_total,
        },
        "median_base_delta": {
            "base_bytes": median.nbytes,
            **median_cost,
            "exact_total_bytes": median.nbytes + median_cost["int8_bitmap_escape_bytes"],
        },
    }


def report_markdown(result: dict) -> str:
    lines = [
        "# 四级LUT联合存储与差分可行性分析",
        "",
        "本报告只分析固定SLUT字节和节点相关性，不重新拟合、不映射图片，也不产生性能结论。",
        "所有差分容量均按可精确重建原始uint8节点计算。",
        "",
        "## 跨配置精确去重",
        "",
        f"- 两套配置原始总字节：{result['cross_profile']['raw_bytes']:,} B。",
        f"- 按完整文件SHA去重后：{result['cross_profile']['deduplicated_bytes']:,} B。",
        f"- 可无损减少：{result['cross_profile']['saved_bytes']:,} B（{result['cross_profile']['saved_fraction']:.2%}）。",
        f"- 相同对象：{', '.join(result['cross_profile']['duplicate_objects']) or '无'}。",
        "",
    ]
    for profile in result["profiles"]:
        lines += [f"## {profile['name']} 四级链", "",
                  f"网格：{profile['m']}³；四份SLUT共{profile['four_files']['raw']:,} B，"
                  f"zlib-9为{profile['four_files']['zlib_9']:,} B，xz-9为{profile['four_files']['xz_9']:,} B。", "",
                  "|级对|分量完全相同比例|RGB节点完全相同比例|平均绝对差|max绝对差|",
                  "|---|---:|---:|---:|---:|"]
        for row in profile["pairwise_nodes"]:
            lines.append(f"|{row['left']}→{row['right']}|{row['equal_fraction']:.2%}|"
                         f"{row['node_rgb_equal_fraction']:.2%}|{row['mean_absolute_delta']:.3f}|"
                         f"{row['max_absolute_delta']}|")
        seq = profile["sequential_delta"]
        med = profile["median_base_delta"]
        lines += ["", "无损节点表示估算：", "",
                  f"- 原四级节点：{profile['node_payload_bytes']:,} B。",
                  f"- 第一级＋相邻级int8/逃逸差分：{seq['exact_total_bytes']:,} B。",
                  f"- 逐位置中位基底＋四级int8/逃逸差分：{med['exact_total_bytes']:,} B。",
                  f"- 中位基底残差落入[-127,127]：{med['within_int8_fraction']:.2%}。", ""]
    lines += [
        "## 解释",
        "",
        "- 完整文件或公共后级完全相同，应优先做内容寻址去重；它没有运行时解码成本。",
        "- 若四级节点差分表示大于原节点总量，则不适合进入热路径；压缩包变小不等于运行时更快。",
        "- 四级链可以在离线阶段联合拟合，但运行时仍需保持逐级RGB8舍入，除非官方允许改变语义并重新做完整精度验收。",
        "- 现有direct表已经把四级计算融合成一次最终查表；继续优化应主要针对direct表布局、地址生成和输出写入，而不是在热路径逐级解码节点差分。",
        "",
    ]
    return "\n".join(lines)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--manifest", type=Path,
                        default=ROOT / "data/p16-unified-models/manifest.json")
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    manifest = json.loads(args.manifest.read_text(encoding="utf-8"))
    profiles = []
    all_objects: list[tuple[str, bytes]] = []
    for name, spec in manifest["profiles"].items():
        paths = [ROOT / row["path"] for row in spec["models"]]
        profiles.append(profile_stats(name, paths))
        all_objects.extend((f"{name}/stage{index + 1}", path.read_bytes())
                           for index, path in enumerate(paths))
        for index, sidecar in enumerate(spec["sidecars"]):
            if sidecar:
                path = ROOT / sidecar["path"]
                all_objects.append((f"{name}/sidecar{index + 1}", path.read_bytes()))
    groups: dict[str, list[tuple[str, bytes]]] = {}
    for name, payload in all_objects:
        groups.setdefault(sha256(payload), []).append((name, payload))
    raw_bytes = sum(len(payload) for _, payload in all_objects)
    deduplicated = sum(len(rows[0][1]) for rows in groups.values())
    result = {
        "schema_version": 1,
        "manifest": args.manifest.as_posix(),
        "profiles": profiles,
        "cross_profile": {
            "raw_bytes": raw_bytes,
            "deduplicated_bytes": deduplicated,
            "saved_bytes": raw_bytes - deduplicated,
            "saved_fraction": (raw_bytes - deduplicated) / raw_bytes,
            "duplicate_objects": [" = ".join(name for name, _ in rows)
                                  for rows in groups.values() if len(rows) > 1],
        },
    }
    args.output.mkdir(parents=True, exist_ok=False)
    (args.output / "results.json").write_text(
        json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    (args.output / "report.md").write_text(report_markdown(result), encoding="utf-8")
    print(json.dumps(result["cross_profile"], ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
