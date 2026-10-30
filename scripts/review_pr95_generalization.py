"""冻结八条数值链，检查公开拟合入口、跨后端输出与跨链精度；不作摄影域认证。"""
from pathlib import Path
import os, sys, json, time, hashlib, platform, subprocess
ROOT=Path(__file__).resolve().parents[1]
sys.path[:0]=[str(ROOT/'python'),str(ROOT/'scripts')]
os.environ.setdefault('OMP_NUM_THREADS','4')
os.environ.setdefault('OPENBLAS_NUM_THREADS','1')
os.environ.setdefault('MKL_NUM_THREADS','1')
import numpy as np
import numba
from PIL import Image
from lutlab import source_lut,io
import p16_frontier as frontier
import flash_chroma_support as native

OUT=ROOT/'artifacts/pr95-review'
CHAINS={'cinema':[11,12,13,14],'avant':[0,1,2,3],'scenic':[30,31,32,33],
        'cinema_reverse':[14,13,12,11],'mixed_tail':[25,55,58,66],
        'mixed_hdr':[49,56,1,64],'zoology':[41,42,43,44],'filmsim':[54,55,56,57]}
def save(name,obj): native.write_json(OUT/name,obj)
def metric(a,b):
    d=a.astype(np.int32)-b.astype(np.int32); e=np.sqrt(np.sum(d*d,axis=-1))
    return {'mean':float(e.mean()),'p99':float(np.quantile(e,.99)),'max':float(e.max())}
def oracle(model,points):
    """独立NumPy排序四面体，int64加权，逐级half-up。"""
    idx,frac=model.tables(); n=len(points); axes=np.arange(3)[:,None]
    cell=idx[axes,points.T].T.astype(np.int64)
    f=frac[axes,points.T].T.astype(np.int64)
    order=np.argsort(-f,axis=1,kind='stable'); f=np.take_along_axis(f,order,axis=1)
    steps=np.array([model.m*model.m,model.m,1])[order]
    base=cell@np.array([model.m*model.m,model.m,1])
    ids=np.column_stack((base,base+steps[:,0],base+steps[:,:2].sum(1),base+steps.sum(1)))
    w=np.column_stack((65536-f[:,0],f[:,0]-f[:,1],f[:,1]-f[:,2],f[:,2]))
    return ((np.sum(model.nodes.reshape(-1,3)[ids].astype(np.int64)*w[:,:,None],axis=1)+32768)>>16).astype(np.uint8)
def refmap(tables,x):
    for t in tables:x=t[x[:,0],x[:,1],x[:,2]]
    return x
def main():
    numba.set_num_threads(4)
    dllpath=os.add_dll_directory('D:/codeblocks/MinGW/bin')
    library=native.Library(OUT/'review.dll')
    assets=json.loads((ROOT/'assets/LUT/manifest.json').read_text(encoding='utf8'))['assets']
    photos=json.loads((ROOT/'assets/photos/manifest.json').read_text(encoding='utf8'))['images']
    chosen=[]
    for dataset in ('kodak','dped','div2k'):chosen += [p for p in photos if p.get('dataset')==dataset][:2]
    plan={'sha':'fb7e195215f14df9f635394d75cde0e0e69c82c9','chains':{k:[assets[i] for i in ids] for k,ids in CHAINS.items()},
          'sizes':[17,33],'method':'sample_interp','grid':'uniform','seed':20261028,'random_probes':65536,
          'photos':chosen,'repetitions':5,'full_domain_chains':['cinema','mixed_hdr'],
          'scope':'公开默认拟合路线跨链诊断；随机探针加八角点、六张完整历史照片；不等于373a联合调优迁移或68^4覆盖',
          'environment':{'platform':platform.platform(),'python':sys.version,'numpy':np.__version__,'numba':numba.__version__,
          'processor':os.environ.get('PROCESSOR_IDENTIFIER'),'compiler':subprocess.check_output(['g++','--version']).decode().splitlines()[0],
          'flags':'-std=c++17 -O3 -DNDEBUG -fopenmp; C99 -O3 -DNDEBUG','library':library.record(),'threads':4}}
    save('plan.json',plan)
    rng=np.random.default_rng(20261028)
    probes=np.vstack((rng.integers(0,256,(65536,3),dtype=np.uint8),np.array(list(__import__('itertools').product((0,255),repeat=3)),np.uint8)))
    frames=[]
    for p in chosen:
        path=ROOT/p['evaluation']['path']; assert native.digest(path)==p['evaluation']['sha256']
        frames.append(np.asarray(Image.open(path).convert('RGB')).reshape(-1,3).copy())
    photo_input=np.concatenate(frames)
    (OUT/'tables').mkdir(exist_ok=True)
    tables={}
    for i in sorted(set(sum(CHAINS.values(),[]))):
        a=assets[i];path=ROOT/a['path'];assert native.digest(path)==a['sha256']
        table,policy=source_lut.bake_source(path,a);dest=OUT/'tables'/f'{i}.lut256';io.save_full(dest,table)
        tables[i]=dest
        print('参考表',i,flush=True)
    results=[]
    for name,ids in CHAINS.items():
        refs=[io.load_full(tables[i],mmap=True) for i in ids]
        truth=refmap(refs,probes); photo_truth=refmap(refs,photo_input)
        for m in (17,33):
            folder=OUT/f'{name}-m{m}'
            manifest=frontier.fit_candidate([tables[i] for i in ids],[m]*4,'sample_interp','uniform',folder)
            model=native.Model(manifest['profiles']['fitted'],folder)
            sparse=[io.load_sparse(folder/f'stage{i}.slut') for i in range(1,5)]
            expected=probes.copy()
            for s in sparse:expected=oracle(s,expected)
            row={'chain':name,'m':m,'probe_accuracy':metric(expected,truth),'models':model.records,'configs':[]}
            scalar_photo=None
            for rep,backend in [('sparse','scalar'),('sparse','avx2'),('direct_u8','avx2'),('direct_u16','avx2'),('direct_rgb24','avx2')]:
                config=native.configuration(rep,backend,threads=1 if backend=='scalar' else 4)
                try:engine=library.create(model,config)
                except RuntimeError as ex:
                    if '10 调色板容量不足' not in str(ex):raise
                    row['configs'].append({'config':config,'status':'capacity','error':str(ex)})
                    continue
                with engine:
                    actual=np.empty_like(probes);engine.apply(probes,actual);np.testing.assert_array_equal(actual,expected)
                    out=np.empty_like(photo_input);engine.apply(photo_input,out)
                    if scalar_photo is None:scalar_photo=out.copy()
                    else:np.testing.assert_array_equal(out,scalar_photo)
                    for count in (1,7,8,9,63,64,65,257):
                        small=probes[:count].copy();engine.apply(small,small);np.testing.assert_array_equal(small,expected[:count])
                    times=[]
                    for _ in range(5):
                        out.fill(173); times.append(engine.apply(photo_input,out));np.testing.assert_array_equal(out,scalar_photo)
                    info={'config':config,'status':'ok','probe_mismatches':0,'photo_mismatches':0,
                          'resources':engine.info,'prepare':engine.preparation,'prepare_ms':engine.prepare_ms,
                          'apply_ms':times,'median_ms':float(np.median(times)),'output_sha256':native.sha(out)}
                    row['configs'].append(info)
            c_result=np.empty_like(probes); assert library.c_apply(model,probes,c_result)==0
            np.testing.assert_array_equal(c_result,expected)
            row['c99_probe_mismatches']=0
            row['photo_accuracy']=metric(scalar_photo,photo_truth)
            row['per_image']=[{'id':p['id'],**metric(scalar_photo[j*len(frames[j]):(j+1)*len(frames[j])],photo_truth[j*len(frames[j]):(j+1)*len(frames[j])])} for j,p in enumerate(chosen)]
            if name in ('cinema','mixed_hdr') and m==33:
                with library.create(model,native.configuration('direct_rgb24','avx2',4)) as direct,library.create(model,native.configuration('sparse','scalar',1)) as scalar:
                    stream=hashlib.sha256();hist=np.zeros(195076,np.int64)
                    for start in range(0,256**3,262144):
                        codes=np.arange(start,start+262144,dtype=np.uint32)
                        x=np.column_stack((codes>>16,(codes>>8)&255,codes&255)).astype(np.uint8)
                        a=np.empty_like(x);b=np.empty_like(x);direct.apply(x,a);scalar.apply(x,b);np.testing.assert_array_equal(a,b)
                        stream.update(a);d=a.astype(np.int32)-refmap(refs,x).astype(np.int32)
                        hist+=np.bincount(np.sum(d*d,axis=1),minlength=len(hist))
                    np.save(OUT/f'{name}-m33-full-hist.npy',hist)
                    row['full_domain']={'colors':256**3,'scalar_direct_mismatches':0,'sha256':stream.hexdigest(),
                        'mean':float(hist@np.sqrt(np.arange(len(hist)))/hist.sum()),'max':float(np.sqrt(np.flatnonzero(hist)[-1]))}
            results.append(row);save('results.json',results)
            print('完成',name,m,row['photo_accuracy'],[(c['config']['representation'],c['status']) for c in row['configs']],flush=True)
    save('completed.json',{'passed':True,'models':len(results),'scope':plan['scope']})
if __name__=='__main__':main()
