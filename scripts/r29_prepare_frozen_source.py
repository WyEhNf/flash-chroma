"""Materialize byte-exact baseline code from its already verified source zip.

No checkout reset, copying uncommitted main files, or cache-identity migration.
The numerical source hashes and an existing public-fit cache identity must equal
the original R29 epoch. Input/model/output directories remain the real workspace.
"""
from __future__ import annotations
import hashlib
import json
import os
from pathlib import Path
import subprocess
import sys
from types import SimpleNamespace
import zipfile
import shutil

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/"python"))
from lutlab import corpus
from lutlab.entry import _write_report


def main():
    archive=ROOT/"artifacts/r29-matrix/source-snapshot.zip"
    manifest_path=ROOT/"artifacts/r29-matrix/source-manifest.json";manifest=json.loads(manifest_path.read_text(encoding="utf-8"))
    digest=corpus.digest_file(archive)
    if digest!=manifest["snapshot"]["sha256"]:raise RuntimeError("baseline raw source zip changed")
    saved=ROOT/"artifacts/r29-frozen-source"/f"epoch-source-{digest}.zip"
    saved_manifest=saved.with_suffix(".json");saved.parent.mkdir(parents=True,exist_ok=True)
    if not saved.exists():shutil.copyfile(archive,saved)
    if corpus.digest_file(saved)!=digest:raise RuntimeError("immutable epoch source copy differs")
    if not saved_manifest.exists():shutil.copyfile(manifest_path,saved_manifest)
    if corpus.digest_file(saved_manifest)!=corpus.digest_file(manifest_path):raise RuntimeError("immutable source index differs")
    report=json.loads((ROOT/"artifacts/r29-matrix/development.json").read_text(encoding="utf-8"))
    frozen=report["frozen"];destination=ROOT/"artifacts/r29-frozen-source"/digest[:20]
    destination.mkdir(parents=True,exist_ok=True)
    with zipfile.ZipFile(archive) as source:
        for name in source.namelist():
            target=(destination/name).resolve();target.relative_to(destination.resolve())
            value=source.read(name)
            if hashlib.sha256(value).hexdigest()!=manifest["source_files"][name]["sha256"]:raise RuntimeError("source payload differs")
            if target.exists():
                if target.read_bytes()!=value:raise RuntimeError("existing frozen source was edited; preserve it and use a new epoch")
            else:target.parent.mkdir(parents=True,exist_ok=True);target.write_bytes(value)
    for name,value in frozen["source_sha256"].items():
        if corpus.digest_file(destination/name)!=value:raise RuntimeError("raw source does not match R29's frozen numerical code")
    plan=json.loads((ROOT/"datasets/problem16-v1/strategy-plan.json").read_text(encoding="utf-8"))
    key="ccm-mild-s0-e8d21c5b/adaptive_full/m17";observation=json.loads(Path(report["observations"][key]["path"]).read_text(encoding="utf-8"))
    models=[Path(path) for path in observation["models"]];batch=json.loads((models[0].parent/"manifest.json").read_text(encoding="utf-8"))
    inputs=[str(ROOT/"data/corpus-v1/cases/ccm-mild-s0-e8d21c5b"/f"lut{k}.lut256") for k in range(1,5)]
    params=dict(scenario="ccm-mild-s0-e8d21c5b",mode="seq",method="adaptive_full",m=17,grid="dp",adaptive=False,
        inputs=inputs,model_dir=str(ROOT/"artifacts/r29-matrix/cases/ccm-mild-s0-e8d21c5b/adaptive_full-m17/models"),allow_composite=False,allow_residual=False)
    code="from pathlib import Path;from types import SimpleNamespace;import sys,json;from lutlab import cli; v=json.loads(sys.argv[1]);v['inputs']=[Path(x) for x in v['inputs']];e=cli.model_entry(SimpleNamespace(**v),existing_only=True);assert e is not None;print(e.manifest['identity_sha256'])"
    environment={**os.environ,"PYTHONPATH":str(destination/"python"),"JSHC_FULL_FIT_LIB":str(ROOT/"build-fit/libjshc_full_fit.dll"),
        "GIT_CEILING_DIRECTORIES":str(ROOT),"OPENBLAS_NUM_THREADS":"1","MKL_NUM_THREADS":"1","OMP_NUM_THREADS":"1"}
    probe=subprocess.run([sys.executable,"-c",code,json.dumps(params)],cwd=destination,env=environment,
        capture_output=True,text=True,encoding="utf-8",errors="replace")
    if probe.returncode or probe.stdout.strip()!=batch["identity_sha256"]:
        raise RuntimeError("frozen public fitter cache identity differs: "+probe.stderr+probe.stdout)
    marker={"schema":1,"archive_sha256":digest,"archive":str(saved),"source_manifest":str(saved_manifest),"source_manifest_sha256":corpus.digest_file(saved_manifest),
        "source_sha256":frozen["source_sha256"],"source_root":str(destination),"original_frozen_environment":{k:v for k,v in frozen.items() if k not in ("phase","class_rule_sha256")},
        "public_cache_identity_probe":batch["identity_sha256"],"probe_returncode":0,"pass":True,
        "logging":"source hashes/zip identify execution; GIT_CEILING_DIRECTORIES prevents reporting the evolving main worktree as this source image"}
    _write_report(destination/"frozen-source.json",marker)
    _write_report(ROOT/"artifacts/r29-matrix/frozen-source.json",marker)
    print(json.dumps({"pass":True,"source_root":str(destination),"preserved_cache_identity":batch["identity_sha256"]}))


if __name__=="__main__":main()
