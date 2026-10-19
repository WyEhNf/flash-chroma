"""检查缓存全命中路径的所有同形循环，不择优挑选；只做汇编/MCA模型，不执行像素。"""
from __future__ import annotations
import argparse
from pathlib import Path
import re
import subprocess
from inspect_skylake_avx2 import ROOT,digest,read,save,functions,loops

def main():
    p=argparse.ArgumentParser(description=__doc__)
    for name in ('plan','build','output'):p.add_argument('--'+name,type=Path,required=True)
    p.add_argument('--objdump',required=True);p.add_argument('--mca',required=True)
    p.add_argument('--reference-gathers',type=int,default=18)
    p.add_argument('--candidate-gathers',type=int,default=15)
    args=p.parse_args();plan=read(args.plan);build=read(args.build/'build.json')
    if build['plan_sha256']!=digest(args.plan) or build['source_sha256']!=plan['source_sha256']:raise ValueError('构建身份不同')
    for name,sha in plan['source_sha256'].items():
        if digest(ROOT/name)!=sha:raise ValueError('冻结源改变：'+name)
    out=args.output.resolve()
    if out.exists():raise ValueError('不覆盖静态分析')
    out.mkdir(parents=True);result={};commands=[]
    for role,target,count in zip(('reference','candidate'),plan['cmake_targets'],(args.reference_gathers,args.candidate_gathers)):
        objects=[x for x in args.build.rglob('channel_avx2.cpp.obj') if target+'.dir' in x.parts]
        if len(objects)!=1:raise ValueError('无法唯一确定对象')
        obj=objects[0];command=[args.objdump,'-d','-C',str(obj)];commands.append(command)
        assembly=subprocess.check_output(command);(out/(role+'.asm')).write_bytes(assembly)
        fs=functions(assembly.decode('utf-8'));all_loops=[l for f in fs for l in loops(f)]
        selected=[l for l in all_loops if '::avx2_chain_cached(' in l['function'] and l['gathers']==count and l['branches']==2 and l['calls']==0]
        if len(selected)!=2:raise ValueError('预期共享/混合后缀各一个全命中循环，实际不符')
        records=[]
        for index,loop in enumerate(selected):
            first=int(loop['start'],16);last=int(loop['end'],16);body=['.text','.Lloop:']
            for address,op,operands in loop['seq']:
                if op.startswith('j'):
                    target_address=int(re.match(r'([0-9a-f]+)',operands)[1],16)
                    if target_address==first:body.append(op+' .Lloop')
                    elif not first<=target_address<=last:body.append(op+' .Loutside')
                    else:raise ValueError('循环含未预期的内部跳转')
                else:body.append(op+' '+operands.split('#')[0].strip())
            body.append('.Loutside:');source=out/f'{role}-{index}-hit.s';source.write_text('\n'.join(body)+'\n',encoding='ascii')
            command=[args.mca,'-mcpu=skylake','-iterations=100','-resource-pressure',str(source)];commands.append(command)
            proc=subprocess.run(command,capture_output=True)
            (out/f'{role}-{index}-mca.stdout.log').write_bytes(proc.stdout)
            (out/f'{role}-{index}-mca.stderr.log').write_bytes(proc.stderr)
            if proc.returncode:raise RuntimeError('模型诊断见原日志')
            text=proc.stdout.decode('utf-8');record={k:v for k,v in loop.items() if k!='seq'}
            record['mca']={k:float(re.search(r'^'+re.escape(k)+r':\s*([0-9.]+)',text,re.M)[1])
                           for k in ('Total Cycles','Total uOps','Block RThroughput')}
            records.append(record)
        result[role]={'object_sha256':digest(obj),'function_sizes':{f['function']:len(f['instructions']) for f in fs},
            'selected_all_hit_loops':records,'all_loop_inventory':[{k:v for k,v in x.items() if k not in ('seq','mnemonics')} for x in all_loops]}
        print(role,[{k:r[k] for k in ('start','instructions','gathers','rsp_operands','calls','mca')} for r in records],flush=True)
    for name,sha in plan['source_sha256'].items():
        if digest(ROOT/name)!=sha:raise ValueError('静态期间源码改变')
    save(out/'results.json',{'purpose':__doc__,'plan_sha256':digest(args.plan),'build_sha256':digest(args.build/'build.json'),
        'variants':result,'commands':commands,'source_sha256':plan['source_sha256'],
        'analysis_sources':{n:digest(ROOT/n) for n in ('scripts/inspect_skylake_cached.py','scripts/inspect_skylake_avx2.py')},
        'tools':{x:{'sha256':digest(x),'version':subprocess.check_output([x,'--version'],text=True).splitlines()[:4]} for x in (args.objdump,args.mca)},
        'native_calls':0,'performance_calls':0,
        'scope':'全命中直线路径的模型；两处同形循环全部保留，未计真实缓存未命中、GDS缓解、分支预测/回退、准备或系统噪声；不是Skylake实测。'})
    (out/'analysis-script.py').write_bytes(Path(__file__).read_bytes())

if __name__=='__main__':main()
