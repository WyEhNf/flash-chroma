"""只读完整质量日志，独立配对820调用和64块/100图身份；不加载native。"""
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
        raise FileExistsError('完整质量独立审计不覆盖')
    plan_path = ROOT / 'experiments/page-id16-native-pages-full-v1.json'
    directory = ROOT / 'artifacts/p16-page-native-pages-full-v1'
    plan, run = load(plan_path), load(directory / 'run.json')
    result = load(directory / 'quality/results.json')
    observed = load(directory / 'quality/observations.json')
    plan_sha = sha(plan_path)
    assert plan_sha == 'c345f5bbc3118bff60854bba07e7b96ff5a782209a96466641655c75e7b10dc1'
    assert run['returncode'] == 0 and result['passed'] and 'failure' not in observed
    assert run['plan_sha256'] == result['plan_sha256'] == plan_sha
    labels = ('core_out', 'c991_out', 'c991_in', 'c994_out', 'c994_in')
    assert result['per_mode_apply_attempts'] == observed['per_mode_apply_attempts'] == {label: 164 for label in labels}
    assert result['total_apply_attempts'] == observed['total_apply_attempts'] == 820
    expected_full = '3c9ce8d98d8db454ce9337c50c2ecadb8ba59485d6bc3e6a42e3cc1dfe307c22'
    expected_photos = 'f3c0d9078bbcf069f33060a45021a28985b70c9616493ba9bea1ac2027858528'
    photos_input = 'e13278cfc91c3411b3c242232239f9ea6fbda3bf5d18c3f17c41a4dedf57defd'
    assert result['full_hashes'] == {label: expected_full for label in labels}
    assert result['photos_hashes'] == {label: expected_photos for label in labels}
    assert result['photos_input_sha256'] == plan['input_sha256'][plan['photos']] == photos_input
    assert plan['input_sha256'][plan['original_rom']] == '146a5f283aaf5d895e4e375990166924b2fe9d6f6f092989f8023b8b8295acc5'
    assert plan['input_sha256'][plan['page_rom']] == 'a953eef0d1a70763a4bca053d4d70dc00dae6e40cc8eecdd1ac48648dfa15173'
    assert run['environment']['OMP_NUM_THREADS'] == '4'
    assert all(run['environment'][key] == '1' for key in ('OPENBLAS_NUM_THREADS', 'MKL_NUM_THREADS', 'NUMEXPR_NUM_THREADS'))
    rows = [json.loads(line) for line in (directory / 'quality/apply-events.jsonl').read_text(encoding='utf-8').splitlines()]
    assert Counter(row['event'] for row in rows) == {'apply_attempt': 820, 'apply_return': 820, 'finally': 1}
    assert rows[-1] == dict(event='finally', apply_attempts=820, failed=False)
    calls, returns = {}, {}
    active = set()
    for row in rows:
        if row['event'] == 'apply_attempt':
            assert row['ordinal'] == len(calls) + 1 and not active
            calls[row['ordinal']] = row
            active.add(row['ordinal'])
        elif row['event'] == 'apply_return':
            assert row['ordinal'] in active and row['ordinal'] not in returns
            assert row['returncode'] == 0 and row['equal_to_independent_u64']
            returns[row['ordinal']] = row
            active.remove(row['ordinal'])
    assert not active and set(calls) == set(returns) == set(range(1, 821))
    full_rows, photo_rows = result['full_rows'], result['photo_rows']
    assert [row['begin'] for row in full_rows] == list(range(0, 1 << 24, 1 << 18))
    assert all(row['pixels'] == 1 << 18 for row in full_rows)
    assert [row['image'] for row in photo_rows] == list(range(100))
    expected_cases = {}
    for row in full_rows:
        assert row['modes'] == {label: row['oracle_sha256'] for label in labels}
        for label in labels:
            expected_cases[('full/' + str(row['begin']), label)] = (1 << 18, row['oracle_sha256'])
    for row in photo_rows:
        assert row['modes'] == {label: row['oracle_sha256'] for label in labels}
        for label in labels:
            expected_cases[('photo/' + str(row['image']), label)] = (1024 * 768, row['oracle_sha256'])
    assert Counter((row['case'], row['mode']) for row in calls.values()) == {case: 1 for case in expected_cases}
    receipts = result['native_entry_receipts']
    assert receipts == observed['native_entry_receipts']
    libraries = {item['sha256']: item for item in receipts}
    main_sha = 'b326a9f3cc6dfa933964b65bf345bf15887d56c62904ad569554b42cf2e93ced'
    core_sha = '11860791a48ea49e85c32e1e8277bf7b5ad98fbae3ffc58c5102bbf9da9a80bf'
    assert set(libraries) == {main_sha, core_sha}
    assert libraries[main_sha]['calls'] == dict(prepare=1, clear=1, core=0, omp_c99=656)
    assert libraries[core_sha]['calls'] == dict(prepare=1, clear=1, core=164, omp_c99=0)
    fields = defaultdict(set)
    counts = Counter()
    for ordinal, row in calls.items():
        label = row['mode']
        pixels, output_sha = expected_cases[(row['case'], label)]
        assert row['pixels'] == pixels and returns[ordinal]['output_sha256'] == output_sha
        expected_library = core_sha if label == 'core_out' else main_sha
        expected_symbol = 'jshc_p4_pages_apply' if label == 'core_out' else 'jshc_p4_pages_apply_parallel'
        assert row['library_sha256'] == expected_library and row['symbol'] == expected_symbol
        assert row['symbol_address'] == libraries[expected_library]['addresses'][expected_symbol]
        assert row['threads'] == (None if label == 'core_out' else 1 if label.startswith('c991') else 4)
        assert (row['source'] == row['target']) == label.endswith('_in')
        assert row['view_address'] % 8 == row['pages_address'] % 8 == 0
        fields[expected_library].add((row['view_address'], row['pages_address']))
        counts[label] += 1
    assert all(len(items) == 1 for items in fields.values())
    assert counts == {label: 164 for label in labels}
    assert result['actual_rom_bytes'] == 12633124 and result['actual_view_bytes'] == 48 and result['actual_slots_bytes'] == 32768
    assert result['actual_capacity'] == 12633124 + 32768 + 48 == 12665940
    args.output.parent.mkdir(parents=True, exist_ok=True)
    value = dict(passed=True, purpose=__doc__, script_sha256=sha(Path(__file__)),
        full_modes=5, full_blocks=64, full_pixels_per_mode=1 << 24, photos_per_mode=100,
        apply_attempts=820, model_native_calls_including_setup_clear=824,
        per_mode=dict(counts), full_sha256=expected_full, photos_sha256=expected_photos,
        photos_input_sha256=photos_input, actual_capacity=12665940,
        resources=observed['after'], before=observed['before'],
        inputs={str(path.relative_to(ROOT)): sha(path) for path in (plan_path,
            directory / 'run.json', directory / 'stdout.txt', directory / 'stderr.txt',
            directory / 'quality/results.json', directory / 'quality/apply-events.jsonl',
            directory / 'quality/observations.json')},
        scope='只从冻结协议/输入SHA/运行时逐块逐图u64等值与SHA日志独立核配对/覆盖/入口/借用地址；不重读图像再生成输出或运行四级整数插值，不加载DLL/native重跑。完整汇总SHA由原质量过程保存，未从block digest反推原像素。精确输出不等于原模型误差为零，未性能/WASM。')
    args.output.write_text(json.dumps(value, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    print(dict(passed=True, apply_attempts=820, full_blocks=64, photos=100,
               audit_sha256=sha(args.output)), flush=True)


if __name__ == '__main__':
    main()
