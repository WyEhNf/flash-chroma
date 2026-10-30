"""生成局部反例与图示，全部读取冻结模型；不重新拟合。"""
import os
for name in ('OMP_NUM_THREADS','OPENBLAS_NUM_THREADS','MKL_NUM_THREADS'): os.environ[name]='1'
from pathlib import Path
import sys, json, csv, hashlib
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
OUT=Path(__file__).resolve().parents[1];ROOT=OUT.parents[2]
sys.path.insert(0,str(ROOT/'python'))
from lutlab import io,fit,interp
plt.rcParams['font.sans-serif']=['Microsoft YaHei','SimHei','DejaVu Sans']
plt.rcParams['axes.unicode_minus']=False
DATA=OUT/'data'
curves=list(csv.DictReader((DATA/'filmic-curves.csv').open(encoding='utf-8-sig')))
fig,axs=plt.subplots(2,1,figsize=(10,6),layout='constrained')
for m,color in [(17,'#2978b5'),(33,'#dd7229')]:
    part=[r for r in curves if r['m']==str(m) and r['variant']=='byte_nodes_q16_weights']
    x=np.array([int(r['input']) for r in part]);y=np.array([float(r['prediction_float']) for r in part])
    axs[0].plot(x[:17],y[:17],marker='.',color=color,label=f'{m}³基线，最终取整前')
    axs[1].step(x,[int(r['error']) for r in part],where='mid',color=color,alpha=.8,label=f'{m}³基线')
axs[0].plot(x[:17],[float(r['source_float']) for r in part][:17],color='black',linestyle='--',label='原始浮点曲线')
axs[0].axvline(4,color='gray',alpha=.4);axs[0].set(title='Filmic 06：低码值曲线与整数输出误差',ylabel='R 输出码值')
axs[1].set(xlabel='R 输入码值（G、B 固定为 0）',ylabel='输出 − RGB8 参考')
for ax in axs:ax.legend(fontsize=9);ax.grid(alpha=.2)
fig.savefig(DATA/'filmic-curves.png',dpi=150);plt.close(fig)

old=ROOT/'artifacts/local-lut-study/20261016';ident='b76d97e0958d'
d=json.loads((old/'luts'/ident/'result.json').read_text(encoding='utf-8'))
T=np.load(old/'references'/f'{ident}.npy')
models={}
for r in d['screen']:
    if r['profile'] in ['dp_jitter','dp_supported'] and r['m']==33:
        models[r['profile']]=io.load_sparse(old/r['model'])
models['general_supported']=io.load_sparse(DATA/'emerald-general-supported-m33.slut')
points=fit.stratified_points();model=models['dp_jitter'];I,W=interp.tetra_weights(points,*model.tables(),33)
node=14553;where=np.flatnonzero(np.any((I==node)&(W>0),axis=1));assert len(where)==1
vertex=np.stack(np.meshgrid(*model.grid,indexing='ij'),axis=-1).reshape(-1,3).astype(np.uint8)
witness=[]
for row in where:
    p=points[row];pred=interp.apply_tetra_q16(model,p[None])[0]
    witness.append(dict(training_rgb=p.tolist(),reference=T[tuple(p)].tolist(),output=pred.tolist(),
        active_nodes=[dict(index=int(n),coordinate=vertex[n].tolist(),weight=float(w),
            fitted=model.nodes.reshape(-1,3)[n].tolist(),reference=T[tuple(vertex[n])].tolist())
            for n,w in zip(I[row],W[row]) if w>0]))
(DATA/'emerald-training-witness.json').write_text(json.dumps(witness,ensure_ascii=False,indent=2),encoding='utf-8')
rg=np.indices((256,256));pixels=np.stack([rg[0].ravel(),rg[1].ravel(),np.zeros(65536,int)],axis=1).astype(np.uint8)
fig,axs=plt.subplots(1,3,figsize=(12,4),layout='constrained')
for ax,(name,model) in zip(axs,models.items()):
    y=interp.apply_tetra_q16(model,pixels).astype(np.int32);t=T[pixels[:,0],pixels[:,1],pixels[:,2]].astype(np.int32)
    error=np.sqrt(np.sum((y-t)**2,axis=1)).reshape(256,256)
    im=ax.imshow(error.T,origin='lower',vmin=0,vmax=26,cmap='magma',extent=(-.5,255.5,-.5,255.5))
    ax.scatter([126],[35],marker='+',c='cyan',s=65)
    ax.set(title={'dp_jitter':'原 jitter 拟合','dp_supported':'可分离整数 DP','general_supported':'通用补支撑拟合'}[name],xlabel='R 输入',ylabel='G 输入')
fig.colorbar(im,ax=axs,label='RGB 欧氏误差',shrink=.85)
fig.suptitle('Emerald 33³：B=0 切片，共用色标；十字为百图最坏颜色')
fig.savefig(DATA/'emerald-slice.png',dpi=150);plt.close(fig)
print(json.dumps(witness,ensure_ascii=False))
