"""构建、缓存与单线程框架受控比较；LUT准备不使用图像，保留原始样本及失败。"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
from pathlib import Path
import platform
import shutil
import subprocess
import sys
import time

ROOT = Path(__file__).resolve().parents[1]
SOURCE_NAMES = ('framework/benchmark.cpp', 'framework/framework_io.hpp',
                'framework/flash_chroma_adapter.hpp', 'framework/fit_experiment.hpp',
                'framework/fit_chain_experiment.hpp', 'include/flash_chroma.hpp', 'scripts/benchmark_framework.py')
VALUES = 256 ** 3 * 3


def digest(path):
    with Path(path).open('rb') as stream:
        return hashlib.file_digest(stream, 'sha256').hexdigest()


def fnv1a64_file(path):
    """与C++已读像素身份交叉核对；不用于模型拟合或计时排名。"""
    value = 14695981039346656037
    with Path(path).open('rb') as stream:
        while block := stream.read(1024 * 1024):
            for byte in block:
                value = ((value ^ byte) * 1099511628211) & 0xffffffffffffffff
    return f'{value:016x}'


def executed_input_identity(result, records, width, height):
    if not isinstance(result, dict) or result.get('width') != width or result.get('height') != height:
        return False
    images = result.get('images')
    if result.get('image_count') != len(records) or not isinstance(images, list) or len(images) != len(records):
        return False
    return all(actual.get('index') == expected['index'] and
               actual.get('input_fnv1a64') == expected['fnv1a64']
               for actual, expected in zip(images, records))


def read(path):
    return json.loads(Path(path).read_text(encoding='utf-8-sig'))


def save_new(path, value):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open('x', encoding='utf-8', newline='\n') as stream:
        json.dump(value, stream, ensure_ascii=False, indent=2, allow_nan=False)
        stream.write('\n')


def sources():
    return {name: digest(ROOT / name) for name in SOURCE_NAMES}


def new_directory(path):
    path = Path(path).resolve()
    path.mkdir(parents=True, exist_ok=False)
    return path


def environment():
    result = {'platform': platform.platform(), 'python': sys.version,
              'cpu': platform.processor(), 'machine': platform.machine(),
              'cpu_only': True, 'requested_threads': 1}
    try:
        import psutil
        result.update(psutil=psutil.__version__, logical_cpus=psutil.cpu_count(),
                      physical_cpus=psutil.cpu_count(logical=False),
                      available_affinity=psutil.Process().cpu_affinity())
    except (ImportError, AttributeError, OSError) as error:
        result['process_observation_unavailable'] = str(error)
    return result


def child_environment(executable=None):
    result = os.environ.copy()
    for name in ('OMP_NUM_THREADS', 'OPENBLAS_NUM_THREADS', 'MKL_NUM_THREADS', 'NUMEXPR_NUM_THREADS'):
        result[name] = '1'
    result['OMP_WAIT_POLICY'] = 'PASSIVE'
    # 运行库与可执行文件同目录优先，其次保留调用者配置的PATH。
    if executable:
        result['PATH'] = str(Path(executable).parent) + os.pathsep + result.get('PATH', '')
    return result


def runtime_environment(executable, build_receipt):
    result = child_environment(executable)
    result['PATH'] = str(Path(build_receipt['compiler']).parent) + os.pathsep + result.get('PATH', '')
    return result


def build(args):
    output = new_directory(args.output)
    compiler = Path(args.compiler).resolve()
    before = sources()
    executable = output / ('framework_benchmark.exe' if os.name == 'nt' else 'framework_benchmark')
    command = [str(compiler), '-std=c++17', '-O3', '-DNDEBUG', '-DFLASH_CHROMA_ENABLE_OPENMP=0',
               '-Wall', '-Wextra', '-Wpedantic', '-I', str(ROOT / 'framework'), '-I', str(ROOT / 'include'),
               str(ROOT / 'framework/benchmark.cpp'), '-o', str(executable)]
    process = subprocess.run(command, cwd=ROOT, capture_output=True, env=child_environment(compiler))
    (output / 'build-stdout.log').write_bytes(process.stdout)
    (output / 'build-stderr.log').write_bytes(process.stderr)
    if process.returncode:
        save_new(output / 'failure.json', {'completed': False, 'command': command, 'returncode': process.returncode})
        raise RuntimeError('构建失败，见build-stderr.log')
    if sources() != before:
        raise RuntimeError('构建期间源码改变，拒绝绑定')
    version = subprocess.check_output([str(compiler), '--version'], env=child_environment(compiler)).decode('utf-8', 'replace')
    receipt = {'schema': 'framework_benchmark_build_v1', 'command': command,
               'compiler': str(compiler), 'compiler_sha256': digest(compiler), 'compiler_version': version,
               'sources': before, 'executable_sha256': digest(executable), 'executable': str(executable),
               'openmp_enabled': False, 'cpu_only': True, 'threads': 1}
    save_new(str(executable) + '.build.json', receipt)
    return receipt


def check_executable(path):
    path = Path(path).resolve()
    receipt = read(str(path) + '.build.json')
    if receipt.get('schema') != 'framework_benchmark_build_v1' or receipt['executable_sha256'] != digest(path):
        raise ValueError('可执行文件与构建回执不符')
    if receipt['sources'] != sources() or receipt.get('openmp_enabled') is not False or receipt.get('threads') != 1:
        raise ValueError('构建来源或单线程配置不符，请重新build')
    return path, receipt


def cache(args):
    executable, build_receipt = check_executable(args.exe)
    framework = Path(args.framework).resolve()
    output = new_directory(args.output)
    records, unique = [], {}
    started = time.perf_counter()
    for index in range(1, 5):
        source = framework / 'data/LUT' / f'Test{index}.3DL'
        source_sha = digest(source)
        if source_sha not in unique:
            binary = output / (source_sha + '.u16le')
            # 输入用相对路径，避免旧MinGW窄argv对中文路径的本地代码页差异。
            command = [str(executable), '--cache-one', f'Test{index}.3DL', str(binary)]
            process = subprocess.run(command, cwd=source.parent, capture_output=True, env=runtime_environment(executable, build_receipt))
            (output / f'parse-{index}-stdout.log').write_bytes(process.stdout)
            (output / f'parse-{index}-stderr.log').write_bytes(process.stderr)
            if process.returncode:
                save_new(output / 'failure.json', {'completed': False, 'command': command, 'returncode': process.returncode})
                raise RuntimeError('3DL严格解析失败，保留原日志')
            parsed = json.loads(process.stdout)
            if parsed['values'] != VALUES or binary.stat().st_size != VALUES * 2 or digest(source) != source_sha:
                raise ValueError('3DL解析计数或来源身份不符')
            unique[source_sha] = {'path': binary.name, 'binary_sha256': digest(binary),
                                  'bytes': binary.stat().st_size, 'parse': parsed}
        records.append({'stage': index, 'source': str(source), 'source_sha256': source_sha,
                        'source_bytes': source.stat().st_size, **unique[source_sha]})
    value = {'schema': 'framework_lut_u16_cache_v1', 'format': 'u16le-file-order',
             'value_count': VALUES, 'records': records, 'unique_tables': len(unique),
             'offline_wall_ms': (time.perf_counter() - started) * 1000,
             'build': build_receipt, 'framework_readme_sha256': digest(framework / 'Readme.md'),
             'scope': '保留3DL原行序的uint16小端缓存；未转轴/通道、未除16、不使用图片。重复SHA只去重存储。'}
    save_new(output / 'manifest.json', value)
    return value


def default_candidates(matrix, budget):
    result = [f'framework17-sparse-scalar,17,17,17,17,framework,0,1,0,65536,{budget}']
    for m in (17, 25, 33):
        for label, structure, backend in (('structure', 1, 0), ('sparse-scalar', 0, 1), ('sparse-avx2', 0, 2)):
            result.append(f'm{m}-{label},{m},{m},{m},{m},uniform,{structure},{backend},0,65536,{budget}')
    if matrix == 'extended':
        for label, representation in (('u8', 1), ('u16', 2), ('rgb24', 3)):
            for backend in (1, 2):
                result.append(f'm33-direct-{label}-{backend},33,33,33,33,uniform,0,{backend},{representation},65536,{budget}')
    return result


def image_records(path, width, height):
    path = Path(path).resolve()
    result = []
    for line in path.read_text(encoding='utf-8-sig').splitlines():
        if not line or line.startswith('#'):
            continue
        image = Path(line)
        image = (image if image.is_absolute() else path.parent / image).resolve()
        if image.stat().st_size != width * height * 3:
            raise ValueError('RGB输入字节数不符：' + str(image))
        result.append({'path': str(image), 'sha256': digest(image), 'bytes': image.stat().st_size})
    if not result:
        raise ValueError('没有输入图片')
    return result


def run(args):
    executable, build_receipt = check_executable(args.exe)
    cache_path = Path(args.cache).resolve()
    cached = read(cache_path)
    if cached.get('schema') != 'framework_lut_u16_cache_v1' or cached.get('format') != 'u16le-file-order' or cached.get('value_count') != VALUES or len(cached['records']) != 4:
        raise ValueError('缓存清单格式不符')
    binaries = []
    for record in cached['records']:
        path = (cache_path.parent / record['path']).resolve()
        if not path.is_relative_to(cache_path.parent) or path.stat().st_size != VALUES * 2 or digest(path) != record['binary_sha256']:
            raise ValueError('缓存字节身份不符')
        if digest(record['source']) != record['source_sha256']:
            raise ValueError('原3DL已改变，不能沿用旧缓存')
        binaries.append(str(path))
    images = image_records(args.images, args.width, args.height)
    output = new_directory(args.output)
    # 使用自己的只读副本固定输入身份，同时避免MinGW读取UTF8清单路径的代码页歧义。
    (output / 'inputs').mkdir()
    input_lines, executed_images = [], []
    for index, record in enumerate(images, 1):
        name = f'image-{index}.bin'
        target = output / 'inputs' / name
        shutil.copyfile(record['path'], target)
        if digest(target) != record['sha256']:
            raise ValueError('输入副本身份不符')
        input_lines.append('inputs/' + name)
        executed_images.append({'index': index, 'path': str(target), 'sha256': record['sha256'],
                                'bytes': record['bytes'], 'fnv1a64': fnv1a64_file(target)})
    image_list = output / 'images.txt'
    image_list.write_text('\n'.join(input_lines) + '\n', encoding='utf-8', newline='\n')
    image_list_sha = digest(image_list)
    candidates = args.candidate or default_candidates(args.matrix, args.workspace_mib * 1024 ** 2)
    command = [str(executable), '--lut-cache', *binaries, '--image-list', str(image_list), '--output', str(output / 'native'),
               '--width', str(args.width), '--height', str(args.height), '--reps', str(args.reps), '--aa-reps', str(args.aa_reps),
               '--warmup', str(args.warmup), '--seed', str(args.seed), '--aa-limit', str(args.aa_limit)]
    for candidate in candidates:
        command += ['--candidate', candidate]
    aa_config = args.aa_config or ('m33-sparse-avx2' if not args.candidate else None)
    if aa_config:
        command += ['--aa-config', aa_config]
    if args.threshold is not None:
        command += ['--threshold', str(args.threshold)]
    if args.write_outputs:
        command += ['--write-outputs']
    before = sources()
    execution = {'schema': 'framework_benchmark_execution_v1', 'command': command, 'cwd': str(ROOT),
                 'build': build_receipt, 'cache_manifest': str(cache_path), 'cache_manifest_sha256': digest(cache_path),
                 'source_luts': cached['records'], 'images': images, 'executed_images': executed_images,
                 'executed_image_list_sha256': image_list_sha, 'environment': environment(),
                 'candidate_plan': candidates, 'fit_uses_images': False,
                 'scope': '准备仅使用LUT；图像副本用于固定评价身份，不传入fit/prepare。未提供官方评分公式。'}
    save_new(output / 'execution.json', execution)
    started = time.perf_counter()
    rss_max, threads_max, affinity, observations = None, None, None, 0
    with (output / 'stdout.log').open('xb') as stdout, (output / 'stderr.log').open('xb') as stderr:
        process = subprocess.Popen(command, cwd=ROOT, stdout=stdout, stderr=stderr, env=runtime_environment(executable, build_receipt))
        observer = None
        try:
            import psutil
            observer = psutil.Process(process.pid)
            if args.affinity:
                observer.cpu_affinity([int(value) for value in args.affinity.split(',')])
            affinity = observer.cpu_affinity()
        except Exception as error:
            if args.affinity:
                process.terminate(); process.wait()
                save_new(output / 'failure.json', {'completed': False, 'error': '显式绑核未成功：' + str(error)})
                raise RuntimeError('不能静默忽略显式绑核') from error
            execution['observation_unavailable'] = str(error)
        while process.poll() is None:
            if observer:
                try:
                    rss_max = max(rss_max or 0, observer.memory_info().rss)
                    threads_max = max(threads_max or 0, observer.num_threads())
                    observations += 1
                except (OSError, psutil.Error):
                    pass
            time.sleep(.2)
        code = process.wait()
        child_process_wall_ms = (time.perf_counter() - started) * 1000
    unchanged = sources() == before and digest(executable) == build_receipt['executable_sha256']
    unchanged = unchanged and all(digest(row['path']) == row['sha256'] for row in images)
    unchanged = unchanged and all(digest(row['source']) == row['source_sha256'] for row in cached['records'])
    unchanged = unchanged and all(digest(path) == row['binary_sha256'] for path, row in zip(binaries, cached['records']))
    unchanged = unchanged and digest(image_list) == image_list_sha
    unchanged = unchanged and all(Path(row['path']).stat().st_size == row['bytes'] and
                                  digest(row['path']) == row['sha256'] for row in executed_images)
    result_path = output / 'native/results.json'
    result = read(result_path) if result_path.is_file() else None
    executed_inputs_verified = executed_input_identity(result, executed_images, args.width, args.height)
    outputs = {}
    for path in sorted((output / 'native/outputs').rglob('*.bin')):
        outputs[path.relative_to(output).as_posix()] = {'bytes': path.stat().st_size, 'sha256': digest(path)}
    driver_validation_wall_ms = (time.perf_counter() - started) * 1000
    summary = {'completed': code in (0, 3) and unchanged and executed_inputs_verified, 'returncode': code,
               'time_stable': bool(result and result.get('time_stable')), 'inputs_and_sources_unchanged': unchanged,
               'executed_input_identity_verified': executed_inputs_verified,
               'child_process_wall_ms': child_process_wall_ms,
               'driver_validation_wall_ms': driver_validation_wall_ms,
               'process_wall_ms': driver_validation_wall_ms,
               'process_wall_ms_alias_of': 'driver_validation_wall_ms',
               'wall_scope': 'child_process_wall_ms从启动前到wait结束立即记录，含进程创建和轮询观测延迟；driver_validation_wall_ms再含结束后SHA/输出核验，不含最终summary写盘；process_wall_ms为后者兼容别名。',
               'process_observation': {'peak_rss_observed_bytes': rss_max, 'max_threads_observed': threads_max,
                                       'affinity': affinity, 'samples': observations, 'interval_seconds': .2,
                                       'scope': '进程观测包含原表、全部已准备候选及参考/图像，不等于单候选运行RAM；采样可能漏过瞬时峰值。'},
               'output_files': outputs, 'raw_results_sha256': digest(result_path) if result else None,
               'official_score_available': False,
               'scope': 'A/A失败返回3并保留质量/原始A/A，不执行后续候选计时；所有输出全像素消费，FNV仅内部一致性，落盘另用SHA256。'}
    if result:
        valid = [c for c in result['candidates'] if c['ready'] and c.get('batch_median_ms') is not None]
        front = []
        for c in valid:
            resource = c['actual']['model_bytes'] + c['actual']['arena_bytes'] + c['actual']['object_bytes']
            point = c['worst_image_mean'], c['batch_median_ms'], resource
            dominated = False
            for other in valid:
                o = other['actual']; other_point = other['worst_image_mean'], other['batch_median_ms'], o['model_bytes'] + o['arena_bytes'] + o['object_bytes']
                if all(a <= b for a, b in zip(other_point, point)) and any(a < b for a, b in zip(other_point, point)):
                    dominated = True; break
            if not dominated:
                front.append({'id': c['id'], 'worst_image_mean': point[0], 'batch_median_ms': point[1], 'owned_runtime_bytes': point[2]})
        summary['observed_frontier'] = front
        if args.threshold is not None:
            feasible = [c for c in valid if c['all_image_mean_pass'] is True]
            summary['fastest_measured_under_threshold'] = min(feasible, key=lambda c: c['batch_median_ms'])['id'] if feasible else None
        else:
            summary['fastest_measured_under_threshold'] = None
    save_new(output / 'summary.json', summary)
    if not unchanged:
        raise RuntimeError('运行期间输入/源码/库改变，拒绝有效比较')
    if code in (0, 3) and not executed_inputs_verified:
        raise RuntimeError('实际执行图片身份、顺序或尺寸与固定副本不符，拒绝有效比较')
    return summary


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest='mode', required=True)
    p = sub.add_parser('build');p.add_argument('--compiler', type=Path, default=Path('E:/mingw64/bin/g++.exe'));p.add_argument('--output', type=Path, required=True)
    p = sub.add_parser('cache');p.add_argument('--exe', type=Path, required=True);p.add_argument('--framework', type=Path, required=True);p.add_argument('--output', type=Path, required=True)
    p = sub.add_parser('run');p.add_argument('--exe', type=Path, required=True);p.add_argument('--cache', type=Path, required=True);p.add_argument('--images', type=Path, required=True);p.add_argument('--output', type=Path, required=True)
    p.add_argument('--matrix', choices=('core','extended'), default='core');p.add_argument('--candidate', action='append', help='11项旧格式默认sample；第12项可选sample/independent_ls/chain_ls');p.add_argument('--workspace-mib', type=int, default=128)
    p.add_argument('--width', type=int, default=1024);p.add_argument('--height', type=int, default=768);p.add_argument('--reps', type=int, default=7);p.add_argument('--aa-reps', type=int, default=7)
    p.add_argument('--warmup', type=int, default=2);p.add_argument('--seed', type=int, default=20261029);p.add_argument('--aa-limit', type=float, default=.05);p.add_argument('--aa-config')
    p.add_argument('--threshold', type=float);p.add_argument('--affinity');p.add_argument('--write-outputs', action='store_true')
    args = parser.parse_args(argv)
    try:
        result = {'build': build, 'cache': cache, 'run': run}[args.mode](args)
        print(json.dumps(result, ensure_ascii=False, indent=2, allow_nan=False))
        return result.get('returncode', 0)
    except Exception as error:
        print(json.dumps({'completed': False, 'error': str(error)}, ensure_ascii=False), file=sys.stderr)
        return 1


if __name__ == '__main__':
    raise SystemExit(main())
