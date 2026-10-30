"""只读核验49的通用AVX2、线性回退同字节及两套内核无外部调用；不作性能结论。"""
import argparse,hashlib,json,subprocess
from pathlib import Path
from inspect_skylake_avx2 import functions
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def read(p):return json.loads(Path(p).read_text(encoding='utf-8'))
def main():
    p=argparse.ArgumentParser(description=__doc__)
    for n in ['build','plan','output']:p.add_argument('--'+n,type=Path,required=True)
    a=p.parse_args();b=read(a.build/'build.json');assert b['plan_sha256']==sha(a.plan)
    if a.output.exists():raise ValueError('不得覆盖静态证据')
    def obj(target,name,folder=None):
        paths=[x for x in a.build.rglob(name+'.o') if target+'.dir' in x.parts and (x.parent.name==target+'.dir' if folder=='local' else folder is None or folder in x.parts)]
        assert len(paths)==1,(target,name,folder);return paths[0]
    def asm(o):return subprocess.check_output(['objdump','-d','-C',str(o)])
    target='jshc_skylake_tilemadd';old={}
    for folder in ['skylake-exception-runtime','skylake-domain-isolated-runtime','skylake-suffix-cache-runtime']:
        left=obj('jshc_skylake_reference','channel_avx2.cpp',folder);right=obj(target,'channel_avx2.cpp',folder)
        assert left.read_bytes()==right.read_bytes();old[folder]=sha(left)
    local=obj(target,'channel_avx2.cpp','local')
    previous=Path('artifacts/skylake-batchspan-linux-build-v1/CMakeFiles/jshc_skylake_batchspan.dir/channel_avx2.cpp.o')
    # 不假设CMake对象相对路径，限定旧目标的本地TU。
    choices=[x for x in Path('artifacts/skylake-batchspan-linux-build-v1').rglob('channel_avx2.cpp.o') if 'jshc_skylake_batchspan.dir' in x.parts and 'skylake-batchspan-runtime' not in x.parts[:-1] and x.parent.name=='jshc_skylake_batchspan.dir']
    if previous.exists():choices=[previous]
    assert len(choices)==1,choices
    assert local.read_bytes()==choices[0].read_bytes(),'通用回退对象与40不同'
    tile=obj(target,'channel_tilemadd.cpp');tile_asm=asm(tile);linear_asm=asm(local)
    assert not any(x in tile_asm for x in [b'pext',b'pdep',b'vpgather']) and b'pext' not in linear_asm
    assert b'vpmaddwd' in tile_asm and b'vpmaddubsw' in tile_asm
    runtime=obj(target,'channel_runtime.cpp');runtime_asm=asm(runtime);assert b'pext' not in runtime_asm and b'pdep' not in runtime_asm
    totals={}
    for label,data in [('candidate',tile_asm),('fallback',linear_asm)]:
        parsed=functions(data.decode('utf-8'));ins=[i for f in parsed for i in f['instructions']]
        assert ins and not any(i[1].startswith('call') for i in ins)
        assert not any(x in data for x in [b'%zmm',b'vfmadd',b'%ymm16',b'%k1'])
        totals[label]={'functions':len(parsed),'instructions':len(ins),'external_calls':0,'pext_instructions':sum(i[1].startswith('pext') for i in ins)}
    a.output.mkdir();(a.output/'candidate.asm').write_bytes(tile_asm);(a.output/'fallback.asm').write_bytes(linear_asm)
    result={'pass':True,'purpose':__doc__,'build_sha256':sha(a.build/'build.json'),'script_sha256':sha(__file__),'original_objects':old,'fallback_identical_to_40':True,'runtime_has_pext':False,'objects':{'candidate':sha(tile),'fallback':sha(local),'dispatcher':sha(runtime)},'static_counts':totals,'new_pixel_calls':0,'new_performance_calls':0}
    (a.output/'results.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n',encoding='utf-8');print(json.dumps(result,ensure_ascii=False))
if __name__=='__main__':main()
