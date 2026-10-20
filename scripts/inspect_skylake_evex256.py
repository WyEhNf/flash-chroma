"""静态核对EVEX-256宽度、分派隔离、AVX2回退原字节及Skylake-SP循环模型；不加载像素库。"""
from __future__ import annotations
import argparse
import json
from pathlib import Path
import re
import subprocess
from inspect_skylake_avx2 import digest, functions, loops, read, save

ROOT=Path(__file__).resolve().parents[1]

def main():
    p=argparse.ArgumentParser(description=__doc__)
    for key in ('plan','build','output'):
        p.add_argument('--'+key,type=Path,required=True)
    p.add_argument('--objdump',required=True)
    p.add_argument('--mca',required=True)
    args=p.parse_args();plan=read(args.plan);build=read(args.build/'build.json')
    if build['plan_sha256']!=digest(args.plan):raise ValueError('冻结计划与构建不符')
    for name,sha in plan['source_sha256'].items():
        if digest(ROOT/name)!=sha:raise ValueError('源码变化：'+name)
    out=args.output.resolve();out.mkdir(exist_ok=False)
    def object_path(target,source_fragment):
        found=[path for path in args.build.rglob('*.obj') if target+'.dir' in path.parts
               and source_fragment in path.as_posix()]
        if not found and source_fragment.startswith('skylake-evex256-runtime/'):
            # CMake把项目自身的源文件对象直接放在target.dir中，外部源才保留目录。
            found=[path for path in args.build.rglob('*.obj') if target+'.dir' in path.parts
                   and path.name==source_fragment.split('/')[-1]+'.obj' and path.parent.name==target+'.dir']
        if len(found)!=1:raise ValueError('对象无法唯一定位：'+str(found))
        return found[0]
    ref=object_path('jshc_skylake_reference','skylake-delta16-runtime/channel_avx2.cpp')
    fallback=object_path('jshc_skylake_evex256','skylake-delta16-runtime/channel_avx2.cpp')
    if ref.read_bytes()!=fallback.read_bytes():raise ValueError('原AVX2回退对象不再相同')
    candidate=object_path('jshc_skylake_evex256','skylake-evex256-runtime/channel_avx2.cpp')
    variants={};commands=[]
    for role,obj in (('reference',ref),('candidate',candidate)):
        cmd=[args.objdump,'-d','-C',str(obj)];commands.append(cmd)
        asm=subprocess.check_output(cmd);(out/f'{role}.asm').write_bytes(asm)
        parsed=functions(asm.decode('utf-8',errors='replace'))
        if re.search(r'%zmm\d',asm.decode('utf-8')):raise ValueError('出现512位ZMM指令')
        all_loops=[loop for f in parsed for loop in loops(f)]
        eligible=[loop for loop in all_loops if loop['gathers']==35 and loop['calls']==0 and loop['branches']==1]
        if not eligible:raise ValueError('没有35gather无调用实际四级平坦循环')
        hot=max(eligible,key=lambda x:x['span_bytes'])
        assembly='\n'.join(op+' .Lloop' if op.startswith('j') else op+' '+operands.split('#')[0].strip()
            for address,op,operands in hot['seq'])
        if role=='candidate' and not re.search(r'%ymm(?:1[6-9]|2\d|3[01])',assembly):
            raise ValueError('没有使用扩展YMM寄存器')
        source=out/f'{role}-hot.s';source.write_text('.text\n.Lloop:\n'+assembly+'\n',encoding='ascii')
        cmd=[args.mca,'-mcpu=skylake-avx512','-iterations=100','-resource-pressure',str(source)];commands.append(cmd)
        proc=subprocess.run(cmd,capture_output=True)
        (out/f'{role}-mca.stdout.log').write_bytes(proc.stdout)
        (out/f'{role}-mca.stderr.log').write_bytes(proc.stderr)
        if proc.returncode:raise ValueError('MCA失败；原始stderr保留')
        log=proc.stdout.decode('utf-8')
        metrics={key:float(re.search(r'^'+re.escape(key)+r':\s*([0-9.]+)',log,re.M)[1])
            for key in ('Total Cycles','Total uOps','Block RThroughput')}
        variants[role]={'object':str(obj.resolve()),'sha256':digest(obj),
            'hot':{k:v for k,v in hot.items() if k!='seq'},'mca':metrics,
            'all_loops':[{k:v for k,v in x.items() if k!='seq'} for x in all_loops],
            'high_ymm_registers':sorted(set(re.findall(r'%ymm(?:1[6-9]|2\d|3[01])',assembly)))}
    dispatcher=object_path('jshc_skylake_evex256','channel_dispatch.cpp')
    dispatch_asm=subprocess.check_output([args.objdump,'-d','-C',str(dispatcher)])
    (out/'dispatcher.asm').write_bytes(dispatch_asm)
    if re.search(rb'%(?:[yz]mm|k)\d',dispatch_asm):raise ValueError('分派TU含有向量ISA')
    r,c=variants['reference'],variants['candidate']
    gate={'cycles_at_least_5_percent':c['mca']['Total Cycles']<=r['mca']['Total Cycles']*.95,
          'rsp_not_increased':c['hot']['rsp_operands']<=r['hot']['rsp_operands']}
    result={'purpose':__doc__,'pass':all(gate.values()),'gate':gate,'variants':variants,
        'fallback_sha256':digest(fallback),'dispatcher_sha256':digest(dispatcher),
        'plan_sha256':digest(args.plan),'build_sha256':digest(args.build/'build.json'),
        'script_sha256':digest(__file__),'commands':commands,
        'tools':{name:{'sha256':digest(name),'version':subprocess.check_output([name,'--version'],text=True).splitlines()[:3]}
                 for name in (args.objdump,args.mca)},
        'new_native_calls':0,'new_performance_calls':0,
        'scope':'Skylake-SP静态模型，不含GDS、真实缓存、频率、CPU调度；不能代替数值/性能验证'}
    save(out/'results.json',result)
    print(json.dumps({'pass':result['pass'],'gate':gate,'variants':{k:{'instructions':v['hot']['instructions'],
        'rsp':v['hot']['rsp_operands'],'mca':v['mca'],'high_ymm':v['high_ymm_registers']} for k,v in variants.items()}},ensure_ascii=False))

if __name__=='__main__':main()
