"""冻结/有限合同/一次同盒geometry计数；不读取真实suffix状态，不建CP。"""
from __future__ import annotations
import argparse
import ast
import hashlib
import itertools
import json
from pathlib import Path
import sys
import numpy as np
import psutil
from cinema_box_group import group_boxes, geometry_totals

ROOT = Path(__file__).resolve().parents[1]
OLD = ROOT / 'artifacts/cinema-current-all-max-support-v1'
OUT = ROOT / 'artifacts/cinema-current-box-group-geometry-v1'
PLAN = ROOT / 'experiments/p16-cinema-current-box-group-v1.json'


def sha(path):
    with Path(path).open('rb') as stream:
        return hashlib.file_digest(stream, 'sha256').hexdigest()


def read(path):
    return json.loads(Path(path).read_text(encoding='utf-8'))


def save(path, value):
    if path.exists():
        raise FileExistsError('不覆盖同盒geometry证据：' + str(path))
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')


def freeze():
    if OUT.exists():
        raise FileExistsError('不覆盖同盒geometry阶段')
    old_path = OLD / 'frozen.json'
    assert sha(old_path) == 'b425b230315a04a742434df0db38b057d533ff108da84c17d45a9f48a779c37d'
    prior = read(old_path)
    summary_path = OLD / 'summary.json'
    assert sha(summary_path) == '926c6a6ae6cee7f911fc9e61fe11cee61a13e33f58c87fa5ad10041027eff165'
    summary = read(summary_path)
    assert summary['stop'] == 'state_count_gate' and summary['state_queries'] == 0
    assert summary['aabb_states'] == 5284765 and summary['complete_support_rows'] == 171271
    aabb = OLD / 'aabb.npz'
    assert sha(aabb) == summary['aabb_sha256'] == '1e8038aedfb6730930219e6ac3bf56c79c65dacdeab2252d7b953a43ba77c1fe'
    audit_path = ROOT / 'artifacts/cinema-current-all-max-support-independent-v1.json'
    audit = read(audit_path)
    assert audit['pass'] and audit['frozen_sha256'] == sha(old_path) and audit['summary_sha256'] == sha(summary_path)
    assert audit['full_cube_selection_independent_rows'] == 1 << 24 and audit['endpoint_integer_rows'] == 342542
    assert audit['complete_support_rows'] == 171271 and audit['aabb_states'] == 5284765
    sources = dict(prior['source_sha256'])
    for name in ('scripts/cinema_box_group.py', 'scripts/count_cinema_current_box_group.py',
                 'scripts/audit_cinema_current_box_group.py', 'experiments/p16-cinema-current-box-group-v1.json',
                 'experiments/p16-cinema-current-box-group-proposal-v1.md'):
        sources[name] = sha(ROOT / name)
    for name, expected in sources.items():
        assert sha(ROOT / name) == expected, name
        if name.endswith('.py'):
            ast.parse((ROOT / name).read_text(encoding='utf-8-sig'))
    inputs = dict(prior['inputs'])
    for name, path in [('old_freeze', old_path), ('old_summary', summary_path), ('old_aabb', aabb),
                       ('old_independent', audit_path), ('old_selection', OLD / 'selection.json'),
                       ('old_selection_arrays', OLD / 'selection.npz')]:
        inputs[name] = {'path': str(path), 'sha256': sha(path)}
    for name, spec in inputs.items():
        assert sha(spec['path']) == spec['sha256'], name
    save(OUT / 'frozen.json', dict(ast_pass=True, source_sha256=sources, inputs=inputs,
        plan=read(PLAN), python=sys.version, numpy=np.__version__, psutil=psutil.__version__, byteorder=sys.byteorder,
        old_state_gate_preserved=True, true_suffix_state_queries=0, solver_calls=0,
        test_type='共享host只读geometry规模，非性能；真实suffix入口尚未授权'))
    print({'frozen_sha256': sha(OUT / 'frozen.json'), 'sources': len(sources), 'inputs': len(inputs)}, flush=True)


def load_frozen():
    frozen = read(OUT / 'frozen.json')
    for name, expected in frozen['source_sha256'].items():
        assert sha(ROOT / name) == expected, name
    for name, spec in frozen['inputs'].items():
        assert sha(spec['path']) == spec['sha256'], name
    return frozen


def simple_stats(lower, upper, gold):
    points = []
    for lo, hi, target in zip(lower, upper, gold):
        rows = list(itertools.product(*[range(int(a), int(b) + 1) for a,b in zip(lo, hi)]))
        q = [sum((int(x)-int(t))**2 for x,t in zip(rgb, target)) for rgb in rows]
        safe = [list(rgb) for rgb, value in zip(rows, q) if value <= 40]
        points.append(([min(q), max(q), len(q), len(safe), max((v for v in q if v <= 40), default=-1)], safe))
    return points


def contract():
    frozen = load_frozen()
    if (OUT / 'contract.json').exists():
        raise FileExistsError('不覆盖同盒有限合同')
    records = []
    cases = [
        ('duplicate_zero_mass', [[0,0,0],[0,0,0],[0,0,0]], [[4,4,4]]*3, [[0,0,0]]*3, [0,2,0]),
        ('same_box_different_gold', [[1,2,3]]*2, [[3,4,5]]*2, [[0,0,0],[255,255,255]], [0,1]),
        ('same_span_different_position', [[1,2,3],[2,3,4]], [[3,4,5],[4,5,6]], [[0,0,0]]*2, [1,0]),
        ('clip_boundary_mixed_empty', [[251,251,251],[255,255,255],[0,0,0]],
            [[255,255,255],[255,255,255],[0,0,0]], [[255,255,255],[0,0,0],[0,0,0]], [0,1,1]),
        ('unsorted_duplicates', [[5,6,7],[0,0,0],[5,6,7],[2,2,2],[0,0,0]],
            [[7,8,9],[4,4,4],[7,8,9],[2,2,2],[4,4,4]], [[6,6,6],[1,1,1],[6,6,6],[9,9,9],[1,1,1]], [1,0,2,0,4]),
        ('empty_input', [], [], [], [])]
    for name, lo, hi, gold, frequency in cases:
        lower, upper, target = [np.asarray(v, np.uint8).reshape(-1,3) for v in (lo,hi,gold)]
        grouped = group_boxes(lower, upper, target)
        exact = simple_stats(lower, upper, target)
        unique = grouped['group_keys']
        shared = simple_stats(unique[:,:3], unique[:,3:6], unique[:,6:9])
        assert exact == [shared[int(i)] for i in grouped['inverse']]
        independent = {}
        for i, key in enumerate(zip(lo,hi,gold)):
            flat = tuple(int(v) for rgb in key for v in rgb)
            independent.setdefault(flat, []).append(i)
        assert len(grouped['group_keys']) == len(independent)
        assert grouped['group_keys'].tolist() == [list(key) for key in sorted(independent)]
        for j, key in enumerate(sorted(independent)):
            assert int(grouped['representative'][j]) == independent[key][0]
            assert int(grouped['multiplicity'][j]) == len(independent[key])
        totals = geometry_totals(grouped, 4194304)
        assert totals['logical_point_states'] == sum(v[0][2] for v in exact)
        assert totals['grouped_query_states'] == sum(v[0][2] for v in shared)
        danger = sum(v[0][1] > 40 for v in exact)
        safe = sum(len(v[1]) for v in exact if v[0][1] > 40)
        assert danger == sum(int(grouped['multiplicity'][j]) for j,v in enumerate(shared) if v[0][1] > 40)
        assert safe == sum(int(grouped['multiplicity'][j])*len(v[1]) for j,v in enumerate(shared) if v[0][1] > 40)
        records.append(dict(name=name, original_rows=len(lo), groups=len(unique), totals=totals,
            original_dangerous_rows=danger, original_safe_rows=safe, zero_training_mass_rows=frequency.count(0),
            full_expanded_stats_and_csr_equal=True))
    unit = group_boxes(np.zeros((1,3),np.uint8), np.zeros((1,3),np.uint8), np.zeros((1,3),np.uint8))
    assert geometry_totals(unit, 1)['within_group_query_gate'] and not geometry_totals(unit, 0)['within_group_query_gate']
    rejects = 0
    for args in [(np.zeros((1,3),np.int16),)*3,
                 (np.array([[1,0,0]],np.uint8),np.zeros((1,3),np.uint8),np.zeros((1,3),np.uint8)),
                 (np.zeros((1,3),np.uint8),np.array([[5,0,0]],np.uint8),np.zeros((1,3),np.uint8))]:
        try:
            group_boxes(*args)
        except ValueError:
            rejects += 1
    assert rejects == 3
    save(OUT / 'contract.json', {'pass':True, 'frozen_sha256':sha(OUT/'frozen.json'), 'cases':records,
        'gate_boundary_cases':2, 'invalid_domain_rejects':rejects, 'true_suffix_state_queries':0, 'solver_calls':0})
    print({'contract_pass': True, 'finite_cases': len(records), 'gate_cases': 2, 'rejects': rejects}, flush=True)


def count():
    frozen = load_frozen()
    finite = read(OUT/'contract.json')
    assert finite['pass'] and finite['frozen_sha256'] == sha(OUT/'frozen.json')
    save(OUT/'start.json', dict(frozen_sha256=sha(OUT/'frozen.json'), contract_sha256=sha(OUT/'contract.json'),
         true_suffix_state_queries=0, solver_calls=0))
    with np.load(frozen['inputs']['old_aabb']['path']) as data:
        arrays = {n:data[n] for n in data.files}
    assert len(arrays['keys']) == 171271 and len(arrays['selected_nodes']) == 273 and len(arrays['hotspot_keys']) == 231
    assert np.all(np.diff(arrays['keys'].astype(np.int64)) > 0)
    grouped = group_boxes(arrays['lower_rgb'], arrays['upper_rgb'], arrays['gold'])
    np.testing.assert_array_equal(grouped['point_state_count'].astype(np.int32), arrays['state_count'])
    limit = frozen['plan']['资源门']['maximum_group_query_states_per_complete_path']
    totals = geometry_totals(grouped, limit)
    assert totals['logical_point_states'] == 5284765 and totals['maximum_group_states'] <= 125
    np.savez_compressed(OUT/'groups.npz', source_keys=arrays['keys'], **grouped)
    result = dict(**totals, pass_geometry_reconstruction=True, within_gate=totals['within_group_query_gate'],
        stop=None if totals['within_group_query_gate'] else 'group_query_state_gate',
        frozen_sha256=sha(OUT/'frozen.json'), contract_sha256=sha(OUT/'contract.json'), groups_sha256=sha(OUT/'groups.npz'),
        original_aabb_sha256=frozen['inputs']['old_aabb']['sha256'], original_state_gate_preserved=True,
        true_suffix_state_queries=0, independent_true_suffix_state_queries=0, aggregate_true_suffix_state_queries=0,
        complete_original_support_rows=171271, selected_physical_nodes=273, original_q41_points=231,
        old_logical_state_stop='state_count_gate', dangerous_original_point_gate=8192, safe_original_table_row_gate=500000,
        source_array_payload_bytes=sum(v.nbytes for v in arrays.values()), group_array_payload_bytes=sum(v.nbytes for v in grouped.values()),
        process_memory_observation=psutil.Process().memory_info()._asdict(),
        memory_scope='记录时刻/OS累计峰的进程观察与数组有效载荷；不是部署RAM或所有表达式暂态的精确和',
        solver_calls=0, performance_samples=0,
        scope='唯一完整geometry分组计数，无真实后缀状态查询；门内不自动安全统计/CP或候选')
    load_frozen()
    save(OUT/'summary.json', result)
    print({k:result[k] for k in ('groups','logical_point_states','grouped_query_states','within_gate','true_suffix_state_queries')}, flush=True)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('mode', choices=('freeze','contract','count'))
    args = parser.parse_args()
    {'freeze':freeze, 'contract':contract, 'count':count}[args.mode]()
