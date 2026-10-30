"""阶段A完整色域与代表图片验证；由已执行脚本按阶段拆分。"""
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
if (DATA/'validation.json').exists():raise RuntimeError('已有完成结果，拒绝覆盖；请使用新输出目录')
def sha(p):
    with Path(p).open('rb') as f:return hashlib.file_digest(f,'sha256').hexdigest()
def dump(p,d):p.write_text(json.dumps(d,ensure_ascii=False,indent=2),encoding='utf8')
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
survey=json.loads((DATA/'survey.json').read_text(encoding='utf8'))
# 对13个可分离源的26份模型做实际完整RGB8恢复，独立于解析曲线证明。
validation=[]
for row in survey:
    if not row['separable']:continue
    report=byid[row['id']]; rec=next(x for x in report['screen'] if x['m']==row['m'] and x['profile']=='dp_supported')
    ref=np.load(OLD/'references'/f"{row['id']}.npy",mmap_mode='r').reshape(-1,3)
    p=DATA/'models'/f"{row['id']}-calibrated-m{row['m']}.slut"
    model=io.load_sparse(p if p.exists() else OLD/rec['model'])
    cube=study_kernels.expand_cube(*model_args(model),0)
    h=np.zeros(195076,np.int64);mismatch=0
    for start in range(0,len(cube),262144):
        d=cube[start:start+262144].astype(np.int32)-ref[start:start+262144].astype(np.int32)
        d2=np.sum(d*d,axis=1);h+=np.bincount(d2,minlength=len(h));mismatch+=int(np.count_nonzero(d2))
    mean=float(h@np.sqrt(np.arange(len(h)))/len(cube))
    assert abs(mean-row['after_cube_mean'])<1e-10
    if row['route']=='exact_monotone_calibrated':assert mismatch==0
    entry=dict(id=row['id'],lut=row['lut'],m=row['m'],route=row['route'],cube_mean=mean,cube_mismatch=mismatch,model_sha256=sha(p if p.exists() else OLD/rec['model']))
    # 代表成功、两档皆失败、单档失败三类，完整100张照片。
    if any(name in row['lut'] for name in ['06 High','Emerald Malaise','Amber Haze','05 Medium High']):
        lookup=flat[:,0].astype(np.int32)*65536+flat[:,1].astype(np.int32)*256+flat[:,2]
        truth=ref[lookup];entry['after_photos']=summary(cube[lookup],truth)
        base=study_kernels.expand_cube(*model_args(io.load_sparse(OLD/rec['model'])),0)
        entry['before_photos']=summary(base[lookup],truth);del base,truth,lookup
    validation.append(entry);dump(DATA/'validation.json',validation)
    print('完整色域验证',row['id'],row['m'],mismatch,flush=True)
    del cube
dump(DATA/"validation-run.json",dict(environment=environment_fingerprint(),threads=numba.get_num_threads(),script_sha256=sha(__file__)))
