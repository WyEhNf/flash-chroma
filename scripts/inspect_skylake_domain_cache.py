"""逐语义检查已证明/原检查的全部八族全命中循环，含编译器别名；不加载候选。"""
from __future__ import annotations
import argparse,re,subprocess
from pathlib import Path
from inspect_skylake_avx2 import ROOT,digest,read,save,functions
from inspect_skylake_preweight import linear_loops


def main():
    p=argparse.ArgumentParser(description=__doc__)
    for name in ('plan','build','output'):p.add_argument('--'+name,type=Path,required=True)
    for name in ('objdump','nm','mca'):p.add_argument('--'+name,required=True)
    args=p.parse_args();plan=read(args.plan);build=read(args.build/'build.json');out=args.output.resolve();policy=plan['domain_cache_policy']
    if out.exists() or build['plan_sha256']!=digest(args.plan) or build['source_sha256']!=plan['source_sha256']:
        raise ValueError('必须是新输出与冻结构建')
    for n,s in plan['source_sha256'].items():
        if digest(ROOT/n)!=s:raise ValueError('冻结源改变：'+n)
    for n in ('reference_static','reference_dispatch'):
        if digest(ROOT/policy[n]['path'])!=policy[n]['sha256']:raise ValueError('旧分派证据不同')
    old=read(ROOT/policy['reference_static']['path']);dispatch=read(ROOT/policy['reference_dispatch']['path'])['semantic_loops']['reference']
    out.mkdir();records={};failures=[];commands=[]
    for role,target in zip(('reference','candidate'),plan['cmake_targets']):
        objects=[p for p in args.build.rglob('channel_avx2.cpp.obj') if target+'.dir' in p.parts]
        if len(objects)!=1:raise ValueError('对象不唯一')
        obj=objects[0];command=[args.objdump,'-d','-C',str(obj)];commands.append(command);raw=subprocess.check_output(command)
        (out/(role+'.asm')).write_bytes(raw);fs=functions(raw.decode());loops=[l for f in fs for l in linear_loops(f)];groups={};aliases=[]
        if role=='reference':
            if digest(obj)!=old['variants']['reference']['object_sha256']:raise ValueError('参考对象未复现，不沿用分派')
            choices=[l for l in loops if '::avx2_chain_cached(' in l['function'] and l['gathers'] in (8,18) and l['calls']==0 and l['branches']==2]
            if len(choices)!=4:raise ValueError('参考四族选择不同')
            for semantic,index in dispatch.items():
                if choices[index]['start']!=old['variants']['reference']['selected'][index]['start']:raise ValueError('旧参考地址不同')
                groups[semantic]=[choices[index]]
        else:
            command=[args.nm,'-n','-C',str(obj)];commands.append(command);symbols=subprocess.check_output(command)
            (out/'candidate-symbols.txt').write_bytes(symbols)
            by_address={f['instructions'][0][0]:f for f in fs if f['instructions']}
            for line in symbols.decode().splitlines():
                m=re.match(r'^([0-9a-f]+)\s+[tT]\s+.*::cached<(true|false),\s*(true|false),\s*(true|false)>',line)
                if not m:continue
                address=int(m[1],16);fn=by_address.get(address)
                if fn is None:raise ValueError('模板符号没有完整函数体')
                proven=m[4]=='true';expected=8 if m[2]=='true' else 18
                semantic=('proven' if proven else 'checked')+'/'+('shared' if m[2]=='true' else 'unshared')+'/'+('shared' if m[3]=='true' else 'mixed')
                group=[l for l in linear_loops(fn) if l['gathers']==expected and not l['calls'] and l['branches'] in ((1,) if proven else (2,3))]
                if group:groups[semantic]=group
                aliases.append({'semantic':semantic,'symbol':line,'function':fn['function'],'address':hex(address),'selected_loops':len(group)})
            wanted={mode+'/'+semantic for mode in ('proven','checked') for semantic in dispatch}
            if set(groups)!=wanted:failures.append('候选未覆盖八族：'+str(sorted(wanted-set(groups))))
        records[role]={'object_sha256':digest(obj),'template_symbols':aliases,'selected_groups':{},
            'all_loop_inventory':[{k:v for k,v in l.items() if k!='seq'} for l in loops]}
        for semantic,group in groups.items():
            records[role]['selected_groups'][semantic]=[]
            for index,l in enumerate(group):
                name=semantic.replace('/','-')+'-'+str(index);first=int(l['start'],16);last=int(l['end'],16);body=['.text','.Lloop:']
                for address,op,operands in l['seq']:
                    if op.startswith('j'):
                        dest=int(re.match(r'([0-9a-f]+)',operands)[1],16)
                        if dest==first:body.append(op+' .Lloop')
                        elif not first<=dest<=last:body.append(op+' .Loutside')
                        else:raise ValueError('全命中轨迹含未建模内部分支')
                    else:body.append(op+' '+operands.split('#')[0].strip())
                body.append('.Loutside:');source=out/f'{role}-{name}.s';source.write_text('\n'.join(body)+'\n',encoding='ascii')
                row={k:v for k,v in l.items() if k!='seq'};row['models']={}
                for cpu in ('skylake','skylake-avx512'):
                    command=[args.mca,'-mcpu='+cpu,'-iterations=100','-resource-pressure',str(source)];commands.append(command)
                    proc=subprocess.run(command,capture_output=True);(out/f'{role}-{name}-{cpu}.stdout.log').write_bytes(proc.stdout);(out/f'{role}-{name}-{cpu}.stderr.log').write_bytes(proc.stderr)
                    if proc.returncode:raise ValueError('MCA失败，保留原日志')
                    text=proc.stdout.decode();row['models'][cpu]={k:float(re.search(r'^'+re.escape(k)+r':\s*([0-9.]+)',text,re.M)[1]) for k in ('Total Cycles','Total uOps','Block RThroughput')}
                records[role]['selected_groups'][semantic].append(row)
    paired=[];actual=[]
    if not failures:
        for mode in ('proven','checked'):
            for semantic in dispatch:
                r=records['reference']['selected_groups'][semantic][0]
                for index,c in enumerate(records['candidate']['selected_groups'][mode+'/'+semantic]):
                    for cpu in ('skylake','skylake-avx512'):
                        ratio={k:c['models'][cpu][k]/r['models'][cpu][k] for k in ('Total Cycles','Block RThroughput')}
                        row={'mode':mode,'semantic':semantic,'candidate_path':index,'cpu':cpu,'ratios':ratio,'pass':all(v<=1.03 for v in ratio.values())}
                        paired.append(row)
                        if mode=='proven' and semantic=='unshared/shared':actual.append(ratio['Total Cycles']<=.97)
    passed=not failures and bool(paired) and all(r['pass'] for r in paired) and len(actual)==2 and all(actual)
    for n,s in plan['source_sha256'].items():
        if digest(ROOT/n)!=s:raise ValueError('静态期间原生/运行源改变')
    save(out/'results.json',{'purpose':__doc__,'plan_sha256':digest(args.plan),'build_sha256':digest(args.build/'build.json'),
        'variants':records,'selection_failures':failures,'paired_cost_gates':paired,'actual_potential_gates':actual,'static_cost_gate_pass':passed,
        'commands':commands,'analysis_sources':{n:digest(ROOT/n) for n in ('scripts/inspect_skylake_domain_cache.py','scripts/inspect_skylake_preweight.py','scripts/inspect_skylake_avx2.py')},
        'tools':{n:{'sha256':digest(n),'version':subprocess.check_output([n,'--version'],text=True).splitlines()[:4]} for n in (args.objdump,args.nm,args.mca)},
        'native_calls':0,'performance_calls':0,'scope':'只对八族全命中循环建模，不含实际miss后缀、创建证明、缓存/GDS或噪声；两个CPU模型均为同一AVX2，不是服务器实测。'})
    print('全族静态门槛：',passed,'选择失败：',failures,flush=True)
    print(paired,flush=True)


if __name__=='__main__':main()
