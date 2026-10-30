"""固定模型四级恢复算法对照；由已执行脚本按阶段拆分。"""
import os
for k in ['OMP_NUM_THREADS','MKL_NUM_THREADS','OPENBLAS_NUM_THREADS']: os.environ[k]='1'
import sys,json,time,hashlib,statistics
from pathlib import Path
ROOT=Path(__file__).resolve().parents[4]
sys.path.insert(0,str(ROOT/'tmp/stage-a-pr42/python'))
import numpy as np
import numba
from numba import njit,prange
from PIL import Image
from lutlab import io,interp,study_kernels
from lutlab.compatibility import model_args
from lutlab.study_chains import compare_images,map_chain
from lutlab.study_provenance import environment_fingerprint
OUT=Path(__file__).resolve().parents[1]; DATA=OUT/'data'; OLD=ROOT/'artifacts/local-lut-study/20261016'
DATA.mkdir(exist_ok=True)
if (DATA/'chains.json').exists():raise RuntimeError('已有完成结果，拒绝覆盖；请使用新输出目录')
def sha(p):
    with Path(p).open('rb') as f:return hashlib.file_digest(f,'sha256').hexdigest()
def dump(p,d):p.write_text(json.dumps(d,ensure_ascii=False,indent=2),encoding='utf8')
@njit(cache=True,parallel=True)
def mixed(rgb,nodes,indices,fractions,m,kinds):
    out=np.empty_like(rgb)
    for i in prange(len(rgb)):
        r,g,b=int(rgb[i,0]),int(rgb[i,1]),int(rgb[i,2])
        for stage in range(4):
            v=study_kernels.pixel(nodes[stage],indices[stage],fractions[stage],m,r,g,b,kinds[stage])
            r=min(255,max(0,int(np.floor(v[0]+.5))))
            g=min(255,max(0,int(np.floor(v[1]+.5))))
            b=min(255,max(0,int(np.floor(v[2]+.5))))
        out[i,0],out[i,1],out[i,2]=r,g,b
    return out
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
def summary(a,b):
    s=compare_images(a.reshape(images.shape),b.reshape(images.shape))
    return dict(mean=float(s[:,0].mean()),rms=float(np.sqrt(np.mean(s[:,1]**2))),worst_image_p99=float(s[:,2].max()),max=float(s[:,3].max()),per_image=[dict(image=im['id'],**{k:float(s[i,j]) for j,k in enumerate(['mean','rms','p99','max'])}) for i,im in enumerate(image_rows)])
numba.set_num_threads(4)
reports=[json.loads(p.read_text(encoding='utf8')) for p in sorted((OLD/'luts').glob('*/result.json'))]
byid={r['lut']['sha256'][:12]:r for r in reports}
image_rows=json.loads((ROOT/'assets/photos/manifest.json').read_text(encoding='utf8'))['images']
frames=[];inputs={}
for r in image_rows:
    p=ROOT/r['evaluation']['path'];assert sha(p)==r['evaluation']['sha256'];inputs[str(p.relative_to(ROOT))]=sha(p)
    with Image.open(p) as im:frames.append(np.asarray(im).reshape(-1,3))
images=np.stack(frames);flat=images.reshape(-1,3);del frames
creative=sorted([r for r in reports if r['lut']['source_id']=='stripedpurple'],key=lambda r:r['lut']['path'])
profiles=['ls_tri_tri','ls_tetra_int','dp_supported','dp_jitter','curvature_int','jitter_tetra']
plan=[]
for ri,start in enumerate([0,11,30],1):
    recipe=creative[start:start+4]
    for m in [17,33]:
        chosen=[min([x for x in r['screen'] if x['m']==m and x['profile'] in profiles and x['status']=='ok'],key=lambda x:(x['quality']['mean'],x['profile'])) for r in recipe]
        plan.append(dict(recipe=ri,m=m,luts=[r['lut'] for r in recipe],models=chosen))
dump(DATA/'plan.json',dict(selection='沿用旧研究三条四级链；各级从六种拟合方法按既有4096像素/图筛选均值选最优，固定模型比较恢复器；不是盲测',profiles=profiles,cases=plan,reps=5,threads=4,modes=['uniform_tetra','uniform_tri','matched'],timing='100张图片批次；含输出分配和四级逐像素恢复，排除读图、拟合、参考生成、误差统计、JIT'))
results=[]
rng=np.random.default_rng(20261021)
probe=np.concatenate([flat[::max(1,len(flat)//32768)],rng.integers(0,256,(65536,3),dtype=np.uint8)])
for case in plan:
    m=case['m'];models=[]
    for rec in case['models']:
        p=OLD/rec['model'];assert sha(p)==rec['model_sha256'];inputs[str(p.relative_to(ROOT))]=sha(p);models.append(io.load_sparse(p))
    args=[model_args(x) for x in models];nodes=np.stack([a[0] for a in args]);idx=np.stack([a[1] for a in args]);frac=np.stack([a[2] for a in args])
    matched=np.array([int(r['profile']=='ls_tri_tri') for r in case['models']],np.int64)
    configs=[('uniform_tetra',np.zeros(4,np.int64)),('uniform_tri',np.ones(4,np.int64)),('matched',matched)]
    truth=flat.copy()
    for lut in case['luts']:
        p=OLD/'references'/f"{lut['sha256'][:12]}.npy";inputs[str(p.relative_to(ROOT))]=sha(p);ref=np.load(p,mmap_mode='r');truth=ref[truth[:,0],truth[:,1],truth[:,2]]
    outputs={};times={name:[] for name,k in configs};optimized={name:[] for name,k in configs[:2]}
    for name,kinds in configs:
        p=mixed(probe,nodes,idx,frac,m,kinds);expected=oracle(probe,models,kinds)
        assert np.array_equal(p,expected),(case['recipe'],m,name,int(np.count_nonzero(p!=expected)))
        if name!='matched':assert np.array_equal(p,map_chain(probe,nodes,idx,frac,m,int(kinds[0])))
        outputs[name]=mixed(flat,nodes,idx,frac,m,kinds)
    # 五轮轮换顺序，基线专用统一kind入口也单独计时以量化动态派发代价。
    jobs=[(name,k,False) for name,k in configs]+[(name,k,True) for name,k in configs[:2]]
    for rep in range(5):
        for j in range(5):
            name,k,special=jobs[(j+rep)%5];t=time.perf_counter()
            out=map_chain(flat,nodes,idx,frac,m,int(k[0])) if special else mixed(flat,nodes,idx,frac,m,k)
            elapsed=(time.perf_counter()-t)*1000
            assert np.array_equal(out,outputs[name])
            (optimized if special else times)[name].append(elapsed)
    row=dict(recipe=case['recipe'],m=m,luts=[x['path'] for x in case['luts']],profiles=[r['profile'] for r in case['models']],matched_kinds=matched.tolist(),oracle_probe_pixels=len(probe),modes={})
    for name,k in configs:
        row['modes'][name]=dict(**summary(outputs[name],truth),batch_ms=times[name],ms_per_image=statistics.median(times[name])/len(images),min_ms_per_image=min(times[name])/len(images),max_ms_per_image=max(times[name])/len(images),output_sha256=hashlib.sha256(outputs[name]).hexdigest())
        if name in optimized:row['modes'][name]['uniform_entry_batch_ms']=optimized[name];row['modes'][name]['uniform_entry_ms_per_image']=statistics.median(optimized[name])/len(images)
    results.append(row);dump(DATA/'chains.json',results)
    print('四级链完成',case['recipe'],m,{name:(v['mean'],v['ms_per_image']) for name,v in row['modes'].items()},flush=True)
    del outputs,truth,out
dump(DATA/'experiment-run.json',dict(environment=environment_fingerprint(),threads=numba.get_num_threads(),threading_layer=numba.threading_layer(),script_sha256=sha(__file__),inputs=inputs,plan_sha256=sha(DATA/'plan.json'),source_commit='59586f7bd6dd248cf0b68bcbdff8e41cf95ac572',scope='Numba CPU float64 Q16权重恢复；四面体探针对照整数参考，三线性探针对照独立NumPy实现；非C++原生内核性能'))
