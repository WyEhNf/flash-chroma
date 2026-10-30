"""固定首解的双DLL完整域/整幅4T/实际百图质量，不拟合或计时。"""
from __future__ import annotations
import argparse
import ast
import ctypes as ct
import hashlib
import json
import os
from pathlib import Path
import sys
from contextlib import ExitStack
import psutil
_ALLOWED=[0,2,4,6]
_process=psutil.Process();_prior_allowed=_process.cpu_affinity();_process.cpu_affinity(_ALLOWED)
if _process.cpu_affinity()!=_ALLOWED:raise ValueError('必须在加载NumPy/任何native前完成进程0x55前置')
ROOT=Path(__file__).resolve().parents[1];CACHE=Path('F:/Hackathon/projects/16-lut-color')
sys.path[:0]=[str(ROOT/'python'),str(ROOT/'experiments/channel-runtime')]
import numba
import numpy as np
import psutil
from PIL import Image
from lutlab import channel_coordinates as cc,channel_hotspot_support as hs,io,study_provenance
from channel_native import Library
from run_channel_tail_nodes import digest,load_model,save
from verify_channel_coordinates import integer_oracle
from qualify_cinema_max48 import TOTAL,SIZE,METRICS,TIERS,THRESHOLDS,histogram,metrics,compare,actual_to
from outplace_support import bind_to
from suffix_cache_support import cache_info
from domain_cache_support import info as domain_info
from direct16_support import info as direct_info
from palette_support import info as palette_info
from check_omp_affinity_control_v2 import Record
PLAN=ROOT/'experiments/p16-cinema-current-full-quality-v2.json'
FROZEN=ROOT/'artifacts/cinema-current-full-quality-frozen-v2.json'
OUT=ROOT/'artifacts/cinema-current-full-quality-v2'
HELPER=ROOT/'artifacts/p16-omp-affinity-control-build-v2/libp16_omp_affinity.dll'
HELPER_SHA='fbf717dd92e0f38e93394c88255ca9a36f9fab48ef30878b0200f9f4c4a0901f'
GOMP=Path('E:/mingw64/bin/libgomp-1.dll')
GOMP_SHA='fc7569276d33d23f55f143eb6723821ef2633c96cbb381c0f507b793d9585e88'
ENV={'OMP_NUM_THREADS':'4','OMP_DYNAMIC':'FALSE','OMP_THREAD_LIMIT':'4','OMP_WAIT_POLICY':'PASSIVE','OPENBLAS_NUM_THREADS':'1','MKL_NUM_THREADS':'1','NUMBA_NUM_THREADS':'4'}


def read(path):return json.loads(Path(path).read_text(encoding='utf-8'))


class RGB24Info(ct.Structure):
    _fields_=[(n,ct.c_uint32) for n in ('version','enabled','format','reason','palette_size','id_bytes','guard_bytes','whole_cache_colors')]
    _fields_ += [(n,ct.c_uint64) for n in ('input_entries','raw_words','table_capacity_bytes','palette_capacity_bytes','temporary_peak_bytes','guaranteed_alignment','data_mod_64')]
    _fields_ += [('prepare_seconds',ct.c_double)]


def rgb24_info(chain):
    f=chain.library.dll.p16_cc_get_direct_rgb24_info;f.argtypes=[ct.c_void_p,ct.POINTER(RGB24Info),ct.c_size_t];f.restype=ct.c_int
    v=RGB24Info()
    if ct.sizeof(v)!=96 or f(chain.handle,ct.byref(v),96) or v.version!=1:raise ValueError('新292诊断ABI不符')
    return {name:getattr(v,name) for name,_ in v._fields_}


def definitions(plan):
    prior=read(ROOT/'artifacts/cinema-max48-pareto-quality-v1/identity.json');roles={}
    for role,old_role in (('a399','a399'),('best','best'),('current741','candidate')):
        spec=prior['roles'][old_role]
        for name,expected in spec['input_sha256'].items():
            if digest(name)!=expected:raise ValueError('固定分母模型已变')
        oracle=Path(spec['oracle']) if role!='current741' else ROOT/'artifacts/cinema-max48-pareto-quality-v1/candidate.rgb'
        expected=spec.get('oracle_sha256') if role!='current741' else 'de4a98d5f3b3d430e349e83146d211296a4e6b3e2a9664a5806b321384a3c3f9'
        if digest(oracle)!=expected:raise ValueError('固定分母流已变')
        roles[role]={'models':spec['models'],'sidecars':spec['sidecars'],'oracle':str(oracle),'oracle_sha256':expected,'prior_role':old_role}
    folder=ROOT/plan['候选目录']
    if digest(folder/'model.npz')!=plan['候选NPZ']:raise ValueError('固定91d候选已变')
    roles['candidate']={'models':[str(folder/'candidate-base.slut'),str(folder/'stage2.slut'),prior['roles']['candidate']['models'][2],str(folder/'stage4.slut')],
        'sidecars':[str(folder/'channel-frac.bin'),None,None,None]}
    return roles


def freeze():
    if FROZEN.exists():raise ValueError('不覆盖完整双DLL质量冻结')
    plan=read(PLAN);roles=definitions(plan);raw=read(ROOT/'experiments/cinema-current-anchor-v1.json')
    paths={Path(p) for spec in roles.values() for p in [*spec['models'],*[v for v in spec['sidecars'] if v],*([spec['oracle']] if 'oracle' in spec else [])]}
    folder=ROOT/plan['候选目录'];paths.add(folder/'model.npz')
    prior=ROOT/'artifacts/cinema-max48-pareto-quality-v1'
    paths.update(prior/n for n in ('identity.json','results.json','histograms.npz'))
    paths.update(ROOT/'artifacts/cinema-current-feasible-cpsat-accept-v1'/n for n in ('summary.json','replay.npz'))
    paths.update(ROOT/'artifacts/cinema-max48-risk-upper-v1'/n for n in ('screen.npz','summary.json'))
    paths.update((ROOT/'report/data/p16-cinema-current-feasible-cpsat-20261024/manifest.json',HELPER,GOMP))
    paths.update((ROOT/'artifacts/cinema-current-full-quality-frozen-v1.json',ROOT/'artifacts/cinema-current-full-quality-execution-v1.log',ROOT/'artifacts/cinema-current-full-quality-mechanical-v2.json'))
    paths.update(CACHE/spec['path'] for spec in raw['tables'])
    manifest=CACHE/'assets/photos/manifest.json';paths.update((manifest,CACHE/'artifacts/full-photo-v1/photo-partition.json',CACHE/'artifacts/cinema-axis-calibration-v1/envelope-reference.npy'))
    for row in read(manifest)['images']:
        p=CACHE/row['evaluation']['path']
        if digest(p)!=row['evaluation']['sha256']:raise ValueError('固定照片已变')
        paths.add(p)
    for spec in plan['libraries'].values():
        if digest(spec['path'])!=spec['sha256']:raise ValueError('冻结库不符')
        paths.add(Path(spec['path']))
    built=read(ROOT/'artifacts/p16-direct-rgb24-build-frozen-v1/frozen.json')
    sources={Path(__file__).relative_to(ROOT).as_posix(),'scripts/audit_cinema_current_full_quality_v2.py','scripts/prepare_cinema_current_full_v2.py','scripts/qualify_cinema_current_full.py','scripts/audit_cinema_current_full_quality.py','experiments/p16-cinema-current-full-quality-v1.json','scripts/audit_cinema_max48_quality.py',PLAN.relative_to(ROOT).as_posix(),
        'experiments/cinema-current-anchor-v1.json','scripts/qualify_cinema_max48.py','scripts/run_channel_tail_nodes.py',
        'scripts/verify_channel_coordinates.py','experiments/channel-runtime/channel_native.py','scripts/outplace_support.py',
        'scripts/suffix_cache_support.py','scripts/domain_cache_support.py','scripts/direct16_support.py','scripts/palette_support.py',
        'scripts/exception_support.py','scripts/check_omp_affinity_control_v2.py'}
    sources.update(p.relative_to(ROOT).as_posix() for p in (ROOT/'python/lutlab').rglob('*.py'))
    for name,row in built['sources'].items():
        if digest(ROOT/name)!=row['sha256']:raise ValueError('292构建源已变')
        sources.add(name)
    for name in sources:
        if name.endswith('.py'):ast.parse((ROOT/name).read_text(encoding='utf-8-sig'),filename=name)
    if digest(HELPER)!=HELPER_SHA or digest(GOMP)!=GOMP_SHA:raise ValueError('只读4T观察器身份不同')
    record={'ast_pass':True,'source_sha256':{n:digest(ROOT/n) for n in sorted(sources)},'input_sha256':{str(p.resolve()):digest(p) for p in sorted(paths)},
        'roles':roles,'plan':plan,'required_environment':ENV,'environment':study_provenance.environment_fingerprint(),
        'scope':'固定91d独立完整双DLL/100图质量，原分母native不重跑，首次错误STOP，无性能或拟合。'}
    save(FROZEN,record);print({'frozen_sha256':digest(FROZEN),'sources':len(sources),'inputs':len(paths)},flush=True)


def validate():
    if OUT.exists():raise ValueError('不覆盖完整双DLL质量执行')
    frozen=read(FROZEN)
    for n,expected in frozen['source_sha256'].items():
        if digest(ROOT/n)!=expected:raise ValueError('冻结执行源已变：'+n)
    for n,expected in frozen['input_sha256'].items():
        if digest(n)!=expected:raise ValueError('冻结输入已变：'+n)
    for n,expected in ENV.items():
        if os.environ.get(n,'').upper()!=expected.upper():raise ValueError('导入前线程环境不符：'+n)
    numba.set_num_threads(4);plan=frozen['plan'];roles=frozen['roles'];prior_dir=ROOT/'artifacts/cinema-max48-pareto-quality-v1';old=read(prior_dir/'results.json')
    initial=read(ROOT/'artifacts/cinema-current-feasible-cpsat-accept-v1/summary.json');candidate_folder=ROOT/plan['候选目录'];first=load_model(candidate_folder/'model.npz')
    serialized=cc.from_sparse(io.load_sparse(roles['candidate']['models'][0],competition=True));frac=np.fromfile(roles['candidate']['sidecars'][0],dtype='<u4').reshape(3,3,256)
    for n,a,b in (('nodes',first.nodes,serialized.nodes),('idx',first.idx,serialized.idx),('channel_frac',first.channel_frac,frac)):
        np.testing.assert_array_equal(a,b,err_msg=n)
    np.testing.assert_array_equal(serialized.grid,first.grid.astype(np.float32).astype(np.float64))
    models=[first,*[cc.from_sparse(io.load_sparse(p,competition=True)) for p in roles['candidate']['models'][1:]]]
    raw_plan=read(ROOT/'experiments/cinema-current-anchor-v1.json');tables=[]
    for spec in raw_plan['tables']:
        path=CACHE/spec['path']
        if digest(path)!=spec['sha256']:raise ValueError('四原始LUT不符')
        tables.append(io.load_full(path,mmap=True).reshape(-1,3))
    gold=np.load(CACHE/'artifacts/cinema-axis-calibration-v1/envelope-reference.npy',mmap_mode='r')
    manifest=read(CACHE/'assets/photos/manifest.json');train_ids={r['id'] for r in read(CACHE/'artifacts/full-photo-v1/photo-partition.json')['training']['images']}
    if len(manifest['images'])!=100 or len(train_ids)!=60:raise ValueError('不是原100/60划分')
    with np.load(ROOT/'artifacts/cinema-max48-risk-upper-v1/screen.npz') as data:keys_support=data['keys'].copy();selected=data['selected_nodes'].copy()
    OUT.mkdir(parents=True);save(OUT/'identity.json',{'frozen_sha256':digest(FROZEN),'source_sha256':frozen['source_sha256'],'plan':plan,'roles':roles,'environment':study_provenance.environment_fingerprint()})
    save(OUT/'process-affinity.json',{'prior_allowed_cpus':_prior_allowed,'allowed_cpus':_process.cpu_affinity(),'set_before_numpy_and_native_import':True,'per_tid_pin':False,'performance_calls':0})
    cubes={r:np.memmap(spec['oracle'],np.uint8,'r',shape=(TOTAL,3)) for r,spec in roles.items() if r!='candidate'}
    cubes['candidate']=np.memmap(OUT/'candidate.rgb',np.uint8,'w+',shape=(TOTAL,3))
    hists={r:np.zeros(SIZE,np.int64) for r in roles};standalone=np.zeros(SIZE,np.int64);truth_hash=hashlib.sha256();oracle_hash=hashlib.sha256()
    configs=[(k,t,p) for k,t in (('scalar',1),('avx2',1),('avx2',4)) for p in ('inplace','to12')]
    streams={lib:{str(c):hashlib.sha256() for c in configs} for lib in plan['libraries']};photo_hashes={lib+'_'+p:hashlib.sha256() for lib in plan['libraries'] for p in ('inplace','to12')}
    photo_hist=np.zeros(SIZE,np.int64);train_hist=photo_hist.copy();photo_rows=[];photo_matrix=[];runtime={};whole=[];snapshots=[];witness=None
    with ExitStack() as stack:
        stack.enter_context(os.add_dll_directory('E:/mingw64/bin'));stack.enter_context(os.add_dll_directory(str(HELPER.parent)))
        for spec in plan['libraries'].values():stack.enter_context(os.add_dll_directory(str(Path(spec['path']).parent)))
        chains={};to_funcs={}
        for lib,spec in plan['libraries'].items():
            library=Library(spec['path'],spec['sha256']);chain=stack.enter_context(library.chain(roles['candidate']['models'],roles['candidate']['sidecars']));chains[lib]=chain;to_funcs[lib]=bind_to(library.dll)
            runtime[lib]={'capacity_bytes':chain.model_bytes,'cache':cache_info(chain),'domain':domain_info(chain),'palette':palette_info(chain),'direct':direct_info(chain),'rgb24':rgb24_info(chain) if lib=='292' else None}
        for start in range(0,TOTAL,65536):
            keys=np.arange(start,start+65536,dtype=np.uint32);rgb=hs.rgb(keys);oracle=rgb.copy();predict=rgb.copy()
            for level,model in enumerate(models):
                oracle=integer_oracle(model,oracle);predict=cc.predict(model,predict);np.testing.assert_array_equal(oracle,predict)
                if level==0:first_oracle=oracle
            np.testing.assert_array_equal(oracle,predict);truth=tables[0][keys]
            for table in tables[1:]:truth=table[hs.key(truth)]
            np.testing.assert_array_equal(truth,gold[start:start+65536]);truth_hash.update(truth.tobytes())
            cubes['candidate'][start:start+65536]=oracle;oracle_hash.update(oracle.tobytes());standalone+=histogram(first_oracle,tables[0][keys])
            for role in roles:hists[role]+=histogram(oracle if role=='candidate' else cubes[role][start:start+65536],truth)
            for lib,chain in chains.items():
                for config in configs:
                    kernel,threads,path=config;actual=chain.apply(rgb.copy(),kernel=kernel,threads=threads) if path=='inplace' else actual_to(to_funcs[lib],chain,rgb,kernel,threads)
                    np.testing.assert_array_equal(actual,oracle);streams[lib][str(config)].update(actual.tobytes())
            if witness is None:
                delta=cubes['current741'][start:start+65536].astype(np.int32)-truth.astype(np.int32);sq=np.sum(delta*delta,axis=1,dtype=np.int32)
                candidates=keys[(sq==41)&~np.isin(keys,keys_support)]
                if len(candidates):
                    source=int(candidates[0]);point=hs.rgb(np.array([source],np.uint32));i,w=hs.corners(first,point)
                    if np.any(w[np.isin(i,selected)]):raise AssertionError('外支撑见证触及选中节点')
                    before=cubes['current741'][source].tolist();after=oracle[source-start].tolist()
                    if before!=after:raise AssertionError('外支撑见证实际模型已变')
                    witness={'source_key':source,'source_rgb':point[0].tolist(),'gold_rgb':truth[source-start].tolist(),'output_rgb':after,'squared_error':41,'selected_positive_weight_sum':0,'scope':'仅固定当前122节点集合的max下界，非全首级全局最优。'}
        cubes['candidate'].flush()
        if any(h.hexdigest()!=oracle_hash.hexdigest() for group in streams.values() for h in group.values()):raise AssertionError('全域checkpoint SHA不一致')
        save(OUT/'full-checkpoint.json',{'candidate_oracle_sha256':oracle_hash.hexdigest(),'reference_payload_sha256':truth_hash.hexdigest(),'native_full_stream_sha256':{lib:{k:h.hexdigest() for k,h in values.items()} for lib,values in streams.items()},'cube':{r:metrics(h) for r,h in hists.items()},'full_native_configs':12,'mismatches':0,'scope':'完整分块流已完成；此时whole4T与照片尚未执行，不将请求4线程冒称实际4工作线程。'})
        helper=ct.CDLL(str(HELPER));fn=helper.p16_omp_affinity;fn.argtypes=[ct.POINTER(Record),ct.c_size_t,ct.c_size_t,ct.c_uint32,ct.POINTER(Record)];fn.restype=ct.c_int
        if ct.sizeof(Record)!=72:raise ValueError('只读线程观察器结构尺寸不符')
        def snapshot():
            records=(Record*4)();code=fn(records,4,72,0,None)
            save(OUT/('team-attempt-%02d.json'%(len(snapshots)+1)),{'return_code':code,'action':0,'records':[{n:getattr(v,n) for n,_ in Record._fields_} for v in records]})
            if code or any(v.version!=1 or v.team_size!=4 or v.omp_tid!=i or v.set_attempted for i,v in enumerate(records)):raise ValueError('只读4T观察失败')
            tids=[v.os_tid for v in records]
            if len(set(tids))!=4:raise AssertionError('没有4个独立OS工作线程')
            snapshots.append({'action':0,'records':[{n:getattr(v,n) for n,_ in Record._fields_} for v in records]});return tids
        full_rgb=np.empty((TOTAL,3),np.uint8)
        for start in range(0,TOTAL,262144):full_rgb[start:start+262144]=hs.rgb(np.arange(start,start+262144,dtype=np.uint32))
        for lib,chain in chains.items():
            for path in ('inplace','to12'):
                before=snapshot();actual=chain.apply(full_rgb.copy(),kernel='avx2',threads=4) if path=='inplace' else actual_to(to_funcs[lib],chain,full_rgb,'avx2',4)
                after=snapshot()
                if before!=after:raise AssertionError('同runtime4T pool发生变化')
                np.testing.assert_array_equal(actual,cubes['candidate']);actual_hash=hashlib.sha256(actual).hexdigest()
                if actual_hash!=oracle_hash.hexdigest():raise AssertionError('整幅4T完整流不同')
                whole.append({'library':lib,'path':path,'pixels':TOTAL,'blocks':256,'sha256':actual_hash,'surrounding_team_os_tids':before,'mismatches':0});del actual
        del full_rgb
        for row in manifest['images']:
            path=CACHE/row['evaluation']['path']
            if digest(path)!=row['evaluation']['sha256']:raise ValueError('照片原件已变')
            with Image.open(path) as image:rgb=np.asarray(image).reshape(-1,3).copy()
            keys=hs.key(rgb);expected=cubes['candidate'][keys]
            for lib,chain in chains.items():
                for route in ('inplace','to12'):
                    actual=chain.apply(rgb.copy(),kernel='avx2',threads=4) if route=='inplace' else actual_to(to_funcs[lib],chain,rgb,'avx2',4)
                    np.testing.assert_array_equal(actual,expected);photo_hashes[lib+'_'+route].update(actual.tobytes())
                    photo_matrix.append({'image':row['id'],'library':lib,'path':route,'sha256':hashlib.sha256(actual).hexdigest(),'mismatches':0})
            h=histogram(expected,gold[keys]);photo_hist+=h
            if row['id'] in train_ids:train_hist+=h
            photo_rows.append({'image':row['id'],**metrics(h),'prediction_sha256':hashlib.sha256(expected).hexdigest()})
        gomp_paths={str(Path(v.path).resolve()) for v in psutil.Process().memory_maps() if Path(v.path).name.lower()=='libgomp-1.dll'}
        if len(gomp_paths)!=1 or next(iter(gomp_paths)).lower()!=str(GOMP.resolve()).lower():raise ValueError('不是同一已冻结libgomp')
    if witness is None:raise AssertionError('未找到固定外域41见证')
    cube_metrics={r:metrics(h) for r,h in hists.items()};photos={r:old['photos'][spec['prior_role']] for r,spec in roles.items() if r!='candidate'}
    photos['candidate']={**metrics(photo_hist),'per_image':photo_rows};training={r:old['training60'][spec['prior_role']] for r,spec in roles.items() if r!='candidate'};training['candidate']=metrics(train_hist)
    first_metrics={r:old['standalone_first_vs_original_table1'][spec['prior_role']] for r,spec in roles.items() if r!='candidate'};first_metrics['candidate']=metrics(standalone)
    for role in ('a399','best','current741'):
        for n,v in old['cube'][roles[role]['prior_role']].items():
            if abs(cube_metrics[role][n]-v)>1e-12:raise AssertionError('固定分母完整直方图改变')
    for actual,before in ((cube_metrics['candidate'],initial['after_uniform']),(training['candidate'],initial['after_training'])):
        for n,v in before.items():
            if abs(actual[n]-v)>1e-12:raise AssertionError('完整独立质量不等于初门重放：'+n)
    if photos['candidate']['n']!=78643200 or training['candidate']['n']!=47185920:raise AssertionError('实际100/60图像素数错误')
    pairs={}
    for role in ('a399','best','current741'):
        rows=[{'image':b['image'],**compare(a,b)} for a,b in zip(photos[role]['per_image'],photo_rows)]
        if any(a['image']!=b['image'] for a,b in zip(photos[role]['per_image'],photo_rows)):raise AssertionError('逐图配对身份不同')
        pairs[role]={'cube':compare(cube_metrics[role],cube_metrics['candidate']),'photos':compare(photos[role],photos['candidate']),
            'training60':compare(training[role],training['candidate']),'per_image':rows,'per_metric_changes':{n:{label:sum(r['metrics'][n]['change']==label for r in rows) for label in ('好','平','差')} for n in METRICS},
            'worst_image_retained_percent':min(r['minimum_retained_percent'] for r in rows)}
    expected_sha=oracle_hash.hexdigest()
    if any(h.hexdigest()!=expected_sha for group in streams.values() for h in group.values()) or len({h.hexdigest() for h in photo_hashes.values()})!=1:raise AssertionError('完整流或百图汇总SHA不同')
    with np.load(prior_dir/'histograms.npz') as old_h:baseline_first={r:old_h['standalone_first_'+spec['prior_role']].copy() for r,spec in roles.items() if r!='candidate'}
    np.savez_compressed(OUT/'histograms.npz',**{'cube_'+r:h for r,h in hists.items()},photos_candidate=photo_hist,training60_candidate=train_hist,
        standalone_first_candidate=standalone,**{'standalone_first_'+r:h for r,h in baseline_first.items()})
    result={'cube':cube_metrics,'photos':photos,'training60':training,'standalone_first_vs_original_table1':first_metrics,'pairs':pairs,
        'nonofficial_strict_max_T_counts':{r:{str(t):sum(v['max']<t for v in data['per_image']) for t in THRESHOLDS} for r,data in photos.items()},
        'runtime':runtime,'candidate_oracle_sha256':expected_sha,'reference_payload_sha256':truth_hash.hexdigest(),
        'native_full_stream_sha256':{lib:{k:h.hexdigest() for k,h in v.items()} for lib,v in streams.items()},'whole4t':whole,'read_only_team_snapshots':snapshots,
        'native_100photos_sha256':{k:h.hexdigest() for k,h in photo_hashes.items()},'photo_matrix':photo_matrix,'outside41_witness':witness,
        'full_native_configs':12,'whole4t_streams':4,'actual_photo_configs':400,'mismatches':0,'unique_libgomp':list(gomp_paths),
        'mean_p99_max_against_best_aggregates':all(group['candidate'][n]<=group['best'][n]+1e-12 for group in (cube_metrics,photos,training) for n in ('mean','p99','max')),
        'native_inner_tid_instrumentation':False,'overall_upgrade':False,
        'scope':'完整双DLL数学/原生/实际百图与三分母资格，旧分母消费认证结果不重跑native；完整4T前后同pool非内部逐块TID插桩；速度50未验。'}
    save(OUT/'results.json',result)
    print({'candidate_cube':cube_metrics['candidate'],'candidate_photos':photos['candidate']['mean'],'configs':12,'whole4t':4,'photos':400,'mismatches':0},flush=True)


if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--freeze',action='store_true');args=p.parse_args()
    if args.freeze:freeze()
    else:validate()
