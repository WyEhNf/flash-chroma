"""本机Studio真实HTTP验收；串行渲染，不运行RAW解码或性能评分。"""
from __future__ import annotations

import argparse
import copy
import hashlib
import io
import json
import math
from pathlib import Path
import platform
import re
import sys
import time
import urllib.error
import urllib.parse
import urllib.request

from PIL import Image

ROOT = Path(__file__).resolve().parents[1]


def digest(path):
    with Path(path).open('rb') as stream:
        return hashlib.file_digest(stream, 'sha256').hexdigest()


def png_record(body, *, require_png=True):
    with Image.open(io.BytesIO(body)) as image:
        image.load()
        if require_png and image.format != 'PNG':
            raise AssertionError('下载结果不是PNG')
        rgb = image.convert('RGB')
        return {'width': rgb.width, 'height': rgb.height,
                'pixel_sha256': hashlib.sha256(rgb.tobytes()).hexdigest(),
                'file_sha256': hashlib.sha256(body).hexdigest()}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--url', default='http://127.0.0.1:8765')
    parser.add_argument('--output', required=True, type=Path)
    parser.add_argument('--library', type=Path, help='本次预期实际使用的单头原生库')
    parser.add_argument('--photo', help='用于真实渲染的代表图片ID')
    parser.add_argument('--preset', help='用于四级调整验证的非恒等组合ID')
    args = parser.parse_args()
    if args.output.exists():
        raise FileExistsError('验收输出已存在，拒绝覆盖')
    parsed = urllib.parse.urlparse(args.url)
    if parsed.scheme != 'http' or parsed.hostname not in ('127.0.0.1', 'localhost'):
        raise ValueError('仅允许检查本机HTTP服务')
    url = args.url.rstrip('/')
    checks, renders = [], []
    result = {'purpose': 'Studio真实HTTP功能、数值输出变化、原尺寸下载及请求边界；非官方精度或性能评分',
              'url': url, 'environment': {'python': sys.version, 'platform': platform.platform()},
              'script_sha256': digest(__file__), 'checks': checks, 'renders': renders,
              'raw_decode_executed': False, 'performance_score_claimed': False, 'all_passed': False}
    token = ''

    def request(path, data=None, expected=(200,), headers=None, binary=False, raw=None):
        h = {'X-App-Token': token, 'Content-Type': 'application/json'}
        h.update(headers or {})
        payload = raw if raw is not None else (json.dumps(data, allow_nan=False).encode('utf-8') if data is not None else None)
        try:
            response = urllib.request.urlopen(urllib.request.Request(url + path, payload, headers=h), timeout=180)
        except urllib.error.HTTPError as error:
            response = error
        body = response.read()
        statuses = (expected,) if isinstance(expected, int) else expected
        if response.status not in statuses:
            raise AssertionError(f'{path}返回{response.status}，预期{statuses}：{body[:300]!r}')
        checks.append({'path': path, 'status': response.status,
                       'body_sha256': hashlib.sha256(body).hexdigest(), 'bytes': len(body),
                       'content_type': response.headers.get('Content-Type')})
        return body if binary else json.loads(body)

    def query(path, **parameters):
        return path + '?' + urllib.parse.urlencode(parameters)

    def render(payload, label):
        begin = time.monotonic()
        record = request('/api/studio/render', payload)
        if not isinstance(record, dict) or not record.get('download_url'):
            raise AssertionError('渲染接口没有真实下载结果')
        required = {'id', 'photo', 'preset', 'mode', 'stages', 'config', 'metrics', 'engine', 'width', 'height'}
        if not required.issubset(record) or record['photo'] != payload['photo'] or record['preset'] != payload['preset']:
            raise AssertionError('渲染结果缺少完整身份或与本次请求不一致')
        config, metrics, engine = (record[key] for key in ('config', 'metrics', 'engine'))
        if not all(isinstance(value, dict) for value in (config, metrics, engine)):
            raise AssertionError('实际配置、指标或引擎不是完整对象')
        required_metrics = {'apply_ms', 'prepare_ms', 'model_ms', 'reference_ms', 'total_ms',
                            'mean_delta_e', 'max_delta_e', 'p99_delta_e', 'runtime_equal', 'model_bytes',
                            'arena_bytes', 'image_buffer_bytes', 'output_sha256', 'reference_kind'}
        if not required_metrics.issubset(metrics):
            raise AssertionError('渲染结果缺少完整实测/参考字段')
        for field in ('mean_delta_e', 'max_delta_e', 'p99_delta_e'):
            value = metrics[field]
            if value is not None and (type(value) not in (int, float) or not math.isfinite(value) or value < 0):
                raise AssertionError('参考色差字段无效：' + field)
        if not isinstance(metrics['reference_kind'], str) or not metrics['reference_kind']:
            raise AssertionError('参考口径未说明')
        if (config.get('profile') != payload['profile'] or config.get('threads') != payload['threads']
                or config.get('weights') != payload['weights']):
            raise AssertionError('实际性能参数没有对应本次请求')
        if config.get('backend') not in ('avx2', 'scalar') or config.get('representation') not in ('sparse', 'direct_u8', 'direct_u16', 'direct_rgb24'):
            raise AssertionError('结果未记录真实支持的执行后端/表示')
        if (len(record['stages']) != 4 or len(config.get('m', [])) != 4
                or any(type(value) is not int or not 17 <= value <= 33 for value in config['m'])):
            raise AssertionError('实际四级模型网格不合法')
        for field in ('apply_ms', 'prepare_ms', 'model_ms', 'reference_ms', 'total_ms'):
            value = metrics.get(field)
            if type(value) not in (int, float) or not math.isfinite(value) or value < 0:
                raise AssertionError('实际计时字段无效：' + field)
        for field in ('model_bytes', 'arena_bytes', 'image_buffer_bytes'):
            if type(metrics.get(field)) is not int or metrics[field] < 0:
                raise AssertionError('资源容量字段无效：' + field)
        if metrics['runtime_equal'] is not None and type(metrics['runtime_equal']) is not bool:
            raise AssertionError('同模型执行一致性状态不明确')
        if metrics.get('runtime_equal') is False:
            raise AssertionError('原生运行库与独立C99本图输出不一致')
        if not engine.get('available') or engine.get('library_sha256') != result['health']['engine']['library_sha256']:
            raise AssertionError('实际渲染运行库与已核对的服务身份不同')
        for key in ('download_url', 'image_url', 'difference_url'):
            path = record.get(key)
            if not isinstance(path, str) or not path.startswith('/api/studio/result?'):
                raise AssertionError('输出链接不是本服务固定结果接口')
        downloaded = png_record(request(record['download_url'], binary=True))
        if (downloaded['width'], downloaded['height']) != (record['width'], record['height']):
            raise AssertionError('结果声明尺寸与实际PNG不同')
        if downloaded['pixel_sha256'] != metrics.get('output_sha256'):
            raise AssertionError('下载PNG像素与原生输出SHA不同')
        for key in ('image_url', 'difference_url'):
            png_record(request(record[key], binary=True), require_png=False)
        item = {'label': label, 'request': payload, 'response': record, 'download': downloaded,
                'http_elapsed_seconds': time.monotonic() - begin,
                'elapsed_scope': '串行HTTP功能验证，含请求、PNG返回及哈希，不是运行库基准'}
        renders.append(item)
        print(json.dumps({'render': label, 'pixel_sha256': downloaded['pixel_sha256']}, ensure_ascii=False), flush=True)
        return item

    try:
        html = request('/', binary=True).decode('utf-8')
        match = (re.search(r'<meta\s+name=["\']app-token["\']\s+content=["\']([^"\']+)', html, re.I)
                 or re.search(r'(?:window\.)?APP_TOKEN\s*=\s*["\']([^"\']+)', html))
        if not match:
            raise AssertionError('Studio页面没有注入会话Token')
        token = match.group(1)
        request('/studio', binary=True)
        raw_page = request('/raw', binary=True).decode('utf-8')
        if 'id="stage-list"' not in html or 'id="process-first"' not in raw_page:
            raise AssertionError('新版Studio与旧RAW页面没有分别保留正确界面')
        if '__APP_TOKEN__' in html or '__APP_TOKEN__' in raw_page:
            raise AssertionError('页面Token占位符未替换')
        health = request('/api/health')
        result['health'] = health
        if (health.get('application') != 'flash-chroma-studio' or health.get('studio_api_version') != 1
                or not health.get('engine', {}).get('available')):
            raise AssertionError('当前端口不是可用的新版Studio原生服务')
        for filename, field in (('server.py', 'server_source_sha256'), ('studio.py', 'studio_source_sha256'),
                                ('studio_catalog.json', 'studio_catalog_sha256')):
            if health.get(field) != digest(ROOT / 'gui' / filename):
                raise AssertionError('服务实际启动来源与当前文件不同：' + filename)
        if args.library and health['engine'].get('library_sha256') != digest(args.library):
            raise AssertionError('服务没有加载指定的当前单头运行库')
        catalog = request('/api/studio/catalog')
        photos, presets, luts = (catalog.get(key) for key in ('photos', 'presets', 'luts'))
        if not isinstance(photos, list) or len(photos) < 16 or not isinstance(presets, list) or len(presets) < 12:
            raise AssertionError('代表素材少于16图或组合少于12套')
        if not isinstance(luts, list) or len(luts) < 12:
            raise AssertionError('没有可调的真实LUT库')
        if len({row['id'] for row in photos}) != len(photos) or len({row['id'] for row in presets}) != len(presets):
            raise AssertionError('素材或组合ID重复')
        for preset in presets:
            if len(preset.get('stages', [])) != 4:
                raise AssertionError('组合不是四级固定阶段')
        result['catalog'] = {'photos': len(photos), 'presets': len(presets), 'luts': len(luts),
                             'photo_ids': [row['id'] for row in photos], 'preset_ids': [row['id'] for row in presets]}
        for photo in photos:
            png_record(request(query('/api/studio/photo', id=photo['id'], size='thumb'), binary=True), require_png=False)
        photo = next((row for row in photos if row['id'] == args.photo), None) if args.photo else photos[0]
        preset = (next((row for row in presets if row['id'] == args.preset), None) if args.preset
                  else next((row for row in presets if row['id'] == 'layered-film'), presets[0]))
        if photo is None or preset is None:
            raise AssertionError('指定验收素材或组合不存在')
        second = next(row for row in presets if row['id'] != preset['id'])
        original_bytes = request(query('/api/studio/photo', id=photo['id'], size='full'), binary=True)
        with Image.open(io.BytesIO(original_bytes)) as original:
            original.load()
            rgb = original.convert('RGB')
            original_identity = {'width': rgb.width, 'height': rgb.height,
                                 'pixel_sha256': hashlib.sha256(rgb.tobytes()).hexdigest()}
        result['source'] = {'id': photo['id'], **original_identity}
        base = {'photo': photo['id'], 'preset': preset['id'], 'profile': 'balanced',
                'weights': [0.75, 0.6, 0.25], 'threads': 1}
        # 拒绝检查不创建有效处理任务，集中在正式渲染之前完成。
        request('/api/studio/render', base, expected=403, headers={'X-App-Token': 'invalid'})
        request('/api/studio/render', base, expected=403, headers={'Origin': 'https://invalid.example'})
        request('/api/health', expected=403, headers={'Host': 'invalid.example'})
        request('/static/../../AGENTS.md', expected=(400, 404), binary=True)
        request('/%2e%2e/AGENTS.md', expected=(400, 404), binary=True)
        request(query('/api/studio/photo', id='../../AGENTS.md', size='full'), expected=(400, 404))
        request(query('/api/studio/result', id='../../AGENTS.md', kind='download'), expected=(400, 404))
        request('/api/studio/render', dict(base, photo='unknown-photo'), expected=(400, 404))
        request('/api/studio/render', dict(base, preset='unknown-preset'), expected=(400, 404))
        request('/api/studio/render', dict(base, stages=[]), expected=400)
        request('/api/studio/render', dict(base, weights=[-1, 0.5, 0.5]), expected=400)
        request('/api/studio/render', dict(base, weights=[0, 0, 0]), expected=400)
        request('/api/studio/render', dict(base, threads=2), expected=400)
        request('/api/studio/render', dict(base, profile='unknown-profile'), expected=400)
        bad_stages = copy.deepcopy(preset['stages'])
        bad_stages[0]['strength'] = 2.0
        request('/api/studio/render', dict(base, stages=bad_stages), expected=400)
        request('/api/studio/render', raw=b'[]', expected=400)
        request('/api/studio/render', raw=b'{', expected=400)
        request('/api/studio/render', raw=b' ' * 16385, expected=400)
        first = render(base, '组合A')
        other = render(dict(base, preset=second['id']), '组合B')
        if first['download']['pixel_sha256'] == other['download']['pixel_sha256']:
            raise AssertionError('不同组合的实际像素输出完全相同')
        stages = copy.deepcopy(preset['stages'])
        disabled = [{**row, 'enabled': False, 'strength': 0.0} for row in stages]
        identity = render(dict(base, stages=disabled), '四级关闭')
        if identity['download']['pixel_sha256'] != original_identity['pixel_sha256']:
            raise AssertionError('四级关闭没有得到输入RGB原像素')
        for index in range(4):
            adjusted = copy.deepcopy(stages)
            adjusted[index]['enabled'] = False
            adjusted[index]['strength'] = 0.0
            changed = render(dict(base, stages=adjusted), f'关闭第{index+1}级')
            if changed['download']['pixel_sha256'] == first['download']['pixel_sha256']:
                raise AssertionError(f'关闭第{index+1}级未改变真实输出，请选择四级均非恒等的验收组合')
        detail = render(dict(base, profile='detail', weights=[0.95, 0.35, 0.15]), '精度优先参数')
        compact = render(dict(base, profile='compact', weights=[0.3, 0.6, 0.95]), '省内存参数')
        if detail['response']['config']['m'] == compact['response']['config']['m']:
            raise AssertionError('两端性能偏好没有改变实际模型网格')
        native_preset = next((row for row in presets if row.get('native_profile') == 'max_first'), None)
        if native_preset is None:
            raise AssertionError('没有当前已验证max_first单头模型预设')
        native = render(dict(base, preset=native_preset['id']), '当前Cinema固定模型')
        if native['response']['mode'] != 'native' or native['response']['config'].get('native_profile') != 'max_first':
            raise AssertionError('Cinema预设没有实际执行固定模型')
        if any(item['download']['width'] != original_identity['width'] or
               item['download']['height'] != original_identity['height'] for item in renders):
            raise AssertionError('原尺寸PNG下载尺寸改变')
        result['all_passed'] = True
    except Exception as error:
        result['error'] = str(error)
        raise
    finally:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        with args.output.open('x', encoding='utf-8') as stream:
            json.dump(result, stream, ensure_ascii=False, indent=2, allow_nan=False)
            stream.write('\n')
    print(json.dumps({'checks': len(checks), 'renders': len(renders), 'all_passed': True}), flush=True)


if __name__ == '__main__':
    main()
