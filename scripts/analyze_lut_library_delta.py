"""评估68个既有最佳SLUT之间的无损共享基底与差分存储。"""
from __future__ import annotations

import argparse
import csv
import hashlib
import json
import math
from pathlib import Path
import struct
import zlib

import numpy as np


def load_slut(path: Path) -> dict:
    data = path.read_bytes()
    if data[:4] != b"SLUT":
        raise ValueError(path)
    version, m, reserved = struct.unpack("<III", data[4:16])
    if version != 1 or reserved:
        raise ValueError(path)
    offset = 16
    components = {"header": data[:16]}
    components["grid"] = data[offset:offset + 12 * m]; offset += 12 * m
    components["idx"] = data[offset:offset + 768]; offset += 768
    components["frac"] = data[offset:offset + 3072]; offset += 3072
    components["nodes"] = data[offset:]
    expected = m**3 * 3
    if len(components["nodes"]) != expected:
        raise ValueError(path)
    return {"path": path, "m": m, "raw": data, "components": components,
            "nodes": np.frombuffer(components["nodes"], np.uint8).copy()}


def exact_delta_cost(left: np.ndarray, right: np.ndarray) -> tuple[int, str, float]:
    delta = right.astype(np.int16) - left.astype(np.int16)
    count = delta.size
    best = (count, "原始uint8")
    # b位有符号主体＋1bit逃逸图＋逃逸值原始uint8；只计算可精确重建的容量。
    for bits in range(3, 8):
        limit = (1 << (bits - 1)) - 1
        escapes = int(np.count_nonzero((delta < -limit) | (delta > limit)))
        cost = math.ceil(count * bits / 8) + math.ceil(count / 8) + escapes
        if cost < best[0]:
            best = (cost, f"int{bits}+bitmap+u8逃逸")
    return best[0], best[1], float(np.mean(np.abs(delta)))


def group_stats(models: list[dict]) -> dict:
    count = len(models)
    raw_nodes = sum(model["nodes"].nbytes for model in models)
    costs = np.zeros((count, count), dtype=np.int64)
    schemes, mean_abs = {}, {}
    for i in range(count):
        for j in range(i + 1, count):
            cost, scheme, distance = exact_delta_cost(models[i]["nodes"], models[j]["nodes"])
            costs[i, j] = costs[j, i] = cost
            schemes[f"{i}-{j}"] = scheme
            mean_abs[f"{i}-{j}"] = distance
    # Prim最小生成树：一个原始根，其余按最省的精确父差分恢复。
    used = {0}; edges = []
    while len(used) < count:
        best = None
        for i in used:
            for j in range(count):
                if j in used:
                    continue
                row = (int(costs[i, j]), i, j)
                if best is None or row < best:
                    best = row
        assert best is not None
        cost, left, right = best
        used.add(right)
        edges.append({"parent": left, "child": right, "bytes": cost,
                      "scheme": schemes[f"{min(left, right)}-{max(left, right)}"],
                      "mean_absolute_delta": mean_abs[f"{min(left, right)}-{max(left, right)}"]})
    mst_bytes = models[0]["nodes"].nbytes + sum(edge["bytes"] for edge in edges)
    return {"m": models[0]["m"], "models": count, "raw_node_bytes": raw_nodes,
            "mst_exact_bytes": mst_bytes, "saved_bytes": raw_nodes - mst_bytes,
            "saved_fraction": (raw_nodes - mst_bytes) / raw_nodes,
            "compressed_edge_count": sum(edge["scheme"] != "原始uint8" for edge in edges),
            "edges": edges}


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--study", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    result_by_lut = {}
    for path in (args.study / "luts").glob("*/result.json"):
        data = json.loads(path.read_text(encoding="utf-8"))
        result_by_lut[data["lut"]["path"]] = (path.parent, data)
    selected = []
    with (args.study / "summary/best-per-lut.csv").open(encoding="utf-8-sig", newline="") as stream:
        for row in csv.DictReader(stream):
            folder, data = result_by_lut[row["lut"]]
            matches = [entry for entry in data["full"]
                       if entry["profile"] == row["profile"] and entry["m"] == int(row["m"])]
            if len(matches) != 1:
                raise ValueError(f"无法唯一定位最佳模型：{row['lut']}")
            model_path = args.study / matches[0]["model"].replace("\\", "/")
            model = load_slut(model_path)
            model["lut"] = row["lut"]
            selected.append(model)
    groups = []
    for m in sorted({model["m"] for model in selected}):
        groups.append(group_stats([model for model in selected if model["m"] == m]))
    raw_bytes = sum(len(model["raw"]) for model in selected)
    component_raw, component_unique = {}, {}
    for name in ("header", "grid", "idx", "frac", "nodes"):
        payloads = [model["components"][name] for model in selected]
        unique = {hashlib.sha256(payload).digest(): payload for payload in payloads}
        component_raw[name] = sum(map(len, payloads))
        component_unique[name] = sum(map(len, unique.values()))
    concat = b"".join(model["raw"] for model in selected)
    result = {"schema_version": 1, "model_count": len(selected),
              "grid_counts": {str(m): sum(model["m"] == m for model in selected)
                              for m in sorted({model["m"] for model in selected})},
              "raw_bytes": raw_bytes, "component_raw_bytes": component_raw,
              "component_deduplicated_bytes": component_unique,
              "component_deduplicated_total": sum(component_unique.values()),
              "zlib9_concatenated_bytes": len(zlib.compress(concat, 9)), "groups": groups}
    args.output.mkdir(parents=True, exist_ok=False)
    (args.output / "results.json").write_text(
        json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    lines = ["# 68个LUT最佳模型的联合差分存储分析", "",
             "本报告使用既有best-per-lut选择，不重新拟合或重算精度。差分方案均要求逐字节恢复原SLUT节点。", "",
             f"- 模型数：{result['model_count']}；网格分布：{result['grid_counts']}。",
             f"- 原始SLUT总量：{raw_bytes:,} B。",
             f"- 仅按组件SHA去重：{result['component_deduplicated_total']:,} B。",
             f"- 整包zlib-9：{result['zlib9_concatenated_bytes']:,} B（离线包体，不是热路径容量）。", ""]
    for group in groups:
        lines += [f"## m{group['m']}", "",
                  f"{group['models']}个模型节点原始{group['raw_node_bytes']:,} B；"
                  f"最小生成树精确差分{group['mst_exact_bytes']:,} B；"
                  f"节省{group['saved_bytes']:,} B（{group['saved_fraction']:.2%}）。",
                  f"其中真正采用位压缩差分的边数：{group['compressed_edge_count']}/{max(0, group['models']-1)}。", ""]
    lines += ["## 结论", "",
              "- 如果最小生成树仍接近原始节点容量，说明跨LUT相关性不足以抵消解码和随机父依赖。",
              "- zlib适合下载包或磁盘归档；运行时应在加载时一次性解压回普通SLUT，不应在每像素插值时解码。",
              "- 组件SHA去重与共享不可变对象没有逐像素代价，应优先于差分热表示。", ""]
    (args.output / "report.md").write_text("\n".join(lines), encoding="utf-8")
    print(json.dumps({key: result[key] for key in ("model_count", "grid_counts", "raw_bytes",
                                                    "component_deduplicated_total",
                                                    "zlib9_concatenated_bytes")},
                     ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
