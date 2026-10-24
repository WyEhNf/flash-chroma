"""先验证新2MiB缓存的域资格与实际容量；只读诊断，不执行像素或性能测试。"""
import os
os.environ.update(OMP_NUM_THREADS='4', OMP_DYNAMIC='FALSE', OMP_THREAD_LIMIT='4',
                  OMP_WAIT_POLICY='PASSIVE', OPENBLAS_NUM_THREADS='1', MKL_NUM_THREADS='1')
import argparse
import ctypes as ct
import hashlib
import json
from pathlib import Path
import sys
import psutil

psutil.Process().cpu_affinity([0, 2, 4, 6])
ROOT = Path(__file__).resolve().parents[1]
sys.path[:0] = [str(ROOT / 'scripts'), str(ROOT / 'experiments/channel-runtime')]
from channel_native import Library
from census_direct_gbank8 import WideInfo
from domain_cache_support import info as domain_info
from suffix_cache_support import cache_info
from palette_support import info as palette_info


def sha(path):
    with Path(path).open('rb') as stream:
        return hashlib.file_digest(stream, 'sha256').hexdigest()


def save(path, value):
    if path.exists():
        raise FileExistsError('不覆盖新资格诊断：' + str(path))
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--variant', choices=['u16', 'rgb24'], required=True)
    a = p.parse_args()
    name = a.variant + '-cache2'
    build = ROOT / f'artifacts/p16-direct-{name}-build-v1'
    out = ROOT / f'artifacts/p16-direct-{name}-observer-v1'
    if out.exists():
        raise FileExistsError('不覆盖已执行观察器')
    proof_path = build / 'build-check.json'
    proof = json.loads(proof_path.read_text(encoding='utf-8'))
    dll = build / ('libjshc_direct_' + a.variant + '_cache2.dll')
    assert proof['passed'] and sha(dll) == proof['dll_sha256']
    source_frozen = ROOT / f'artifacts/p16-direct-{name}-source-v1/frozen.json'
    generated_path = source_frozen.parent / 'generated.json'
    generated = json.loads(generated_path.read_text(encoding='utf-8'))
    for filename, row in generated['outputs'].items():
        assert sha(ROOT / f'experiments/p16-direct-{name}-runtime' / filename) == row['sha256']
    original = ROOT / 'artifacts/p16-direct-gbank8-census-v1/frozen.json'
    old = json.loads(original.read_text(encoding='utf-8'))
    old_plan = ROOT / 'artifacts/p16-direct-sentinel-perf-frozen-v1/plan.json'
    old_spec = json.loads(old_plan.read_text(encoding='utf-8'))['models']['old_best']
    models = {'max41': old['models']['max41'],
              'old_best': {k: old_spec[k] for k in ['models', 'sidecars']}}
    sources = [Path(__file__), ROOT / 'scripts/census_direct_gbank8.py',
               ROOT / 'scripts/domain_cache_support.py', ROOT / 'scripts/suffix_cache_support.py',
               ROOT / 'scripts/palette_support.py', ROOT / 'experiments/channel-runtime/channel_native.py',
               ROOT / 'experiments/p16-direct-cache2-plan-v1.md']
    identities = {str(v): sha(v) for spec in models.values() for v in spec['models'] + [v for v in spec['sidecars'] if v]}
    identities.update({str(v): sha(v) for v in [dll, proof_path, source_frozen, generated_path, original, old_plan]})
    save(out / 'protocol.json', {'purpose': __doc__, 'variant': a.variant,
         'sources_sha256': {v.relative_to(ROOT).as_posix(): sha(v) for v in sources},
         'inputs_sha256': identities, 'models': models, 'cpus': psutil.Process().cpu_affinity(),
         'pixel_apply_calls': 0, 'performance_calls': 0})
    directories = [os.add_dll_directory('E:/mingw64/bin'), os.add_dll_directory(str(build))]
    library = Library(str(dll), proof['dll_sha256'])
    assert library.revision == (293 if a.variant == 'u16' else 294)
    rows = {}
    for model, spec in models.items():
        with library.chain(spec['models'], spec['sidecars']) as chain:
            function = getattr(library.dll, 'p16_cc_get_direct_' + a.variant + '_info')
            function.argtypes = [ct.c_void_p, ct.POINTER(WideInfo), ct.c_size_t]
            function.restype = ct.c_int
            wide = WideInfo()
            assert ct.sizeof(wide) == 96 and function(chain.handle, ct.byref(wide), 96) == 0
            rows[model] = {'cache': cache_info(chain), 'domain': domain_info(chain),
                           'palette': palette_info(chain),
                           'wide': {k: getattr(wide, k) for k, _ in WideInfo._fields_},
                           'model_bytes': chain.model_bytes}
    c, d, w = rows['max41']['cache'], rows['max41']['domain'], rows['max41']['wide']
    eligible = bool(c['enabled'] and c['reason'] == 0 and c['entries'] == 264222
                    and c['table_capacity_bytes'] == 1056888 and d['eligible']
                    and d['fast_path_enabled'] and d['unproven_cells'] == 0 and w['enabled'])
    old_ok = bool(rows['old_best']['cache']['enabled'] and rows['old_best']['domain']['eligible']
                  and rows['old_best']['palette']['enabled'])
    result = {'passed': eligible and old_ok, 'max41_eligible': eligible, 'old_best_priority_preserved': old_ok,
              'variant': a.variant, 'dll_sha256': proof['dll_sha256'], 'models': rows,
              'pixel_apply_calls': 0, 'performance_calls': 0,
              'limitations': '只验证新缓存/域/直接表示的native资格，不替代完整输出或速度；未作分配失败注入'}
    for filename, expected in identities.items():
        assert sha(filename) == expected, filename
    save(out / 'results.json', result)
    print(json.dumps(result, ensure_ascii=False))
    assert result['passed'], '新缓存/域/表示前置未通过，后续停止'


if __name__ == '__main__':
    main()
