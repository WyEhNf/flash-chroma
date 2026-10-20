"""冻结双案例的来源、全色域误差、百图复核及单因素诊断；不执行 Git 上传。"""
import os
for name in ('OMP_NUM_THREADS', 'OPENBLAS_NUM_THREADS', 'MKL_NUM_THREADS'):
    os.environ[name] = '1'
import sys
from pathlib import Path
ROOT = Path(__file__).resolve().parents[4]
sys.path.insert(0, str(ROOT / 'python'))
import csv
import hashlib
import json
import platform
import subprocess
import numpy as np
import numba
from PIL import Image
from lutlab import io, interp, fit, curve, source_lut, study_kernels as kernels
from lutlab.compatibility import model_args
from lutlab.study_provenance import environment_fingerprint

OUT = Path(__file__).resolve().parents[1]
OLD = ROOT / 'artifacts/local-lut-study/20261016'
PAIRS = ROOT / 'artifacts/lut-dual-baseline/20261017'
DATA = OUT / 'data'
DATA.mkdir(exist_ok=True)
numba.set_num_threads(4)

def sha(p):
    with Path(p).open('rb') as f:
        return hashlib.file_digest(f, 'sha256').hexdigest()

def dump(name, value):
    (DATA/name).write_text(json.dumps(value, ensure_ascii=False, indent=2,
        default=lambda x: x.tolist() if isinstance(x, np.ndarray) else x.item(), allow_nan=False), encoding='utf-8')

def rows(name, values):
    with (DATA/name).open('w', encoding='utf-8-sig', newline='') as f:
        w = csv.DictWriter(f, fieldnames=list(values[0])); w.writeheader(); w.writerows(values)

def keys(rgb):
    a = rgb.reshape(-1, 3).astype(np.int32)
    return (a[:, 0]*256+a[:, 1])*256+a[:, 2]

def stats(hist):
    n = hist.sum(); v = np.sqrt(np.arange(len(hist))); cum = hist.cumsum()
    rank = .99*(n-1); lo = int(np.floor(rank)); hi = int(np.ceil(rank))
    p99 = np.interp(rank-lo, [0,1], [v[np.searchsorted(cum,lo,side='right')], v[np.searchsorted(cum,hi,side='right')]])
    return dict(mean=float(hist@v/n), rms=float(np.sqrt(hist@np.arange(len(hist))/n)),
        p99=float(p99), max=float(v[np.flatnonzero(hist)[-1]]), fraction_ge_2=float(hist[4:].sum()/n))

manifest = json.loads((ROOT/'assets/photos/manifest.json').read_text(encoding='utf-8'))
photo_keys = []; photos = []; provenance = {}
for image in manifest['images']:
    image = image['evaluation']
    p = ROOT/image['path']; actual = sha(p)
    assert actual == image['sha256'], p
    photo_keys.append(keys(np.asarray(Image.open(p).convert('RGB'))))
    photos.append(image['path']); provenance[image['path']] = actual
freq = np.zeros(256**3, np.int64)
for k in photo_keys:
    np.add.at(freq, k, 1)
historical = list(csv.DictReader((PAIRS/'full-results.csv').open(encoding='utf-8-sig')))
results = []; per_image = []; checks = []; detail = {}

def measure(case, label, pred, truth, historical_profile=None, m=None, lut=None):
    pred = pred.reshape(-1,3); truth = truth.reshape(-1,3)
    delta = pred.astype(np.int32)-truth.astype(np.int32)
    d2 = np.sum(delta*delta, axis=1)
    full = stats(np.bincount(d2, minlength=195076))
    weighted = stats(np.bincount(d2, weights=freq, minlength=195076))
    image_stats = []
    for p,k in zip(photos,photo_keys):
        s = stats(np.bincount(d2[k],minlength=195076)); image_stats.append(s)
        per_image.append(dict(case=case,variant=label,image=p,**s))
    worst_p99 = max(s['p99'] for s in image_stats)
    record = dict(case=case,variant=label,m=m,cube_mean=full['mean'],cube_rms=full['rms'],cube_p99=full['p99'],cube_max=full['max'],
        photo_mean=weighted['mean'],photo_rms=weighted['rms'],photo_worst_p99=worst_p99,photo_max=weighted['max'],
        photo_fraction_ge_2=weighted['fraction_ge_2'],cube_fraction_ge_2=full['fraction_ge_2'])
    results.append(record)
    peak = int(np.argmax(d2)); seen = np.flatnonzero(freq); peak_photo = int(seen[np.argmax(d2[seen])])
    def witness(k):
        return dict(rgb=[k>>16,(k>>8)&255,k&255],reference=truth[k].tolist(),output=pred[k].tolist(),
                    error=float(np.sqrt(d2[k])),photo_occurrences=int(freq[k]))
    detail[case+'/'+label] = dict(cube_peak=witness(peak),photo_peak=witness(peak_photo),
        photos_with_ge2=sum(s['fraction_ge_2']>0 for s in image_stats))
    if historical_profile:
        old = [r for r in historical if r['lut']==lut and r['profile']==historical_profile and int(r['m'])==m]
        assert len(old)==1
        for a,b in [('photo_mean','mean'),('photo_rms','rms'),('photo_worst_p99','worst_image_p99'),('photo_max','max')]:
            assert abs(record[a]-float(old[0][b]))<1e-10,(case,label,a,record[a],old[0][b])
        checks.append(dict(check='历史百图四项误差一致',case=case,variant=label))
    print(case,label,record,flush=True)
    return d2

def oracle(model, actual):
    # 独立逐通道整数累加，分块穷举所有 RGB8，与 Numba 映射比较。
    idx, frac = model.tables(); nodes = model.nodes.reshape(-1,3).astype(np.int64)
    for start in range(0,256**3,131072):
        k=np.arange(start,start+131072,dtype=np.int32)
        rgb=np.stack([k>>16,(k>>8)&255,k&255],axis=1).astype(np.uint8)
        I,W=interp.tetra_index_weights_q(rgb,idx,frac,model.m)
        out=((np.sum(nodes[I]*W[:,:,None].astype(np.int64),axis=1)+32768)>>16).astype(np.uint8)
        assert np.array_equal(out,actual[start:start+len(k)])

def curve_cube(values):
    out=np.empty((256,256,256,3),np.uint8)
    for a in range(3):
        shape=[1,1,1];shape[a]=256;out[...,a]=values[:,a].reshape(shape)
    return out.reshape(-1,3)

for case, ident in [('filmic06','0846de8be0c3'),('emerald','b76d97e0958d')]:
    report_path=OLD/'luts'/ident/'result.json'
    old=json.loads(report_path.read_text(encoding='utf-8')); lut=old['lut']['path']
    assert sha(ROOT/lut)==old['lut']['sha256']
    provenance[lut]=sha(ROOT/lut);provenance[str(report_path.relative_to(ROOT))]=sha(report_path)
    refpath=OLD/'references'/f'{ident}.npy'; assert sha(refpath)==old['reference_sha256']
    provenance[str(refpath.relative_to(ROOT))]=sha(refpath)
    T=np.load(refpath).reshape(256,256,256,3); truth=T.reshape(-1,3)
    channels=curve.separable_channels(T);assert channels is not None and [c[0] for c in channels]==[0,1,2]
    detail[case+'/structure']=dict(verified_colors=256**3,axes=[c[0] for c in channels])
    models={}; frozen={}
    for r in old['screen']:
        if r['profile'] not in ['sample_tetra','dp_jitter','dp_supported']: continue
        if case=='filmic06' and r['profile']=='dp_jitter':continue
        p=OLD/r['model'];assert sha(p)==r['model_sha256'];provenance[str(p.relative_to(ROOT))]=sha(p)
        model=io.load_sparse(p);key=(r['profile'],r['m']);models[key]=model;frozen[key]=r
        pred=kernels.expand_cube(*model_args(model),0);oracle(model,pred)
        checks.append(dict(check='全色域整数参考逐字节一致',case=case,profile=r['profile'],m=r['m'],colors=256**3))
        d2=measure(case,f"{r['profile']}_m{r['m']}",pred,truth,r['profile'],r['m'],lut)
        if case=='emerald' and r['profile']=='dp_jitter':
            np.save(DATA/f'emerald-jitter-m{r["m"]}-d2.npy',d2)
    if case=='filmic06':
        raw,grid,policy=source_lut.load_source(ROOT/lut,old['lut']);raw=raw.reshape(17,17,17,3)
        raw_curves=np.stack([raw[:,0,0,0],raw[0,:,0,1],raw[0,0,:,2]],axis=1)
        for a in range(3):
            shape=[1,1,1];shape[a]=17
            assert np.array_equal(raw[...,a],np.broadcast_to(raw_curves[:,a].reshape(shape),(17,17,17)))
        continuous=np.stack([np.interp(np.arange(256),grid[a],raw_curves[:,a]) for a in range(3)],axis=1)
        q=lambda a:np.clip(np.floor(a+.5),0,255).astype(np.uint8)
        assert np.array_equal(curve_cube(q(continuous)),truth)
        checks.append(dict(check='原始3DL独立一维展开与完整参考逐字节一致',colors=256**3))
        curves=[]
        for m in [17,33]:
            model=models['sample_tetra',m];g=model.grid.astype(np.float64);idx,frac=model.tables()
            nodes=model.nodes
            nodecurve=np.stack([nodes[:,0,0,0],nodes[0,:,0,1],nodes[0,0,:,2]],axis=1)
            exactidx,exactfrac=source_lut.source_axes(g)
            def reconstruct(n,f):return np.stack([(1-f[a])*n[exactidx[a],a]+f[a]*n[exactidx[a]+1,a] for a in range(3)],axis=1)
            ideal=np.stack([np.interp(g[a],grid[a],raw_curves[:,a]) for a in range(3)],axis=1)
            moved=np.stack([np.interp(np.rint(g[a]),grid[a],raw_curves[:,a]) for a in range(3)],axis=1)
            assert np.array_equal(q(moved),nodecurve)
            variants={'raw_exact_positions_exact_weights':reconstruct(ideal,exactfrac),
                'raw_rounded_positions_exact_weights':reconstruct(moved,exactfrac),
                'byte_nodes_exact_weights':reconstruct(nodecurve,exactfrac),
                'byte_nodes_q16_weights':reconstruct(nodecurve,frac/65536.)}
            for label,value in variants.items():
                pred=curve_cube(q(value));measure(case,f'{label}_m{m}',pred,truth,m=m)
                if label=='byte_nodes_q16_weights':
                    baseline=kernels.expand_cube(*model_args(model),0);assert np.array_equal(pred,baseline)
                    tri=kernels.expand_cube(*model_args(model),1);assert np.array_equal(tri,baseline)
                    checks.append(dict(check='该可分离基线三线性与四面体全色域输出一致',m=m,colors=256**3))
                detail[f'filmic06/{label}_m{m}']['pre_round_channel_mae']=float(np.mean(np.abs(value-continuous)))
                for x in range(256):
                    curves.append(dict(m=m,variant=label,input=x,source_float=continuous[x,0],reference=int(T[x,0,0,0]),
                        prediction_float=value[x,0],prediction=int(q(value)[x,0]),error=int(q(value)[x,0])-int(T[x,0,0,0])))
            detail[f'filmic06/axis_m{m}']=dict(grid=g[0],rounded=np.rint(g[0]),nodes=nodecurve[:,0],raw_exact=ideal[:,0],raw_moved=moved[:,0])
        rows('filmic-curves.csv',curves)
    else:
        for m in [17,33]:
            jitter=models['dp_jitter',m];supported=models['dp_supported',m]
            assert np.array_equal(jitter.grid,supported.grid)
            assert all(np.array_equal(a,b) for a,b in zip(jitter.tables(),supported.tables()))
            g=jitter.grid;I,W=interp.tetra_weights(fit.stratified_points(),*jitter.tables(),m)
            diag=np.bincount(I.ravel(),weights=(W*W).ravel(),minlength=m**3)
            counts=np.bincount(I[W>0],minlength=m**3)
            vertices=np.stack(np.meshgrid(*g,indexing='ij'),axis=-1).reshape(-1,3).astype(np.uint8)
            node_error=np.sqrt(np.sum((jitter.nodes.reshape(-1,3).astype(np.int32)-truth[keys(vertices)].astype(np.int32))**2,axis=1))
            worst=detail[f'emerald/dp_jitter_m{m}']['photo_peak']['rgb']
            wi,ww=interp.tetra_weights(np.array([worst],np.uint8),*jitter.tables(),m)
            active=[]
            for n,w in zip(wi[0],ww[0]):
                if w==0:continue
                active.append(dict(node=int(n),coordinate=vertices[n],weight=float(w),data_diagonal=float(diag[n]),sample_count=int(counts[n]),
                    jitter=jitter.nodes.reshape(-1,3)[n],supported=supported.nodes.reshape(-1,3)[n],reference=truth[keys(vertices[n:n+1])[0]]))
            detail[f'emerald/support_m{m}']=dict(grid=g,zero_diagonal_nodes=int(np.sum(diag==0)),min_diagonal=float(diag.min()),
                weak_below_1_64=int(np.sum(diag<1/64)),max_node_error=float(node_error.max()),
                worst_photo_active_nodes=active,historical_supported_route=frozen['dp_supported',m]['diagnostics'])
            # 相同轴表、相同整数精化，显式绕过可分离专用路径，检验通用支撑修复。
            diagnostic={};x,H,b=fit.fit_supported_tetra(T,g,diagnostics=diagnostic)
            fixed=io.SparseLut(g,fit.quantize(fit.int_refine(x,H,b).reshape(m,m,m,3)),*jitter.tables())
            io.save_sparse(DATA/f'emerald-general-supported-m{m}.slut',fixed)
            pred=kernels.expand_cube(*model_args(fixed),0);oracle(fixed,pred)
            measure(case,f'general_supported_m{m}',pred,truth,m=m)
            detail[f'emerald/general_supported_m{m}']['fit_diagnostics']=diagnostic
            checks.append(dict(check='新通用支撑模型全色域整数参考逐字节一致',m=m,colors=256**3))
    dump('details.json',detail);rows('metrics.csv',results);rows('per-image.csv',per_image);dump('checks.json',checks)

for p in [Path(__file__),*[ROOT/'python/lutlab'/n for n in ['fit.py','curve.py','source_lut.py','io.py','interp.py','study_kernels.py']]]:
    provenance[str(p.relative_to(ROOT))]=sha(p)
dump('run.json',dict(environment=environment_fingerprint(),numba_threads=numba.get_num_threads(),threading_layer=numba.threading_layer(),
    git_commit=subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip(),inputs_and_code_sha256=provenance,
    purpose='误差来源诊断、全色域运行时一致性及百图精度复核；没有性能计时',photo_count=len(photos),photo_pixels=int(freq.sum())))
print('诊断完成',flush=True)
