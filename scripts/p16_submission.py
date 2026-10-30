"""第16题CPU交付包与固定四级模型百图入口；不替代新LUT的离线拟合。"""
from __future__ import annotations

import argparse
from contextlib import ExitStack
import json
import math
import os
from pathlib import Path
import re
import shutil
import statistics
import struct
import time
import traceback

import numpy as np
from PIL import Image

import p16_unified_support as native

ROOT = Path(__file__).resolve().parents[1]
SCHEMA = 'p16_cpu_submission_v1'
INTERPOLATION_BASIS = 'tetra_q16'
CINEMA_LICENSE_SHA256 = 'f9ec0414792341c7d72b8a95049ba770d543357836d4cfe71ec103460fdb242c'
THREAD_ENV = ('OMP_NUM_THREADS', 'OMP_WAIT_POLICY', 'OPENBLAS_NUM_THREADS', 'MKL_NUM_THREADS')


def write_json(path, value):
    Path(path).write_text(json.dumps(value, ensure_ascii=False, indent=2, allow_nan=False) + '\n', encoding='utf-8')


def _record(path, root):
    return {'path': path.relative_to(root).as_posix(), 'sha256': native.digest(path), 'bytes': path.stat().st_size}


def _source(record, root):
    if not isinstance(record, dict) or not re.fullmatch('[0-9a-f]{64}', record.get('sha256', '')):
        raise ValueError('源记录必须包含path与64位小写SHA256')
    path = Path(record['path'])
    path = (root / path).resolve() if not path.is_absolute() else path.resolve()
    if native.digest(path) != record['sha256']:
        raise ValueError('源文件摘要不符：' + str(path))
    return path


def _slut(path):
    payload = path.read_bytes()
    if len(payload) < 16 or payload[:4] != b'SLUT':
        raise ValueError('SLUT头无效：' + str(path))
    version, m, reserved = struct.unpack_from('<III', payload, 4)
    if version != 1 or reserved or not 17 <= m <= 33 or len(payload) != 16 + 12*m + 768 + 3072 + m**3*3:
        raise ValueError('SLUT版本、m或长度不符合四级RGB8合同')
    grid = np.frombuffer(payload, '<f4', 3*m, 16).reshape(3, m)
    idx = np.frombuffer(payload, np.uint8, 768, 16 + 12*m).reshape(3, 256)
    frac = np.frombuffer(payload, '<u4', 768, 16 + 12*m + 768).reshape(3, 256)
    if (not np.isfinite(grid).all() or not np.all(np.diff(grid, axis=1) > 0)
            or np.any(grid[:, 0] > 0) or np.any(grid[:, -1] < 255)
            or np.any(idx > m - 2) or np.any(frac > 65536)):
        raise ValueError('SLUT轴表或节点尺寸不合法')
    return m, idx.copy()


def _sidecar(path, idx, m):
    if path.stat().st_size != 3*3*256*4:
        raise ValueError('侧表必须为小端u32[3][3][256]')
    fractions = np.fromfile(path, dtype='<u4').reshape(3, 3, 256)
    coordinates = idx[None].astype(np.int64)*65536 + fractions.astype(np.int64)
    if (np.any(fractions > 65536) or np.any(np.diff(coordinates, axis=2) < 0)
            or np.any(coordinates[:, :, 0] != 0)
            or np.any(coordinates[:, :, -1] != (m - 1)*65536)):
        raise ValueError('侧表有效坐标或端点不合法')


def _basis_declaration(value, inherited=None, *, required=False):
    basis = value.get('interpolation_basis', inherited)
    if ('interpolation_basis' in value and basis != INTERPOLATION_BASIS) or (required and basis != INTERPOLATION_BASIS):
        raise ValueError('统一库仅支持tetra_q16插值；用户清单须明确声明相同basis，不能把tri模型当作tetra运行')
    for key in ('stage_interpolators', 'stage_kinds'):
        if key not in value:
            continue
        stages = value[key]
        if not isinstance(stages, list) or len(stages) != 4:
            raise ValueError(key + '必须明确列出四级tetra_q16插值')
        for stage in stages:
            if not ((type(stage) is int and stage == 0)
                    or (type(stage) is str and stage in ('0', 'tetra', 'tetra_q16', 'tetrahedral'))):
                raise ValueError(key + '含非tetra_q16阶段；tri或kind=1不能由统一库执行')
    return basis


def pack(manifest_path, output, source_root=None):
    manifest_path, output = Path(manifest_path).resolve(), Path(output).resolve()
    if output.exists():
        raise FileExistsError('交付目录已存在，拒绝覆盖')
    original = json.loads(manifest_path.read_text(encoding='utf-8'))
    if source_root is not None:
        root = Path(source_root).resolve()
    elif 'path_root' in original or 'source_root' in original:
        root = Path(original.get('path_root', original.get('source_root')))
        root = root.resolve() if root.is_absolute() else (manifest_path.parent / root).resolve()
    else:
        root = ROOT  # 兼容既有data/p16-unified-models/manifest.json。
    if not original.get('profiles') or original.get('default_profile') not in original['profiles']:
        raise ValueError('清单需要profiles及有效default_profile')
    known_manifests = {ROOT / 'data/p16-unified-models/manifest.json', ROOT / 'data/p16-score-models/manifest.json',
        ROOT / 'submission/p16-cpu-source-manifest.json'}
    known_cinema = manifest_path in known_manifests
    basis = _basis_declaration(original, INTERPOLATION_BASIS if known_cinema else None)
    for row in original['profiles'].values():
        _basis_declaration(row, basis, required=True)
    output.mkdir(parents=True)
    (output / 'objects').mkdir()
    (output / 'licenses').mkdir()
    objects, profiles, logical_bytes, logical_records = {}, {}, 0, 0

    def copy_object(record):
        nonlocal logical_bytes, logical_records
        path = _source(record, root)
        key = record['sha256']
        destination = output / 'objects' / key
        if not destination.exists():
            shutil.copyfile(path, destination)
        if native.digest(destination) != key:
            raise ValueError('拷贝后的对象摘要不符')
        result = _record(destination, output)
        objects[key] = result
        logical_bytes += result['bytes']
        logical_records += 1
        return result, path

    for name, row in original['profiles'].items():
        if not isinstance(name, str) or not name:
            raise ValueError('profile名称必须为非空字符串')
        if len(row['models']) != 4 or len(row['sidecars']) != 4:
            raise ValueError('每个profile固定四级SLUT和四个对应侧表槽')
        models, sidecars, sizes = [], [], []
        for model, side in zip(row['models'], row['sidecars']):
            copied, source = copy_object(model)
            m, idx = _slut(source)
            if 'm' in model and model['m'] != m:
                raise ValueError('模型记录m与SLUT头不一致')
            copied['m'] = m
            models.append(copied)
            sizes.append(m)
            if side:
                copied_side, source_side = copy_object(side)
                _sidecar(source_side, idx, m)
                sidecars.append(copied_side)
            else:
                sidecars.append(None)
        profiles[name] = {'models': models, 'sidecars': sidecars, 'm': sizes,
            'fixed_for_entire_batch': True, 'kernel_policy': 'avx2_preferred',
            'interpolation_basis': INTERPOLATION_BASIS,
            'oracle_sha256': row.get('oracle_sha256'),
            'semantics_note': row.get('semantics_note', '保留源清单模型；sidecar为分输出坐标研究表示，格式许可需另确认')}
    license_records = original.get('licenses')
    if license_records is None:
        if known_cinema:
            path = root / 'data/p16-unified-models/LICENSE.stripedpurple'
            if not path.is_file():
                raise ValueError('已知Cinema清单缺少原MIT许可文本')
            license_records = [{'path': str(path), 'sha256': native.digest(path)}]
        else:
            license_records = []
    licenses = []
    for index, record in enumerate(license_records):
        source = _source(record, root)
        destination = output / 'licenses' / f'{index:02d}-{source.name}'
        shutil.copyfile(source, destination)
        licenses.append(_record(destination, output))
    if known_cinema and not any(record['sha256'] == CINEMA_LICENSE_SHA256 for record in licenses):
        raise ValueError('已知Cinema清单必须保留原MIT许可，不得静默省略')
    value = {'schema': SCHEMA, 'source_root': '.', 'default_profile': original['default_profile'],
        'interpolation_basis': INTERPOLATION_BASIS,
        'profiles': profiles, 'objects': objects, 'licenses': licenses,
        'policy': {'cpu_only': True, 'gpu_allowed': False, 'npu_allowed': False,
            'kernel': 'avx2_preferred', 'automatic_avx512': False, 'stages': 4,
            'interpolation_basis': INTERPOLATION_BASIS,
            'stage_io': 'RGB8整数；每级Q16 half-up', 'parameters_fixed_for_all_images': True},
        'source_manifest': {'path': str(manifest_path), 'sha256': native.digest(manifest_path)},
        'source_path_root': str(root), 'source_research': original.get('source_research'),
        'source_declaration': {'known_cinema_manifest': known_cinema,
            'license_status': 'provided' if licenses else 'not_provided',
            'statement': '按原字节保留清单提供的许可；打包不代表发布授权。' if licenses
                else '用户清单未提供来源或许可声明；不推断第三方许可，打包不代表发布授权。'},
        'note': original.get('note', '新LUT须使用现有fit入口重新拟合并提供用户自己的清单'),
        'package_storage': {'logical_model_records': logical_records, 'logical_model_bytes': logical_bytes,
            'unique_model_objects': len(objects), 'unique_model_object_bytes': sum(v['bytes'] for v in objects.values()),
            'scope': '整文件SHA精确去重只减少交付包体；不表示运行时Model、图像或峰值RAM降低。'}}
    write_json(output / 'manifest.json', value)
    load_package(output)
    return value


def _package_record(record, root):
    path = (root / record['path']).resolve()
    if not path.is_relative_to(root) or not path.is_file():
        raise ValueError('包对象路径必须位于交付目录内')
    if path.stat().st_size != record['bytes'] or native.digest(path) != record['sha256']:
        raise ValueError('包对象大小或摘要不符：' + str(path))
    return {'path': str(path), 'sha256': record['sha256']}


def load_package(directory):
    root = Path(directory).resolve()
    manifest_path = root / 'manifest.json'
    manifest = json.loads(manifest_path.read_text(encoding='utf-8'))
    policy = manifest['policy']
    if policy.get('interpolation_basis') != INTERPOLATION_BASIS:
        raise ValueError('统一库交付策略必须明确为tetra_q16插值')
    _basis_declaration(manifest, policy['interpolation_basis'], required=True)
    if (manifest.get('schema') != SCHEMA or manifest.get('source_root') != '.'
            or policy.get('cpu_only') is not True or policy.get('gpu_allowed') is not False
            or policy.get('npu_allowed') is not False or policy.get('automatic_avx512') is not False
            or policy.get('kernel') != 'avx2_preferred' or policy.get('stages') != 4
            or policy.get('parameters_fixed_for_all_images') is not True):
        raise ValueError('交付包不符合CPU固定四级模型策略')
    declaration = manifest.get('source_declaration', {})
    if (declaration.get('known_cinema_manifest') is True and not any(
            record['sha256'] == CINEMA_LICENSE_SHA256 for record in manifest.get('licenses', []))):
        raise ValueError('已知Cinema交付包缺少原MIT许可记录')
    if not manifest.get('licenses') and declaration.get('license_status') != 'not_provided':
        raise ValueError('未提供许可的用户包须明确记录来源声明缺失')
    for record in [*manifest['objects'].values(), *manifest['licenses']]:
        _package_record(record, root)
    models = {}
    for name, row in manifest['profiles'].items():
        if row.get('interpolation_basis') != INTERPOLATION_BASIS:
            raise ValueError('profile必须明确记录tetra_q16插值')
        _basis_declaration(row, required=True)
        if (len(row['models']) != 4 or len(row['sidecars']) != 4 or row.get('fixed_for_entire_batch') is not True
                or row.get('kernel_policy') != 'avx2_preferred'):
            raise ValueError('profile不符合固定四级模型策略')
        model_records, side_records, sizes = [], [], []
        for record, side in zip(row['models'], row['sidecars']):
            checked = _package_record(record, root)
            m, idx = _slut(Path(checked['path']))
            if record['m'] != m:
                raise ValueError('包内SLUT的m记录不一致')
            model_records.append(checked)
            sizes.append(m)
            if side:
                side_checked = _package_record(side, root)
                _sidecar(Path(side_checked['path']), idx, m)
                side_records.append(side_checked)
            else:
                side_records.append(None)
        if row['m'] != sizes:
            raise ValueError('profile的四级m记录不一致')
        models[name] = {'models': model_records, 'sidecars': side_records, 'm': sizes,
            'interpolation_basis': INTERPOLATION_BASIS}
    return manifest, models, {'path': str(manifest_path), 'sha256': native.digest(manifest_path)}


def _rgb8(path):
    with Image.open(path) as image:
        if image.mode != 'RGB' or image.size != (1024, 768):
            raise ValueError('测试图像必须为1024×768 RGB8：' + str(path))
        # Pillow会把16位RGB PNG转换成mode=RGB，必须检查源容器的真实位深。
        if image.format == 'PNG':
            with path.open('rb') as stream:
                header = stream.read(29)
            if header[:8] != b'\x89PNG\r\n\x1a\n' or header[24:26] != bytes((8, 2)):
                raise ValueError('PNG源必须为8位真彩RGB，不接收静默降位深')
        elif image.format == 'JPEG':
            if getattr(image, 'bits', None) != 8:
                raise ValueError('JPEG源必须为8位RGB')
        elif image.format == 'TIFF':
            bits = image.tag_v2.get(258, ())
            if tuple(bits) != (8, 8, 8):
                raise ValueError('TIFF源必须明确为3×8位RGB')
        elif image.format not in ('BMP', 'WEBP'):
            raise ValueError('当前入口支持RGB8 PNG/JPEG/TIFF/BMP/WebP')
        image.load()
        array = np.asarray(image)
        if array.dtype != np.uint8 or array.shape != (768, 1024, 3):
            raise ValueError('图像解码结果不符合RGB8')
        return array


def image_paths(listing, image_root):
    lines = [line.strip() for line in Path(listing).read_text(encoding='utf-8-sig').splitlines() if line.strip()]
    if len(lines) != 100:
        raise ValueError('批次清单必须包含正好100个非空图像路径')
    root = Path(image_root).resolve()
    return [(Path(line) if Path(line).is_absolute() else root / line).resolve() for line in lines]


def _error_row(prediction, truth):
    difference = prediction.astype(np.int32) - truth.astype(np.int32)
    squared = np.sum(difference*difference, axis=-1, dtype=np.int32)
    distance = np.sqrt(squared.astype(np.float64))
    return {'pixels': int(distance.size), 'delta_e_sum': float(distance.sum(dtype=np.float64)),
        'mean_delta_e': float(distance.mean(dtype=np.float64)),
        'max_delta_e': float(distance.max()), 'p99_delta_e': float(np.percentile(distance, 99))}


def accuracy_summary(rows, threshold):
    count = sum(row['pixels'] for row in rows)
    if count <= 0:
        raise ValueError('精度统计需要至少一个像素')
    mean = math.fsum(row['delta_e_sum'] for row in rows) / count
    passing = None if threshold is None else all(row['mean_delta_e'] < threshold for row in rows)
    return {'pixel_weighted_mean_delta_e': mean, 'pixels': count,
        'threshold_strict': threshold, 'all_image_mean_pass': passing,
        'aggregate_mean_pass': None if threshold is None else mean < threshold,
        'threshold_origin': '未提供' if threshold is None else '调用者提供；未声明为官方阈值',
        'official_threshold_pass': None, 'official_score_available': False, 'per_image': rows,
        'scope': '每张图所有像素RGB欧氏距离平均，门为未舍入mean严格<T；总均值按像素数加权，p99/max仅诊断。'}


def _reference(frames, target, paths, threshold):
    records = []
    with ExitStack() as stack:
        tables = []
        for value in paths:
            path = Path(value).resolve()
            if path.stat().st_size != (1 << 24)*3:
                raise ValueError('密集参考LUT必须含256³个RGB8节点')
            records.append({'path': str(path), 'sha256': native.digest(path), 'bytes': path.stat().st_size})
            table = np.memmap(path, dtype=np.uint8, mode='r', shape=(256, 256, 256, 3))
            stack.callback(table._mmap.close)
            tables.append(table)
        rows = []
        for index, frame in enumerate(frames):
            truth = frame
            for table in tables:
                truth = table[truth[:, :, 0], truth[:, :, 1], truth[:, :, 2]]
            rows.append({'index': index, **_error_row(target[index], truth)})
    for record in records:
        if native.digest(record['path']) != record['sha256']:
            raise ValueError('精度校验期间参考LUT改变')
    return {'sources': records, **accuracy_summary(rows, threshold),
        'reference_execution': '四张原始密集LUT独立按级RGB8直接查表；仅用于计时外校验，未参与映射或按图调参。'}


def run(args):
    if not 1 <= args.repeats <= 100 or not 1 <= args.threads <= 256:
        raise ValueError('repeats应为1..100，threads应为1..256')
    if args.threshold is not None and (not math.isfinite(args.threshold) or args.threshold < 0 or not args.reference_luts):
        raise ValueError('阈值须有限非负，且必须提供四张参考LUT')
    output = args.output.resolve()
    if output.exists():
        raise FileExistsError('运行输出目录已存在，拒绝覆盖')
    output.mkdir(parents=True)
    manifest, profiles, package_record = load_package(args.package)
    name = args.profile or manifest['default_profile']
    if name not in profiles:
        raise ValueError('包内不存在所选profile：' + name)
    profile = profiles[name]
    paths = image_paths(args.images, args.image_root)
    native.setup(args.dll_directory, args.cpus)
    library = native.Library(args.library)
    if library.revision != 102:
        raise ValueError('此交付入口要求修订102统一CPU C ABI')
    backend = 'avx2' if library.supported('avx2') else 'scalar'
    environment = native.environment(args.build_receipt)
    environment['script_sha256'].update(native.script_records(__file__))
    environment['thread_environment'] = {key: os.environ.get(key) for key in THREAD_ENV}
    environment['requested_native_threads'] = args.threads
    environment['selected_backend'] = backend
    freeze = {'package': package_record, 'profile': name, 'models': profile, 'library': library.record(),
        'environment': environment, 'kernel_policy': 'avx2_preferred', 'selected_backend': backend,
        'gpu_used': False, 'npu_used': False, 'automatic_avx512': False,
        'images': {'list_path': str(args.images.resolve()), 'list_sha256': native.digest(args.images),
            'image_root': str(args.image_root.resolve()), 'count': 100},
        'repeats': args.repeats, 'warmup_batches_after_first_output': 1}
    write_json(output / 'executed-plan.json', freeze)
    started_application = time.perf_counter_ns()
    frames = np.empty((100, 768, 1024, 3), np.uint8)
    image_records = []
    for index, path in enumerate(paths):
        digest = native.digest(path)
        frames[index] = _rgb8(path)
        image_records.append({'index': index, 'path': str(path), 'file_sha256': digest,
            'pixel_sha256': native.sha(frames[index])})
    target = np.empty_like(frames)
    target.fill(173)
    before_create = native.rss()
    started_create = time.perf_counter_ns()
    chain = library.create(profile, hint=frames.size // 3)
    try:
        first_apply, first_stopped = chain.apply(frames, target, backend, args.threads)
        create_first = (first_stopped - started_create)*1e-9
        if args.write_images:
            folder = output / 'images'
            folder.mkdir()
            for index, frame in enumerate(target):
                Image.fromarray(frame).save(folder / f'{index + 1:04d}.png')
        application_wall = (time.perf_counter_ns() - started_application)*1e-9
        first_hash = native.sha(target)
        first_per_image = [native.sha(frame) for frame in target]
        source_hash = native.sha(frames)
        state = native.diagnostics(chain)
        memory = {'before_create': before_create, 'after_first_output': native.rss(),
            'model_capacity_bytes': state['model_capacity_bytes'], 'source_image_bytes': frames.nbytes,
            'output_image_bytes': target.nbytes, 'explicit_image_buffers_bytes': frames.nbytes + target.nbytes,
            'scope': 'Model真实capacity与两份整百图缓冲；RSS/Private/进程峰值包含Python和allocator，不等于算法RAM；包体去重不计作运行RAM节省。'}
        warmup, _ = chain.apply(frames, target, backend, args.threads)
        if native.sha(target) != first_hash:
            raise RuntimeError('预热输出与首次输出不同')
        rounds, hashes = [], []
        for index in range(args.repeats):
            elapsed, _ = chain.apply(frames, target, backend, args.threads)
            actual = native.sha(target)
            if actual != first_hash:
                raise RuntimeError('第' + str(index) + '轮输出与首次输出不同')
            rounds.append(elapsed)
            hashes.append(actual)
        memory['after_benchmark_before_reference'] = native.rss()
        timings = {'prepare_native_seconds': chain.prepare_seconds, 'first_batch_apply_seconds': first_apply,
            'prepare_to_first_batch_continuous_wall_seconds': create_first,
            'read_images_to_first_output_application_wall_seconds': application_wall,
            'application_includes_write_images': bool(args.write_images), 'warmup_batch_seconds': warmup,
            'batch_apply_seconds_raw': rounds, 'batch_apply_seconds_median': statistics.median(rounds),
            'batch_apply_seconds_min': min(rounds), 'batch_apply_seconds_max': max(rounds),
            'scope': 'batch_apply包围单次百图C ABI映射，排除读图/哈希/分配；prepare含SLUT/sidecar读取和cache/direct准备，不含离线稀疏拟合；application从首张读图前至首批输出可用，含输入哈希/解码/双缓冲分配与准备，write_images时还含写盘。'}
        write_json(output / 'runtime.json', {'timings': timings, 'memory': memory, 'state': state,
            'batch_output_sha256': first_hash, 'per_image_output_sha256': first_per_image,
            'per_round_output_sha256': hashes})
    finally:
        chain.close()
    if native.sha(frames) != source_hash:
        raise RuntimeError('运行时改写了输入图像')
    memory['after_destroy_before_reference'] = native.rss()
    quality = ({'verified': False, 'threshold_strict': None, 'official_threshold_pass': None,
        'official_score_available': False, 'scope': '未提供四张参考LUT，未验拟合精度和官方门槛。'}
        if not args.reference_luts else {'verified': True, **_reference(frames, target, args.reference_luts, args.threshold)})
    if native.digest(package_record['path']) != package_record['sha256']:
        raise RuntimeError('运行期间包清单改变')
    for record in [*profile['models'], *[v for v in profile['sidecars'] if v]]:
        if native.digest(record['path']) != record['sha256']:
            raise RuntimeError('运行期间固定模型改变')
    if native.digest(library.path) != library.sha256:
        raise RuntimeError('运行期间原生库改变')
    result = {'completed': True, 'package': package_record, 'profile': name, 'fixed_models': profile,
        'library': library.record(), 'environment': environment, 'selected_backend': backend,
        'gpu_used': False, 'npu_used': False, 'parameters_fixed_for_all_images': True,
        'images': image_records, 'source_pixels_sha256': source_hash,
        'batch_output_sha256': first_hash, 'per_image_output_sha256': first_per_image,
        'per_round_output_sha256': hashes, 'timings': timings, 'memory': memory, 'state': state,
        'quality': quality, 'official_score_available': False,
        'local_accuracy_pass': quality.get('all_image_mean_pass'),
        'scope': '固定已准备四级模型的CPU百图入口；新LUT先离线拟合并生成自有manifest；不提供赛事分数。'}
    write_json(output / 'results.json', result)
    return result


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    commands = parser.add_subparsers(dest='command', required=True)
    packing = commands.add_parser('pack', help='按整文件SHA打包固定模型并保留许可证')
    packing.add_argument('--manifest', type=Path, default=ROOT / 'submission/p16-cpu-source-manifest.json')
    packing.add_argument('--source-root', type=Path)
    packing.add_argument('--output', type=Path, required=True)
    running = commands.add_parser('run', help='CPU固定profile映射100张RGB8图像')
    running.add_argument('--package', type=Path, required=True)
    running.add_argument('--profile')
    running.add_argument('--library', type=Path, required=True)
    running.add_argument('--images', type=Path, required=True)
    running.add_argument('--image-root', type=Path, required=True)
    running.add_argument('--output', type=Path, required=True)
    running.add_argument('--reference-luts', type=Path, nargs=4)
    running.add_argument('--threshold', type=float)
    running.add_argument('--repeats', type=int, default=7)
    running.add_argument('--threads', type=int, default=4)
    running.add_argument('--write-images', action='store_true')
    running.add_argument('--build-receipt', type=Path)
    running.add_argument('--dll-directory')
    running.add_argument('--cpus')
    args = parser.parse_args(argv)
    output_existed = args.output.exists()
    try:
        result = pack(args.manifest, args.output, args.source_root) if args.command == 'pack' else run(args)
    except BaseException:
        if not output_existed and args.output.is_dir() and not (args.output / 'results.json').exists():
            write_json(args.output / 'failure.json', {'completed': False, 'traceback': traceback.format_exc()})
        raise
    print(json.dumps({'command': args.command, 'output': str(args.output.resolve()),
        'profile': result.get('profile'), 'local_accuracy_pass': result.get('local_accuracy_pass'),
        'package_storage': result.get('package_storage')}, ensure_ascii=False))
    return 2 if result.get('local_accuracy_pass') is False else 0


if __name__ == '__main__':
    raise SystemExit(main())
