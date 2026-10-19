"""检查共享轴预计算的两类完整四级循环，按gather/乘法族固定对应，不择优选循环。"""
from __future__ import annotations
import argparse
import collections
from pathlib import Path
import re
import subprocess
from inspect_skylake_avx2 import ROOT, digest, read, save, functions


def linear_loops(function):
    rows=[]
    for end,op,operands in function['instructions']:
        match=re.match(r'([0-9a-f]+)\s+<',operands)
        if not op.startswith('j') or not match or int(match[1],16)>=end:
            continue
        start=int(match[1],16);seq=[x for x in function['instructions'] if start<=x[0]<=end]
        h=collections.Counter(x[1] for x in seq)
        rows.append({'function':function['function'],'start':hex(start),'end':hex(end),'seq':seq,
            'instructions':len(seq),'gathers':sum(v for k,v in h.items() if k.startswith('vpgather')),
            'vpmulld':h['vpmulld'],'calls':sum(x[1].startswith('call') for x in seq),
            'branches':sum(x[1].startswith('j') for x in seq),'rsp_operands':sum('%rsp' in x[2] for x in seq)})
    return rows


def main():
    p=argparse.ArgumentParser(description=__doc__)
    for name in ('plan','build','output'):p.add_argument('--'+name,type=Path,required=True)
    p.add_argument('--objdump',required=True);p.add_argument('--mca',required=True);args=p.parse_args()
    plan=read(args.plan);build=read(args.build/'build.json');out=args.output.resolve()
    if out.exists() or build['plan_sha256']!=digest(args.plan) or build['source_sha256']!=plan['source_sha256']:
        raise ValueError('输出须新建，构建须匹配冻结计划')
    for name,sha in plan['source_sha256'].items():
        if digest(ROOT/name)!=sha:raise ValueError('冻结源改变：'+name)
    out.mkdir();records={};commands=[];failures=[]
    for role,target in zip(('reference','candidate'),plan['cmake_targets']):
        objects=[x for x in args.build.rglob('channel_avx2.cpp.obj') if target+'.dir' in x.parts]
        if len(objects)!=1:raise ValueError('对象不唯一')
        obj=objects[0];command=[args.objdump,'-d','-C',str(obj)];commands.append(command)
        raw=subprocess.check_output(command);(out/(role+'.asm')).write_bytes(raw)
        fs=functions(raw.decode());all_loops=[l for f in fs for l in linear_loops(f)]
        wanted=44 if role=='reference' else 38;selected=[]
        for gathers in (35,38):
            found=[l for l in all_loops if l['gathers']==gathers and l['vpmulld']==wanted and l['calls']==0 and l['branches']==1]
            if len(found)!=1:failures.append(role+':'+str(gathers)+'gather/'+str(wanted)+'mul家族不是唯一平坦零调用循环')
            else:selected.append(found[0])
        records[role]={'object_sha256':digest(obj),'function_sizes':{f['function']:len(f['instructions']) for f in fs},
            'all_loops':[{k:v for k,v in l.items() if k!='seq'} for l in all_loops],
            'selected':[{k:v for k,v in l.items() if k!='seq'} for l in selected]}
        if len(selected)==2:
            for i,l in enumerate(selected):
                body=['.text','.Lloop:']
                for address,op,operands in l['seq']:
                    if op.startswith('j'):
                        if int(re.match(r'([0-9a-f]+)',operands)[1],16)!=int(l['start'],16):
                            raise ValueError('单分支轨迹没有回到自身起点')
                        body.append(op+' .Lloop')
                    else:body.append(op+' '+operands.split('#')[0].strip())
                source=out/f'{role}-{i}-hot.s';source.write_text('\n'.join(body)+'\n',encoding='ascii')
                command=[args.mca,'-mcpu=skylake','-iterations=100','-resource-pressure',str(source)];commands.append(command)
                proc=subprocess.run(command,capture_output=True)
                (out/f'{role}-{i}-mca.stdout.log').write_bytes(proc.stdout);(out/f'{role}-{i}-mca.stderr.log').write_bytes(proc.stderr)
                if proc.returncode:raise ValueError('MCA解析失败，保留原日志')
                text=proc.stdout.decode();records[role]['selected'][i]['mca']={k:float(re.search(r'^'+re.escape(k)+r':\s*([0-9.]+)',text,re.M)[1])
                    for k in ('Total Cycles','Total uOps','Block RThroughput')}
        print(role,[{k:r[k] for k in ('start','instructions','gathers','vpmulld','rsp_operands')}|{'mca':r.get('mca')} for r in records[role]['selected']],flush=True)
    for name,sha in plan['source_sha256'].items():
        if digest(ROOT/name)!=sha:raise ValueError('静态分析中源改变：'+name)
    save(out/'results.json',{'purpose':__doc__,'plan_sha256':digest(args.plan),'build_sha256':digest(args.build/'build.json'),
        'variants':records,'selection_failures':failures,'commands':commands,
        'analysis_sources':{n:digest(ROOT/n) for n in ('scripts/inspect_skylake_preweight.py','scripts/inspect_skylake_avx2.py')},
        'tools':{n:{'sha256':digest(n),'version':subprocess.check_output([n,'--version'],text=True).splitlines()[:4]} for n in (args.objdump,args.mca)},
        'native_calls':0,'performance_calls':0,'scope':'完整平坦循环的静态建模，不含真实缓存/GDS、准备或噪声，不是Skylake实测'})
    if failures:print('静态选择尚未满足：',failures,flush=True)


if __name__=='__main__':main()
