"""Freeze descriptive family rules before any holdout strategy observations.

Rules compare all nine predeclared profiles at the same m. A profile is eligible
only when both development/calibration cases have valid full-cube observations.
This is a class-label guide, not an automatic classifier for unknown official LUTs.
"""
from __future__ import annotations

import argparse
from collections import defaultdict
from datetime import datetime,timezone
import json
import os
from pathlib import Path
import statistics
import sys

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/"python"))
from lutlab import corpus
from lutlab.entry import _write_report


def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument("--matrix",type=Path,default=ROOT/"artifacts/r29-matrix")
    p.add_argument("--catalog",type=Path,default=ROOT/"datasets/problem16-v1/catalog.json")
    p.add_argument("--plan",type=Path,default=ROOT/"datasets/problem16-v1/strategy-plan.json")
    p.add_argument("--output",type=Path,default=ROOT/"datasets/problem16-v1/class-rules.json")
    p.add_argument("--source-root",type=Path,help="verified numerical R29 source image after main-tree development advances")
    args=p.parse_args()
    lock=args.matrix/"phase-controller.lock"
    with lock.open("x",encoding="utf-8") as stream:
        json.dump({"pid":os.getpid(),"owner":"R29 immutable class rule freeze"},stream)
    try:freeze(args)
    finally:lock.unlink()


def freeze(args):
    plan=json.loads(args.plan.read_text());catalog=json.loads(args.catalog.read_text())
    source_root=args.source_root.resolve() if args.source_root else ROOT
    source_image=None
    if args.source_root:
        source_image=json.loads((source_root/"frozen-source.json").read_text(encoding="utf-8"))
        if not source_image["pass"]:raise RuntimeError("numerical source image was not verified")
        for name,digest in source_image["source_sha256"].items():
            if corpus.digest_file(source_root/name)!=digest:raise RuntimeError("numerical source image changed")
    previous=json.loads(args.output.read_text()) if args.output.exists() else None
    lookup={c["id"]:c for c in catalog["cases"]};groups=defaultdict(lambda:defaultdict(list));failures=[];parents={};frozen=None
    holdout=args.matrix/"holdout.json"
    if previous is None and holdout.exists() and json.loads(holdout.read_text()).get("observations"):
        raise RuntimeError("holdout already observed; cannot claim a new rule was frozen before it")
    for phase in ("development","calibration"):
        path=args.matrix/f"{phase}.json";report=json.loads(path.read_text())
        if not report["phase_complete"]:raise RuntimeError("both full training phases must complete before rule freeze")
        fingerprint={k:v for k,v in report["frozen"].items() if k not in ("phase","class_rule_sha256")}
        if fingerprint["plan_sha256"]!=corpus.digest_file(args.plan) or fingerprint["catalog_sha256"]!=corpus.digest_file(args.catalog):
            raise RuntimeError("training phase belongs to another dataset or plan")
        if frozen is not None and fingerprint!=frozen:raise RuntimeError("training phases used different code or hardware")
        for name,digest in fingerprint["source_sha256"].items():
            if corpus.digest_file(source_root/name)!=digest:raise RuntimeError("training source differs from the selected numerical source image")
        frozen=fingerprint;parents[str(path)]=corpus.digest_file(path)
        for key,item in report["observations"].items():
            case_id,profile,budget=key.split("/");case=lookup[case_id]
            if case["split"]!=phase:raise RuntimeError("training observation leaked from another split")
            if item["status"]!="screened":failures.append({"key":key,"status":item["status"]});continue
            observation=Path(item["path"])
            if corpus.digest_file(observation)!=item["sha256"]:raise RuntimeError("training evidence changed")
            value=json.loads(observation.read_text())
            groups[(case["family"],case["intensity"],budget)][profile].append(value["cube"])
    rules={}
    for (family,intensity,budget),strategies in groups.items():
        eligible={profile:values for profile,values in strategies.items() if len(values)==2}
        if not eligible:raise RuntimeError("no profile has both class training cases")
        mean=min(eligible,key=lambda profile:(statistics.mean(v["mean"] for v in eligible[profile]),profile))
        tail=min(eligible,key=lambda profile:(max(v["max"] for v in eligible[profile]),profile))
        rules[f"{family}/{intensity}/{budget}"]={"mean_profile":mean,"max_profile":tail,
            "eligible_profiles":sorted(eligible),"cases_per_profile":2,
            "mean_metrics":{profile:statistics.mean(v["mean"] for v in values) for profile,values in eligible.items()},
            "interpretation":"two source seeds only; evaluate regret on the unseen source seed, not a confidence guarantee"}
    expected_groups=20*3*len(plan["sizes"])
    if len(rules)!=expected_groups:raise RuntimeError("class rule coverage is incomplete")
    result={"schema":1,"scope":__doc__,"frozen_utc":previous["frozen_utc"] if previous else datetime.now(timezone.utc).isoformat(),"frozen_before_holdout":True,
        "source_sha256":{str(Path(__file__).relative_to(ROOT)):corpus.digest_file(Path(__file__))},
        "plan_sha256":corpus.digest_file(args.plan),"catalog_sha256":corpus.digest_file(args.catalog),
        "training_reports_sha256":parents,"frozen_training_environment":frozen,
        "rules":rules,"failed_training_observations":failures,"official":False}
    if source_image:result["numerical_source_image_sha256"]=source_image["archive_sha256"]
    if previous is not None:
        if previous!=result:raise RuntimeError("preserve previous frozen rules; choose a new output epoch")
        if holdout.exists():
            report=json.loads(holdout.read_text())
            if report.get("observations") and report["frozen"]["class_rule_sha256"]!=corpus.digest_file(args.output):
                raise RuntimeError("holdout used another frozen rule")
    else:_write_report(args.output,result)
    print(json.dumps({"class_budget_rules":len(rules),"frozen_before_holdout":True,"reused":previous is not None}))


if __name__=="__main__":main()
