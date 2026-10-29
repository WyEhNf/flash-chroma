"""本机图片调色工作台：固定四级模型由真实单头CPU库执行。"""
from __future__ import annotations

from collections import OrderedDict
import ctypes as ct
import hashlib
import io
import json
import math
import os
from pathlib import Path
import secrets
import struct
import sys
import threading
import time
from urllib.parse import urlencode
import zipfile

import numpy as np
from PIL import Image, ImageOps

ROOT = Path(__file__).resolve().parents[1]
for _module_path in (ROOT / 'scripts', ROOT / 'python'):
    if str(_module_path) not in sys.path:
        sys.path.insert(0, str(_module_path))
import flash_chroma_support as native
from lutlab import io as lutio

API_VERSION = 1
PROFILES = {'compact': 17, 'balanced': 25, 'detail': 33}
PHOTO_SIZES = {'thumb': 320, 'preview': 1400, 'full': None}
MAX_PIXELS = 16_000_000


class StudioUnavailable(RuntimeError):
    """真实运行环境不可用，调用方应显示503而不是伪造图像。"""


class StudioBusy(RuntimeError):
    """有一个实际渲染正在执行。"""


def digest(path):
    with Path(path).open('rb') as stream:
        return hashlib.file_digest(stream, 'sha256').hexdigest()


def _png(array):
    output = io.BytesIO()
    Image.fromarray(array).save(output, 'PNG', compress_level=2)
    return output.getvalue()


def _jpeg(array):
    output = io.BytesIO()
    Image.fromarray(array).save(output, 'JPEG', quality=86)
    return output.getvalue()


def _finite_number(value, name, low=0, high=1):
    if isinstance(value, bool) or not isinstance(value, (int, float)) or not math.isfinite(value) or not low <= value <= high:
        raise ValueError(f'{name}必须是{low}到{high}之间的有限数值')
    return float(value)


def _serialize(model):
    """复用lutlab的SLUT/Q16轴表，内存序列化不依赖临时模型文件。"""
    lutio.validate_sparse(model, competition=True)
    idx, frac = model.tables()
    return b''.join((b'SLUT', struct.pack('<III', 1, model.m, 0), model.grid.astype('<f4').tobytes(),
                     idx.tobytes(), frac.astype('<u4').tobytes(), np.ascontiguousarray(model.nodes).tobytes()))


class MemoryModel:
    """与宿主FFI相同的只读模型字节契约；对象持有借用缓冲寿命。"""
    def __init__(self, blobs, sidecars=None):
        self.buffers, self.records = [], []
        self.sidecar_payloads = list(sidecars or [None] * 4)
        self.payloads = list(blobs)
        def wrap(payload):
            if payload is None:
                return native.Bytes(None, 0)
            storage = (ct.c_uint8 * len(payload)).from_buffer_copy(payload)
            self.buffers.append(storage)
            self.records.append({'sha256': hashlib.sha256(payload).hexdigest(), 'bytes': len(payload)})
            return native.Bytes(ct.cast(storage, native.U8), len(payload))
        self.models = (native.Bytes * 4)(*(wrap(b) for b in blobs))
        self.sidecars = (native.Bytes * 4)(*(wrap(b) for b in self.sidecar_payloads))
        self.total_bytes = sum(len(b) for b in self.payloads) + sum(len(b) for b in self.sidecar_payloads if b is not None)
        self.fingerprint = hashlib.sha256(b''.join(blobs) + b''.join(b or b'' for b in self.sidecar_payloads)).hexdigest()


def _cube(path):
    """沿用collect_existing_luts/load_source的CUBE格式和R最快轴序；仅需NumPy。

    不推断摄影色彩空间。输入解释为RGB8归一化码值，参考采用源CUBE三线性。
    """
    if path.stat().st_size > 32 * 1024 * 1024:
        raise ValueError('交互CUBE文件超过32MiB限制')
    size, low, high, rows = None, [0., 0., 0.], [1., 1., 1.], []
    for original in path.read_text(encoding='utf-8-sig').splitlines():
        line = original.split('#', 1)[0].strip()
        if not line:
            continue
        parts = line.split()
        if parts[0] == 'TITLE':
            continue
        if parts[0] == 'LUT_3D_SIZE':
            if size is not None or len(parts) != 2:
                raise ValueError('CUBE尺寸声明非法')
            size = int(parts[1])
            if not 2 <= size <= 65:
                raise ValueError('交互CUBE尺寸须为2..65')
        elif parts[0] in ('DOMAIN_MIN', 'DOMAIN_MAX'):
            values = list(map(float, parts[1:]))
            if len(values) != 3:
                raise ValueError('CUBE输入域须有三个分量')
            if parts[0] == 'DOMAIN_MIN':
                low = values
            else:
                high = values
        else:
            if len(parts) != 3 or len(rows) >= 65 ** 3:
                raise ValueError('CUBE数据行非法或过多')
            rows.append(list(map(float, parts)))
    table, low, high = np.asarray(rows, np.float64), np.asarray(low), np.asarray(high)
    if size is None or table.shape != (size ** 3, 3) or not np.all(np.isfinite(table)):
        raise ValueError('CUBE节点数或数值非法')
    if not np.all(np.isfinite([low, high])) or not np.all(high > low):
        raise ValueError('CUBE输入域非法')
    return {'nodes': table.reshape(size, size, size, 3).transpose(2, 1, 0, 3) * 255.,
            'low': low * 255., 'high': high * 255., 'size': size}


def _cube_values(cube, points):
    """与source_lut的源坐标口径相同，分块执行未舍入的八节点三线性。"""
    shape = points.shape
    flat = points.reshape(-1, 3).astype(np.float64, copy=False)
    result = np.empty(flat.shape, np.float64)
    for begin in range(0, len(flat), 65536):
        values = flat[begin:begin + 65536]
        position = np.clip((values - cube['low']) / (cube['high'] - cube['low']), 0, 1) * (cube['size'] - 1)
        cell = np.minimum(np.floor(position).astype(np.intp), cube['size'] - 2)
        fraction = position - cell
        out = np.zeros(values.shape, np.float64)
        for r in (0, 1):
            for g in (0, 1):
                for b in (0, 1):
                    weight = ((fraction[:, 0] if r else 1 - fraction[:, 0]) *
                              (fraction[:, 1] if g else 1 - fraction[:, 1]) *
                              (fraction[:, 2] if b else 1 - fraction[:, 2]))
                    out += cube['nodes'][cell[:, 0] + r, cell[:, 1] + g, cell[:, 2] + b] * weight[:, None]
        result[begin:begin + len(values)] = out
    return result.reshape(shape)


def _blend(cube, pixels, strength):
    if strength == 0 or cube is None:
        return pixels.copy()
    changed = np.clip(_cube_values(cube, pixels), 0, 255)
    mixed = pixels.astype(np.float64) * (1 - strength) + changed * strength
    return np.floor(np.clip(mixed, 0, 255) + .5).astype(np.uint8)


class StudioService:
    def __init__(self, root=ROOT, catalog=None, library=None):
        self.root = Path(root).resolve()
        self.catalog_path = Path(catalog or self.root / 'gui/studio_catalog.json').resolve()
        self.lock, self.render_lock = threading.RLock(), threading.Lock()
        self.results, self.engines, self.photos, self.cubes, self.looks = (OrderedDict() for _ in range(5))
        self.library, self.library_error = None, None
        self.source_sha256 = digest(__file__)
        self.catalog_sha256 = digest(self.catalog_path) if self.catalog_path.is_file() else None
        self.catalog_data = json.loads(self.catalog_path.read_text(encoding='utf-8')) if self.catalog_path.is_file() else {}
        self.photo_rows = self._index(self.catalog_data.get('photos', []), '照片')
        self.lut_rows = self._index(self.catalog_data.get('luts', []), 'LUT')
        self.preset_rows = self._index(self.catalog_data.get('presets', []), '预设')
        self.native_manifest = None
        self.reference_tables = None
        self._discover_library(library)

    @staticmethod
    def _index(rows, label):
        result = {}
        for row in rows:
            ident = row.get('id')
            if not isinstance(ident, str) or not ident or ident in result:
                raise ValueError(label + '目录身份重复或缺失')
            result[ident] = dict(row)
        return result

    def _roots(self):
        roots = [self.root]
        # 工作树素材可复用主checkout的既有本地资产，不下载或外发。
        workspace = self.root.parent.parent if self.root.parent.name == 'worktrees' else self.root.parent.parent
        if (workspace / 'projects/16-lut-color').is_dir():
            roots.append(workspace / 'projects/16-lut-color')
        if (workspace / 'worktrees/p16-unified-avx512-20261026').is_dir():
            roots.append(workspace / 'worktrees/p16-unified-avx512-20261026')
        return roots

    def _path(self, record):
        name = record.get('path')
        if not isinstance(name, str) or not name:
            raise ValueError('目录记录缺少本地路径')
        supplied = Path(name)
        roots = self._roots()
        options = [supplied] if supplied.is_absolute() else [r / supplied for r in roots]
        for path in options:
            path = path.resolve()
            allowed = roots + [self.root.parent.parent]
            if any(path.is_relative_to(r) for r in allowed) and path.is_file():
                return path
        raise FileNotFoundError('本地素材缺失：' + record.get('title', record.get('id', '素材')))

    def _verified_path(self, record):
        path = self._path(record)
        expected = record.get('sha256')
        if not isinstance(expected, str) or digest(path) != expected:
            raise ValueError('本地素材SHA与目录不符：' + record.get('id', path.name))
        return path

    def _discover_library(self, explicit):
        supplied = explicit or os.environ.get('FLASH_CHROMA_LIBRARY')
        if supplied:
            candidates = [Path(supplied).expanduser().resolve()]
        else:
            candidates = [r / folder / name for r in self._roots()
                          for folder in ('artifacts/single-header-perf-build', 'build-single-header', 'artifacts/single-header-build')
                          for name in ('libflash_chroma_bridge.dll', 'libflash_chroma_bridge.so', 'libflash_chroma_bridge.dylib')]
        errors = []
        for path in candidates:
            if not path.is_file():
                continue
            try:
                self.library = native.Library(path)
                return
            except (OSError, ValueError, AttributeError) as error:
                errors.append(f'{path.name}: {error}')
                if supplied:
                    break
        self.library_error = '; '.join(errors) or '尚未找到单头CPU库，请构建single_header或指定--studio-library'

    def engine_info(self):
        library = self.library
        return {'available': library is not None, 'name': 'flash-chroma 单头CPU',
                'backend': 'avx2' if library and library.capabilities & 2 else 'scalar',
                'capabilities': library.capabilities if library else 0,
                'library_sha256': library.sha256 if library else None,
                'sha256': library.sha256 if library else None,
                'library_path': str(library.path) if library else None,
                'api_version': API_VERSION, 'cpu_only': True, 'error': self.library_error}

    def catalog(self):
        photos = []
        for row in self.photo_rows.values():
            item = {k: v for k, v in row.items() if k != 'path'}
            try:
                item['available'] = self._path(row).is_file()
            except (OSError, ValueError):
                item['available'] = False
            for size in PHOTO_SIZES:
                item[size + '_url'] = '/api/studio/photo?' + urlencode({'id': row['id'], 'size': size})
            photos.append(item)
        luts = [{k: v for k, v in row.items() if k != 'path'} for row in self.lut_rows.values()]
        presets = []
        for row in self.preset_rows.values():
            item = dict(row)
            if item.get('native_profile'):
                item['stages'] = [dict(stage, display_title=f'Cinema 固定映射 {i + 1}', lut_title=f'Cinema 第{i + 1}级')
                                  for i, stage in enumerate(item.get('stages', []))]
            presets.append(item)
        return {'api_version': API_VERSION, 'photos': photos, 'luts': luts, 'presets': presets,
                'default_photo': self.catalog_data.get('default_photo', next(iter(self.photo_rows), None)),
                'default_preset': self.catalog_data.get('default_preset', next(iter(self.preset_rows), None)),
                'profiles': [{'id': key, 'm': value} for key, value in PROFILES.items()],
                'engine': self.engine_info(), 'catalog_sha256': self.catalog_sha256,
                'scope': '本地实际图片与LUT；新创意组合按本图参考重新评价，不继承历史比赛成绩'}

    def _photo(self, ident, max_side=None):
        if not isinstance(ident, str) or ident not in self.photo_rows:
            raise ValueError('未知照片')
        key = (ident, max_side)
        if key in self.photos:
            self.photos.move_to_end(key)
            return self.photos[key]
        path = self._verified_path(self.photo_rows[ident])
        with Image.open(path) as image:
            if image.width * image.height > MAX_PIXELS:
                raise ValueError('照片超过1600万像素交互限制')
            image = ImageOps.exif_transpose(image).convert('RGB')
            if max_side:
                image.thumbnail((max_side, max_side), Image.Resampling.LANCZOS)
            pixels = np.ascontiguousarray(np.asarray(image))
        pixels.flags.writeable = False
        self.photos[key] = pixels
        while len(self.photos) > 8:
            self.photos.popitem(last=False)
        return pixels

    def photo(self, ident, size='preview'):
        if size not in PHOTO_SIZES:
            raise ValueError('照片尺寸参数非法')
        with self.lock:
            pixels = self._photo(ident, PHOTO_SIZES[size])
            # 原尺寸入口保留输入RGB字节，避免JPEG再编码混淆恒等映射和导出核对。
            return _png(pixels) if size == 'full' else _jpeg(pixels)

    def _cube(self, ident):
        if ident == 'identity':
            return None
        if ident not in self.lut_rows:
            raise ValueError('未知LUT')
        if ident not in self.cubes:
            self.cubes[ident] = _cube(self._verified_path(self.lut_rows[ident]))
            while len(self.cubes) > 6:
                self.cubes.popitem(last=False)
        self.cubes.move_to_end(ident)
        return self.cubes[ident]

    def _stages(self, rows):
        if not isinstance(rows, list) or len(rows) != 4:
            raise ValueError('必须固定四级映射')
        stages = []
        for row in rows:
            if (not isinstance(row, dict) or not isinstance(row.get('lut'), str)
                    or row['lut'] not in {*self.lut_rows, 'identity'}):
                raise ValueError('四级中包含未知LUT')
            enabled = row.get('enabled', True)
            if not isinstance(enabled, bool):
                raise ValueError('stage enabled必须为布尔值')
            stages.append({'lut': row['lut'], 'enabled': enabled,
                           'strength': _finite_number(row.get('strength', 1), 'LUT强度')})
        return stages

    def _configuration(self, profile, weights, threads, native_profile=None):
        if not isinstance(profile, str) or profile not in PROFILES:
            raise ValueError('未知性能档位')
        if not isinstance(weights, list) or len(weights) != 3:
            raise ValueError('连续偏好需要精度、速度、省内存三个权重')
        weights = [_finite_number(w, '连续权重') for w in weights]
        if not sum(weights):
            raise ValueError('连续权重不能全为零')
        if type(threads) is not int or threads not in (1, 4):
            raise ValueError('线程数仅支持1或4')
        if threads == 4 and not self.library.capabilities & 4:
            raise ValueError('当前库未启用OpenMP，请选择1线程')
        total = sum(weights)
        desired = PROFILES[profile] + 8 * (weights[0] - .5 * (weights[1] + weights[2])) / total
        precise = weights[0] > .5 * (weights[1] + weights[2])
        m = min((17, 25, 33), key=lambda value: (abs(value - desired), -value if precise else value))
        backend = 'avx2' if self.library.capabilities & 2 else 'scalar'
        representation = 'sparse'
        if native_profile and profile != 'compact' and weights[1] >= weights[2] and backend == 'avx2':
            representation = 'direct_u8' if native_profile == 'default' else 'direct_u16'
        config = native.configuration(representation, backend=backend, threads=threads,
            block_pixels=4096 if weights[2] > weights[1] else 65536,
            max_workspace_bytes=48 * 1024 * 1024)
        return m, config, weights

    def _native_model(self, profile):
        if self.native_manifest is None:
            for root in self._roots():
                for relative in ('data/p16-frontier/models/manifest.json', 'artifacts/frontier-models-v1/manifest.json',
                                 'data/p16-score-models/manifest.json'):
                    path = root / relative
                    if path.is_file():
                        value = json.loads(path.read_text(encoding='utf-8'))
                        base = Path(value.get('path_root', path.parent))
                        if not base.is_absolute():
                            base = path.parent / base
                        self.native_manifest = value, base.resolve()
                        break
                if self.native_manifest:
                    break
        if not self.native_manifest:
            raise StudioUnavailable('本地Cinema模型清单缺失')
        value, base = self.native_manifest
        if profile not in value.get('profiles', {}):
            raise ValueError('本地Cinema模型档位缺失')
        row = value['profiles'][profile]
        blobs, sidecars = [], []
        for entries, target in ((row['models'], blobs), (row['sidecars'], sidecars)):
            for record in entries:
                if record is None:
                    target.append(None)
                    continue
                path = Path(record['path'])
                if not path.is_absolute():
                    path = base / path
                payload = path.read_bytes()
                if hashlib.sha256(payload).hexdigest() != record['sha256']:
                    raise ValueError('Cinema模型SHA不符')
                target.append(payload)
        return MemoryModel(blobs, sidecars)

    def _creative_model(self, stages, m):
        axis = np.floor(np.linspace(0., 255., m) + .5)
        grid = np.stack([axis] * 3)
        points = np.stack(np.meshgrid(axis, axis, axis, indexing='ij'), axis=-1)
        blobs = []
        for stage in stages:
            cube = self._cube(stage['lut']) if stage['enabled'] else None
            strength = stage['strength'] if stage['enabled'] else 0
            # 网格轴已取整数；恒等级也必须显式转成部署模型的RGB8节点。
            nodes = np.ascontiguousarray(_blend(cube, points, strength), dtype=np.uint8)
            blobs.append(_serialize(lutio.SparseLut(grid, nodes)))
        return MemoryModel(blobs)

    def _engine(self, model, config):
        key = (model.fingerprint, json.dumps(config, sort_keys=True))
        if key in self.engines:
            self.engines.move_to_end(key)
            return self.engines[key][1], True
        engine = self.library.create(model, config)
        self.engines[key] = (model, engine)
        while len(self.engines) > 4:
            _, (_, previous) = self.engines.popitem(last=False)
            previous.close()
        return engine, False

    def _native_reference(self, source):
        if self.reference_tables is None:
            records = self.native_manifest[0].get('original_luts', []) if self.native_manifest else []
            if not records:
                archive = self.root / 'report/data/p16-score-candidate-20261027/raw-evidence.zip'
                if archive.is_file():
                    with zipfile.ZipFile(archive) as package:
                        records = json.loads(package.read('run-default/results.json'))['quality']['sources']
            tables = []
            try:
                if len(records) == 4:
                    for record in records:
                        path = Path(record['path'])
                        if not path.is_file() or path.stat().st_size != 256 ** 3 * 3 or digest(path) != record['sha256']:
                            tables = []
                            break
                        tables.append(np.memmap(path, np.uint8, 'r', shape=(256, 256, 256, 3)))
            except (OSError, ValueError):
                tables = []
            self.reference_tables = tables
        if len(self.reference_tables) != 4:
            return None
        result = source.copy()
        for table in self.reference_tables:
            result = table[result[..., 0], result[..., 1], result[..., 2]]
        return result

    def render(self, data, preview_size=None, keep=True):
        if self.library is None:
            raise StudioUnavailable(self.library_error)
        # 只串行执行原生/参考处理；允许缩略图与主预览作短队列，避免正常切换就429。
        if not self.render_lock.acquire(timeout=8):
            raise StudioBusy('正在处理另一张图片，请稍后重试')
        try:
            with self.lock:
                return self._render(data, preview_size, keep)
        finally:
            self.render_lock.release()

    def _render(self, data, preview_size, keep):
        begin = time.perf_counter_ns()
        if not isinstance(data, dict):
            raise ValueError('渲染请求须为对象')
        photo_id = data.get('photo', self.catalog_data.get('default_photo'))
        preset_id = data.get('preset', self.catalog_data.get('default_preset'))
        if not isinstance(preset_id, str) or preset_id not in self.preset_rows:
            raise ValueError('未知预设')
        preset = self.preset_rows[preset_id]
        stages = self._stages(data.get('stages', preset.get('stages')))
        native_profile = preset.get('native_profile') if 'stages' not in data else None
        profile = data.get('profile', preset.get('profile', 'balanced'))
        m, config, weights = self._configuration(profile, data.get('weights', [.6, .6, .6]), data.get('threads', 4), native_profile)
        source = self._photo(photo_id, preview_size)
        model_begin = time.perf_counter_ns()
        model = self._native_model(native_profile) if native_profile else self._creative_model(stages, m)
        model_ms = (time.perf_counter_ns() - model_begin) / 1e6
        engine, reused = self._engine(model, config)
        target = np.empty_like(source)
        apply_ms = engine.apply(source, target)
        ref_begin = time.perf_counter_ns()
        scalar = np.empty_like(source)
        if self.library.c_apply(model, source, scalar):
            raise RuntimeError('独立C99本图校验失败')
        runtime_equal = bool(np.array_equal(target, scalar))
        if not runtime_equal:
            raise RuntimeError('单头C++与独立C99本图输出不一致，未发布处理结果')
        if native_profile:
            reference = self._native_reference(source)
            reference_kind = '四张原始密集Cinema LUT逐级RGB8查表；本图全部像素'
            if reference is None:
                reference_kind = '缺少原密集LUT，仅独立C99执行一致性；不报告拟合色差'
        else:
            reference = source.copy()
            for stage in stages:
                cube = self._cube(stage['lut']) if stage['enabled'] else None
                reference = _blend(cube, reference, stage['strength'] if stage['enabled'] else 0)
            reference_kind = '当前四个CUBE强度混合后逐级RGB8量化；本图全部像素三线性参考'
        reference_ms = (time.perf_counter_ns() - ref_begin) / 1e6
        comparison = reference if reference is not None else source
        delta = target.astype(np.int32) - comparison.astype(np.int32)
        distance = np.sqrt(np.sum(delta * delta, axis=-1, dtype=np.int64))
        difference = np.minimum(np.abs(delta) * (16 if reference is not None else 4), 255).astype(np.uint8)
        ident = secrets.token_hex(12)
        output_png, difference_png = _png(target), _png(difference)
        actual_stages = []
        for i, (stage, payload) in enumerate(zip(stages, model.payloads)):
            title = f'Cinema 固定映射 {i + 1}' if native_profile else self.lut_rows.get(stage['lut'], {}).get('title', '恒等映射')
            actual = dict(lut=f'native:{native_profile}:stage{i + 1}', enabled=True, strength=1.) if native_profile else stage
            actual_stages.append(dict(actual, display_title=title, lut_title=title,
                                      m=struct.unpack_from('<I', payload, 8)[0], model_sha256=hashlib.sha256(payload).hexdigest()))
        metrics = {'apply_ms': apply_ms, 'prepare_ms': 0. if reused else engine.prepare_ms,
                   'model_ms': model_ms, 'reference_ms': reference_ms,
                   'total_ms': (time.perf_counter_ns() - begin) / 1e6,
                   'mean_delta_e': float(distance.mean()) if reference is not None else None,
                   'max_delta_e': float(distance.max()) if reference is not None else None,
                   'p99_delta_e': float(np.quantile(distance, .99)) if reference is not None else None,
                   'runtime_equal': runtime_equal, 'model_bytes': engine.info['model_bytes'],
                   'arena_bytes': engine.info['arena_bytes'], 'image_buffer_bytes': source.nbytes + target.nbytes,
                   'output_sha256': hashlib.sha256(memoryview(target)).hexdigest(), 'reference_kind': reference_kind,
                   'difference_scope': '与本图参考的RGB绝对差×16' if reference is not None else '输出与输入RGB绝对差×4',
                   'memory_scope': '模型/arena/两份RGB图像分别列示；不等于Python进程峰值',
                   'timing_scope': '一次本图实际调用，非稳定基准；total含解码、建模、准备、参考和PNG编码',
                   'official_threshold_pass': None, 'official_score': None, 'engine_reused': reused}
        result_config = dict(config, profile=profile, weights=weights, m=[s['m'] for s in actual_stages],
            native_profile=native_profile, requested_threads=data.get('threads', 4),
            selection_policy='固定native模型，仅调整执行表示/块大小' if native_profile else '档位与连续偏好映射到m17/25/33；参数策略，不是已测Pareto排名',
            quality_scope='仅本图本组合，不继承未知LUT或历史照片成绩')
        link = lambda kind: '/api/studio/result?' + urlencode({'id': ident, 'kind': kind})
        result = {'id': ident, 'image_url': link('output'), 'difference_url': link('difference'),
                  'download_url': link('download'), 'photo': photo_id, 'preset': preset_id,
                  'mode': 'native' if native_profile else 'creative', 'stages': actual_stages,
                  'config': result_config, 'metrics': metrics, 'engine': self.engine_info(),
                  'width': target.shape[1], 'height': target.shape[0]}
        if keep:
            self.results[ident] = (result, output_png, difference_png)
            while len(self.results) > 10:
                self.results.popitem(last=False)
        return result, target

    def result(self, ident, kind='output'):
        with self.lock:
            if not isinstance(ident, str) or ident not in self.results:
                raise FileNotFoundError('结果已过期，请重新处理图片')
            if kind not in ('output', 'difference', 'download'):
                raise ValueError('结果类型非法')
            row, image, difference = self.results[ident]
            return (difference if kind == 'difference' else image), f'flash-chroma-{ident}.png'

    def look(self, photo, preset):
        if not isinstance(photo, str) or not isinstance(preset, str):
            raise ValueError('照片和预设身份须为字符串')
        key = photo, preset
        with self.lock:
            if key in self.looks:
                return self.looks[key]
        result, pixels = self.render({'photo': photo, 'preset': preset, 'threads': 1}, preview_size=320, keep=False)
        payload = _jpeg(pixels)
        with self.lock:
            self.looks[key] = payload
            while len(self.looks) > 24:
                self.looks.popitem(last=False)
        return payload

    def close(self):
        with self.lock:
            for _, engine in self.engines.values():
                engine.close()
            self.engines.clear()
