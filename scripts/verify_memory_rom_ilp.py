"""对固定8像素C99接口重放完整域、独立C99和保护页合同。"""
import argparse
from pathlib import Path
import ctypes as ct
import study_memory_rom as study
import verify_memory_rom_contract as contract
from study_memory_rom import ROOT,sha,read,save

def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--library',type=Path,required=True);p.add_argument('--roms',type=Path,required=True);p.add_argument('--data-root',type=Path,required=True);p.add_argument('--output',type=Path,required=True);a=p.parse_args()
    plan=ROOT/'experiments/memory-rom-ilp-v1.json'
    if any(sha(ROOT/n)!=v for n,v in read(plan)['source_sha256'].items()):raise ValueError('冻结源码变化')
    original=study.romlib
    def bind(path):
        d=original(path);d.jshc_mem_apply_ilp.argtypes=d.jshc_mem_apply.argtypes;d.jshc_mem_apply_ilp.restype=ct.c_int;d.jshc_mem_apply=d.jshc_mem_apply_ilp;return d
    study.romlib=bind;contract.romlib=bind
    a.output.mkdir(parents=True,exist_ok=False)
    sub=argparse.Namespace(**vars(a));sub.output=a.output/'full';study.verify(sub)
    # 保护页脚本的C99 oracle与AVX2相互验证；ILP原地另由全域和有限合同覆盖。
    import sys
    sys.argv=[__file__,'--library',str(a.library),'--roms',str(a.roms),'--output',str(a.output/'contract')];contract.main()
    save(a.output/'driver.json',dict(purpose=__doc__,plan_sha256=sha(plan),script_sha256=sha(__file__),full_sha256=sha(a.output/'full/results.json'),contract_sha256=sha(a.output/'contract/results.json')))
if __name__=='__main__':main()
