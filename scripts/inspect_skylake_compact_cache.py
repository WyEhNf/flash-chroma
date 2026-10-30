"""按已证明的参考分派和候选模板语义配对所有编码/原格式循环，只做静态建模，不加载库。"""
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
    plan=read(args.plan);build=read(args.build/'build.json');out=args.output.resolve();policy=plan['compact_cache_policy']
    if out.exists() or build['plan_sha256']!=digest(args.plan) or build['source_sha256']!=plan['source_sha256']:
        raise ValueError('新输出及冻结构建身份不符')
    for n,s in plan['source_sha256'].items():
        if digest(ROOT/n)!=s:raise ValueError('冻结源改变：'+n)
    for n in ('reference_static','reference_dispatch'):
        spec=policy[n]
        if digest(ROOT/spec['path'])!=spec['sha256']:raise ValueError('参考语义证据改变')
    old=read(ROOT/policy['reference_static']['path']);dispatch=read(ROOT/policy['reference_dispatch']['path'])['semantic_loops']['candidate']
    out.mkdir();records={};failures=[];commands=[];selected={}
    for role,target in zip(('reference','candidate'),plan['cmake_targets']):
        objects=[p for p in args.build.rglob('channel_avx2.cpp.obj') if target+'.dir' in p.parts]
        if len(objects)!=1:raise ValueError('对象不唯一')
        obj=objects[0];command=[args.objdump,'-d','-C',str(obj)];commands.append(command);raw=subprocess.check_output(command)
        (out/(role+'.asm')).write_bytes(raw);fs=functions(raw.decode());loops=[l for f in fs for l in linear_loops(f)]
        groups={}
        if role=='reference':
            if digest(obj)!=old['variants']['candidate']['object_sha256']:raise ValueError('参考对象不同，不可沿用已证明分派对应')
            choices=[l for l in loops if '::avx2_chain_cached(' in l['function'] and l['gathers'] in (8,18) and l['calls']==0 and l['branches']==2]
            if len(choices)!=4:raise ValueError('参考四条全命中路径选择不同')
            for semantic,index in dispatch.items():
                if choices[index]['start']!=old['variants']['candidate']['selected'][index]['start']:raise ValueError('参考循环地址对应不符')
                groups[semantic]=[choices[index]]
        else:
            for f in fs:
                m=re.search(r'::cached<(true|false),\s*(true|false),\s*(true|false)>',f['function'])
                if not m:continue
                semantic=('shared' if m[1]=='true' else 'unshared')+'/'+('shared' if m[2]=='true' else 'mixed')
                key=('encoded' if m[3]=='true' else 'raw')+'/'+semantic;expected=8 if m[1]=='true' else 18
                group=[l for l in linear_loops(f) if l['gathers']==expected and l['calls']==0 and l['branches'] in (2,3)]
                if group:groups.setdefault(key,[]).extend(group)
            wanted={format+'/'+semantic for format in ('encoded','raw') for semantic in dispatch}
            if set(groups)!=wanted:failures.append('候选不能覆盖全部八种语义：'+str(sorted(wanted-set(groups))))
        selected[role]=groups
        records[role]={'object_sha256':digest(obj),'function_sizes':{f['function']:len(f['instructions']) for f in fs},
            'selected_groups':{},'all_loop_inventory':[{k:v for k,v in l.items() if k!='seq'} for l in loops]}
        for semantic,group in groups.items():
            records[role]['selected_groups'][semantic]=[]
            for index,l in enumerate(group):
                name=semantic.replace('/','-')+'-'+str(index);first=int(l['start'],16);last=int(l['end'],16);body=['.text','.Lloop:']
                for address,op,args_text in l['seq']:
                    if op.startswith('j'):
                        dest=int(re.match(r'([0-9a-f]+)',args_text)[1],16)
                        if dest==first:body.append(op+' .Lloop')
                        elif not first<=dest<=last:body.append(op+' .Loutside')
                        else:raise ValueError('有未建模内部分支，须保留并完善分析器')
                    else:body.append(op+' '+args_text.split('#')[0].strip())
                body.append('.Loutside:');source=out/f'{role}-{name}.s';source.write_text('\n'.join(body)+'\n',encoding='ascii')
                row={k:v for k,v in l.items() if k!='seq'};row['models']={}
                for cpu in ('skylake','skylake-avx512'):
                    command=[args.mca,'-mcpu='+cpu,'-iterations=100','-resource-pressure',str(source)];commands.append(command)
                    r=subprocess.run(command,capture_output=True)
                    (out/f'{role}-{name}-{cpu}.stdout.log').write_bytes(r.stdout);(out/f'{role}-{name}-{cpu}.stderr.log').write_bytes(r.stderr)
                    if r.returncode:raise ValueError('MCA失败，保留原日志')
                    text=r.stdout.decode();row['models'][cpu]={k:float(re.search(r'^'+re.escape(k)+r':\s*([0-9.]+)',text,re.M)[1]) for k in ('Total Cycles','Total uOps','Block RThroughput')}
                records[role]['selected_groups'][semantic].append(row)
        print(role,{k:[{z:r[z] for z in ('instructions','gathers','rsp_operands','models')} for r in v] for k,v in records[role]['selected_groups'].items()},flush=True)
    paired=[]
    if not failures:
        for format in ('raw','encoded'):
            for semantic in dispatch:
                reference=records['reference']['selected_groups'][semantic][0]
                for index,candidate in enumerate(records['candidate']['selected_groups'][format+'/'+semantic]):
                    for cpu in ('skylake','skylake-avx512'):
                        ratio={k:candidate['models'][cpu][k]/reference['models'][cpu][k] for k in ('Total Cycles','Block RThroughput')}
                        paired.append({'format':format,'semantic':semantic,'candidate_path':index,'cpu':cpu,'ratios':ratio,'pass':all(v<=1.03 for v in ratio.values())})
    for n,s in plan['source_sha256'].items():
        if digest(ROOT/n)!=s:raise ValueError('分析时原生/运行工具改变')
    save(out/'results.json',{'purpose':__doc__,'plan_sha256':digest(args.plan),'build_sha256':digest(args.build/'build.json'),
        'variants':records,'selection_failures':failures,'paired_cost_gates':paired,'static_cost_gate_pass':not failures and bool(paired) and all(p['pass'] for p in paired),
        'commands':commands,'analysis_sources':{n:digest(ROOT/n) for n in ('scripts/inspect_skylake_compact_cache.py','scripts/inspect_skylake_preweight.py','scripts/inspect_skylake_avx2.py')},
        'tools':{n:{'sha256':digest(n),'version':subprocess.check_output([n,'--version'],text=True).splitlines()[:4]} for n in (args.objdump,args.mca)},
        'native_calls':0,'performance_calls':0,'scope':'全部原格式/编码及四分派逐语义比较，不删最贵路径；两种CPU模型消费AVX2，无实际缓存/GDS/准备/噪声或时间结论。'})
    print('全部静态成本门槛：',not failures and bool(paired) and all(p['pass'] for p in paired),flush=True)


if __name__=='__main__':main()
