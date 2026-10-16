"""Persistent, evidence-bound per-case champions, including failed candidates.

Whole-cube quality, image qualification, size and timing are distinct policies.
An unmeasured case stays unmeasured. A single fit_s or unpaired timing can never
win the speed policy. No local illustrative threshold is called official.
"""
from __future__ import annotations

import argparse
from collections import Counter
import hashlib
import json
import math
from pathlib import Path
import re

from . import cache, corpus, io, timingbook
from .execution_proof import validate_native_kernel
from .entry import _write_report

ROOT=Path(__file__).resolve().parents[2]
HISTORY=("r20-validation/audit.json","r21-boundary/study.json","r22-structured-v3/study.json",
    "r24-supported/study.json","r25-full/study.json","r25-full/capacity/study.json",
    "r26-box/study.json","r27-step/study.json")


def _path(value):
    path=Path(str(value).replace("\\","/"))
    if path.exists():return path.resolve()
    relative=ROOT/path
    if relative.exists():return relative.resolve()
    for prefix in ("artifacts/","report/","data/","output/"):
        text=str(path).replace("\\","/")
        if "/"+prefix in text:
            restored=ROOT/(prefix+text.split("/"+prefix,1)[1])
            if restored.exists():return restored.resolve()
    raise FileNotFoundError(path)


def _portable(path):
    path=Path(path).resolve()
    try:return path.relative_to(ROOT).as_posix()
    except ValueError:return str(path)


def validate_quality(value):
    if value.get("n_colors")!=256**3:raise ValueError("champions require the whole RGB8 cube, not a sample")
    for name in ("mean","rms","p99","max"):
        number=value.get(name)
        if isinstance(number,bool) or not isinstance(number,(int,float)) or not math.isfinite(number) or number<0:
            raise ValueError("invalid measured quality")
    if not value["mean"]<=value["rms"]+1e-12 or value["rms"]>value["max"]+1e-12 or value["p99"]>value["max"]+1e-12:
        raise ValueError("inconsistent quality statistics")


def rank(rows):
    """Rank only verified complete-cube observations; never infer missing timing."""
    rows=[row for row in rows if row["correctness_pass"]]
    for row in rows:validate_quality(row["cube"])
    if not rows:return {"best_measured_mean":None,"best_measured_max":None,"pareto":[],"qualified_by_image_set":{},"speed":None}
    def tie(row):return (row["node_payload_bytes"],row["strategy"],row["observation_id"])
    mean=min(rows,key=lambda row:(row["cube"]["mean"],*tie(row)))
    tail=min(rows,key=lambda row:(row["cube"]["max"],row["cube"]["p99"],*tie(row)))
    def objectives(row):return (row["cube"]["mean"],row["cube"]["max"],row["node_payload_bytes"])
    pareto=[row for row in rows if not any(
        all(a<=b for a,b in zip(objectives(other),objectives(row)))
        and any(a<b for a,b in zip(objectives(other),objectives(row))) for other in rows)]
    # Identical model executions may have multiple strategy/evidence aliases.
    unique={}
    for row in sorted(pareto,key=tie):
        unique.setdefault((tuple(row["model_sha256"]),row["kernel"]),row["observation_id"])
    cohorts={}
    for row in rows:
        images=row.get("images")
        if images and images["native_verified"] and images["count"]==100 and images["illustrative_mean_pass"]:
            cohorts.setdefault(images["list_sha256"],[]).append(row)
    qualified={key:min(group,key=lambda row:(row["cube"]["mean"],*tie(row)))["observation_id"] for key,group in cohorts.items()}
    return {"best_measured_mean":mean["observation_id"],"best_measured_max":tail["observation_id"],
        "pareto":list(unique.values()),"qualified_by_image_set":qualified,"speed":timingbook.rank(rows),
        "speed_reason":"only registered paired native timings, grouped by exact model/resource/epoch; fit_s is never a speed measurement"}


class Casebook:
    def __init__(self, root):
        self.root=Path(root);self.root.mkdir(parents=True,exist_ok=True)
        (self.root/"observations").mkdir(exist_ok=True)
        self.index_path=self.root/"index.json"
        self.index=json.loads(self.index_path.read_text(encoding="utf-8")) if self.index_path.exists() else {
            "schema":1,"cases":{},"catalogs":[],"official_score_available":False,
            "policies":{"mean":"minimum exact whole-cube mean, then payload, strategy name",
                "tail":"minimum exact whole-cube max, then p99, payload",
                "pareto":["whole_cube_mean","whole_cube_max","node_payload_bytes"],
                "qualification":"100 actually executed standard images, strict illustrative mean<2 plus cube mean<2; separate per image cohort",
                "speed":"unknown until paired matching-input/model/resource timing is registered"}}
        if self.index["schema"]!=1:raise ValueError("unknown casebook schema")

    def save(self):_write_report(self.index_path,self.index)

    def add_case(self, case_id, metadata, source_sha256=None):
        if not re.fullmatch(r"[a-zA-Z0-9_.-]{1,128}",case_id):raise ValueError("unsafe case ID")
        if source_sha256 is not None and (len(source_sha256)!=4 or len(set(source_sha256))!=4):raise ValueError("four distinct source hashes required")
        expected={"metadata":metadata,"source_sha256":source_sha256}
        existing=self.index["cases"].get(case_id)
        if existing is not None:
            if existing["metadata"]!=metadata:raise ValueError("immutable case metadata changed; add a new version")
            if existing["source_sha256"] not in (None,source_sha256):raise ValueError("source identity changed")
            if source_sha256 is not None:existing["source_sha256"]=source_sha256
        else:self.index["cases"][case_id]={**expected,"observations":[],"status":"unmeasured","champions":rank([])}
        self.save()

    def attach_catalog(self, catalog_path, dataset=None):
        catalog_path=Path(catalog_path);definition=json.loads(catalog_path.read_text(encoding="utf-8"))
        audited=False
        if dataset is not None and (Path(dataset)/"inspection.json").exists():
            inspection=json.loads((Path(dataset)/"inspection.json").read_text(encoding="utf-8"))
            audited=inspection.get("pass") and {r["id"] for r in inspection["cases"]}=={c["id"] for c in definition["cases"]}
        for case in definition["cases"]:
            hashes=None
            if audited:
                manifest=Path(dataset)/"cases"/case["id"]/"manifest.json"
                if manifest.exists():hashes=[s["sha256"] for s in json.loads(manifest.read_text(encoding="utf-8"))["stages"]]
            self.add_case(case["id"],{key:case[key] for key in ("family","intensity","seed","split","tags","expected")},hashes)
        record={"path":_portable(catalog_path),"sha256":corpus.digest_file(catalog_path),"cases":len(definition["cases"])}
        if record not in self.index["catalogs"]:self.index["catalogs"].append(record)
        self.save()

    def record(self, evidence_path):
        evidence_path=Path(evidence_path);value=json.loads(evidence_path.read_text(encoding="utf-8"))
        case=self.index["cases"][value["case_id"]]
        if case["source_sha256"] is None or value["source_sha256"]!=case["source_sha256"]:
            raise ValueError("observation is bound to a different or unknown source chain")
        if value["semantics"]!="independent" or not value["correctness_pass"]:
            raise ValueError("only structurally verified independent mappings may be champions")
        validate_quality(value["cube"])
        models=[_path(p) for p in value["models"]]
        if len(models)!=4 or [corpus.digest_file(p) for p in models]!=value["model_sha256"]:
            raise ValueError("model bytes differ from measured evidence")
        contract=io.inspect_submission_contract(models,semantics="independent")
        if not contract["pass"] or contract["semantics_evidence"]!="verified_model_manifest":raise ValueError("model provenance is not verified")
        manifest=json.loads((models[0].parent/"manifest.json").read_text(encoding="utf-8"))
        if [s["sha256"] for s in manifest["identity"]["inputs"]]!=case["source_sha256"]:raise ValueError("model source binding differs")
        if sum(io.load_sparse(p,competition=True).nodes.nbytes for p in models)!=value["node_payload_bytes"]:raise ValueError("node payload claim differs")
        if value["m"]!=contract["grid_sizes"]:raise ValueError("grid dimensions differ")
        observed=value.get("images")
        if observed and (observed["count"]!=100 or not observed["native_verified"]):raise ValueError("image qualification requires actual execution of all 100 frames")
        for item in value["evidence"]:
            if corpus.digest_file(_path(item["path"]))!=item["sha256"]:raise ValueError("underlying evidence changed")
        primary=json.loads(_path(value["evidence"][0]["path"]).read_text(encoding="utf-8"))
        if "backends" in primary:
            cpu=primary["backends"]["cpu"]
            if not primary["structural_contract_pass"] or not cpu["cube_stats_computed"]:
                raise ValueError("primary execution was not structurally verified")
            if [s["sha256"] for s in primary["sources"]]!=value["source_sha256"] or list(cpu["model_sha256"].values())!=value["model_sha256"]:
                raise ValueError("primary execution used different source or model bytes")
            if cpu["cube"]!=value["cube"] or cpu["kernel"]!=value["kernel"]:
                raise ValueError("normalized metrics differ from primary evidence")
            if observed:
                actual_pass=all(r["mean"]<2 for r in cpu["per_image"]) and cpu["cube"]["mean"]<2
                if (cpu["n_images"]!=100 or not cpu["image_execution_verified"] or observed["list_sha256"]!=cpu["image_list_sha256"]
                        or observed["illustrative_mean_pass"]!=actual_pass or observed["worst_mean"]!=max(r["mean"] for r in cpu["per_image"])):
                    raise ValueError("normalized image qualification differs from actual execution")
        elif primary.get("kind")=="casebook_native_cube_screen_v1":
            execution=primary["runtime"]
            validate_native_kernel(execution,value["kernel"],value.get("backend","cpu"))
            if (primary["cube"]!=value["cube"] or primary["source_sha256"]!=value["source_sha256"]
                    or list(execution["models_sha256"].values())!=value["model_sha256"]
                    or execution["returncode"]!=0 or not primary["inputs_unchanged"]):
                raise ValueError("native whole-cube screen is inconsistent")
            if observed:raise ValueError("cube screening cannot claim actual image qualification")
        else:raise ValueError("unsupported primary measurement evidence")
        if value.get("performance"):
            timingbook.validate(value)
            self.index["policies"]["speed"]="paired native mapping times per exact model/resource/benchmark epoch; point estimates, demonstrated winners and time/memory Pareto are separate"
        key=hashlib.sha256(corpus.canonical(value)).hexdigest()
        stored={**value,"observation_id":key,"record_source":{"path":_portable(evidence_path),"sha256":corpus.digest_file(evidence_path)}}
        target=self.root/"observations"/f"{key}.json"
        if target.exists() and json.loads(target.read_text(encoding="utf-8"))!=stored:raise RuntimeError("immutable observation changed")
        if not target.exists():_write_report(target,stored)
        if key not in case["observations"]:case["observations"].append(key)
        rows=[json.loads((self.root/"observations"/f"{k}.json").read_text(encoding="utf-8")) for k in case["observations"]]
        case.update(status="measured",champions=rank(rows))
        self.save();return key

    def audit(self):
        checked=0
        for case in self.index["cases"].values():
            for key in list(case["observations"]):
                stored=json.loads((self.root/"observations"/f"{key}.json").read_text(encoding="utf-8"))
                value={k:v for k,v in stored.items() if k not in ("observation_id","record_source")}
                if hashlib.sha256(corpus.canonical(value)).hexdigest()!=key:raise ValueError("stored observation changed")
                source=_path(stored["record_source"]["path"])
                if corpus.digest_file(source)!=stored["record_source"]["sha256"]:raise ValueError("normalized source record changed")
                if self.record(source)!=key:raise ValueError("observation identity changed")
                checked+=1
        return {"pass":True,"observations":checked,"scope":"source/model/evidence integrity; previous numerical execution is not rerun"}

    def summary(self):
        cases=self.index["cases"]
        rows={}
        for key,case in cases.items():
            family=case["metadata"]["family"];split=case["metadata"]["split"];intensity=case["metadata"]["intensity"]
            group=rows.setdefault(f"{family}/{intensity}/{split}",{"case_count":0,"measured_cases":0,"mean_winner_counts":{},"unmeasured":[]})
            group["case_count"]+=1
            if case["status"]!="measured":group["unmeasured"].append(key);continue
            group["measured_cases"]+=1
            best=json.loads((self.root/"observations"/f"{case['champions']['best_measured_mean']}.json").read_text(encoding="utf-8"))
            name=best["strategy"]+"/m"+"-".join(map(str,best["m"]))
            group["mean_winner_counts"][name]=group["mean_winner_counts"].get(name,0)+1
        return {"cases":len(cases),"measured_cases":sum(c["status"]=="measured" for c in cases.values()),
            "cases_with_paired_runtime_groups":sum(bool(c["champions"].get("speed")) for c in cases.values()),
            "observations":sum(len(c["observations"]) for c in cases.values()),"groups":rows,
            "distinct_known_source_chains":len({tuple(c["source_sha256"]) for c in cases.values() if c["source_sha256"] is not None}),
            "scope":"descriptive winners among measured candidates only; no class sweet-zone or held-out generalisation claim yet"}

    def record_failure(self, evidence_path):
        path=Path(evidence_path);value=json.loads(path.read_text(encoding="utf-8"));case=self.index["cases"][value["case_id"]]
        if value["source_sha256"]!=case["source_sha256"] or value["status"] not in ("fit_failure","execution_failure","correctness_failure"):
            raise ValueError("failure must be bound to this case and an explicit failing stage")
        digest=corpus.digest_file(path)
        record={"path":_portable(path),"sha256":digest,"strategy":value["strategy"],"m":value["m"],"status":value["status"]}
        if record not in case.setdefault("failures",[]):case["failures"].append(record)
        self.save();return digest


def import_history(book, output):
    output=Path(output);output.mkdir(parents=True,exist_ok=True)
    seen=set();imported=[]
    for name in HISTORY:
        study_path=ROOT/"artifacts"/name;study=json.loads(study_path.read_text(encoding="utf-8"))
        if not study.get("finished_utc"):raise ValueError("unfinished historical study")
        for row in study["cases"]:
            for field,sha_field in (("result","result_sha256"),("baseline_result","baseline_sha256"),("jitter_result","jitter_result_sha256")):
                if field not in row:continue
                path=_path(row[field]);digest=corpus.digest_file(path)
                if digest!=row[sha_field]:raise ValueError("historical result changed")
                if digest in seen:continue
                seen.add(digest);accepted=json.loads(path.read_text(encoding="utf-8"));cpu=accepted["backends"]["cpu"]
                if not (accepted["structural_contract_pass"] and accepted["backend_cube_sha256_equal"] and accepted["backend_images_sha256_equal"]):
                    raise ValueError("historical source/model/execution contract was not proved")
                source=[s["sha256"] for s in accepted["sources"]]
                case_id="legacy-"+row["scenario"]
                book.add_case(case_id,{"family":row["scenario"].rsplit("-",1)[0],"intensity":"legacy",
                    "seed":int(row["scenario"].rsplit("-",1)[1]),"split":"legacy",
                    "tags":["historical","synthetic","previously_used_for_tuning"],"expected":{}},source)
                models=[_path(p) for p in cpu["model_sha256"]]
                manifest=json.loads((models[0].parent/"manifest.json").read_text(encoding="utf-8"));parameters=manifest["identity"]["parameters"]
                versions=hashlib.sha256(corpus.canonical(manifest["identity"]["source_sha256"])).hexdigest()[:8]
                value={"case_id":case_id,"source_sha256":source,"semantics":"independent","correctness_pass":True,
                    "strategy":parameters["method"]+"/"+parameters["grid"]+"@"+versions,"m":cpu["sizes"],
                    "models":[_portable(p) for p in models],"model_sha256":list(cpu["model_sha256"].values()),
                    "kernel":cpu["kernel"],"node_payload_bytes":sum(io.load_sparse(p).nodes.nbytes for p in models),
                    "cube":cpu["cube"],"images":{"count":cpu["n_images"],"native_verified":cpu["image_execution_verified"],
                        "list_sha256":cpu["image_list_sha256"],"worst_mean":max(r["mean"] for r in cpu["per_image"]),
                        "illustrative_mean_pass":all(r["mean"]<2 for r in cpu["per_image"]) and cpu["cube"]["mean"]<2,
                        "cpu_cuda_byte_equal":True},
                    "evidence":[{"path":_portable(path),"sha256":digest}],"official":False}
                destination=output/f"{digest}.json";_write_report(destination,value)
                imported.append(book.record(destination))
    return {"distinct_acceptance_results":len(seen),"imported_observations":len(set(imported)),"studies":HISTORY}


def main(argv=None):
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument("command",choices=["init","import-history","record","summary","audit"])
    parser.add_argument("--root",type=Path,default=ROOT/"datasets/problem16-v1/casebook")
    parser.add_argument("--catalog",type=Path,default=ROOT/"datasets/problem16-v1/catalog.json")
    parser.add_argument("--data",type=Path,default=ROOT/"data/corpus-v1")
    parser.add_argument("--evidence",type=Path)
    args=parser.parse_args(argv);book=Casebook(args.root)
    if args.command=="init":book.attach_catalog(args.catalog,args.data)
    elif args.command=="import-history":print(json.dumps(import_history(book,ROOT/"artifacts/r28-corpus/legacy-observations")))
    elif args.command=="record":
        if args.evidence is None:parser.error("record requires --evidence")
        print(book.record(args.evidence))
    elif args.command=="audit":
        result=book.audit();_write_report(args.root/"audit.json",result);print(json.dumps(result))
    summary=book.summary();_write_report(args.root/"summary.json",summary)
    print(json.dumps({k:v for k,v in summary.items() if k!="groups"},indent=2));return 0


if __name__=="__main__":raise SystemExit(main())
