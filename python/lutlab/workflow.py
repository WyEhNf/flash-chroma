"""Build or use a supplied binary, verify inputs, and report qualified tradeoffs."""
from __future__ import annotations

import argparse
import json
import os
import subprocess
import sys
from pathlib import Path

from . import data, metrics, selection
from .runlog import Run


def _step(run: Run, name: str, command: list[str], env: dict | None = None) -> None:
    result = subprocess.run(command, cwd=data.ROOT, text=True, env=env,
                            stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    run.path(f"{name}.log").write_text(result.stdout, encoding="utf-8")
    run.metrics.setdefault("commands", []).append({"command": command, "returncode": result.returncode})
    print(result.stdout, end="")
    result.check_returncode()


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--scenario", default="isp-0")
    parser.add_argument("--threshold", required=True, type=float)
    parser.add_argument("--metric", choices=["mean", "p99", "max"], default="mean")
    parser.add_argument("--constraint-scope", choices=["images", "cube", "both"], default="images")
    parser.add_argument("--m", type=int, nargs="+", default=[17, 25, 33])
    parser.add_argument("--profiles", nargs="+", choices=list(selection.PROFILES), default=selection.DEFAULT_PROFILES,
                        help="independent candidates include dp_jitter; dp_guarded must be selected explicitly")
    parser.add_argument("--threads", type=int, default=0)
    parser.add_argument("--reps", type=int, default=5)
    parser.add_argument("--allow-composite", action="store_true")
    parser.add_argument("--allow-residual", action="store_true")
    parser.add_argument("--existing-only", action="store_true")
    parser.add_argument("--executable", type=Path, help="use an existing build, without reconfiguring it")
    parser.add_argument("--build-dir", type=Path, default=data.ROOT / "build")
    parser.add_argument("--generator", help="optional CMake generator for a new build directory")
    parser.add_argument("--skip-tests", action="store_true", help="use only after separate staged verification of this exact build")
    args = parser.parse_args(argv)
    with Run("competition-check", vars(args), commit_logs=False) as run:
        build_dir = args.build_dir.resolve()
        executable = args.executable or os.environ.get("JSHC_BIN")
        if executable is None:
            configure = ["cmake", "-S", str(data.ROOT), "-B", str(build_dir), "-DCMAKE_BUILD_TYPE=Release"]
            if args.generator:
                configure += ["-G", args.generator]
            _step(run, "configure", configure)
            _step(run, "build", ["cmake", "--build", str(build_dir), "--config", "Release", "--parallel"])
            name = "jshc.exe" if os.name == "nt" else "jshc"
            executable = next((path for path in (build_dir / name, build_dir / "Release" / name)
                               if path.is_file()), build_dir / name)
        binary = metrics.resolve_jshc(executable)
        run.metrics["executable"] = str(binary)
        run.metrics["executable_sha256"] = metrics.file_sha256(binary)
        run.metrics["python_executable"] = sys.executable
        run.metrics["build_directory"] = str(build_dir)
        if not args.skip_tests:
            # Supplied binaries can live in arbitrary build directories, including
            # multi-configuration Release subdirectories.
            test_dir = next((path for path in (binary.parent, binary.parent.parent)
                             if (path / "CTestTestfile.cmake").is_file()), None)
            if test_dir is not None:
                _step(run, "test-cpp", ["ctest", "--test-dir", str(test_dir), "-C", "Release", "--output-on-failure"])
            else:
                run.metrics["cpp_test_status"] = "not_available_for_supplied_binary"
            environment = os.environ.copy()
            environment["JSHC_BIN"] = str(binary)
            environment["PYTHONPATH"] = os.pathsep.join(filter(None, [str(data.ROOT / "python"), environment.get("PYTHONPATH")]))
            _step(run, "test-python", [sys.executable, "-m", "pytest", "-q", "tests"], environment)
        else:
            run.metrics["tests_skipped_explicitly"] = True
        if not (data.DATA / "manifest.json").exists():
            data.build_images(seed=0)
            run.metrics["dataset_bootstrapped"] = True
        if not (data.scenario_dir(args.scenario) / "meta.json").exists():
            data.build_scenario(args.scenario)
            run.metrics["scenario_bootstrapped"] = True
        run.metrics["dataset"] = data.verify_images()
        result = selection.select(args.scenario, args.m, args.profiles, args.threshold,
            data.DATA / "eval.txt", data.DATA / "bench.txt", args.threads, args.reps,
            args.metric, args.allow_composite, args.existing_only, True,
            allow_residual=args.allow_residual, constraint_scope=args.constraint_scope, executable=binary)
        run.path("selection.json").write_text(json.dumps(result, indent=2), encoding="utf-8")
        run.metrics["winner"] = result["winner"]
        run.metrics["scenario"] = result["scenario_provenance"]
        print(json.dumps({"recommendations": result["recommendations"],
                          "research_recommendations": result["research_recommendations"],
                          "candidate_status": {row["id"]: row["status"] for row in result["candidates"]}}, indent=2))
    # Research permission cannot turn an unqualified baseline into submission success.
    return 0 if result["winner"] else 2


if __name__ == "__main__":
    raise SystemExit(main())
