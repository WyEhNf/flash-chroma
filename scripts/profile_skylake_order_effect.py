"""只读描述旧混合协议的角色顺序效应；每组仅两个进程，不认定具体硬件原因。"""
from pathlib import Path
from statistics import median
import hashlib,json,argparse
ROOT=Path(__file__).resolve().parents[1]
def read(p):return json.loads(p.read_text(encoding='utf-8'))
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--output',type=Path,required=True);a=p.parse_args()
    if a.output.exists():raise ValueError('不得覆盖顺序分析')
    rows=[];inputs={}
    for name in ('batchspan','overlap16'):
        folder=ROOT/f'artifacts/skylake-{name}-quiet-perf-v1';workers=[]
        for i in range(4):
            path=folder/f'worker{i}.json';workers.append(read(path));inputs[path.relative_to(ROOT).as_posix()]=sha(path)
        for threads in (1,4):
            for role in ('reference','candidate'):
                for first in (True,False):
                    chosen=[next(r for r in w['records'] if r['requested_threads']==threads and r['variant']==role) for w in workers if (w['order'][0]==role)==first]
                    assert len(chosen)==2
                    rows.append({'case':name,'requested_threads':threads,'variant':role,'role_measured_first':first,'sample_processes':2,**{label+'_seconds':[median(r[key]) for r in chosen] for key,label in [('apply_seconds','apply'),('outplace_seconds','outplace')]}})
    result={'purpose':__doc__,'rows':rows,'input_sha256':inputs,'script_sha256':sha(Path(__file__)),'new_native_calls':0,'new_performance_calls':0,'limitation':'描述性小样本，顺序与分配/大页状态、缓存、频率等可能相关，尚未单独归因；最终确认改用每角色/线程/API模式的独立进程，不删除旧通过点'}
    a.output.parent.mkdir(parents=True,exist_ok=True);a.output.write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n',encoding='utf-8');print('旧混合顺序分析完成，无新计时')
if __name__=='__main__':main()
