"""保存六案例原件并独立解码每TID六事件；不调用原生库。"""
import hashlib
import json
from pathlib import Path
import shutil
import struct

ROOT = Path(__file__).resolve().parents[3]
HERE = Path(__file__).resolve().parent


def read(path):
    return json.loads(path.read_text(encoding='utf-8'))


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    source = ROOT/'artifacts/skylake-four-thread-diagnostic-v1'
    target = HERE/'raw'
    if target.exists():
        raise ValueError('不得覆盖诊断档案')
    shutil.copytree(source, target)
    policy = read(ROOT/'experiments/skylake-four-thread-diagnostic-v1.json')
    results = read(target/'results.json')
    assert results['pass'] and results['warmup_calls'] == results['counted_calls'] == 6
    assert results['wallclock_calls'] == 0 and not results['threefold_goal_completed']
    events = [name for name, config in policy['events']]
    rows = []
    groups = 0
    for i, record in enumerate(results['records']):
        assert record['pass'] and record['source_unchanged'] and record['sentinels_unchanged']
        assert record['case'] == policy['cases'][i]['case']
        assert record['requested_threads'] == policy['cases'][i]['threads']
        assert record['output_sha256'] == record['warmup_output_sha256'] == record['output_sha256_expected']
        assert record['pixels'] == 78643200 and record['runtime_blocks'] == 1200
        summed = dict.fromkeys(events, 0)
        participants = []
        for counter in record['thread_counters']:
            raw = struct.unpack('<9Q', bytes.fromhex(counter['raw_group_read_hex']))
            assert raw[0] == 6
            assert raw[1:3] == (counter['time_enabled_ns'], counter['time_running_ns'])
            assert dict(zip(events, raw[3:])) == counter['counts']
            if counter['time_enabled_ns']:
                fraction = raw[2]/raw[1]
                assert fraction == counter['running_fraction'] and .99 <= fraction <= 1
            else:
                assert counter['inactive_zero_window']
            groups += 1
            if counter['participates_in_requested_team']:
                pixels = record['pixels']//record['requested_threads']
                assert pixels == counter['nominal_assigned_pixels']
                for event in events:
                    summed[event] += counter['counts'][event]
                    assert abs(counter['counts'][event]/pixels-counter['per_nominal_pixel'][event]) < 1e-14
                participants.append(counter['tid'])
        assert len(participants) == record['requested_threads']
        assert summed == record['participating_sum']['counts']
        for event in events:
            assert abs(summed[event]/record['pixels']-record['participating_sum']['per_nominal_pixel'][event]) < 1e-14
        for phase in ('before', 'after'):
            pages = record['table_'+phase]['paged_info']
            assert pages['fully_huge'] and pages['aligned_2m']
            assert pages['bytes'] == pages['smaps']['mapping_bytes'] == 2**24
        rows.append({'case': record['case'], 'threads': record['requested_threads'],
            'participating_tids': participants, 'per_nominal_pixel': record['participating_sum']['per_nominal_pixel'],
            'oldest_load_wait_cycle_fraction': summed['oldest_load_not_complete']/summed['cycles'],
            'individual_cycle_range': record['individual_cycle_range']})
    assert groups == 24
    libraries = HERE/'libraries'
    libraries.mkdir()
    for key in ('library', 'driver'):
        spec = policy[key]
        original = ROOT/spec['path']
        assert digest(original) == spec['sha256']
        shutil.copy2(original, libraries/original.name)
    offline = HERE/'normalized-dictionary-readonly'
    shutil.copytree(ROOT/'artifacts/skylake-normalized-dictionary-readonly-v1', offline)
    files = {p.relative_to(HERE).as_posix(): {'bytes': p.stat().st_size, 'sha256': digest(p)}
        for folder in (target, libraries, offline) for p in sorted(folder.rglob('*')) if p.is_file()}
    (HERE/'manifest.json').write_text(json.dumps({'schema': 1, 'files': files}, ensure_ascii=False, indent=2)+'\n', encoding='utf-8')
    audit = {'pass': True, 'files': len(files), 'raw_thread_groups': groups, 'cases': rows,
        'warmup_calls': 6, 'counted_calls': 6, 'new_wallclock_calls': 0,
        'threefold_goal_completed': False, 'scope': '独立解码24组六事件原始字节并核对参与线程求和、名义像素、输出和THP；含barrier/收尾，不证明缓存级或具体停顿根因。'}
    (HERE/'audit.json').write_text(json.dumps(audit, ensure_ascii=False, indent=2)+'\n', encoding='utf-8')
    print(json.dumps(audit, ensure_ascii=False))


if __name__ == '__main__':
    main()
