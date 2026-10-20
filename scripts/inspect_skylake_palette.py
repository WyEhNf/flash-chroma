"""构建后只核对ISA隔离、原回退对象和新内核无外部调用；不以MCA代替缓存实测。"""
import argparse,json,subprocess
from pathlib import Path
from inspect_skylake_avx2 import digest,read,save,functions
ROOT=Path(__file__).resolve().parents[1]
def main():
    p=argparse.ArgumentParser(description=__doc__)
    for name in ('plan','build','output'):p.add_argument('--'+name,type=Path,required=True)
    p.add_argument('--objdump',required=True);args=p.parse_args();plan=read(args.plan);build=read(args.build/'build.json')
    assert build['plan_sha256']==digest(args.plan)
    for name,sha in plan['source_sha256'].items():assert digest(ROOT/name)==sha,name
    out=args.output;out.mkdir(exist_ok=False)
    def obj(target,folder):
        paths=[x for x in args.build.rglob('channel_avx2.cpp.obj') if target+'.dir' in x.parts and
            (x.parent.name==target+'.dir' if folder=='local' else folder in x.parts)]
        if len(paths)!=1:raise ValueError('对象无法唯一选择')
        return paths[0]
    old={}
    for folder in ('skylake-domain-isolated-runtime','skylake-suffix-cache-runtime'):
        ref=obj('jshc_skylake_reference',folder);candidate=obj('jshc_skylake_palette',folder)
        if ref.read_bytes()!=candidate.read_bytes():raise ValueError('原回退对象变化')
        old[folder]=digest(ref)
    current=obj('jshc_skylake_palette','local');asm=subprocess.check_output([args.objdump,'-d','-C',str(current)])
    (out/'candidate.asm').write_bytes(asm)
    parsed=functions(asm.decode('utf-8'));calls=[ins for f in parsed for ins in f['instructions'] if ins[1].startswith('call')]
    if calls:raise ValueError('新像素内核存在未内联调用')
    if any(x in asm for x in (b'%zmm',b'vfmadd',b'%ymm16',b'%k1')):raise ValueError('新内核有非AVX2指令')
    result={'pass':True,'purpose':__doc__,'original_objects':old,'candidate_sha256':digest(current),'functions':len(parsed),
        'instructions':sum(len(f['instructions']) for f in parsed),'external_calls':len(calls),'plan_sha256':digest(args.plan),
        'build_sha256':digest(args.build/'build.json'),'script_sha256':digest(__file__),'new_pixel_calls':0,'performance_calls':0}
    save(out/'results.json',result);print(json.dumps(result,ensure_ascii=False))
if __name__=='__main__':main()
