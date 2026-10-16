"""One predeclared bin-capacity/lookahead/reachable-fit pilot, not a class survey.

Two new coupled controls compare legal node budgets; a third one-over-budget
control must decline the exact constructor. All have four distinct original
LUTs, with three different permutations whose composition is identity. The
existing stress-13 case tests the four new policies against frozen R27 evidence.
Baseline fits execute the byte-preserved R29 public fitter. New policies use the
same public parameters/cache factory as the integrated CLI. Exact model-byte
matches reuse full-cube numerical evidence; no fastest or official score claim.
"""
from __future__ import annotations

import argparse
from datetime import datetime,timezone
import hashlib
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import time
from types import SimpleNamespace

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/"python"));sys.path.insert(0,str(ROOT))
import numpy as np
from lutlab import axisbins,cache,casebook,cli,corpus,io,runtime,step,validation
from lutlab.entry import _write_report
from scripts.r29_strategy_matrix import probe_stats


def control_catalog():
    cases=[corpus._case("axis_bin_capacity",f"bins{n}",0,"regression",
        [corpus.op("coupled_steps",bins=n,seed=33000+n),corpus.op("permute",axes=[1,0,2]),
         corpus.op("permute",axes=[0,2,1]),corpus.op("permute",axes=[2,0,1])],
        ["coupled","discontinuous","finite_palette","capacity_boundary","four_distinct_sources","regression_control"],
        {"composite":"first_stage","first_stage_monotone_bins":n,"lower_hold_required_knots":n+1,
         "exact_bins_sufficient_m":n,"is_global_representation_lower_bound":False}) for n in (17,33,34)]
    return {"schema":1,"generator":corpus.generator_fingerprint(),"cases":cases,"images":[],
        "image_cohort_reference":"problem16-v1","official":False,
        "scope":"additional source controls; reuse existing image/probe cohorts without relabelling them as new images"}


def prepare(output,directory,catalog_path):
    definition=control_catalog()
    if catalog_path.exists() and json.loads(catalog_path.read_text(encoding="utf-8"))!=definition:
        raise RuntimeError("source extension catalog is immutable")
    _write_report(catalog_path,definition)
    for name in ("objects","recipes","cases"):(directory/name).mkdir(parents=True,exist_ok=True)
    result={"pass":False,"cases":[],"catalog_sha256":corpus.digest_file(catalog_path),"reused_images":True}
    for case in definition["cases"]:
        manifest=corpus.materialize_case(directory,case,definition["generator"])
        if manifest["composite"]["sha256"]!=manifest["stages"][0]["sha256"]:
            raise RuntimeError("the three different permutation sources do not compose to identity")
        folder=directory/"cases"/case["id"]
        tables=[io.load_full(folder/f"lut{k}.lut256",mmap=True) for k in range(1,5)]
        truth=io.load_full(folder/"composite.lut256",mmap=True)
        try:
            for begin in range(0,256,8):
                values=tables[0][begin:begin+8].copy()
                for table in tables[1:]:values=io.apply_full(table,values)
                if not np.array_equal(values,truth[begin:begin+8]):raise RuntimeError("new source full RGB composition failed")
        finally:
            for table in [*tables,truth]:table._mmap.close()
        result["cases"].append({"id":case["id"],"colors":256**3,"composition_pass":True})
    objects={path.name:corpus.digest_file(path) for path in (directory/"objects").glob("*.lut256")}
    if any(name!=digest+".lut256" for name,digest in objects.items()):raise RuntimeError("content-addressed extension object changed")
    result.update(pass_=True,verified_case_count=len(result["cases"]),source_objects=len(objects),
        unique_full_object_bytes=len(objects)*io.FULL_NBYTES,finished_utc=datetime.now(timezone.utc).isoformat())
    result["pass"]=result.pop("pass_");_write_report(directory/"inspection.json",result)
    _write_report(output/"source-inspection.json",result)
    print(f"[bins] prepared {len(result['cases'])} new four-source controls",flush=True)
    return definition


def new_entry(paths,name,m,profile,output,memo):
    args=SimpleNamespace(scenario=name,mode="seq",method=profile,m=m,grid="dp",adaptive=False,
        inputs=paths,model_dir=output/"models"/name/f"{profile}-m{m}",allow_composite=False,allow_residual=False)
    identity=cache.build_identity(paths,cli.fit_parameters(args));entry=cache.lookup(args.model_dir,identity)
    if entry is not None:return entry
    tables=[io.load_full(path,mmap=True) for path in paths]
    try:
        for table,source in zip(tables,identity["inputs"]):
            if hashlib.sha256(memoryview(table)).hexdigest()!=source["sha256"]:raise RuntimeError("source changed while opening")
        lookahead,reachable=axisbins.PROFILES[profile]
        chain,info=axisbins.fit_chain(tables,m,lookahead=lookahead,reachable=reachable,stage_cache=memo)
    finally:
        for table in tables:table._mmap.close()
    if cache.build_identity(paths,cli.fit_parameters(args))!=identity:raise RuntimeError("source/code changed during fit")
    return cache.publish(args.model_dir,identity,chain,info)


def baseline_entry(paths,name,m,output,frozen_root):
    destination=output/"baseline-models"/name/f"m{m}";log=output/"baseline-logs"/f"{name}-m{m}.log";log.parent.mkdir(exist_ok=True)
    params=dict(scenario=name,mode="seq",method="adaptive_full",m=m,grid="dp",adaptive=False,
        inputs=list(map(str,paths)),model_dir=str(destination),allow_composite=False,allow_residual=False)
    code="from pathlib import Path;from types import SimpleNamespace;import sys,json;from lutlab import cli;v=json.loads(sys.argv[1]);v['inputs']=[Path(x) for x in v['inputs']];e=cli.model_entry(SimpleNamespace(**v));print('R33_ENTRY='+str(e.directory))"
    environment={**os.environ,"PYTHONPATH":str(frozen_root/"python"),"GIT_CEILING_DIRECTORIES":str(ROOT),
        "JSHC_LOG_DIR":str(output/"baseline-runlogs")}
    command=[sys.executable,"-c",code,json.dumps(params)];started=time.perf_counter()
    process=subprocess.run(command,cwd=frozen_root,env=environment,capture_output=True,text=True,encoding="utf-8",errors="replace")
    log.write_text(process.stdout+process.stderr,encoding="utf-8")
    if process.returncode:raise RuntimeError("frozen baseline fitter failed; inspect "+str(log))
    line=next(line for line in reversed(process.stdout.splitlines()) if line.startswith("R33_ENTRY="))
    directory=Path(line[len("R33_ENTRY="):]);manifest=json.loads((directory/"manifest.json").read_text(encoding="utf-8"))
    entry=cache.inspect_entry(directory,manifest["identity"])
    if entry is None:raise RuntimeError("frozen baseline did not publish a verified batch")
    for name,digest in entry.manifest["identity"]["source_sha256"].items():
        path=frozen_root/name if name=="pixi.lock" else frozen_root/"python/lutlab"/name
        if corpus.digest_file(path)!=digest:raise RuntimeError("baseline cache belongs to a different source image")
    return entry,{"command":command,"returncode":0,"process_wall_seconds_not_benchmark":time.perf_counter()-started,
        "log_sha256":corpus.digest_file(log),"source_root":str(frozen_root)}


def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument("--output",type=Path,default=ROOT/"artifacts/r33-axis-bins")
    p.add_argument("--data",type=Path,default=ROOT/"data/corpus-axis-bins-v1")
    p.add_argument("--catalog",type=Path,default=ROOT/"datasets/problem16-axis-bins-v1/catalog.json")
    args=p.parse_args();args.output.mkdir(parents=True,exist_ok=True)
    lease=ROOT/"artifacts/r29-matrix/phase-controller.lock"
    with lease.open("x",encoding="utf-8") as stream:json.dump({"pid":os.getpid(),"owner":"R33 pilot canonical casebook writer"},stream)
    try:run(args)
    finally:lease.unlink()


def run(args):
    marker=json.loads((ROOT/"artifacts/r29-matrix/frozen-source.json").read_text(encoding="utf-8"));frozen_root=Path(marker["source_root"])
    for name,digest in marker["source_sha256"].items():
        if corpus.digest_file(frozen_root/name)!=digest:raise RuntimeError("frozen baseline image changed")
    source_names=["scripts/r33_axis_bins_study.py","python/lutlab/axisbins.py","python/lutlab/cache.py","python/lutlab/cascade.py",
        "python/lutlab/cli.py","python/lutlab/selection.py","python/lutlab/fit.py","python/lutlab/step.py","python/lutlab/io.py",
        "python/lutlab/interp.py","python/lutlab/casebook.py","scripts/r29_strategy_matrix.py"]
    sources={name:corpus.digest_file(ROOT/name) for name in source_names}
    definition=prepare(args.output,args.data,args.catalog)
    book=casebook.Casebook(ROOT/"datasets/problem16-v1/casebook");book.attach_catalog(args.catalog,args.data)
    historical_path=ROOT/"artifacts/r27-step/acceptance-stress-13-m33-adaptive.json"
    historical=json.loads(historical_path.read_text(encoding="utf-8"));source_hashes=[row["sha256"] for row in historical["sources"]]
    stress_id=next(name for name,case in book.index["cases"].items() if case["source_sha256"]==source_hashes)
    cases={case["intensity"]:case for case in definition["cases"]}
    configs=[(cases["bins17"]["id"],17,"adaptive_full"),(cases["bins17"]["id"],18,"adaptive_full"),
        (cases["bins33"]["id"],33,"adaptive_full")]
    configs += [(cases[label]["id"],m,profile) for label,m in (("bins17",17),("bins33",33))
        for profile in ("adaptive_bins","lookahead_reachable")]
    configs += [(stress_id,33,profile) for profile in axisbins.PROFILES]
    plan={"scope":__doc__,"configs":configs,"new_policy_profiles":axisbins.PROFILES,
        "frozen_R27_stress_baseline_reused":True,"measured_configurations":12,"new_full_screens_before_byte_dedup":11,
        "source_sha256":sources,"official":False,"class_sweet_zone_proven":False}
    _write_report(args.output/"pilot-plan.json",plan)
    report={"started_utc":datetime.now(timezone.utc).isoformat(),"source_sha256":sources,"scope":__doc__,"plan_sha256":corpus.digest_file(args.output/"pilot-plan.json"),
        "cases":[],"pass":False,"class_sweet_zone_proven":False,"timing_is_benchmark":False,"official":False,
        "baseline_source_image_sha256":marker["archive_sha256"],"reused_baseline":{
            "evidence":str(historical_path),"sha256":corpus.digest_file(historical_path),"case_id":stress_id,
            "models_sha256":historical["backends"]["cpu"]["model_sha256"],"cube":historical["backends"]["cpu"]["cube"]}}
    result=args.output/"study.json";_write_report(result,report)
    # One-over-budget is a constructor contract, not a silently omitted failed
    # accuracy candidate. This new case remains explicitly unmeasured in book.
    rejected=io.load_full(args.data/"cases"/cases["bins34"]["id"]/"lut1.lut256",mmap=True)
    try:
        detail={}
        if axisbins.exact_bins(rejected,33,diagnostics=detail) is not None:raise RuntimeError("one-over-budget constructor claimed exactness")
        report["one_over_budget_constructor"]=detail
    finally:rejected._mmap.close()
    cpu=ROOT/"build-r18-cpu/jshc.exe";gpu=ROOT/"build-r23-gpu/jshc_gpu.exe"
    binary_hashes={"cpu":corpus.digest_file(cpu),"cuda":corpus.digest_file(gpu)};report["binary_sha256"]=binary_hashes
    probe_def=json.loads((ROOT/"data/corpus-v1/probes.json").read_text(encoding="utf-8"))
    probes={name:np.load(ROOT/"data/corpus-v1/probes"/f"{name}.npy",allow_pickle=False,mmap_mode="r") for name in probe_def}
    memo={};screens={}
    for case_id,m,profile in configs:
        if case_id==stress_id:
            paths=[casebook._path(row["path"]) for row in historical["sources"]];truth_path=paths[0].parent/"composite.lut256"
        else:
            folder=args.data/"cases"/case_id;paths=[folder/f"lut{k}.lut256" for k in range(1,5)];truth_path=folder/"composite.lut256"
        hashes=[corpus.digest_file(path) for path in paths];truth_hash=corpus.digest_file(truth_path)
        if profile=="adaptive_full":entry,fit_execution=baseline_entry(paths,case_id,m,args.output,frozen_root)
        else:
            if "public_cli_fit" not in report:
                command=[sys.executable,"-m","lutlab","fit","--inputs",*map(str,paths),"--scenario",case_id,
                    "--m",str(m),"--method",profile,"--grid","dp","--model-dir",str(args.output/"models"/case_id/f"{profile}-m{m}")]
                execution=runtime._execute(command)
                (args.output/"public-cli-fit.log").write_text(execution["stdout"]+execution["stderr"],encoding="utf-8")
                if execution["returncode"]:raise RuntimeError("integrated public CLI candidate failed; inspect public-cli-fit.log")
                report["public_cli_fit"]={"command":command,"returncode":0,"profile":profile,
                    "log_sha256":corpus.digest_file(args.output/"public-cli-fit.log")}
            entry=new_entry(paths,case_id,m,profile,args.output,memo)
            fit_execution={"route":"same public cache/fit parameters; process-local source/geometry cache","returncode":0}
        model_hashes=[corpus.digest_file(path) for path in entry.paths]
        folder=args.output/"measurements"/case_id/f"{profile}-m{m}";folder.mkdir(parents=True,exist_ok=True)
        key=(tuple(hashes),truth_hash,tuple(model_hashes),tuple(binary_hashes.values()))
        if key in screens:
            previous=Path(screens[key]);primary=json.loads(previous.read_text(encoding="utf-8"))
            primary={**primary,"fit_execution":fit_execution,"reuse":{"evidence":str(previous),"sha256":corpus.digest_file(previous),
                "reason":"same four source/model bytes, reference and native binaries"}}
            quality=primary["cube"]
        else:
            with tempfile.TemporaryDirectory(prefix="r33-cube-") as temporary:
                temporary=Path(temporary);raw=temporary/"cpu.rgb";device=temporary/"cuda.rgb"
                execution=runtime.cube(entry.paths,raw,executable=cpu,kernel="tetra_avx2",threads=4,competition=True)
                cuda_execution=runtime.cube(entry.paths,device,backend="cuda",executable=gpu,competition=True)
                output_hash=corpus.digest_file(raw)
                if output_hash!=corpus.digest_file(device):raise RuntimeError("new strategy CPU/CUDA full RGB output differs")
                with validation._mapped_full(raw) as predicted,validation._mapped_full(truth_path) as truth:
                    quality=validation._cube_stats(predicted,truth,8,2.)
                    per_probe={name:probe_stats(predicted,truth,points) for name,points in probes.items()}
                primary={"kind":"casebook_native_cube_screen_v1","case_id":case_id,"source_sha256":hashes,"reference_sha256":truth_hash,
                    "runtime":execution,"cuda_runtime":cuda_execution,"output_sha256":output_hash,"cube":quality,"probes":per_probe,
                    "fit_execution":fit_execution,"image_path_qualification":False,"timing_is_benchmark":False,"inputs_unchanged":True,
                    "source_epoch":"R33 new policies; baseline fitter is the frozen R29 source image"}
        if [corpus.digest_file(path) for path in paths]!=hashes or corpus.digest_file(truth_path)!=truth_hash:raise RuntimeError("source/reference changed during screen")
        primary_path=folder/"screen.json";_write_report(primary_path,primary);screens.setdefault(key,str(primary_path))
        version=hashlib.sha256(corpus.canonical({k:v for k,v in entry.manifest["identity"].items() if k!="inputs"})).hexdigest()[:12]
        value={"case_id":case_id,"source_sha256":hashes,"semantics":"independent","correctness_pass":True,
            "strategy":profile+"@"+version,"profile":profile,"model_identity_sha256":entry.manifest["identity_sha256"],"m":[m]*4,
            "models":list(map(str,entry.paths)),"model_sha256":model_hashes,"kernel":"tetra_avx2",
            "node_payload_bytes":sum(io.load_sparse(path).nodes.nbytes for path in entry.paths),"cube":quality,
            "evidence":[{"path":str(primary_path),"sha256":corpus.digest_file(primary_path)}],"official":False}
        observation=folder/"observation.json";_write_report(observation,value);identifier=book.record(observation)
        report["cases"].append({"case_id":case_id,"profile":profile,"m":m,"observation_id":identifier,"observation":str(observation),
            "observation_sha256":corpus.digest_file(observation),"models":list(map(str,entry.paths)),"cube":quality,
            "node_payload_bytes":value["node_payload_bytes"],"fit_info":entry.manifest["fit"],"numerical_evidence_reused":"reuse" in primary})
        _write_report(result,report);_write_report(book.root/"summary.json",book.summary())
        print(f"[bins] {len(report['cases'])}/{len(configs)} {case_id}/{profile}/m{m}: mean={quality['mean']:.9f}, max={quality['max']:.9f}",flush=True)
    for case_id in (cases["bins17"]["id"],cases["bins33"]["id"]):
        for row in report["cases"]:
            if row["case_id"]==case_id and row["profile"]!="adaptive_full" and row["cube"]["max"]!=0:
                raise RuntimeError("new exact-bin capacity control was not exact")
    for name,digest in sources.items():
        if corpus.digest_file(ROOT/name)!=digest:raise RuntimeError("new-policy source changed during the pilot")
    if corpus.digest_file(cpu)!=binary_hashes["cpu"] or corpus.digest_file(gpu)!=binary_hashes["cuda"]:raise RuntimeError("native binary changed")
    report.update(pass_=True,finished_utc=datetime.now(timezone.utc).isoformat(),completed_new_measurements=len(configs),
        next_scope="all 200 original source cases, three sizes and independent source holdout before class sweet-zone claims")
    report["pass"]=report.pop("pass_");_write_report(result,report)
    print(json.dumps({"pass":True,"new_measurements":len(configs),"historical_baseline_reused":True,"class_sweet_zone_proven":False}))


if __name__=="__main__":main()
