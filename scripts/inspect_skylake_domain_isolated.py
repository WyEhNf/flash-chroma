"""验证原回退对象逐字节保留，并对唯一新增无检查循环作client/server静态门槛。"""
import argparse,re,subprocess
from pathlib import Path
from inspect_skylake_avx2 import ROOT,digest,read,save,functions
from inspect_skylake_preweight import linear_loops


def main():
    p=argparse.ArgumentParser(description=__doc__)
    for name in ('plan','build','output'):p.add_argument('--'+name,type=Path,required=True)
    for name in ('objdump','mca'):p.add_argument('--'+name,required=True)
    args=p.parse_args();plan=read(args.plan);build=read(args.build/'build.json');out=args.output.resolve();policy=plan['domain_cache_policy']
    if out.exists() or build['plan_sha256']!=digest(args.plan) or build['source_sha256']!=plan['source_sha256']:
        raise ValueError('须新输出与冻结构建')
    for name,s in plan['source_sha256'].items():
        if digest(ROOT/name)!=s:raise ValueError('冻结源不同：'+name)
    old=read(ROOT/policy['reference_static']['path']);dispatch=read(ROOT/policy['reference_dispatch']['path'])['semantic_loops']['reference']
    refs=[p for p in args.build.rglob('channel_avx2.cpp.obj') if plan['cmake_targets'][0]+'.dir' in p.parts]
    cand=[p for p in args.build.rglob('channel_avx2.cpp.obj') if plan['cmake_targets'][1]+'.dir' in p.parts]
    fallback=[p for p in cand if 'skylake-suffix-cache-runtime' in p.parts];fast=[p for p in cand if p not in fallback]
    if len(refs)!=1 or len(fallback)!=1 or len(fast)!=1:raise ValueError('三个AVX2对象不能唯一定位')
    out.mkdir();proof={'reference_sha256':digest(refs[0]),'candidate_fallback_sha256':digest(fallback[0]),
        'old_reference_sha256':old['variants']['reference']['object_sha256']}
    proof['byte_identical']=len(set(proof.values()))==1;save(out/'fallback-object-proof.json',proof)
    if not proof['byte_identical']:raise ValueError('回退对象不同，不可用原路径成本界')
    records={};commands=[]
    for role,obj in (('reference',refs[0]),('candidate',fast[0])):
        command=[args.objdump,'-d','-C',str(obj)];commands.append(command);raw=subprocess.check_output(command);(out/(role+'.asm')).write_bytes(raw)
        parsed=functions(raw.decode());all_loops=[l for f in parsed for l in linear_loops(f)]
        if role=='reference':
            chosen=[l for l in all_loops if '::avx2_chain_cached(' in l['function'] and l['gathers'] in (8,18) and not l['calls'] and l['branches']==2]
            if len(chosen)!=4:raise ValueError('原四路径不同')
            loop=chosen[dispatch['unshared/shared']]
            if loop['start']!=old['variants']['reference']['selected'][dispatch['unshared/shared']]['start']:raise ValueError('原路径地址不同')
        else:
            chosen=[l for l in all_loops if '::avx2_chain_domain(' in l['function'] and l['gathers']==18 and not l['calls'] and l['branches']==1]
            if len(chosen)!=1:raise ValueError('唯一新增完整无检查循环不成立')
            loop=chosen[0]
        first=int(loop['start'],16);last=int(loop['end'],16);body=['.text','.Lloop:']
        for address,op,operands in loop['seq']:
            if op.startswith('j'):
                target=int(re.match(r'([0-9a-f]+)',operands)[1],16)
                if target==first:body.append(op+' .Lloop')
                elif not first<=target<=last:body.append(op+' .Loutside')
                else:raise ValueError('有未建模的内部分支')
            else:body.append(op+' '+operands.split('#')[0].strip())
        body.append('.Loutside:');source=out/(role+'.s');source.write_text('\n'.join(body)+'\n',encoding='ascii')
        record={k:v for k,v in loop.items() if k!='seq'};record['models']={};record['object_sha256']=digest(obj)
        record['all_loop_inventory']=[{k:v for k,v in l.items() if k!='seq'} for l in all_loops]
        for cpu in ('skylake','skylake-avx512'):
            command=[args.mca,'-mcpu='+cpu,'-iterations=100','-resource-pressure',str(source)];commands.append(command);r=subprocess.run(command,capture_output=True)
            (out/f'{role}-{cpu}.stdout.log').write_bytes(r.stdout);(out/f'{role}-{cpu}.stderr.log').write_bytes(r.stderr)
            if r.returncode:raise ValueError('MCA失败')
            record['models'][cpu]={k:float(re.search(r'^'+re.escape(k)+r':\s*([0-9.]+)',r.stdout.decode(),re.M)[1]) for k in ('Total Cycles','Total uOps','Block RThroughput')}
        records[role]=record
    bounds=[]
    for cpu in ('skylake','skylake-avx512'):
        ratios={k:records['candidate']['models'][cpu][k]/records['reference']['models'][cpu][k] for k in ('Total Cycles','Block RThroughput')}
        bounds.append({'cpu':cpu,'ratios':ratios,'pass':ratios['Total Cycles']<=.97 and ratios['Block RThroughput']<=1.03})
    for name,s in plan['source_sha256'].items():
        if digest(ROOT/name)!=s:raise ValueError('分析中冻结源改变')
    save(out/'results.json',{'purpose':__doc__,'plan_sha256':digest(args.plan),'build_sha256':digest(args.build/'build.json'),
        'fallback_object_proof':proof,'variants':records,'actual_cost_gates':bounds,'static_cost_gate_pass':proof['byte_identical'] and all(b['pass'] for b in bounds),
        'all_other_four_hit_paths_ratio':1.0,'commands':commands,'analysis_source_sha256':digest(__file__),
        'native_calls':0,'performance_calls':0,'scope':'原对象同字节证明的是原内核，不包括新证明准备/入口成本；MCA无真实缓存/GDS/噪声，不是Skylake实测。'})
    print({'fallback_equal':proof['byte_identical'],'bounds':bounds,'pass':all(b['pass'] for b in bounds)},flush=True)


if __name__=='__main__':main()
