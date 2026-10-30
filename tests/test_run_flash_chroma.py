"""真实部署入口的选择身份、模型来源、证据及输出路径合同；不模拟百图数值验收。"""
from __future__ import annotations

import copy
import hashlib
import json
from pathlib import Path
import sys

import numpy as np
from PIL import Image
import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'scripts'))
import p16_frontier as frontier
import run_flash_chroma as runner


def fixture(tmp_path):
    candidate = {'id': 'candidate', 'context': 'host', 'model_id': 'model', 'evidence': 'raw.json#candidate',
                 'config': {'target': 'desktop', 'backend': 'scalar', 'representation': 'sparse',
                            'threads': 1, 'block_pixels': 4096, 'max_workspace_bytes': 0},
                 'metrics': {'mean_error': .2, 'worst_image_mean': .4, 'batch_ms': 10,
                             'runtime_bytes': 100, 'workspace_bytes': 0},
                 'verified': dict.fromkeys(frontier.VERIFICATIONS, True)}
    context = {'source_luts_sha256': [str(i)*64 for i in range(1, 5)], 'dataset_sha256': '5'*64,
               'platform_id': 'platform', 'timing_scope': 'hot', 'image_mode': 'separate', 'build_id': '6'*64}
    catalog = {'schema': frontier.SCHEMA, 'contexts': {'host': context},
               'models': {'model': {}}, 'candidates': [candidate]}
    catalog_path, selection_path = tmp_path / 'catalog.json', tmp_path / 'selection.json'
    frontier.save_new(catalog_path, catalog)
    selected = frontier.tradeoff(catalog)
    selected['catalog_sha256'] = frontier.digest(catalog_path)
    frontier.save_new(selection_path, selected)
    return catalog, candidate, context, catalog_path, selection_path


def rewrite(path, value):
    path.write_text(json.dumps(value, ensure_ascii=False, allow_nan=False), encoding='utf-8')


def test_saved_selection_binds_catalog_and_exact_config(tmp_path):
    catalog, candidate, context, catalog_path, selection_path = fixture(tmp_path)
    actual, selected, recomputed, identities = runner.bind_selection(catalog_path, selection_path)
    assert selected == candidate and recomputed['status'] == 'ok'
    assert identities['catalog']['sha256'] == frontier.digest(catalog_path)
    changed = json.loads(selection_path.read_text(encoding='utf-8'))
    changed['selected']['config']['threads'] = 4
    rewrite(selection_path, changed)
    with pytest.raises(ValueError, match='候选被修改'):
        runner.bind_selection(catalog_path, selection_path)


def test_catalog_change_and_request_change_are_rejected(tmp_path):
    catalog, _, _, catalog_path, selection_path = fixture(tmp_path)
    changed = json.loads(selection_path.read_text(encoding='utf-8'))
    changed['request']['max_error'] = .1
    rewrite(selection_path, changed)
    with pytest.raises(ValueError, match='不能重新选择'):
        runner.bind_selection(catalog_path, selection_path)
    catalog['notes'] = ['后续修改，旧selection必须失效']
    rewrite(catalog_path, catalog)
    with pytest.raises(ValueError, match='摘要不符'):
        runner.bind_selection(catalog_path, selection_path)


def test_model_manifest_must_be_pinned_before_loading(tmp_path):
    catalog, candidate, _, catalog_path, _ = fixture(tmp_path)
    path = tmp_path / 'model.json'
    path.write_text('{}', encoding='utf-8')
    catalog['models']['model'] = {'manifest': 'model.json', 'manifest_sha256': '0'*64, 'profile': 'fixed'}
    with pytest.raises(ValueError, match='模型manifest'):
        runner.bind_model(catalog, candidate, catalog_path)
    assert runner.resolve_record_path('model.json', catalog_path) == path.resolve()


def test_raw_evidence_binds_actual_output_and_config(tmp_path):
    _, candidate, context, catalog_path, _ = fixture(tmp_path)
    value = {'completed': True, 'library': {'sha256': context['build_id']},
             'source_pixels_sha256': context['dataset_sha256'], 'environment': {'cpu': 'fixture'},
             'records': [{'id': 'candidate', 'config': copy.deepcopy(candidate['config']), 'batch_sha256': '7'*64}]}
    path = tmp_path / 'raw.json'
    frontier.save_new(path, value)
    row, identity = runner.bind_evidence(candidate, context, catalog_path)
    assert row['batch_sha256'] == '7'*64 and identity['sha256'] == frontier.digest(path)
    value['records'][0]['config']['block_pixels'] = 65536
    rewrite(path, value)
    with pytest.raises(ValueError, match='执行配置不一致'):
        runner.bind_evidence(candidate, context, catalog_path)
    value['records'][0]['config'] = candidate['config']
    value['completed'] = False
    rewrite(path, value)
    with pytest.raises(ValueError, match='尚未完成'):
        runner.bind_evidence(candidate, context, catalog_path)


def test_new_output_and_fixed_index_pngs(tmp_path):
    output = runner.create_output(tmp_path / 'new' / 'run')
    pixels = np.array([[[[1, 2, 3], [4, 5, 6]]], [[[7, 8, 9], [10, 11, 12]]]], np.uint8)
    rows = runner.write_frames(output, pixels)
    assert [Path(row['path']).name for row in rows] == ['0001.png', '0002.png']
    for index, row in enumerate(rows):
        with Image.open(row['path']) as image:
            np.testing.assert_array_equal(np.asarray(image), pixels[index])
    first = Path(rows[0]['path']).read_bytes()
    with pytest.raises(FileExistsError):
        runner.create_output(output)
    with pytest.raises(FileExistsError):
        runner.write_frames(output, pixels)
    assert Path(rows[0]['path']).read_bytes() == first


def test_platform_identity_does_not_claim_speed_optimum():
    environment = {'cpu': 'fixture', 'affinity': [0, 2]}
    sha = hashlib.sha256(json.dumps(environment, sort_keys=True, ensure_ascii=False).encode()).hexdigest()
    matching = runner._platform_record(environment, {'platform_id': sha}, {'environment': environment})
    assert matching['current_matches_catalog_fingerprint']
    assert not matching['same_environment_speed_optimum_claimed']
    other = runner._platform_record({'cpu': 'another'}, {'platform_id': sha}, {'environment': environment})
    assert not other['current_matches_catalog_fingerprint'] and other['source_environment_matches_catalog_fingerprint']
