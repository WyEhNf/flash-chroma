"""第二个独立小阶段：仅修正m17三处134，直接检查真实单调性，不扫描。"""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
import shutil
import sys
import zipfile

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT/"scripts"))
import run_filmic_calibration as base
import numba
import numpy as np
from PIL import Image
from lutlab import io, error_analysis as ea, runtime, study_provenance
from lutlab.compatibility import write_json


def sources(plan_path):
    return {**base.numerical_sources(plan_path), str(Path(__file__).relative_to(ROOT)).replace("\\", "/"): base.digest(__file__)}


def prepare(args, plan):
    if (args.output/"run.json").exists():
        raise ValueError("第二阶段已有运行身份，不覆盖")
    for spec in plan["parent_files"].values():
        base.checked(spec)
    base.checked(plan["source"])
    executable = base.checked(plan["executable"])
    source_map = sources(args.plan)
    identity = {"plan": plan, "source_sha256": source_map,
                "environment": study_provenance.environment_fingerprint(), "numba_threads": numba.get_num_threads()}
    study_provenance.claim_run(args.output/"run.json",
        {"identity": identity, "identity_sha256": study_provenance.identity_digest(identity)})
    with zipfile.ZipFile(args.output/"measured-source.zip", "w", zipfile.ZIP_DEFLATED) as archive:
        for name, sha in source_map.items():
            if base.digest(ROOT/name) != sha:
                raise ValueError("冻结源码改变")
            archive.write(ROOT/name, name)
    original = io.load_sparse(base.checked(plan["parent_files"]["original_model"]), competition=True)
    initial = io.load_sparse(base.checked(plan["parent_files"]["static_model"]), competition=True)
    if (not np.array_equal(original.nodes, initial.nodes) or not np.array_equal(original.grid, initial.grid)
            or not np.array_equal(original.tables()[0], initial.tables()[0])):
        raise AssertionError("前阶段固定字段不一致")
    idx, frac = initial.tables()
    changed = frac.astype(np.int64).copy()
    for move in plan["moves"]:
        if int(changed[move["axis"], move["input"]]) != move["before"]:
            raise ValueError("三处冻结前值不同")
        changed[move["axis"], move["input"]] = move["after"]
    q = idx.astype(np.int64)*io.ONE+changed
    monotone = bool(np.all(np.diff(q, axis=1) >= 0))
    within_shift = bool(np.all(np.abs(changed-original.tables()[1].astype(np.int64)) <= 4096))
    endpoints = bool(np.array_equal(changed[:, [0,255]], original.tables()[1][:, [0,255]]))
    curve_labels = np.load(base.checked(plan["parent_files"]["source_curves"]))
    candidate = io.SparseLut(initial.grid.copy(), initial.nodes.copy(), idx.copy(), changed.astype(np.uint32))
    values = base.curve_output(candidate)
    exact = bool(np.array_equal(values, curve_labels))
    neighbors = [{"axis": a, "inputs": [133,134,135],
                  "fraction": changed[a, 133:136].tolist(), "effective_q": q[a, 133:136].tolist()}
                 for a in range(3)]
    diagnostic = {"monotone": monotone, "within_original_shift4096": within_shift,
        "endpoints_unchanged": endpoints, "all_768_codes_exact": exact, "neighbors": neighbors,
        "largest_total_shift": int(np.abs(changed-original.tables()[1].astype(np.int64)).max()),
        "extra_changes_vs_static": int(np.count_nonzero(changed != frac)),
        "changes_vs_original": int(np.count_nonzero(changed != original.tables()[1])),
        "scope": "独立第二阶段放宽静态中点充分区间，保持真实单调、总偏移、idx/节点/grid/端点；非原静态计划成功"}
    write_json(args.output/"analysis.json", diagnostic)
    if not (monotone and within_shift and endpoints and exact):
        write_json(args.output/"preparation.json", {"eligible": False, "diagnostic": diagnostic,
                   "run_identity": study_provenance.identity_digest(identity)})
        print(json.dumps(diagnostic, ensure_ascii=False), flush=True)
        return
    io.save_sparse(args.output/"calibrated.slut", candidate)
    rng = np.random.default_rng(2026101909)
    probes = np.concatenate((rng.integers(0,256,size=(2048,3),dtype=np.uint8),
                             np.column_stack([np.arange(256,dtype=np.uint8)]*3)))
    np.testing.assert_array_equal(ea.Operator([candidate])(probes), base.integer_oracle(candidate, probes))
    np.testing.assert_array_equal(ea.Operator([candidate])(probes),
                                 np.column_stack([values[probes[:,a],a] for a in range(3)]))
    result = {"eligible": True, "run_identity": study_provenance.identity_digest(identity),
        "model_sha256": base.digest(args.output/"calibrated.slut"), "diagnostic": diagnostic,
        "oracle_probe_pixels": len(probes), "capabilities": runtime.capabilities(executable=executable)}
    write_json(args.output/"preparation.json", result)
    print(json.dumps(result, ensure_ascii=False), flush=True)


def accept(args, plan):
    run, prepared = base.read(args.output/"run.json"), base.read(args.output/"preparation.json")
    if (run["identity_sha256"] != study_provenance.identity_digest(run["identity"])
            or prepared["run_identity"] != run["identity_sha256"] or not prepared["eligible"]
            or sources(args.plan) != run["identity"]["source_sha256"] or (args.output/"full-results.json").exists()):
        raise ValueError("身份不同、候选不合格或已有完整结果")
    base.checked(plan["source"])
    for spec in plan["parent_files"].values():
        base.checked(spec)
    executable = base.checked(plan["executable"])
    path = args.output/"calibrated.slut"
    if base.digest(path) != prepared["model_sha256"]:
        raise ValueError("候选改变")
    model = io.load_sparse(path, competition=True)
    reference = np.load(base.checked(plan["parent_files"]["reference"]), mmap_mode="r")
    cube = base.full_cube(model, reference, args.output/"cube.rgb")
    if any(cube[k] != 0 for k in ("mean", "rms", "p99", "max")):
        raise AssertionError("完整色域未兑现逐码精确结论")
    native = []
    for kernel in prepared["capabilities"]["available_kernels"]:
        if not kernel.startswith("tetra_") or kernel in ("tetra_c99","tetra_structured_avx2"):
            continue
        output = args.output/"native.rgb"
        receipt = runtime.cube([path], output, executable=executable, kernel=kernel, threads=1)
        if base.digest(output) != cube["prediction_sha256"]:
            raise AssertionError("原生完整输出不同")
        native.append({**receipt, "sha256": base.digest(output), "byte_mismatches": 0})
    rows = base.read(base.checked({"path":plan["photos"]["manifest"],"sha256":plan["photos"]["manifest_sha256"]}))["images"]
    if len(rows) != 100:
        raise ValueError("不是冻结100图")
    operator, photo_rows, stream = ea.Operator([model]), [], hashlib.sha256()
    for row in rows:
        with Image.open(base.checked(row["evaluation"])) as image:
            if image.mode != "RGB" or image.size != (1024,768):
                raise ValueError("照片格式不同")
            rgb = np.asarray(image).reshape(-1,3)
        output = operator(rgb)
        truth = reference.reshape(-1,3)[base.rgb_keys(rgb)]
        np.testing.assert_array_equal(output, truth)
        photo_rows.append({"image":row["id"], **ea.metrics(output,truth)})
        stream.update(output.tobytes())
    listing = args.output/"photos.txt"
    listing.write_text("\n".join(str(ROOT/r["evaluation"]["path"]) for r in rows)+"\n",encoding="utf-8")
    output = args.output/"native-photos.rgb"
    receipt = runtime.verify([path], listing, executable=executable, kernel="tetra_avx2", threads=1, output=output)
    if base.digest(output) != stream.hexdigest():
        raise AssertionError("原生百图不同")
    parent = base.read(base.checked(plan["parent_files"]["full_results"]))
    result = {"run_identity":run["identity_sha256"],"model_sha256":prepared["model_sha256"],
        "cube":cube,"photos":{"n_images":100,"mean":0.,"rms":0.,"worst_image_p99":0.,"max":0.,"per_image":photo_rows},
        "native_cube":native,"native_photos":{**receipt,"sha256":base.digest(output),"byte_mismatches":0},
        "original_baseline":parent["sizes"]["17"]["baseline"]["cube"],
        "static_stage_calibrated":parent["sizes"]["17"]["calibrated"]["cube"],
        "scope":plan["limits"],"default_promoted":False}
    write_json(args.output/"full-results.json",result)
    print(json.dumps({"cube_mean":cube["mean"],"photos_mean":result["photos"]["mean"],
                      "native_kernels":[r["kernel"] for r in native]},ensure_ascii=False),flush=True)


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument("mode",choices=("prepare","accept"))
    args=parser.parse_args()
    args.output=Path(__file__).resolve().parent
    args.plan=args.output/"plan.json"
    numba.set_num_threads(4)
    (prepare if args.mode=="prepare" else accept)(args,base.read(args.plan))


if __name__=="__main__":
    main()
