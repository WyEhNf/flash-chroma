"""Case-shard the byte-preserved R29 driver without changing numerical code.

The only two AST edits select declared case IDs and redirect the phase-index
path. All fitting, cache identity, probes, rounding and native commands stay in
the original driver. A shard never claims to complete the original phase.
"""
from __future__ import annotations

import argparse
import ast
import copy
import hashlib
import importlib.util
import json
from pathlib import Path
import sys


def digest(path):
    with Path(path).open("rb") as stream:
        return hashlib.file_digest(stream, "sha256").hexdigest()


def projection(driver):
    tree = ast.parse(driver.read_bytes(), filename=str(driver))
    original = ast.dump(tree, include_attributes=False)
    main = next(node for node in tree.body if isinstance(node, ast.FunctionDef) and node.name == "main")
    edits = []
    for node in main.body:
        if not isinstance(node, ast.Assign) or len(node.targets) != 1 or not isinstance(node.targets[0], ast.Name):
            continue
        name = node.targets[0].id
        if name == "cases":
            expected = ast.parse('cases=[c for c in definition["cases"] if c["split"]==args.phase]').body[0]
            if ast.dump(node, include_attributes=False) != ast.dump(expected, include_attributes=False):
                raise RuntimeError("unrecognized case selector; refuse an unreviewed driver")
            replacement = ast.parse('[c for c in definition["cases"] if c["split"]==args.phase and c["id"] in __r50_case_ids]', mode="eval").body
        elif name == "report_path":
            expected = ast.parse('report_path=args.output/f"{args.phase}.json"').body[0]
            if ast.dump(node, include_attributes=False) != ast.dump(expected, include_attributes=False):
                raise RuntimeError("unrecognized phase-index assignment")
            replacement = ast.Name(id="__r50_report_path", ctx=ast.Load())
        else:
            continue
        edits.append((node, copy.deepcopy(node.value)))
        node.value = ast.copy_location(replacement, node.value)
    if len(edits) != 2:
        raise RuntimeError("exactly two scheduling/I/O assignments must change")
    projected = copy.deepcopy(tree)
    for node, previous in edits:
        node.value = previous
    if ast.dump(tree, include_attributes=False) != original:
        raise RuntimeError("undoing the two nonnumeric edits did not reproduce the original AST")
    return ast.fix_missing_locations(projected), hashlib.sha256(original.encode()).hexdigest()


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--job", type=Path, required=True)
    args = parser.parse_args()
    job_bytes = args.job.read_bytes()
    job = json.loads(job_bytes)
    source = Path(job["source_root"]).resolve()
    marker = json.loads((source / "frozen-source.json").read_bytes())
    if not marker["pass"] or marker["archive_sha256"] != job["numerical_source_image_sha256"]:
        raise RuntimeError("job source image differs")
    for name, expected in marker["source_sha256"].items():
        if digest(source / name) != expected:
            raise RuntimeError("frozen source image changed")
    wrapper = Path(__file__).resolve()
    io_path = Path(job["reportio"])
    if digest(wrapper) != job["worker_sha256"] or digest(io_path) != job["reportio_sha256"]:
        raise RuntimeError("declared scheduling/I/O wrapper changed")
    spec = importlib.util.spec_from_file_location("r50_declared_reportio", io_path)
    publisher = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(publisher)
    sys.path.insert(0, str(source / "python"))
    sys.path.insert(1, str(source))
    from lutlab import entry
    driver = source / "scripts/r29_strategy_matrix.py"
    code, ast_hash = projection(driver)
    plan = json.loads(Path(job["plan"]).read_bytes())
    catalog = json.loads(Path(job["catalog"]).read_bytes())
    phase_ids = {c["id"] for c in catalog["cases"] if c["split"] == job["phase"]}
    assigned = set(job["case_ids"])
    if not assigned or not assigned <= phase_ids or len(assigned) != len(job["case_ids"]):
        raise RuntimeError("undeclared, duplicate or cross-split shard case")
    per_case = len(plan["profiles"]) * len(plan["sizes"])
    index_path = Path(job["index_path"]).resolve()
    overlay = {"kind": "case_partition_and_index_path_only_v1", "job_sha256": hashlib.sha256(job_bytes).hexdigest(),
               "worker_sha256": job["worker_sha256"], "reportio_sha256": job["reportio_sha256"],
               "driver_sha256": digest(driver), "original_ast_sha256": ast_hash,
               "changed_assignments": ["cases", "report_path"], "case_ids": sorted(assigned),
               "numerical_source_image_sha256": marker["archive_sha256"]}

    def publish(path, value):
        if Path(path).resolve() == index_path:
            if value["phase_expected_candidates"] != per_case * len(assigned):
                raise RuntimeError("shard denominator changed")
            value = {**value, "shard_expected_candidates": per_case * len(assigned),
                     "shard_complete": value["phase_complete"], "phase_complete": False,
                     "phase_expected_candidates": per_case * len(phase_ids), "scheduling_overlay": overlay}
        publisher.write_report(path, value)

    entry._write_report = publish
    forwarded = ["--phase", job["phase"], "--output", job["matrix"], "--casebook", job["casebook"],
                 "--plan", job["plan"], "--catalog", job["catalog"], "--data", job["data"], "--cpu", job["cpu"],
                 "--max-candidates", "0"]
    if job.get("class_rule"):
        forwarded += ["--class-rule", job["class_rule"]]
    sys.argv = [str(driver), *forwarded]
    namespace = {"__name__": "__main__", "__file__": str(driver), "__package__": None,
                 "__r50_case_ids": frozenset(assigned), "__r50_report_path": index_path}
    exec(compile(code, str(driver), "exec"), namespace)
    if args.job.read_bytes() != job_bytes or digest(wrapper) != job["worker_sha256"] or digest(io_path) != job["reportio_sha256"]:
        raise RuntimeError("scheduling/I/O definition changed during execution")


if __name__ == "__main__":
    main()
