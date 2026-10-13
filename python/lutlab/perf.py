"""Architecture-neutral Zig lane/block/OpenMP/thread throughput sweep."""
from __future__ import annotations

import argparse
import json
import os
import subprocess
from pathlib import Path

from . import data, metrics
from .runlog import Run


def sweep(models: list[Path], image_list: Path, widths: list[int], blocks: list[int],
          schedules: list[str], thread_counts: list[int], reps: int) -> dict:
    rows = []
    for threads in thread_counts:
        for width in widths:
            for block in blocks:
                for schedule in schedules:
                    kernel = {4: "tetra_zig_simd4", 8: "tetra_zig_simd",
                              16: "tetra_zig_simd16"}[width]
                    env = os.environ.copy()
                    env["JSHC_BLOCK_PIXELS"] = str(block)
                    env["OMP_SCHEDULE"] = schedule
                    cmd = [str(metrics.JSHC_BIN), "bench", "-l", str(image_list),
                           "-k", kernel, "-t", str(threads), "-r", str(reps),
                           *map(str, models)]
                    result = subprocess.run(cmd, cwd=data.ROOT, env=env, text=True,
                                            capture_output=True, check=True)
                    bench = json.loads(result.stdout)
                    row = {"width": width, "block_pixels": block, "schedule": schedule,
                           "threads": threads, **bench}
                    rows.append(row)
                    print(f"[perf] lanes={width} block={block} schedule={schedule} "
                          f"threads={threads} set_ms={bench['set_ms_best_rep']}", flush=True)
    return {"winner": min(rows, key=lambda r: r["set_ms_p50_rep"]), "rows": rows}


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--list", type=Path, default=data.DATA / "bench.txt")
    ap.add_argument("--widths", nargs="+", type=int, choices=[4, 8, 16], default=[4, 8, 16])
    ap.add_argument("--blocks", nargs="+", type=int, choices=[1024, 4096, 8192], default=[1024, 4096, 8192])
    ap.add_argument("--schedules", nargs="+", choices=["static", "dynamic,1", "guided,1"],
                    default=["static", "dynamic,1"])
    ap.add_argument("--threads", nargs="+", type=int, default=[1, 4, 20])
    ap.add_argument("--reps", type=int, default=3)
    ap.add_argument("models", nargs="+", type=Path)
    args = ap.parse_args(argv)
    with Run("zig-perf", vars(args)) as run:
        result = sweep(args.models, args.list, args.widths, args.blocks,
                       args.schedules, args.threads, args.reps)
        run.path("sweep.json").write_text(json.dumps(result, indent=2))
        run.metrics.update({"n_configs": len(result["rows"]), "winner": result["winner"]})
        print(json.dumps(result["winner"], indent=2))


if __name__ == "__main__":
    main()
