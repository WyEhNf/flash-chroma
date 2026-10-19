"""完整检查R连续缓存的四种全命中循环，含所有后向边；建模client/server两种Skylake，不运行候选。"""
from __future__ import annotations
import argparse
from pathlib import Path
import re
import subprocess
from inspect_skylake_avx2 import ROOT,digest,read,save,functions
from inspect_skylake_preweight import linear_loops


def main():
    p=argparse.ArgumentParser(description=__doc__)
    for n in ('plan','build','output'):p.add_argument('--'+n,type=Path,required=True)
    p.add_argument('--objdump',required=True);p.add_argument('--mca',required=True);args=p.parse_args()
    plan=read(args.plan);build=read(args.build/'build.json');out=args.output.resolve()
    if out.exists() or build['plan_sha256']!=digest(args.plan) or build['source_sha256']!=plan['source_sha256']:
        raise ValueError('输出须新建，构建须匹配冻结计划')
    for name,sha in plan['source_sha256'].items():
        if digest(ROOT/name)!=sha:raise ValueError('冻结源变化：'+name)
    out.mkdir();records={};commands=[]
    for role,target in zip(('reference','candidate'),plan['cmake_targets']):
        objects=[x for x in args.build.rglob('channel_avx2.cpp.obj') if target+'.dir' in x.parts]
        if len(objects)!=1:raise ValueError('对象不唯一')
        obj=objects[0];command=[args.objdump,'-d','-C',str(obj)];commands.append(command)
        raw=subprocess.check_output(command);(out/(role+'.asm')).write_bytes(raw)
        fs=functions(raw.decode());all_loops=[l for f in fs for l in linear_loops(f)]
        chosen=[l for l in all_loops if '::avx2_chain_cached(' in l['function'] and l['gathers'] in (8,18) and l['calls']==0 and l['branches']==2]
        if len(chosen)!=4 or any(sum(l['gathers']==g for l in chosen)!=2 for g in (8,18)):
            save(out/(role+'-refusal.json'),{'purpose':'完整四族尚不能唯一选取，不允许挑选有利循环',
                'inventory':[{k:v for k,v in l.items() if k!='seq'} for l in all_loops]})
            raise ValueError('四族完整全命中循环选择不符合预期')
        selected=[]
        for i,l in enumerate(chosen):
            first=int(l['start'],16);last=int(l['end'],16);body=['.text','.Lloop:']
            for address,op,operands in l['seq']:
                if op.startswith('j'):
                    dest=int(re.match(r'([0-9a-f]+)',operands)[1],16)
                    if dest==first:body.append(op+' .Lloop')
                    elif not first<=dest<=last:body.append(op+' .Loutside')
                    else:raise ValueError('完整路径存在未建模的内部分支')
                else:body.append(op+' '+operands.split('#')[0].strip())
            body.append('.Loutside:');source=out/f'{role}-{i}-hit.s';source.write_text('\n'.join(body)+'\n',encoding='ascii')
            record={k:v for k,v in l.items() if k!='seq'};record['models']={}
            for cpu in ('skylake','skylake-avx512'):
                command=[args.mca,'-mcpu='+cpu,'-iterations=100','-resource-pressure',str(source)];commands.append(command)
                proc=subprocess.run(command,capture_output=True)
                (out/f'{role}-{i}-{cpu}.stdout.log').write_bytes(proc.stdout);(out/f'{role}-{i}-{cpu}.stderr.log').write_bytes(proc.stderr)
                if proc.returncode:raise ValueError('MCA失败，保留原日志')
                text=proc.stdout.decode();record['models'][cpu]={k:float(re.search(r'^'+re.escape(k)+r':\s*([0-9.]+)',text,re.M)[1])
                    for k in ('Total Cycles','Total uOps','Block RThroughput')}
            selected.append(record)
        records[role]={'object_sha256':digest(obj),'selected':selected,'all_loop_inventory':[{k:v for k,v in l.items() if k!='seq'} for l in all_loops]}
        print(role,[{k:r[k] for k in ('gathers','instructions','rsp_operands','models')} for r in selected],flush=True)
    bounds=[]
    for cpu in ('skylake','skylake-avx512'):
        for gathers in (8,18):
            r=[v for v in records['reference']['selected'] if v['gathers']==gathers];c=[v for v in records['candidate']['selected'] if v['gathers']==gathers]
            ratio={k:max(v['models'][cpu][k] for v in c)/min(v['models'][cpu][k] for v in r) for k in ('Total Cycles','Block RThroughput')}
            bounds.append({'cpu_model':cpu,'gathers':gathers,'conservative_candidate_max_over_reference_min':ratio,
                'pass':all(x<=1.03 for x in ratio.values())})
    for name,sha in plan['source_sha256'].items():
        if digest(ROOT/name)!=sha:raise ValueError('静态期间源变化：'+name)
    save(out/'results.json',{'purpose':__doc__,'plan_sha256':digest(args.plan),'build_sha256':digest(args.build/'build.json'),
        'variants':records,'conservative_bounds':bounds,'static_cost_gate_pass':all(b['pass'] for b in bounds),'commands':commands,
        'analysis_sources':{n:digest(ROOT/n) for n in ('scripts/inspect_skylake_rcontiguous.py','scripts/inspect_skylake_preweight.py','scripts/inspect_skylake_avx2.py')},
        'tools':{n:{'sha256':digest(n),'version':subprocess.check_output([n,'--version'],text=True).splitlines()[:4]} for n in (args.objdump,args.mca)},
        'native_calls':0,'performance_calls':0,'scope':'两种CPU模型都消费同一AVX2汇编，不启用AVX512。全部四族不挑选，取候选最贵/参考最便宜保守界；没有真实缓存、GDS、回退或系统噪声，不是Skylake实测。'})
    print('完整静态成本门槛：',all(b['pass'] for b in bounds),flush=True)


if __name__=='__main__':main()
