"""100独立生产/有限合同构建前冻结，不构建或执行native。"""
import hashlib
import json
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
TARGET=ROOT/'experiments/p16-scanline-prepare-static-v1.json'
if TARGET.exists():raise FileExistsError('100静态冻结不覆盖')
sha=lambda path:hashlib.sha256(path.read_bytes()).hexdigest()
sources=[p for p in sorted((ROOT/'experiments/p16-scanline-prepare-runtime').rglob('*')) if p.is_file()]
sources += [p for p in sorted((ROOT/'experiments/p16-scanline-prepare-draft').rglob('*')) if p.is_file()]
sources += [Path(__file__),ROOT/'scripts/generate_p16_scanline_prepare.py',ROOT/'scripts/build_p16_scanline_prepare.py',
    ROOT/'scripts/run_p16_scanline_finite.py',ROOT/'scripts/audit_p16_scanline_assembly.py',ROOT/'experiments/p16-scanline-prepare-有限预注册.md']
prior=ROOT/'experiments/p16-shared-proven-static-v1.json'
old=json.loads(prior.read_text(encoding='utf-8'))
for row in old['sources']:
    path=Path(row['path']);assert sha(path)==row['sha256'];sources.append(path)
sources.append(prior)
unique={str(path):path for path in sources}
plan={'purpose':'100固定枚举scanline准备器唯一构建与有限native合同','parent_revision':97,'candidate_revision':100,
    'sources':[{'path':str(path),'sha256':sha(path)} for path in sorted(unique.values())],
    'old_static_freeze_sha256':sha(prior),'abi_changes':0,'handle_members_added':0,
    'finite_expected':{'views':12,'full_batches':36,'fallback_batches':96,'candidate_calls':792,'old97_calls':132,
        'native_calls':924,'oracle_pixels':2363136,'old97_pixels':2363136,'candidate_pixels':14178816,
        'canary_cases':924,'readonly_checks':924,'axis_mod32_four_cases':108},
    'native_quality_calls':0,'full_chain_calls':0,'photo_calls':0,'performance_calls':0,
    'resource_bound':{'single_case_estimated_working_set_less_than_bytes':2097152,'conservative_new_memory_less_than_bytes':8388608,
        'measured_rss':False},
    'scope':'构建完成先报告八旧对象/汇编/栈，再按此版一次finite；不含完整链/照片/性能，首错STOP。'}
TARGET.write_text(json.dumps(plan,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print(json.dumps({'plan_sha256':sha(TARGET),'sources':len(plan['sources']),'native_quality_calls':0,'performance_calls':0},ensure_ascii=False))
