"""One staged registry contract/audit; no image or fitting experiment reruns."""
from __future__ import annotations

import csv
from datetime import datetime, timezone
import json
from pathlib import Path
import sys

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/"python"))
from lutlab import casebook,corpus,runtime
from lutlab.entry import _write_report


def main():
    output=ROOT/"artifacts/r28-corpus";output.mkdir(parents=True,exist_ok=True)
    result=runtime._execute([sys.executable,"-m","pytest","-q","tests/test_casebook_contract.py"])
    (output/"pytest-casebook.log").write_text(result["stdout"]+result["stderr"],encoding="utf-8")
    print(result["stdout"],flush=True)
    if result["returncode"]:raise RuntimeError("casebook contract failed")
    book=casebook.Casebook(ROOT/"datasets/problem16-v1/casebook")
    audit=book.audit();summary=book.summary()
    rows=[]
    for key,case in book.index["cases"].items():
        if case["status"]!="measured":continue
        for policy in ("best_measured_mean","best_measured_max"):
            identity=case["champions"][policy]
            record=json.loads((book.root/"observations"/f"{identity}.json").read_text())
            rows.append({"case":key,"policy":policy,"strategy":record["strategy"],"m":"-".join(map(str,record["m"])),
                **{k:record["cube"][k] for k in ("mean","rms","p99","max")},"node_payload_bytes":record["node_payload_bytes"],
                "worst_image_mean":record.get("images",{}).get("worst_mean"),"observation_id":identity})
    with (output/"legacy-champions.csv").open("w",encoding="utf-8-sig",newline="") as stream:
        writer=csv.DictWriter(stream,fieldnames=list(rows[0]));writer.writeheader();writer.writerows(rows)
    source_names=("python/lutlab/casebook.py","tests/test_casebook_contract.py","scripts/r28_casebook_audit.py")
    report={"finished_utc":datetime.now(timezone.utc).isoformat(),"scope":__doc__,"audit":audit,
        "summary":{k:v for k,v in summary.items() if k!="groups"},"contracts":{k:v for k,v in result.items() if k not in ("stdout","stderr")},
        "source_sha256":{name:corpus.digest_file(ROOT/name) for name in source_names},
        "historical_execution_reused":True,"new_source_case_accuracy_experiments":0,"pass":True}
    _write_report(output/"casebook-audit.json",report);_write_report(book.root/"summary.json",summary)
    print(json.dumps({"audit":audit,"summary":report["summary"]},indent=2))


if __name__=="__main__":main()
