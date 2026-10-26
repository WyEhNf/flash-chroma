"""独立补充整幅16M/256块的四工作线程正确性；不改原分块质量协议。"""
from __future__ import annotations
import argparse
import ctypes as ct
import hashlib
import json
import os
from pathlib import Path
import sys

ROOT=Path(__file__).resolve().parents[1]
sys.path[:0]=[str(ROOT/'scripts')]
from check_direct_rgb24_native import Library,BUILD,FROZEN as PRIMARY_FROZEN,OUT as PRIMARY,sha,save,to
from check_omp_affinity_control_v2 import Record
import numpy as np
import psutil

FROZEN=ROOT/'artifacts/p16-direct-rgb24-full-mt-frozen-v1'
OUT=ROOT/'artifacts/p16-direct-rgb24-full-mt-v1'
HELPER=ROOT/'artifacts/p16-omp-affinity-control-build-v2/libp16_omp_affinity.dll'
HELPER_SHA='fbf717dd92e0f38e93394c88255ca9a36f9fab48ef30878b0200f9f4c4a0901f'
GOMP=Path('E:/mingw64/bin/libgomp-1.dll')
GOMP_SHA='fc7569276d33d23f55f143eb6723821ef2633c96cbb381c0f507b793d9585e88'

def freeze():
    if FROZEN.exists():raise FileExistsError('不覆盖整幅MT冻结')
    primary=json.loads((PRIMARY_FROZEN/'frozen.json').read_text(encoding='utf-8'))
    if sha(HELPER)!=HELPER_SHA or sha(GOMP)!=GOMP_SHA:raise ValueError('只读线程观察器或libgomp变更')
    sources=dict(primary['sources_sha256'])
    for path in (Path(__file__),ROOT/'scripts/check_omp_affinity_control_v2.py'):
        sources[path.relative_to(ROOT).as_posix()]=sha(path)
    for name,expected in sources.items():
        if sha(ROOT/name)!=expected:raise ValueError('源身份变更')
    FROZEN.mkdir(parents=True)
    (FROZEN/'checker.py').write_bytes(Path(__file__).read_bytes())
    frozen={'scope':'四新链+87旧best各整幅16777216像素、256个65536块，AVX2请求4、原地及分离共10完整流；前后同libgomp4成员snapshot，无pin，不计时','sources_sha256':sources,'primary_frozen_sha256':sha(PRIMARY_FROZEN/'frozen.json'),'helper':str(HELPER),'helper_sha256':HELPER_SHA,'libgomp_sha256':GOMP_SHA,'required_environment':{'OMP_NUM_THREADS':'4','OMP_DYNAMIC':'FALSE','OMP_THREAD_LIMIT':'4','OMP_WAIT_POLICY':'PASSIVE','OPENBLAS_NUM_THREADS':'1','MKL_NUM_THREADS':'1'},'performance_calls':0}
    save(FROZEN/'frozen.json',frozen)
    print(json.dumps({'frozen_sha256':sha(FROZEN/'frozen.json'),'sources':len(sources),'performance_calls':0}))

def validate():
    if OUT.exists():raise FileExistsError('不覆盖整幅MT执行')
    frozen=json.loads((FROZEN/'frozen.json').read_text(encoding='utf-8'))
    for name,expected in frozen['sources_sha256'].items():
        if sha(ROOT/name)!=expected:raise ValueError('MT冻结后源变更：'+name)
    for name,expected in frozen['required_environment'].items():
        if os.environ.get(name,'').upper()!=expected.upper():raise ValueError('须在导入NumPy/OpenMP前设置环境：'+name)
    primary=json.loads((PRIMARY_FROZEN/'frozen.json').read_text(encoding='utf-8'))
    if sha(PRIMARY_FROZEN/'frozen.json')!=frozen['primary_frozen_sha256']:raise ValueError('原质量冻结变更')
    checked=json.loads((PRIMARY/'results.json').read_text(encoding='utf-8'))
    if not checked['passed'] or checked['frozen_sha256']!=frozen['primary_frozen_sha256']:raise ValueError('分块/照片质量尚未通过')
    if sha(HELPER)!=HELPER_SHA or sha(GOMP)!=GOMP_SHA:raise ValueError('观察器身份变更')
    OUT.mkdir(parents=True)
    psutil.Process().cpu_affinity([0,2,4,6])
    save(OUT/'process-preflight.json',{'allowed_cpus':psutil.Process().cpu_affinity(),'per_tid_pin':False,'performance_calls':0})
    dirs=[os.add_dll_directory('E:/mingw64/bin'),os.add_dll_directory(str(BUILD)),os.add_dll_directory(str(HELPER.parent))]
    helper=ct.CDLL(str(HELPER));fn=helper.p16_omp_affinity
    fn.argtypes=[ct.POINTER(Record),ct.c_size_t,ct.c_size_t,ct.c_uint32,ct.POINTER(Record)];fn.restype=ct.c_int
    assert ct.sizeof(Record)==72
    teams=[]
    def snapshot():
        records=(Record*4)();code=fn(records,4,72,0,None)
        row={'return_code':code,'action':0,'members':[{name:getattr(value,name) for name,_ in Record._fields_} for value in records]};teams.append(row)
        save(OUT/f'team-{len(teams):02d}.json',row)
        if code:raise ValueError('只读线程观察失败：'+str(code))
        assert all(value.version==1 and value.team_size==4 and value.omp_tid==index and value.set_attempted==0 for index,value in enumerate(records))
        assert len({value.os_tid for value in records})==4
        return [value.os_tid for value in records]
    rgb=np.empty((2**24,3),np.uint8)
    for begin in range(0,2**24,262144):
        codes=np.arange(begin,begin+262144,dtype=np.uint32);rgb[begin:begin+262144,0]=codes>>16;rgb[begin:begin+262144,1]=codes>>8;rgb[begin:begin+262144,2]=codes
    original_sha=hashlib.sha256(rgb).hexdigest();rows=[]
    roles=[(name,'new',spec) for name,spec in primary['roles'].items()]+[('87_old_best','old87',primary['roles']['old_best'])]
    for name,library_name,spec in roles:
        library_spec=primary['libraries'][library_name]
        if sha(library_spec['path'])!=library_spec['sha256']:raise ValueError('库身份变化')
        for path,expected in spec['input_sha256'].items():
            if sha(path)!=expected:raise ValueError('模型输入变化')
        if sha(spec['oracle'])!=spec['oracle_sha256']:raise ValueError('oracle变化')
        library=Library(library_spec['path'],library_spec['sha256'])
        with library.chain(spec['models'],spec['sidecars']) as chain:
            expected=np.memmap(spec['oracle'],np.uint8,'r',shape=(2**24,3))
            for route in ('inplace','to'):
                before=snapshot()
                actual=chain.apply(rgb.copy(),kernel='avx2',threads=4) if route=='inplace' else to(chain,rgb,'avx2',4)
                after=snapshot();assert before==after
                for begin in range(0,2**24,262144):np.testing.assert_array_equal(actual[begin:begin+262144],expected[begin:begin+262144])
                actual_sha=hashlib.sha256(actual).hexdigest();assert actual_sha==spec['oracle_sha256']
                assert hashlib.sha256(rgb).hexdigest()==original_sha
                rows.append({'model':name,'path':route,'pixels':2**24,'blocks':256,'requested_threads':4,'surrounding_team_os_tids':before,'sha256':actual_sha,'mismatches':0});del actual
    modules={str(Path(value.path).resolve()) for value in psutil.Process().memory_maps() if Path(value.path).name.lower()=='libgomp-1.dll'}
    assert len(modules)==1 and next(iter(modules)).lower()==str(GOMP.resolve()).lower()
    for name,expected in frozen['sources_sha256'].items():
        if sha(ROOT/name)!=expected:raise ValueError('执行后源变更')
    assert len(rows)==10 and len(teams)==20
    save(OUT/'results.json',{'passed':True,'frozen_sha256':sha(FROZEN/'frozen.json'),'primary_quality_sha256':sha(PRIMARY/'results.json'),'outputs':rows,'read_only_team_snapshots':teams,'unique_libgomp':list(modules),'helper_sha256':HELPER_SHA,'input_sha256':original_sha,'performance_calls':0,'limitation':'观察器前后为同runtime四成员pool；native内每块未加入TID插桩。各4模型系同一已冻结稀疏模型，不是拟合或速度结论。'})
    print(json.dumps({'passed':True,'whole_domain_streams':10,'same_runtime_snapshots':20,'mismatches':0,'performance_calls':0}))

def main():
    parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('--freeze',action='store_true');args=parser.parse_args()
    if args.freeze:freeze()
    else:validate()

if __name__=='__main__':main()
