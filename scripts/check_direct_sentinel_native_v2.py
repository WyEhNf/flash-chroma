"""290真实四链的完整色域、逐图与格式正确性；独立冻结，不进行性能比较。"""
from __future__ import annotations
import argparse
from collections import Counter
from contextlib import ExitStack
import ctypes as ct
import hashlib
import json
import os
from pathlib import Path
import sys

ROOT=Path(__file__).resolve().parents[1]
ORIGINAL=Path('F:/Hackathon/projects/16-lut-color')
sys.path[:0]=[str(ROOT/'python'),str(ROOT/'experiments/channel-runtime'),str(ROOT/'scripts')]
import numpy as np
from PIL import Image
from channel_native import Library
from lutlab import io,study_provenance
from outplace_support import bind_to,apply_to,reject_to
from suffix_cache_support import cache_info
from domain_cache_support import info as domain_info
from direct16_support import info as direct_info,table as direct_table
from palette_support import info as palette_info

BUILD=ROOT/'artifacts/p16-direct-sentinel-v2-build-v1'
FROZEN=ROOT/'artifacts/p16-direct-sentinel-v2-quality-frozen-v1'
OUT=ROOT/'artifacts/p16-direct-sentinel-v2-quality-v1'

def sha(path):
    with Path(path).open('rb') as stream:return hashlib.file_digest(stream,'sha256').hexdigest()

def save(path,value):
    if path.exists():raise FileExistsError('不覆盖证据：'+str(path))
    path.parent.mkdir(parents=True,exist_ok=True)
    path.write_text(json.dumps(value,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')

class Info(ct.Structure):
    _fields_=[(name,ct.c_uint32) for name in ('version','enabled','format','reason','palette_size','id_bytes','guard_bytes','whole_cache_colors')]
    _fields_ += [(name,ct.c_uint64) for name in ('input_entries','raw_words','table_capacity_bytes','palette_capacity_bytes','temporary_peak_bytes','guaranteed_alignment','data_mod_64')]
    _fields_ += [('prepare_seconds',ct.c_double)]

def info(chain):
    f=chain.library.dll.p16_cc_get_direct_sentinel_info
    f.argtypes=[ct.c_void_p,ct.POINTER(Info),ct.c_size_t];f.restype=ct.c_int
    value=Info()
    if ct.sizeof(value)!=96 or f(chain.handle,ct.byref(value),96) or value.version!=1:raise ValueError('哨兵96B诊断不符')
    return {name:getattr(value,name) for name,_ in value._fields_}

def palette(chain,new=True):
    if new:count=info(chain)['palette_size'];name='p16_cc_copy_sentinel_palette'
    else:
        f=chain.library.dll.p16_cc_get_direct_u16_info;f.argtypes=[ct.c_void_p,ct.POINTER(Info),ct.c_size_t];f.restype=ct.c_int
        value=Info()
        if f(chain.handle,ct.byref(value),96):raise ValueError('288诊断失败')
        count=value.palette_size;name='p16_cc_copy_u16_palette'
    out=np.empty(count,np.uint32);f=getattr(chain.library.dll,name)
    f.argtypes=[ct.c_void_p,ct.POINTER(ct.c_uint32),ct.c_size_t];f.restype=ct.c_int
    if f(chain.handle,out.ctypes.data_as(ct.POINTER(ct.c_uint32)),count):raise ValueError('palette快照失败')
    return out

def cache_values(chain):
    values=np.empty(cache_info(chain)['entries'],np.uint32);f=chain.library.dll.jshc_cc_copy_cache
    f.argtypes=[ct.c_void_p,ct.POINTER(ct.c_uint32),ct.c_size_t];f.restype=ct.c_int
    if f(chain.handle,values.ctypes.data_as(ct.POINTER(ct.c_uint32)),len(values)):raise ValueError('cache快照失败')
    return values

def to(chain,rgb,kernel,threads):
    out=np.empty_like(rgb);error=ct.create_string_buffer(1024);u8=ct.POINTER(ct.c_uint8)
    if bind_to(chain.library.dll)(chain.handle,rgb.ctypes.data_as(u8),out.ctypes.data_as(u8),rgb.nbytes,int(kernel=='avx2'),threads,error,len(error)):
        raise RuntimeError(error.value.decode('utf-8','replace'))
    return out

def freeze():
    if FROZEN.exists():raise FileExistsError('不覆盖质量冻结')
    build_path=BUILD/'build-check.json';build=json.loads(build_path.read_text(encoding='utf-8'))
    contract_path=ROOT/'artifacts/p16-direct-sentinel-v2-contracts-v1/results.json'
    contracts=json.loads(contract_path.read_text(encoding='utf-8'))
    if not build['passed'] or not contracts['passed']:raise ValueError('构建/有限门未通过')
    old_path=ROOT/'artifacts/p16-direct-u16-ilp-frozen-v1/frozen.json'
    old=json.loads(old_path.read_text(encoding='utf-8'))
    roles={name:old['models'][name] for name in ('max_first','p99_first','old_best')}
    max_path=ROOT/'artifacts/cinema-max48-pareto-quality-v1/identity.json'
    max_identity=json.loads(max_path.read_text(encoding='utf-8'))
    roles['max48']=dict(max_identity['roles']['candidate'])
    roles['max48']['oracle']=str(ROOT/'artifacts/cinema-max48-pareto-quality-v1/candidate.rgb')
    roles['max48']['oracle_sha256']='de4a98d5f3b3d430e349e83146d211296a4e6b3e2a9664a5806b321384a3c3f9'
    for role in roles.values():
        for name,expected in role['input_sha256'].items():
            if sha(name)!=expected:raise ValueError('模型变更：'+name)
        if sha(role['oracle'])!=role['oracle_sha256']:raise ValueError('独立全域oracle变更')
    built=json.loads((ROOT/'artifacts/p16-direct-sentinel-v2-build-frozen-v1/frozen.json').read_text(encoding='utf-8'))
    paths={ROOT/name for name in built['sources']}
    paths.update([Path(__file__),ROOT/'scripts/check_direct_sentinel_contracts_v2.py',ROOT/'experiments/channel-runtime/channel_native.py'])
    paths.update((ROOT/'python/lutlab').rglob('*.py'))
    paths.update(ROOT/'scripts'/name for name in ('outplace_support.py','suffix_cache_support.py','domain_cache_support.py','direct16_support.py','palette_support.py'))
    for name,row in built['sources'].items():
        if sha(ROOT/name)!=row['sha256']:raise ValueError('构建源变更：'+name)
    libraries={'new':{'path':str(BUILD/'libjshc_direct_sentinel_v2.dll'),'sha256':build['dll_sha256']},'old87':{'path':old['frozen_87_library'],'sha256':old['frozen_87_sha256']},'old288':{'path':str(ROOT/'artifacts/p16-direct-u16-ilp-build-v1/libjshc_direct_u16_ilp.dll'),'sha256':'d95332e9ac8b56a9d589bf176a5b020e2d60a176d1f360594a0300b5efae5b9f'}}
    for library in libraries.values():
        if sha(library['path'])!=library['sha256']:raise ValueError('运行库身份变更')
    manifest=ORIGINAL/'assets/photos/manifest.json'
    frozen={'schema':'p16_direct_sentinel_quality_v2','scope':'四真实链各6完整域配置+87旧best6配置，共30；四链100照片各2路径共800；972短输入模式/后端及诊断拒绝；全16M物理ID与独立Counter/288精确值核验','roles':roles,'libraries':libraries,'sources_sha256':{path.relative_to(ROOT).as_posix():sha(path) for path in sorted(paths)},'build_check_sha256':sha(build_path),'finite_check_sha256':sha(contract_path),'legacy_identity_sha256':sha(old_path),'max48_identity_sha256':sha(max_path),'manifest':str(manifest),'manifest_sha256':sha(manifest),'environment':study_provenance.environment_fingerprint(),'performance_calls':0,'accuracy_refit':False,'allocation_failure_injection':False}
    FROZEN.mkdir(parents=True)
    for name in frozen['sources_sha256']:
        target=FROZEN/'sources'/name;target.parent.mkdir(parents=True,exist_ok=True);target.write_bytes((ROOT/name).read_bytes())
    save(FROZEN/'frozen.json',frozen)
    print(json.dumps({'frozen_sha256':sha(FROZEN/'frozen.json'),'sources':len(frozen['sources_sha256']),'roles':list(roles),'performance_calls':0}))

def synthetic(library,baseline):
    directory=OUT/'synthetic';directory.mkdir()
    line=np.arange(17,dtype=np.float64)*16;line[-1]=255;grid=np.tile(line,(3,1));r,g,b=np.meshgrid(line,line,line,indexing='ij')
    identity=np.stack((r,g,b),axis=-1).astype(np.uint8);suffix=directory/'identity.slut';io.save_sparse(suffix,io.SparseLut(grid,identity))
    _,frac=io.axis_tables(grid);side=np.repeat(frac[None],3,axis=0);side[1,2,1]+=1
    side_path=directory/'side.bin';side.astype('<u4').tofile(side_path)
    records=[];rng=np.random.default_rng(2026102416)
    sample=np.concatenate((rng.integers(0,256,(4096,3),dtype=np.uint8),np.array([[0,0,0],[255,255,255]],np.uint8)))
    for name in ('255','256','overflow','one_stage'):
        nodes=np.stack((r//2,r//2+g//8,r//2+b//8),axis=-1).astype(np.uint8) if name=='overflow' else np.repeat(r[...,None],3,axis=-1).astype(np.uint8)
        first=directory/(name+'-first.slut');io.save_sparse(first,io.SparseLut(grid,nodes));tail=suffix
        if name in ('255','256'):
            tail=directory/(name+'-tail.slut');out=np.repeat(np.minimum(r,254 if name=='255' else 255)[...,None],3,axis=-1).astype(np.uint8);io.save_sparse(tail,io.SparseLut(grid,out))
        models=[first] if name=='one_stage' else [first,tail,tail,tail];sides=[side_path]+[None]*(len(models)-1)
        with library.chain(models,sides) as chain,baseline.chain(models,sides) as old:
            state=info(chain);direct=direct_info(chain)
            if name=='255':assert not state['enabled'] and state['reason']==1 and direct['format']==9 and direct['enabled']
            elif name=='256':assert state['enabled'] and state['palette_size']==256 and state['whole_cache_colors']==256 and direct['format']==17
            elif name=='overflow':assert not state['enabled'] and state['reason']==3 and state['whole_cache_colors']>65536
            else:assert not state['enabled'] and state['reason']==2
            expected=old.apply(sample.copy(),kernel='scalar',threads=1)
            for kernel,threads in [('scalar',1),('avx2',1),('avx2',4)]:
                np.testing.assert_array_equal(chain.apply(sample.copy(),kernel=kernel,threads=threads),expected);np.testing.assert_array_equal(to(chain,sample,kernel,threads),expected)
            records.append({'name':name,'sentinel':state,'direct':direct,'cache':cache_info(chain),'domain':domain_info(chain),'model_bytes':chain.model_bytes,'sha256':hashlib.sha256(expected.tobytes()).hexdigest()})
    return records

def validate():
    if OUT.exists():raise FileExistsError('不覆盖质量执行目录')
    path=FROZEN/'frozen.json';frozen=json.loads(path.read_text(encoding='utf-8'))
    for name,expected in frozen['sources_sha256'].items():
        if sha(ROOT/name)!=expected:raise ValueError('质量冻结源变更：'+name)
    for spec in frozen['roles'].values():
        for name,expected in spec['input_sha256'].items():
            if sha(name)!=expected:raise ValueError('模型输入变更')
        if sha(spec['oracle'])!=spec['oracle_sha256']:raise ValueError('独立oracle变更')
    for spec in frozen['libraries'].values():
        if sha(spec['path'])!=spec['sha256']:raise ValueError('DLL变更')
    OUT.mkdir(parents=True)
    dll_dirs=[os.add_dll_directory('E:/mingw64/bin'),os.add_dll_directory(str(BUILD))]
    libraries={name:Library(spec['path'],spec['sha256']) for name,spec in frozen['libraries'].items()}
    assert libraries['new'].revision==291 and libraries['old87'].revision==87 and libraries['old288'].revision==288
    result={'frozen_sha256':sha(path),'libraries':frozen['libraries'],'environment':study_provenance.environment_fingerprint(),'performance_calls':0,'capacity':{},'id_identity':[],'full_matrix':[],'photo_matrix':[],'synthetic':synthetic(libraries['new'],libraries['old87'])}
    save(OUT/'start.json',result)
    refs={name:np.memmap(spec['oracle'],np.uint8,'r',shape=(256**3,3)) for name,spec in frozen['roles'].items()}
    with ExitStack() as stack:
        chains={name:stack.enter_context(libraries['new'].chain(spec['models'],spec['sidecars'])) for name,spec in frozen['roles'].items()}
        spec=frozen['roles']['old_best'];chains['87_old_best']=stack.enter_context(libraries['old87'].chain(spec['models'],spec['sidecars']))
        for name,chain in chains.items():
            state=info(chain) if name!='87_old_best' else None
            result['capacity'][name]={'model_bytes':chain.model_bytes,'cache':cache_info(chain),'domain':domain_info(chain),'palette':palette_info(chain),'direct':direct_info(chain),'sentinel':state}
            if name not in ('old_best','87_old_best'):
                assert state['enabled'] and state['format']==17 and state['id_bytes']==1 and state['guard_bytes']==4 and state['palette_size']==256 and state['guaranteed_alignment']==1
                raw=direct_table(chain).view(np.uint8);hot=palette(chain)
                assert raw.size==2**24+4 and np.all(raw[-4:]==0) and hot[255]==0
                counts=Counter(int(value) for value in cache_values(chain))
                expected=np.array(sorted(value for value,count in sorted(counts.items(),key=lambda pair:(-pair[1],pair[0]))[:255]),np.uint32)
                np.testing.assert_array_equal(hot[:255],expected)
                spec=frozen['roles'][name]
                with libraries['old288'].chain(spec['models'],spec['sidecars']) as old:
                    old_raw=direct_table(old).view(np.uint16);old_palette=palette(old,False);miss=0
                    assert old_raw.size==2**24+2 and np.all(old_raw[-2:]==0)
                    for start in range(0,2**24,65536):
                        values=old_palette[old_raw[start:start+65536]];positions=np.searchsorted(expected,values)
                        present=(positions<255)&(expected[np.minimum(positions,254)]==values)
                        wanted=np.where(present,positions,255).astype(np.uint8)
                        np.testing.assert_array_equal(raw[start:start+65536],wanted);miss+=int(np.count_nonzero(~present))
                result['id_identity'].append({'model':name,'raw_sha256':hashlib.sha256(raw.tobytes()).hexdigest(),'palette_sha256':hashlib.sha256(hot.tobytes()).hexdigest(),'whole_cache_colors':len(counts),'domain_misses':miss,'full_physical_entries':2**24,'guard_zero':True,'independent_counter':True,'legacy288_values_equal':True})
                del raw,old_raw,old_palette
            else:assert direct_info(chain)['enabled'] and direct_info(chain)['format']==9
        save(OUT/'tables.json',result)
        hashes={(name,kernel,threads,route):hashlib.sha256() for name in chains for kernel,threads in [('scalar',1),('avx2',1),('avx2',4)] for route in ('inplace','to')}
        for start in range(0,2**24,65536):
            keys=np.arange(start,start+65536,dtype=np.int64);rgb=np.column_stack((keys>>16,(keys>>8)&255,keys&255)).astype(np.uint8);before=rgb.copy()
            for name,chain in chains.items():
                expected=refs['old_best' if name=='87_old_best' else name][keys]
                for kernel,threads in [('scalar',1),('avx2',1),('avx2',4)]:
                    for route in ('inplace','to'):
                        actual=chain.apply(rgb.copy(),kernel=kernel,threads=threads) if route=='inplace' else to(chain,rgb,kernel,threads)
                        np.testing.assert_array_equal(actual,expected);hashes[name,kernel,threads,route].update(actual.tobytes())
            np.testing.assert_array_equal(rgb,before)
        result['full_matrix']=[{'model':name,'kernel':kernel,'threads':threads,'path':route,'sha256':digest.hexdigest(),'mismatches':0} for (name,kernel,threads,route),digest in hashes.items()]
        assert len(result['full_matrix'])==30
        save(OUT/'full.json',result);print(json.dumps({'full_configs':30,'mismatches':0,'performance_calls':0}),flush=True)
        manifest=Path(frozen['manifest'])
        if sha(manifest)!=frozen['manifest_sha256']:raise ValueError('照片manifest变更')
        images=json.loads(manifest.read_text(encoding='utf-8'))['images']
        assert len(images)==100
        for row in images:
            image_path=ORIGINAL/row['evaluation']['path']
            if sha(image_path)!=row['evaluation']['sha256']:raise ValueError('照片内容变更')
            with Image.open(image_path) as image:rgb=np.asarray(image).reshape(-1,3).copy()
            keys=rgb.astype(np.int64)@np.array([65536,256,1],np.int64);before=rgb.copy()
            for name,chain in chains.items():
                if name=='87_old_best':continue
                expected=refs[name][keys]
                for route in ('inplace','to'):
                    actual=chain.apply(rgb.copy(),kernel='avx2',threads=4) if route=='inplace' else to(chain,rgb,'avx2',4)
                    np.testing.assert_array_equal(actual,expected);result['photo_matrix'].append({'image':row['id'],'model':name,'path':route,'sha256':hashlib.sha256(actual.tobytes()).hexdigest(),'mismatches':0})
            np.testing.assert_array_equal(rgb,before)
        assert len(result['photo_matrix'])==800
        short=0;rng=np.random.default_rng(2026102417)
        for name,chain in chains.items():
            if name=='87_old_best':continue
            for length in [*range(18),31,32,33,4095,4096,4097,65535,65536,65537]:
                for pattern in ('random','white','mixed'):
                    rgb=np.full((length,3),255,np.uint8) if pattern=='white' else rng.integers(0,256,(length,3),dtype=np.uint8)
                    if pattern=='mixed':rgb[::7]=255
                    keys=rgb.astype(np.int64)@np.array([65536,256,1],np.int64);expected=refs[name][keys]
                    for kernel,threads in [('scalar',1),('avx2',1),('avx2',4)]:
                        np.testing.assert_array_equal(chain.apply(rgb.copy(),kernel=kernel,threads=threads),expected)
                        for same in (False,True):
                            if apply_to(chain.library.dll,chain.handle,rgb.tobytes(),int(kernel=='avx2'),threads,source_offset=1,target_offset=3,same=same)!=expected.tobytes():raise ValueError('短尾/未对齐/同址错误')
                        short+=1
            result.setdefault('outplace_rejections',{})[name]=reject_to(chain.library.dll,chain.handle)
        assert short==972
        chain=chains['max_first'];value=Info();ct.memset(ct.byref(value),0xa7,96);before=bytes(value);f=libraries['new'].dll.p16_cc_get_direct_sentinel_info;rejected=0
        for handle,pointer,size in [(None,ct.byref(value),96),(chain.handle,None,96),(chain.handle,ct.byref(value),95),(chain.handle,ct.byref(value),97)]:
            assert f(handle,pointer,size)==1 and bytes(value)==before;rejected+=1
        values=np.full(256,0xa7a7a7a7,np.uint32);pointer=values.ctypes.data_as(ct.POINTER(ct.c_uint32));before=values.copy();f=libraries['new'].dll.p16_cc_copy_sentinel_palette
        for handle,out,count in [(None,pointer,256),(chain.handle,None,256),(chain.handle,pointer,255),(chain.handle,pointer,257)]:
            assert f(handle,out,count)==1 and np.array_equal(values,before);rejected+=1
        result['contract']={'short_pattern_backend_cases':short,'diagnostic_rejections':rejected,'allocation_failure_injection':False,'performance_calls':0}
    for name,expected in frozen['sources_sha256'].items():
        if sha(ROOT/name)!=expected:raise ValueError('执行后源变更：'+name)
    for spec in frozen['libraries'].values():
        if sha(spec['path'])!=spec['sha256']:raise ValueError('执行后DLL变更')
    result['passed']=True;result['limitations']='仅整数正确性和容量；尚无正式速度/真实RSS、分配失败与无AVX2注入。100图已见，官方Threshold与派生表许可仍未知。'
    save(OUT/'results.json',result)
    print(json.dumps({'passed':True,'full_configs':len(result['full_matrix']),'photo_configs':len(result['photo_matrix']),'contract':result['contract'],'performance_calls':0}),flush=True)

def main():
    parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('--freeze',action='store_true');args=parser.parse_args()
    if args.freeze:freeze()
    else:validate()

if __name__=='__main__':main()
