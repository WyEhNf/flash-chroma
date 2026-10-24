"""293/294仅预算放宽后的新增质量：max41及best，全域、物理表、整幅四线程与百图；不计时。"""
import os
os.environ.update(OMP_NUM_THREADS='4', OMP_DYNAMIC='FALSE', OMP_THREAD_LIMIT='4',
                  OMP_WAIT_POLICY='PASSIVE', OPENBLAS_NUM_THREADS='1', MKL_NUM_THREADS='1')
import psutil
psutil.Process().cpu_affinity([0, 2, 4, 6])
import argparse
from contextlib import ExitStack
import ctypes as ct
import hashlib
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
ORIGINAL = Path('F:/Hackathon/projects/16-lut-color')
sys.path[:0] = [str(ROOT / 'python'), str(ROOT / 'scripts'), str(ROOT / 'experiments/channel-runtime')]
import numpy as np
from channel_native import Library
from census_direct_gbank8 import WideInfo
from suffix_cache_support import cache_info
from domain_cache_support import info as domain_info
from palette_support import info as palette_info
from direct16_support import info as direct_info, table as direct_table
from outplace_support import bind_to, apply_to, reject_to
from check_omp_affinity_control_v2 import Record
from lutlab.study_provenance import environment_fingerprint
from build_direct_cache2 import sha, save

FROZEN = ROOT / 'artifacts/p16-direct-cache2-quality-frozen-v1'
OUT = ROOT / 'artifacts/p16-direct-cache2-quality-v1'
HELPER = ROOT / 'artifacts/p16-omp-affinity-control-build-v2/libp16_omp_affinity.dll'
HELPER_SHA = 'fbf717dd92e0f38e93394c88255ca9a36f9fab48ef30878b0200f9f4c4a0901f'
GOMP = Path('E:/mingw64/bin/libgomp-1.dll')
GOMP_SHA = 'fc7569276d33d23f55f143eb6723821ef2633c96cbb381c0f507b793d9585e88'
RAW = ORIGINAL / 'artifacts/skylake-server-matrix-v1/server-inputs/photos.rgb'
RAW_SHA = 'e13278cfc91c3411b3c242232239f9ea6fbda3bf5d18c3f17c41a4dedf57defd'


def wide_info(chain, variant):
    f = getattr(chain.library.dll, 'p16_cc_get_direct_' + variant + '_info')
    f.argtypes = [ct.c_void_p, ct.POINTER(WideInfo), ct.c_size_t]
    f.restype = ct.c_int
    value = WideInfo()
    assert ct.sizeof(value) == 96 and f(chain.handle, ct.byref(value), 96) == 0
    return {name: getattr(value, name) for name, _ in WideInfo._fields_}


def to(chain, source, kernel, threads):
    target = np.empty_like(source)
    u8 = ct.POINTER(ct.c_uint8)
    error = ct.create_string_buffer(1024)
    result = bind_to(chain.library.dll)(chain.handle, source.ctypes.data_as(u8), target.ctypes.data_as(u8),
                                       source.nbytes, int(kernel == 'avx2'), threads, error, len(error))
    if result:
        raise RuntimeError(error.value.decode('utf-8', 'replace'))
    return target


def freeze():
    if FROZEN.exists():
        raise FileExistsError('不覆盖质量冻结')
    primary = ROOT / 'artifacts/cinema-current-full-quality-v2'
    identity_path = primary / 'identity.json'
    identity = json.loads(identity_path.read_text(encoding='utf-8'))
    current_results = json.loads((primary / 'results.json').read_text(encoding='utf-8'))
    assert current_results['mismatches'] == 0
    models = {'max41': dict(identity['roles']['candidate']), 'old_best': dict(identity['roles']['best'])}
    models['max41'].update(oracle=str(primary / 'candidate.rgb'),
                          oracle_sha256='728666cbc05f0cd2d9da112ce41a26117d67baee1511760d83df8f8cefe8ed98')
    sources = {}
    prior = ROOT / 'artifacts/p16-direct-rgb24-full-mt-frozen-v1/frozen.json'
    sources.update(json.loads(prior.read_text(encoding='utf-8'))['sources_sha256'])
    libraries, inputs = {}, {str(v): sha(v) for v in [identity_path, primary / 'results.json', prior,
         ROOT / 'artifacts/p16-direct-rgb24-quality-v1/results.json', ORIGINAL / 'assets/photos/manifest.json']}
    for variant in ('u16', 'rgb24'):
        name = variant + '-cache2' if variant == 'u16' else 'rgb24-cache2-v2'
        build = ROOT / f'artifacts/p16-direct-{name}-build-v1'
        build_proof = build / 'build-check.json'
        proof = json.loads(build_proof.read_text(encoding='utf-8'))
        bf = ROOT / f'artifacts/p16-direct-{name}-build-frozen-v1/frozen.json'
        assert proof['passed'] and sha(bf) == proof['frozen_sha256']
        sources.update({k: v['sha256'] for k, v in json.loads(bf.read_text(encoding='utf-8'))['sources'].items()})
        observer = ROOT / f'artifacts/p16-direct-{name}-observer-v1/results.json'
        contracts = ROOT / f'artifacts/p16-direct-{name}-contracts-v1/results.json'
        assert json.loads(observer.read_text(encoding='utf-8'))['passed']
        assert json.loads(contracts.read_text(encoding='utf-8'))['passed']
        dll = build / ('libjshc_direct_' + variant + '_cache2.dll')
        assert sha(dll) == proof['dll_sha256']
        libraries[variant] = {'path': str(dll), 'sha256': proof['dll_sha256'], 'revision': 293 if variant == 'u16' else 294}
        inputs.update({str(v): sha(v) for v in [bf, build_proof, observer, contracts, dll]})
    for filename in ['check_direct_cache2_quality.py', 'audit_direct_cache2_quality.py', 'build_direct_cache2.py', 'generate_direct_cache2.py',
                     'observe_direct_cache2.py', 'check_direct_cache2_contracts.py', 'census_direct_gbank8.py',
                     'prepare_direct_cache2_cmake_v2.py', 'build_direct_cache2_cmake_v2.py',
                     'observe_direct_cache2_cmake_v2.py', 'check_direct_cache2_contracts_cmake_v2.py']:
        sources['scripts/' + filename] = sha(ROOT / 'scripts' / filename)
    sources['experiments/p16-direct-cache2-plan-v1.md'] = sha(ROOT / 'experiments/p16-direct-cache2-plan-v1.md')
    for path in [RAW, HELPER, GOMP]:
        inputs[str(path)] = sha(path)
    assert inputs[str(RAW)] == RAW_SHA and RAW.stat().st_size == 235929600
    assert inputs[str(HELPER)] == HELPER_SHA and inputs[str(GOMP)] == GOMP_SHA
    for model in models.values():
        assert sha(model['oracle']) == model['oracle_sha256']
        for path in model['models'] + [v for v in model['sidecars'] if v] + [model['oracle']]:
            inputs[str(path)] = sha(path)
    for filename, expected in sources.items():
        assert sha(ROOT / filename) == expected, filename
        copy = FROZEN / 'sources' / filename
        copy.parent.mkdir(parents=True, exist_ok=True)
        copy.write_bytes((ROOT / filename).read_bytes())
    save(FROZEN / 'frozen.json', {'purpose': __doc__, 'sources_sha256': sources, 'inputs_sha256': inputs,
         'models': models, 'libraries': libraries, 'environment': environment_fingerprint(),
         'full_streams_expected': 24, 'whole4t_streams_expected': 8, 'whole4t_snapshots_expected': 16,
         'photo_comparisons_expected': 800, 'short_pattern_backend_cases_expected': 972,
         'allocation_failure_injection': False, 'no_avx2_injection': False, 'performance_calls': 0})
    print(json.dumps({'sources': len(sources), 'inputs': len(inputs),
                      'frozen_sha256': sha(FROZEN / 'frozen.json'), 'performance_calls': 0}, ensure_ascii=False))


def verify(frozen):
    for filename, expected in frozen['sources_sha256'].items():
        assert sha(ROOT / filename) == expected, filename
    for filename, expected in frozen['inputs_sha256'].items():
        assert sha(filename) == expected, filename


def validate():
    if OUT.exists():
        raise FileExistsError('不覆盖新质量运行')
    frozen = json.loads((FROZEN / 'frozen.json').read_text(encoding='utf-8'))
    verify(frozen)
    OUT.mkdir(parents=True)
    save(OUT / 'start.json', {'frozen_sha256': sha(FROZEN / 'frozen.json'),
                             'affinity_before_native': psutil.Process().cpu_affinity(), 'performance_calls': 0})
    directories = [os.add_dll_directory('E:/mingw64/bin'), os.add_dll_directory(str(HELPER.parent))]
    directories += [os.add_dll_directory(str(Path(v['path']).parent)) for v in frozen['libraries'].values()]
    helper = ct.CDLL(str(HELPER))
    fn = helper.p16_omp_affinity
    fn.argtypes = [ct.POINTER(Record), ct.c_size_t, ct.c_size_t, ct.c_uint32, ct.POINTER(Record)]
    fn.restype = ct.c_int
    teams = []

    def snapshot():
        values = (Record * 4)()
        code = fn(values, 4, 72, 0, None)
        row = {'returncode': code, 'action': 0, 'members': [{k: getattr(v, k) for k, _ in Record._fields_} for v in values]}
        teams.append(row)
        save(OUT / f'team-{len(teams):02d}.json', row)
        assert code == 0 and all(v.version == 1 and v.team_size == 4 and v.omp_tid == i and not v.set_attempted
                                 and v.query_before_ok and v.query_after_ok and v.mask_before == 0x55
                                 and v.mask_after == 0x55 and v.cpu_before in (0, 2, 4, 6)
                                 and v.cpu_after in (0, 2, 4, 6) for i, v in enumerate(values))
        tids = [v.os_tid for v in values]
        assert len(set(tids)) == 4
        return tids

    libraries = {k: Library(v['path'], v['sha256']) for k, v in frozen['libraries'].items()}
    assert all(libraries[k].revision == v['revision'] for k, v in frozen['libraries'].items())
    refs = {k: np.memmap(v['oracle'], np.uint8, 'r', shape=(2**24, 3)) for k, v in frozen['models'].items()}
    result = {'frozen_sha256': sha(FROZEN / 'frozen.json'), 'environment': environment_fingerprint(),
              'capacity': {}, 'physical': [], 'full_streams': [], 'whole4t_streams': [],
              'photos': [], 'rejections': {}, 'performance_calls': 0}
    with ExitStack() as stack:
        chains = {(variant, model): stack.enter_context(library.chain(spec['models'], spec['sidecars']))
                  for variant, library in libraries.items() for model, spec in frozen['models'].items()}
        for (variant, model), chain in chains.items():
            wide = wide_info(chain, variant)
            state = {'wide': wide, 'cache': cache_info(chain), 'domain': domain_info(chain),
                     'palette': palette_info(chain), 'direct': direct_info(chain), 'model_bytes': chain.model_bytes}
            result['capacity'][variant + '_' + model] = state
            assert state['cache']['enabled'] and state['domain']['eligible'] and not state['domain']['unproven_cells']
            if model == 'old_best':
                assert not wide['enabled'] and state['palette']['enabled'] and state['direct']['format'] == 9
                continue
            assert wide['enabled'] and wide['guard_bytes'] == 4
            assert wide['format'] == (16 if variant == 'u16' else 18)
            raw = direct_table(chain)
            if variant == 'u16':
                ids = raw.view('<u2')
                assert len(ids) == 2**24 + 2 and np.all(ids[-2:] == 0)
                colors = np.empty(wide['palette_size'], np.uint32)
                f = chain.library.dll.p16_cc_copy_u16_palette
                f.argtypes = [ct.c_void_p, ct.POINTER(ct.c_uint32), ct.c_size_t]
                f.restype = ct.c_int
                assert f(chain.handle, colors.ctypes.data_as(ct.POINTER(ct.c_uint32)), len(colors)) == 0
                assert colors.size >= 256 and np.all(colors[1:] > colors[:-1]) and np.max(ids[:-2]) < colors.size
            else:
                data = raw.view(np.uint8)
                assert len(data) == 3*2**24 + 4 and np.all(data[-4:] == 0)
            for blue in range(256):
                code = np.arange(blue*65536, (blue+1)*65536, dtype=np.uint32)
                oracle_keys = ((code & 255) << 16) | (code & 0xff00) | blue
                if variant == 'u16':
                    words = colors[ids[code]]
                    actual = np.column_stack((words & 255, (words >> 8) & 255, words >> 16)).astype(np.uint8)
                else:
                    actual = data[:-4].reshape(-1, 3)[code]
                np.testing.assert_array_equal(actual, refs[model][oracle_keys])
            result['physical'].append({'variant': variant, 'model': model, 'raw_sha256': hashlib.sha256(raw).hexdigest(),
                                       'entries': 2**24, 'all_values_equal_to_integer_oracle': True, 'guard_zero': True})
            del raw
            if variant == 'u16':
                del ids, colors
            else:
                del data
        save(OUT / 'tables.json', result)
        hashes = {(v, m, k, p): hashlib.sha256() for v, m in chains for k in ['scalar', 'avx2'] for p in ['inplace', 'to']}
        for begin in range(0, 2**24, 65536):
            keys = np.arange(begin, begin+65536, dtype=np.uint32)
            source = np.column_stack((keys >> 16, (keys >> 8) & 255, keys & 255)).astype(np.uint8)
            for (variant, model), chain in chains.items():
                expected = refs[model][keys]
                for kernel in ['scalar', 'avx2']:
                    for route in ['inplace', 'to']:
                        actual = chain.apply(source.copy(), kernel=kernel, threads=1) if route == 'inplace' else to(chain, source, kernel, 1)
                        np.testing.assert_array_equal(actual, expected)
                        hashes[variant, model, kernel, route].update(actual)
        result['full_streams'] = [{'variant': v, 'model': m, 'kernel': k, 'threads': 1, 'path': p,
                                  'sha256': h.hexdigest(), 'mismatches': 0} for (v, m, k, p), h in hashes.items()]
        assert len(result['full_streams']) == 16
        for row in result['full_streams']:
            assert row['sha256'] == frozen['models'][row['model']]['oracle_sha256']
        save(OUT / 'single-thread-full.json', result)
        source = np.empty((2**24, 3), np.uint8)
        for begin in range(0, 2**24, 262144):
            codes = np.arange(begin, begin+262144, dtype=np.uint32)
            source[begin:begin+262144] = np.column_stack((codes >> 16, (codes >> 8) & 255, codes & 255)).astype(np.uint8)
        source_sha = hashlib.sha256(source).hexdigest()
        for (variant, model), chain in chains.items():
            for route in ['inplace', 'to']:
                before = snapshot()
                actual = chain.apply(source.copy(), kernel='avx2', threads=4) if route == 'inplace' else to(chain, source, 'avx2', 4)
                after = snapshot()
                assert before == after
                digest = hashlib.sha256(actual).hexdigest()
                assert digest == frozen['models'][model]['oracle_sha256']
                np.testing.assert_array_equal(actual, refs[model])
                assert hashlib.sha256(source).hexdigest() == source_sha
                result['whole4t_streams'].append({'variant': variant, 'model': model, 'path': route,
                     'pixels': 2**24, 'blocks': 256, 'surrounding_team_os_tids': before, 'sha256': digest, 'mismatches': 0})
        del source, actual
        save(OUT / 'whole4t-full.json', result)
        photos = np.memmap(RAW, np.uint8, 'r', shape=(100, 786432, 3))
        for image in range(100):
            source = photos[image]
            keys = source.astype(np.uint32) @ np.array([65536, 256, 1], np.uint32)
            for (variant, model), chain in chains.items():
                for route in ['inplace', 'to']:
                    actual = chain.apply(source.copy(), kernel='avx2', threads=4) if route == 'inplace' else to(chain, source, 'avx2', 4)
                    np.testing.assert_array_equal(actual, refs[model][keys])
                    result['photos'].append({'image_index': image, 'variant': variant, 'model': model, 'path': route,
                                             'sha256': hashlib.sha256(actual).hexdigest(), 'mismatches': 0})
        save(OUT / 'photos.json', result)
        short = 0
        rng = np.random.default_rng(2026102418)
        for (variant, model), chain in chains.items():
            for length in [*range(18), 31, 32, 33, 4095, 4096, 4097, 65535, 65536, 65537]:
                for pattern in ['random', 'white', 'mixed']:
                    source = np.full((length, 3), 255, np.uint8) if pattern == 'white' else rng.integers(0, 256, (length, 3), dtype=np.uint8)
                    if pattern == 'mixed':
                        source[::7] = 255
                    keys = source.astype(np.uint32) @ np.array([65536, 256, 1], np.uint32)
                    expected = refs[model][keys]
                    for kernel, threads in [('scalar', 1), ('avx2', 1), ('avx2', 4)]:
                        np.testing.assert_array_equal(chain.apply(source.copy(), kernel=kernel, threads=threads), expected)
                        for same in [False, True]:
                            assert apply_to(chain.library.dll, chain.handle, source.tobytes(), int(kernel == 'avx2'), threads,
                                            source_offset=1, target_offset=3, same=same) == expected.tobytes()
                        short += 1
            result['rejections'][variant + '_' + model] = reject_to(chain.library.dll, chain.handle)
        assert short == 972 and len(result['photos']) == 800 and len(result['whole4t_streams']) == 8 and len(teams) == 16
        result['short_pattern_backend_cases'] = short
    modules = {str(Path(v.path).resolve()) for v in psutil.Process().memory_maps() if Path(v.path).name.lower() == 'libgomp-1.dll'}
    assert len(modules) == 1 and next(iter(modules)).casefold() == str(GOMP.resolve()).casefold()
    result.update(passed=True, read_only_team_snapshots=teams, unique_libgomp=sorted(modules), full_stream_count=24,
                  photo_comparisons=800, short_native_output_comparisons=3*972,
                  limitations='只认293/294的max41及best新增正确性，不授速度档；4T前后同pool观察，未在native逐块插桩；未注入bad_alloc或无AVX2。')
    verify(frozen)
    save(OUT / 'results.json', result)
    print(json.dumps({'passed': True, 'full_streams': 24, 'whole4t': 8, 'team_snapshots': 16,
                      'photo_comparisons': 800, 'short_pattern_backend_cases': short, 'performance_calls': 0}, ensure_ascii=False))


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--freeze', action='store_true')
    args = parser.parse_args()
    freeze() if args.freeze else validate()
