"""对入围单级模型穷举全部RGB8输入；不将图片最大误差当全域最大误差。"""
import argparse
import json
from pathlib import Path
import sys
import numpy as np
import numba

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "python"))
from lutlab import io, study_kernels
from lutlab.compatibility import KINDS, METRICS, digest, model_args, write_json

parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument("--input", type=Path, required=True)
args = parser.parse_args()
out = args.input.resolve()
numba.set_num_threads(4)
encoded = np.arange(256 ** 3, dtype=np.uint32)
points = np.empty((256 ** 3, 3), np.uint8)
points[:, 0], points[:, 1], points[:, 2] = encoded >> 16, (encoded >> 8) & 255, encoded & 255
del encoded
results = {"scope": "单级完整16,777,216个RGB8输入", "source_code_sha256": digest(Path(__file__)), "rows": []}
for index, path in enumerate(sorted((out / "luts").glob("*/result.json"))):
    report = json.loads(path.read_text(encoding="utf-8"))
    truth = np.load(out / "references" / (report["lut"]["sha256"][:12] + ".npy"), mmap_mode="r").reshape(-1,3)
    for row in report["full"]:
        model_path = out / row["model"]
        if digest(model_path) != row["model_sha256"]:
            raise ValueError("模型哈希变化")
        model = io.load_sparse(model_path)
        summary = study_kernels.image_metrics(points[None], truth, *model_args(model), KINDS[row["kernel"]])[0]
        results["rows"].append({"lut": report["lut"]["path"], "profile": row["profile"], "m": row["m"],
            "model_sha256": row["model_sha256"], **{k: float(summary[i]) for i,k in enumerate(METRICS)}})
    write_json(out / "cube-finalists.json", results)
    print(f"已穷举 {index+1}/68 LUT，共{len(results['rows'])}个模型", flush=True)
