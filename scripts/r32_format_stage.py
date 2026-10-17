"""One concentrated cross-loader gate, preserving frozen scanning binaries.

Reject all 30 negative fixtures through applicable native entry points; compare
the prior CPU/GPU behaviour only at known metadata/container gaps. Validate the
rebuilt kernels, one complete frozen RGB cube and actual 100+5 image paths.
No timing from this correctness stage is a performance benchmark.
"""
from __future__ import annotations

import ctypes as ct
import argparse
from datetime import datetime,timezone
import json
from pathlib import Path
import sys
import tempfile
import uuid

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/"python"));sys.path.insert(0,str(ROOT))
import numpy as np
from lutlab import casebook,corpus,io,runtime,validation
from lutlab.entry import _write_report
from scripts.r30_portable_stage import Model,load_library


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--reuse-cpp-gate",type=Path)
    args=parser.parse_args()
    output=ROOT/"artifacts/r32-formats";output.mkdir(exist_ok=True)
    source_names=["scripts/r32_format_stage.py","cpp/src/lut.cpp","cpp/src/main.cpp","cpp/include/jshc/image_contract.hpp",
        "cpp/tests/test_kernels.cpp","gpu/main.cu","gpu/CMakeLists.txt","gpu/build-windows.ps1",
        "python/lutlab/io.py","scripts/r30_portable_stage.py"]
    sources={name:corpus.digest_file(ROOT/name) for name in source_names}
    binaries={"cpu":ROOT/"build-r32-format-cpu/jshc.exe","cuda":ROOT/"build-r32-format-gpu/jshc_gpu.exe"}
    frozen={"cpu":ROOT/"build-r18-cpu/jshc.exe","cuda":ROOT/"build-r23-gpu/jshc_gpu.exe"}
    all_binary_hashes={str(path.relative_to(ROOT)):corpus.digest_file(path) for path in [*binaries.values(),*frozen.values(),ROOT/"build-r32-format-cpu/jshc_tests.exe"]}
    fixture_manifest=ROOT/"datasets/problem16-v1/invalid-formats.json";definition=json.loads(fixture_manifest.read_text(encoding="utf-8"))
    folder=output/("outputs-"+uuid.uuid4().hex[:8]);folder.mkdir()
    valid=ROOT/"data/corpus-v1/invalid/valid-control.slut"
    if corpus.digest_file(valid)!=definition["valid_control_sha256"]:raise RuntimeError("valid sparse fixture changed")
    image=ROOT/"assets/photos/kodak/rgb8-1024x768/kodim03.png"
    report={"started_utc":datetime.now(timezone.utc).isoformat(),"scope":__doc__,"source_sha256":sources,
        "binary_sha256":all_binary_hashes,"fixture_manifest_sha256":corpus.digest_file(fixture_manifest),
        "negative_fixtures":[],"prior_behaviour":[],"valid_controls":{},"pass":False,
        "timing_is_benchmark":False,"official":False,"physical_arm_execution":False}
    result=output/"stage.json";_write_report(result,report)
    for backend,exe in binaries.items():
        destination=folder/f"valid-{backend}.png"
        record=runtime.apply([valid]*4,image,destination,backend=backend,executable=exe,threads=4 if backend=="cpu" else 0,competition=True)
        report["valid_controls"][backend]={"runtime":record,"decoded_output_sha256":__import__("hashlib").sha256(io.load_image(destination).tobytes()).hexdigest()}
    if report["valid_controls"]["cpu"]["decoded_output_sha256"]!=report["valid_controls"]["cuda"]["decoded_output_sha256"]:
        raise RuntimeError("valid control CPU/CUDA output differs")
    if args.reuse_cpp_gate:
        proof=json.loads(args.reuse_cpp_gate.read_text(encoding="utf-8-sig"))
        for name,digest in proof["input_sha256"].items():
            if corpus.digest_file(ROOT/name)!=digest:raise RuntimeError("completed C++ gate code/binary/log changed")
        if proof["cpp_phase_gate"]["returncode"]!=0:raise RuntimeError("cannot reuse an unsuccessful C++ gate")
        report["cpp_phase_gate"]={**proof["cpp_phase_gate"],"reused_proof_sha256":corpus.digest_file(args.reuse_cpp_gate)}
    else:
        ctest=runtime._execute(["ctest","--test-dir",str(ROOT/"build-r32-format-cpu"),"--output-on-failure"])
        (output/"ctest.log").write_text(ctest["stdout"]+ctest["stderr"],encoding="utf-8")
        if ctest["returncode"]:raise RuntimeError("rebuilt C++ kernel/serialization/metadata gate failed")
        report["cpp_phase_gate"]={k:v for k,v in ctest.items() if k not in ("stdout","stderr")}
    _write_report(result,report)
    lib=load_library((ROOT/"build-r30-portable/libjshc_portable.dll").resolve())
    full_sources=[ROOT/"data/corpus-v1/cases/ccm-mild-s0-e8d21c5b"/f"lut{k}.lut256" for k in range(1,5)]
    def invoke(exe,backend,item,destination):
        path=casebook._path(item["path"]);target=item["target"]
        if target=="full_LUT_loader":
            command=[str(exe),"ref","--competition","-t","1","-i",str(image),"-o",str(destination),str(path),*map(str,full_sources[1:])]
        else:
            model_paths=[path,valid,valid,valid] if "loader" in target else [valid]*4
            input_path=image if "loader" in target else path
            command=[str(exe),"apply","--competition","-i",str(input_path),"-o",str(destination)]
            if backend=="cpu":command.extend(["-t","1"])
            command.extend(map(str,model_paths))
        return {**runtime._execute(command),"command":command}
    for item in definition["records"]:
        path=casebook._path(item["path"])
        if corpus.digest_file(path)!=item["sha256"]:raise RuntimeError("negative fixture changed")
        row={"id":item["id"],"target":item["target"],"sha256":item["sha256"],"native":{}}
        for backend,exe in binaries.items():
            if backend=="cuda" and item["target"]=="full_LUT_loader":continue
            destination=folder/f"{item['id']}-{backend}.png"
            record=invoke(exe,backend,item,destination)
            if record["returncode"]==0 or destination.exists():raise RuntimeError("native accepted invalid fixture: "+item["id"]+"/"+backend)
            row["native"][backend]={"returncode":record["returncode"],"stderr":record["stderr"],"command":record["command"],"output_created":False}
        if item["target"] in ("sparse_loader","Python_sparse_loader","competition_loader"):
            try:io.load_sparse(path,competition=True)
            except (ValueError,OSError):pass
            else:raise RuntimeError("Python accepted negative sparse fixture")
            data=path.read_bytes();blob=ct.create_string_buffer(data);model=Model()
            before=ct.string_at(ct.byref(model),ct.sizeof(model))
            status=lib.jshc_p_model_prepare(ct.byref(model),blob,len(data))
            if not status or before!=ct.string_at(ct.byref(model),ct.sizeof(model)):raise RuntimeError("portable C negative-format contract failed")
            row.update(python_sparse_rejected=True,portable_c_status=status,portable_c_output_unchanged=True)
        if item["id"] in ("nan-grid","infinite-grid","duplicate-grid","palette"):
            for backend,exe in frozen.items():
                destination=folder/f"{item['id']}-frozen-{backend}.png"
                record=invoke(exe,backend,item,destination)
                report["prior_behaviour"].append({"fixture":item["id"],"backend":backend,"returncode":record["returncode"],
                    "accepted":record["returncode"]==0,"output_created":destination.exists(),"stderr":record["stderr"]})
        report["negative_fixtures"].append(row);_write_report(result,report)
    historical_path=ROOT/"artifacts/r27-step/acceptance-stress-13-m33-adaptive.json"
    historical=json.loads(historical_path.read_text(encoding="utf-8"));expected=historical["backends"]["cpu"]
    models=[casebook._path(path) for path in expected["model_sha256"]]
    for path,digest in zip(models,expected["model_sha256"].values()):
        if corpus.digest_file(path)!=digest:raise RuntimeError("frozen model changed")
    listing=ROOT/"data/corpus-v1/benchmark100.txt"
    frames=[Path(line) for line in listing.read_text(encoding="utf-8").splitlines() if line]
    if len(frames)!=100:raise RuntimeError("valid frame cohort differs")
    truth_path=casebook._path(historical["sources"][0]["path"]).parent/"composite.lut256"
    if corpus.digest_file(truth_path)!=historical["reference_sha256"]:raise RuntimeError("frozen full reference changed")
    with tempfile.TemporaryDirectory(prefix="r32-valid-paths-") as temporary:
        temporary=Path(temporary);records={};cube_paths={}
        for backend,exe in binaries.items():
            raw=temporary/f"cube-{backend}.rgb";record=runtime.cube(models,raw,backend=backend,executable=exe,threads=4 if backend=="cpu" else 0,competition=True)
            if corpus.digest_file(raw)!=expected["mapped_cube_sha256"]:raise RuntimeError("rebuilt native cube differs from frozen output")
            cube_paths[backend]=raw;records[backend]={"cube_runtime":record,"mapped_cube_sha256":corpus.digest_file(raw)}
        with validation._mapped_full(cube_paths["cpu"]) as mapped,validation._mapped_full(truth_path) as truth:
            for backend,exe in binaries.items():
                raw=temporary/f"images-{backend}.rgb"
                record=runtime.verify(models,listing,backend=backend,executable=exe,threads=4 if backend=="cpu" else 0,competition=True,output=raw)
                if raw.stat().st_size!=100*1024*768*3:raise RuntimeError("valid 100-image output length differs")
                with raw.open("rb") as stream:
                    for path in frames:
                        rgb=io.load_image(path);actual=np.frombuffer(stream.read(rgb.nbytes),np.uint8).reshape(rgb.shape)
                        if not np.array_equal(actual,io.apply_full(mapped,rgb)):raise RuntimeError("native decoded image path differs from cube mapping")
                    if stream.read(1):raise RuntimeError("extra image output bytes")
                records[backend].update(image_runtime=record,image_count=100,images_sha256=corpus.digest_file(raw),all_image_outputs_equal_cube_lookup=True)
            report["valid_100_images"]=records
            photo_catalog=json.loads((ROOT/"datasets/problem16-photos-v1/catalog.json").read_text(encoding="utf-8"));photo_records=[]
            for photo in photo_catalog["images"]:
                path=ROOT/photo["path"];rgb=io.load_image(path);prediction=io.apply_full(mapped,rgb)
                row={"id":photo["id"],"input_sha256":corpus.digest_file(path),"quality":validation._stats(prediction,io.apply_full(truth,rgb))[0],"backends":{}}
                for backend,exe in binaries.items():
                    raw=temporary/f"{photo['id']}-{backend}.png"
                    record=runtime.apply(models,path,raw,backend=backend,executable=exe,threads=4 if backend=="cpu" else 0,competition=True)
                    if not np.array_equal(io.load_image(raw),prediction):raise RuntimeError("photo decoded image path differs")
                    row["backends"][backend]={"runtime":record,"actual_decoded_output_equal_cube":True}
                photo_records.append(row)
            report["photographs5"]={"cohort_sha256":photo_catalog["cohort_sha256"],"rows":photo_records,
                "known_source_family":True,"official_threshold_known":False,"is_100_image_qualification":False}
    if records["cpu"]["images_sha256"]!=records["cuda"]["images_sha256"]:raise RuntimeError("CPU/CUDA image bytes differ")
    for name,digest in sources.items():
        if corpus.digest_file(ROOT/name)!=digest:raise RuntimeError("source changed during concentrated gate")
    for name,digest in all_binary_hashes.items():
        if corpus.digest_file(ROOT/name)!=digest:raise RuntimeError("rebuilt or frozen binary changed")
    report.update(finished_utc=datetime.now(timezone.utc).isoformat(),pass_=True)
    report["pass"]=report.pop("pass_");_write_report(result,report)
    print(json.dumps({"pass":True,"negative_cpu":len(report["negative_fixtures"]),
        "negative_cuda":sum("cuda" in row["native"] for row in report["negative_fixtures"]),
        "negative_portable_c":sum("portable_c_status" in row for row in report["negative_fixtures"]),
        "valid_native_images_per_backend":105,"old_scan_binaries_unchanged":True}))


if __name__=="__main__":main()
