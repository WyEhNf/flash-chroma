"""Execute the frozen portable C object in AArch64 little/big endian QEMU.

This is emulator correctness evidence, never physical ARM speed/power evidence.
Each freestanding ELF borrows the exact four SLUT blobs and emits two complete
RGB8 output cubes. The host hashes specialized and generic streams separately
against prior independent native results; no new fitting or native rerun occurs.
Only Linux write/exit syscalls and local memcpy/memset are supplied by the test
harness. No ARM libc/sysroot, root installation, or binfmt registration is used.
"""
from __future__ import annotations

import argparse
from datetime import datetime,timezone
import hashlib
import json
from pathlib import Path
import shutil
import subprocess
import sys
import time

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/"python"))
from lutlab import casebook,corpus,io,runtime
from lutlab.entry import _write_report


def linux_path(path):
    path=Path(path).resolve()
    if path.drive.upper()!="F:":raise RuntimeError("this recorded WSL mount mapping only covers F:")
    return "/mnt/f/"+path.as_posix()[3:]


def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument("--output",type=Path,default=ROOT/"artifacts/r31-arm-execution")
    p.add_argument("--tools",type=Path,default=ROOT/"artifacts/r31-arm-tools/package/usr/bin")
    args=p.parse_args();args.output.mkdir(parents=True,exist_ok=True)
    compiler=shutil.which("clang");linker=shutil.which("ld.lld")
    if not compiler or not linker:raise RuntimeError("recorded Clang/LLD toolchain is required")
    source_names=["portable/src/jshc_portable.c","portable/include/jshc_portable.h","portable/verify_aarch64.c",
        "scripts/r31_arm_execution.py","scripts/r31_extract_qemu.sh"]
    sources={name:corpus.digest_file(ROOT/name) for name in source_names}
    previous_path=ROOT/"artifacts/r30-portable/stage.json";previous=json.loads(previous_path.read_text())
    if not previous["pass"]:raise RuntimeError("the portable stage must pass first")
    for name in ("portable/src/jshc_portable.c","portable/include/jshc_portable.h"):
        if previous["source_sha256"][name]!=sources[name]:raise RuntimeError("portable runtime changed after its staged proof")
    records={row["target"]:row for row in previous["cross_compile"]}
    report={"started_utc":datetime.now(timezone.utc).isoformat(),"source_sha256":sources,"scope":__doc__,
        "portable_stage_sha256":corpus.digest_file(previous_path),"execution_environment":"WSL Ubuntu 26.04 x86_64, QEMU user mode 10.2.1",
        "physical_arm_execution":False,"mobile_performance_measured":False,"official":False,"pass":False,"runs":[],
        "compiler_version":runtime._execute([compiler,"--version"]),"linker_version":runtime._execute([linker,"--version"])}
    result=args.output/"stage.json";_write_report(result,report)
    for historical in previous["historical_cubes"]:
        evidence=casebook._path(historical["evidence"])
        if corpus.digest_file(evidence)!=historical["evidence_sha256"]:raise RuntimeError("frozen native evidence changed")
        model_paths=[casebook._path(path) for path in historical["models_sha256"]]
        for path,digest in zip(model_paths,historical["models_sha256"].values()):
            if corpus.digest_file(path)!=digest:raise RuntimeError("serialized model changed")
        name=evidence.stem;folder=args.output/name;folder.mkdir(exist_ok=True)
        assembly=folder/"models.S";lines=[".section .rodata"]
        for i,path in enumerate(model_paths):
            lines.extend([".balign 8",".byte 0",f".global model_blob_{i}",f"model_blob_{i}:",
                f'.incbin "{path.as_posix()}"',f".global model_blob_{i}_end",f"model_blob_{i}_end:"])
        assembly.write_text("\n".join(lines)+"\n",encoding="utf-8")
        for target,triple,qemu_name in (("aarch64","aarch64-linux-gnu","qemu-aarch64"),
                                       ("aarch64-big-endian","aarch64_be-linux-gnu","qemu-aarch64_be")):
            core=ROOT/"artifacts/r30-portable"/f"{target}.o"
            if corpus.digest_file(core)!=records[target]["object_sha256"]:raise RuntimeError("frozen cross-compiled object changed")
            qemu=args.tools/qemu_name
            if not qemu.is_file():raise FileNotFoundError(qemu)
            elf=folder/f"{target}.elf"
            command=[compiler,"--target="+triple,"-fuse-ld=lld","-std=c99","-Os","-mgeneral-regs-only","-ffreestanding",
                "-fno-builtin","-fno-stack-protector","-fno-unwind-tables","-fno-asynchronous-unwind-tables",
                "-nostdlib","-static","-Wall","-Wextra","-Wconversion","-Werror","-I",str(ROOT/"portable/include"),
                str(ROOT/"portable/verify_aarch64.c"),str(core),str(assembly),"-Wl,-e,_start","-o",str(elf)]
            build=runtime._execute(command);(folder/f"{target}-build.log").write_text(build["stdout"]+build["stderr"],encoding="utf-8")
            if build["returncode"]:raise RuntimeError(f"freestanding ELF link failed: {target}; inspect build log")
            invoke=["wsl.exe","-d","Ubuntu","--exec",linux_path(qemu),linux_path(elf)]
            stderr=folder/f"{target}-stderr.log";digests=[];started=time.perf_counter()
            with stderr.open("wb") as error:
                process=subprocess.Popen(invoke,cwd=ROOT,stdout=subprocess.PIPE,stderr=error)
                try:
                    for variant in ("specialized","generic"):
                        remaining=io.FULL_NBYTES;digest=hashlib.sha256()
                        while remaining:
                            block=process.stdout.read(min(remaining,1024*1024))
                            if not block:raise RuntimeError("emulator ended before completing both RGB8 cubes")
                            remaining-=len(block);digest.update(block)
                        value=digest.hexdigest()
                        if value!=historical["mapped_cube_sha256"]:raise RuntimeError(f"{target}/{variant} differs from frozen native full cube")
                        digests.append({"variant":variant,"bytes":io.FULL_NBYTES,"sha256":value})
                    if process.stdout.read(1):raise RuntimeError("unexpected bytes after both complete cubes")
                    code=process.wait()
                    if code:raise RuntimeError(f"emulator exit status {code}; inspect stderr")
                finally:
                    process.stdout.close()
                    if process.poll() is None:process.terminate();process.wait()
            report["runs"].append({"source_evidence":historical["evidence"],"source_evidence_sha256":historical["evidence_sha256"],
                "model_sha256":historical["models_sha256"],"target":target,"elf_sha256":corpus.digest_file(elf),
                "elf_bytes":elf.stat().st_size,"frozen_core_object_sha256":corpus.digest_file(core),
                "qemu_sha256":corpus.digest_file(qemu),"compile_command":command,"execution_command":invoke,
                "exit_code":0,"streams":digests,"elapsed_correctness_seconds_not_benchmark":time.perf_counter()-started,
                "actual_emulated_execution":True,"physical_arm_execution":False})
            _write_report(result,report);print(f"[arm] {name}/{target}: specialized and generic whole cubes matched frozen native",flush=True)
    for name,digest in sources.items():
        if corpus.digest_file(ROOT/name)!=digest:raise RuntimeError("source changed during ARM verification")
    if corpus.digest_file(previous_path)!=report["portable_stage_sha256"]:raise RuntimeError("portable stage changed")
    report.update(pass_=True,finished_utc=datetime.now(timezone.utc).isoformat(),
        emulated_colour_evaluations=len(report["runs"])*2*256**3)
    report["pass"]=report.pop("pass_");_write_report(result,report)
    print(json.dumps({"pass":True,"target_case_runs":len(report["runs"]),"complete_cube_streams":len(report["runs"])*2,
        "physical_arm_execution":False,"mobile_performance_measured":False}))


if __name__=="__main__":main()
