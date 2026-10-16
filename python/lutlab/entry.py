"""One public command surface for fitting, CPU/CUDA mapping and acceptance."""
from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys
from .reportio import write_report as _write_report


def main(argv=None):
    argv = list(sys.argv[1:] if argv is None else argv)
    if argv and argv[0] == "dataset":
        from . import dataset
        return dataset.main(argv[1:])
    if argv and argv[0] == "hackextend":
        from . import hackextend
        return hackextend.main(argv[1:])
    if argv and argv[0] == "hackset":
        from . import hackset
        return hackset.main(argv[1:])
    if argv and argv[0] == "corpus":
        from . import corpus
        return corpus.main(argv[1:])
    if argv and argv[0] == "casebook":
        from . import casebook
        return casebook.main(argv[1:])
    if argv and argv[0] in ("fit", "evaluate", "bench", "gen-data"):
        from . import cli
        return cli.main(argv) or 0
    if argv and argv[0] == "select":
        from . import selection
        return selection.main(argv[1:])
    if argv and argv[0] == "check":
        from . import workflow
        return workflow.main(argv[1:])
    if argv and argv[0] == "compare":
        from . import performance
        return performance.main(argv[1:])
    if argv and argv[0] == "accept":
        from . import qualification
        return qualification.main(argv[1:])

    parser = argparse.ArgumentParser(prog="python -m lutlab", description=__doc__,
        epilog="Also: fit, evaluate, bench, gen-data, select, check, compare, accept; use COMMAND --help.")
    commands = parser.add_subparsers(dest="command", required=True)
    for name, help_text in (("fit", "fit four LUTs into a verified immutable model batch"),
                            ("evaluate", "evaluate a cached scenario model"),
                            ("bench", "benchmark a cached scenario model on CPU"),
                            ("gen-data", "construct local datasets"),
                            ("select", "select qualified sparse models"),
                            ("check", "build and check a scenario workflow"),
                            ("compare", "run balanced paired CPU/CUDA/OCIO comparison"),
                            ("accept", "verify source binding and problem-16 numerical requirements"),
                            ("corpus", "construct and inspect labelled versioned test data"),
                            ("casebook", "maintain evidence-bound per-case champions"),
                            ("hackset", "构造及核对独立压力输入与最小反例候选"),
                            ("hackextend", "追加三维与串联压力配方"),
                            ("dataset", "读取、重建和核对合并后的版本化数据集")):
        commands.add_parser(name, help=help_text)
    for name in ("info", "plan", "apply", "cube", "verify", "bench-models", "validate"):
        command = commands.add_parser(name)
        command.add_argument("--backend", choices=["cpu", "cuda"], default="cpu")
        command.add_argument("--executable", type=Path)
        command.add_argument("--device", type=int, default=0)
        command.add_argument("--report", type=Path)
        if name == "info":
            continue
        command.add_argument("--models", nargs=4, type=Path, required=True)
        command.add_argument("--kernel", default="tetra_c99" if name == "plan" else "auto")
        command.add_argument("--threads", type=int, default=0)
        command.add_argument("--block", type=int, default=256)
        command.add_argument("--competition", action=argparse.BooleanOptionalAction, default=True)
        if name in ("apply", "cube", "verify"):
            command.add_argument("--output", type=Path, required=name != "verify")
        if name == "apply":
            command.add_argument("--input", type=Path, required=True)
        if name in ("verify", "bench-models", "validate"):
            command.add_argument("--images", type=Path, required=True, help="UTF-8 image-list file")
        if name in ("verify", "bench-models"):
            command.add_argument("--batch", action="store_true")
        if name == "bench-models":
            command.add_argument("--reps", type=int, default=5)
        if name == "validate":
            command.add_argument("--reference", type=Path, required=True, help="exact four-full-LUT composite")
            command.add_argument("--threshold", type=float, required=True)
            command.add_argument("--metric", choices=["mean", "p99", "max"], default="mean")
            command.add_argument("--constraint-scope", choices=["images", "cube", "both"], default="both")
            command.add_argument("--skip-cube", action="store_true")
    args = parser.parse_args(argv)
    from . import runtime
    if args.command == "info":
        result = runtime.capabilities(args.backend, args.executable, device=args.device)
    else:
        common = dict(backend=args.backend, executable=args.executable, kernel=args.kernel,
                      threads=args.threads, competition=args.competition,
                      device=args.device, block=args.block)
        if args.command == "apply":
            result = runtime.apply(args.models, args.input, args.output, **common)
        elif args.command == "plan":
            result = runtime.plan(args.models, **common)
        elif args.command == "cube":
            result = runtime.cube(args.models, args.output, **common)
        elif args.command == "verify":
            result = runtime.verify(args.models, args.images, output=args.output,
                                    batch=args.batch, **common)
        elif args.command == "bench-models":
            result = runtime.bench(args.models, args.images, reps=args.reps,
                                   batch=args.batch, **common)
        else:
            from . import validation
            result = validation.validate(args.models, args.reference, args.images,
                threshold=args.threshold, metric=args.metric,
                constraint_scope=args.constraint_scope, full_cube=not args.skip_cube,
                semantics="independent", **common)
    _write_report(args.report, result)
    print(json.dumps(result, indent=2, ensure_ascii=False, allow_nan=False))
    return 0 if result.get("pass", True) else 2
