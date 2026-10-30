"""照片工作台的真实参数、源LUT轴序、RGB字节和拒绝契约。"""
from __future__ import annotations
import hashlib
import io
import json
from pathlib import Path
import sys
from types import SimpleNamespace

import numpy as np
from PIL import Image
import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from gui import studio


def write_cube(path, transform):
    # CUBE声明R轴最快；预期仿射函数直接按输入RGB推导，不复用被测采样器。
    lines = ['TITLE "test"', 'LUT_3D_SIZE 2']
    for b in (0, 1):
        for g in (0, 1):
            for r in (0, 1):
                lines.append(' '.join(str(v) for v in transform(r, g, b)))
    path.write_text('\n'.join(lines)+'\n', encoding='utf-8')


def fixture_catalog(tmp_path):
    pixels = np.random.default_rng(12029).integers(0, 256, (19, 23, 3), dtype=np.uint8)
    photo = tmp_path / 'photo.png'; Image.fromarray(pixels).save(photo)
    cube = tmp_path / 'red.cube'; write_cube(cube, lambda r,g,b: (1, 0, 0))
    stages = [{'lut': 'red', 'strength': .3, 'enabled': True}] + [{'lut': 'identity', 'strength': 0., 'enabled': False}] * 3
    manifest = {'default_photo': 'sample', 'default_preset': 'red-look',
        'photos': [{'id': 'sample', 'path': str(photo), 'title': '测试照片', 'sha256': studio.digest(photo)}],
        'luts': [{'id': 'red', 'path': str(cube), 'title': '测试红色', 'sha256': studio.digest(cube)}],
        'presets': [{'id': 'red-look', 'stages': stages}, {'id': 'native-look', 'native_profile': 'default',
            'stages': [{'lut': 'identity', 'strength': 0., 'enabled': False}] * 4}]}
    path = tmp_path / 'catalog.json'; path.write_text(json.dumps(manifest), encoding='utf-8')
    return path, pixels, manifest


def unit_service():
    service = studio.StudioService.__new__(studio.StudioService)
    service.lut_rows = {'known': {}}
    service.library = SimpleNamespace(capabilities=7)
    return service


def test_cube_axis_order_and_affine_sampling(tmp_path):
    path = tmp_path / 'affine.cube'
    write_cube(path, lambda r,g,b: (.2 + .4*r, .1 + .6*g, .3 + .3*b))
    points = np.array([[17., 143., 201.], [255., 0., 13.], [0., 255., 255.]])
    actual = studio._cube_values(studio._cube(path), points)
    expected = np.column_stack((51 + .4*points[:,0], 25.5 + .6*points[:,1], 76.5 + .3*points[:,2]))
    np.testing.assert_allclose(actual, expected, rtol=0, atol=1e-10)


def test_full_photo_preserves_original_rgb_bytes(tmp_path):
    catalog, pixels, _ = fixture_catalog(tmp_path)
    service = studio.StudioService(tmp_path, catalog=catalog, library=tmp_path/'absent.dll')
    payload = service.photo('sample', 'full')
    assert payload.startswith(b'\x89PNG')
    with Image.open(io.BytesIO(payload)) as image:
        np.testing.assert_array_equal(np.asarray(image), pixels)
    with Image.open(io.BytesIO(service.photo('sample', 'thumb'))) as image:
        assert image.format == 'JPEG'


def test_changed_source_bytes_are_not_silently_accepted(tmp_path):
    catalog, _, manifest = fixture_catalog(tmp_path)
    service = studio.StudioService(tmp_path, catalog=catalog, library=tmp_path/'absent.dll')
    Path(manifest['photos'][0]['path']).write_bytes(b'changed')
    with pytest.raises(ValueError, match='SHA'):
        service.photo('sample', 'full')


@pytest.mark.parametrize('value', [True, None, '0.5', float('nan'), float('inf'), -.1, 1.1])
def test_rejects_invalid_finite_values(value):
    with pytest.raises(ValueError):
        studio._finite_number(value, '测试数值')


@pytest.mark.parametrize('changes', [dict(profile=[]), dict(weights=[0,0,0]), dict(weights=[.2,.4]),
    dict(weights=[True,.3,.4]), dict(threads=True), dict(threads=4.0), dict(threads=3)])
def test_configuration_rejects_invalid_parameters(changes):
    values = dict(profile='balanced', weights=[.7,.5,.3], threads=1); values.update(changes)
    with pytest.raises(ValueError):
        unit_service()._configuration(**values)


def test_preferences_and_profiles_change_actual_configuration():
    service = unit_service()
    compact = service._configuration('compact', [.2,.5,.9], 1)
    detail = service._configuration('detail', [.95,.3,.1], 4)
    assert compact[0] == 17 and detail[0] == 33
    assert compact[1]['block_pixels'] == 4096 and detail[1]['block_pixels'] == 65536
    assert compact[1]['threads'] == 1 and detail[1]['threads'] == 4


@pytest.mark.parametrize('bad', [[], None, [{'lut': ['known'], 'strength': 1, 'enabled': True}]*4,
    [{'lut': 'unknown', 'strength': 1, 'enabled': True}]*4,
    [{'lut': 'known', 'strength': 1, 'enabled': 1}]*4,
    [{'lut': 'known', 'strength': float('nan'), 'enabled': True}]*4])
def test_stages_reject_nonfour_and_invalid_values(bad):
    with pytest.raises(ValueError):
        unit_service()._stages(bad)


def current_library():
    for directory in ('artifacts/single-header-perf-build', 'build-single-header'):
        for filename in ('libflash_chroma_bridge.dll', 'libflash_chroma_bridge.so', 'libflash_chroma_bridge.dylib'):
            path = ROOT / directory / filename
            if path.is_file():
                return path
    pytest.skip('当前环境尚未构建单头bridge；纯参数与源格式合同仍执行')


def test_real_runtime_identity_and_stage_change(tmp_path):
    catalog, pixels, manifest = fixture_catalog(tmp_path)
    service = studio.StudioService(tmp_path, catalog=catalog, library=current_library())
    try:
        assert service.library is not None, service.library_error
        base = {'photo': 'sample', 'preset': 'red-look', 'profile': 'compact', 'threads': 1, 'weights': [.2,.5,.9]}
        changed, actual = service.render(base)
        assert changed['metrics']['runtime_equal'] is True
        assert not np.array_equal(actual, pixels)
        assert changed['config']['m'] == [17]*4
        disabled = [{**stage, 'enabled': False, 'strength': 0.} for stage in manifest['presets'][0]['stages']]
        identity, identity_pixels = service.render(dict(base, stages=disabled))
        np.testing.assert_array_equal(identity_pixels, pixels)
        assert identity['metrics']['mean_delta_e'] == 0
        assert identity['metrics']['runtime_equal'] is True
        # 明确传stages即创意覆盖，不能把native预设的identity占位误当作执行固定Cinema链。
        overridden, override_pixels = service.render(dict(base, preset='native-look', stages=disabled))
        assert overridden['mode'] == 'creative'
        np.testing.assert_array_equal(override_pixels, pixels)
        payload, _ = service.result(changed['id'], 'download')
        with Image.open(io.BytesIO(payload)) as image:
            assert image.size == (pixels.shape[1], pixels.shape[0])
            assert hashlib.sha256(image.tobytes()).hexdigest() == changed['metrics']['output_sha256']
    finally:
        service.close()


def test_runtime_failure_returns_explicit_http_error(monkeypatch):
    # 模拟原生准备失败，前端应收到可读503，不应悬空断开或拿旧图当成功。
    from gui import server
    body = json.dumps({'photo': 'sample', 'preset': 'red-look'}).encode()
    handler = object.__new__(server.Handler)
    handler.path = '/api/studio/render'
    handler.server = SimpleNamespace(server_port=8876)
    handler.headers = {'Host': '127.0.0.1:8876', 'X-App-Token': server.TOKEN, 'Content-Length': str(len(body))}
    handler.rfile = io.BytesIO(body)
    calls = []
    handler.send = lambda status, payload, *args: calls.append((status, payload))
    def fail(data):
        raise RuntimeError('原生准备失败')
    monkeypatch.setattr(server, 'STUDIO', SimpleNamespace(render=fail))
    handler.do_POST()
    assert calls == [(503, {'message': '原生准备失败'})]
