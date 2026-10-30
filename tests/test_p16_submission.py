"""交付包真实SLUT去重/篡改、固定CPU策略与严格全像素均值合同。"""
from __future__ import annotations

import json
from pathlib import Path
import struct
import subprocess
import sys

import numpy as np
import pytest

SCRIPTS = Path(__file__).resolve().parents[1] / 'scripts'
sys.path.insert(0, str(SCRIPTS))
import p16_submission as submission


def _slut(path, m, value):
    grid = np.tile(np.linspace(0, 255, m), (3, 1)).astype('<f4')
    code = np.arange(256, dtype=np.int64)
    cell = np.minimum(code*(m - 1)//255, m - 2)
    frac = ((code*(m - 1) - cell*255)*65536 + 127)//255
    idx = np.tile(cell, (3, 1)).astype(np.uint8)
    fractions = np.tile(frac, (3, 1)).astype('<u4')
    nodes = np.full((m, m, m, 3), value, np.uint8)
    path.write_bytes(b'SLUT' + struct.pack('<III', 1, m, 0) + grid.tobytes() + idx.tobytes()
        + fractions.tobytes() + nodes.tobytes())
    return {'path': path.name, 'sha256': submission.native.digest(path)}


def _manifest(tmp_path):
    source = tmp_path / 'source'
    source.mkdir()
    rows = [_slut(source / f'stage{index}.slut', m, 10 + index) for index, m in enumerate((17, 18, 25, 33))]
    alternative = _slut(source / 'alternative.slut', 17, 99)
    license_path = source / 'LICENSE.asset'
    license_path.write_bytes(b'Copyright fixture\nPermission preserved verbatim.\n')
    manifest = {'path_root': 'source', 'interpolation_basis': 'tetra_q16', 'default_profile': 'default', 'profiles': {
        'default': {'models': rows, 'sidecars': [None]*4},
        'user-profile': {'models': [alternative, *rows[1:]], 'sidecars': [None]*4}},
        'licenses': [{'path': license_path.name, 'sha256': submission.native.digest(license_path)}]}
    path = tmp_path / 'source-manifest.json'
    path.write_text(json.dumps(manifest), encoding='utf-8')
    return path


def test_real_slut_pack_is_portable_deduplicated_and_tamper_evident(tmp_path):
    manifest = _manifest(tmp_path)
    output = tmp_path / 'package'
    result = submission.pack(manifest, output)
    assert result['package_storage']['logical_model_records'] == 8
    assert result['package_storage']['unique_model_objects'] == 5
    assert result['package_storage']['unique_model_object_bytes'] < result['package_storage']['logical_model_bytes']
    metadata, profiles, _ = submission.load_package(output)
    assert profiles['default']['m'] == [17, 18, 25, 33]
    assert 'user-profile' in profiles
    assert metadata['policy']['gpu_allowed'] is False
    assert metadata['policy']['automatic_avx512'] is False
    assert metadata['policy']['interpolation_basis'] == 'tetra_q16'
    assert all(row['interpolation_basis'] == 'tetra_q16' for row in metadata['profiles'].values())
    assert Path(profiles['default']['models'][1]['path']) == Path(profiles['user-profile']['models'][1]['path'])
    assert (output / metadata['licenses'][0]['path']).read_bytes() == (tmp_path / 'source/LICENSE.asset').read_bytes()
    before = (output / 'manifest.json').read_bytes()
    with pytest.raises(FileExistsError):
        submission.pack(manifest, output)
    assert (output / 'manifest.json').read_bytes() == before
    # 删除原始模型目录不影响内容寻址包；运行不依赖旧source_root。
    import shutil
    source = (tmp_path / 'source').resolve()
    assert source.parent == tmp_path.resolve() and source.name == 'source'
    shutil.rmtree(source)
    submission.load_package(output)
    object_path = Path(profiles['default']['models'][0]['path'])
    object_path.write_bytes(object_path.read_bytes()[:-1] + b'\x01')
    with pytest.raises(ValueError, match='摘要'):
        submission.load_package(output)


def test_cpu_policy_and_escaping_object_are_rejected(tmp_path):
    output = tmp_path / 'package'
    submission.pack(_manifest(tmp_path), output)
    path = output / 'manifest.json'
    manifest = json.loads(path.read_text(encoding='utf-8'))
    manifest['policy']['gpu_allowed'] = True
    path.write_text(json.dumps(manifest), encoding='utf-8')
    with pytest.raises(ValueError, match='CPU'):
        submission.load_package(output)
    manifest['policy']['gpu_allowed'] = False
    manifest['licenses'][0]['path'] = '../outside-license'
    path.write_text(json.dumps(manifest), encoding='utf-8')
    with pytest.raises(ValueError, match='目录内'):
        submission.load_package(output)


def test_mean_gate_uses_every_pixel_strict_limit_and_no_official_score():
    first = submission._error_row(np.array([[[1, 0, 0]]], np.uint8), np.zeros((1, 1, 3), np.uint8))
    second = submission._error_row(np.zeros((1, 3, 3), np.uint8), np.zeros((1, 3, 3), np.uint8))
    result = submission.accuracy_summary([first, second], 1.0)
    assert result['pixel_weighted_mean_delta_e'] == .25
    assert result['aggregate_mean_pass'] is True
    assert result['all_image_mean_pass'] is False  # 第一图mean恰为1，严格<不通过。
    assert result['official_threshold_pass'] is None
    assert result['official_score_available'] is False
    assert submission.accuracy_summary([first], None)['all_image_mean_pass'] is None


def test_source_depth_gate_rejects_pillow_rgb16_conversion(rgb16_png):
    with pytest.raises(ValueError, match='静默降位深'):
        submission._rgb8(rgb16_png)


def test_pack_and_help_without_psutil_or_user_license(tmp_path):
    manifest = _manifest(tmp_path)
    value = json.loads(manifest.read_text(encoding='utf-8'))
    value['licenses'] = []
    manifest.write_text(json.dumps(value), encoding='utf-8')
    output = tmp_path / 'package-without-psutil'
    code = '''
import contextlib, io, sys
class BlockPsutil:
    def find_spec(self, fullname, path=None, target=None):
        if fullname == "psutil" or fullname.startswith("psutil."):
            raise ImportError("测试显式阻止可选psutil导入")
sys.meta_path.insert(0, BlockPsutil())
sys.path.insert(0, sys.argv[1])
import p16_submission as s
assert s.native.psutil is None
assert s.native.rss()["available"] is False
assert s.native.environment()["psutil"] is None
assert s.native.environment()["physical_cores"] is None
s.native.setup()
with contextlib.redirect_stdout(io.StringIO()):
    for args in (["--help"], ["pack", "--help"], ["run", "--help"]):
        try:
            s.main(args)
        except SystemExit as error:
            assert error.code == 0
assert s.main(["pack", "--manifest", sys.argv[2], "--output", sys.argv[3]]) == 0
package, _, _ = s.load_package(sys.argv[3])
assert package["licenses"] == []
assert package["source_declaration"]["license_status"] == "not_provided"
'''
    subprocess.run([sys.executable, '-X', 'utf8', '-c', code, str(SCRIPTS), str(manifest), str(output)], check=True)


def test_sidecar_endpoints_use_serialized_m_instead_of_observed_max_index(tmp_path):
    idx = np.zeros((3, 256), np.uint8)
    idx[:, 255] = 1
    frac = np.zeros((3, 3, 256), dtype='<u4')
    frac[:, :, 255] = 65536
    path = tmp_path / 'sidecar.bin'
    frac.tofile(path)
    # 观测最大idx=1会把端点误判成2*Q；真实m17要求16*Q。
    with pytest.raises(ValueError, match='端点'):
        submission._sidecar(path, idx, 17)


def test_known_cinema_manifest_cannot_omit_or_replace_original_license(tmp_path, monkeypatch):
    original = _manifest(tmp_path)
    manifest = tmp_path / 'data/p16-score-models/manifest.json'
    manifest.parent.mkdir(parents=True)
    value = json.loads(original.read_text(encoding='utf-8'))
    value['path_root'] = str(tmp_path / 'source')
    monkeypatch.setattr(submission, 'ROOT', tmp_path)
    for index, licenses in enumerate(([], value['licenses'])):
        # fixture许可证不是已知Cinema原MIT文本；空列表和替换均须拒绝。
        value['licenses'] = licenses
        manifest.write_text(json.dumps(value), encoding='utf-8')
        with pytest.raises(ValueError, match='原MIT许可'):
            submission.pack(manifest, tmp_path / f'rejected-package-{index}')


@pytest.mark.parametrize(('scope', 'field', 'value'), [
    ('manifest', 'interpolation_basis', 'trilinear_float'),
    ('profile', 'interpolation_basis', 'tri_q16'),
    ('manifest', 'stage_interpolators', ['tetra', 'tri', 'tetra', 'tetra']),
    ('profile', 'stage_kinds', [0, 1, 0, 0]),
])
def test_pack_rejects_explicit_tri_or_matched_stage_contract(tmp_path, scope, field, value):
    manifest = _manifest(tmp_path)
    content = json.loads(manifest.read_text(encoding='utf-8'))
    selected = content if scope == 'manifest' else content['profiles']['default']
    selected[field] = value
    manifest.write_text(json.dumps(content), encoding='utf-8')
    output = tmp_path / 'wrong-basis-package'
    with pytest.raises(ValueError, match='tetra_q16'):
        submission.pack(manifest, output)
    assert not output.exists()


def test_user_manifest_requires_basis_and_loaded_package_cannot_change_it(tmp_path):
    manifest = _manifest(tmp_path)
    content = json.loads(manifest.read_text(encoding='utf-8'))
    del content['interpolation_basis']
    manifest.write_text(json.dumps(content), encoding='utf-8')
    output = tmp_path / 'package'
    with pytest.raises(ValueError, match='basis'):
        submission.pack(manifest, output)
    content['interpolation_basis'] = 'tetra_q16'
    manifest.write_text(json.dumps(content), encoding='utf-8')
    submission.pack(manifest, output)
    packaged = json.loads((output / 'manifest.json').read_text(encoding='utf-8'))
    packaged['policy']['interpolation_basis'] = 'trilinear_float'
    (output / 'manifest.json').write_text(json.dumps(packaged), encoding='utf-8')
    with pytest.raises(ValueError, match='tetra_q16'):
        submission.load_package(output)
    packaged['policy']['interpolation_basis'] = 'tetra_q16'
    packaged['profiles']['default']['interpolation_basis'] = 'tri_q16'
    (output / 'manifest.json').write_text(json.dumps(packaged), encoding='utf-8')
    with pytest.raises(ValueError, match='tetra_q16'):
        submission.load_package(output)
