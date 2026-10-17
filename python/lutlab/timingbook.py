"""Evidence-bound runtime choices for one exact model and resource cohort.

Point-estimate minima and pairwise demonstrated winners are separate. Different
benchmark epochs, models, thread counts or image cohorts never share a speed
group. Fitting/process-wall time is never an eligible mapping measurement.
"""
from __future__ import annotations

import hashlib
import math
from pathlib import Path
import statistics

from . import corpus, reportio


def normalize(path, case_label, configuration):
    from .casebook import _path
    path = _path(path)
    report = reportio.read_json(path)
    if not report["pass"] or not report["inputs_unchanged"] or report["pairs"] < 9:
        raise ValueError("runtime registration requires the completed paired gate")
    if not report["quiet_before"]["known_controller_and_children_terminal"] or not report["quiet_after"]["known_controller_and_children_terminal"]:
        raise ValueError("fitting was active during the mapping comparison")
    proof = next(row for row in report["preflight"] if row["case"] == case_label and row["configuration"] == configuration)
    native = proof["native_runtime"]
    models = list(native["models_sha256"].values())
    kernel = report["configurations"][configuration]
    if native["returncode"] or native["kernel"] != kernel or native["images"] != 100:
        raise ValueError("runtime preflight was not a complete native execution")
    rows = [row for row in report["runs"] if row["case"] == case_label and row["configuration"] == configuration]
    pairs = report["pairs"]
    comparisons = {tuple(row["comparison"]) for row in rows}
    if len(rows) != len(comparisons) * pairs or len({(tuple(row["comparison"]), row["pair"]) for row in rows}) != len(rows):
        raise ValueError("runtime measurements are incomplete or duplicated")
    for comparison in comparisons:
        if {row["pair"] for row in rows if tuple(row["comparison"]) == comparison} != set(range(pairs)):
            raise ValueError("missing AB/BA pair")
    for row in rows:
        value = row["runtime"]
        if (value["returncode"] or value["kernel"] != kernel or value["requested_threads"] != 16
                or not value["batch_mode"] or value["images"] != 100 or value["reps"] != 1
                or value["executable_sha256"] != native["executable_sha256"]
                or list(value["models_sha256"].values()) != models
                or row["host_to_host_ms"] != value["set_ms_p50_rep"]
                or not math.isfinite(row["host_to_host_ms"]) or row["host_to_host_ms"] <= 0):
            raise ValueError("runtime sample belongs to another model/resource/metric")
    listing = native["command"][native["command"].index("-l") + 1]
    cohort = report["input_and_binary_sha256"][listing]
    report_hash = corpus.digest_file(path)
    resources = {"backend": "cpu", "threads": 16, "batch": True, "image_list_sha256": cohort,
                 "executable_sha256": native["executable_sha256"], "benchmark_sha256": report_hash}
    group = hashlib.sha256(corpus.canonical({"resources": resources, "model_sha256": models, "case_label": case_label})).hexdigest()
    faster = []
    for comparison in report["comparisons"]:
        if comparison["case"] != case_label: continue
        if comparison["candidate"] == configuration and comparison["candidate_faster_holm_alpha_05"]:
            faster.append(comparison["reference"])
        if comparison["reference"] == configuration and comparison["reference_faster_holm_alpha_05"]:
            faster.append(comparison["candidate"])
    sizes = {row["runtime"]["model_runtime_bytes"] for row in rows}
    if len(sizes) != 1:
        raise ValueError("model-memory scope changed within a configuration")
    return {"kind": "paired_native_runtime_v1", "report": {"path": str(path), "sha256": report_hash},
            "case_label": case_label, "configuration": configuration, "model_sha256": models, "kernel": kernel,
            "resource_group": group, "resources": resources, "pairs": pairs,
            "median_set_ms": statistics.median(row["host_to_host_ms"] for row in rows),
            "model_runtime_bytes": sizes.pop(), "proven_faster_configurations": sorted(set(faster)),
            "inference_scope": "same exact four models and benchmark epoch only; Holm-adjusted direct comparisons"}


def validate(value):
    from .casebook import _path
    data = value["performance"]
    if data.get("kind") != "paired_native_runtime_v1":
        raise ValueError("unknown timing evidence kind")
    expected = normalize(data["report"]["path"], data["case_label"], data["configuration"])
    if data != expected or data["model_sha256"] != value["model_sha256"] or data["kernel"] != value["kernel"]:
        raise ValueError("normalized speed claim differs from actual native samples")
    if not any(item["sha256"] == data["report"]["sha256"] for item in value["evidence"]):
        raise ValueError("timing report is not bound to the immutable observation")
    primary = reportio.read_json(_path(value["evidence"][0]["path"]))
    execution = primary["runtime"]
    command = execution["command"]
    if (execution["executable_sha256"] != data["resources"]["executable_sha256"]
            or execution["backend"] != "cpu" or "-k" not in command
            or command[command.index("-k") + 1] != value["kernel"]):
        raise ValueError("quality and speed used different native builds")


def rank(rows):
    groups = {}
    for row in rows:
        value = row.get("performance")
        if value:
            groups.setdefault(value["resource_group"], {})[value["configuration"]] = row
    result = {}
    for group, candidates in groups.items():
        point = min(candidates.values(), key=lambda row: (row["performance"]["median_set_ms"], row["observation_id"]))
        names = set(candidates)
        proved = [row for name, row in candidates.items() if names - {name} <= set(row["performance"]["proven_faster_configurations"])] if len(names) > 1 else []
        def objectives(row):
            return row["performance"]["median_set_ms"], row["performance"]["model_runtime_bytes"]
        frontier = [row["observation_id"] for row in candidates.values() if not any(
            all(a <= b for a, b in zip(objectives(other), objectives(row))) and
            any(a < b for a, b in zip(objectives(other), objectives(row))) for other in candidates.values())]
        result[group] = {"best_observed_median": point["observation_id"],
            "proven_fastest_among_registered": proved[0]["observation_id"] if len(proved) == 1 else None,
            "resources": point["performance"]["resources"],
            "configurations": {name: row["observation_id"] for name, row in candidates.items()},
            "measured_time_memory_pareto": frontier,
            "scope": "one exact compressed model chain; no ranking across different accuracy or resource cohorts"}
    return result or None
