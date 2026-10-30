"""质量成功后冻结289八角色正式性能，不执行计时。"""
import hashlib
import json
from pathlib import Path
import ast
ROOT = Path(__file__).resolve().parents[1]


def sha(path):
    with path.open('rb') as stream:
        return hashlib.file_digest(stream, 'sha256').hexdigest()


def main():
    path = ROOT / 'experiments/p16-direct-u10-perf-v1.json'
    if path.exists():
        raise ValueError('不覆盖正式性能协议')
    quality_path = ROOT / 'artifacts/p16-direct-u10-quality-v1/results.json'
    quality = json.loads(quality_path.read_text(encoding='utf-8'))
    if not quality['passed']:
        raise ValueError('必须先完整质量成功')
    source_names = ['scripts/run_direct_u10_perf.py', 'scripts/freeze_direct_u10_perf.py',
        'scripts/check_direct_u16_ilp_perf.py', 'scripts/check_direct_u10_perf.py',
        'scripts/prepare_direct_u10_perf_audit.py', 'scripts/run_direct_u16_ilp_perf.py',
        'scripts/run_velvia_bubble_perf.py', 'scripts/check_velvia_bubble_native.py',
        'scripts/check_direct_u10_native.py', 'scripts/check_direct_u16_ilp_native.py',
        'scripts/run_channel_tail_nodes.py', 'scripts/outplace_support.py', 'scripts/direct16_support.py',
        'scripts/suffix_cache_support.py', 'scripts/domain_cache_support.py', 'scripts/palette_support.py',
        'scripts/exception_support.py', 'python/lutlab/study_provenance.py',
        'experiments/channel-runtime/channel_native.py']
    for name in source_names:
        if name.endswith('.py'):
            ast.parse((ROOT / name).read_text(encoding='utf-8'))
    roles = ['87a399', '87old', '288old', '289old', '288max', '288p99', '289max', '289p99']
    comparisons = [['87old', '288old'], ['87old', '289old'], ['288old', '289old']]
    comparisons += [[base, role] for role in ('289max', '289p99') for base in ('87a399', '87old', '288old')]
    comparisons += [['288max', '289max'], ['288p99', '289p99'], ['87a399', '288max'], ['87a399', '288p99']]
    frozen = ROOT / 'artifacts/p16-direct-u10-quality-frozen-v1/frozen.json'
    plan = {'schema': 'p16_direct_u10_perf_v1', 'scope': '八角色同场289/288/87；保留全部控制失效与有效低50，禁止补测择样。',
        'workers': 4, 'threads': [1, 4], 'paths': ['inplace', 'to'], 'repeats_per_group': 5,
        'warmup_per_group': 1, 'roles': roles, 'group_order': [r + 'A' for r in roles] + [r + 'B' for r in reversed(roles)],
        'comparisons': comparisons, 'AA_time_ratio_bounds': [.85, 1.15],
        'AA_rule': '逐worker/scenario，双方全部metric的B/A闭区间有效，逐组五次中位数；无效不授档。',
        'speed_rule': '先组内五次中位数，跨两相位/四worker/1或4线程/原地pure及copy/分离总API取有效最劣倒数；100/90/80/70/60/50六档。',
        'no_obvious_time_ratio_cap': 1.1,
        'candidate_gate': '289两点分别对87a399/87old/288old全部AA通过且最劣至少50；289/288同模型仅本场，不能只换慢分母。',
        'prepare_scope': '八角色按roles顺序各构造一次并首批百图4线程原地；构造+首批仅描述，不称有AA或真正进程/文件缓存冷启动。',
        'allowed_logical_cpus': [0, 2, 4, 6], 'thread_pinning': False,
        'process_control': '每worker在加载数据/DLL之前设进程允许CPU集合0x55；不固定单个OMP TID、不锁频，不作与旧环境差异的因果结论。',
        'dataset': '固定100张已见1024×768 RGB8照片，共78,643,200像素；全部源和每组末实际输出SHA。',
        'ordering': '奇数worker逆序四场景；各场角色A正序、B逆序回文，warmup1+正式5，无后验重排。',
        'quality_frozen': frozen.relative_to(ROOT).as_posix(), 'quality_frozen_sha256': sha(frozen),
        'quality_result': quality_path.relative_to(ROOT).as_posix(), 'quality_result_sha256': sha(quality_path),
        'source_sha256': {name: sha(ROOT / name) for name in source_names},
        'memory': '8句柄同时驻留+百图source/work，另已有288/289六fresh RSS，不将性能组峰当单模型最小RAM。',
        'limits': '必须取得排他性能窗口；非官方Threshold/服务器/实板验证，无AVX512，不切默认。'}
    path.write_text(json.dumps(plan, ensure_ascii=False, indent=2) + '\n', encoding='utf-8', newline='\n')
    print(json.dumps({'plan_sha256': sha(path), 'roles': len(roles), 'comparisons': len(comparisons), 'performance_calls': 0}))


if __name__ == '__main__':
    main()
