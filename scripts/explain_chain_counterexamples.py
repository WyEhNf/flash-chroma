"""在冻结模型上追加三点整数证书和有限干预；不拟合、不测速、不展开新全色域。"""
import argparse
import hashlib
import json
import math
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "python"))
import numba
import numpy as np
from lutlab import error_analysis as ea, error_certificate, io
from lutlab.compatibility import write_json


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input", type=Path, required=True)
    args = parser.parse_args()
    numba.set_num_threads(4)
    results = json.loads((args.input / "results.json").read_text(encoding="utf-8"))
    discovery = np.load(args.input / "discovery.npy")
    answer = {"parent_run_identity": results["run_identity"], "code_sha256": {}, "cases": []}
    for path in (Path(__file__), ROOT / "python/lutlab/error_certificate.py"):
        answer["code_sha256"][str(path.relative_to(ROOT))] = hashlib.sha256(path.read_bytes()).hexdigest()
    for case in results["cases"]:
        folder = args.input / case["case"]["id"]
        models = [io.load_sparse(folder / f"baseline-stage{k+1}.slut") for k in range(len(case["sources"]))]
        tables = [io.load_full(ROOT / r["path"].replace("\\", "/"), mmap=True) for r in case["sources"]]
        selected = case["selected_stage"] - 1
        hotspots = np.asarray([r["rgb"] for r in case["final"]["baseline"]["cube"]["hotspots"]], np.uint8)
        stage_colours = ea.Operator(models[:selected])(hotspots)
        certificates = []
        for colour in stage_colours:
            for axis in range(3):
                for stride in (1, 2, 4):
                    if not stride <= int(colour[axis]) <= 255-stride:
                        continue
                    points = np.tile(colour, (3, 1))
                    points[0, axis] -= stride
                    points[2, axis] += stride
                    certificate = error_certificate.three_point_bound(models[selected], points,
                        ea.source_apply(tables[selected], points))
                    certificates.append(certificate)
        certificate = max(certificates, key=lambda r: r["rgb_l2_max_lower_bound"]) if certificates else None
        coalition = []
        count = len(models)
        target = ea.exact_chain(tables, discovery)
        for mask in range(1 << count):
            mapped = discovery.copy()
            for k in range(count):
                mapped = ea.source_apply(tables[k], mapped) if mask & (1 << k) else ea.Operator([models[k]])(mapped)
            statistics = ea.metrics(mapped, target)
            coalition.append({"exact_stage_mask": mask, "exact_stages": [k+1 for k in range(count) if mask & (1 << k)],
                              **statistics})
        costs = [r["rms"] ** 2 for r in coalition]
        allocation = []
        for k in range(count):
            value = 0.
            for mask in range(1 << count):
                if mask & (1 << k):
                    continue
                size = mask.bit_count()
                weight = math.factorial(size) * math.factorial(count-size-1) / math.factorial(count)
                value += weight * (costs[mask] - costs[mask | (1 << k)])
            allocation.append(value)
        if abs(sum(allocation) - costs[0]) > 1e-8:
            raise AssertionError("有限干预的MSE分配不守恒")
        answer["cases"].append({"case": case["case"]["id"], "selected_stage": selected+1,
            "fixed_weights_lower_bound": certificate, "interventions": coalition,
            "mse_shapley_allocation": allocation,
            "scope": "固定262144颜色的干预分配，含阶段交互；不是运行方案或未知输入的物理贡献保证"})
        print(case["case"]["id"], "固定权重单级max必要下界", None if certificate is None else certificate["rgb_l2_max_lower_bound"],
              "MSE干预分配", allocation, flush=True)
    write_json(args.input / "explanations.json", answer)


if __name__ == "__main__":
    main()
