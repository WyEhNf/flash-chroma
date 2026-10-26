"""187关闭/开启及冻结87的全域、照片、尾部和typed拒绝正确性；不计性能。"""
from __future__ import annotations
import argparse
import ctypes as ct
import hashlib
import json
import os
from pathlib import Path
import sys
from contextlib import ExitStack
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'python'))
sys.path.insert(0,str(ROOT/'experiments/channel-runtime'))
import numpy as np
from PIL import Image
from lutlab import io,study_provenance
from channel_native import Library
from run_channel_tail_nodes import digest,save
from outplace_support import bind_to,apply_to,reject_to
from suffix_cache_support import cache_info


class Config(ct.Structure):
    _fields_=[(n,ct.c_uint32) for n in ('version','enabled','kappa','count')]+[('cells',ct.c_uint32*2),('masks',ct.c_uint32*2)]


class Info(ct.Structure):
    _fields_=[(n,ct.c_uint32) for n in ('version','enabled','hit_record_bytes','max_records')]+[('maximum_hit_stack_bytes',ct.c_uint64)]


def config(enabled):return Config(1,enabled,3,2,(ct.c_uint32*2)(31725,31726),(ct.c_uint32*2)(1,1))


def bind(d):
    d.p16_cc_set_bubble.argtypes=[ct.c_void_p,ct.POINTER(Config),ct.POINTER(ct.c_char),ct.c_size_t]
    d.p16_cc_set_bubble.restype=ct.c_int
    d.p16_cc_get_bubble_info.argtypes=[ct.c_void_p,ct.POINTER(Info),ct.POINTER(ct.c_char),ct.c_size_t]
    d.p16_cc_get_bubble_info.restype=ct.c_int


def set_mode(chain,enabled):
    error=ct.create_string_buffer(1024)
    if chain.library.dll.p16_cc_set_bubble(chain.handle,ct.byref(config(enabled)),error,len(error)):
        raise RuntimeError(error.value.decode('utf-8','replace'))


def info(chain):
    out=Info();error=ct.create_string_buffer(1024)
    if chain.library.dll.p16_cc_get_bubble_info(chain.handle,ct.byref(out),error,len(error)):raise AssertionError('info失败')
    return {n:getattr(out,n) for n,_ in Info._fields_}


def to(chain,rgb,kernel,threads):
    out=np.empty_like(rgb);error=ct.create_string_buffer(1024);u8=ct.POINTER(ct.c_uint8)
    code=bind_to(chain.library.dll)(chain.handle,rgb.ctypes.data_as(u8),out.ctypes.data_as(u8),rgb.nbytes,int(kernel=='avx2'),threads,error,len(error))
    if code:raise RuntimeError(error.value.decode('utf-8','replace'))
    return out


def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--cache-root',type=Path,required=True);p.add_argument('--frozen',type=Path,required=True)
    p.add_argument('--library',type=Path,required=True);p.add_argument('--output',type=Path,required=True)
    args=p.parse_args()
    if args.output.exists():raise ValueError('不覆盖原生验收')
    args.output.mkdir(parents=True)
    frozen=json.loads((args.frozen/'frozen.json').read_text(encoding='utf-8'))
    for name,sha in frozen['source_sha256'].items():
        if digest(ROOT/name)!=sha:raise ValueError('构建冻结后源码已变')
    for name,sha in frozen['serialized_sha256'].items():
        if digest(args.frozen/name)!=sha:raise ValueError('序列化模型变动')
    refs={'off':args.cache_root/'artifacts/velvia-channel-coordinates-accept-v1/cube.rgb','on':ROOT/'artifacts/velvia-bubble-accept-v1/candidate.rgb'}
    if digest(refs['off'])!=frozen['oracle_baseline_sha256'] or digest(refs['on'])!=frozen['oracle_candidate_sha256']:raise ValueError('oracle SHA不符')
    reference={n:np.memmap(path,np.uint8,'r',shape=(256**3,3)) for n,path in refs.items()}
    dll_directories=[os.add_dll_directory('E:/mingw64/bin'),os.add_dll_directory(str(args.library.resolve().parent))]
    libraries={'87':Library(frozen['frozen_87_library'],frozen['frozen_87_sha256']),'187':Library(args.library,digest(args.library))}
    assert libraries['87'].revision==87 and libraries['187'].revision==187
    bind(libraries['187'].dll)
    result={'environment':study_provenance.environment_fingerprint(),'input_frozen_sha256':digest(args.frozen/'frozen.json'),
        'quality_source_sha256':digest(Path(__file__)),'library_sha256':{n:v.sha256 for n,v in libraries.items()},
        'performance_calls':0,'new_default':False,'full_matrix':[],'photo_matrix':[]}
    save(args.output/'run.json',result)
    base=args.frozen/'base.slut';side=args.frozen/'channel-frac.bin'
    with ExitStack() as stack:
        chains={'87':stack.enter_context(libraries['87'].chain([base],[side])),
            '187off':stack.enter_context(libraries['187'].chain([base],[side])),
            '187on':stack.enter_context(libraries['187'].chain([base],[side]))}
        set_mode(chains['187off'],0);set_mode(chains['187on'],1)
        result['capacity']={n:{'model_bytes':c.model_bytes,'cache':cache_info(c),'bubble':info(c) if n!='87' else None} for n,c in chains.items()}
        # 全色域覆盖所有三种后端/线程与两种输入输出语义。
        hashes={(n,k,t,path):hashlib.sha256() for n in chains for k,t in [('scalar',1),('avx2',1),('avx2',4)] for path in ('inplace','to')}
        for start in range(0,256**3,65536):
            keys=np.arange(start,start+65536,dtype=np.int64)
            rgb=np.column_stack((keys>>16,(keys>>8)&255,keys&255)).astype(np.uint8);before=rgb.copy()
            for n,c in chains.items():
                expected=reference['on' if n=='187on' else 'off'][keys]
                for kernel,threads in [('scalar',1),('avx2',1),('avx2',4)]:
                    for path in ('inplace','to'):
                        out=c.apply(rgb.copy(),kernel=kernel,threads=threads) if path=='inplace' else to(c,rgb,kernel,threads)
                        np.testing.assert_array_equal(out,expected);hashes[n,kernel,threads,path].update(out.tobytes())
            np.testing.assert_array_equal(rgb,before)
        result['full_matrix']=[{'model':n,'kernel':k,'threads':t,'path':path,'sha256':h.hexdigest(),'mismatches':0} for (n,k,t,path),h in hashes.items()]
        print(json.dumps({'full_matrix_configs':len(hashes),'all_mismatches':0,'capacity':result['capacity']},ensure_ascii=False),flush=True)
        # 每张历史照片新鲜AVX2/4前向，真实分离与原地各验三模型。
        manifest=json.loads((args.cache_root/'assets/photos/manifest.json').read_text(encoding='utf-8'))
        for row in manifest['images']:
            path=args.cache_root/row['evaluation']['path']
            if digest(path)!=row['evaluation']['sha256']:raise ValueError('照片SHA不符')
            with Image.open(path) as image:rgb=np.asarray(image).reshape(-1,3).copy()
            keys=rgb.astype(np.int64)@np.array([65536,256,1],np.int64)
            for n,c in chains.items():
                expected=reference['on' if n=='187on' else 'off'][keys]
                for path in ('inplace','to'):
                    out=c.apply(rgb.copy(),kernel='avx2',threads=4) if path=='inplace' else to(c,rgb,'avx2',4)
                    np.testing.assert_array_equal(out,expected)
                    result['photo_matrix'].append({'image':row['id'],'model':n,'path':path,'sha256':hashlib.sha256(out.tobytes()).hexdigest(),'mismatches':0})
        c=chains['187on'];d=c.library.dll;error=ct.create_string_buffer(1024);rejected=0
        for field,value in [('version',0),('enabled',2),('kappa',2),('count',1),('cells',0),('masks',0)]:
            bad=config(1)
            if field in ('cells','masks'):getattr(bad,field)[0]=value
            else:setattr(bad,field,value)
            if d.p16_cc_set_bubble(c.handle,ct.byref(bad),error,len(error))!=1 or info(c)['enabled']!=1:raise AssertionError('typed错误未拒绝或改变模式')
            rejected+=1
        for handle,value in [(None,ct.byref(config(1))),(c.handle,None)]:
            if d.p16_cc_set_bubble(handle,value,error,len(error))!=1:raise AssertionError('null未拒绝')
            rejected+=1
        for models,sides in [([base],[None]),([base,base],[side,side])]:
            with libraries['187'].chain(models,sides) as invalid:
                if d.p16_cc_set_bubble(invalid.handle,ct.byref(config(1)),error,len(error))!=1:raise AssertionError('不支持stage/base未拒绝')
                rejected+=1
        small=args.output/'contract17.slut'
        io.save_sparse(small,io.SparseLut(np.tile(np.linspace(0,255,17),(3,1)),np.zeros((17,17,17,3),np.uint8)))
        with libraries['187'].chain([small]) as invalid:
            if d.p16_cc_set_bubble(invalid.handle,ct.byref(config(1)),error,len(error))!=1:raise AssertionError('m17未拒绝')
            rejected+=1
        rng=np.random.default_rng(2026102401);short_cases=0
        for length in [*range(18),31,32,33,4095,4096,4097,65535,65536,65537]:
            for pattern in ('dense','none','mixed'):
                rgb=np.tile(np.array([[239,252,113]],np.uint8),(length,1)) if pattern=='dense' else (np.zeros((length,3),np.uint8) if pattern=='none' else rng.integers(0,256,(length,3),dtype=np.uint8))
                if pattern=='mixed':rgb[::7]=[239,252,114]
                keys=rgb.astype(np.int64)@np.array([65536,256,1],np.int64);expected=reference['on'][keys]
                for kernel,threads in [('scalar',1),('avx2',1),('avx2',4)]:
                    np.testing.assert_array_equal(c.apply(rgb.copy(),kernel=kernel,threads=threads),expected)
                    for same in (False,True):
                        actual=apply_to(d,c.handle,rgb.tobytes(),int(kernel=='avx2'),threads,source_offset=1,target_offset=3,same=same)
                        if actual!=expected.tobytes():raise AssertionError('密集/尾部/偏移输出不符')
                    short_cases+=1
        result['contract']={'typed_or_shape_rejections':rejected,'short_dense_none_mixed_cases':short_cases,'invalid_outplace_rejections':reject_to(d,c.handle),'all_mismatches':0}
    result['passed']=True
    result['limitations']='仅正确性与逻辑容量；未正式计时，未测RSS/构造峰值；非stock表示及邻接代价继续有效'
    save(args.output/'results.json',result)
    print(json.dumps({'passed':True,'full_configs':len(result['full_matrix']),'photo_configs':len(result['photo_matrix']),'contract':result['contract']},ensure_ascii=False),flush=True)


if __name__=='__main__':main()
