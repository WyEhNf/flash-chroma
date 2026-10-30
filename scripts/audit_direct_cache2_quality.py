"""只读独立复核293/294新增资格及既有逐图SHA，不重新执行native或拟合。"""
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
ORIGINAL = Path('F:/Hackathon/projects/16-lut-color')
FROZEN = ROOT / 'artifacts/p16-direct-cache2-quality-frozen-v1/frozen.json'
OUT = ROOT / 'artifacts/p16-direct-cache2-quality-v1'


def sha(path):
    with Path(path).open('rb') as stream:
        return hashlib.file_digest(stream, 'sha256').hexdigest()


def main():
    target = OUT / 'independent-check.json'
    if target.exists():
        raise FileExistsError('不覆盖独立离线复核')
    frozen = json.loads(FROZEN.read_text(encoding='utf-8'))
    result_path = OUT / 'results.json'
    result = json.loads(result_path.read_text(encoding='utf-8'))
    assert result['passed'] and result['frozen_sha256'] == sha(FROZEN)
    for name, expected in frozen['sources_sha256'].items():
        assert sha(ROOT / name) == expected, name
    for name, expected in frozen['inputs_sha256'].items():
        assert sha(name) == expected, name
    expected = {k: v['oracle_sha256'] for k, v in frozen['models'].items()}
    singles = result['full_streams']
    assert len(singles) == 16
    assert {(r['variant'], r['model'], r['kernel'], r['path']) for r in singles} == {
        (v, m, k, p) for v in ['u16', 'rgb24'] for m in ['max41', 'old_best'] for k in ['scalar', 'avx2'] for p in ['inplace', 'to']}
    assert all(r['sha256'] == expected[r['model']] and r['mismatches'] == 0 and r['threads'] == 1 for r in singles)
    whole = result['whole4t_streams']
    assert len(whole) == 8 and result['full_stream_count'] == 24
    assert {(r['variant'], r['model'], r['path']) for r in whole} == {
        (v, m, p) for v in ['u16', 'rgb24'] for m in ['max41', 'old_best'] for p in ['inplace', 'to']}
    for row in whole:
        assert row['pixels'] == 2**24 and row['blocks'] == 256 and row['sha256'] == expected[row['model']] and not row['mismatches']
        assert len(set(row['surrounding_team_os_tids'])) == 4
    snapshots = result['read_only_team_snapshots']
    assert len(snapshots) == 16
    for snapshot in snapshots:
        assert snapshot['returncode'] == 0 and snapshot['action'] == 0 and len(snapshot['members']) == 4
        assert len({r['os_tid'] for r in snapshot['members']}) == 4
        for index, member in enumerate(snapshot['members']):
            assert member['version'] == 1 and member['omp_tid'] == index and member['team_size'] == 4
            assert member['set_attempted'] == 0 and member['mask_before'] == member['mask_after'] == 0x55
    for index, row in enumerate(whole):
        before, after = snapshots[2*index:2*index+2]
        assert row['surrounding_team_os_tids'] == [r['os_tid'] for r in before['members']] == [r['os_tid'] for r in after['members']]
    for variant in ['u16', 'rgb24']:
        current = result['capacity'][variant + '_max41']
        assert current['cache']['enabled'] and current['cache']['entries'] == 264222 and current['cache']['table_capacity_bytes'] == 1056888
        assert current['domain']['eligible'] and current['domain']['reachable_cells'] == 32768 and current['domain']['unproven_cells'] == 0
        assert current['wide']['enabled'] and current['wide']['format'] == (16 if variant == 'u16' else 18)
        assert current['wide']['table_capacity_bytes'] == ((2 if variant == 'u16' else 3)*2**24 + 4)
        previous = result['capacity'][variant + '_old_best']
        assert previous['palette']['enabled'] and previous['palette']['palette_size'] == 234 and not previous['wide']['enabled']
        assert previous['model_bytes'] == 18715824
    assert len(result['physical']) == 2 and all(r['all_values_equal_to_integer_oracle'] and r['guard_zero'] and r['entries'] == 2**24 for r in result['physical'])
    assert result['short_pattern_backend_cases'] == 972 and result['short_native_output_comparisons'] == 2916
    assert len(result['rejections']) == 4
    manifest = ORIGINAL / 'assets/photos/manifest.json'
    assert sha(manifest) == '10893812e0d3cecea7ba8b6bbf4700addd09927feed220149501def03c374f7c'
    images = json.loads(manifest.read_text(encoding='utf-8'))['images']
    assert len(images) == 100
    current_path = ROOT / 'artifacts/cinema-current-full-quality-v2/results.json'
    previous_path = ROOT / 'artifacts/p16-direct-rgb24-quality-v1/results.json'
    current = json.loads(current_path.read_text(encoding='utf-8'))
    previous = json.loads(previous_path.read_text(encoding='utf-8'))
    lookups = {'max41': {}, 'old_best': {}}
    for row in current['photo_matrix']:
        key = (row['image'], row['path'])
        assert not row['mismatches'] and lookups['max41'].setdefault(key, row['sha256']) == row['sha256']
    for row in previous['photo_matrix']:
        if row['model'] == 'old_best':
            key = (row['image'], row['path'])
            assert not row['mismatches'] and lookups['old_best'].setdefault(key, row['sha256']) == row['sha256']
    assert all(len(v) == 200 for v in lookups.values())
    photos = result['photos']
    assert len(photos) == 800 and result['photo_comparisons'] == 800
    assert len({(r['image_index'], r['variant'], r['model'], r['path']) for r in photos}) == 800
    for row in photos:
        key = (images[row['image_index']]['id'], row['path'])
        assert row['sha256'] == lookups[row['model']][key] and row['mismatches'] == 0
    modules = result['unique_libgomp']
    assert len(modules) == 1 and Path(modules[0]).resolve() == Path('E:/mingw64/bin/libgomp-1.dll').resolve()
    audit = {'passed': True, 'purpose': __doc__, 'frozen_sha256': sha(FROZEN), 'results_sha256': sha(result_path),
             'checked_sources': len(frozen['sources_sha256']), 'checked_inputs': len(frozen['inputs_sha256']),
             'new_full_streams': 24, 'whole4t': 8, 'read_only_team_snapshots': 16,
             'photo_sha_checks_against_prior_independent_native': 800, 'short_pattern_backend_cases': 972,
             'prior_current_results_sha256': sha(current_path), 'prior_best_results_sha256': sha(previous_path),
             'native_calls': 0, 'performance_calls': 0, 'limitations': '消费已保存原件与历史逐图SHA；不是新性能、bad_alloc或跨架构实机证明'}
    target.write_text(json.dumps(audit, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    print(json.dumps(audit, ensure_ascii=False))


if __name__ == '__main__':
    main()
