"""Freeze descriptive matrix progress and case winners without pixel reruns.

A completed work chunk is not a completed matrix, class rule, image qualification,
or paired timing stage. Preserve both candidate failures and all missing cases.
"""
from __future__ import annotations

import argparse
from collections import Counter,defaultdict
import csv
from datetime import datetime,timezone
import json
import os
from pathlib import Path
import sys

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/"python"))
from lutlab import casebook,corpus
from lutlab.entry import _write_report


def write_csv(path,rows):
    if not rows:return
    with path.open("w",encoding="utf-8-sig",newline="") as stream:
        writer=csv.DictWriter(stream,fieldnames=list(rows[0]));writer.writeheader();writer.writerows(rows)


def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument("--matrix",type=Path,default=ROOT/"artifacts/r29-matrix/development.json")
    p.add_argument("--casebook",type=Path,default=ROOT/"datasets/problem16-v1/casebook")
    p.add_argument("--source-root",type=Path,help="byte-preserved R29 numerical source after main-tree development advances")
    args=p.parse_args()
    # This tool verifies/imports observations and therefore is a ledger writer.
    # Refuse a live controller rather than detecting a changing matrix only
    # after a stale in-memory index might already have overwritten newer rows.
    lock=args.matrix.parent/"phase-controller.lock"
    with lock.open("x",encoding="utf-8") as stream:
        json.dump({"pid":os.getpid(),"owner":"R29 completed inventory/canonical writer"},stream)
    try:freeze(args)
    finally:lock.unlink()


def freeze(args):
    matrix=json.loads(args.matrix.read_text());matrix_hash=corpus.digest_file(args.matrix)
    source_root=args.source_root.resolve() if args.source_root else ROOT
    sources={str((source_root/name).relative_to(ROOT)):digest for name,digest in matrix["frozen"]["source_sha256"].items()}
    sources[str(Path(__file__).relative_to(ROOT))]=corpus.digest_file(Path(__file__))
    for name,digest in sources.items():
        if corpus.digest_file(ROOT/name)!=digest:raise RuntimeError("matrix source changed")
    book=casebook.Casebook(args.casebook);catalog=json.loads((ROOT/"datasets/problem16-v1/catalog.json").read_text())
    plan=json.loads((ROOT/"datasets/problem16-v1/strategy-plan.json").read_text());lookup={c["id"]:c for c in catalog["cases"]}
    groups=defaultdict(list);rows=[];probes=[]
    for key,item in matrix["observations"].items():
        case_id,profile,budget=key.split("/");case=lookup[case_id];path=casebook._path(item["path"])
        if corpus.digest_file(path)!=item["sha256"]:raise RuntimeError("matrix observation changed")
        if item["status"]!="screened":
            rows.append({"case_id":case_id,"family":case["family"],"intensity":case["intensity"],"split":case["split"],
                "profile":profile,"m":int(budget[1:]),"status":item["status"],"mean":None,"rms":None,"p99":None,"max":None,"node_payload_bytes":None})
            continue
        if book.record(path)!=item["observation_id"]:raise RuntimeError("casebook observation identity changed")
        value=json.loads(path.read_text());primary=casebook._path(value["evidence"][0]["path"])
        detail=json.loads(primary.read_text())
        row={"case_id":case_id,"family":case["family"],"intensity":case["intensity"],"split":case["split"],
            "profile":profile,"m":int(budget[1:]),"status":item["status"],
            **{metric:value["cube"][metric] for metric in ("mean","rms","p99","max")},"node_payload_bytes":value["node_payload_bytes"]}
        rows.append(row);groups[case_id].append(row)
        for name,metrics in detail["probes"].items():
            probes.append({"case_id":case_id,"profile":profile,"m":row["m"],"probe":name,**metrics})
    winners={}
    for case_id,values in groups.items():
        mean=min(values,key=lambda r:(r["mean"],r["node_payload_bytes"],r["profile"]))
        tail=min(values,key=lambda r:(r["max"],r["p99"],r["node_payload_bytes"],r["profile"]))
        winners[case_id]={"mean":mean,"max":tail,"evaluated_candidates":len(values),
            "full_declared_case_comparison":len(values)==len(plan["sizes"])*len(plan["profiles"]),
            "scope":"this source seed only; class generalisation is unproven"}
    audit=book.audit();summary=book.summary();_write_report(book.root/"summary.json",summary)
    count=len(matrix["observations"]);folder=args.matrix.parent;label=args.matrix.stem
    write_csv(folder/f"comparison-{label}-{count:04d}.csv",rows);write_csv(folder/f"probes-{label}-{count:04d}.csv",probes)
    result={"finished_utc":datetime.now(timezone.utc).isoformat(),"scope":__doc__,"source_sha256":sources,
        "matrix_sha256":matrix_hash,"finished_candidate_observations":count,"full_plan_candidates":plan["total_candidates"],
        "phase_expected_candidates":matrix["phase_expected_candidates"],"phase_complete":matrix["phase_complete"],
        "status_counts":dict(Counter(row["status"] for row in rows)),"new_cases_with_observations":len(groups),
        "new_cases_full_declared_comparison":sum(v["full_declared_case_comparison"] for v in winners.values()),
        "unmeasured_new_cases":[c["id"] for c in catalog["cases"] if c["id"] not in groups],"case_winners":winners,
        "casebook_integrity_audit":audit,"casebook_summary":{k:v for k,v in summary.items() if k!="groups"},
        "class_sweet_zone_proven":False,"image_path_qualification":False,"paired_timing_complete":False,
        "full_user_goal_complete":False,"official":False,"completed_snapshot_contract_pass":True}
    if corpus.digest_file(args.matrix)!=matrix_hash:raise RuntimeError("matrix is still changing; freeze after its chunk ends")
    path=folder/f"snapshot-{label}-{count:04d}.json"
    if path.exists():raise RuntimeError("preserve the existing snapshot; append a later completed chunk")
    _write_report(path,result);print(json.dumps({k:result[k] for k in ("finished_candidate_observations","full_plan_candidates", "new_cases_full_declared_comparison","casebook_summary")},indent=2))


if __name__=="__main__":main()
