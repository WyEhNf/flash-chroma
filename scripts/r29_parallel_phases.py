"""Run independent baseline phases as isolated processes, with one casebook writer.

No subagents and no performance measurements. Each fitter uses the frozen R29
driver and its own casebook. The parent imports immutable observations serially
into the canonical casebook. Sizes/profiles/total plan remain unchanged; bounded
chunks stop work, not the denominator. Holdout still requires frozen class rules.
"""
from __future__ import annotations

import argparse
from datetime import datetime,timezone
import json
import os
from pathlib import Path
import subprocess
import sys
import time
import uuid
import signal

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/"python"))
from lutlab import casebook,corpus
from lutlab.entry import _write_report


def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument("--matrix",type=Path,default=ROOT/"artifacts/r29-matrix")
    p.add_argument("--casebook",type=Path,default=ROOT/"datasets/problem16-v1/casebook")
    p.add_argument("--phases",nargs="+",choices=["development","calibration","regression","holdout"],
        default=["development","calibration","regression"])
    p.add_argument("--max-new-per-phase",type=int,default=135,help="0 means finish each whole phase; does not change the full 5400 plan")
    p.add_argument("--class-rule",type=Path)
    p.add_argument("--source-root",type=Path,help="verified raw R29 source image; keeps the original numerical epoch while main development continues")
    args=p.parse_args()
    if args.max_new_per_phase<0 or len(set(args.phases))!=len(args.phases):p.error("invalid phase work limit or duplicate phase")
    if "holdout" in args.phases and args.class_rule is None:p.error("holdout requires --class-rule")
    source_root=args.source_root.resolve() if args.source_root else ROOT
    source_image=None
    if args.source_root:
        source_image=json.loads((source_root/"frozen-source.json").read_text(encoding="utf-8"))
        if not source_image["pass"]:raise RuntimeError("frozen source image did not pass its identity check")
        for name,digest in source_image["source_sha256"].items():
            if corpus.digest_file(source_root/name)!=digest:raise RuntimeError("frozen source was edited")
    args.matrix.mkdir(parents=True,exist_ok=True)
    lock=args.matrix/"phase-controller.lock"
    epoch=uuid.uuid4().hex[:12];folder=args.matrix/"controllers"/epoch;folder.mkdir(parents=True)
    report={"started_utc":datetime.now(timezone.utc).isoformat(),"scope":__doc__,"controller_pid":os.getpid(),
        "source_sha256":{n:corpus.digest_file(ROOT/n) for n in ("scripts/r29_parallel_phases.py","scripts/r29_strategy_matrix.py","python/lutlab/casebook.py")},
        "full_plan_candidates":5400,"max_new_per_phase":args.max_new_per_phase,"children":{},"merged_observations":0,
        "pass":False,"full_user_goal_complete":False,"timing_is_benchmark":False}
    if source_image:report["frozen_source_image"]={"root":str(source_root),"archive_sha256":source_image["archive_sha256"],
        "public_cache_identity_probe":source_image["public_cache_identity_probe"]}
    path=folder/"controller.json";_write_report(path,report)
    children={};logs=[];seen={};book=casebook.Casebook(args.casebook)
    def collect():
        added=0;counts={}
        for phase in args.phases:
            matrix=args.matrix/f"{phase}.json"
            if not matrix.exists():continue
            state=json.loads(matrix.read_text(encoding="utf-8"));counts[phase]=len(state["observations"])
            for key,item in state["observations"].items():
                identity=(phase,key)
                if identity in seen:
                    if seen[identity]!=item["sha256"]:raise RuntimeError("a completed worker observation changed")
                    continue
                evidence=casebook._path(item["path"])
                if corpus.digest_file(evidence)!=item["sha256"]:raise RuntimeError("worker evidence hash differs")
                if item["status"]=="screened":
                    if book.record(evidence)!=item["observation_id"]:raise RuntimeError("worker observation identity differs")
                else:book.record_failure(evidence)
                seen[identity]=item["sha256"];added+=1
        if added:
            report["merged_observations"]=len(seen);report["phase_observations"]=counts
            _write_report(book.root/"summary.json",book.summary())
            _write_report(path,report)
            print("[phases] verified/imported "+json.dumps(counts)+"; full plan 5400",flush=True)
    # A stale lock is never assumed dead: inspect its process before removing it.
    with lock.open("x",encoding="utf-8") as f:json.dump({"pid":os.getpid(),"started_utc":datetime.now(timezone.utc).isoformat()},f)
    try:
        book=casebook.Casebook(args.casebook)
        collect()
        for phase in args.phases:
            matrix=args.matrix/f"{phase}.json"
            if matrix.exists() and json.loads(matrix.read_text(encoding="utf-8"))["phase_complete"]:
                report["children"][phase]={"status":"already_complete","returncode":0};continue
            namespace=source_image["archive_sha256"][:16] if source_image else "main-source"
            worker=args.matrix/"worker-casebooks"/namespace/phase
            command=[sys.executable,str(source_root/"scripts/r29_strategy_matrix.py"),"--phase",phase,
                "--output",str(args.matrix),"--casebook",str(worker),"--max-candidates",str(args.max_new_per_phase)]
            command.extend(["--plan",str(ROOT/"datasets/problem16-v1/strategy-plan.json"),"--catalog",str(ROOT/"datasets/problem16-v1/catalog.json"),
                "--data",str(ROOT/"data/corpus-v1"),"--cpu",str(ROOT/"build-r18-cpu/jshc.exe")])
            if args.class_rule:command.extend(["--class-rule",str(args.class_rule)])
            log=folder/f"{phase}.log";handle=log.open("wb");logs.append(handle)
            environment=os.environ.copy()
            if source_image:
                environment.update(PYTHONPATH=str(source_root/"python"),GIT_CEILING_DIRECTORIES=str(ROOT),
                    JSHC_LOG_DIR=str(args.matrix/"frozen-runlogs"/phase))
            process=subprocess.Popen(command,cwd=source_root,stdout=handle,stderr=subprocess.STDOUT,env=environment,
                start_new_session=os.name!="nt")
            children[phase]=process;report["children"][phase]={"pid":process.pid,"command":command,"log":str(log),"status":"running"}
        _write_report(path,report)
        while any(process.poll() is None for process in children.values()):
            collect()
            for phase,process in children.items():
                if process.poll() is not None:report["children"][phase].update(status="terminal",returncode=process.returncode)
            _write_report(path,report);time.sleep(3)
        collect()
        for phase,process in children.items():report["children"][phase].update(status="terminal",returncode=process.returncode)
        for name,digest in report["source_sha256"].items():
            if corpus.digest_file(ROOT/name)!=digest:raise RuntimeError("controller/driver source changed during execution")
        report.update(finished_utc=datetime.now(timezone.utc).isoformat(),pass_=all(x["returncode"]==0 for x in report["children"].values()))
        report["pass"]=report.pop("pass_");_write_report(path,report)
        if not report["pass"]:raise RuntimeError("a worker stopped unexpectedly; preserve partial results and inspect its terminal log")
        print(json.dumps({"controller_chunk_pass":True,"phase_observations":report.get("phase_observations",{}),"full_plan_candidates":5400}))
    finally:
        # Do not leave fitting processes running after a controller failure.
        for process in children.values():
            if process.poll() is None:
                if os.name=="nt":
                    subprocess.run(["taskkill","/PID",str(process.pid),"/T","/F"],stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL)
                else:os.killpg(process.pid,signal.SIGTERM)
                process.wait()
        for handle in logs:handle.close()
        lock.unlink()


if __name__=="__main__":main()
