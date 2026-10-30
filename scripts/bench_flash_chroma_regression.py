"""三方同场回归：旧评分库、修复前单头库、修复后单头库；集中执行且不补轮择优。"""
from __future__ import annotations

import argparse
import ctypes as ct
import json
import os
from pathlib import Path
import statistics
import sys
import time

import numpy as np

import flash_chroma_support as modern
import p16_unified_support as legacy
import p16_submission as submission

ROOT = Path(__file__).resolve().parents[1]
PROFILES = ('default', 'max_first')
THREADS = (1, 4)
PAIRS = (('old', 'old'), ('before', 'before'), ('fixed', 'fixed'), ('old', 'fixed'), ('before', 'fixed'))
AA_BOUNDS = (.90, 1.10)
THREAD_ENVIRONMENT = ('OMP_NUM_THREADS', 'OMP_WAIT_POLICY', 'OMP_PROC_BIND', 'OMP_PLACES',
                      'OMP_DYNAMIC', 'GOMP_CPU_AFFINITY', 'OPENBLAS_NUM_THREADS', 'MKL_NUM_THREADS')


def save_new(path, value):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open('x', encoding='utf-8', newline='\n') as stream:
        json.dump(value, stream, ensure_ascii=False, indent=2, allow_nan=False)
        stream.write('\n')


def resolve(path, base):
    path = Path(path)
    return (path if path.is_absolute() else Path(base) / path).resolve()


def loaded_identity(library):
    handle = int(library.dll._handle)
    row = {'handle': handle, 'requested_path': str(library.path), 'mapped_path_verified': False}
    if os.name == 'nt':
        kernel = ct.WinDLL('kernel32', use_last_error=True)
        function = kernel.GetModuleFileNameW
        function.argtypes = [ct.c_void_p, ct.c_wchar_p, ct.c_uint32]
        function.restype = ct.c_uint32
        buffer = ct.create_unicode_buffer(32768)
        size = function(ct.c_void_p(handle), buffer, len(buffer))
        if not size or size == len(buffer):
            raise OSError('无法核对实际加载模块路径')
        mapped = Path(buffer.value).resolve()
        if os.path.normcase(str(mapped)) != os.path.normcase(str(library.path)):
            raise ValueError('实际加载模块与指定DLL路径不同')
        if modern.digest(mapped) != library.sha256:
            raise ValueError('实际加载模块SHA与指定DLL不同')
        row.update(mapped_path=str(mapped), mapped_path_verified=True, sha256=library.sha256)
    return row


def read_images(receipt_path):
    receipt_path = Path(receipt_path).resolve()
    receipt = json.loads(receipt_path.read_text(encoding='utf-8'))
    if not receipt.get('completed') or len(receipt.get('images', [])) != 100:
        raise ValueError('图像回执必须是已完成的固定100图记录')
    frames = np.empty((100, 768, 1024, 3), np.uint8)
    records = []
    for index, row in enumerate(receipt['images']):
        path = resolve(row['path'], receipt_path.parent)
        file_sha = row.get('sha256', row.get('file_sha256'))
        if modern.digest(path) != file_sha:
            raise ValueError('图像文件SHA与回执不同：' + str(path))
        frames[index] = submission._rgb8(path)
        pixel_sha = modern.sha(frames[index])
        if pixel_sha != row['pixel_sha256']:
            raise ValueError('图像解码SHA与回执不同：' + str(path))
        records.append({'path': str(path), 'sha256': file_sha, 'pixel_sha256': pixel_sha})
    source_sha = modern.sha(frames)
    if source_sha != receipt['source_pixels_sha256']:
        raise ValueError('完整百图像素顺序或内容与回执不同')
    expected = {}
    for row in receipt.get('records', []):
        name = row.get('profile')
        if name in PROFILES and 'batch_sha256' in row:
            if name in expected and expected[name] != row['batch_sha256']:
                raise ValueError('原回执同一profile存在不一致输出')
            expected[name] = row['batch_sha256']
    if set(expected) != set(PROFILES):
        raise ValueError('原回执需包含default和max_first的已验百图输出SHA')
    return frames, records, source_sha, expected


def summarize(cycles):
    ratios, side_a, side_b = [], [], []
    for cycle in cycles:
        a = [row['milliseconds'] for row in cycle['trials'] if row['role'] == 'A']
        b = [row['milliseconds'] for row in cycle['trials'] if row['role'] == 'B']
        if len(a) != 2 or len(b) != 2:
            raise ValueError('每个周期必须恰好包含两次A和两次B')
        side_a.extend(a)
        side_b.extend(b)
        ratios.append(statistics.mean(b) / statistics.mean(a))
    return {'a_median_ms': statistics.median(side_a), 'b_median_ms': statistics.median(side_b),
            'a_min_ms': min(side_a), 'a_max_ms': max(side_a), 'b_min_ms': min(side_b), 'b_max_ms': max(side_b),
            'cycle_ratios_b_over_a': ratios, 'ratio_median': statistics.median(ratios),
            'ratio_of_trial_medians_b_over_a': statistics.median(side_b)/statistics.median(side_a),
            'ratio_min': min(ratios), 'ratio_max': max(ratios),
            'all_cycles_within_aa_bounds': all(AA_BOUNDS[0] <= ratio <= AA_BOUNDS[1] for ratio in ratios),
            'median_non_regression': statistics.median(ratios) <= 1.0,
            'all_cycles_non_regressing': all(ratio <= 1.0 for ratio in ratios)}


def qualification(records):
    """只给同范围、同profile及线程的对照授予描述性资格；任何控制失败均保留。"""
    index = {(r['scope'], r['profile'], r['threads'], r['pair']): r for r in records}
    results = []
    for row in records:
        if row['pair'] not in ('old_fixed', 'before_fixed'):
            continue
        prefix = (row['scope'], row['profile'], row['threads'])
        left = row['versions'][0]
        controls = [index[(*prefix, left+'_'+left)], index[(*prefix, 'fixed_fixed')]]
        aa_pass = all(r['summary']['all_cycles_within_aa_bounds'] for r in controls)
        fair_threads = row['scope'] == 'hot_apply' or left != 'old' or row['threads'] == 4
        results.append({'scope': row['scope'], 'profile': row['profile'], 'threads': row['threads'],
                        'pair': row['pair'], 'fixed_over_reference_median': row['summary']['ratio_median'],
                        'fixed_over_reference_all_cycles': row['summary']['cycle_ratios_b_over_a'],
                        'fixed_over_reference_min_max': [row['summary']['ratio_min'], row['summary']['ratio_max']],
                        'both_aa_controls_pass': aa_pass, 'prepare_thread_policy_comparable': fair_threads,
                        'median_non_regression': row['summary']['median_non_regression'],
                        'qualified_median_non_regression': aa_pass and fair_threads and row['summary']['median_non_regression'],
                        'all_cycles_non_regressing': row['summary']['all_cycles_non_regressing'],
                        'limitation': '同场单次固定计划，不锁频；首批旧库含模型文件读取，新库模型已读。1T旧prepare仍固定4T，不能作为同准备线程比值。'})
    return results


class Experiment:
    def __init__(self, args, frames, models, expected, libraries, original_rows):
        self.args, self.frames, self.models, self.expected = args, frames, models, expected
        self.libraries, self.original_rows = libraries, original_rows
        self.target = np.empty_like(frames)
        self.target.fill(173)
        self.poison_by_profile = {}
        self.source = frames.reshape(-1, 3)
        self.destination = self.target.reshape(-1, 3)
        self.progress = {'completed': False, 'records': [], 'last_trial': None, 'active_case': None}
        with (self.args.output / 'measurements.jsonl').open('x', encoding='utf-8'):
            pass

    def config(self, name, threads):
        return modern.configuration('direct_u8' if name == 'default' else 'direct_u16', 'avx2', threads)

    def create(self, name, version, threads):
        if version == 'old':
            return self.libraries['old'].create(self.original_rows[name], hint=self.source.size // 3)
        return self.libraries[version].create(self.models[name], self.config(name, threads))

    def apply(self, engine, version, threads):
        if version == 'old':
            return engine.apply(self.frames, self.target, 'avx2', threads)[0] * 1000
        return engine.apply(self.source, self.destination)

    def reset_output(self, name):
        # 计时外覆盖目标；首次正确输出确认后，每字节取反，漏写任一字节都会改变SHA。
        if name in self.poison_by_profile:
            np.copyto(self.target, self.poison_by_profile[name])
        else:
            self.target.fill(173)

    def state(self, engine, version, name):
        if version == 'old':
            diagnostics = legacy.diagnostics(engine)
            direct = diagnostics['direct']
            expected_format = 9 if name == 'default' else 16
            if not direct['enabled'] or direct['format'] != expected_format:
                raise RuntimeError('旧库没有实际进入要求的direct表示')
            return {'diagnostics': diagnostics, 'backend': 'avx2', 'prepare_thread_policy': 'direct构建固定4T，嵌套OpenMP时1T'}
        if engine.info['selected_backend'] != 2:
            raise RuntimeError('单头库实际未选择AVX2')
        preparation = getattr(engine, 'preparation', None)
        return {'resources': dict(engine.info), 'config': dict(engine.config), 'preparation': preparation,
                'prepare_thread_policy': ('原通用U8/U16全域palette准备串行' if version == 'before' else
                    ('本句柄小域cache和扫描线按config.threads；嵌套OpenMP时1T' if preparation and preparation['suffix_cache'] else
                     '本句柄通用palette回退串行；无小域cache资格')),
                'prepare_threads_measured': False}

    def check_output(self, trial, name):
        trial['sha256'] = modern.sha(self.target)
        trial['expected_sha256'] = self.expected[name]
        self.progress['last_trial'] = dict(trial)
        active = self.progress['active_case']
        journal = {key: active[key] for key in ('scope', 'profile', 'threads', 'pair')}
        journal['trial'] = trial
        with (self.args.output / 'measurements.jsonl').open('a', encoding='utf-8', newline='\n') as stream:
            stream.write(json.dumps(journal, ensure_ascii=False, allow_nan=False)+'\n')
        if trial['sha256'] != self.expected[name]:
            raise RuntimeError('百图输出SHA不一致，保留失败原值并停止：' + name)
        if name not in self.poison_by_profile:
            self.poison_by_profile[name] = np.bitwise_not(self.target)

    def checkpoint(self, record):
        self.progress['records'].append(record)
        self.progress['active_case'] = None
        filename = f'{record["scope"]}-{record["profile"]}-{record["threads"]}t-{record["pair"]}.json'
        save_new(self.args.output / filename, record)
        modern.write_json(self.args.output / 'partial.json', self.progress)
        print(json.dumps({'scope': record['scope'], 'profile': record['profile'], 'threads': record['threads'],
                          'pair': record['pair'], 'summary': record['summary']}, ensure_ascii=False), flush=True)

    def hot_pair(self, name, threads, versions):
        engines, warmups, states, cycles = [], [], [], []
        self.progress['active_case'] = {'scope': 'hot_apply', 'profile': name, 'threads': threads,
                                       'pair': '_'.join(versions), 'versions': versions,
                                       'warmups': warmups, 'states': states, 'cycles': cycles}
        try:
            for side, version in enumerate(versions):
                engine = self.create(name, version, threads)
                engines.append(engine)
                self.reset_output(name)
                trial = {'role': 'A' if side == 0 else 'B', 'version': version, 'phase': 'warmup',
                         'milliseconds': self.apply(engine, version, threads)}
                warmups.append(trial)
                self.check_output(trial, name)
                states.append(self.state(engine, version, name))
            for cycle_index in range(self.args.cycles):
                order = 'ABBA' if cycle_index % 2 == 0 else 'BAAB'
                trials = []
                cycles.append({'index': cycle_index, 'order': order, 'trials': trials})
                for role in order:
                    side = 0 if role == 'A' else 1
                    self.reset_output(name)
                    trial = {'role': role, 'version': versions[side], 'phase': 'formal',
                             'cycle': cycle_index, 'order': order,
                             'milliseconds': self.apply(engines[side], versions[side], threads)}
                    trials.append(trial)
                    self.check_output(trial, name)
            self.checkpoint({'scope': 'hot_apply', 'profile': name, 'threads': threads,
                             'pair': '_'.join(versions), 'versions': versions, 'warmups': warmups,
                             'states': states, 'cycles': cycles, 'summary': summarize(cycles)})
        finally:
            for engine in engines:
                engine.close()

    def first_pair(self, name, threads, versions):
        cycles = []
        self.progress['active_case'] = {'scope': 'prepare_first_batch', 'profile': name, 'threads': threads,
                                       'pair': '_'.join(versions), 'versions': versions, 'cycles': cycles}
        for cycle_index in range(self.args.cycles):
            order = 'ABBA' if cycle_index % 2 == 0 else 'BAAB'
            trials = []
            cycles.append({'index': cycle_index, 'order': order, 'trials': trials})
            for role in order:
                side = 0 if role == 'A' else 1
                version = versions[side]
                engine = None
                try:
                    self.reset_output(name)
                    started = time.perf_counter_ns()
                    engine = self.create(name, version, threads)
                    ready = time.perf_counter_ns()
                    apply_ms = self.apply(engine, version, threads)
                    stopped = time.perf_counter_ns()
                    trial = {'role': role, 'version': version, 'phase': 'formal', 'cycle': cycle_index,
                             'order': order, 'milliseconds': (stopped-started)/1e6,
                             'create_ms': (ready-started)/1e6, 'apply_ms': apply_ms,
                             'native_prepare_ms': engine.prepare_seconds*1000 if version == 'old' else engine.prepare_ms}
                    trials.append(trial)
                    self.check_output(trial, name)
                    trial['state'] = self.state(engine, version, name)
                finally:
                    if engine is not None:
                        engine.close()
        self.checkpoint({'scope': 'prepare_first_batch', 'profile': name, 'threads': threads,
                         'pair': '_'.join(versions), 'versions': versions, 'cycles': cycles,
                         'summary': summarize(cycles)})


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--old-library', type=Path, default=ROOT.parent/'p16-unified-avx512-20261026/artifacts/p16-score-cpu-build/libjshc_unified.dll')
    parser.add_argument('--before-library', type=Path, default=ROOT/'artifacts/single-header-build/libflash_chroma_bridge.dll')
    parser.add_argument('--fixed-library', type=Path, default=ROOT/'artifacts/single-header-perf-build/libflash_chroma_bridge.dll')
    parser.add_argument('--manifest', type=Path, default=ROOT/'data/p16-frontier/models/manifest.json')
    parser.add_argument('--image-receipt', type=Path, default=ROOT/'report/data/p16-frontier-header-20261027/results.json')
    parser.add_argument('--old-build-receipt', type=Path, default=ROOT/'report/data/p16-score-candidate-20261027/build-receipt.json')
    parser.add_argument('--output', type=Path, required=True)
    parser.add_argument('--cycles', type=int, default=4)
    parser.add_argument('--cpus', default='0,2,4,6')
    args = parser.parse_args(argv)
    args.output = args.output.resolve()
    if args.output.exists():
        raise FileExistsError('拒绝覆盖已有回归计划或结果')
    if not 3 <= args.cycles <= 10:
        raise ValueError('周期数须预先固定为3..10，本方案默认4，不补轮择优')
    # 在载入OpenMP库之前确定同一进程的等待策略与亲和，所有三方保持相同。
    os.environ.setdefault('OMP_WAIT_POLICY', 'PASSIVE')
    legacy.setup(cpus=args.cpus)
    paths = {'old': args.old_library.resolve(), 'before': args.before_library.resolve(), 'fixed': args.fixed_library.resolve()}
    library_hashes = {name: modern.digest(path) for name, path in paths.items()}
    if len(set(library_hashes.values())) != 3:
        raise ValueError('三方DLL必须具有三个不同SHA，不能误把同一构建重复标记为修复对照')
    libraries = {'old': legacy.Library(paths['old']), 'before': modern.Library(paths['before']), 'fixed': modern.Library(paths['fixed'])}
    loaded = {name: loaded_identity(library) for name, library in libraries.items()}
    if len({row['handle'] for row in loaded.values()}) != 3:
        raise ValueError('三方运行模块句柄必须不同，拒绝加载别名')
    if not libraries['old'].supported('avx2') or any(not (libraries[name].capabilities & 2) for name in ('before', 'fixed')):
        raise ValueError('本集中性能回归要求三方实际支持AVX2')
    manifest, models = modern.load_models(args.manifest, PROFILES)
    model_root = Path(manifest.get('path_root', args.manifest.resolve().parent))
    if not model_root.is_absolute():
        model_root = args.manifest.resolve().parent / model_root
    original_rows = {}
    for name in PROFILES:
        original_rows[name] = {key: [dict(row, path=str(resolve(row['path'], model_root))) if row is not None else None
                                   for row in models[name].profile[key]] for key in ('models', 'sidecars')}
    frames, images, source_sha, expected = read_images(args.image_receipt)
    model_memory = {name: [modern.sha(np.ctypeslib.as_array(buffer)) for buffer in model.buffers] for name, model in models.items()}
    source_files = {str(path.resolve()): modern.digest(path) for path in
                    (Path(__file__), ROOT/'scripts/flash_chroma_support.py', ROOT/'scripts/p16_unified_support.py', ROOT/'scripts/p16_submission.py')}
    records = [libraries[name].record() for name in ('old', 'before', 'fixed')]
    old_build = {'path': str(args.old_build_receipt.resolve()), 'sha256': modern.digest(args.old_build_receipt)}
    old_receipt = json.loads(args.old_build_receipt.read_text(encoding='utf-8'))
    if old_receipt.get('outputs', {}).get(paths['old'].name) != library_hashes['old']:
        raise ValueError('旧评分库SHA与指定构建回执不同')
    if any(libraries[name].build_receipt is None for name in ('before', 'fixed')):
        raise ValueError('修复前后单头DLL须保留实际链接生成的.build.json来源回执')
    frozen_inputs = {'manifest': {'path': str(args.manifest.resolve()), 'sha256': modern.digest(args.manifest)},
                     'image_receipt': {'path': str(args.image_receipt.resolve()), 'sha256': modern.digest(args.image_receipt)}}
    args.output.mkdir(parents=True)
    experiment = Experiment(args, frames, models, expected, libraries, original_rows)
    plan = {'purpose': '集中验证成熟速度路径迁移：三方同场、固定ABBA/BAAB和每次输出SHA；失败不补轮、不删慢轮',
            'environment': legacy.environment(), 'thread_environment': {name: os.environ.get(name) for name in THREAD_ENVIRONMENT},
            'libraries': dict(zip(('old', 'before', 'fixed'), records)), 'old_build_receipt': old_build,
            'loaded_modules': loaded,
            'inputs': frozen_inputs, 'models': {name: {'files': model.records, 'profile': model.profile} for name, model in models.items()},
            'images': images, 'source_pixels_sha256': source_sha, 'expected_batch_sha256': expected,
            'profiles': PROFILES, 'threads': THREADS, 'pairs': PAIRS, 'cycles': args.cycles,
            'orders': ['ABBA', 'BAAB'], 'aa_bounds': AA_BOUNDS, 'hash_every_call': True,
            'output_reset': '每次计时前覆盖目标；首次输出经独立SHA验证后，以其逐字节取反作为后续毒化值。毒化在热映射计时及首批墙时之外。',
            'primary_ratio': '四个周期中，每周期mean(B两次)/mean(A两次)的中位；另列全部周期范围和各侧原始样本中位比',
            'formal_hot_calls': len(PROFILES)*len(THREADS)*len(PAIRS)*args.cycles*4,
            'formal_first_calls': len(PROFILES)*len(THREADS)*len(PAIRS)*args.cycles*4,
            'warmup_calls': len(PROFILES)*len(THREADS)*len(PAIRS)*2,
            'source_address_mod64': int(frames.ctypes.data % 64), 'target_address_mod64': int(experiment.target.ctypes.data % 64),
            'hot_scope': '预加载同一百图、相同分离输出、每次单FFI完整批次；排除准备/分配/解码/SHA。每次SHA都在计时后进行，对所有三方相同，可能改变下一次缓存状态。',
            'first_scope': '相同预加载图片，新句柄创建至首批输出；旧API含SLUT/sidecar文件读取，新API模型已读。含arena分配、准备及Python/可用诊断封装，不含解码、SHA及销毁；另列native_prepare_ms，不能称纯准备算法公平比值。',
            'prepare_threads': {'old': 'direct构建固定4T；嵌套团队内1T', 'before': 'U8/U16通用palette构造串行',
                                'fixed': '小域cache与扫描线按请求线程；通用palette回退串行；嵌套团队内1T'},
            'prepare_threads_measured': False, 'first_1t_limitation': '旧prepare固定4T而新按配置；1T首批不授同准备线程非退化资格，4T为主要目标',
            'source_sha256': source_files, 'official_score_available': False, 'frequency_locked': False}
    save_new(args.output/'plan.json', plan)
    try:
        for name in PROFILES:
            for threads in THREADS:
                for versions in PAIRS:
                    experiment.hot_pair(name, threads, versions)
                for versions in PAIRS:
                    experiment.first_pair(name, threads, versions)
        if modern.sha(frames) != source_sha:
            raise RuntimeError('三方执行过程中源图像被改写')
        for name, model in models.items():
            if [modern.sha(np.ctypeslib.as_array(buffer)) for buffer in model.buffers] != model_memory[name]:
                raise RuntimeError('单头库改写借用模型内存')
            for row in model.records:
                if modern.digest(row['path']) != row['sha256']:
                    raise RuntimeError('模型文件在回归期间改变')
        for row in images:
            if modern.digest(row['path']) != row['sha256']:
                raise RuntimeError('图像文件在回归期间改变')
        for name, path in paths.items():
            if modern.digest(path) != library_hashes[name]:
                raise RuntimeError('DLL在回归期间改变')
        for path, sha in source_files.items():
            if modern.digest(path) != sha:
                raise RuntimeError('基准或封装源码在回归期间改变')
        for row in frozen_inputs.values():
            if modern.digest(row['path']) != row['sha256']:
                raise RuntimeError('manifest或输入回执在回归期间改变')
        results = {'completed': True, 'plan': plan, 'records': experiment.progress['records'],
                   'qualification': qualification(experiment.progress['records']),
                   'formal_calls': plan['formal_hot_calls']+plan['formal_first_calls'],
                   'scope': '仅运行时同模型输出与本机性能回归；不新增密集原LUT拟合精度或目标Xeon6140成绩'}
        save_new(args.output/'results.json', results)
        print('三方集中回归完成，所有原始周期保留：'+str(args.output/'results.json'), flush=True)
    except BaseException as error:
        failure = dict(experiment.progress, error={'type': type(error).__name__, 'message': str(error)})
        save_new(args.output/'failure.json', failure)
        raise
    return 0


if __name__ == '__main__':
    try:
        raise SystemExit(main())
    except (ValueError, OSError, RuntimeError) as error:
        print('回归失败，已保留原始证据：'+str(error), file=sys.stderr)
        raise SystemExit(1)
