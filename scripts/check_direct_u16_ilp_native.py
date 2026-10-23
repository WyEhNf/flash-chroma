"""精确16bit直接ID的冻结、有限合同、完整域与逐图正确性；不计性能。"""
from __future__ import annotations
import argparse
import ctypes as ct
import hashlib
import json
import os
from pathlib import Path
import subprocess
import sys
from contextlib import ExitStack
ROOT=Path(__file__).resolve().parents[1]
sys.path[:0]=[str(ROOT/'python'),str(ROOT/'experiments/channel-runtime')]
import numpy as np
from PIL import Image
from lutlab import io,study_provenance
from channel_native import Library
from run_channel_tail_nodes import digest,save
from outplace_support import bind_to,apply_to,reject_to
from suffix_cache_support import cache_info
from domain_cache_support import info as domain_info
from direct16_support import info as direct_info,table as direct_table
from palette_support import info as palette_info


class Info(ct.Structure):
    _fields_=[(n,ct.c_uint32) for n in ('version','enabled','format','reason','palette_size','id_bytes','guard_bytes','reserved')]
    _fields_ += [(n,ct.c_uint64) for n in ('input_entries','raw_words','table_capacity_bytes','palette_capacity_bytes','temporary_peak_bytes','guaranteed_alignment','data_mod_64')]
    _fields_ += [('prepare_seconds',ct.c_double)]


def info(chain):
    d=chain.library.dll;f=d.p16_cc_get_direct_u16_info
    f.argtypes=[ct.c_void_p,ct.POINTER(Info),ct.c_size_t];f.restype=ct.c_int
    value=Info()
    if ct.sizeof(value)!=96 or f(chain.handle,ct.byref(value),ct.sizeof(value)) or value.version!=1:raise ValueError('16bit诊断ABI不同')
    return {n:getattr(value,n) for n,_ in value._fields_}


def to(chain,rgb,kernel,threads):
    out=np.empty_like(rgb);error=ct.create_string_buffer(1024);u8=ct.POINTER(ct.c_uint8)
    if bind_to(chain.library.dll)(chain.handle,rgb.ctypes.data_as(u8),out.ctypes.data_as(u8),rgb.nbytes,int(kernel=='avx2'),threads,error,len(error)):
        raise RuntimeError(error.value.decode('utf-8','replace'))
    return out


def freeze(args):
    if args.output.exists():raise ValueError('不覆盖冻结目录')
    args.output.mkdir(parents=True)
    original=args.cache_root/'artifacts/cinema-envelope-v1/stage4_sweep004'
    specs={}
    for name in ('max_first','p99_first','old_best'):
        directory=ROOT/('artifacts/cinema-arrival-last-budget-v1/candidate' if name=='old_best' else 'artifacts/cinema-second-nodes-v1/'+name+'/candidate')
        models=[directory/'candidate-base.slut',original/'selected-stage2.slut' if name=='old_best' else directory/'stage2.slut',original/'selected-stage3.slut',directory/'stage4.slut']
        oracle=ROOT/('artifacts/cinema-arrival-budget-accept-v1/candidate.rgb' if name=='old_best' else 'artifacts/cinema-second-accept-'+name+'-v1/candidate.rgb')
        expected={'max_first':'143e5cc05f4f2635608cd7720b4013a10998d3f7acc8cf35275b38dcfba0792e',
            'p99_first':'4f3bb1eb15cadc38eea189fdbdc11495c9541889c67315bbbc96e5c08f9cf12c',
            'old_best':'373a2fcbe4fafb73a6daebfd5c71b3308cdb43baf289e37fc564e75dc9033aed'}[name]
        if digest(oracle)!=expected:raise ValueError('已有独立oracle变更')
        specs[name]={'models':[str(p.resolve()) for p in models],'sidecars':[str((directory/'channel-frac.bin').resolve()),None,None,None],
            'oracle':str(oracle.resolve()),'oracle_sha256':expected,'input_sha256':{str(p.resolve()):digest(p) for p in [*models,directory/'channel-frac.bin']}}
    paths={ROOT/'CMakeLists.txt',Path(__file__),ROOT/'experiments/p16-direct-u16-ilp-plan-v1.md'}
    for directory in ('cpp','portable','experiments/p16-direct-u16-ilp-runtime','experiments/skylake-andn-normal-runtime','experiments/skylake-domain-isolated-runtime',
            'experiments/skylake-exception-runtime','experiments/skylake-suffix-cache-runtime','experiments/channel-runtime'):
        paths.update(p for p in (ROOT/directory).rglob('*') if p.is_file() and (p.suffix in ('.c','.cpp','.hpp','.h') or p.name=='CMakeLists.txt'))
    paths.add(ROOT/'scripts/prepare_direct_u16_ilp.py')
    paths.add(ROOT/'scripts/inspect_direct_u16_rss.py')
    paths.update(ROOT/'scripts'/name for name in ('run_channel_tail_nodes.py','outplace_support.py','suffix_cache_support.py','domain_cache_support.py',
        'direct16_support.py','palette_support.py','exception_support.py'))
    paths.update(ROOT/'python/lutlab'/name for name in ('io.py','study_provenance.py'))
    paths.add(ROOT/'experiments/channel-runtime/channel_native.py')
    old=Path('F:/Hackathon/worktrees/p16-speed-20261023/artifacts/p16-speed-direct-build-v1/libjshc_direct_prepare_simd.dll')
    old_sha='58591a725d367dce3713ff88af4d5549afea5af1ac4f3a39284443586893c158'
    if digest(old)!=old_sha:raise ValueError('冻结87库变更')
    legacy=ROOT/'artifacts/p16-direct-u16-build-v1/libjshc_direct_u16.dll';legacy_sha='5ec24854848159541c55f58aff831bec5de401d794cf3dfe3fddf64e3ebcb508'
    if digest(legacy)!=legacy_sha:raise ValueError('287 DLL变更')
    save(args.output/'frozen.json',{'schema':'p16_direct_u16_ilp_quality_v1','models':specs,'frozen_87_library':str(old),'frozen_87_sha256':old_sha,
        'frozen_287_library':str(legacy),'frozen_287_sha256':legacy_sha,
        'sources_sha256':{p.relative_to(ROOT).as_posix():digest(p) for p in sorted(paths)},'photo_manifest_sha256':digest(args.cache_root/'assets/photos/manifest.json'),
        'quality_scope':'三模型完整域18配置，旧best冻结87再6配置，600逐图，有限类型/guard/尾部/回退；无性能','environment':study_provenance.environment_fingerprint()})


def synthetic(library,output):
    directory=output/'synthetic';directory.mkdir()
    line=np.arange(17,dtype=np.float64)*16;line[-1]=255;grid=np.tile(line,(3,1));r,g,b=np.meshgrid(line,line,line,indexing='ij')
    identity=np.stack((r,g,b),axis=-1).astype(np.uint8)
    suffix=directory/'identity.slut';io.save_sparse(suffix,io.SparseLut(grid,identity))
    _,frac=io.axis_tables(grid);side=np.repeat(frac[None],3,axis=0);side[1,2,1]+=1
    side_path=directory/'side.bin';side.astype('<u4').tofile(side_path)
    records=[];rng=np.random.default_rng(2026102416)
    sample=np.concatenate((rng.integers(0,256,(4096,3),dtype=np.uint8),np.array([[0,0,0],[255,255,255]],np.uint8)))
    for name in ('255','256','overflow','one_stage'):
        if name=='overflow':nodes=np.stack((r//2,r//2+g//8,r//2+b//8),axis=-1).astype(np.uint8)
        else:nodes=np.repeat(r[...,None],3,axis=-1).astype(np.uint8)
        first=directory/(name+'-first.slut');io.save_sparse(first,io.SparseLut(grid,nodes))
        tail=suffix
        if name in ('255','256'):
            tail=directory/(name+'-tail.slut');out=np.repeat(np.minimum(r,254 if name=='255' else 255)[...,None],3,axis=-1).astype(np.uint8)
            io.save_sparse(tail,io.SparseLut(grid,out))
        models=[first] if name=='one_stage' else [first,tail,tail,tail];sides=[side_path]+[None]*(len(models)-1)
        with library.chain(models,sides) as chain:
            state=info(chain);row={'name':name,'wide':state,'direct':direct_info(chain),'cache':cache_info(chain),'domain':domain_info(chain),'model_bytes':chain.model_bytes}
            if name=='255':assert state['enabled']==0 and state['reason']==1 and row['direct']['format']==9 and row['direct']['enabled']==1
            elif name=='256':assert state['enabled']==1 and state['palette_size']==256 and row['direct']['format']==16
            elif name=='overflow':assert state['enabled']==0 and state['reason']==3 and state['palette_size']>65536
            else:assert state['enabled']==0 and state['reason']==2
            # 冻结87的标量整数模型执行构成独立运行时对照，不依赖新直表。
            with library.baseline.chain(models,sides) as old:
                expected=old.apply(sample.copy(),kernel='scalar',threads=1)
            for kernel,threads in [('scalar',1),('avx2',1),('avx2',4)]:
                np.testing.assert_array_equal(chain.apply(sample.copy(),kernel=kernel,threads=threads),expected)
                np.testing.assert_array_equal(to(chain,sample,kernel,threads),expected)
            row['sample_sha256']=hashlib.sha256(expected.tobytes()).hexdigest();records.append(row)
    return records


def validate(args):
    if args.output.exists():raise ValueError('不覆盖原生验收')
    args.output.mkdir(parents=True)
    frozen=json.loads(args.frozen.read_text(encoding='utf-8'))
    for path,sha in frozen['sources_sha256'].items():
        if digest(ROOT/path)!=sha:raise ValueError('冻结后源码变更：'+path)
    for spec in frozen['models'].values():
        for path,sha in spec['input_sha256'].items():
            if digest(path)!=sha:raise ValueError('模型变更')
        if digest(spec['oracle'])!=spec['oracle_sha256']:raise ValueError('oracle变更')
    dll_dirs=[os.add_dll_directory('E:/mingw64/bin'),os.add_dll_directory(str(args.library.resolve().parent))]
    contract=subprocess.run([str(args.contracts.resolve())],capture_output=True,text=True)
    (args.output/'contracts-stdout.txt').write_text(contract.stdout,encoding='utf-8');(args.output/'contracts-stderr.txt').write_text(contract.stderr,encoding='utf-8')
    if contract.returncode:raise RuntimeError('独立guard合同失败，返回码'+str(contract.returncode))
    guard=json.loads(contract.stdout)
    assert guard['guarded_cases']==(88 if guard['bmi_supported'] else 22)
    library=Library(args.library,digest(args.library));library.baseline=Library(frozen['frozen_87_library'],frozen['frozen_87_sha256'])
    legacy=Library(frozen['frozen_287_library'],frozen['frozen_287_sha256'])
    assert library.revision==288 and library.baseline.revision==87
    result={'frozen_sha256':digest(args.frozen),'library_sha256':library.sha256,'contracts_exe_sha256':digest(args.contracts),
        'environment':study_provenance.environment_fingerprint(),'performance_calls':0,'new_default':False,'guard_contract':json.loads(contract.stdout),
        'full_matrix':[],'photo_matrix':[],'capacity':{}}
    save(args.output/'run.json',result)
    result['synthetic']=synthetic(library,args.output)
    refs={n:np.memmap(s['oracle'],np.uint8,'r',shape=(256**3,3)) for n,s in frozen['models'].items()}
    with ExitStack() as stack:
        chains={n:stack.enter_context(library.chain(s['models'],s['sidecars'])) for n,s in frozen['models'].items()}
        spec=frozen['models']['old_best'];chains['87_old_best']=stack.enter_context(library.baseline.chain(spec['models'],spec['sidecars']))
        for n,c in chains.items():
            result['capacity'][n]={'model_bytes':c.model_bytes,'cache':cache_info(c),'domain':domain_info(c),'palette':palette_info(c),'direct':direct_info(c),'wide':info(c) if n!='87_old_best' else None}
            if n in ('max_first','p99_first'):assert info(c)['enabled']==1 and direct_info(c)['format']==16
            else:assert direct_info(c)['format']==9 and direct_info(c)['enabled']==1
        result['287_table_identity']=[]
        for n in ('max_first','p99_first'):
            spec=frozen['models'][n]
            with legacy.chain(spec['models'],spec['sidecars']) as old:
                raw_old=direct_table(old);raw_new=direct_table(chains[n]);np.testing.assert_array_equal(raw_old,raw_new)
                old_palette=np.unique(np.frombuffer(_cache_bytes(old),np.uint32));new_palette=np.unique(np.frombuffer(_cache_bytes(chains[n]),np.uint32))
                np.testing.assert_array_equal(old_palette,new_palette)
                assert old.model_bytes==chains[n].model_bytes
                result['287_table_identity'].append({'model':n,'table_sha256':hashlib.sha256(raw_new.tobytes()).hexdigest(),
                    'palette_sha256':hashlib.sha256(new_palette.tobytes()).hexdigest(),'table_bytes_equal':True,'palette_equal':True,'capacity_equal':True,
                    '287_data_mod64':info(old)['data_mod_64'],'288_data_mod64':info(chains[n])['data_mod_64']})
        hashes={(n,k,t,p):hashlib.sha256() for n in chains for k,t in [('scalar',1),('avx2',1),('avx2',4)] for p in ('inplace','to')}
        for start in range(0,256**3,65536):
            keys=np.arange(start,start+65536,dtype=np.int64);rgb=np.column_stack((keys>>16,(keys>>8)&255,keys&255)).astype(np.uint8);before=rgb.copy()
            for n,c in chains.items():
                expected=refs['old_best' if n=='87_old_best' else n][keys]
                for kernel,threads in [('scalar',1),('avx2',1),('avx2',4)]:
                    for path in ('inplace','to'):
                        out=c.apply(rgb.copy(),kernel=kernel,threads=threads) if path=='inplace' else to(c,rgb,kernel,threads)
                        np.testing.assert_array_equal(out,expected);hashes[n,kernel,threads,path].update(out.tobytes())
            np.testing.assert_array_equal(rgb,before)
        result['full_matrix']=[{'model':n,'kernel':k,'threads':t,'path':p,'sha256':h.hexdigest(),'mismatches':0} for (n,k,t,p),h in hashes.items()]
        save(args.output/'full.json',result)
        print(json.dumps({'full_configs':len(hashes),'mismatches':0,'capacity':result['capacity']},ensure_ascii=False),flush=True)
        manifest_path=args.cache_root/'assets/photos/manifest.json'
        if digest(manifest_path)!=frozen['photo_manifest_sha256']:raise ValueError('照片manifest变更')
        for row in json.loads(manifest_path.read_text(encoding='utf-8'))['images']:
            path=args.cache_root/row['evaluation']['path']
            if digest(path)!=row['evaluation']['sha256']:raise ValueError('照片变更')
            with Image.open(path) as image:rgb=np.asarray(image).reshape(-1,3).copy()
            keys=rgb.astype(np.int64)@np.array([65536,256,1],np.int64)
            for n,c in chains.items():
                if n=='87_old_best':continue
                expected=refs[n][keys]
                for path in ('inplace','to'):
                    out=c.apply(rgb.copy(),kernel='avx2',threads=4) if path=='inplace' else to(c,rgb,'avx2',4)
                    np.testing.assert_array_equal(out,expected);result['photo_matrix'].append({'image':row['id'],'model':n,'path':path,'sha256':hashlib.sha256(out.tobytes()).hexdigest(),'mismatches':0})
        short=0;rng=np.random.default_rng(2026102417)
        for n in ('max_first','p99_first','old_best'):
            c=chains[n]
            for length in [*range(18),31,32,33,4095,4096,4097,65535,65536,65537]:
                for pattern in ('random','white','mixed'):
                    rgb=np.full((length,3),255,np.uint8) if pattern=='white' else rng.integers(0,256,(length,3),dtype=np.uint8)
                    if pattern=='mixed':rgb[::7]=255
                    keys=rgb.astype(np.int64)@np.array([65536,256,1],np.int64);expected=refs[n][keys]
                    for kernel,threads in [('scalar',1),('avx2',1),('avx2',4)]:
                        np.testing.assert_array_equal(c.apply(rgb.copy(),kernel=kernel,threads=threads),expected)
                        for same in (False,True):
                            if apply_to(c.library.dll,c.handle,rgb.tobytes(),int(kernel=='avx2'),threads,source_offset=1,target_offset=3,same=same)!=expected.tobytes():raise AssertionError('短输入/同址/未对齐错误')
                        short+=1
            result.setdefault('outplace_rejections',{})[n]=reject_to(c.library.dll,c.handle)
        c=chains['max_first'];f=library.dll.p16_cc_get_direct_u16_info;v=Info();ct.memset(ct.byref(v),0xa7,ct.sizeof(v));before=bytes(v)
        rejected=0
        for handle,pointer,size in [(None,ct.byref(v),96),(c.handle,None,96),(c.handle,ct.byref(v),95),(c.handle,ct.byref(v),97)]:
            assert f(handle,pointer,size)==1 and bytes(v)==before;rejected+=1
        f=library.dll.p16_cc_copy_u16_palette;f.argtypes=[ct.c_void_p,ct.POINTER(ct.c_uint32),ct.c_size_t];f.restype=ct.c_int
        state=info(c);palette=np.full(state['palette_size'],0xa7a7a7a7,np.uint32);pointer=palette.ctypes.data_as(ct.POINTER(ct.c_uint32));before=palette.copy()
        for handle,out,count in [(None,pointer,len(palette)),(c.handle,None,len(palette)),(c.handle,pointer,len(palette)-1),(c.handle,pointer,len(palette)+1)]:
            assert f(handle,out,count)==1 and np.array_equal(palette,before);rejected+=1
        assert f(c.handle,pointer,len(palette))==0
        # 快照按原始u32词复制，物理布局仍是u16；最后两个u16为owned guard。
        raw=direct_table(c);state=info(c);words=raw.view(np.uint16)
        assert len(words)==(1<<24)+2 and np.all(words[-2:]==0) and words[:-2].max()<state['palette_size']
        np.testing.assert_array_equal(palette,np.unique(np.frombuffer(_cache_bytes(c),dtype=np.uint32)))
        result['direct_snapshot']={'sha256':hashlib.sha256(raw.tobytes()).hexdigest(),'raw_words':len(raw),'max_id':int(words[:-2].max()),'guard_zero':True}
        result['contract']={'short_pattern_backend_cases':short,'diagnostic_rejections':rejected,'mismatches':0,'allocation_failure_injection':False}
    result['passed']=True;result['limitations']='仅正确性及逻辑容量；未正式性能/RSS/构造峰值，分配失败未注入；x86小端AVX2，sidecar官方许可未知'
    save(args.output/'results.json',result)
    print(json.dumps({'passed':True,'full_configs':len(result['full_matrix']),'photo_configs':len(result['photo_matrix']),'contract':result['contract']},ensure_ascii=False),flush=True)


def _cache_bytes(chain):
    count=cache_info(chain)['entries'];values=np.empty(count,np.uint32)
    f=chain.library.dll.jshc_cc_copy_cache;f.argtypes=[ct.c_void_p,ct.POINTER(ct.c_uint32),ct.c_size_t];f.restype=ct.c_int
    if f(chain.handle,values.ctypes.data_as(ct.POINTER(ct.c_uint32)),count):raise AssertionError('完整cache快照失败')
    return values.tobytes()


def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--cache-root',type=Path,required=True);p.add_argument('--output',type=Path,required=True)
    p.add_argument('--freeze',action='store_true');p.add_argument('--frozen',type=Path);p.add_argument('--library',type=Path);p.add_argument('--contracts',type=Path);args=p.parse_args()
    if args.freeze:freeze(args)
    else:
        if not all((args.frozen,args.library,args.contracts)):raise ValueError('验收需要冻结清单、DLL与独立合同程序')
        validate(args)


if __name__=='__main__':main()
