"""Policy checks: partial colour evidence, missing timings and evidence tampering."""
from copy import deepcopy
import json

import numpy as np
import pytest

from lutlab import cache, casebook, corpus, io


def test_ranking_keeps_mean_tail_and_budget_distinct():
    def row(key,mean,maximum,size):
        return {"observation_id":key,"correctness_pass":True,"cube":{"n_colors":256**3,"mean":mean,"rms":mean+.1,"p99":maximum/2,"max":maximum},
            "node_payload_bytes":size,"model_sha256":[key]*4,"strategy":key,"kernel":"tetra_scalar","fit_s":.0001}
    rows=[row("mean",.5,10,400000),row("tail",.8,2,400000),row("small",1,5,58000)]
    result=casebook.rank(rows)
    assert result["best_measured_mean"]=="mean" and result["best_measured_max"]=="tail"
    assert set(result["pareto"])=={"mean","tail","small"} and result["speed"] is None
    assert not result["qualified_by_image_set"]
    bad=deepcopy(rows[0]);bad["cube"]["n_colors"]=262144
    with pytest.raises(ValueError,match="whole RGB8 cube"):casebook.rank([bad])


def test_casebook_rejects_tampered_primary_evidence_and_wrong_sources(tmp_path):
    # These are schema fixtures, not actual quality measurements or LUT sources.
    sources=[tmp_path/f"source{k}.fixture" for k in range(4)]
    for k,path in enumerate(sources):path.write_bytes(bytes([k])*16)
    identity=cache.build_identity(sources,{"mode":"seq","method":"sample","m":17,"grid":"uniform","semantics":"independent","n_stages":4})
    models=[io.SparseLut(io.uniform_grid(17),np.full((17,17,17,3),k,np.uint8)) for k in range(4)]
    entry=cache.publish(tmp_path/"models",identity,models,{"fit_s":0.})
    hashes=[r["sha256"] for r in identity["inputs"]]
    book=casebook.Casebook(tmp_path/"book")
    book.add_case("fixture",{"family":"fixture","split":"regression","intensity":"control"},hashes)
    cube={"n_colors":256**3,"mean":0.,"rms":0.,"p99":0.,"max":0.}
    primary={"kind":"casebook_native_cube_screen_v1","source_sha256":hashes,"cube":cube,"inputs_unchanged":True,
        "runtime":{"models_sha256":{str(p):corpus.digest_file(p) for p in entry.paths},"returncode":0}}
    primary_path=tmp_path/"primary.json";primary_path.write_text(json.dumps(primary))
    value={"case_id":"fixture","source_sha256":hashes,"semantics":"independent","correctness_pass":True,
        "strategy":"fixture","m":[17]*4,"models":list(map(str,entry.paths)),"model_sha256":list(primary["runtime"]["models_sha256"].values()),
        "kernel":"tetra_scalar","node_payload_bytes":sum(m.nodes.nbytes for m in models),"cube":cube,
        "evidence":[{"path":str(primary_path),"sha256":corpus.digest_file(primary_path)}]}
    path=tmp_path/"observation.json";path.write_text(json.dumps(value));key=book.record(path)
    assert book.index["cases"]["fixture"]["champions"]["best_measured_mean"]==key
    changed=deepcopy(value);changed["cube"]["max"]=1.;path.write_text(json.dumps(changed))
    with pytest.raises(ValueError,match="inconsistent"):book.record(path)
    changed=deepcopy(value);changed["source_sha256"]=list(reversed(hashes));path.write_text(json.dumps(changed))
    with pytest.raises(ValueError,match="source chain"):book.record(path)
    path.write_text(json.dumps(value));primary_path.write_text(json.dumps({**primary,"inputs_unchanged":False}))
    with pytest.raises(ValueError,match="evidence changed"):book.record(path)
