"""One command: build, test, verify inputs, select a strictly passing candidate."""
from __future__ import annotations

import argparse
import json
import subprocess
from pathlib import Path

from . import data, selection
from .runlog import Run


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--scenario", default="isp-0")
    ap.add_argument("--threshold", required=True, type=float)
    ap.add_argument("--metric", choices=["mean", "p99", "max"], default="mean")
    ap.add_argument("--m", type=int, nargs="+", default=[17, 25, 33])
    ap.add_argument("--profiles", nargs="+", choices=list(selection.PROFILES),
                    default=list(selection.PROFILES))
    ap.add_argument("--threads", type=int, default=0)
    ap.add_argument("--reps", type=int, default=3)
    ap.add_argument("--allow-composite", action="store_true")
    ap.add_argument("--existing-only", action="store_true")
    args = ap.parse_args(argv)
    with Run("competition-check", vars(args)) as run:
        subprocess.run(["pixi", "run", "test"], cwd=data.ROOT, check=True)
        run.metrics["dataset"] = data.verify_images()
        run.metrics["scenario"] = data.verify_scenario(args.scenario)
        result = selection.select(args.scenario, args.m, args.profiles, args.threshold,
                                  data.DATA / "eval.txt", data.DATA / "bench.txt",
                                  args.threads, args.reps, args.metric, args.allow_composite,
                                  args.existing_only, True)
        run.path("selection.json").write_text(json.dumps(result, indent=2))
        run.metrics["winner"] = result["winner"]
        print(json.dumps({"winner": result["winner"],
                          "candidate_status": {f"{r['profile']}-m{r['m']}": r['status']
                                               for r in result["candidates"]}}, indent=2))
    return 0 if result["winner"] else 2


if __name__ == "__main__":
    raise SystemExit(main())
