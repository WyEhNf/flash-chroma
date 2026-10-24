"""机械生成独立v2入口：仅补观察器进程前置、checkpoint与输出路径。"""
from __future__ import annotations
import hashlib
import json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]


def sha(path):return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def main():
    frozen_path=ROOT/'artifacts/cinema-current-full-quality-frozen-v1.json';frozen=json.loads(frozen_path.read_text(encoding='utf-8'))
    if sha(frozen_path)!='96589fdd296e8be93fec31d9c84acab76d67f4dd925deaed45bb8c9b2b962b9e':raise ValueError('不是保留的首次失败冻结')
    names=('scripts/qualify_cinema_current_full.py','scripts/audit_cinema_current_full_quality.py','experiments/p16-cinema-current-full-quality-v1.json')
    for name in names:
        if sha(ROOT/name)!=frozen['source_sha256'][name]:raise ValueError('v1冻结源被改')
    target=ROOT/'scripts/qualify_cinema_current_full_v2.py';audit_target=ROOT/'scripts/audit_cinema_current_full_quality_v2.py';plan_target=ROOT/'experiments/p16-cinema-current-full-quality-v2.json';proof=ROOT/'artifacts/cinema-current-full-quality-mechanical-v2.json'
    if any(p.exists() for p in (target,audit_target,plan_target,proof)):raise ValueError('不覆盖独立v2机械源')
    text=(ROOT/names[0]).read_text(encoding='utf-8')
    substitutions=[("from contextlib import ExitStack\n", "from contextlib import ExitStack\nimport psutil\n_ALLOWED=[0,2,4,6]\n_process=psutil.Process();_prior_allowed=_process.cpu_affinity();_process.cpu_affinity(_ALLOWED)\nif _process.cpu_affinity()!=_ALLOWED:raise ValueError('必须在加载NumPy/任何native前完成进程0x55前置')\n"),
        ('p16-cinema-current-full-quality-v1.json','p16-cinema-current-full-quality-v2.json'),
        ('cinema-current-full-quality-frozen-v1.json','cinema-current-full-quality-frozen-v2.json'),
        ('cinema-current-full-quality-v1\'','cinema-current-full-quality-v2\''),
        ("'scripts/audit_cinema_current_full_quality.py'", "'scripts/audit_cinema_current_full_quality_v2.py','scripts/prepare_cinema_current_full_v2.py','scripts/qualify_cinema_current_full.py','scripts/audit_cinema_current_full_quality.py','experiments/p16-cinema-current-full-quality-v1.json'"),
        ("    paths.update((ROOT/'report/data/p16-cinema-current-feasible-cpsat-20261024/manifest.json',HELPER,GOMP))", "    paths.update((ROOT/'report/data/p16-cinema-current-feasible-cpsat-20261024/manifest.json',HELPER,GOMP))\n    paths.update((ROOT/'artifacts/cinema-current-full-quality-frozen-v1.json',ROOT/'artifacts/cinema-current-full-quality-execution-v1.log',ROOT/'artifacts/cinema-current-full-quality-mechanical-v2.json'))"),
        ("    cubes={r:np.memmap", "    save(OUT/'process-affinity.json',{'prior_allowed_cpus':_prior_allowed,'allowed_cpus':_process.cpu_affinity(),'set_before_numpy_and_native_import':True,'per_tid_pin':False,'performance_calls':0})\n    cubes={r:np.memmap"),
        ("        cubes['candidate'].flush()", "        cubes['candidate'].flush()\n        if any(h.hexdigest()!=oracle_hash.hexdigest() for group in streams.values() for h in group.values()):raise AssertionError('全域checkpoint SHA不一致')\n        save(OUT/'full-checkpoint.json',{'candidate_oracle_sha256':oracle_hash.hexdigest(),'reference_payload_sha256':truth_hash.hexdigest(),'native_full_stream_sha256':{lib:{k:h.hexdigest() for k,h in values.items()} for lib,values in streams.items()},'cube':{r:metrics(h) for r,h in hists.items()},'full_native_configs':12,'mismatches':0,'scope':'完整分块流已完成；此时whole4T与照片尚未执行，不将请求4线程冒称实际4工作线程。'})"),
        ("            records=(Record*4)();code=fn(records,4,72,0,None)\n", "            records=(Record*4)();code=fn(records,4,72,0,None)\n            save(OUT/('team-attempt-%02d.json'%(len(snapshots)+1)),{'return_code':code,'action':0,'records':[{n:getattr(v,n) for n,_ in Record._fields_} for v in records]})\n")]
    for old,new in substitutions:
        if text.count(old)!=1:raise ValueError('机械替换的唯一位置不符：'+old[:70])
        text=text.replace(old,new)
    target.write_text(text,encoding='utf-8')
    audit=(ROOT/names[1]).read_text(encoding='utf-8')
    for old,new in (('cinema-current-full-quality-v1\'','cinema-current-full-quality-v2\''),('cinema-current-full-quality-frozen-v1.json','cinema-current-full-quality-frozen-v2.json')):
        if audit.count(old)!=1:raise ValueError('独立审计仅输出路径替换位置不符')
        audit=audit.replace(old,new)
    audit_target.write_text(audit,encoding='utf-8')
    plan=json.loads((ROOT/names[2]).read_text(encoding='utf-8'));plan['v2机械前置']={'allowed_cpus':[0,2,4,6],'set_before_numpy_native_import':True,'checkpoint_before_whole4t':True,'persist_every_helper_return_code':True,'模型DLL门阈值不变':True,'v1首次失败保留':True}
    plan_target.write_text(json.dumps(plan,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    original_plan=dict(plan);original_plan.pop('v2机械前置');assert original_plan==json.loads((ROOT/names[2]).read_text(encoding='utf-8'))
    record={'pass':True,'v1_frozen_sha256':sha(frozen_path),'v1_failed_log_sha256':sha(ROOT/'artifacts/cinema-current-full-quality-execution-v1.log'),
        'v1_source_sha256':{n:sha(ROOT/n) for n in names},'v2_generated_sha256':{p.relative_to(ROOT).as_posix():sha(p) for p in (target,audit_target,plan_target)},
        'generator_sha256':sha(__file__),'driver_exact_substitutions':len(substitutions),'model_library_thresholds_unchanged':True,
        'scope':'机械变动仅导入前进程0x55、日志checkpoint/原helper返回值和独立输出路径；不修改v1、模型或数学质量目标。'}
    proof.write_text(json.dumps(record,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    print({'pass':True,'generated_files':3,'proof_sha256':sha(proof)},flush=True)


if __name__=='__main__':main()
