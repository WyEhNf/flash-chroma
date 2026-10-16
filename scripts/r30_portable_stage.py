"""One staged C99/FFI gate: frozen native whole-cube bytes, uint64 oracle,
row/tile/in-place/error contracts, and cross-compilation (not ARM execution).

This is correctness/deployment evidence; observed execution time is not a paired
benchmark and does not select a fastest kernel. No fitting or old native tests
are repeated. Source/old model/evidence hashes are bound to the result.
"""
from __future__ import annotations

import argparse
import ast
import ctypes as ct
from datetime import datetime, timezone
import hashlib
import itertools
import json
from pathlib import Path
import shutil
import sys

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/"python"))
import numpy as np
from lutlab import casebook,corpus,io,runtime
from lutlab.entry import _write_report


class Model(ct.Structure):
    _fields_=[("ready",ct.c_uint32),("m",ct.c_uint32),("flags",ct.c_uint32),("constant_rgb",ct.c_uint32),
        ("blob",ct.c_void_p),("blob_bytes",ct.c_size_t),("index",ct.c_void_p),("fraction_le",ct.c_void_p),
        ("nodes",ct.c_void_p),("curve",(ct.c_uint32*256)*3)]


class Chain(ct.Structure):
    _fields_=[("ready",ct.c_uint32),("options",ct.c_uint32),("models",ct.POINTER(Model)*4),
        ("path",ct.c_uint8*4),("effective_one_hot",ct.c_uint8*4)]


def load_library(path):
    library=ct.CDLL(str(path))
    for name in ("jshc_p_model_bytes","jshc_p_chain_bytes"):
        fn=getattr(library,name);fn.argtypes=[];fn.restype=ct.c_size_t
    library.jshc_p_abi_version.argtypes=[];library.jshc_p_abi_version.restype=ct.c_uint32
    assert library.jshc_p_abi_version()==1
    assert (library.jshc_p_model_bytes(),library.jshc_p_chain_bytes())==(ct.sizeof(Model),ct.sizeof(Chain))
    library.jshc_p_model_prepare.argtypes=[ct.POINTER(Model),ct.c_void_p,ct.c_size_t]
    library.jshc_p_chain_prepare.argtypes=[ct.POINTER(Chain),ct.POINTER(ct.POINTER(Model)),ct.c_uint32]
    library.jshc_p_apply_rgb8.argtypes=[ct.POINTER(Chain),ct.c_void_p,ct.c_size_t,ct.c_size_t,
        ct.c_void_p,ct.c_size_t,ct.c_size_t,ct.c_size_t,ct.c_size_t]
    return library


class Prepared:
    def __init__(self,library,paths):
        self.library=library;self.buffers=[];self.models=[];self.sparse=[]
        for path in paths:
            value=path.read_bytes();buffer=ct.create_string_buffer(len(value)+1)
            ct.memmove(ct.addressof(buffer)+1,value,len(value)) # intentionally unaligned SLUT
            model=Model();status=library.jshc_p_model_prepare(ct.byref(model),ct.addressof(buffer)+1,len(value))
            if status:raise RuntimeError(f"C preparation rejected {path}: {status}")
            self.buffers.append(buffer);self.models.append(model);self.sparse.append(io.load_sparse(path,competition=True))
        self.pointers=(ct.POINTER(Model)*4)(*[ct.pointer(m) for m in self.models])
        self.chain=Chain();self.generic=Chain()
        assert library.jshc_p_chain_prepare(ct.byref(self.chain),self.pointers,0)==0
        assert library.jshc_p_chain_prepare(ct.byref(self.generic),self.pointers,1)==0

    def apply(self,values,generic=False):
        values=np.ascontiguousarray(values,dtype=np.uint8);out=np.empty_like(values)
        n=values.size//3;chain=self.generic if generic else self.chain
        status=self.library.jshc_p_apply_rgb8(ct.byref(chain),values.ctypes.data,values.nbytes,n*3,
            out.ctypes.data,out.nbytes,n*3,n,1)
        if status:raise RuntimeError(f"C execution failed: {status}")
        return out


def oracle64(models,values):
    """Stable axis permutation plus nonnegative uint64 barycentric sums.

    Uses complete independently loaded serialized axis tables. Does not call any
    native runtime or the fitting/interpolation implementation under test.
    """
    out=values.copy().reshape(-1,3)
    for model in models:
        idx,frac=model.tables();m=model.m;n=len(out)
        fractions=np.stack([frac[a,out[:,a]] for a in range(3)],axis=1).astype(np.int64)
        order=np.argsort(-fractions,axis=1,kind="stable")
        sorted_fraction=np.take_along_axis(fractions,order,axis=1)
        strides=np.array([m*m,m,1],np.int64)
        base=sum(idx[a,out[:,a]].astype(np.int64)*strides[a] for a in range(3))
        vertices=np.stack([base,base+strides[order[:,0]],
            base+strides[order[:,0]]+strides[order[:,1]],base+strides.sum()],axis=1)
        weights=np.stack([65536-sorted_fraction[:,0],sorted_fraction[:,0]-sorted_fraction[:,1],
            sorted_fraction[:,1]-sorted_fraction[:,2],sorted_fraction[:,2]],axis=1).astype(np.uint64)
        nodes=model.nodes.reshape(-1,3)[vertices].astype(np.uint64)
        result=(np.sum(weights[:,:,None]*nodes,axis=1,dtype=np.uint64)+32768)>>16
        assert result.shape==(n,3) and np.all(result<=255)
        out=result.astype(np.uint8)
    return out.reshape(values.shape)


def synthetic_models(folder):
    folder.mkdir(parents=True,exist_ok=True);rng=np.random.default_rng(2026101630)
    records={}
    for kind in ("general","separable","onehot_prefix","constant"):
        paths=[]
        for stage,m in enumerate((17,18,25,33)):
            grid=io.uniform_grid(m);idx,frac=io.axis_tables(grid)
            nodes=rng.integers(0,256,(m,m,m,3),dtype=np.uint8)
            if kind=="general":
                choices=np.array([0,1,32767,32768,32769,65535,65536],np.uint32)
                frac=choices[(np.arange(768).reshape(3,256)+stage)%len(choices)]
                idx=rng.integers(0,m-1,(3,256),dtype=np.uint8)
            if kind=="separable" or (kind=="onehot_prefix" and stage==3):
                curves=rng.integers(0,256,(3,m),dtype=np.uint8)
                axes=np.indices((m,m,m))
                nodes=np.stack([curves[0,axes[(stage+1)%3]],np.full((m,m,m),37+stage,np.uint8),
                    curves[2,axes[(stage+2)%3]]],axis=-1)
            if kind=="onehot_prefix" and stage==0:
                nodes=np.array([0,64,128,255],np.uint8)[rng.integers(0,4,(m,m,m,3))]
                frac=np.where(frac>=32768,65536,0).astype(np.uint32)
            if kind=="onehot_prefix" and stage==1:
                frac[:]=32768;frac[:,[0,64,128]]=0;frac[:,255]=65536
            if kind=="constant":nodes[:]=[17+stage,71+stage,233-stage]
            path=folder/f"{kind}-stage{stage+1}-m{m}.slut"
            io.save_sparse(path,io.SparseLut(grid,nodes,idx,frac));paths.append(path)
        records[kind]=paths
    # Fractional nonuniform metadata, integer endpoint handling and unequal m.
    grid=np.stack([np.r_[0,np.sort(rng.choice(np.arange(1,255),24,replace=False)),255] for _ in range(3)]).astype(float)
    nodes=rng.integers(0,256,(26,26,26,3),dtype=np.uint8)
    path=folder/"nonuniform-m26.slut";io.save_sparse(path,io.SparseLut(grid,nodes))
    records["nonuniform"]=[path,*records["general"][1:]]
    return records


def api_contracts(prepared):
    lib=prepared.library;chain=ct.byref(prepared.chain);checks=[]
    width,height,stride=13,7,47;rng=np.random.default_rng(3030)
    source=rng.integers(0,256,64+height*stride+64,dtype=np.uint8)
    destination=np.full_like(source,0xa5);start=65
    # Odd address and row strides; source/destination padding may differ.
    expected=oracle64(prepared.sparse,np.stack([source[start+y*stride:start+y*stride+width*3].reshape(width,3) for y in range(height)]))
    def apply(src,src_n,src_stride,dst,dst_n,dst_stride,w,h):
        return lib.jshc_p_apply_rgb8(chain,src,src_n,src_stride,dst,dst_n,dst_stride,w,h)
    status=apply(source.ctypes.data+start,source.nbytes-start,stride,destination.ctypes.data+start,
        destination.nbytes-start,stride,width,height)
    assert status==0
    written=np.zeros(len(source),bool)
    for y in range(height):
        sl=slice(start+y*stride,start+y*stride+width*3);written[sl]=True
        assert np.array_equal(destination[sl].reshape(width,3),expected[y])
    assert np.all(destination[~written]==0xa5);checks.append("unaligned_strided_rows_padding_and_canaries")
    tiled=np.full_like(source,0xa5)
    for y in range(0,height,3):
        for x in range(0,width,5):
            offset=start+y*stride+3*x
            assert apply(source.ctypes.data+offset,source.nbytes-offset,stride,tiled.ctypes.data+offset,
                tiled.nbytes-offset,stride,min(5,width-x),min(3,height-y))==0
    assert np.array_equal(tiled,destination);checks.append("row_and_column_tiles")
    inplace=source.copy()
    assert apply(inplace.ctypes.data+start,inplace.nbytes-start,stride,inplace.ctypes.data+start,
        inplace.nbytes-start,stride,width,height)==0
    assert np.array_equal(inplace[written],destination[written]) and np.array_equal(inplace[~written],source[~written])
    checks.append("exact_in_place")
    before=destination.copy();limit=ct.c_size_t(-1).value
    errors=[("short_input",source.ctypes.data,2,3,destination.ctypes.data,3,3,1,1,3),
        ("short_stride",source.ctypes.data,100,2,destination.ctypes.data,100,3,1,2,3),
        ("short_output",source.ctypes.data,100,3,destination.ctypes.data,2,3,1,1,3),
        ("width_overflow",source.ctypes.data,100,3,destination.ctypes.data,100,3,limit,1,5),
        ("height_overflow",source.ctypes.data,limit,3,destination.ctypes.data,limit,3,1,limit,5),
        ("null_source",0,3,3,destination.ctypes.data,3,3,1,1,1)]
    for name,*args,expected_status in errors:
        assert apply(*args)==expected_status,name
        assert np.array_equal(before,destination),name
        checks.append(name+"_before_output_write")
    duplicate=source.copy();before_duplicate=duplicate.copy()
    assert apply(duplicate.ctypes.data,99,3,duplicate.ctypes.data+1,99,3,1,2)==6
    assert np.array_equal(duplicate,before_duplicate);checks.append("partial_overlap_reject")
    assert apply(0,0,0,0,0,0,limit,0)==0;checks.append("zero_height_noop")
    assert apply(0,0,0,0,0,0,0,limit)==0;checks.append("zero_width_noop")
    assert apply(source.ctypes.data,3,3,prepared.models[0].nodes,3,3,1,1)==6
    assert apply(source.ctypes.data,3,3,ct.addressof(prepared.models[0]),3,3,1,1)==6
    assert apply(source.ctypes.data,3,3,ct.addressof(prepared.chain),3,3,1,1)==6
    checks.append("destination_model_blob_workspace_and_chain_overlap_reject")
    blob=prepared.models[0].blob;size=prepared.models[0].blob_bytes
    assert lib.jshc_p_model_prepare(ct.cast(blob,ct.POINTER(Model)),blob,size)==6
    assert lib.jshc_p_chain_prepare(ct.cast(ct.pointer(prepared.models[0]),ct.POINTER(Chain)),prepared.pointers,0)==6
    checks.append("preparation_workspace_overlap_reject")
    scratch=Chain();assert lib.jshc_p_chain_prepare(ct.byref(scratch),prepared.pointers,2)==4
    pointers=(ct.POINTER(Model)*4)(ct.pointer(Model()),*[ct.pointer(m) for m in prepared.models[1:]])
    assert lib.jshc_p_chain_prepare(ct.byref(scratch),pointers,0)==7
    checks.append("unknown_options_and_unprepared_model_reject")
    return checks


def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument("--library",type=Path,default=ROOT/"build-r30-portable/libjshc_portable.dll")
    p.add_argument("--output",type=Path,default=ROOT/"artifacts/r30-portable")
    p.add_argument("--resume-from",type=Path,help="reuse completed numerical evidence only with identical C/FFI/oracle code")
    p.add_argument("--previous-driver",type=Path,help="immutable driver snapshot bound to the resumed result")
    args=p.parse_args();args.output.mkdir(parents=True,exist_ok=True)
    source_names=["portable/include/jshc_portable.h","portable/src/jshc_portable.c","portable/CMakeLists.txt",
        "scripts/r30_portable_stage.py","python/lutlab/io.py"]
    sources={n:corpus.digest_file(ROOT/n) for n in source_names};lib=load_library(args.library.resolve())
    library_hash=corpus.digest_file(args.library)
    previous=None
    if args.resume_from:
        if args.previous_driver is None:p.error("--resume-from requires --previous-driver")
        previous=json.loads(args.resume_from.read_text())
        if previous["library_sha256"]!=library_hash:raise RuntimeError("cannot reuse evidence from a different native library")
        for name,digest in previous["source_sha256"].items():
            if name!="scripts/r30_portable_stage.py" and corpus.digest_file(ROOT/name)!=digest:
                raise RuntimeError("native/format source changed since the completed evidence")
        if corpus.digest_file(args.previous_driver)!=previous["source_sha256"]["scripts/r30_portable_stage.py"]:
            raise RuntimeError("previous driver snapshot differs from its recorded hash")
        old=args.previous_driver.read_text();current=Path(__file__).read_text()
        def definitions(value):
            return {node.name:ast.dump(node,include_attributes=False) for node in ast.parse(value).body
                if isinstance(node,(ast.FunctionDef,ast.ClassDef)) and node.name!="main"}
        if definitions(old)!=definitions(current):raise RuntimeError("FFI, oracle or contract helpers changed; numerical checks must be rerun")
    report={"started_utc":datetime.now(timezone.utc).isoformat(),"scope":__doc__,"source_sha256":sources,
        "library_sha256":library_hash,"abi":1,"prepared_model_bytes":ct.sizeof(Model),"prepared_chain_bytes":ct.sizeof(Chain),
        "synthetic":{},"historical_cubes":[],"format_rejections":[],"cross_compile":[],"pass":False,
        "arm_execution_verified":False,"mobile_performance_measured":False,"official":False}
    if previous:report["resumed_evidence"]={"path":str(args.resume_from),"sha256":corpus.digest_file(args.resume_from),
        "driver_sha256":corpus.digest_file(args.previous_driver),"scope":"same native bytes and identical FFI/oracle/contract helper AST; preserve original incomplete stage"}
    result=args.output/"stage.json";_write_report(result,report)
    fixture_sets=synthetic_models(args.output/"fixtures")
    rng=np.random.default_rng(1630)
    points=np.unique(np.concatenate([rng.integers(0,256,(65536,3),dtype=np.uint8),
        np.array(list(itertools.product([0,1,2,63,64,127,128,129,254,255],repeat=3)),np.uint8)]),axis=0)
    for kind,paths in fixture_sets.items():
        prepared=Prepared(lib,paths);oracle=oracle64(prepared.sparse,points)
        assert np.array_equal(prepared.apply(points),oracle),kind
        assert np.array_equal(prepared.apply(points,True),oracle),kind+" generic"
        if kind=="onehot_prefix":assert list(prepared.chain.path)==[2,2,0,1]
        if kind=="constant":assert list(prepared.chain.path)==[3]*4
        report["synthetic"][kind]={"colors":len(points),"paths":list(prepared.chain.path),"uint64_oracle_equal":True,
            "models_sha256":{str(path.relative_to(ROOT)):corpus.digest_file(path) for path in paths}}
        if kind=="general":report["api_contracts"]=api_contracts(prepared)
    formats=json.loads((ROOT/"datasets/problem16-v1/invalid-formats.json").read_text())
    for item in formats["records"]:
        if item["target"]!="sparse_loader":continue
        path=casebook._path(item["path"]);data=path.read_bytes()
        assert corpus.digest_file(path)==item["sha256"]
        blob=ct.create_string_buffer(data);out=Model();ct.memset(ct.byref(out),0xa5,ct.sizeof(out))
        before=ct.string_at(ct.byref(out),ct.sizeof(out));status=lib.jshc_p_model_prepare(ct.byref(out),blob,len(data))
        assert status!=0 and before==ct.string_at(ct.byref(out),ct.sizeof(out)),item["id"]
        try:io.load_sparse(path,competition=True)
        except (ValueError,IOError):pass
        else:raise AssertionError("Python unexpectedly accepted fixture "+item["id"])
        report["format_rejections"].append({"id":item["id"],"sha256":item["sha256"],"c_status":status,"python_rejects":True})
    _write_report(result,report)
    for relative in ("artifacts/r25-full/acceptance-clip-7-m17-full.json",
                     "artifacts/r25-full/acceptance-film-11-m18-full.json",
                     "artifacts/r27-step/acceptance-stress-13-m33-adaptive.json"):
        path=ROOT/relative;historical=json.loads(path.read_text());reference=historical["backends"]["cpu"]
        model_hashes=reference["model_sha256"];paths=[casebook._path(name) for name in model_hashes]
        for model_path,digest in zip(paths,model_hashes.values()):assert corpus.digest_file(model_path)==digest
        prepared=Prepared(lib,paths)
        if "r27-step" in relative:
            assert list(prepared.chain.path)==[1,1,2,0]
            assert list(prepared.chain.effective_one_hot)==[0,1,1,0]
        prior=next((row for row in previous["historical_cubes"] if row["evidence"]==relative),None) if previous else None
        if prior:
            if (prior["evidence_sha256"]!=corpus.digest_file(path) or prior["models_sha256"]!={str(p.relative_to(ROOT)):corpus.digest_file(p) for p in paths}
                    or prior["mapped_cube_sha256"]!=reference["mapped_cube_sha256"] or prior["paths"]!=list(prepared.chain.path)
                    or not prior["specialized_and_generic_equal_frozen_native"]):
                raise RuntimeError("previous full-cube evidence no longer matches its source and native model bytes")
            report["historical_cubes"].append({**prior,"reused_from_sha256":corpus.digest_file(args.resume_from)})
            _write_report(result,report);print(f"[portable] {relative}: verified completed cube evidence reused",flush=True);continue
        hashes=[hashlib.sha256(),hashlib.sha256()]
        for begin in range(0,256,4):
            keys=np.arange(begin*65536,(begin+4)*65536,dtype=np.uint32)
            rgb=np.stack([keys>>16,(keys>>8)&255,keys&255],axis=1).astype(np.uint8)
            a,b=prepared.apply(rgb),prepared.apply(rgb,True)
            assert np.array_equal(a,b)
            hashes[0].update(a.tobytes());hashes[1].update(b.tobytes())
        assert hashes[0].hexdigest()==hashes[1].hexdigest()==reference["mapped_cube_sha256"],relative
        report["historical_cubes"].append({"evidence":relative,"evidence_sha256":corpus.digest_file(path),
            "models_sha256":{str(p.relative_to(ROOT)):corpus.digest_file(p) for p in paths},"colors":256**3,
            "mapped_cube_sha256":hashes[0].hexdigest(),"specialized_and_generic_equal_frozen_native":True,
            "paths":list(prepared.chain.path),"model_flags":[m.flags for m in prepared.models]})
        _write_report(result,report);print(f"[portable] {relative}: full RGB8 cube matched frozen native bytes",flush=True)
    clang=shutil.which("clang")
    if clang:
        for name,flags in (("cortex-m4",["--target=arm-none-eabi","-mcpu=cortex-m4","-mthumb"]),
                           ("aarch64",["--target=aarch64-none-elf","-mgeneral-regs-only"]),
                           ("aarch64-big-endian",["--target=aarch64_be-none-elf","-mgeneral-regs-only"]),
                           ("riscv32",["--target=riscv32-none-elf","-march=rv32im","-mabi=ilp32"])):
            obj=args.output/f"{name}.o"
            command=[clang,*flags,"-std=c99","-Os","-ffreestanding","-fno-builtin","-Wall","-Wextra","-Wconversion","-Werror",
                "-I",str(ROOT/"portable/include"),"-c",str(ROOT/"portable/src/jshc_portable.c"),"-o",str(obj)]
            record=runtime._execute(command);(args.output/f"compile-{name}.log").write_text(record["stdout"]+record["stderr"],encoding="utf-8")
            if record["returncode"]:raise RuntimeError(f"cross-compilation failed: {name}")
            report["cross_compile"].append({"target":name,"execution_verified":False,"command":command,
                "object_bytes":obj.stat().st_size,"object_sha256":corpus.digest_file(obj),"returncode":0})
    else:report["cross_compile_unavailable"]="clang not found"
    for name,digest in sources.items():assert corpus.digest_file(ROOT/name)==digest
    assert corpus.digest_file(args.library)==library_hash
    report.update(finished_utc=datetime.now(timezone.utc).isoformat(),pass_=True)
    report["pass"]=report.pop("pass_");_write_report(result,report)
    print(json.dumps({"pass":True,"historical_full_cubes":len(report["historical_cubes"]),
        "synthetic_oracle_batches":len(report["synthetic"]),"api_contracts":len(report["api_contracts"]),
        "format_rejections":len(report["format_rejections"]),"cross_compile_only":len(report["cross_compile"])}))


if __name__=="__main__":main()
