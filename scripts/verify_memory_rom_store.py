"""对固定8像素C99接口重放完整域、独立C99和保护页合同。"""
import argparse
from pathlib import Path
import ctypes as ct
import numpy as np
import study_memory_rom as study
import verify_memory_rom_contract as contract
from study_memory_rom import ROOT,sha,read,save

def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--library',type=Path,required=True);p.add_argument('--roms',type=Path,required=True);p.add_argument('--data-root',type=Path,required=True);p.add_argument('--output',type=Path,required=True);a=p.parse_args()
    plan=ROOT/'experiments/memory-rom-store-v1.json'
    if any(sha(ROOT/n)!=v for n,v in read(plan)['source_sha256'].items()):raise ValueError('冻结源码变化')
    original=study.romlib
    def bind(path):
        d=original(path);d.jshc_mem_apply_store.argtypes=d.jshc_mem_apply.argtypes;d.jshc_mem_apply_store.restype=ct.c_int;d.jshc_mem_apply=d.jshc_mem_apply_store;return d
    study.romlib=bind;contract.romlib=bind
    a.output.mkdir(parents=True,exist_ok=False)
    sub=argparse.Namespace(**vars(a));sub.output=a.output/'full';study.verify(sub)
    # 保护页脚本的C99 oracle与AVX2相互验证；ILP原地另由全域和有限合同覆盖。
    import sys
    sys.argv=[__file__,'--library',str(a.library),'--roms',str(a.roms),'--output',str(a.output/'contract')];contract.main()
    # 新组内4字节写必须直接在C99后端检查目标末尾保护页，不能由AVX2替代。
    d=original(a.library);pure=original(a.library.parent/'jshc_memory_c99.dll')
    pure.jshc_mem_apply_store.argtypes=pure.jshc_mem_apply.argtypes
    alloc=ct.windll.kernel32.VirtualAlloc;alloc.argtypes=[ct.c_void_p,ct.c_size_t,ct.c_uint32,ct.c_uint32];alloc.restype=ct.c_void_p
    protect=ct.windll.kernel32.VirtualProtect;protect.argtypes=[ct.c_void_p,ct.c_size_t,ct.c_uint32,ct.POINTER(ct.c_uint32)]
    free=ct.windll.kernel32.VirtualFree;free.argtypes=[ct.c_void_p,ct.c_size_t,ct.c_uint32]
    rng=np.random.default_rng(2026102404);guards=0
    for bits in (0,4,6,8,10):
        model,keep=study.loadrom(d,a.roms/f'rom-{bits}.bin')
        for n in (1,7,8,9,15,16,17,31,32,63,64,65,4096,65536,65537):
            span=((3*n+4095)//4096)*4096;address=alloc(None,span+4096,0x3000,4)
            if not address:raise ct.WinError()
            old=ct.c_uint32();target=address+span-3*n
            if not protect(address+span,4096,1,ct.byref(old)):raise ct.WinError()
            try:
                src=rng.integers(0,256,3*n,dtype=np.uint8);expected=np.empty_like(src)
                if d.jshc_mem_apply_parallel(ct.byref(model),src.ctypes.data_as(study.U8),expected.ctypes.data_as(study.U8),n,1,1):raise AssertionError('AVX2 oracle拒绝')
                for inplace in (False,True):
                    ct.memmove(target,src.ctypes.data,3*n)
                    source=ct.cast(target,study.U8) if inplace else src.ctypes.data_as(study.U8)
                    if pure.jshc_mem_apply_store(ct.byref(model),source,ct.cast(target,study.U8),n) or ct.string_at(target,3*n)!=bytes(expected):raise AssertionError('纯C99保护页错误')
                    guards+=1
            finally:free(address,0,0x8000)
    save(a.output/'driver.json',dict(purpose=__doc__,plan_sha256=sha(plan),script_sha256=sha(__file__),pure_c99_guard_cases=guards,full_sha256=sha(a.output/'full/results.json'),contract_sha256=sha(a.output/'contract/results.json')))
if __name__=='__main__':main()
