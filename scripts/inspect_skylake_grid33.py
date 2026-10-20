"""只用标准库分析33³常量地址两类热循环；不加载候选库或调用像素核。"""
from __future__ import annotations
import argparse,json,re,subprocess
from pathlib import Path
from inspect_skylake_avx2 import digest,functions,loops,read,save
ROOT=Path(__file__).resolve().parents[1]

def main():
    p=argparse.ArgumentParser(description=__doc__)
    for key in ('plan','build','output'):p.add_argument('--'+key,type=Path,required=True)
    p.add_argument('--objdump',required=True);p.add_argument('--mca',required=True)
    args=p.parse_args();plan=read(args.plan);build=read(args.build/'build.json')
    if build['plan_sha256']!=digest(args.plan):raise ValueError('构建身份不同')
    for name,sha in plan['source_sha256'].items():
        if digest(ROOT/name)!=sha:raise ValueError('冻结源码不同：'+name)
    out=args.output;out.mkdir(exist_ok=False)
    def object_path(target,local=False):
        found=[path for path in args.build.rglob('channel_avx2.cpp.obj') if target+'.dir' in path.parts
            and ((path.parent.name==target+'.dir') if local else 'skylake-delta16-runtime' in path.parts)]
        if len(found)!=1:raise ValueError('不能唯一定位对象')
        return found[0]
    target=plan['cmake_targets'][1]
    ref=object_path('jshc_skylake_reference');fallback=object_path(target)
    if ref.read_bytes()!=fallback.read_bytes():raise ValueError('回退不再同字节')
    variants={};commands=[]
    for role,obj in [('reference',ref),('candidate',object_path(target,True))]:
        cmd=[args.objdump,'-d','-C',str(obj)];commands.append(cmd);asm=subprocess.check_output(cmd)
        (out/f'{role}.asm').write_bytes(asm);families={}
        all_loops=[x for f in functions(asm.decode('utf-8')) for x in loops(f)]
        for count in (35,38):
            eligible=[x for x in all_loops if x['gathers']==count and x['branches']==1 and x['calls']==0]
            if len(eligible)!=1:raise ValueError('35/38gather家族必须唯一且无调用')
            hot=eligible[0]
            code='\n'.join(op+' .Lloop' if op.startswith('j') else op+' '+arg.split('#')[0].strip() for _,op,arg in hot['seq'])
            source=out/f'{role}-{count}-hot.s';source.write_text('.text\n.Lloop:\n'+code+'\n',encoding='ascii')
            cmd=[args.mca,'-mcpu=skylake','-iterations=100','-resource-pressure',str(source)];commands.append(cmd)
            proc=subprocess.run(cmd,capture_output=True)
            (out/f'{role}-{count}-mca.stdout.log').write_bytes(proc.stdout)
            (out/f'{role}-{count}-mca.stderr.log').write_bytes(proc.stderr)
            if proc.returncode:raise ValueError('MCA失败，原始stderr已保留')
            text=proc.stdout.decode('utf-8');mca={key:float(re.search('^'+key+r':\s*([0-9.]+)',text,re.M)[1])
                for key in ('Total Cycles','Total uOps','Block RThroughput')}
            families[str(count)]={'hot':{k:v for k,v in hot.items() if k!='seq'},'mca':mca}
        variants[role]={'object':str(obj.resolve()),'sha256':digest(obj),'families':families}
    gates={}
    for count in ('35','38'):
        r=variants['reference']['families'][count];c=variants['candidate']['families'][count]
        gates[count]={'cycles_at_least_3_percent':c['mca']['Total Cycles']<=.97*r['mca']['Total Cycles'],
            'rsp_not_increased':c['hot']['rsp_operands']<=r['hot']['rsp_operands']}
    result={'purpose':__doc__,'pass':all(all(x.values()) for x in gates.values()),'gate':gates,'variants':variants,
        'fallback_sha256':digest(fallback),'plan_sha256':digest(args.plan),'build_sha256':digest(args.build/'build.json'),
        'script_sha256':digest(__file__),'commands':commands,'new_native_calls':0,'new_performance_calls':0,
        'scope':'Skylake静态模型，不替代真实CPU性能或整数正确性'}
    save(out/'results.json',result)
    print(json.dumps({'pass':result['pass'],'gate':gates,'variants':{role:{n:{'instructions':x['hot']['instructions'],
        'mul':x['hot']['vpmulld'],'rsp':x['hot']['rsp_operands'],'mca':x['mca']} for n,x in v['families'].items()}
        for role,v in variants.items()}},ensure_ascii=False))

if __name__=='__main__':main()
