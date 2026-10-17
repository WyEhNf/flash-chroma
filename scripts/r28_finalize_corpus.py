"""Finish R28 only after the live full construction/inspection has completed.

Extract exact final-domain palette/gamut labels, bind the audited new cases to
the persistent casebook, and freeze a reviewable inventory. No model accuracy or
performance is inferred from data construction or source classification.
"""
from __future__ import annotations

from collections import Counter,defaultdict
import csv
from datetime import datetime,timezone
import json
from pathlib import Path
import sys
import time

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/"python"))
import numpy as np
from lutlab import casebook,corpus,io
from lutlab.entry import _write_report


def characterize(path):
    table=io.load_full(path,mmap=True)
    seen=np.zeros(256**3,np.bool_);channels=np.zeros((3,256),np.int64);boundary=0
    try:
        for begin in range(0,256,8):
            values=table[begin:begin+8].reshape(-1,3)
            keys=(values[:,0].astype(np.uint32)<<16)|(values[:,1].astype(np.uint32)<<8)|values[:,2]
            seen[keys]=True
            for c in range(3):channels[c]+=np.bincount(values[:,c],minlength=256)
            boundary+=int(np.count_nonzero(np.any((values==0)|(values==255),axis=1)))
        grey=np.arange(256,dtype=np.uint8)
        neutrals=table[grey,grey,grey]
        count=int(np.count_nonzero(seen))
        return {"output_palette_size":count,"chain_output_constant":count==1,
            "active_component_values":[int(np.count_nonzero(c)) for c in channels],
            "component_min":[int(np.flatnonzero(c)[0]) for c in channels],
            "component_max":[int(np.flatnonzero(c)[-1]) for c in channels],
            "boundary_output_colors":boundary,"black_output":table[0,0,0].tolist(),"white_output":table[255,255,255].tolist(),
            "neutral_inputs_with_neutral_output":int(np.count_nonzero(np.all(neutrals==neutrals[:,:1],axis=1))),
            "scope":"exact whole composed RGB8 cube; a constant chain can still contain difficult independent stages"}
    finally:table._mmap.close()


def main():
    output=ROOT/"artifacts/r28-corpus";dataset=ROOT/"data/corpus-v1"
    catalog_path=ROOT/"datasets/problem16-v1/catalog.json";definition=json.loads(catalog_path.read_text())
    build_path=output/"build.json";build=json.loads(build_path.read_text())
    inspection_path=dataset/"inspection.json"
    if not build["complete"]:raise RuntimeError("construction still incomplete; resume its confirmed live handle, do not start a second builder")
    if corpus.digest_file(inspection_path)!=build["inspection_sha256"] or corpus.digest_file(catalog_path)!=build["catalog_sha256"]:
        raise RuntimeError("completed corpus evidence changed")
    inspection=json.loads(inspection_path.read_text())
    if not inspection["pass"] or inspection["verified_case_count"]!=200 or inspection["verified_image_count"]!=320:
        raise RuntimeError("the declared first corpus is not completely verified")
    if definition["generator"]!=corpus.generator_fingerprint():raise RuntimeError("frozen generator changed")
    book_audit=json.loads((output/"casebook-audit.json").read_text())
    if not book_audit["pass"]:raise RuntimeError("registry contract/audit did not pass")
    for name,digest in book_audit["source_sha256"].items():
        if corpus.digest_file(ROOT/name)!=digest:raise RuntimeError("casebook code changed after contract stage")
    book=casebook.Casebook(ROOT/"datasets/problem16-v1/casebook");book.attach_catalog(catalog_path,dataset)
    by_id={c["id"]:c for c in definition["cases"]};groups=defaultdict(list);descriptors={};rows=[]
    for case in definition["cases"]:
        record=json.loads((dataset/"cases"/case["id"]/"manifest.json").read_text())
        groups[record["composite"]["sha256"]].append(case["id"])
    for index,case in enumerate(definition["cases"],1):
        folder=dataset/"cases"/case["id"];record=json.loads((folder/"manifest.json").read_text())
        key=record["composite"]["sha256"]
        if key not in descriptors:descriptors[key]=characterize(folder/"composite.lut256")
        description={**descriptors[key],"same_final_target_cases":groups[key],
            "holdout_final_target_seen_in_training":case["split"]=="holdout" and any(by_id[other]["split"] in ("development","calibration") for other in groups[key])}
        book.index["cases"][case["id"]]["characterization"]=description
        rows.append({"case_id":case["id"],"family":case["family"],"intensity":case["intensity"],"seed":case["seed"],"split":case["split"],
            "tags":"|".join(case["tags"]),"source_sha256":"|".join(item["sha256"] for item in record["stages"]),"composite_sha256":key,
            "output_palette_size":description["output_palette_size"],"chain_output_constant":description["chain_output_constant"],
            "active_component_values":json.dumps(description["active_component_values"]),
            "holdout_final_target_seen_in_training":description["holdout_final_target_seen_in_training"]})
        if index%10==0:print(f"[characterize] {index}/200 exact output palettes",flush=True)
    book.save();summary=book.summary();_write_report(book.root/"summary.json",summary)
    image_manifest=json.loads((dataset/"images.json").read_text())
    with (output/"case-inventory.csv").open("w",encoding="utf-8-sig",newline="") as stream:
        writer=csv.DictWriter(stream,fieldnames=list(rows[0]));writer.writeheader();writer.writerows(rows)
    image_rows=[{"id":item["id"],"family":item["family"],"intensity":item["intensity"],"seed":item["seed"],"split":item["split"],
        "sha256":item["sha256"],"rgb_sha256":item["rgb_sha256"],"natural_photo":item["natural_photo"],
        **{k:json.dumps(v) if isinstance(v,list) else v for k,v in item["features"].items()}} for item in image_manifest["records"]]
    with (output/"image-inventory.csv").open("w",encoding="utf-8-sig",newline="") as stream:
        writer=csv.DictWriter(stream,fieldnames=list(image_rows[0]));writer.writeheader();writer.writerows(image_rows)
    source_names=["python/lutlab/corpus.py","python/lutlab/luts.py","python/lutlab/io.py","python/lutlab/entry.py",
        "python/lutlab/casebook.py","tests/test_corpus_contract.py","tests/test_casebook_contract.py",
        "scripts/r28_casebook_audit.py","scripts/r28_format_fixtures.py","scripts/r28_finalize_corpus.py",
        "scripts/r29_strategy_matrix.py","scripts/r29_freeze_class_rules.py","datasets/problem16-v1/catalog.json","datasets/problem16-v1/strategy-plan.json"]
    report={"finished_utc":datetime.now(timezone.utc).isoformat(),"scope":__doc__,"source_sha256":{n:corpus.digest_file(ROOT/n) for n in source_names},
        "build_result_sha256":corpus.digest_file(build_path),"inspection_sha256":corpus.digest_file(inspection_path),
        "casebook_audit_sha256":corpus.digest_file(output/"casebook-audit.json"),"cases":200,"images":320,
        "format_fixtures":json.loads((ROOT/"datasets/problem16-v1/invalid-formats.json").read_text())["count"],
        "format_execution_status":"not_executed","probes":inspection["probe_sets"],
        "constant_final_chains":sum(row["chain_output_constant"] for row in rows),
        "distinct_final_transforms":len(groups),"duplicate_final_transform_groups":[ids for ids in groups.values() if len(ids)>1],
        "holdout_final_target_seen_in_training":[row["case_id"] for row in rows if row["holdout_final_target_seen_in_training"]],
        "unique_full_object_bytes":inspection["unique_full_object_bytes"],"construction_elapsed_seconds":build["finished_unix"]-build["started_unix"],
        "casebook_summary":{k:v for k,v in summary.items() if k!="groups"},
        "new_case_strategy_observations":0,"matrix_plan_candidates":5400,"portability_phase":"not_completed",
        "official_score_available":False,"dataset_and_registry_stage_pass":True,"full_user_goal_complete":False}
    _write_report(output/"final.json",report)
    print(json.dumps({k:report[k] for k in ("cases","images","constant_final_chains","distinct_final_transforms","unique_full_object_bytes","dataset_and_registry_stage_pass","full_user_goal_complete")},indent=2))


if __name__=="__main__":main()
