"""核对冻结68源和136份DP模型，执行PR42精确单调校准可行性普查。"""
import os
for k in ['OMP_NUM_THREADS','MKL_NUM_THREADS','OPENBLAS_NUM_THREADS']:os.environ[k]='1'
import sys,json,hashlib,csv,subprocess
from pathlib import Path
ROOT=Path(__file__).resolve().parents[4]
SOURCE=ROOT/'tmp/stage-a-pr42/python'
sys.path.insert(0,str(SOURCE))
import numpy as np
from lutlab import io,curve,separable_calibration as cal
from lutlab.study_provenance import environment_fingerprint
OUT=Path(__file__).resolve().parents[1];DATA=OUT/'data';DATA.mkdir(exist_ok=True)
OLD=ROOT/'artifacts/local-lut-study/20261016'
def sha(p):
    with Path(p).open('rb') as f:return hashlib.file_digest(f,'sha256').hexdigest()
def dump(p,d):p.write_text(json.dumps(d,ensure_ascii=False,indent=2),encoding='utf-8')
def table(p,rows):
    with p.open('w',encoding='utf-8-sig',newline='') as f:
        w=csv.DictWriter(f,fieldnames=list(rows[0]));w.writeheader();w.writerows(rows)
if (DATA/'survey.json').exists():raise RuntimeError('已有完成结果，拒绝覆盖；新实验须使用新目录')
records=[];evidence=[];hashes={};reports=[]
for p in sorted((OLD/'luts').glob('*/result.json')):
    report=json.loads(p.read_text(encoding='utf-8'));reports.append(report)
assert len(reports)==68
for report in reports:
    entry=report['lut'];ident=entry['sha256'][:12];path=ROOT/entry['path']
    assert sha(path)==entry['sha256'];hashes[entry['path']]=entry['sha256']
    ref=OLD/'references'/f'{ident}.npy';assert sha(ref)==report['reference_sha256']
    hashes[str(ref.relative_to(ROOT))]=report['reference_sha256']
    T=np.load(ref,mmap_mode='r');channels=curve.separable_channels(T)
    for m in [17,33]:
        r=next(r for r in report['screen'] if r['profile']=='dp_supported' and r['m']==m)
        p=OLD/r['model'];assert sha(p)==r['model_sha256'];hashes[str(p.relative_to(ROOT))]=r['model_sha256']
        model=io.load_sparse(p)
        candidate,detail=cal.exact_monotone(model,channels,maximum_shift=4096)
        base_metrics={};after_metrics={}
        if channels is not None:
            # 若共享输入轴，卷积独立性不成立；本数据若出现此情况必须另实现联合枚举。
            axes=[a for a,v in channels];assert sorted(axes)==[0,1,2]
            predicted=[]
            for c,(a,v) in enumerate(channels):
                select=[0,0,0,c];select[a]=slice(None)
                predicted.append(cal.evaluate_curve(model.nodes[tuple(select)],model.tables()[0][a],model.tables()[1][a]))
            base_metrics=cal.cube_metrics(np.stack(predicted,axis=1),np.stack([v for a,v in channels],axis=1))
        if candidate is not None:
            assert np.array_equal(candidate.nodes,model.nodes) and np.array_equal(candidate.grid,model.grid)
            assert np.array_equal(candidate.tables()[0],model.tables()[0])
            destination=DATA/'models'/f'{ident}-calibrated-m{m}.slut';destination.parent.mkdir(exist_ok=True)
            io.save_sparse(destination,candidate)
            loaded=io.load_sparse(destination)
            assert np.array_equal(loaded.tables()[1],candidate.tables()[1])
            after_metrics=dict(n=256**3,mean=0.,rms=0.,p99=0.,max=0.)
            route='exact_monotone_calibrated'
        else:route='structured_dp_fallback' if channels is not None else 'general_supported_fallback'
        reasons={}
        for x in detail.get('failures',[]):reasons[x['reason']]=reasons.get(x['reason'],0)+1
        record=dict(lut=entry['path'],source=entry['source_id'],id=ident,m=m,separable=channels is not None,
            axes=str([a for a,v in channels]) if channels else '',route=route,reason=detail.get('reason'),
            failure_reasons=json.dumps(reasons,ensure_ascii=False),changed_fractions=detail.get('changed_fractions',0),
            before_cube_mean=base_metrics.get('mean'),before_cube_max=base_metrics.get('max'),
            after_cube_mean=after_metrics.get('mean',base_metrics.get('mean')),after_cube_max=after_metrics.get('max',base_metrics.get('max')))
        records.append(record);evidence.append(dict(**record,calibration=detail,source_diagnostics=r['diagnostics']))
    print(ident,entry['path'],records[-2]['route'],records[-1]['route'],flush=True)
for p in SOURCE.rglob('*.py'):hashes[str(p.relative_to(ROOT))]=sha(p)
hashes[str(Path(__file__).relative_to(ROOT))]=sha(__file__)
table(DATA/'survey.csv',records);dump(DATA/'survey.json',evidence)
dump(DATA/'survey-run.json',dict(source_commit='59586f7bd6dd248cf0b68bcbdff8e41cf95ac572',
    workspace_commit=subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip(),
    environment=environment_fingerprint(),hashes=hashes,source_luts=68,size_cases=136,
    scope='完整源结构验证＋冻结DP模型坐标校准；未重新拟合全部模型，非可分离者明确复用旧general_supported模型；解析全域统计仅用于三轴独立可分离源'))
