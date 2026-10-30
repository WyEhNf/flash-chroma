"""只读V2日志独立Counter/调用配对/地址关系审计；不导入本仓native桥。"""
import argparse
from collections import Counter, defaultdict
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def load(path):
    return json.loads(path.read_text(encoding='utf-8'))


def sha(path):
    with path.open('rb') as stream:
        return hashlib.file_digest(stream, 'sha256').hexdigest()


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    if args.output.exists():
        raise FileExistsError('独立审计不覆盖')
    plan_path = ROOT / 'experiments/page-id16-native-pages-finite-v2.json'
    directory = ROOT / 'artifacts/p16-page-native-pages-finite-v2'
    plan, run = load(plan_path), load(directory / 'run.json')
    results = load(directory / 'finite/results.json')
    observations = load(directory / 'finite/observations.json')
    assert sha(plan_path) == '907c17b1bf079bf700fd6e7191bf03231ac8be89a86ae3a01b5792ee3215c8a9'
    assert run['returncode'] == 0 and results['passed'] and 'failure' not in observations
    assert run['plan_sha256'] == results['plan_sha256'] == sha(plan_path)
    expected = dict(finite=534, io_rejections=243, format_prepare_rejections=42,
        other_prepare_rejections=64, failure_state_replays=53, lifecycle_scenarios=4,
        clear_rejections=8, image_guards=108, rom_guards=20, pointer_table_guards=20,
        unaligned_rom=40, fixture_pointer_equalities=16384)
    assert results['counts'] == observations['counts'] == plan['expected_counts'] == expected
    assert run['environment']['OMP_NUM_THREADS'] == '4'
    assert all(run['environment'][key] == '1' for key in
               ('OPENBLAS_NUM_THREADS', 'MKL_NUM_THREADS', 'NUMEXPR_NUM_THREADS'))
    records = [json.loads(line) for line in (directory / 'finite/events.jsonl').read_text(encoding='utf-8').splitlines()]
    kinds = Counter(row['event'] for row in records)
    assert kinds == {'native_attempt': 1175, 'native_return': 1175, 'receipt': 17520, 'finally': 1}
    assert records[-1] == dict(event='finally', native_attempts=1175, failed=False)
    receipts = [row for row in records if row['event'] == 'receipt']
    assert Counter(row['kind'] for row in receipts) == expected
    assert len({(row['kind'], row['label']) for row in receipts}) == len(receipts)
    by_kind = defaultdict(list)
    for row in receipts:
        by_kind[row['kind']].append(row['label'])
        assert row['count'] == len(by_kind[row['kind']])
    labels = ('core_out', 'c991_out', 'c991_in', 'c994_out', 'c994_in', 'core_in')
    lengths = (0, 1, 7, 8, 9, 31, 32, 40, 64, 72, 73, 405, 406, 1023, 1024,
               1025, 4095, 4096, 4097, 65535, 65536, 65537)
    finite_labels = {f'{mode}/{n}/{offset}' for mode in labels for n in lengths for offset in (0, 1, 3, 7)}
    finite_labels |= {mode + '/null-zero' for mode in labels}
    assert set(by_kind['finite']) == finite_labels
    image_lengths = (0, 1, 2, 3, 7, 8, 9, 15, 16, 17, 31, 32, 33, 65535, 65536,
                     65537, 131071, 131072)
    assert set(by_kind['image_guards']) == {f'{mode}/{n}' for mode in labels for n in image_lengths}
    fixture_names = ('actual', 'count1', 'count256', 'max4096')
    for kind in ('rom_guards', 'pointer_table_guards'):
        assert set(by_kind[kind]) == {f'{fixture}/{mode}' for fixture in fixture_names for mode in labels[:5]}
    assert set(by_kind['unaligned_rom']) == {f'{offset}/{mode}' for offset in range(8) for mode in labels[:5]}
    assert set(by_kind['fixture_pointer_equalities']) == {f'{fixture}/{index}' for fixture in fixture_names for index in range(4096)}
    assert results['events'] == [dict(kind=row['kind'], label=row['label']) for row in receipts]
    attempts, returns = {}, {}
    in_flight = set()
    for row in records:
        if row['event'] == 'native_attempt':
            assert row['ordinal'] == len(attempts) + 1 and not in_flight
            attempts[row['ordinal']] = row
            in_flight.add(row['ordinal'])
        elif row['event'] == 'native_return':
            assert row['ordinal'] in in_flight and row['ordinal'] not in returns
            returns[row['ordinal']] = row['returncode']
            in_flight.remove(row['ordinal'])
    assert not in_flight and set(attempts) == set(returns) == set(range(1, 1176))
    summary = Counter((attempts[index]['entry'], returns[index]) for index in attempts)
    expected_returns = {
        ('jshc_p4_pages_prepare', 0): 19, ('jshc_p4_pages_prepare', 1): 106,
        ('jshc_p4_pages_clear', 0): 22, ('jshc_p4_pages_clear', 1): 8,
        ('jshc_p4_pages_apply', 0): 285, ('jshc_p4_pages_apply', 1): 80,
        ('jshc_p4_pages_apply_parallel', 0): 492, ('jshc_p4_pages_apply_parallel', 1): 163,
    }
    assert summary == expected_returns
    expected_by_library = {
        'b326a9f3cc6dfa933964b65bf345bf15887d56c62904ad569554b42cf2e93ced':
            dict(prepare=124, clear=29, core=0, omp_c99=655),
        '11860791a48ea49e85c32e1e8277bf7b5ad98fbae3ffc58c5102bbf9da9a80bf':
            dict(prepare=1, clear=1, core=365, omp_c99=0),
    }
    names = dict(jshc_p4_pages_prepare='prepare', jshc_p4_pages_clear='clear',
                 jshc_p4_pages_apply='core', jshc_p4_pages_apply_parallel='omp_c99')
    actual_libraries = defaultdict(Counter)
    for row in attempts.values():
        actual_libraries[row['library_sha256']][names[row['entry']]] += 1
    assert set(actual_libraries) == set(expected_by_library)
    for library_sha, expected_calls in expected_by_library.items():
        assert dict(actual_libraries[library_sha]) == {name: value for name, value in expected_calls.items() if value}
    assert observations['native_attempts'] == 1175
    assert observations['native_entry_receipts'] == results['native_entry_receipts']
    for receipt in results['native_entry_receipts']:
        assert receipt['calls'] == expected_by_library[receipt['sha256']]
        assert receipt['addresses']['jshc_p4_pages_apply'] != receipt['addresses']['jshc_p4_apply']
        assert plan['input_sha256'][receipt['path']] == receipt['sha256']
    overlaps = []
    rom_guards, pointer_guards, offsets = [], [], []
    for row in attempts.values():
        if row['entry'] != 'jshc_p4_pages_prepare':
            continue
        params, label, view = row['parameters'], row['case_hint'], row['view_address']
        if label in ('view-slots-full', 'view-slots-partial', 'view-blob-full',
                     'view-blob-partial', 'slots-blob-full', 'slots-blob-partial'):
            partial = label.endswith('partial')
            if label.startswith('view-slots'):
                assert params['slots'] == view + (40 if partial else 0)
            elif label.startswith('view-blob'):
                assert params['blob'] == view + (40 if partial else 0)
            else:
                assert params['blob'] == params['slots'] + (32760 if partial else 0)
            assert returns[row['ordinal']] == 1
            overlaps.append(dict(label=label, view=view, blob=params['blob'], slots=params['slots']))
        if label.startswith('rom-guard-prepare/'):
            assert (params['blob'] + params['bytes']) % 4096 == 0
            rom_guards.append(label)
        if label.startswith('pointer-guard-prepare/'):
            assert params['slots'] % 4096 == 0 and (params['slots'] + 32768) % 4096 == 0
            pointer_guards.append(label)
        if label.startswith('unaligned-prepare/'):
            offset = int(label.rsplit('/', 1)[1])
            assert params['blob'] % 8 == offset
            offsets.append(offset)
    assert len(overlaps) == 12 and Counter(item['label'] for item in overlaps) == {
        name: 2 for name in ('view-slots-full', 'view-slots-partial', 'view-blob-full',
                            'view-blob-partial', 'slots-blob-full', 'slots-blob-partial')}
    assert len(rom_guards) == len(pointer_guards) == 4 and offsets == list(range(8))
    self_overlap = [row for row in attempts.values() if row['case_hint'].endswith('/slots-view')]
    assert len(self_overlap) == 6 and all(returns[row['ordinal']] == 1 for row in self_overlap)
    assert results['actual_capacity'] == 12633124 + 32768 + 48 == 12665940
    args.output.parent.mkdir(parents=True, exist_ok=True)
    value = dict(passed=True, purpose=__doc__, script_sha256=sha(Path(__file__)),
        counts=expected, jsonl_records=len(records), model_native_attempts=1175,
        return_distribution=[dict(entry=entry, returncode=code, count=count)
                             for (entry, code), count in sorted(summary.items())],
        per_library=expected_by_library, prepare_overlap_address_checks=overlaps,
        rom_tail_alignment_checks=rom_guards, pointer_tail_alignment_checks=pointer_guards,
        actual_unaligned_residues=offsets,
        resources=observations['after'], before=observations['before'],
        inputs={str(path.relative_to(ROOT)): sha(path) for path in
                (plan_path, directory / 'run.json', directory / 'stdout.txt', directory / 'stderr.txt',
                 directory / 'finite/results.json', directory / 'finite/events.jsonl',
                 directory / 'finite/observations.json')},
        scope='独立日志Counter/集合/返回配对和记录的prepare地址关系，不加载DLL/再调native；self-overlap runtime只记录view地址和拒绝返回，pages=self地址依据绑定的冻结V2赋值源，未独立dump每个view/pages字段。16384槽值未原样dump，日志证明原断言完成，不冒充再次读取指针内存。full/photos/perf/WASM均未执行，进程峰含Python/库/oracle/夹具/日志。')
    args.output.write_text(json.dumps(value, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    print(dict(passed=True, counts=expected, attempts=1175, records=len(records),
               audit_sha256=sha(args.output)), flush=True)


if __name__ == '__main__':
    main()
