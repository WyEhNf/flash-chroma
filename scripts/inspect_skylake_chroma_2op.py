"""静态核验61双指令通道差索引、原回退同字节、AVX2 ISA与无外部调用。"""
import argparse,hashlib,json,subprocess
from pathlib import Path
from inspect_skylake_avx2 import functions
ROOT=Path(__file__).resolve().parents[1]
def read(p):return json.loads(Path(p).read_text(encoding='utf-8'))
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def main():
    p=argparse.ArgumentParser(description=__doc__)
    for n in ['plan','build','output']:p.add_argument('--'+n,type=Path,required=True)
    a=p.parse_args();plan=read(a.plan);build=read(a.build/'build.json');assert build['plan_sha256']==sha(a.plan)
    for n,h in plan['source_sha256'].items():assert sha(ROOT/n)==h
    if a.output.exists():raise ValueError('不得覆盖静态证据')
    def obj(target,folder):
        xs=[x for x in a.build.rglob('channel_avx2.cpp.o') if target+'.dir' in x.parts and (x.parent.name==target+'.dir' if folder=='local' else folder in x.parts)]
        assert len(xs)==1,(target,folder);return xs[0]
    target='jshc_skylake_chroma_2op';old={}
    for folder in ['skylake-exception-runtime','skylake-domain-isolated-runtime','skylake-suffix-cache-runtime']:
        l=obj('jshc_skylake_reference',folder);r=obj(target,folder);assert l.read_bytes()==r.read_bytes();old[folder]=sha(l)
    current=obj(target,'local');data=subprocess.check_output(['objdump','-d','-C',str(current)]);parsed=functions(data.decode('utf-8'));ins=[i for f in parsed for i in f['instructions']];mn=[i[1] for i in ins]
    forbidden={'pext','pextl','pextq','pdep','pdepl','pdepq'}
    assert not any(i in forbidden or i.startswith(('vpgather','call')) for i in mn)
    assert not any(x in data for x in [b'%zmm',b'vfmadd',b'%ymm16',b'%k1'])
    assert any(i.startswith('vpextr') for i in mn)
    assert 'vpsubb' in mn and 'vpslld' in mn
    a.output.mkdir();(a.output/'candidate.asm').write_bytes(data)
    result={'pass':True,'purpose':__doc__,'original_objects':old,'candidate_object_sha256':sha(current),'functions':len(parsed),'instructions':len(ins),'external_calls':0,'pext_instructions':0,'vector_lane_extractions':sum(i.startswith('vpextr') for i in mn),'script_sha256':sha(__file__),'plan_sha256':sha(a.plan),'build_sha256':sha(a.build/'build.json'),'new_pixel_calls':0,'new_performance_calls':0}
    (a.output/'results.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n',encoding='utf-8');print(json.dumps(result,ensure_ascii=False))
if __name__=='__main__':main()
