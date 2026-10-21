"""独立核对诊断、59完整域及单次周期筛查；不执行像素或新计时。"""
from pathlib import Path
import hashlib
import json
import sys

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / 'report/data/skylake-lookup-overlap-v1'


def read(path):
    return json.loads(path.read_text(encoding='utf-8'))


def digest(path):
    with path.open('rb') as stream:
        return hashlib.file_digest(stream, 'sha256').hexdigest()


def main():
    manifest = read(DATA / 'manifest.json')
    for name, spec in manifest['files'].items():
        path = DATA / name
        assert path.stat().st_size == spec['bytes'] and digest(path) == spec['sha256'], name
    plan_path = ROOT / 'experiments/skylake-vectorpack-v1.json'
    policy_path = ROOT / 'experiments/skylake-vectorpack-pmu-v1.json'
    plan, policy = read(plan_path), read(policy_path)
    assert policy['models_plan']['sha256'] == digest(plan_path)
    assert policy['script']['sha256'] == digest(ROOT / policy['script']['path'])
    for name, value in plan['source_sha256'].items():
        assert digest(ROOT / name) == value, name
    build = read(DATA / 'skylake-vectorpack-linux-build-v1/build.json')
    static = read(DATA / 'skylake-vectorpack-linux-static-v1/results.json')
    full = read(DATA / 'skylake-vectorpack-linux-full-v1/results.json')
    pmu = read(DATA / 'skylake-vectorpack-pmu-v1/results.json')
    diagnostic = read(DATA / 'skylake-lookup-diagnostics-v1/profile-v1/results.json')
    layout = read(DATA / 'skylake-lookup-diagnostics-v1/layout-64-window-v1.json')
    assert build['plan_sha256'] == digest(plan_path)
    assert static['pass'] and static['external_calls'] == 0 and static['pext_instructions'] == 0
    assert static['new_pixel_calls'] == 0 and static['new_performance_calls'] == 0
    assert full['pass'] and full['byte_mismatches'] == 0 and full['sentinel_mismatches'] == 0
    assert full['independent_table_colors'] == 2**24
    assert len(full['full_domain_pixels_per_configuration']) == 12
    assert len(full['outplace_full_pixels']) == 12
    assert set(full['full_domain_pixels_per_configuration'].values()) == {2**24}
    assert set(full['outplace_full_pixels'].values()) == {2**24}
    assert full['direct_table_sha256'] == 'a020c67a0e8ce77e668e6c6d85206af53005923316b4778194637182b4cfaea0'
    assert full['performance_calls'] == 0 and full['photo_calls'] == 0
    assert pmu['profile_completed'] and pmu['candidate_counted_calls'] == 4
    assert pmu['candidate_wallclock_timing_calls'] == 0
    rows = {(r['requested_threads'], r['variant']): r for r in pmu['records']}
    ratios = {}
    for threads in (1, 4):
        reference = rows[(threads, 'reference40')]
        candidate = rows[(threads, 'vectorpack59')]
        for record in (reference, candidate):
            assert record['multiplexing_acceptable']
            assert record['output_sha256'] == policy['expected_output_sha256']
            assert record['paged_info']['fully_huge']
        ratios[str(threads)] = candidate['cycles_per_pixel'] / reference['cycles_per_pixel']
    assert ratios['1'] > policy['screen']['one_thread_cycle_ratio_max']
    assert diagnostic['pass'] and diagnostic['wallclock_calls'] == 0
    cases = {r['case']: r for r in diagnostic['records']}
    assert cases['photo_inplace']['oldest_load_wait_cycle_fraction'] > 0.6
    assert cases['uniform_inplace']['oldest_load_wait_cycle_fraction'] < 0.1
    assert layout['candidate_pixel_calls'] == 0 and layout['candidate_timing_calls'] == 0
    result = {'pass': True, 'archived_files': len(manifest['files']), 'full_domain_api_configs': 24,
              'cycle_ratios_vs_same_session_40': ratios, 'screen_pass': False,
              'new_full_wallclock_calls': 0, 'goal_threefold_completed': False,
              'scope': '归档字节、源码、全域回执、PMU门槛与诊断；不重新测量'}
    path = DATA / 'independent-audit.json'
    if path.exists():
        raise ValueError('不得覆盖复核回执')
    path.write_text(json.dumps(result, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    print(json.dumps(result, ensure_ascii=False))


if __name__ == '__main__':
    main()
