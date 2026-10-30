"""直接编译管线的完整整数验证及独立进程配对计时。"""
from __future__ import annotations
import argparse
import ctypes as ct
import hashlib
import importlib.util
import json
import os
from pathlib import Path
import platform
import statistics
import subprocess
import sys
import time
import numpy as np
from PIL import Image
import psutil

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'experiments/channel-runtime'))
from channel_native import Library,digest
from palette_support import tables,info
from outplace_support import bind_to,apply_to,reject_to

def save(path,data):
    path.parent.mkdir(parents=True,exist_ok=True)
    path.write_text(json.dumps(data,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')

def models(root):
    return ([root/'artifacts/cinema-current-anchor-accept-v1/candidate-base.slut']+
            [root/f'artifacts/cinema-envelope-v1/stage4_sweep004/selected-stage{i}.slut' for i in (2,3,4)],
            [root/'artifacts/cinema-current-anchor-accept-v1/channel-frac.bin',None,None,None])

def direct(chain):
    words=np.empty(1<<22,np.uint32)
    f=chain.library.dll.jshc_cc_copy_direct
    f.argtypes=[ct.c_void_p,ct.POINTER(ct.c_uint32),ct.c_size_t];f.restype=ct.c_int
    if f(chain.handle,words.ctypes.data_as(ct.POINTER(ct.c_uint32)),words.size):raise AssertionError('直表导出失败')
    return words

def setup(args):
    # 在原生线程池建立前绑定同一L3的四个物理核。
    psutil.Process().cpu_affinity([0,2,4,6])
    if os.name=='nt':args.dll_directory=os.add_dll_directory('E:/mingw64/bin')
    libraries={n:Library(p,digest(p)) for n,p in [('baseline',args.baseline),('candidate',args.candidate)]}
    return libraries,models(args.data_root)

def verify(args):
    libs,(paths,sides)=setup(args)
    rows=[];mismatch=0;hashes={}
    with libs['baseline'].chain(paths,sides) as a,libs['candidate'].chain(paths,sides) as b:
        table_sha=None
        if not args.generic:
            wa,pa=tables(a);wb,pb=tables(b)
            assert np.array_equal(pa,pb)
            da,db=direct(a),direct(b)
            assert np.array_equal(da,db)
            table_sha=hashlib.sha256(db.tobytes()).hexdigest()
            del da,db,wa,wb
        state={'baseline':info(a),'candidate':info(b),'bytes':[a.model_bytes,b.model_bytes]}
        streams={n:hashlib.sha256() for n in ['oracle','candidate1','candidate4','outplace1','outplace4']}
        for begin in range(0,1<<24,1<<18):
            code=np.arange(begin,begin+(1<<18),dtype=np.uint32)
            source=np.stack([code>>16,(code>>8)&255,code&255],axis=1).astype(np.uint8)
            gold=a.apply(source.copy(),kernel='scalar',threads=1)
            streams['oracle'].update(gold.tobytes())
            for threads in (1,4):
                got=b.apply(source.copy(),kernel='avx2',threads=threads)
                mismatch+=int(np.count_nonzero(got!=gold))
                streams[f'candidate{threads}'].update(got.tobytes())
                raw=apply_to(libs['candidate'].dll,b.handle,source.tobytes(),1,threads)
                assert raw==gold.tobytes()
                streams[f'outplace{threads}'].update(raw)
        assert mismatch==0
        hashes={n:h.hexdigest() for n,h in streams.items()}
        assert len(set(hashes.values()))==1
        rng=np.random.default_rng(16685)
        lengths=[0,1,2,7,8,9,15,31,63,64,65,127,128,129,4095,4096,4097,65535,65536,65537,65793]
        count=0
        for length in lengths:
            source=rng.integers(0,256,(length,3),dtype=np.uint8)
            gold=a.apply(source.copy(),kernel='scalar',threads=1).tobytes()
            for offset in (0,1,7,15,31,63):
                for threads in (1,4):
                    for same in (False,True):
                        got=apply_to(libs['candidate'].dll,b.handle,source.tobytes(),1,threads,offset,63-offset,same)
                        assert got==gold;count+=1
        rows.append({'scope':'四级边界、哨兵、实际分离及同址','cases':count})
        rejects=reject_to(libs['candidate'].dll,b.handle)
    # 不启用派生表的首级回退必须继续正确。
    with libs['baseline'].chain(paths[:1],sides[:1]) as a,libs['candidate'].chain(paths[:1],sides[:1]) as b:
        assert info(b) is None or not info(b)['enabled']
        source=np.random.default_rng(85).integers(0,256,(65793,3),dtype=np.uint8)
        gold=a.apply(source.copy(),kernel='scalar',threads=1).tobytes()
        for threads in (1,4):
            assert b.apply(source.copy(),kernel='avx2',threads=threads).tobytes()==gold
            assert apply_to(libs['candidate'].dll,b.handle,source.tobytes(),1,threads)==gold
        fallback_bytes=[a.model_bytes,b.model_bytes]
    result={'passed':True,'purpose':'同模型整数运行时正确性，非拟合精度/性能',
            'libraries':{n:{'path':str(l.path),'sha256':l.sha256,'revision':l.revision} for n,l in libs.items()},
            'inputs':{str(p):digest(p) for p in paths+[sides[0]]},'table_sha256':table_sha,
            'full_colors':1<<24,'full_byte_mismatches':mismatch,'output_sha256':hashes,
            'state':state,'finite':rows,'negative_cases':rejects,'fallback_bytes':fallback_bytes,
            'environment':env(args.generic)}
    save(args.output/'correctness.json',result)
    print(json.dumps(result,ensure_ascii=False))

def env(generic=False):
    return {'platform':platform.platform(),'python':sys.version,'numpy':np.__version__,
            'processor':platform.processor(),'affinity':psutil.Process().cpu_affinity(),
            'cpu_count':psutil.cpu_count(),'compiler':'GCC 15.2.0 -O3 -DNDEBUG',
            'isa':'通用像素TU仅AVX2；无AVX512' if generic else '仅像素TU AVX2，复用80的三个TU另加BMI1；无AVX512','locked_frequency':False}

def bench_worker(args):
    libs,(paths,sides)=setup(args)
    manifest=json.loads((args.data_root/'assets/photos/manifest.json').read_text(encoding='utf-8'))
    source=np.empty((100,768,1024,3),np.uint8)
    for i,row in enumerate(manifest['images']):
        path=args.data_root/row['evaluation']['path']
        assert digest(path)==row['evaluation']['sha256']
        with Image.open(path) as image:source[i]=np.asarray(image)
    source_sha=hashlib.sha256(source.tobytes()).hexdigest()
    expected=json.loads((args.output/'correctness.json').read_text(encoding='utf-8'))
    records=[]
    order=('baseline','candidate') if args.worker in (0,3) else ('candidate','baseline')
    for name in order:
        lib=libs[name]
        assert lib.sha256==expected['libraries'][name]['sha256']
        started=time.perf_counter()
        chain=lib.chain(paths,sides)
        prepared=time.perf_counter()-started
        with chain:
            work=np.empty_like(source);pointer=ct.POINTER(ct.c_uint8)
            initial=bind_to(lib.dll);error=ct.create_string_buffer(1024)
            cold_start=time.perf_counter()
            assert not initial(chain.handle,source.ctypes.data_as(pointer),work.ctypes.data_as(pointer),source.nbytes,1,4,error,len(error)),error.value
            cold_outplace=time.perf_counter()-cold_start
            cold_sha=hashlib.sha256(work.tobytes()).hexdigest()
            f=lib.dll.jshc_cc_bench_to
            f.argtypes=[ct.c_void_p,pointer,pointer,ct.c_size_t,ct.c_int,ct.c_int,ct.c_size_t,ct.POINTER(ct.c_double),ct.POINTER(ct.c_char),ct.c_size_t]
            f.restype=ct.c_int
            for threads in ((1,4) if args.worker%2==0 else (4,1)):
                warm=chain.apply(source.copy(),kernel='avx2',threads=threads)
                output_sha=hashlib.sha256(warm.tobytes()).hexdigest();del warm
                assert output_sha==cold_sha
                samples=chain.bench(source,kernel='avx2',threads=threads,repeats=7)
                times=np.empty(7,np.float64);error=ct.create_string_buffer(1024)
                assert not f(chain.handle,source.ctypes.data_as(pointer),work.ctypes.data_as(pointer),source.nbytes,1,threads,7,
                    times.ctypes.data_as(ct.POINTER(ct.c_double)),error,len(error)),error.value
                assert hashlib.sha256(work.tobytes()).hexdigest()==output_sha
                # 同句柄两次完全相同的apply批次，显示测量随时间漂移。
                control=chain.bench(source,kernel='avx2',threads=threads,repeats=7)
                records.append({'variant':name,'threads':threads,'prepare_seconds':prepared,'model_bytes':chain.model_bytes,
                    'cold_first_outplace4_seconds':cold_outplace,
                    'palette':info(chain),'output_sha256':output_sha,'apply':samples['apply_seconds'],
                    'copy_apply':samples['copy_apply_seconds'],'outplace':times.tolist(),'control_apply':control['apply_seconds']})
                save(args.output/f'worker{args.worker}-partial.json',{'records':records,'source_sha256':source_sha})
    assert hashlib.sha256(source.tobytes()).hexdigest()==source_sha
    save(args.output/f'worker{args.worker}.json',{'records':records,'source_sha256':source_sha,'environment':env(args.generic)})

def bench(args):
    if args.worker is not None:return bench_worker(args)
    if (args.output/'performance.json').exists() or any(args.output.glob('worker*.json')):
        raise FileExistsError('保留已有性能证据，不覆盖或重跑')
    for index in range(4):
        cmd=[sys.executable,'-X','utf8',__file__,'--mode','bench','--data-root',str(args.data_root),
             '--baseline',str(args.baseline),'--candidate',str(args.candidate),'--output',str(args.output),'--worker',str(index)]
        if args.generic:cmd.append('--generic')
        subprocess.run(cmd,check=True)
        print('完成配对进程',index,flush=True)
    workers=[json.loads((args.output/f'worker{i}.json').read_text(encoding='utf-8')) for i in range(4)]
    assert len({w['source_sha256'] for w in workers})==1
    result=[]
    for threads in (1,4):
        pairs=[{r['variant']:r for r in w['records'] if r['threads']==threads} for w in workers]
        row={'threads':threads}
        for key in ('apply','copy_apply','outplace'):
            ratios=[statistics.median(p['candidate'][key])/statistics.median(p['baseline'][key]) for p in pairs]
            row[key]={'ratios':ratios,'median_ratio':statistics.median(ratios),
                      'median_ms_per_image':{n:statistics.median([statistics.median(p[n][key])*10 for p in pairs]) for n in ('baseline','candidate')}}
        row['prepare_ratios']=[p['candidate']['prepare_seconds']/p['baseline']['prepare_seconds'] for p in pairs]
        row['prepare_seconds']={n:[p[n]['prepare_seconds'] for p in pairs] for n in ('baseline','candidate')}
        row['prepared_first_outplace_ratios']=[(p['candidate']['prepare_seconds']+p['candidate']['outplace'][0])/
            (p['baseline']['prepare_seconds']+p['baseline']['outplace'][0]) for p in pairs]
        row['prepare_plus_cold_first_outplace4_ratios']=[(p['candidate']['prepare_seconds']+p['candidate']['cold_first_outplace4_seconds'])/
            (p['baseline']['prepare_seconds']+p['baseline']['cold_first_outplace4_seconds']) for p in pairs]
        row['same_handle_control']={n:[statistics.median(p[n]['control_apply'])/statistics.median(p[n]['apply']) for p in pairs] for n in ('baseline','candidate')}
        result.append(row)
    controls=[v for row in result for values in row['same_handle_control'].values() for v in values]
    control_valid=all(0.9<=v<=1.1 for v in controls)
    controls_valid=control_valid and all(0.95<=statistics.median(values)<=1.05 for row in result for values in row['same_handle_control'].values())
    photo_hashes={r['output_sha256'] for w in workers for r in w['records']}
    assert len(photo_hashes)==1
    generic_accepted=args.generic and controls_valid and all(row['outplace']['median_ratio']<=0.97 and max(row['outplace']['ratios'])<=1.05 for row in result)
    save(args.output/'performance.json',{'purpose':'同机描述性配对结果；没有锁频控温，不外推官方服务器',
        'sample_unit':'每进程每配置7次完整100图，中位后形成配对比，4进程AB/BA/BA/AB',
        'workers':4,'summary':result,'control_valid':controls_valid,'generic_outplace_accepted':generic_accepted,
        'photo_output_sha256':list(photo_hashes)[0],
        'worker_sha256':[digest(args.output/f'worker{i}.json') for i in range(4)]})
    print(json.dumps(result,ensure_ascii=False))

def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--mode',choices=('verify','bench'),required=True)
    p.add_argument('--data-root',type=Path,required=True)
    p.add_argument('--baseline',type=Path,required=True)
    p.add_argument('--candidate',type=Path,required=True)
    p.add_argument('--output',type=Path,required=True)
    p.add_argument('--worker',type=int)
    p.add_argument('--generic',action='store_true')
    args=p.parse_args();args.output.mkdir(parents=True,exist_ok=True)
    (verify if args.mode=='verify' else bench)(args)
if __name__=='__main__':main()
