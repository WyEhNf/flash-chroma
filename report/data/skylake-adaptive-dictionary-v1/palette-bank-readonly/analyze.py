"""导出已验65精确表，再只读统计固定8像素包的同16色bank频率；不运行性能计时。"""
from __future__ import annotations
import argparse
import ctypes as ct
import hashlib
import json
import os
from pathlib import Path
import platform
import re
import sys

ROOT = Path(__file__).resolve().parents[2]
OUT = Path(__file__).resolve().parent
PLAN = ('experiments/skylake-id-batch4-v1.json', 'b1b1f26f3e5bbed74bd203cba0e36662efac1c70079065fdcedecafca47641e3')
BUILD = ('artifacts/skylake-id-batch4-linux-build-v1/build.json', '64e46668c1485f9a3389fa6cb3d12605f4d11f260dcb70f660a0a864a42c1f4b')
FULL = ('artifacts/skylake-id-batch4-linux-full-v1/results.json', 'e00ca989d771fbb417b8697187e4d101fcae040829b01d5bf9687f484f88e613')
PHOTOS = ('artifacts/skylake-server-matrix-v1/server-inputs/photos.rgb', 'e13278cfc91c3411b3c242232239f9ea6fbda3bf5d18c3f17c41a4dedf57defd')
DIRECT_SHA = 'a020c67a0e8ce77e668e6c6d85206af53005923316b4778194637182b4cfaea0'
OUTPUT_SHA = 'f3c0d9078bbcf069f33060a45021a28985b70c9616493ba9bea1ac2027858528'


def digest(path):
    with Path(path).open('rb') as stream:
        return hashlib.file_digest(stream, 'sha256').hexdigest()


def checked(spec):
    if isinstance(spec, tuple):
        spec = {'path': spec[0], 'sha256': spec[1]}
    path = Path(spec['path'])
    if not path.is_absolute():
        path = ROOT/path
    if digest(path) != spec['sha256']:
        raise ValueError('输入SHA不同：'+str(path))
    return path


def read(path):
    return json.loads(Path(path).read_text(encoding='utf-8'))


def save_new(path, value):
    with Path(path).open('x', encoding='utf-8') as stream:
        stream.write(json.dumps(value, ensure_ascii=False, indent=2, allow_nan=False)+'\n')


def export():
    if platform.system() != 'Linux':
        raise ValueError('65导出阶段需要原Linux库')
    for name in ('direct.u8', 'palette.u32', 'export.json'):
        if (OUT/name).exists():
            raise ValueError('不得覆盖既有导出：'+name)
    plan, build, full = (read(checked(x)) for x in (PLAN, BUILD, FULL))
    if (build['plan_sha256'] != PLAN[1] or not full['pass']
            or full['build_sha256'] != BUILD[1] or full['libraries'] != build['libraries']):
        raise ValueError('65构建与完整验收身份不同')
    model_specs = [plan['fixed_inputs']['base'], *plan['suffix_models']]
    models = [checked(s) for s in model_specs]
    sidecar = checked(plan['fixed_inputs']['sidecar'])
    library = checked(build['libraries']['candidate'])
    os.environ['OMP_DYNAMIC'] = 'FALSE'
    d = ct.CDLL(str(library))
    for name in ('abi_version', 'revision', 'capabilities'):
        f = getattr(d, 'jshc_cc_'+name)
        f.argtypes = []
        f.restype = ct.c_uint32
    if d.jshc_cc_abi_version() != 1 or d.jshc_cc_revision() != 65 or d.jshc_cc_capabilities() != 7:
        raise ValueError('实际库不是已验65')
    d.jshc_cc_create.argtypes = [ct.POINTER(ct.c_char_p), ct.POINTER(ct.c_char_p), ct.c_size_t,
        ct.POINTER(ct.c_void_p), ct.POINTER(ct.c_char), ct.c_size_t]
    d.jshc_cc_create.restype = ct.c_int
    d.jshc_cc_destroy.argtypes = [ct.c_void_p]
    d.jshc_cc_destroy.restype = None
    paths = (ct.c_char_p*4)(*(str(p).encode() for p in models))
    sides = (ct.c_char_p*4)(str(sidecar).encode(), None, None, None)
    handle = ct.c_void_p()
    error = ct.create_string_buffer(1024)
    if d.jshc_cc_create(paths, sides, 4, ct.byref(handle), error, len(error)):
        raise RuntimeError(error.value.decode())
    try:
        class DirectInfo(ct.Structure):
            _fields_ = [(n, ct.c_uint32) for n in ('version', 'enabled', 'format', 'reserved')]
            _fields_ += [(n, ct.c_uint64) for n in ('entries', 'table_capacity_bytes')]
            _fields_ += [(n, ct.c_int32) for n in ('dg_min', 'db_min')]
        class PaletteInfo(ct.Structure):
            _fields_ = [(n, ct.c_uint32) for n in ('version', 'enabled', 'palette_size', 'reason')]
            _fields_ += [(n, ct.c_uint64) for n in ('blocks', 'fast_blocks', 'table_capacity_bytes', 'temporary_peak_bytes')]
            _fields_ += [('prepare_seconds', ct.c_double)]
        direct = DirectInfo()
        f = d.jshc_cc_get_direct_info
        f.argtypes = [ct.c_void_p, ct.POINTER(DirectInfo), ct.c_size_t]
        f.restype = ct.c_int
        if f(handle, ct.byref(direct), ct.sizeof(direct)):
            raise ValueError('直表诊断失败')
        if (direct.version, direct.enabled, direct.format, direct.entries, direct.table_capacity_bytes) != (1, 1, 9, 2**22, 2**24):
            raise ValueError('不是65的16MiB小端ID表')
        info = PaletteInfo()
        f = d.jshc_cc_get_palette_info
        f.argtypes = [ct.c_void_p, ct.POINTER(PaletteInfo), ct.c_size_t]
        f.restype = ct.c_int
        if f(handle, ct.byref(info), ct.sizeof(info)) or info.enabled != 1 or info.palette_size != 230:
            raise ValueError('不是原230项调色板')
        words, old_words, palette = (ct.c_uint32*(2**22))(), (ct.c_uint32*(2**21))(), (ct.c_uint32*256)()
        f = d.jshc_cc_copy_direct
        f.argtypes = [ct.c_void_p, ct.POINTER(ct.c_uint32), ct.c_size_t]
        f.restype = ct.c_int
        if f(handle, words, len(words)):
            raise ValueError('直表导出失败')
        f = d.jshc_cc_copy_palette
        f.argtypes = [ct.c_void_p, ct.POINTER(ct.c_uint32), ct.c_size_t, ct.POINTER(ct.c_uint32), ct.c_size_t]
        f.restype = ct.c_int
        if f(handle, old_words, len(old_words), palette, 256):
            raise ValueError('调色板导出失败')
        raw_direct = ct.string_at(words, 2**24)
        raw_palette = ct.string_at(palette, 1024)
        if hashlib.sha256(raw_direct).hexdigest() != DIRECT_SHA:
            raise ValueError('导出直表与已验SHA不同')
        for name, raw in (('direct.u8', raw_direct), ('palette.u32', raw_palette)):
            with (OUT/name).open('xb') as stream:
                stream.write(raw)
        result = {'purpose': '只导出既有已验65句柄的只读表，不映射照片或计时',
            'environment': {'platform': platform.platform(), 'python': sys.version},
            'script_sha256': digest(__file__), 'plan': {'path': PLAN[0], 'sha256': PLAN[1]},
            'build': {'path': BUILD[0], 'sha256': BUILD[1]}, 'full': {'path': FULL[0], 'sha256': FULL[1]},
            'library': build['libraries']['candidate'], 'models': model_specs,
            'sidecar': plan['fixed_inputs']['sidecar'],
            'direct_info': {n: getattr(direct, n) for n, _ in direct._fields_},
            'palette_size': int(info.palette_size), 'palette_slots': 256,
            'direct': {'path': 'direct.u8', 'bytes': len(raw_direct), 'sha256': DIRECT_SHA},
            'palette': {'path': 'palette.u32', 'bytes': len(raw_palette), 'sha256': hashlib.sha256(raw_palette).hexdigest()},
            'native_calls': {'create': 1, 'copy_direct': 1, 'copy_palette': 1, 'destroy': 1,
                'explicit_apply': 0, 'bench': 0},
            'scope': '构造器沿原四模型准备表；没有新拟合、照片原生映射、性能计数或计时调用。'}
    finally:
        d.jshc_cc_destroy(handle)
    save_new(OUT/'export.json', result)
    print('已导出65原直表及调色板，未计时', flush=True)


def history_scan():
    paths = sorted(set((ROOT/'docs/stages').glob('*skylake*.md'))
        | set((ROOT/'scripts').glob('*skylake*.py'))
        | set((ROOT/'experiments').glob('skylake*-runtime/*.cpp'))
        | set((ROOT/'experiments').glob('skylake*-runtime/*.hpp')))
    pattern = re.compile(r'same_bank|palette_bank|bank.{0,30}palette|palette.{0,30}bank|同16|同一.?16.?色', re.I)
    matches = []
    for path in paths:
        for line, text in enumerate(path.read_text(encoding='utf-8').splitlines(), 1):
            if pattern.search(text):
                matches.append({'path': path.relative_to(ROOT).as_posix(), 'line': line, 'text': text})
    related = ['docs/stages/2026-10-20-skylake-uniform-suffix-static.md',
               'docs/stages/2026-10-21-skylake-block-dictionary.md',
               'artifacts/skylake-palette-decode-readonly-v1/analysis.json']
    return {'searched_file_count': len(paths), 'pattern': pattern.pattern,
        'scope': ['docs/stages/*skylake*.md', 'scripts/*skylake*.py', 'experiments/skylake*-runtime/*.cpp及*.hpp'],
        'matches': matches, 'related_sha256': {name: digest(ROOT/name) for name in related},
        'interpretation': '未发现已实施的同16色bank精确PSHUFB路径；旧11是首级RGB全同后仅算一次后缀，旧230色解码分析研究共用残差表，均不是本次条件式bank解码。'}


def analyze():
    import numpy as np
    if (OUT/'analysis.json').exists():
        raise ValueError('不得覆盖既有统计结果')
    export_info = read(OUT/'export.json')
    if export_info['script_sha256'] != digest(__file__):
        raise ValueError('导出后分析脚本发生改变')
    for key in ('direct', 'palette'):
        if digest(OUT/export_info[key]['path']) != export_info[key]['sha256']:
            raise ValueError('导出表SHA不同')
    plan = read(checked(PLAN))
    manifest_path = checked(plan['fixed_inputs']['manifest'])
    manifest = read(manifest_path)
    photo_path = checked(PHOTOS)
    if photo_path.stat().st_size != 235929600 or len(manifest['images']) != 100:
        raise ValueError('照片数量或长度不同')
    table = np.fromfile(OUT/'direct.u8', dtype=np.uint8)
    palette = np.fromfile(OUT/'palette.u32', dtype='<u4')
    if table.size != 2**24 or palette.size != 256 or int(table.max()) >= 230:
        raise ValueError('表长或ID越界')
    photos = np.memmap(photo_path, mode='r', dtype=np.uint8, shape=(100, 1024*768, 3))
    rows = []
    total_bank = np.zeros(16, dtype=np.int64)
    output_hash = hashlib.sha256()
    for image_index, image in enumerate(photos):
        meta = manifest['images'][image_index]
        pixel_sha = hashlib.sha256(image).hexdigest()
        if pixel_sha != meta['evaluation']['pixel_sha256']:
            raise ValueError('照片顺序或逐图像素不同：'+meta['id'])
        codes = image[:, 0].astype(np.uint32)|(image[:, 1].astype(np.uint32)<<8)|(image[:, 2].astype(np.uint32)<<16)
        ids = table[codes]
        packets = ids.reshape(-1, 8)
        banks = packets >> 4
        same_bank = np.all(banks == banks[:, :1], axis=1)
        same_id = np.all(packets == packets[:, :1], axis=1)
        if np.any(same_id & ~same_bank):
            raise AssertionError('完全同ID必须属于同bank')
        count, hit, identical = len(packets), int(same_bank.sum()), int(same_id.sum())
        bank_counts = np.bincount(banks[same_bank, 0], minlength=16)
        total_bank += bank_counts
        # 仅离线索引并核对冻结最终输出SHA，避免地址顺序错误产生虚假频率。
        rgb32 = palette[ids]
        rgb = np.column_stack((rgb32 & 255, (rgb32 >> 8) & 255, (rgb32 >> 16) & 255)).astype(np.uint8)
        output_hash.update(rgb)
        rows.append({'image_index': image_index, 'image_id': meta['id'], 'pixel_sha256': pixel_sha,
            'packets': count, 'same_bank_packets': hit, 'same_bank_packet_fraction': hit/count,
            'same_bank_covered_pixels': hit*8, 'same_bank_pixel_fraction': hit/count,
            'same_id_packets': identical, 'same_id_packet_fraction': identical/count,
            'same_bank_but_not_same_id_packets': hit-identical,
            'same_bank_packet_counts_by_bank': bank_counts.tolist()})
    if output_hash.hexdigest() != OUTPUT_SHA:
        raise AssertionError('导出表离线解码照片的最终SHA不同')
    packet_count = sum(r['packets'] for r in rows)
    hit = sum(r['same_bank_packets'] for r in rows)
    identical = sum(r['same_id_packets'] for r in rows)
    def distribution(key):
        a = np.array([r[key] for r in rows])
        return {'minimum': float(a.min()), 'p10': float(np.quantile(a, .10)),
            'median': float(np.median(a)), 'p90': float(np.quantile(a, .90)), 'maximum': float(a.max())}
    result = {'purpose': __doc__, 'analysis_completed': True,
        'environment': {'platform': platform.platform(), 'python': sys.version, 'numpy': np.__version__},
        'script_sha256': digest(__file__), 'export_sha256': digest(OUT/'export.json'),
        'inputs': {'photos': {'path': PHOTOS[0], 'sha256': PHOTOS[1], 'bytes': 235929600},
            'manifest': plan['fixed_inputs']['manifest'], 'direct': export_info['direct'], 'palette': export_info['palette'],
            'library': export_info['library'], 'models': export_info['models'], 'sidecar': export_info['sidecar'],
            'plan': export_info['plan'], 'build': export_info['build'], 'full': export_info['full']},
        'method': ['每图从像素0起按连续8像素分包；固定自然宽度8，没有偏移或宽度扫描。',
            'code=R|(G<<8)|(B<<16)，从实际导出的16MiB表取精确ID。',
            '同bank条件为8个ID>>4全相等；完全同ID作为包含于同bank的对照。',
            '每包长度一致且无尾包，因此包比例等于被完整同bank包覆盖的像素比例。',
            '按清单逐图核对像素SHA，并以导出palette离线解码核对冻结100图总输出SHA。'],
        'summary': {'packet_pixels': 8, 'images': 100, 'pixels': 100*1024*768,
            'packets': packet_count, 'same_bank_packets': hit, 'same_bank_packet_fraction': hit/packet_count,
            'same_bank_covered_pixels': hit*8, 'same_bank_pixel_fraction': hit/packet_count,
            'same_id_packets': identical, 'same_id_packet_fraction': identical/packet_count,
            'same_id_covered_pixels': identical*8, 'same_bank_but_not_same_id_packets': hit-identical,
            'same_bank_but_not_same_id_fraction': (hit-identical)/packet_count,
            'same_bank_packet_counts_by_bank': total_bank.tolist(),
            'per_image_same_bank_fraction_distribution': distribution('same_bank_packet_fraction'),
            'per_image_same_id_fraction_distribution': distribution('same_id_packet_fraction')},
        'per_image': rows, 'offline_decoded_photo_output_sha256': output_hash.hexdigest(),
        'history': history_scan(), 'performance_calls': 0, 'native_photo_mapping_calls': 0,
        'scope': '仅已见固定100图的集合与频率；不等同硬件命中率、分支可预测性或吞吐。不覆盖任意缓冲区对齐所改变的包起点。'}
    save_new(OUT/'analysis.json', result)
    print(json.dumps(result['summary'], ensure_ascii=False, indent=2), flush=True)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('phase', choices=('export', 'analyze'))
    args = parser.parse_args()
    export() if args.phase == 'export' else analyze()
