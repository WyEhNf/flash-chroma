"""99唯一纯整数合同执行前闭包，不覆盖计划，不执行合同。"""
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
TARGET = ROOT/'experiments/p16-b2-packed-axis-contract-v1.json'
if TARGET.exists():
    raise FileExistsError('99冻结计划不覆盖')
sha = lambda path: hashlib.sha256(path.read_bytes()).hexdigest()
prior = json.loads((ROOT/'experiments/p16-node-tiling-census-v1.json').read_text(encoding='utf-8'))
models = {}
for row in prior['models']:
    assert sha(Path(row['path'])) == row['sha256']
    models['ordinary' if row['m'] == 33 else 'm'+str(row['m'])] = row
source_paths = [Path(__file__), ROOT/'scripts/contract_p16_b2_packed_axis.py',
    ROOT/'experiments/p16-b2-packed-axis-预注册.md',
    ROOT/'experiments/skylake-domain-isolated-runtime/channel_avx2.cpp',
    ROOT/'experiments/p16-shared-proven-runtime/compile_shared_avx2.cpp']
plan = {'purpose': '99唯一packed-axis B2符号/有限合同，native/performance均为0',
    'script_sha256': sha(ROOT/'scripts/contract_p16_b2_packed_axis.py'), 'models': models,
    'sources': [{'path': str(path), 'sha256': sha(path)} for path in source_paths],
    'fixed': {'m': 33, 'B': 2, 'T': 17, 'F': 65536, 'all_cells': 32768,
        'old_orders': 6, 'symbolic_representatives': [0, 1, 2, 3, 65536],
        'no_alternative_idx_variant': True, 'minimum_new_payload': 160320},
    'forbidden': ['gold', '照片', '16M颜色输出', '拟合', 'nativebuild', '原生库加载', '性能', '正式版本择优']}
TARGET.write_text(json.dumps(plan, ensure_ascii=False, indent=2)+'\n', encoding='utf-8')
print(json.dumps({'plan_sha256': sha(TARGET), 'script_sha256': plan['script_sha256'],
    'source_files': len(source_paths)}, ensure_ascii=False))
