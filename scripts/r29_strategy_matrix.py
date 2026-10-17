"""Resume the complete predeclared matrix, serially, without shrinking its scope.

Each successful observation executes an actual native full RGB8 cube. Image
decoding qualification and paired performance are separate later stages. The
holdout phase requires a frozen class rule; an interrupted/limited run remains
incomplete and resumes only with matching dataset, strategy and source hashes.
"""
from __future__ import annotations

import argparse
from datetime import datetime, timezone
import hashlib
import json
import os
from pathlib import Path
import sys
import tempfile
import time
from types import SimpleNamespace

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/"python"))
import numpy as np
from lutlab import cache,casebook,cli,corpus,fullfit,io,runtime,selection,validation
from lutlab.entry import _write_report


def probe_stats(predicted,truth,points):
    pred=io.apply_full(predicted,points);target=io.apply_full(truth,points)
    squared=validation._squared_error(pred,target)
    hist=np.bincount(squared,minlength=3*255**2+1)
    cumulative=np.cumsum(hist);n=len(points);roots=np.sqrt(np.arange(len(hist),dtype=np.float64))
    rank=.99*(n-1);low,high=int(np.floor(rank)),int(np.ceil(rank))
    a,b=np.searchsorted(cumulative,[low+1,high+1])
    return {"n_colors":n,"mean":float(hist@roots/n),"rms":float(np.sqrt(hist@np.arange(len(hist),dtype=np.float64)/n)),
        "p99":float(roots[a]+(rank-low)*(roots[b]-roots[a])),"max":float(roots[np.flatnonzero(hist)[-1]])}


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--plan",type=Path,default=ROOT/"datasets/problem16-v1/strategy-plan.json")
    parser.add_argument("--catalog",type=Path,default=ROOT/"datasets/problem16-v1/catalog.json")
    parser.add_argument("--data",type=Path,default=ROOT/"data/corpus-v1")
    parser.add_argument("--casebook",type=Path,default=ROOT/"datasets/problem16-v1/casebook")
    parser.add_argument("--output",type=Path,default=ROOT/"artifacts/r29-matrix")
    parser.add_argument("--cpu",type=Path,default=ROOT/"build-r18-cpu/jshc.exe")
    parser.add_argument("--phase",choices=["development","calibration","regression","holdout"],default="development")
    parser.add_argument("--class-rule",type=Path)
    parser.add_argument("--max-candidates",type=int,default=0,help="bounded work chunk; does not redefine full plan completion")
    args=parser.parse_args()
    if args.max_candidates<0:parser.error("negative candidate work limit")
    plan=json.loads(args.plan.read_text());definition=json.loads(args.catalog.read_text())
    if corpus.digest_file(args.catalog)!=plan["catalog_sha256"] or definition["generator"]!=corpus.generator_fingerprint():
        raise RuntimeError("dataset definition or generator changed")
    inspected=json.loads((args.data/"inspection.json").read_text())
    if not inspected["pass"] or inspected["verified_case_count"]!=len(definition["cases"]):
        raise RuntimeError("complete corpus inspection is required before strategy comparisons")
    if args.phase=="holdout" and args.class_rule is None:parser.error("holdout requires a frozen --class-rule")
    if args.class_rule:
        rule=json.loads(args.class_rule.read_text())
        if rule["plan_sha256"]!=corpus.digest_file(args.plan) or not rule["frozen_before_holdout"]:
            raise RuntimeError("class rule is not bound to the predeclared plan")
    for name,parameters in plan["profiles"].items():
        if list(selection.PROFILES[name])!=parameters or parameters[0]!="seq":raise RuntimeError("strategy definition changed")
    cpu=args.cpu.resolve();args.output.mkdir(parents=True,exist_ok=True)
    os.environ.update(OPENBLAS_NUM_THREADS="1",MKL_NUM_THREADS="1",OMP_NUM_THREADS="1",OMP_DYNAMIC="FALSE",OMP_THREAD_LIMIT="32",
        JSHC_BIN=str(cpu),JSHC_FULL_FIT_LIB=str(fullfit.resolve_library()))
    os.environ["PYTHONPATH"]=os.pathsep.join([str(ROOT/"python"),str(ROOT/"artifacts/r18-tools/python")])
    sources={f"python/lutlab/{name}":digest for name,digest in cache.source_fingerprint().items() if name!="pixi.lock"}
    for name in ("python/lutlab/corpus.py","python/lutlab/casebook.py","python/lutlab/runtime.py","python/lutlab/validation.py",
                 "python/lutlab/entry.py","python/lutlab/selection.py",str(Path(__file__).relative_to(ROOT))):
        sources[name]=corpus.digest_file(ROOT/name)
    frozen={"plan_sha256":corpus.digest_file(args.plan),"catalog_sha256":corpus.digest_file(args.catalog),
        "inspection_sha256":corpus.digest_file(args.data/"inspection.json"),"executable_sha256":corpus.digest_file(cpu),
        "source_sha256":sources,"trainer":fullfit.trainer_fingerprint(),"phase":args.phase,
        "class_rule_sha256":corpus.digest_file(args.class_rule) if args.class_rule else None}
    report_path=args.output/f"{args.phase}.json"
    if report_path.exists():
        report=json.loads(report_path.read_text())
        if report["frozen"]!=frozen:raise RuntimeError("resume source/dataset differs; preserve prior results and create a new epoch")
    else:report={"started_utc":datetime.now(timezone.utc).isoformat(),"frozen":frozen,"observations":{},"phase_complete":False,
        "full_plan_candidates":plan["total_candidates"],"official":False,"scope":__doc__}
    book=casebook.Casebook(args.casebook);book.attach_catalog(args.catalog,args.data)
    for item in report["observations"].values():
        path=casebook._path(item["path"])
        if corpus.digest_file(path)!=item["sha256"]:raise RuntimeError("completed observation changed; restore its evidence before resuming")
        if item["status"]=="screened" and book.record(path)!=item["observation_id"]:
            raise RuntimeError("completed observation no longer has the same model/evidence identity")
    probes=json.loads((args.data/"probes.json").read_text())
    points={name:np.load(args.data/"probes"/f"{name}.npy",mmap_mode="r",allow_pickle=False) for name in probes}
    cases=[c for c in definition["cases"] if c["split"]==args.phase]
    if set(plan["case_ids"])!={c["id"] for c in definition["cases"]}:raise RuntimeError("plan omits or adds catalog cases")
    expected_keys={f"{case['id']}/{profile}/m{m}" for case in cases for m in plan["sizes"] for profile in plan["profiles"]}
    if set(report["observations"])-expected_keys:raise RuntimeError("saved phase has observations outside the predeclared matrix")
    report["phase_expected_candidates"]=len(expected_keys)
    _write_report(report_path,report);performed=0

    def check_source():
        for name,digest in sources.items():
            if corpus.digest_file(ROOT/name)!=digest:raise RuntimeError(f"source changed during matrix: {name}")
        if corpus.digest_file(cpu)!=frozen["executable_sha256"] or fullfit.trainer_fingerprint()!=frozen["trainer"]:
            raise RuntimeError("native executable or fitting library changed during matrix")

    for case in cases:
        folder=args.data/"cases"/case["id"];manifest=json.loads((folder/"manifest.json").read_text())
        if manifest["spec_sha256"]!=hashlib.sha256(corpus.canonical(case)).hexdigest():raise RuntimeError("case metadata does not describe the materialized source")
        source_paths=[folder/f"lut{k}.lut256" for k in range(1,5)]
        source_hashes=[item["sha256"] for item in manifest["stages"]]
        for path,digest in zip(source_paths,source_hashes):
            if corpus.digest_file(path)!=digest:raise RuntimeError("case source changed since data inspection")
        truth_path=folder/"composite.lut256"
        if corpus.digest_file(truth_path)!=manifest["composite"]["sha256"]:raise RuntimeError("case truth changed")
        for m in plan["sizes"]:
            for profile,(mode,method,grid,kernel) in plan["profiles"].items():
                key=f"{case['id']}/{profile}/m{m}"
                if key in report["observations"]:continue
                if args.max_candidates and performed>=args.max_candidates:
                    report["last_chunk_finished_utc"]=datetime.now(timezone.utc).isoformat();_write_report(report_path,report);return
                check_source();performed+=1
                destination=args.output/"cases"/case["id"]/f"{profile}-m{m}"
                destination.mkdir(parents=True,exist_ok=True)
                models_dir=destination/"models"
                command=[sys.executable,"-m","lutlab","fit","--inputs",*map(str,source_paths),"--scenario",case["id"],
                    "--m",str(m),"--method",method,"--grid",grid,"--model-dir",str(models_dir)]
                fit_execution=runtime._execute(command)
                (destination/"fit.log").write_text(fit_execution["stdout"]+fit_execution["stderr"],encoding="utf-8")
                failure={"case_id":case["id"],"source_sha256":source_hashes,"strategy":profile,"m":[m]*4,
                    "frozen":frozen,"fit_execution":{k:v for k,v in fit_execution.items() if k not in ("stdout","stderr")}}
                if fit_execution["returncode"]:
                    path=destination/"failure.json";_write_report(path,{**failure,"status":"fit_failure"})
                    book.record_failure(path);report["observations"][key]={"status":"fit_failure","path":str(path),"sha256":corpus.digest_file(path)}
                    _write_report(report_path,report);print(f"[matrix] {key}: fit_failure",flush=True);continue
                args_fit=SimpleNamespace(scenario=case["id"],mode="seq",method=method,m=m,grid=grid,adaptive=False,
                    inputs=source_paths,model_dir=models_dir,allow_composite=False,allow_residual=False)
                entry=cli.model_entry(args_fit,existing_only=True)
                if entry is None:raise RuntimeError("public fitter did not publish an inspectable model batch")
                models=entry.paths
                actual_kernel="tetra_avx2" if kernel=="auto" else kernel
                with tempfile.TemporaryDirectory(prefix="casebook-screen-") as temporary:
                    raw=Path(temporary)/"cube.rgb"
                    try:
                        execution=runtime.cube(models,raw,executable=cpu,kernel=actual_kernel,threads=4,competition=True)
                    except runtime.BackendError as error:
                        path=destination/"failure.json";_write_report(path,{**failure,"status":"execution_failure","runtime":error.record})
                        book.record_failure(path);report["observations"][key]={"status":"execution_failure","path":str(path),"sha256":corpus.digest_file(path)}
                        _write_report(report_path,report);continue
                    if raw.stat().st_size!=io.FULL_NBYTES:raise RuntimeError("native cube output size differs")
                    with validation._mapped_full(raw) as prediction,validation._mapped_full(truth_path) as truth:
                        quality=validation._cube_stats(prediction,truth,8,2.)
                        per_probe={name:probe_stats(prediction,truth,array) for name,array in points.items()}
                    output_sha=corpus.digest_file(raw)
                check_source()
                if corpus.digest_file(truth_path)!=manifest["composite"]["sha256"]:
                    raise RuntimeError("truth changed before publishing an observation")
                primary={"kind":"casebook_native_cube_screen_v1","case_id":case["id"],"source_sha256":source_hashes,
                    "reference_sha256":manifest["composite"]["sha256"],"runtime":execution,"output_sha256":output_sha,
                    "cube":quality,"probes":per_probe,"inputs_unchanged":all(corpus.digest_file(path)==digest for path,digest in zip(source_paths,source_hashes)),
                    "fit_execution":failure["fit_execution"],"fit_observed_s":entry.manifest["fit"]["fit_s"],
                    "image_path_qualification":False,"timing_is_benchmark":False,"frozen":frozen}
                primary_path=destination/"screen.json";_write_report(primary_path,primary)
                algorithm_version=hashlib.sha256(corpus.canonical({k:v for k,v in entry.manifest["identity"].items() if k!="inputs"})).hexdigest()[:12]
                value={"case_id":case["id"],"source_sha256":source_hashes,"semantics":"independent","correctness_pass":True,
                    "strategy":profile+"@"+algorithm_version,"profile":profile,"model_identity_sha256":entry.manifest["identity_sha256"],
                    "m":[m]*4,"models":list(map(str,models)),
                    "model_sha256":[corpus.digest_file(p) for p in models],"kernel":actual_kernel,
                    "node_payload_bytes":sum(io.load_sparse(p).nodes.nbytes for p in models),"cube":quality,
                    "evidence":[{"path":str(primary_path),"sha256":corpus.digest_file(primary_path)}],"official":False}
                observation=destination/"observation.json";_write_report(observation,value)
                observation_id=book.record(observation)
                report["observations"][key]={"status":"screened","observation_id":observation_id,"path":str(observation),
                    "sha256":corpus.digest_file(observation),"cube_mean":quality["mean"],"cube_max":quality["max"]}
                _write_report(report_path,report)
                print(f"[matrix] {len(report['observations'])}/{report['phase_expected_candidates']} {key}: mean={quality['mean']:.6f}, max={quality['max']:.6f}",flush=True)
        if corpus.digest_file(truth_path)!=manifest["composite"]["sha256"]:raise RuntimeError("truth changed during case")
    check_source();report.update(phase_complete=set(report["observations"])==expected_keys,
        finished_utc=datetime.now(timezone.utc).isoformat(),finished_candidates=len(report["observations"]))
    _write_report(report_path,report);_write_report(args.casebook/"summary.json",book.summary())


if __name__=="__main__":main()
