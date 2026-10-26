"""补充冻结稀疏句柄3级fallback合同，保留原有限合同未覆盖3级的事实。"""
import argparse
import hashlib
from pathlib import Path
import numpy as np
from verify_compact_sparse import fixture,Library,integer_oracle
from study_memory_rom import ROOT,sha,save,env

def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--library',type=Path,required=True);p.add_argument('--output',type=Path,required=True);a=p.parse_args();a.output.mkdir(parents=True,exist_ok=False)
    source_sha=sha(__file__);rng,paths,sides,ordinary,extended,equal=fixture(a.output)
    d=Library(a.library,sha(a.library));cases=[];count=0
    for label,side,models in [('shared3',[None]*3,ordinary[:3]),('mixed3',[sides[0],None,sides[2]],[extended[0],ordinary[1],extended[2]])]:
        with d.chain(paths[:3],side) as chain:
            for n in (0,1,7,8,9,4095,4096,4097):
                src=rng.integers(0,256,(n,3),dtype=np.uint8);expected=src.copy()
                for model in models:expected=integer_oracle(model,expected)
                for kernel,t in [('scalar',1),('avx2',1),('avx2',4)]:
                    for offset in (0,1,2,3):
                        buf=np.full(3*n+offset+17,0xa7,dtype=np.uint8);view=buf[offset:offset+3*n].reshape(n,3);view[:]=src;chain.apply(view,kernel=kernel,threads=t)
                        if not np.array_equal(view,expected) or not np.all(buf[:offset]==0xa7) or not np.all(buf[offset+3*n:]==0xa7):raise AssertionError('3级合同失败')
                        count+=1
            cases.append(dict(label=label,model_bytes=chain.model_bytes))
    if sha(__file__)!=source_sha:raise AssertionError('执行中源码改变')
    save(a.output/'results.json',dict(passed=True,purpose=__doc__,environment=env(),script_sha256=source_sha,library_sha256=sha(a.library),comparisons=count,cases=cases))
    print(count)
if __name__=='__main__':main()
