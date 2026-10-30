"""独立三分母质量资格：四级oracle、24原生配置、四模型100逐图；不拟合或计时。"""
from __future__ import annotations
import argparse
import ctypes as ct
import hashlib
import json
import math
import os
from pathlib import Path
import sys
from contextlib import ExitStack
ROOT = Path(__file__).resolve().parents[1]
sys.path[:0] = [str(ROOT/'python'), str(ROOT/'experiments/channel-runtime')]
import numba
import numpy as np
from PIL import Image
from lutlab import channel_coordinates as cc, channel_hotspot_support as hs, io, study_provenance
from channel_native import Library
from run_channel_tail_nodes import digest, load_model, save
from verify_channel_coordinates import integer_oracle
from outplace_support import bind_to
from suffix_cache_support import cache_info
from domain_cache_support import info as domain_info
from direct16_support import info as direct_info
from palette_support import info as palette_info

TOTAL = 1 << 24
SIZE = 3*255**2+1
METRICS = ('mean', 'rms', 'p99', 'max', 'cvar_1pct')
TIERS = (100, 90, 80, 70, 60, 50)
THRESHOLDS = (4, 5, 6, 7, 7.5, 7.7, 8, 8.2)


def histogram(predicted, reference):
    delta = predicted.astype(np.int32)-reference.astype(np.int32)
    return np.bincount(np.sum(delta*delta, axis=1, dtype=np.int32), minlength=SIZE)


def metrics(hist):
    end = int(np.flatnonzero(hist)[-1])+1
    result = hs.metrics(hist[:end]); result['max'] = math.sqrt(result['max_squared'])
    return result


def retain(old, new):
    if new == 0: return 100.0
    if old == 0: return 0.0
    return min(100.0, old/new*100)


def compare(before, after):
    ratios = {name: retain(before[name], after[name]) for name in METRICS}
    return {'metrics': {name: {'before': before[name], 'after': after[name], 'retained_percent': ratios[name],
        'change': '平' if abs(after[name]-before[name]) <= 1e-12 else '好' if after[name] < before[name] else '差'} for name in METRICS},
        'minimum_retained_percent': min(ratios.values()), 'tiers_pass': {str(t): min(ratios.values())+1e-12 >= t for t in TIERS}}


def actual_to(function, chain, source, kernel, threads):
    before = source.copy(); target = np.empty_like(source); error = ct.create_string_buffer(1024); u8 = ct.POINTER(ct.c_uint8)
    if np.shares_memory(target, source): raise AssertionError('真正分离输出发生别名')
    if function(chain.handle, source.ctypes.data_as(u8), target.ctypes.data_as(u8), source.nbytes,
            int(kernel == 'avx2'), threads, error, len(error)):
        raise RuntimeError(error.value.decode('utf-8', 'replace'))
    np.testing.assert_array_equal(source, before)
    return target


def definitions(cache, plan):
    suffix = cache/'artifacts/cinema-envelope-v1/stage4_sweep004'
    folders = {'a399': cache/'artifacts/cinema-current-anchor-accept-v1',
        'best': ROOT/'artifacts/cinema-arrival-last-budget-v1/candidate',
        'max_first': ROOT/'artifacts/cinema-second-nodes-v1/max_first/candidate',
        'candidate': ROOT/plan['候选']['directory']}
    roles = {}
    oracle_paths = {'a399': cache/'artifacts/cinema-current-anchor-accept-v1/cube.rgb',
        'best': ROOT/'artifacts/cinema-arrival-budget-accept-v1/candidate.rgb',
        'max_first': ROOT/'artifacts/cinema-second-accept-max_first-v1/candidate.rgb'}
    expected = {'a399': plan['三个固定分母']['a399']['cube_sha256'], 'best': plan['三个固定分母']['综合best']['cube_sha256'],
        'max_first': plan['三个固定分母']['max_first']['cube_sha256']}
    for role, folder in folders.items():
        models = [folder/'candidate-base.slut', (folder/'stage2.slut' if role in ('candidate', 'max_first') else suffix/'selected-stage2.slut'),
            suffix/'selected-stage3.slut', folder/'stage4.slut' if role != 'a399' else suffix/'selected-stage4.slut']
        side = folder/'channel-frac.bin'
        roles[role] = {'models': models, 'sidecars': [side, None, None, None],
            'input_sha256': {str(p.resolve()): digest(p) for p in [*models, side]}}
        if role != 'candidate':
            if digest(oracle_paths[role]) != expected[role]: raise ValueError('固定分母完整流身份已变：'+role)
            roles[role].update(oracle=oracle_paths[role], oracle_sha256=expected[role])
    candidate = folders['candidate']; fixed = plan['候选']
    for file, name in (('model.npz', 'model_npz_sha256'), ('candidate-base.slut', 'first_slut_sha256'),
            ('channel-frac.bin', 'sidecar_sha256'), ('stage2.slut', 'stage2_sha256'), ('stage4.slut', 'stage4_sha256')):
        if digest(candidate/file) != fixed[name]: raise ValueError('max48固定候选文件已变：'+file)
    if digest(suffix/'selected-stage3.slut') != fixed['stage3_sha256']: raise ValueError('固定第三级已变')
    return roles


def main():
    p = argparse.ArgumentParser(description=__doc__); p.add_argument('--cache-root', type=Path, required=True)
    p.add_argument('--library', type=Path, required=True); p.add_argument('--frozen', type=Path, required=True)
    p.add_argument('--output', type=Path, required=True); args = p.parse_args()
    if args.output.exists(): raise ValueError('不覆盖三分母独立质量资格')
    frozen = json.loads(args.frozen.read_text(encoding='utf-8'))
    if not frozen['ast_pass']: raise ValueError('执行前AST未通过')
    for name, expected in frozen['source_sha256'].items():
        if digest(ROOT/name) != expected: raise ValueError('执行前全源已变：'+name)
    for name, expected in frozen['input_sha256'].items():
        if digest(name) != expected: raise ValueError('执行前固定输入已变：'+name)
    plan_path = ROOT/'experiments/p16-cinema-max48-pareto-quality-v1.json'
    plan = json.loads(plan_path.read_text(encoding='utf-8')); cache = args.cache_root.resolve()
    if digest(args.library) != '58591a725d367dce3713ff88af4d5549afea5af1ac4f3a39284443586893c158': raise ValueError('不是冻结87库')
    numba.set_num_threads(4); roles = definitions(cache, plan); candidate_folder = ROOT/plan['候选']['directory']
    raw_plan = json.loads((ROOT/'experiments/cinema-current-anchor-v1.json').read_text(encoding='utf-8'))
    tables = []
    for spec in raw_plan['tables']:
        path = cache/spec['path']
        if digest(path) != spec['sha256']: raise ValueError('独立四原始表已变')
        tables.append(io.load_full(path, mmap=True).reshape(-1, 3))
    reference_path = cache/'artifacts/cinema-axis-calibration-v1/envelope-reference.npy'
    if digest(reference_path) != 'ec79ca618022293b2d2f5c832f1a8647c88e4994ce820664310e09c0f4bf5690': raise ValueError('全域gold已变')
    reference = np.load(reference_path, mmap_mode='r')
    manifest_path = cache/'assets/photos/manifest.json'; partition_path = cache/'artifacts/full-photo-v1/photo-partition.json'
    if digest(manifest_path) != '10893812e0d3cecea7ba8b6bbf4700addd09927feed220149501def03c374f7c' or digest(partition_path) != 'e9833fc552619d36d9dae8920e2297db37ff4235aae805346c09aa50b7247c50':
        raise ValueError('100图或原60划分已变')
    manifest = json.loads(manifest_path.read_text(encoding='utf-8'))
    training_ids = {row['id'] for row in json.loads(partition_path.read_text(encoding='utf-8'))['training']['images']}
    if len(manifest['images']) != 100 or len(training_ids) != 60: raise ValueError('照片划分不是100/60')
    args.output.mkdir(parents=True)
    first = load_model(candidate_folder/'model.npz'); suffix_models = [cc.from_sparse(io.load_sparse(path, competition=True)) for path in roles['candidate']['models'][1:]]
    models = [first, *suffix_models]
    first_keys, first_frames = {}, {}
    for role, spec in roles.items():
        key = digest(spec['models'][0])+':'+digest(spec['sidecars'][0]); first_keys[role] = key
        if key not in first_frames:
            base = cc.from_sparse(io.load_sparse(spec['models'][0], competition=True))
            frac = np.fromfile(spec['sidecars'][0], dtype='<u4').reshape(3, 3, 256)
            frame = cc.ChannelLut(base.grid, base.nodes, base.idx, frac); cc.validate(frame)
            first_frames[key] = frame
    # SLUT的grid按协议写float32；执行Q16基使用idx/frac，逐项核实际序列化值。
    np.testing.assert_array_equal(first_frames[first_keys['candidate']].grid, first.grid.astype(np.float32).astype(np.float64))
    for name in ('nodes', 'idx', 'channel_frac'):
        np.testing.assert_array_equal(getattr(first_frames[first_keys['candidate']], name), getattr(first, name))
    cubes = {role: np.memmap(spec['oracle'], np.uint8, 'r', shape=(TOTAL, 3)) for role, spec in roles.items() if role != 'candidate'}
    cubes['candidate'] = np.memmap(args.output/'candidate.rgb', np.uint8, 'w+', shape=(TOTAL, 3))
    configs = [(kernel, threads, path) for kernel, threads in (('scalar', 1), ('avx2', 1), ('avx2', 4)) for path in ('inplace', 'outplace')]
    sources = {Path(__file__), plan_path, ROOT/'experiments/cinema-current-anchor-v1.json', ROOT/'scripts/run_channel_tail_nodes.py',
        ROOT/'scripts/verify_channel_coordinates.py', ROOT/'scripts/outplace_support.py', ROOT/'scripts/suffix_cache_support.py',
        ROOT/'scripts/domain_cache_support.py', ROOT/'scripts/direct16_support.py', ROOT/'scripts/palette_support.py',
        ROOT/'scripts/exception_support.py', ROOT/'experiments/channel-runtime/channel_native.py'}
    sources.update(ROOT/name for name in frozen['source_sha256'])
    save(args.output/'identity.json', {'source_sha256': {path.relative_to(ROOT).as_posix(): digest(path) for path in sorted(sources)},
        'roles': {role: {**spec, 'models': [str(path) for path in spec['models']], 'sidecars': [str(path) if path else None for path in spec['sidecars']],
            'oracle': str(spec['oracle']) if 'oracle' in spec else None} for role, spec in roles.items()},
        'frozen_sha256': digest(args.frozen), 'reference_sha256': digest(reference_path), 'original_tables': raw_plan['tables'], 'library_sha256': digest(args.library),
        'environment': study_provenance.environment_fingerprint(), 'numba_threads': 4, 'native_configurations_per_role': configs,
        'plan': plan, 'scope': '独立新三分母质量资格；旧minL1局部失败保留，无solver/拟合/吞吐计时。'})
    old_failure = json.loads((ROOT/'artifacts/cinema-first-safe-cpsat-accept-v2/summary.json').read_text(encoding='utf-8'))
    if old_failure['eligible_for_independent_final_checks'] or len(old_failure['failures']) != 6: raise ValueError('旧六预算失败原件异常')
    histograms = {role: np.zeros(SIZE, np.int64) for role in roles}
    first_histograms = {key: np.zeros(SIZE, np.int64) for key in first_frames}
    hashes = {role: {str(config): hashlib.sha256() for config in configs} for role in roles}
    oracle_hash = hashlib.sha256(); truth_hash = hashlib.sha256(); runtime = {}; photo_rows = {role: [] for role in roles}
    photo_hist = {role: np.zeros(SIZE, np.int64) for role in roles}; train_hist = {role: np.zeros(SIZE, np.int64) for role in roles}
    merged_hash = {role: hashlib.sha256() for role in roles}
    with ExitStack() as stack:
        stack.enter_context(os.add_dll_directory('E:/mingw64/bin')); stack.enter_context(os.add_dll_directory(str(args.library.resolve().parent)))
        library = Library(args.library, digest(args.library)); to_function = bind_to(library.dll)
        chains = {role: stack.enter_context(library.chain(spec['models'], spec['sidecars'])) for role, spec in roles.items()}
        for role, chain in chains.items(): runtime[role] = {'capacity_bytes': chain.model_bytes, 'cache': cache_info(chain),
            'domain': domain_info(chain), 'palette': palette_info(chain), 'direct': direct_info(chain)}
        for start in range(0, TOTAL, 65536):
            keys = np.arange(start, start+65536, dtype=np.uint32); rgb = hs.rgb(keys)
            oracle, predicted = rgb.copy(), rgb.copy()
            for level, model in enumerate(models):
                oracle = integer_oracle(model, oracle); predicted = cc.predict(model, predicted)
                if level == 0: candidate_first = oracle
            np.testing.assert_array_equal(oracle, predicted)
            truth = tables[0][keys]
            for table in tables[1:]: truth = table[hs.key(truth)]
            np.testing.assert_array_equal(truth, reference[start:start+65536]); truth_hash.update(truth.tobytes())
            for key, frame in first_frames.items():
                standalone = candidate_first if key == first_keys['candidate'] else integer_oracle(frame, rgb)
                first_histograms[key] += histogram(standalone, tables[0][keys])
            cubes['candidate'][start:start+65536] = oracle; oracle_hash.update(oracle.tobytes())
            for role, chain in chains.items():
                expected = cubes[role][start:start+65536]
                for kernel, threads, path in configs:
                    actual = chain.apply(rgb.copy(), kernel=kernel, threads=threads) if path == 'inplace' else actual_to(to_function, chain, rgb, kernel, threads)
                    np.testing.assert_array_equal(actual, expected); hashes[role][str((kernel, threads, path))].update(actual.tobytes())
                histograms[role] += histogram(expected, truth)
        cubes['candidate'].flush()
        for row in manifest['images']:
            path = cache/row['evaluation']['path']
            if digest(path) != row['evaluation']['sha256']: raise ValueError('固定照片已变')
            with Image.open(path) as image: rgb = np.asarray(image).reshape(-1, 3).copy()
            keys = hs.key(rgb)
            for role, chain in chains.items():
                actual = chain.apply(rgb.copy(), kernel='avx2', threads=4); np.testing.assert_array_equal(actual, cubes[role][keys])
                h = histogram(actual, reference[keys]); photo_hist[role] += h
                if row['id'] in training_ids: train_hist[role] += h
                merged_hash[role].update(actual.tobytes())
                photo_rows[role].append({'image': row['id'], **metrics(h), 'prediction_sha256': hashlib.sha256(actual.tobytes()).hexdigest()})
    cube_metrics = {role: metrics(hist) for role, hist in histograms.items()}; photo_metrics = {role: metrics(hist) for role, hist in photo_hist.items()}
    training_metrics = {role: metrics(hist) for role, hist in train_hist.items()}
    if any(value['n'] != 47185920 for value in training_metrics.values()): raise AssertionError('实际原60图像素数不符')
    if any(value['n'] != 78643200 for value in photo_metrics.values()): raise AssertionError('实际100图像素数不符')
    for actual, prior in ((cube_metrics['candidate'], old_failure['after_uniform']),
            (training_metrics['candidate'], old_failure['after_training'])):
        for name, value in prior.items():
            if abs(actual[name]-value) > 1e-12: raise AssertionError('独立四级与原L1完整支撑观测不等：'+name)
    pairs = {}
    for role in ('a399', 'best', 'max_first'):
        per_image = [{'image': new['image'], **compare(old, new)} for old, new in zip(photo_rows[role], photo_rows['candidate'])]
        pairs[role] = {'cube': compare(cube_metrics[role], cube_metrics['candidate']), 'photos': compare(photo_metrics[role], photo_metrics['candidate']),
            'training60': compare(training_metrics[role], training_metrics['candidate']), 'per_image': per_image,
            'per_metric_changes': {metric: {label: sum(row['metrics'][metric]['change'] == label for row in per_image) for label in ('好', '平', '差')} for metric in METRICS},
            'worst_image_retained_percent': min(row['minimum_retained_percent'] for row in per_image)}
    passed = all(cube_metrics['candidate']['mean'] <= cube_metrics[role]['mean']+1e-12 and
        photo_metrics['candidate']['mean'] <= photo_metrics[role]['mean']+1e-12 for role in ('a399', 'best'))
    thresholds = {role: {str(t): sum(row['max'] < t for row in rows) for t in THRESHOLDS} for role, rows in photo_rows.items()}
    result = {'cube': cube_metrics, 'photos': {role: {**photo_metrics[role], 'per_image': rows} for role, rows in photo_rows.items()},
        'standalone_first_vs_original_table1': {role: metrics(first_histograms[first_keys[role]]) for role in roles},
        'training60': training_metrics, 'pairs': pairs, 'nonofficial_strict_max_T_counts': thresholds, 'runtime': runtime,
        'candidate_oracle_sha256': oracle_hash.hexdigest(), 'reference_payload_sha256': truth_hash.hexdigest(),
        'native_full_stream_sha256': {role: {key: h.hexdigest() for key, h in records.items()} for role, records in hashes.items()},
        'native_100photos_sha256': {role: h.hexdigest() for role, h in merged_hash.items()}, 'full_native_configs': 24,
        'full_and_photo_native_mismatches': 0, 'old_minl1_failed_metrics': old_failure['failures'],
        'mean_qualified_against_common_baselines': passed, 'overall_upgrade': False,
        'scope': '只完成独立三分母完整域/实际百图质量与真实runtime容量；不改变旧六预算失败。速度50%尚未证，不切默认。'}
    for role in ('a399', 'best', 'max_first'):
        if any(h.hexdigest() != roles[role]['oracle_sha256'] for h in hashes[role].values()): raise AssertionError('固定分母全域流SHA异常')
    if any(h.hexdigest() != oracle_hash.hexdigest() for h in hashes['candidate'].values()): raise AssertionError('候选24矩阵完整流不等')
    np.savez_compressed(args.output/'histograms.npz', **{scope+'_'+role: hist for scope, group in
        (('cube', histograms), ('photos', photo_hist), ('training60', train_hist),
         ('standalone_first', {role: first_histograms[first_keys[role]] for role in roles})) for role, hist in group.items()})
    save(args.output/'results.json', result)
    print({'mean_qualified': passed, 'candidate_cube': cube_metrics['candidate'], 'candidate_photos': photo_metrics['candidate'], 'configs': 24}, flush=True)


if __name__ == '__main__': main()
