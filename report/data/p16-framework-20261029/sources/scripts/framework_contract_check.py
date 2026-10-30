"""独立核对比赛框架、原始3DL轴序/量化及候选RGB8输出；不测量性能。"""
from __future__ import annotations

import argparse
import hashlib
import json
import math
from pathlib import Path
import platform
import sys
import warnings

import numpy as np

SIDE = 256
IMAGE_SHAPE = (768, 1024, 3)
SCHEMA = 'flash_chroma_framework_oracle_v1'


def digest(path):
    with Path(path).open('rb') as stream:
        return hashlib.file_digest(stream, 'sha256').hexdigest()


def save_new(path, value):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open('x', encoding='utf-8', newline='\n') as stream:
        json.dump(value, stream, ensure_ascii=False, indent=2, allow_nan=False)
        stream.write('\n')


def record(path):
    path = Path(path).resolve()
    return {'path': str(path), 'bytes': path.stat().st_size, 'sha256': digest(path)}


def parse_source(path, side=SIDE):
    # loadtxt独立按行检查列数，不能把多列/少列跨行拼成合法三元组。
    # 部分NumPy版本会警告后将小数读入整数；审计不能容忍这种静默改写。
    with warnings.catch_warnings():
        warnings.simplefilter('error', DeprecationWarning)
        data = np.loadtxt(path, dtype=np.int32, comments=None, ndmin=2)
    if data.shape != (side ** 3, 3):
        raise ValueError('3DL须恰含256³行三整数，实际shape=' + str(data.shape))
    if data.min() < 0 or data.max() > 65535:
        raise ValueError('独立审计只接受uint16范围；不静默接受源整数溢出')
    return data


def normalize_reference(raw, side=SIDE):
    raw = np.asarray(raw)
    if raw.shape != (side ** 3, 3) or not np.issubdtype(raw.dtype, np.integer):
        raise ValueError('原始表必须是N³×3整数数组')
    if raw.min() < 0 or raw.max() > 65535:
        raise ValueError('原始表超出uint16范围')
    # 原框架：raw[((b*N+g)*N+r)*3+(2-c)] / 16，然后转uint8。
    # 特意保留截断和uint8转换；不采用四舍五入、裁剪或候选适配器的转换函数。
    quantized = (raw // 16).astype(np.uint8)
    return np.ascontiguousarray(quantized.reshape(side, side, side, 3).transpose(2, 1, 0, 3)[..., ::-1])


def separability_proof(dense):
    if dense.ndim != 4 or dense.shape[0] != dense.shape[1] or dense.shape[1] != dense.shape[2] or dense.shape[3] != 3:
        raise ValueError('证明对象必须是N×N×N×3')
    side = dense.shape[0]
    curves = np.stack((dense[:, 0, 0, 0], dense[0, :, 0, 1], dense[0, 0, :, 2]))
    expected = (curves[0, :, None, None], curves[1, None, :, None], curves[2, None, None, :])
    mismatches = [int(np.count_nonzero(dense[..., channel] != expected[channel])) for channel in range(3)]
    return {'verified_all_nodes': True, 'checked_nodes': side ** 3,
            'checked_channel_values': side ** 3 * 3, 'mismatches_by_channel': mismatches,
            'separable': not any(mismatches), 'curves_rgb': curves.tolist() if not any(mismatches) else None,
            'scope': '独立NumPy检查全部规范化节点；未使用图像像素或候选结构证明。'}


def check_cache(cache_path, raw):
    cache_path = Path(cache_path)
    expected_bytes = raw.size * 2
    if cache_path.stat().st_size != expected_bytes:
        raise ValueError('缓存字节数不符：' + str(cache_path))
    cache = np.memmap(cache_path, mode='r', dtype='<u2', shape=raw.shape)
    equal = np.array_equal(cache, raw)
    del cache
    if not equal:
        raise ValueError('缓存与原始3DL三元组不一致：' + str(cache_path))
    return dict(record(cache_path), format='u16le-file-order', values_equal_to_original=True)


def inspect_framework(framework):
    framework = Path(framework).resolve()
    files = [record(framework / name) for name in ('Readme.md', 'C/main.c', 'C++/main.cpp')]
    luts = [record(framework / 'data/LUT' / ('Test%d.3DL' % i)) for i in range(1, 5)]
    images = []
    for i in range(1, 5):
        path = framework / 'data/image' / ('%d.bin' % i)
        item = record(path)
        if item['bytes'] != math.prod(IMAGE_SHAPE):
            raise ValueError('图片必须恰为1024×768 RGB8：' + str(path))
        images.append(dict(item, index=i, shape=list(IMAGE_SHAPE)))
    groups = {}
    for i, item in enumerate(luts, 1):
        groups.setdefault(item['sha256'], []).append(i)
    return {'schema': 'flash_chroma_framework_contract_v1', 'framework': str(framework),
            'files': files, 'luts': luts, 'images': images,
            'identical_lut_groups': [v for v in groups.values() if len(v) > 1],
            'environment': {'python': sys.version, 'numpy': np.__version__, 'platform': platform.platform()},
            'contract': {'threads': 1, 'gpu_npu_allowed': False, 'preprocess_timed': False,
                         'image_information_for_compression': False, 'm_range': [17, 33],
                         'official_thresholds': None, 'score_formula': None,
                         'template_image_loop': [1, 4], 'image_shape': list(IMAGE_SHAPE),
                         'mean_metric': 'mean(sqrt(dr²+dg²+db²))',
                         'reference_normalization': 'uint8(raw[((B*256+G)*256+R)*3+(2-C)]/16)'},
            'scope': '文件身份、现有四样图和已读源码合同；没有执行性能测试或推算官方分数。'}


def prepare(framework, output, cache_paths=()):
    output = Path(output).resolve()
    if output.exists():
        raise FileExistsError('输出目录已存在，拒绝覆盖：' + str(output))
    if cache_paths and len(cache_paths) != 4:
        raise ValueError('--cache应按四级顺序提供四条路径')
    contract = inspect_framework(framework)
    output.mkdir(parents=True)
    try:
        save_new(output / 'contract.json', contract)
        unique, stages = {}, []
        for index, source in enumerate(contract['luts']):
            key = source['sha256']
            if key not in unique:
                raw = parse_source(source['path'])
                source_range = [int(raw.min()), int(raw.max())]
                dense = normalize_reference(raw)
                proof = separability_proof(dense)
                path = output / ('reference-' + key[:16] + '.rgb8lut')
                with path.open('xb') as stream:
                    dense.tofile(stream)
                entry = {'source_sha256': key, 'source_value_range': source_range,
                         'within_documented_0_4080': source_range[0] >= 0 and source_range[1] <= 4080,
                         'dense': {'path': path.name, 'bytes': path.stat().st_size, 'sha256': digest(path)},
                         'proof': proof, 'caches': []}
                if cache_paths:
                    # 同SHA来源的全部候选缓存逐个核对，不能只接受首个路径。
                    for j, other in enumerate(contract['luts']):
                        if other['sha256'] == key:
                            entry['caches'].append(check_cache(cache_paths[j], raw))
                del dense, raw
                unique[key] = entry
            stages.append({'index': index + 1, 'source': source, 'normalized_key': key})
        for source in contract['luts'] + contract['files'] + contract['images']:
            if digest(source['path']) != source['sha256']:
                raise ValueError('独立准备期间输入被修改：' + source['path'])
        manifest = {'schema': SCHEMA, 'contract': contract, 'stages': stages, 'unique': unique,
                    'reference_format': 'uint8[R,G,B,C], B-fast, 256³×3',
                    'scope': '原始3DL严格解析及独立规范化/全域结构证明；非拟合、非计时、非官方得分。'}
        save_new(output / 'manifest.json', manifest)
        return {'passed': True, 'manifest': str(output / 'manifest.json'),
                'unique_luts': len(unique), 'separable': {k: v['proof']['separable'] for k, v in unique.items()}}
    except Exception as error:
        save_new(output / 'failure.json', {'completed': False, 'error': str(error)})
        raise


def metrics(expected, actual):
    if expected.shape != actual.shape:
        raise ValueError('像素shape不同')
    difference = actual.astype(np.int32) - expected.astype(np.int32)
    squared = np.sum(difference * difference, axis=-1, dtype=np.int32)
    return {'mean_rgb_distance': float(np.sqrt(squared.astype(np.float64)).mean()),
            'rms_rgb_distance': float(np.sqrt(squared.mean(dtype=np.float64))),
            'max_rgb_distance': float(np.sqrt(squared.max())),
            'different_pixels': int(np.count_nonzero(squared)), 'byte_equal': bool(np.array_equal(expected, actual))}


def load_image_list(path):
    path = Path(path).resolve()
    identity = record(path)
    lines = [line.strip() for line in path.read_text(encoding='utf-8-sig').splitlines() if line.strip()]
    if not lines:
        raise ValueError('补充图片列表不能为空')
    images, seen = [], set()
    for index, line in enumerate(lines, 1):
        entry = Path(line)
        resolved = (entry if entry.is_absolute() else path.parent / entry).resolve()
        if resolved in seen:
            raise ValueError('补充图片列表有重复路径：' + str(resolved))
        seen.add(resolved)
        item = record(resolved)
        if item['bytes'] != math.prod(IMAGE_SHAPE):
            raise ValueError('补充图片必须恰为1024×768 RGB8：' + str(resolved))
        images.append(dict(item, index=index, shape=list(IMAGE_SHAPE)))
    if digest(path) != identity['sha256']:
        raise ValueError('补充图片列表在读取期间改变')
    return images, identity


def image_scope(image_list):
    return 'supplemental_images' if image_list is not None else 'framework_samples'


def verify(oracle, candidate_dir, threshold=None, image_list=None):
    oracle = Path(oracle).resolve()
    value = json.loads(oracle.read_text(encoding='utf-8'))
    if value.get('schema') != SCHEMA:
        raise ValueError('不支持的独立参考schema')
    if threshold is not None and (not math.isfinite(threshold) or threshold < 0):
        raise ValueError('threshold必须是非负有限数')
    scope = image_scope(image_list)
    images, list_identity = load_image_list(image_list) if image_list is not None else (value['contract']['images'], None)
    before = digest(oracle)
    arrays = {}
    for key, entry in value['unique'].items():
        relative = Path(entry['dense']['path'])
        path = (oracle.parent / relative).resolve()
        if not path.is_relative_to(oracle.parent) or not path.is_file():
            raise ValueError('独立参考路径非法')
        if digest(path) != entry['dense']['sha256'] or path.stat().st_size != SIDE ** 3 * 3:
            raise ValueError('独立参考身份不符')
        arrays[key] = np.memmap(path, mode='r', dtype=np.uint8, shape=(SIDE, SIDE, SIDE, 3))
    records = []
    try:
        for item in images:
            if digest(item['path']) != item['sha256']:
                raise ValueError('输入图片身份改变：' + item['path'])
            expected = np.fromfile(item['path'], dtype=np.uint8).reshape(IMAGE_SHAPE)
            for stage in value['stages']:
                lut = arrays[stage['normalized_key']]
                expected = lut[expected[..., 0], expected[..., 1], expected[..., 2]]
            path = Path(candidate_dir) / ('image-%d.bin' % item['index'])
            candidate = record(path)
            if candidate['bytes'] != math.prod(IMAGE_SHAPE):
                raise ValueError('候选输出不是完整RGB8帧：' + str(path))
            actual = np.fromfile(path, dtype=np.uint8).reshape(IMAGE_SHAPE)
            observed = metrics(expected, actual)
            records.append({'index': item['index'], 'input_sha256': item['sha256'], 'candidate': candidate,
                            'reference_pixel_sha256': hashlib.sha256(expected.tobytes()).hexdigest(),
                            **observed, 'mean_strictly_below_threshold': None if threshold is None else observed['mean_rgb_distance'] < threshold})
        for item in value['contract']['luts'] + value['contract']['files']:
            if digest(item['path']) != item['sha256']:
                raise ValueError('原始框架或LUT身份改变：' + item['path'])
        if digest(oracle) != before:
            raise ValueError('参考清单在核对过程中被修改')
        if list_identity is not None and digest(list_identity['path']) != list_identity['sha256']:
            raise ValueError('补充图片列表在核对过程中被修改')
        return {'completed': True, 'oracle_sha256': before, 'images': len(records), 'records': records,
                'input_scope': scope, 'image_list': list_identity,
                'all_byte_equal': all(r['byte_equal'] for r in records), 'threshold': threshold,
                'all_image_mean_pass': None if threshold is None else all(r['mean_strictly_below_threshold'] for r in records),
                'official_score_available': False,
                'scope': ('原框架四图' if scope == 'framework_samples' else '显式补充图片列表，非框架原四图或官方测试集')
                         + '、四级密集查表独立NumPy参考；无性能计时，不据图片数量宣称正式验收。'}
    finally:
        arrays.clear()


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    commands = parser.add_subparsers(dest='mode', required=True)
    for mode in ('inspect', 'prepare'):
        command = commands.add_parser(mode)
        command.add_argument('--framework', type=Path, required=True)
        command.add_argument('--output', type=Path, required=True)
        if mode == 'prepare': command.add_argument('--cache', type=Path, nargs=4)
    command = commands.add_parser('verify')
    command.add_argument('--oracle', type=Path, required=True)
    command.add_argument('--candidate-dir', type=Path, required=True)
    command.add_argument('--image-list', type=Path, help='可选补充RGB8 bin列表；相对路径按列表目录解析，默认仍核对原框架四图')
    command.add_argument('--threshold', type=float)
    command.add_argument('--output', type=Path, required=True)
    args = parser.parse_args(argv)
    try:
        if args.mode == 'prepare':
            result = prepare(args.framework, args.output, args.cache or ())
        elif args.mode == 'inspect':
            result = inspect_framework(args.framework)
            save_new(args.output, result)
        else:
            if args.output.exists(): raise FileExistsError('输出已存在，拒绝覆盖')
            result = verify(args.oracle, args.candidate_dir, args.threshold, args.image_list)
            save_new(args.output, result)
        print(json.dumps(result, ensure_ascii=False, indent=2, allow_nan=False))
        return 2 if result.get('all_image_mean_pass') is False else 0
    except Exception as error:
        print(json.dumps({'completed': False, 'error': str(error)}, ensure_ascii=False), file=sys.stderr)
        return 1


if __name__ == '__main__':
    raise SystemExit(main())
