"""用原290 DLL、固定64种指针对齐和只读VEH定位首次访问异常；无性能。"""
from __future__ import annotations
import argparse
import ctypes as ct
import hashlib
import json
import os
from pathlib import Path
import struct
import subprocess
import sys

ROOT=Path(__file__).resolve().parents[1]
sys.path[:0]=[str(ROOT/'scripts')]
from check_direct_sentinel_native_v2 import BUILD,Library,sha,bind_to
import numpy as np

OUT=ROOT/'artifacts/p16-direct-sentinel-v2-alignment-diagnose-v1'
PROBE=ROOT/'artifacts/p16-exception-probe-build-v1/libp16_exception_probe.dll'
DLL_SHA='cbc670dbdb1b6bb39fe1b5994d909c1424308f8e4fad03f356b05740b3016154'

class Record(ct.Structure):
    _fields_=[('version',ct.c_uint32),('seen',ct.c_uint32)]+[(name,ct.c_uint64) for name in ('code','rip','rsp','rbp','address','rax','rbx','rcx','rdx','rsi','rdi','r8','r9','r10','r11','r12','r13','r14','r15')]

def child():
    dirs=[os.add_dll_directory('E:/mingw64/bin'),os.add_dll_directory(str(BUILD)),os.add_dll_directory(str(PROBE.parent))]
    probe=ct.CDLL(str(PROBE));assert ct.sizeof(Record)==160
    for name in ('p16_probe_install','p16_probe_clear','p16_probe_uninstall'):
        function=getattr(probe,name);function.argtypes=[];function.restype=ct.c_int
    probe.p16_probe_read.argtypes=[ct.POINTER(Record),ct.c_size_t];probe.p16_probe_read.restype=ct.c_int
    assert probe.p16_probe_install()==0
    directory=ROOT/'artifacts/p16-direct-sentinel-quality-v1/synthetic';models=[directory/'256-first.slut',*[directory/'256-tail.slut']*3];sides=[directory/'side.bin',None,None,None]
    original=json.loads((ROOT/'artifacts/p16-direct-sentinel-quality-frozen-v1/frozen.json').read_text(encoding='utf-8'))['libraries']['old87']
    baseline=Library(original['path'],original['sha256']);dll=BUILD/'libjshc_direct_sentinel.dll';assert sha(dll)==DLL_SHA;library=Library(dll,DLL_SHA)
    sample=np.concatenate((np.random.default_rng(2026102416).integers(0,256,(4096,3),dtype=np.uint8),np.array([[0,0,0],[255,255,255]],np.uint8)))
    with baseline.chain(models,sides) as old:expected=old.apply(sample.copy(),kernel='scalar',threads=1)
    to=bind_to(library.dll);u8=ct.POINTER(ct.c_uint8);error=ct.create_string_buffer(1024)
    parent_buffer=np.empty(sample.nbytes+128,np.uint8);target_buffer=np.empty(sample.nbytes+128,np.uint8)
    rows=[]
    with library.chain(models,sides) as chain:
        for route in ('inplace','to'):
            for alignment in range(64):
                source_offset=(alignment-int(parent_buffer.ctypes.data)%64)%64 if route=='inplace' else (-int(parent_buffer.ctypes.data))%64
                target_offset=(alignment-int(target_buffer.ctypes.data)%64)%64
                source=parent_buffer[source_offset:source_offset+sample.nbytes].reshape(-1,3);destination=source if route=='inplace' else target_buffer[target_offset:target_offset+sample.nbytes].reshape(-1,3)
                parent_buffer.fill(0xa7);target_buffer.fill(0xa7);source[:]=sample
                row={'route':route,'alignment':alignment,'source_address':int(source.ctypes.data),'destination_address':int(destination.ctypes.data),'requested_threads':4,'pixels':len(source),'blocks':1}
                assert probe.p16_probe_clear()==0
                try:
                    if route=='inplace':actual=chain.apply(source,kernel='avx2',threads=4)
                    else:
                        code=to(chain.handle,source.ctypes.data_as(u8),destination.ctypes.data_as(u8),source.nbytes,1,4,error,len(error))
                        if code:raise RuntimeError(error.value.decode('utf-8','replace'))
                        actual=destination
                except Exception as failure:
                    record=Record();assert probe.p16_probe_read(ct.byref(record),160)==0
                    row.update({'exception_type':type(failure).__name__,'error':str(failure),'registers':{name:getattr(record,name) for name,_ in Record._fields_},'dll_module_base':library.dll._handle})
                    module=ct.c_void_p();kernel=ct.WinDLL('kernel32',use_last_error=True)
                    kernel.GetModuleHandleExW.argtypes=[ct.c_uint32,ct.c_void_p,ct.POINTER(ct.c_void_p)];kernel.GetModuleHandleExW.restype=ct.c_int
                    if record.rip and kernel.GetModuleHandleExW(6,ct.c_void_p(record.rip),ct.byref(module)):
                        name=ct.create_unicode_buffer(32768);kernel.GetModuleFileNameW.argtypes=[ct.c_void_p,ct.c_wchar_p,ct.c_uint32];kernel.GetModuleFileNameW.restype=ct.c_uint32
                        if kernel.GetModuleFileNameW(module,name,len(name)):
                            data=Path(name.value).read_bytes();nt=struct.unpack_from('<I',data,60)[0];image_base=struct.unpack_from('<Q',data,nt+48)[0]
                            row.update({'fault_module':name.value,'fault_module_base':module.value,'fault_rva':record.rip-module.value,'preferred_image_base':image_base,'preferred_fault_address':image_base+record.rip-module.value,'fault_module_sha256':hashlib.sha256(data).hexdigest()})
                    rows.append(row);print(json.dumps({'completed':False,'rows':rows,'performance_calls':0}),flush=True);os._exit(2)
                np.testing.assert_array_equal(actual,expected)
                if route=='to':np.testing.assert_array_equal(source,sample)
                row.update({'passed':True,'output_sha256':hashlib.sha256(actual).hexdigest()});rows.append(row)
    assert probe.p16_probe_uninstall()==0
    print(json.dumps({'completed':True,'rows':rows,'performance_calls':0}),flush=True)

def parent():
    if OUT.exists():raise FileExistsError('不覆盖对齐定位')
    probe_receipt=json.loads((PROBE.parent/'receipt.json').read_text(encoding='utf-8'))
    if probe_receipt['returncode'] or sha(PROBE)!=probe_receipt['dll_sha256']:raise ValueError('观察器构建身份不同')
    frozen_path=ROOT/'artifacts/p16-direct-sentinel-quality-frozen-v1/frozen.json';frozen=json.loads(frozen_path.read_text(encoding='utf-8'))
    for name,expected in frozen['sources_sha256'].items():
        if sha(ROOT/name)!=expected:raise ValueError('原失败源变更')
    OUT.mkdir(parents=True)
    protocol={'purpose':'原DLL的固定64种源/目标对齐定位，不覆盖V1或修复，不计时','checker_sha256':sha(__file__),'probe_sha256':sha(PROBE),'probe_receipt_sha256':sha(PROBE.parent/'receipt.json'),'quality_frozen_sha256':sha(frozen_path),'dll_sha256':DLL_SHA,'maximum_cases':128,'stop_on_first_exception':True,'performance_calls':0}
    (OUT/'checker.py').write_bytes(Path(__file__).read_bytes());(OUT/'protocol.json').write_text(json.dumps(protocol,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    env=os.environ.copy();env['PATH']='E:/mingw64/bin'+os.pathsep+env['PATH'];env['PYTHONIOENCODING']='utf-8'
    result=subprocess.run([sys.executable,str(Path(__file__)),'--child'],cwd=ROOT,env=env,capture_output=True,check=False)
    (OUT/'stdout.txt').write_bytes(result.stdout);(OUT/'stderr.txt').write_bytes(result.stderr)
    (OUT/'execution.json').write_text(json.dumps({'returncode':result.returncode,'protocol_sha256':sha(OUT/'protocol.json'),'stdout_sha256':hashlib.sha256(result.stdout).hexdigest(),'stderr_sha256':hashlib.sha256(result.stderr).hexdigest(),'performance_calls':0},indent=2)+'\n',encoding='utf-8')
    if result.stdout:
        parsed=json.loads(result.stdout);(OUT/'results.json').write_text(json.dumps(parsed,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
        print(json.dumps({'returncode':result.returncode,'completed':parsed['completed'],'cases_observed':len(parsed['rows']),'last':parsed['rows'][-1],'performance_calls':0}))
    else:print(json.dumps({'returncode':result.returncode,'no_diagnostic_stdout':True,'performance_calls':0}))

def main():
    parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('--child',action='store_true');args=parser.parse_args()
    if args.child:child()
    else:parent()

if __name__=='__main__':main()
