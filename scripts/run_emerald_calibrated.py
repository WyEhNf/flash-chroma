"""完成PR41第二个可分离来源的17³精确校准与一次集中验收。"""
from __future__ import annotations
import argparse
import hashlib
import json
from pathlib import Path
import shutil
import sys
import zipfile

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT/'python'))
import numba
import numpy as np
from PIL import Image
from lutlab import curve, error_analysis as ea, io, runtime, separable_calibration as sc, study_provenance
from lutlab.compatibility import write_json
from run_filmic_calibration import colours, curve_output, full_cube, rgb_keys


def digest(path):
    with Path(path).open('rb') as stream:
        return hashlib.file_digest(stream,'sha256').hexdigest()


def checked(spec):
    p = ROOT/spec['path']
    if digest(p) != spec['sha256']:
        raise ValueError(f'冻结来源SHA不同：{p}')
    return p


def sources(plan_path):
    names = ['scripts/run_emerald_calibrated.py','scripts/run_filmic_calibration.py',
        'python/lutlab/separable_calibration.py','python/lutlab/curve.py','python/lutlab/io.py',
        'python/lutlab/interp.py','python/lutlab/study_kernels.py','python/lutlab/error_analysis.py',
        'python/lutlab/runtime.py','python/lutlab/study_provenance.py','python/lutlab/compatibility.py']
    return {name:digest(ROOT/name) for name in names}|{plan_path.relative_to(ROOT).as_posix():digest(plan_path)}


def prepare(args, plan):
    if args.output.exists():
        raise ValueError('不覆盖已有实验目录')
    for spec in plan['inputs'].values(): checked(spec)
    checked(plan['executable'])
    checked(plan['manifest'])
    for spec in plan['contracts']:
        receipt = json.loads(checked(spec['results']).read_text(encoding='utf-8'))
        evidence = json.loads(checked(spec['run']).read_text(encoding='utf-8'))
        if receipt.get('passed') != spec['expected_checks']:
            raise ValueError('精确接口集中合同未通过')
        if evidence['identity_sha256'] != study_provenance.identity_digest(evidence['identity']):
            raise ValueError('精确接口合同身份不一致')
        bindings = {'python/lutlab/separable_calibration.py':evidence['identity']['module_sha256'],
                    'scripts/verify_separable_calibration.py':evidence['identity']['driver_sha256']}
        for name,sha in bindings.items():
            if digest(ROOT/name) != sha:
                raise ValueError('精确接口与已通过合同源码不同')
    previous_run = json.loads(checked(plan['inputs']['feasibility_run']).read_text(encoding='utf-8'))
    previous = json.loads(checked(plan['inputs']['feasibility_results']).read_text(encoding='utf-8'))
    if (previous_run['identity_sha256'] != study_provenance.identity_digest(previous_run['identity'])
            or previous['run_identity'] != previous_run['identity_sha256']):
        raise ValueError('前阶段可行性身份不一致')
    ref = np.load(checked(plan['inputs']['reference']), mmap_mode='r')
    channels = curve.separable_channels(ref)
    if channels is None or [axis for axis,_ in channels] != [0,1,2]:
        raise ValueError('此单一来源没有完整同轴结构证明')
    baselines = {str(m):io.load_sparse(checked(plan['inputs'][f'baseline{m}']),competition=True) for m in (17,33)}
    candidate, calibration = sc.exact_monotone(baselines['17'],channels,maximum_shift=plan['maximum_shift'])
    if candidate is None:
        raise ValueError('既定精确校准不可行，停止不换方案')
    curves = np.stack([v for _,v in channels],axis=1)
    analytical = {f'baseline{m}':sc.cube_metrics(curve_output(model),curves) for m,model in baselines.items()}
    analytical['calibrated17'] = sc.cube_metrics(curve_output(candidate),curves)
    if (any(analytical['calibrated17'][k] != 0 for k in ['mean','rms','p99','max'])
            or not all(analytical[f'baseline{m}']['mean'] > 0 and analytical[f'baseline{m}']['p99'] > 0 for m in (17,33))):
        raise ValueError('未达到预声明精确零误差与尾部改善触发，停止完整验收')
    identity = {'plan':plan,'source_sha256':sources(args.plan),'environment':study_provenance.environment_fingerprint()}
    identity['environment'].update(numba_threads=numba.get_num_threads(),purpose='精度与原生正确性；不测性能')
    study_provenance.claim_run(args.output/'run.json',{'identity':identity,'identity_sha256':study_provenance.identity_digest(identity)})
    with zipfile.ZipFile(args.output/'measured-source.zip','w',zipfile.ZIP_DEFLATED) as z:
        for name,sha in identity['source_sha256'].items():
            if digest(ROOT/name) != sha:raise ValueError('源码冻结期间变化')
            z.write(ROOT/name,name)
    io.save_sparse(args.output/'calibrated17.slut',candidate)
    for m in (17,33): shutil.copyfile(checked(plan['inputs'][f'baseline{m}']),args.output/f'baseline{m}.slut')
    write_json(args.output/'preparation.json',{'run_identity':study_provenance.identity_digest(identity),
        'calibration':calibration,'analytic_cube':analytical,'candidate_sha256':digest(args.output/'calibrated17.slut'),
        'reference_rgb_sha256':hashlib.sha256(ref.tobytes()).hexdigest(),'full_triggered':True,
        'caps':runtime.capabilities(executable=checked(plan['executable']))})
    print(json.dumps({'analytic_cube':analytical,'calibration':calibration},ensure_ascii=False),flush=True)


def accept(args, plan):
    if (args.output/'full-results.json').exists():raise ValueError('已完成验收，不重复执行')
    run = json.loads((args.output/'run.json').read_text(encoding='utf-8'))
    prep = json.loads((args.output/'preparation.json').read_text(encoding='utf-8'))
    if (run['identity_sha256'] != study_provenance.identity_digest(run['identity'])
            or prep['run_identity'] != run['identity_sha256'] or sources(args.plan) != run['identity']['source_sha256']):
        raise ValueError('拟合与验收身份不同')
    for spec in plan['inputs'].values():checked(spec)
    executable=checked(plan['executable'])
    manifest=checked(plan['manifest'])
    reference=np.load(checked(plan['inputs']['reference']),mmap_mode='r')
    path=args.output/'calibrated17.slut'
    if digest(path)!=prep['candidate_sha256']:raise ValueError('冻结模型改变')
    model=io.load_sparse(path,competition=True)
    cube=full_cube(model,reference,args.output/'candidate-cube.rgb')
    if any(cube[k]!=0 for k in ['mean','rms','p99','max']):raise AssertionError('候选完整色域没有兑现精确解析值')
    if cube['prediction_sha256']!=prep['reference_rgb_sha256']:raise AssertionError('全域输出SHA与完整参考不同')
    receipts=[]
    for kernel in plan['kernels']:
        if kernel not in prep['caps']['available_kernels']:raise ValueError('冻结后端不可用')
        output=args.output/f'{kernel}-cube.rgb'
        record=runtime.cube([path],output,executable=executable,kernel=kernel,threads=1)
        if digest(output)!=cube['prediction_sha256']:raise AssertionError('原生完整色域与独立整数oracle不一致')
        receipts.append({**record,'sha256':digest(output),'byte_mismatches':0})
        print(kernel,'完整色域逐字节一致',flush=True)
    models={'baseline17':io.load_sparse(args.output/'baseline17.slut',competition=True),
            'baseline33':io.load_sparse(args.output/'baseline33.slut',competition=True),'calibrated17':model}
    rows=json.loads(manifest.read_text(encoding='utf-8'))['images']
    if len(rows)!=100:raise ValueError('不是冻结100图')
    records={k:[] for k in models}; expected_hash=hashlib.sha256()
    full_output=np.memmap(args.output/'candidate-cube.rgb',np.uint8,'r',shape=(256**3,3))
    for row in rows:
        image_path=checked(row['evaluation'])
        with Image.open(image_path) as image:
            if image.mode!='RGB' or image.size!=(1024,768):raise ValueError('比赛图片契约不符')
            points=np.asarray(image).reshape(-1,3)
        truth=reference.reshape(-1,3)[rgb_keys(points)]
        for name,sparse in models.items():
            output=ea.Operator([sparse])(points)
            if name=='calibrated17':
                np.testing.assert_array_equal(output,full_output[rgb_keys(points)])
                np.testing.assert_array_equal(output,truth)
                expected_hash.update(output.tobytes())
            records[name].append({'image':row['id'],**ea.metrics(output,truth)})
    photos={}
    for name,per in records.items():
        photos[name]={'n_images':len(per),'mean':float(np.mean([r['mean'] for r in per])),
            'rms':float(np.sqrt(np.mean([r['rms']**2 for r in per]))),'worst_image_p99':max(r['p99'] for r in per),
            'max':max(r['max'] for r in per),'mean_image_cvar_1pct':float(np.mean([r['cvar_1pct'] for r in per])),
            'per_image':per}
    listing=args.output/'photos.txt'
    listing.write_text('\n'.join(str(ROOT/r['evaluation']['path']) for r in rows)+'\n',encoding='utf-8')
    raw=args.output/'native-photos.rgb'
    native_photos=runtime.verify([path],listing,executable=executable,kernel='tetra_avx2',threads=4,output=raw)
    if digest(raw)!=expected_hash.hexdigest():raise AssertionError('AVX2完整百图与研究输出不同')
    result={'run_identity':run['identity_sha256'],'candidate_sha256':digest(path),'cube':cube,
        'baseline_cube_analytic':{k:v for k,v in prep['analytic_cube'].items() if k.startswith('baseline')},
        'native_cube':receipts,'photos':photos,'native_photos':{**native_photos,'sha256':digest(raw),'byte_mismatches':0},
        'model_bytes':{k:(args.output/f'{k}.slut').stat().st_size for k in models},
        'scope':plan['limits'],'default_promoted':False,'performance_measured':False}
    write_json(args.output/'full-results.json',result)
    print(json.dumps({'cube':cube,'photos':{k:{m:v[m] for m in ['mean','rms','worst_image_p99','max']} for k,v in photos.items()}},ensure_ascii=False),flush=True)


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('mode',choices=['prepare','accept'])
    parser.add_argument('--plan',type=Path,required=True)
    parser.add_argument('--output',type=Path,required=True)
    args=parser.parse_args();args.plan=args.plan.resolve();args.output=args.output.resolve()
    numba.set_num_threads(4)
    (prepare if args.mode=='prepare' else accept)(args,json.loads(args.plan.read_text(encoding='utf-8')))


if __name__=='__main__':main()
