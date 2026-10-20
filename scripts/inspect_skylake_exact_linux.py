"""标准库静态检查独立Linux精确表内核与原回退对象；不调用像素或性能入口。"""
import argparse,subprocess
from pathlib import Path
from inspect_skylake_avx2 import digest,read,save,functions
ROOT=Path(__file__).resolve().parents[1]
def main():
    p=argparse.ArgumentParser(description=__doc__)
    for name in ('plan','build','output'):p.add_argument('--'+name,type=Path,required=True)
    args=p.parse_args();plan=read(args.plan);build=read(args.build/'build.json');assert build['plan_sha256']==digest(args.plan)
    for name,sha in plan['source_sha256'].items():assert digest(ROOT/name)==sha,name
    candidate=plan['cmake_targets'][1];out=args.output;out.mkdir(exist_ok=False)
    def obj(target,folder):
        paths=[x for x in args.build.rglob('channel_avx2.cpp.o') if target+'.dir' in x.parts and (x.parent.name==target+'.dir' if folder=='local' else folder in x.parts)]
        if len(paths)!=1:raise ValueError('对象无法唯一定位')
        return paths[0]
    old={}
    for folder in ('skylake-domain-isolated-runtime','skylake-suffix-cache-runtime','skylake-exception-runtime'):
        ref=obj('jshc_skylake_reference',folder);cand=obj(candidate,folder)
        if ref.read_bytes()!=cand.read_bytes():raise ValueError('原回退对象改变：'+folder)
        old[folder]=digest(ref)
    current=obj(candidate,'local');asm=subprocess.check_output(['objdump','-d','-C',str(current)]);(out/'candidate.asm').write_bytes(asm)
    parsed=functions(asm.decode());instructions=[i for f in parsed for i in f['instructions']]
    calls=[i for i in instructions if i[1].startswith('call')]
    if calls:raise ValueError('像素内核含未内联调用')
    if any(x in asm for x in (b'%zmm',b'vfmadd',b'%ymm16',b'%k1')):raise ValueError('内核含超出AVX2指令')
    save(out/'results.json',{'pass':True,'purpose':__doc__,'original_objects':old,'candidate_object_sha256':digest(current),'functions':len(parsed),'instructions':len(instructions),'external_calls':len(calls),'gather_instructions':sum('gather' in i[1] for i in instructions),'plan_sha256':digest(args.plan),'build_sha256':digest(args.build/'build.json'),'script_sha256':digest(__file__)})
    print('静态检查通过；指令数',len(instructions),'外部调用',len(calls))
if __name__=='__main__':main()
