"""构建并调度RGB24同表回归，区分小样筛选、纯核与含输出分配范围。"""
from __future__ import annotations

import argparse
import hashlib
import json
import math
import os
from pathlib import Path
import platform
import shutil
import statistics
import subprocess
import time

try:
    import psutil
except ImportError:
    psutil = None

ROOT = Path(__file__).resolve().parents[1]
SOURCE_NAMES = ('framework/rgb24_regression.cpp', 'framework/framework_io.hpp',
                'framework/flash_chroma_adapter.hpp', 'framework/fit_experiment.hpp',
                'framework/fit_chain_experiment.hpp', 'include/flash_chroma.hpp',
                'scripts/bench_rgb24_regression.py')
LUT_BYTES = 256 ** 3 * 3 * 2
IMAGE_BYTES = 1024 * 768 * 3


def digest(path):
    with Path(path).open('rb') as stream:
        return hashlib.file_digest(stream, 'sha256').hexdigest()


def fnv(path):
    value = 14695981039346656037
    with Path(path).open('rb') as stream:
        while block := stream.read(1024 * 1024):
            for byte in block:
                value = ((value ^ byte) * 1099511628211) & 0xffffffffffffffff
    return f'{value:016x}'


def source_ids():
    return {name: digest(ROOT / name) for name in SOURCE_NAMES}


def read(path):
    return json.loads(Path(path).read_text(encoding='utf-8'))


def save(path, value):
    with Path(path).open('x', encoding='utf-8', newline='\n') as stream:
        json.dump(value, stream, ensure_ascii=False, indent=2, allow_nan=False)
        stream.write('\n')


def new_directory(path):
    path = Path(path).resolve()
    if path.exists():
        raise FileExistsError('输出目录已存在，拒绝覆盖')
    path.mkdir(parents=True)
    return path


def environment(compiler=None):
    env = os.environ.copy()
    for key in ('OMP_NUM_THREADS', 'OPENBLAS_NUM_THREADS', 'MKL_NUM_THREADS', 'NUMEXPR_NUM_THREADS'):
        env[key] = '1'
    if compiler:
        env['PATH'] = str(Path(compiler).parent) + os.pathsep + env.get('PATH', '')
    return env


def build(args):
    output = new_directory(args.output)
    compiler = args.compiler.resolve()
    before = source_ids()
    executable = output / 'rgb24_regression.exe'
    command = [str(compiler), '-std=c++17', '-O3', '-DNDEBUG', '-static',
               '-DFLASH_CHROMA_ENABLE_OPENMP=0', '-Wall', '-Wextra', '-Wpedantic',
               '-I', str(ROOT / 'framework'), '-I', str(ROOT / 'include'),
               str(ROOT / 'framework/rgb24_regression.cpp'), '-o', str(executable)]
    process = subprocess.run(command, cwd=ROOT, capture_output=True, env=environment(compiler))
    (output / 'build-stdout.log').write_bytes(process.stdout)
    (output / 'build-stderr.log').write_bytes(process.stderr)
    if process.returncode or source_ids() != before:
        save(output / 'failure.json', {'passed': False, 'returncode': process.returncode,
                                      'source_unchanged': source_ids() == before})
        raise RuntimeError('构建失败或构建期间来源改变，见构建日志')
    receipt = {'schema': 'rgb24_regression_build_v1', 'command': command,
               'compiler': str(compiler), 'compiler_sha256': digest(compiler),
               'compiler_version': subprocess.check_output([str(compiler), '--version'], env=environment(compiler)).decode('utf-8', 'replace'),
               'executable': str(executable), 'executable_sha256': digest(executable),
               'sources': before, 'threads': 1, 'openmp_enabled': False}
    save(str(executable) + '.build.json', receipt)
    return receipt


def verify_executable(path):
    path = path.resolve()
    receipt = read(str(path) + '.build.json')
    if receipt.get('schema') != 'rgb24_regression_build_v1' or receipt.get('sources') != source_ids() or \
            receipt.get('executable_sha256') != digest(path) or receipt.get('threads') != 1 or receipt.get('openmp_enabled') is not False:
        raise ValueError('可执行程序与当前源码或构建凭据不符，必须重新build')
    return path, receipt


def identity(path):
    path = Path(path).resolve()
    return {'path': str(path), 'bytes': path.stat().st_size, 'sha256': digest(path)}


def input_records(path, count):
    path = path.resolve()
    records = []
    for line in path.read_text(encoding='utf-8-sig').splitlines():
        line = line.strip()
        if not line or line.startswith('#'):
            continue
        source = Path(line)
        source = (source if source.is_absolute() else path.parent / source).resolve()
        record = identity(source)
        if record['bytes'] != IMAGE_BYTES:
            raise ValueError('输入必须为1024x768 RGB8 raw')
        records.append(record)
    if len(records) != count or len({row['path'] for row in records}) != count:
        raise ValueError(f'需要{count}个不同路径的固定图片，顺序保持不变')
    return records


def summarize_native(value):
    summaries = []
    phase = 'screen' if value['screen'] else 'comparison'
    for scope in ('hot', 'allocated'):
        for kernel in ('legacy', 'cached', 'stream'):
            selected = [run for run in value['runs'] if run['scope'] == scope and
                        run['phase'] == phase and run['kernel'] == kernel and run['verified']]
            if not selected:
                continue
            batches = [run['batch_ms'] for run in selected]
            per_image = list(zip(*(run['image_ms'] for run in selected)))
            summaries.append({'scope': scope, 'kernel': kernel, 'batch_samples_ms': batches,
                              'batch_median_ms': statistics.median(batches),
                              'batch_min_ms': min(batches), 'batch_max_ms': max(batches),
                              'per_image_median_ms': [statistics.median(row) for row in per_image]})
    speedups = []
    for scope in ('hot', 'allocated'):
        rows = {row['kernel']: row for row in summaries if row['scope'] == scope}
        if 'legacy' in rows:
            for kernel in ('cached', 'stream'):
                if kernel in rows:
                    baseline, candidate = rows['legacy']['batch_median_ms'], rows[kernel]['batch_median_ms']
                    speedups.append({'scope': scope, 'kernel': kernel, 'baseline_over_candidate': baseline / candidate,
                                     'candidate_time_change_fraction': candidate / baseline - 1})
    return summaries, speedups


def validate_native(value, images):
    if not value or len(value.get('images', [])) != len(images):
        return False
    for i, (actual, expected) in enumerate(zip(value['images'], images), 1):
        if actual['index'] != i or actual['path'] != expected['path'] or actual['bytes'] != IMAGE_BYTES or actual['input_fnv1a64'] != expected['fnv1a64']:
            return False
    for run in value.get('runs', []):
        if not run['verified'] or len(run['image_ms']) != len(images) or not all(math.isfinite(x) and x >= 0 for x in run['image_ms']):
            return False
        if not math.isclose(sum(run['image_ms']), run['batch_ms'], rel_tol=1e-12, abs_tol=1e-9):
            return False
    return True


def run(args):
    if psutil is None:
        raise RuntimeError('受控执行需要psutil以验证绑核和进程观测；纯报告解析不依赖该模块')
    executable, receipt = verify_executable(args.exe)
    if args.affinity not in psutil.Process().cpu_affinity():
        raise ValueError('指定绑核不在当前可用CPU列表内')
    cache_path = args.cache.resolve()
    cached = read(cache_path)
    if cached.get('schema') != 'framework_lut_u16_cache_v1' or cached.get('format') != 'u16le-file-order' or len(cached.get('records', [])) != 4:
        raise ValueError('原LUT缓存格式不符')
    binaries, lut_identities = [], []
    for row in cached['records']:
        binary = (cache_path.parent / row['path']).resolve()
        if not binary.is_relative_to(cache_path.parent) or binary.stat().st_size != LUT_BYTES or digest(binary) != row['binary_sha256'] or digest(row['source']) != row['source_sha256']:
            raise ValueError('LUT源或缓存身份不匹配')
        binaries.append(str(binary))
        lut_identities.append({'source': identity(row['source']), 'cache': identity(binary)})
    originals = input_records(args.images, 4 if args.screen else 100)
    output = new_directory(args.output)
    (output / 'inputs').mkdir()
    executed = []
    for i, row in enumerate(originals, 1):
        target = output / 'inputs' / f'image-{i}.bin'
        shutil.copyfile(row['path'], target)
        actual = identity(target)
        if actual['sha256'] != row['sha256']:
            raise ValueError('图片复制期间身份改变')
        actual['fnv1a64'] = fnv(target)
        executed.append(actual)
    image_list = output / 'images.txt'
    image_list.write_text(''.join(row['path'] + '\n' for row in executed), encoding='utf-8', newline='\n')
    list_before, original_list_before, cache_before = identity(image_list), identity(args.images), identity(cache_path)
    before = source_ids()
    command = [str(executable), '--cache', *binaries, '--images', str(image_list), '--output', str(output / 'native'),
               '--reps', str(args.reps or (5 if args.screen else 7)), '--aa-reps', str(args.aa_reps),
               '--warmup', str(args.warmup), '--seed', str(args.seed), '--aa-limit', str(args.aa_limit), '--variant', args.variant]
    if args.screen:
        command.append('--screen')
    execution = {'schema': 'rgb24_regression_execution_v1', 'command': command, 'cwd': str(ROOT),
                 'build': receipt, 'cache_manifest': cache_before, 'source_luts': lut_identities,
                 'original_images': originals, 'executed_images': executed, 'original_image_list': original_list_before,
                 'executed_image_list': list_before, 'platform': platform.platform(), 'cpu': platform.processor(),
                 'python': platform.python_version(), 'psutil': psutil.__version__, 'affinity': [args.affinity],
                 'fit_uses_images': False, 'scope': '同进程同表，先从四原LUT生成framework-step m33 chain_ls，再读取图片。'}
    save(output / 'execution.json', execution)
    started = time.perf_counter()
    peak_rss, max_threads, observations, affinity = 0, 0, 0, None
    with (output / 'stdout.log').open('xb') as stdout, (output / 'stderr.log').open('xb') as stderr:
        process = subprocess.Popen(command, cwd=ROOT, stdout=stdout, stderr=stderr, env=environment(receipt['compiler']))
        try:
            observer = psutil.Process(process.pid)
            observer.cpu_affinity([args.affinity])
            affinity = observer.cpu_affinity()
            if affinity != [args.affinity]:
                raise RuntimeError('绑核未成功')
            while process.poll() is None:
                try:
                    if observer.cpu_affinity() != affinity:
                        raise RuntimeError('执行期间绑核改变')
                    peak_rss = max(peak_rss, observer.memory_info().rss)
                    max_threads = max(max_threads, observer.num_threads())
                    observations += 1
                except psutil.NoSuchProcess:
                    if process.poll() is None:
                        raise
                    break
                time.sleep(.1)
            code = process.wait()
        except Exception:
            if process.poll() is None:
                process.terminate()
            process.wait()
            raise
        child_wall = (time.perf_counter() - started) * 1000
    unchanged = source_ids() == before and digest(executable) == receipt['executable_sha256']
    unchanged = unchanged and identity(image_list) == list_before and identity(args.images) == original_list_before and identity(cache_path) == cache_before
    unchanged = unchanged and all(identity(row['path']) == row for row in originals)
    unchanged = unchanged and all(identity(row['path']) == {key: row[key] for key in ('path', 'bytes', 'sha256')} for row in executed)
    unchanged = unchanged and all(identity(row[k]['path']) == row[k] for row in lut_identities for k in ('source', 'cache'))
    native_path = output / 'native/results.json'
    native = read(native_path) if native_path.exists() else None
    verified = validate_native(native, executed)
    artifacts = {path.name: identity(path) for path in (output / 'native').glob('*') if path.is_file()}
    summaries, speedups = summarize_native(native) if native else ([], [])
    completed = code in (0, 3) and unchanged and verified and bool(native and native['completed'])
    aa_complete = bool(native) and len(native['aa']) == 8 and all(row['passed'] for row in native['aa'])
    comparisons_complete = bool(native) and all(
        sum(run['phase'] == 'comparison' and run['scope'] == scope and run['kernel'] == kernel
            for run in native['runs']) == 2 * native['reps']
        for scope in ('hot', 'allocated') for kernel in ('legacy', args.variant))
    performance_valid = completed and not args.screen and native['stable'] is True and code == 0 and aa_complete and comparisons_complete
    summary = {'schema': 'rgb24_regression_summary_v1', 'completed': completed, 'returncode': code,
               'sources_inputs_exe_unchanged': unchanged, 'executed_input_output_verified': verified,
               'screen_only': args.screen, 'performance_valid': performance_valid,
               'aa': native['aa'] if native else [], 'observed_statistics': summaries,
               'descriptive_speedups': speedups, 'child_process_wall_ms': child_wall,
               'driver_validation_wall_ms': (time.perf_counter() - started) * 1000,
               'process_observation': {'peak_rss_bytes': peak_rss, 'max_threads': max_threads,
                                       'samples': observations, 'affinity': affinity,
                                       'scope': '含拟合/原表/共享表/全部图像；进程线程数不等于算法线程数。'},
               'native_artifacts': artifacts, 'official_score_available': False,
               'scope': 'screen仅描述4图现象；正式前后双方A/A均须通过才赋予performance_valid。hot与allocated分开，后者仍是直接核加fresh输出，原框架最终确认另测。失败原始样本保留。'}
    save(output / 'summary.json', summary)
    return {'completed': completed, 'returncode': code if completed else 1,
            'performance_valid': performance_valid, 'summary': str(output / 'summary.json')}


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest='action', required=True)
    child = sub.add_parser('build')
    child.add_argument('--compiler', type=Path, default=Path('E:/mingw64/bin/g++.exe'))
    child.add_argument('--output', type=Path, required=True)
    child = sub.add_parser('run')
    child.add_argument('--exe', type=Path, required=True)
    child.add_argument('--cache', type=Path, required=True)
    child.add_argument('--images', type=Path, required=True)
    child.add_argument('--output', type=Path, required=True)
    child.add_argument('--screen', action='store_true')
    child.add_argument('--variant', choices=('cached', 'stream'), default='stream')
    child.add_argument('--reps', type=int)
    child.add_argument('--aa-reps', type=int, default=7)
    child.add_argument('--warmup', type=int, default=2)
    child.add_argument('--seed', type=int, default=20261030)
    child.add_argument('--aa-limit', type=float, default=.05)
    child.add_argument('--affinity', type=int, default=16)
    args = parser.parse_args(argv)
    try:
        result = build(args) if args.action == 'build' else run(args)
        print(json.dumps(result, ensure_ascii=False, indent=2))
        return result.get('returncode', 0)
    except Exception as error:
        print(json.dumps({'completed': False, 'error': str(error)}, ensure_ascii=False))
        return 1


if __name__ == '__main__':
    raise SystemExit(main())
