"""101构建前单版闭包；native有限合同必须等实库复核后另grant。"""
import hashlib
import json
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
TARGET=ROOT/'experiments/p16-early-index-static-v1.json'
if TARGET.exists():raise FileExistsError('101静态冻结不覆盖')
sha=lambda path:hashlib.sha256(path.read_bytes()).hexdigest()
sources=[p for p in sorted((ROOT/'experiments/p16-early-index-runtime').rglob('*')) if p.is_file()]
sources+=[p for p in sorted((ROOT/'experiments/p16-early-index-draft').rglob('*')) if p.is_file()]
sources+=[Path(__file__),ROOT/'scripts/generate_p16_early_index.py',ROOT/'scripts/build_p16_early_index.py',
    ROOT/'scripts/audit_p16_early_index_assembly.py',ROOT/'scripts/run_p16_early_index_finite.py',ROOT/'experiments/p16-early-index-有限预注册.md']
prior=ROOT/'experiments/p16-scanline-prepare-static-v1.json'
assert sha(prior)=='e7c2366010e1b9876f1a386c8405568eea853f81bbdcbb7d7d54fb574439793f'
parent=json.loads(prior.read_text(encoding='utf-8'))
for entry in parent['sources']:
    path=Path(entry['path']);assert sha(path)==entry['sha256'];sources.append(path)
sources.append(prior);unique={str(path):path for path in sources}
plan={'purpose':'101精确索引展开/早channel消费唯一构建及待授权有限合同','parent_revision':100,'candidate_revision':101,
    'sources':[{'path':str(path),'sha256':sha(path)} for path in sorted(unique.values())],
    'parent_static_freeze_sha256':sha(prior),'abi_changes':0,'handle_members_added':0,
    'finite_expected':{'views':20,'full_batches':60,'fallback_batches':160,'candidate_calls':1320,'old100_calls':220,
        'native_calls':1540,'oracle_pixels':3938560,'old100_pixels':3938560,'candidate_pixels':23631360,
        'canary_cases':1540,'readonly_checks':1540,'axis_mod32_four_cases':180,'pure_address_cases':93312,
        'legal_extreme_views':8,'negative_alpha_views':6,'positive_beta_views':2,'zero_beta_views':2},
    'derived_prepare_entry_count_including_fallback_nesting':3620,
    'native_executions_at_freeze':0,'full_chain_calls':0,'photo_calls':0,'performance_calls':0,
    'resource_bound':{'estimated_new_peak_less_than_bytes':16777216,'measured_rss':False},
    'scope':'先唯一-j1构建并核9旧对象/5-9gather/实际frame，报告root；尚无私有native/完整链/照片/性能执行grant。'}
TARGET.write_text(json.dumps(plan,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print(json.dumps({'plan_sha256':sha(TARGET),'sources':len(plan['sources']),'finite_expected':plan['finite_expected'],'native_executions':0},ensure_ascii=False))
