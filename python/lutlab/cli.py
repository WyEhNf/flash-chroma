"""CLI entrypoint for dataset generation, fitting, evaluation, and benchmarking."""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from . import cascade, data, fit as fit_mod, interp, io, luts, metrics
from .runlog import Run


def cmd_gen_data(args):
    with Run("gen-data", {"scenarios": args.scenarios, "seed": args.seed}) as run:
        lists = data.build_images(seed=args.seed)
        scen_meta = {}
        for sid in args.scenarios:
            m = data.build_scenario(sid, force=args.force)
            scen_meta[sid] = m
            print(f"[gen-data] scenario {sid} ready (build_s={m['build_s']}s)")
        run.metrics.update({"image_lists": lists, "n_scenarios": len(scen_meta)})


def cmd_fit(args):
    with Run("fit", {"scenario": args.scenario, "m": args.m, "method": args.method, "mode": args.mode}) as run:
        sdir = data.scenario_dir(args.scenario)
        if not (sdir / "meta.json").exists():
            data.build_scenario(args.scenario)
        tables = [io.load_full(sdir / f"lut{k}.lut256") for k in range(1, 5)]
        out_dir = data.DATA / "models" / args.scenario / f"{args.mode}_{args.method}_m{args.m}"
        out_dir.mkdir(parents=True, exist_ok=True)
        if args.mode == "seq":
            chain, info = cascade.fit_cascade_sequential(tables, args.m, args.method, use_adaptive_grid=args.adaptive)
        elif args.mode == "residual":
            chain, info = cascade.fit_cascade_residual(tables, args.m, use_adaptive_grid=args.adaptive)
        elif args.mode == "composite":
            chain, info = cascade.fit_composite_single(tables, args.m, args.method, use_adaptive_grid=args.adaptive)
        else:
            raise ValueError(args.mode)
        paths = []
        for idx, s in enumerate(chain, 1):
            p = out_dir / f"stage{idx}.slut"
            io.save_sparse(p, s)
            paths.append(str(p))
        run.metrics.update(info | {"slut_paths": paths, "n_stages": len(chain)})
        print(json.dumps(run.metrics, indent=2))


def cmd_evaluate(args):
    with Run("evaluate", {"scenario": args.scenario, "m": args.m, "method": args.method, "mode": args.mode}) as run:
        sdir = data.scenario_dir(args.scenario)
        if not (sdir / "meta.json").exists():
            data.build_scenario(args.scenario)
        comp = io.load_full(sdir / "composite.lut256")
        model_dir = data.DATA / "models" / args.scenario / f"{args.mode}_{args.method}_m{args.m}"
        if not model_dir.exists():
            cmd_fit(args)
        sluts = [io.load_sparse(p) for p in sorted(model_dir.glob("stage*.slut"))]

        def pred_fn(img):
            x = img
            for s in sluts:
                x = interp.apply_tetra_q16(s, x)
            return x

        img_list = (data.DATA / "eval.txt").read_text().splitlines()
        ev = metrics.eval_images(pred_fn, comp, img_list)
        summary = {k: v for k, v in ev.items() if k != "per_image"}
        run.metrics.update(summary)
        (run.dir / "eval_detail.json").write_text(json.dumps(ev, indent=2))
        print(json.dumps(summary, indent=2))


def cmd_bench(args):
    with Run("bench", {"scenario": args.scenario, "m": args.m, "kernel": args.kernel, "threads": args.threads, "mode": args.mode}) as run:
        sdir = data.scenario_dir(args.scenario)
        if not (sdir / "meta.json").exists():
            data.build_scenario(args.scenario)
        model_dir = data.DATA / "models" / args.scenario / f"{args.mode}_{args.method}_m{args.m}"
        if not model_dir.exists():
            cmd_fit(args)
        slut_paths = sorted(model_dir.glob("stage*.slut"))
        b = metrics.run_cpp_bench(
            slut_paths,
            data.DATA / "bench.txt",
            kernel=args.kernel,
            threads=args.threads,
            reps=args.reps,
        )
        run.metrics.update(b)
        print(json.dumps(b, indent=2))


def main(argv=None):
    ap = argparse.ArgumentParser(prog="lutlab")
    sub = ap.add_subparsers(dest="cmd", required=True)

    g = sub.add_parser("gen-data")
    g.add_argument("--scenarios", nargs="+", default=luts.DEFAULT_SCENARIOS)
    g.add_argument("--seed", type=int, default=0)
    g.add_argument("--force", action="store_true")

    for name in ("fit", "evaluate", "bench"):
        p = sub.add_parser(name)
        p.add_argument("--scenario", default="isp-0")
        p.add_argument("--m", type=int, default=33)
        p.add_argument("--method", default="ls_tetra_int")
        p.add_argument("--mode", choices=["seq", "residual", "composite"], default="seq")
        p.add_argument("--adaptive", action="store_true")
        if name == "bench":
            p.add_argument("--kernel", default="tetra_avx2")
            p.add_argument("--threads", type=int, default=0)
            p.add_argument("--reps", type=int, default=5)

    args = ap.parse_args(argv)
    {"gen-data": cmd_gen_data, "fit": cmd_fit, "evaluate": cmd_evaluate, "bench": cmd_bench}[args.cmd](args)


if __name__ == "__main__":
    main(sys.argv[1:])
