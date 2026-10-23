"""按冻结计划验证专门化输出，并在独立进程执行一次配对计时。"""
import os
for key in ['OMP_NUM_THREADS','MKL_NUM_THREADS','OPENBLAS_NUM_THREADS']:os.environ[key]='1'
import sys,json,argparse,hashlib,time,statistics,subprocess
from pathlib import Path
OUT=Path(__file__).resolve().parents[1]
PLAN=json.loads((OUT/'plan.json').read_text(encoding='utf8'))
ROOT=Path(PLAN['input_root']);OLD=ROOT/'artifacts/local-lut-study/20261016'
PREVIOUS=ROOT/'artifacts/lut-applicability-chain/20261021'
sys.path.insert(0,str(ROOT/'tmp/stage-a-pr42/python'))
import numpy as np
import numba,psutil
from PIL import Image
from lutlab import io,interp
from lutlab.compatibility import model_args
from lutlab.study_provenance import environment_fingerprint
import kernels

def digest(path):
    with Path(path).open('rb') as f:return hashlib.file_digest(f,'sha256').hexdigest()

def array_sha(array):return hashlib.sha256(array).hexdigest()

def save(path,value):path.write_text(json.dumps(value,ensure_ascii=False,indent=2),encoding='utf8')

def oracle(rgb,models,kinds):
    x=rgb.copy()
    for model,k in zip(models,kinds):
        if k==0:x=interp.apply_tetra_q16(model,x)
        else:
            ix,w=interp.tri_weights(x,*model.tables(),model.m)
            v=np.zeros((len(x),3),np.float64)
            for j in range(8):v+=w[:,j,None]*model.nodes.reshape(-1,3)[ix[:,j]]
            x=np.clip(np.floor(v+.5),0,255).astype(np.uint8)
    return x

def load_case(case):
    models=[]
    for r in case['models']:
        p=OLD/r['model'];assert digest(p)==r['model_sha256'];models.append(io.load_sparse(p))
    args=[model_args(m) for m in models]
    params=tuple(np.stack([a[i] for a in args]) for i in range(3))+(case['m'],)
    kinds=np.array([int(r['profile']=='ls_tri_tri') for r in case['models']],np.int64)
    function=getattr(kernels,'fixed_'+''.join(map(str,kinds)))
    old=next(x for x in previous if x['recipe']==case['recipe'] and x['m']==case['m'])
    return models,params,kinds,function,old['modes']['matched']['output_sha256']

def warm(params,kinds,function):
    times={}
    for label,fn in [('baseline',lambda: kernels.mixed(images[:64],*params,kinds)),('candidate',lambda: function(images[:64],*params)),('intermediate',lambda: getattr(kernels,'dispatch_'+''.join(map(str,kinds)))(images[:64],*params))]:
        t=time.perf_counter();fn();times[label]=time.perf_counter()-t
    return times

def measure(params,kinds,function,expected,label):
    target=kernels.mixed if label=='baseline' else (function if label=='candidate' else getattr(kernels,'dispatch_'+''.join(map(str,kinds))))
    arguments=(images,*params,kinds) if label=='baseline' else (images,*params)
    t=time.perf_counter()
    output=target(*arguments)
    elapsed=time.perf_counter()-t
    observed=array_sha(output);assert observed==expected
    return dict(seconds=elapsed,ms_per_image=elapsed*1000/len(image_rows),output_sha256=observed)

parser=argparse.ArgumentParser(description=__doc__)
parser.add_argument('mode',choices=['verify','bench']);parser.add_argument('--worker',type=int,choices=[0,1])
args=parser.parse_args()
if args.mode=='bench' and args.worker is None:parser.error('计时需要固定worker编号')
destination=OUT/('verification.json' if args.mode=='verify' else f'worker-{args.worker}.json')
if destination.exists():raise RuntimeError('拒绝覆盖已有结果；保留失败记录，不自动重测')
lock=json.loads((OUT/'run-lock.json').read_text(encoding='utf8'))
for path,expected in lock['files'].items():assert digest(OUT/path)==expected,path
source_run=json.loads((PREVIOUS/'data/survey-run.json').read_text(encoding='utf8'))
source_hashes={k:v for k,v in source_run['hashes'].items() if k.startswith('tmp/stage-a-pr42/python/')}
for path,expected in source_hashes.items():assert digest(ROOT/path)==expected,path
numba.set_num_threads(PLAN['threads'])
previous=json.loads((PREVIOUS/'data/chains.json').read_text(encoding='utf8'))
image_rows=json.loads((ROOT/'assets/photos/manifest.json').read_text(encoding='utf8'))['images']
frames=[];image_hashes={}
for r in image_rows:
    p=ROOT/r['evaluation']['path'];assert digest(p)==r['evaluation']['sha256'];image_hashes[r['evaluation']['path']]=digest(p)
    with Image.open(p) as image:frames.append(np.asarray(image).reshape(-1,3))
assert len(frames)==100
images=np.concatenate(frames);del frames
input_sha=array_sha(images)
result=dict(complete=False,mode=args.mode,worker=args.worker,environment=environment_fingerprint(),
            affinity=psutil.Process().cpu_affinity(),threads=numba.get_num_threads(),
            source_commit=PLAN['source_commit'],source_hashes=source_hashes,image_hashes=image_hashes,
            input_sha256=input_sha,plan_sha256=digest(OUT/'plan.json'),script_sha256=digest(__file__),cases=[])
save(destination,result)

if args.mode=='verify':
    import ast
    old_tree=ast.parse((PREVIOUS/'code/experiment.py').read_text(encoding='utf8'))
    new_tree=ast.parse((OUT/'code/kernels.py').read_text(encoding='utf8'))
    old_fn=next(x for x in old_tree.body if isinstance(x,ast.FunctionDef) and x.name=='mixed')
    new_fn=next(x for x in new_tree.body if isinstance(x,ast.FunctionDef) and x.name=='mixed')
    assert ast.dump(old_fn)==ast.dump(new_fn)
    result['baseline_ast_identical']=True
    rng=np.random.default_rng(20261021)
    probe=np.concatenate([images[::len(images)//32768],rng.integers(0,256,(65536,3),dtype=np.uint8)])
    for case in PLAN['cases']:
        models,params,kinds,function,expected=load_case(case)
        warming=warm(params,kinds,function)
        reference=oracle(probe,models,kinds)
        assert np.array_equal(kernels.mixed(probe,*params,kinds),reference)
        assert np.array_equal(function(probe,*params),reference)
        intermediate=getattr(kernels,'dispatch_'+''.join(map(str,kinds)))
        assert np.array_equal(intermediate(probe,*params),reference)
        for n in [0,1,7,8,15,16,31,32,63,64,65,257]:
            assert np.array_equal(function(probe[:n],*params),reference[:n])
        baseline_sha=hashlib.sha256();candidate_sha=hashlib.sha256()
        for start in range(0,256**3,262144):
            q=np.arange(start,start+262144,dtype=np.int32);rgb=np.empty((len(q),3),np.uint8)
            rgb[:,0]=q>>16;rgb[:,1]=(q>>8)&255;rgb[:,2]=q&255
            a=kernels.mixed(rgb,*params,kinds);b=function(rgb,*params)
            assert np.array_equal(a,b),(case['recipe'],case['m'],start)
            assert np.array_equal(a,intermediate(rgb,*params)),(case['recipe'],case['m'],start,'intermediate')
            baseline_sha.update(a);candidate_sha.update(b)
        for label in ['baseline','candidate','intermediate']:measure(params,kinds,function,expected,label)
        entry=dict(recipe=case['recipe'],m=case['m'],kinds=kinds.tolist(),full_cube_pixels=256**3,
                   probe_pixels=len(probe),baseline_cube_sha256=baseline_sha.hexdigest(),candidate_cube_sha256=candidate_sha.hexdigest(),
                   full_cube_mismatches=0,photos_output_sha256=expected,warm_first_call_seconds=warming,
                   runtime_array_bytes=sum(p.nbytes for p in params[:3]),serialized_node_bytes=sum(m.nodes.nbytes for m in models))
        result['cases'].append(entry);save(destination,result)
        print('验证通过',case['recipe'],case['m'],'完整色域＋独立探针＋完整百图',flush=True)
else:
    validation=json.loads((OUT/'verification.json').read_text(encoding='utf8'));assert validation['complete']
    assert validation['plan_sha256']==result['plan_sha256'] and validation['input_sha256']==input_sha
    control=next(c for c in PLAN['cases'] if c['recipe']==PLAN['control_case']['recipe'] and c['m']==PLAN['control_case']['m'])
    models,params,kinds,function,expected=load_case(control);warm(params,kinds,function)
    controls=[]
    for pair in range(PLAN['control_case']['pairs_per_worker']):
        order=['A','B'] if (pair+args.worker)%2==0 else ['B','A'];values={}
        for label in order:values[label]=measure(params,kinds,function,expected,'baseline')
        controls.append(dict(pair=pair,order=order,values=values,ratio=values['B']['seconds']/values['A']['seconds']))
    control_ratios=[x['ratio'] for x in controls]
    med=statistics.median(control_ratios)
    result['control']=dict(recipe=control['recipe'],m=control['m'],pairs=controls,median_ratio=med,
        valid=PLAN['gate']['control_median_ratio'][0]<=med<=PLAN['gate']['control_median_ratio'][1] and all(PLAN['gate']['control_each_ratio'][0]<=x<=PLAN['gate']['control_each_ratio'][1] for x in control_ratios))
    save(destination,result);print('同内核控制',args.worker,result['control']['valid'],med,flush=True)
    cases=PLAN['cases'] if args.worker==0 else list(reversed(PLAN['cases']))
    for case in cases:
        models,params,kinds,function,expected=load_case(case);warming=warm(params,kinds,function);pairs=[]
        # 完整批次预热不计时，基线与候选均验证输出。
        for label in ['baseline','candidate','intermediate']:measure(params,kinds,function,expected,label)
        for pair in range(PLAN['pairs_per_case_per_worker']):
            roles=['baseline','intermediate','candidate']; shift=(pair+args.worker)%3;order=roles[shift:]+roles[:shift];values={}
            for label in order:values[label]=measure(params,kinds,function,expected,label)
            pairs.append(dict(pair=pair,order=order,values=values,ratio=values['candidate']['seconds']/values['baseline']['seconds'],intermediate_ratio=values['candidate']['seconds']/values['intermediate']['seconds']))
        entry=dict(recipe=case['recipe'],m=case['m'],kinds=kinds.tolist(),pairs=pairs,
            median_ratio=statistics.median(p['ratio'] for p in pairs),warm_first_call_seconds=warming)
        result['cases'].append(entry);save(destination,result)
        print('计时完成',args.worker,case['recipe'],case['m'],'候选/基线',entry['median_ratio'],flush=True)
assert array_sha(images)==input_sha
result.update(complete=True,threading_layer=numba.threading_layer(),inputs_unchanged=True)
save(destination,result)
