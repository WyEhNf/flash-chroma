"""标准库tuple/dict独立重建全部九字节组，不查询后缀，不复用NumPy unique。"""
from __future__ import annotations
import argparse
from collections import Counter
from pathlib import Path
import numpy as np
from count_cinema_current_box_group import OUT, load_frozen, read, save, sha


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    if args.output.exists():
        raise FileExistsError('不覆盖同盒tuple独立审计')
    frozen = load_frozen()
    result = read(OUT/'summary.json')
    assert result['groups_sha256'] == sha(OUT/'groups.npz')
    with np.load(frozen['inputs']['old_aabb']['path']) as data:
        lower, upper, gold, keys = [data[n] for n in ('lower_rgb','upper_rgb','gold','keys')]
        old_count = data['state_count']
    with np.load(OUT/'groups.npz') as data:
        grouped = {n:data[n] for n in data.files}
    np.testing.assert_array_equal(keys, grouped['source_keys'])
    members = {}
    logical = 0
    for i, (lo,hi,target) in enumerate(zip(lower,upper,gold)):
        key = tuple(int(v) for row in (lo,hi,target) for v in row)
        count = 1
        for a,b in zip(lo,hi):
            width = int(b)-int(a)+1
            assert 1 <= width <= 5
            count *= width
        assert int(old_count[i]) == count == int(grouped['point_state_count'][i])
        logical += count
        members.setdefault(key, []).append(i)
    ordered = sorted(members)
    assert len(ordered) == len(grouped['group_keys']) == result['groups']
    assert logical == result['logical_point_states'] == 5284765
    inverse = [None]*len(keys)
    query = 0
    counts = Counter()
    for j,key in enumerate(ordered):
        rows = members[key]
        assert tuple(int(v) for v in grouped['group_keys'][j]) == key
        assert int(grouped['representative'][j]) == rows[0]
        assert int(grouped['multiplicity'][j]) == len(rows)
        n = (key[3]-key[0]+1)*(key[4]-key[1]+1)*(key[5]-key[2]+1)
        assert int(grouped['group_state_count'][j]) == n
        query += n
        for row in rows:
            inverse[row] = j
            counts[j] += 1
    assert inverse == grouped['inverse'].tolist() and all(v is not None for v in inverse)
    assert [counts[j] for j in range(len(ordered))] == grouped['multiplicity'].tolist()
    limit = frozen['plan']['资源门']['maximum_group_query_states_per_complete_path']
    assert query == result['grouped_query_states'] and (query <= limit) == result['within_gate']
    assert result['true_suffix_state_queries'] == result['aggregate_true_suffix_state_queries'] == 0
    save(args.output, dict(**{'pass':True}, frozen_sha256=sha(OUT/'frozen.json'), summary_sha256=sha(OUT/'summary.json'),
        groups_sha256=sha(OUT/'groups.npz'), original_points=len(keys), groups=len(ordered),
        logical_point_states=logical, grouped_query_states=query, query_limit=limit, within_gate=query<=limit,
        independent_tuple_rows=len(keys), complete_inverse_and_members_equal=True,
        true_suffix_state_queries=0, solver_calls=0, performance_samples=0))
    print({'independent_pass':True, 'original_points':len(keys), 'groups':len(ordered), 'grouped_query_states':query}, flush=True)


if __name__ == '__main__':
    main()
