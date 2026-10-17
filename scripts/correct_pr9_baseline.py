"""从已提交汇总复算 m33 基线，另存勘误，不拟合、不测速、不覆写历史表。"""
import argparse
import csv
import hashlib
import io
import json
from pathlib import Path
import statistics
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "python"))
from lutlab.study_reporting import select_baseline


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input", type=Path, default=ROOT / "artifacts/local-lut-study/20261016/summary")
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    if args.output.resolve().is_relative_to(args.input.resolve()):
        raise ValueError("勘误必须保存到历史输入目录之外")
    with (args.input / "full-results.csv").open(encoding="utf-8-sig", newline="") as stream:
        full = list(csv.DictReader(stream))
    with (args.input / "best-per-lut.csv").open(encoding="utf-8-sig", newline="") as stream:
        reader = csv.DictReader(stream)
        fields, rows = reader.fieldnames, list(reader)
    changes, improvements = [], []
    for row in rows:
        baseline = select_baseline([r for r in full if r["lut"] == row["lut"]])
        number = float(baseline["mean"])
        improvement = 100 * (1 - float(row["mean"]) / number) if number else None
        if float(row["baseline_mean"]) != number:
            changes.append({"lut": row["lut"], "previous_baseline_mean": row["baseline_mean"],
                            "corrected_baseline_mean": baseline["mean"],
                            "previous_improvement_percent": row["improvement_percent"],
                            "corrected_improvement_percent": improvement})
            row.update(baseline_mean=baseline["mean"], improvement_percent=improvement)
        if improvement is not None:
            improvements.append(improvement)
    result = {"scope": "已提交完整100图汇总的派生勘误；原始测量与最优候选不变",
              "baseline": "sample_tetra/m33", "lut_count": len(rows), "affected_luts": len(changes),
              "median_improvement_percent": statistics.median(improvements), "changes": changes,
              "inputs_sha256": {name: hashlib.sha256((args.input / name).read_bytes()).hexdigest()
                                for name in ("full-results.csv", "best-per-lut.csv")}}
    buffer = io.StringIO(newline="")
    writer = csv.DictWriter(buffer, fields, lineterminator="\n")
    writer.writeheader()
    writer.writerows(rows)
    outputs = {"best-per-lut.corrected.csv": buffer.getvalue(),
               "correction.json": json.dumps(result, ensure_ascii=False, indent=2, allow_nan=False) + "\n"}
    args.output.mkdir(parents=True, exist_ok=True)
    for name, value in outputs.items():
        path = args.output / name
        encoded = value.encode("utf-8")
        if path.exists() and path.read_bytes() != encoded:
            raise ValueError(f"已有不同勘误内容，拒绝覆盖：{path}")
        if not path.exists():
            path.write_bytes(encoded)
    print(json.dumps({key: result[key] for key in ("lut_count", "affected_luts", "median_improvement_percent")}))


if __name__ == "__main__":
    main()
