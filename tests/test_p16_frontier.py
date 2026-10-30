"""连续目标的约束、非凸前沿、上下文隔离及离线任务域合同。"""
from __future__ import annotations

import copy
from pathlib import Path
import sys

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'scripts'))
import p16_frontier as frontier


def candidate(name, error, time, memory, **changes):
    row = {'id': name, 'context': 'host', 'model_id': 'model', 'evidence': 'contract-fixture',
           'config': {'target': 'desktop', 'backend': 'scalar', 'representation': 'sparse',
                      'threads': 1, 'block_pixels': 4096, 'max_workspace_bytes': 0},
           'metrics': {'mean_error': error, 'worst_image_mean': error + .05, 'batch_ms': time,
                       'runtime_bytes': memory, 'workspace_bytes': 0},
           'verified': dict.fromkeys(frontier.VERIFICATIONS, True)}
    for key, value in changes.items():
        row[key].update(value)
    return row


def catalog():
    return {'schema': frontier.SCHEMA, 'contexts': {'host': {
                'source_luts_sha256': [str(i)*64 for i in range(1, 5)], 'dataset_sha256': '5'*64,
                'platform_id': 'fixture-cpu', 'timing_scope': 'hot_batch', 'image_mode': 'separate', 'build_id': 'fixture'}},
            'models': {'model': {}}, 'candidates': [candidate('accurate', .1, 10, 100),
                candidate('nonconvex', .6, 6, 100), candidate('fastest', 1, 1, 100),
                candidate('dominated', 2, 20, 200)]}


def test_nonconvex_point_and_budget_choose_it():
    value = catalog()
    result = frontier.tradeoff(value)
    assert result['frontier_ids'] == ['accurate', 'nonconvex', 'fastest']
    # 中间点在精度/时间凸包上方，普通正权重和可能永不选中；epsilon预算仍能返回它。
    result = frontier.tradeoff(value, goal='fastest', max_error=.7)
    assert result['selected']['id'] == 'nonconvex'
    assert result['selected']['config'] == value['candidates'][1]['config']


def test_continuous_weights_and_units_preserve_choice():
    value = catalog()
    assert frontier.tradeoff(value, weights=(.999, .001, 0))['selected']['id'] == 'accurate'
    assert frontier.tradeoff(value, weights=(.001, .999, 0))['selected']['id'] == 'fastest'
    result = frontier.tradeoff(value, weights=(.2, .7, .1))
    for row in value['candidates']:
        row['metrics']['batch_ms'] *= 1000
        row['metrics']['runtime_bytes'] *= 1024
    assert frontier.tradeoff(value, weights=(.2, .7, .1))['selected']['id'] == result['selected']['id']


@pytest.mark.parametrize('weights', [(0, 0, 0), (-.1, 1, 0), (1.01, 0, 0), (float('nan'), 1, 0), (0, float('inf'), 1)])
def test_invalid_continuous_domain(weights):
    with pytest.raises(ValueError, match='连续权重'):
        frontier.tradeoff(catalog(), weights=weights)


def test_strict_image_threshold_and_inclusive_resource_limits():
    value = catalog()
    assert frontier.tradeoff(value, max_error=.15)['status'] == 'no_feasible'
    result = frontier.tradeoff(value, goal='accurate', max_error=.150001,
                               max_runtime_bytes=100, max_workspace_bytes=0)
    assert result['selected']['id'] == 'accurate'
    assert frontier.tradeoff(value, max_runtime_bytes=99)['status'] == 'no_feasible'


def test_context_target_backend_and_threads_do_not_leak():
    value = catalog()
    wrong = copy.deepcopy(value['contexts']['host'])
    wrong['platform_id'] = 'other-cpu'
    value['contexts']['other'] = wrong
    row = candidate('other-host', 0, .01, 1)
    row['context'] = 'other'
    value['candidates'].append(row)
    with pytest.raises(ValueError, match='显式指定'):
        frontier.tradeoff(value)
    result = frontier.tradeoff(value, context='host')
    assert result['selected']['id'] != 'other-host'
    assert result['rejected']['context'] == 1
    value['candidates'][0]['config'].update(backend='avx2', threads=4)
    assert frontier.tradeoff(value, context='host', goal='accurate', backends=('scalar',), max_threads=1)['selected']['id'] == 'nonconvex'
    assert frontier.tradeoff(value, context='host', target='embedded')['status'] == 'no_feasible'


def test_unstable_time_is_opt_in_and_unknown_time_cannot_be_optimized():
    value = catalog()
    for row in value['candidates']:
        row['verified']['time_stable'] = False
    assert frontier.tradeoff(value)['status'] == 'no_feasible'
    result = frontier.tradeoff(value, allow_unstable_time=True)
    assert result['status'] == 'ok' and result['provisional']
    for row in value['candidates']:
        row['verified']['time'] = False
        row['metrics']['batch_ms'] = None
    assert frontier.tradeoff(value, allow_unstable_time=True)['status'] == 'no_feasible'
    result = frontier.tradeoff(value, goal='accurate', ignore_time=True)
    assert result['selected']['id'] == 'accurate' and result['provisional']
    with pytest.raises(ValueError, match='忽略时间'):
        frontier.tradeoff(value, ignore_time=True)


def test_invalid_catalog_cannot_pass_even_from_unselected_context():
    value = catalog()
    value['candidates'][1]['metrics']['mean_error'] = float('nan')
    with pytest.raises(ValueError):
        frontier.tradeoff(value)
    value = catalog()
    value['candidates'][0]['config']['target'] = 'embedded'
    value['candidates'][0]['config']['representation'] = 'direct_rgb24'
    with pytest.raises(ValueError, match='embedded/portable'):
        frontier.validate_catalog(value)
    value = catalog()
    value['candidates'][0]['metrics']['workspace_bytes'] = 1
    with pytest.raises(ValueError, match='内存'):
        frontier.validate_catalog(value)


def test_budget_filter_precedes_frontier():
    value = catalog()
    # 平均误差/时间/内存都更好，但最差单图超标；不能先全局剪枝而丢掉合法候选。
    value['candidates'][0]['metrics'].update(mean_error=0, worst_image_mean=3, batch_ms=.1, runtime_bytes=1)
    result = frontier.tradeoff(value, max_error=.8)
    assert result['selected']['id'] == 'nonconvex'


def test_pending_catalog_has_no_fake_validation():
    value = catalog()
    for row in value['candidates']:
        row['verified'] = dict.fromkeys(frontier.VERIFICATIONS, False)
        row['metrics'] = {key: None for key in row['metrics']}
    assert frontier.validate_catalog(value)
    assert frontier.tradeoff(value)['status'] == 'no_feasible'


def test_plan_cartesian_m_and_deployment_constraints():
    sources = [{'path': f'lut{i}.lut256', 'sha256': str(i)*64} for i in range(1, 5)]
    plan = frontier.make_plan(sources, m_values=(17, 33))
    assert len(plan['models']) == 16
    assert [17, 33, 17, 33] in [row['m'] for row in plan['models']]
    assert all(row['status'] == 'planned_unverified' for row in plan['models'])
    assert all('fit' in row['command'] and '--m' in row['command'] for row in plan['models'])
    for config in plan['runtime_domain']:
        if config['target'] in ('embedded', 'portable'):
            assert (config['representation'], config['backend'], config['threads']) == ('sparse', 'scalar', 1)
    with pytest.raises(ValueError, match='预算'):
        frontier.make_plan(sources, m_values=(17, 25, 33), max_models=80)


def test_save_new_preserves_evidence(tmp_path):
    output = tmp_path / 'result.json'
    frontier.save_new(output, {'status': 'first'})
    original = output.read_bytes()
    with pytest.raises(FileExistsError):
        frontier.save_new(output, {'status': 'second'})
    assert output.read_bytes() == original
