"""Content-addressed, verified model batches with atomic directory publication.

The readable variant directory is only a namespace. Each identity binds all input
LUT bytes, effective fit parameters, code and solver versions. Published batches
are immutable; incomplete temporary directories and legacy files are never hits.
"""
from __future__ import annotations

import datetime as dt
import hashlib
import importlib.metadata
import inspect
import json
import math
import os
import platform
import sys
import tempfile
import uuid
from dataclasses import dataclass
from pathlib import Path

from . import io

SCHEMA_VERSION = 1
SOURCE_FILES = ("cache.py", "cli.py", "cascade.py", "fit.py", "interp.py", "io.py")


def file_sha256(path: str | Path) -> str:
    with Path(path).open("rb") as stream:
        return hashlib.file_digest(stream, "sha256").hexdigest()


def _json_bytes(value) -> bytes:
    return json.dumps(value, sort_keys=True, separators=(",", ":"),
                      ensure_ascii=True, allow_nan=False).encode("utf-8")


def source_fingerprint() -> dict:
    package = Path(__file__).resolve().parent
    sources = {name: file_sha256(package / name) for name in SOURCE_FILES}
    lock = package.parents[1] / "pixi.lock"
    if lock.is_file():
        sources["pixi.lock"] = file_sha256(lock)
    return sources


def fitting_defaults() -> dict:
    """Record callable defaults as well as the source hashes of internal constants."""
    from . import cascade, fit
    defaults = {}
    for module in (fit, cascade):
        for name, value in sorted(vars(module).items()):
            # lru_cache wraps sampling/grid helpers in a callable object. Its
            # underlying defaults still govern the actual fit and must be bound.
            function = inspect.unwrap(value)
            if not inspect.isfunction(function) or function.__module__ != module.__name__:
                continue
            parameters = {}
            for key, parameter in inspect.signature(function).parameters.items():
                if parameter.default is inspect.Parameter.empty:
                    continue
                default = parameter.default
                if default is None or isinstance(default, (str, int, float, bool)):
                    parameters[key] = default
                else:
                    parameters[key] = repr(default)
            if parameters:
                defaults[f"{module.__name__}.{name}"] = parameters
    return defaults


def algorithm_settings(parameters: dict) -> dict:
    """Human-readable effective R18 controls, alongside complete source hashes.

    These are recorded controls, not a second set of tunable defaults. Callable
    defaults are read from the fitter; in-body constants remain source-bound.
    """
    from . import fit

    def default(function, name):
        return inspect.signature(function).parameters[name].default

    settings = {}
    if parameters.get("method") in ("ls_tetra_jitter", "ls_tetra_guarded"):
        settings["training"] = {
            "scheme": "one_jittered_point_per_4x4x4_block", "block_width": 4,
            "sample_count": 64 ** 3, "seed": default(fit.fit_stratified_tetra, "seed"),
            "sampling_function_default_seed": default(fit.stratified_points, "seed"),
        }
        settings["least_squares"] = {
            "basis": "tetra_q16_unrounded_output", "lambda": default(fit.solve_spd, "lam"),
            "rtol": default(fit.solve_spd, "tol"), "maxiter": default(fit.solve_spd, "maxiter"),
            "initialization": "separable_trilinear_least_squares",
        }
        settings["integer_refinement"] = {
            "objective": "unrounded_quadratic", "sweeps": default(fit.int_refine, "sweeps"),
        }
    if parameters.get("method") == "ls_tetra_guarded":
        settings["q16_refinement"] = {
            "sweeps": default(fit.fit_guarded_tetra, "sweeps"),
            "guard_count": default(fit.guard_points_excluding, "count"),
            "guard_seed": default(fit.guard_points_excluding, "seed"),
            "guard_excludes_training": True,
            "nonregression_metrics": ["mean", "rms", "p99", "max"],
            "guarantee_scope": "single-stage training and guard sets only",
        }
    if parameters.get("grid") == "dp":
        m = parameters["m"]
        settings["grid"] = {
            "method": "axis_chord_sse_dynamic_programming",
            "perpendicular_probes": default(fit.adaptive_dp_grid, "probes"),
            "minimum_step": 2, "maximum_step": math.ceil(2 * 255 / (m - 1)),
            "spacing_penalty": 1e-6, "endpoints": [0, 255], "integer_axis_knots": True,
            "objective_scope": "axiswise unrounded chord SSE surrogate",
        }
    return settings


def build_identity(input_paths: list[Path], parameters: dict) -> dict:
    if len(input_paths) != 4:
        raise ValueError("model identity requires exactly four source LUTs")
    return {
        "schema_version": SCHEMA_VERSION,
        "inputs": [{"stage": stage, "bytes": path.stat().st_size,
                    "sha256": file_sha256(path)} for stage, path in enumerate(input_paths, 1)],
        "parameters": parameters,
        "fitting_defaults": fitting_defaults(),
        "algorithm_settings": algorithm_settings(parameters),
        "source_sha256": source_fingerprint(),
        "solver_environment": {
            "python": platform.python_version(), "numpy": importlib.metadata.version("numpy"),
            "scipy": importlib.metadata.version("scipy"), "machine": platform.machine(),
            "platform": sys.platform, "byteorder": sys.byteorder,
        },
        "format": {"version": 1, "full_shape": list(io.FULL_SHAPE), "node_dtype": "uint8",
                   "channel_order": "RGB", "index_order": "r,g,b,channel (C order)",
                   "fraction_bits": io.Q, "axis_tables": "serialized authoritative",
                   "rounding": ("float trilinear: round and clamp to uint8 per stage"
                                if parameters.get("interpolation_basis") == "trilinear_float"
                                else "Q16 tetra: (weighted_sum + 32768) >> 16 per stage"),
                   "stage_io": "uint8 RGB after every mapping"},
    }


def identity_key(identity: dict) -> str:
    return hashlib.sha256(_json_bytes(identity)).hexdigest()


@dataclass(frozen=True)
class Entry:
    directory: Path
    paths: list[Path]
    manifest: dict


def inspect_entry(directory: Path, identity: dict) -> Entry | None:
    """A corrupt manifest, missing stage or byte change is always a cache miss."""
    try:
        manifest = json.loads((directory / "manifest.json").read_text(encoding="utf-8"))
        if manifest["schema_version"] != SCHEMA_VERSION or manifest["identity"] != identity:
            return None
        if manifest["identity_sha256"] != identity_key(identity):
            return None
        parameters = identity["parameters"]
        names = [f"stage{k}.slut" for k in range(1, parameters["n_stages"] + 1)]
        if sorted(p.name for p in directory.glob("*.slut")) != names:
            return None
        if [record["file"] for record in manifest["models"]] != names:
            return None
        paths = [directory / name for name in names]
        for path, record in zip(paths, manifest["models"]):
            if path.stat().st_size != record["bytes"] or file_sha256(path) != record["sha256"]:
                return None
            model = io.load_sparse(path, competition=True)
            if model.m != parameters["m"] or record["m"] != model.m:
                return None
        return Entry(directory, paths, manifest)
    except (OSError, ValueError, KeyError, TypeError, OverflowError):
        return None


def lookup(variant_dir: Path, identity: dict) -> Entry | None:
    parent = variant_dir / identity_key(identity)
    if not parent.is_dir():
        return None
    # Concurrent publishers may produce multiple complete, equivalent batches.
    # Inspect whole batches; never combine individual stages from directories.
    for directory in sorted(parent.iterdir()):
        if directory.is_dir() and not directory.name.startswith("."):
            entry = inspect_entry(directory, identity)
            if entry is not None:
                return entry
    return None


def publish(variant_dir: Path, identity: dict, chain: list[io.SparseLut], fit_info: dict) -> Entry:
    parameters = identity["parameters"]
    if len(chain) != parameters["n_stages"]:
        raise ValueError("fitter returned the wrong stage count")
    for model in chain:
        io.validate_sparse(model, competition=True)
        if model.m != parameters["m"]:
            raise ValueError("fitter returned the wrong grid size")
    key = identity_key(identity)
    parent = variant_dir / key
    parent.mkdir(parents=True, exist_ok=True)
    # Same filesystem and a fresh destination make rename atomic on Windows/POSIX.
    # A process interruption before rename leaves only an ignored .pending batch.
    with tempfile.TemporaryDirectory(prefix=".pending-", dir=parent) as tmp:
        temporary = Path(tmp)
        records = []
        for stage, model in enumerate(chain, 1):
            path = temporary / f"stage{stage}.slut"
            io.save_sparse(path, model)
            with path.open("r+b") as stream:
                os.fsync(stream.fileno())
            records.append({"file": path.name, "bytes": path.stat().st_size,
                            "sha256": file_sha256(path), "m": model.m})
        manifest = {"schema_version": SCHEMA_VERSION, "identity_sha256": key,
                    "identity": identity, "models": records, "fit": fit_info,
                    "created_utc": dt.datetime.now(dt.timezone.utc).isoformat()}
        manifest_path = temporary / "manifest.json"
        with manifest_path.open("w", encoding="utf-8", newline="\n") as stream:
            json.dump(manifest, stream, indent=2, allow_nan=False)
            stream.write("\n")
            stream.flush()
            os.fsync(stream.fileno())
        if inspect_entry(temporary, identity) is None:
            raise RuntimeError("new model batch failed its integrity check")
        # If another process finished the same identity, reuse only its verified batch.
        if existing := lookup(variant_dir, identity):
            return existing
        destination = parent / f"batch-{uuid.uuid4().hex}"
        temporary.rename(destination)
    result = inspect_entry(destination, identity)
    if result is None:
        raise RuntimeError("published model batch failed its integrity check")
    return result
