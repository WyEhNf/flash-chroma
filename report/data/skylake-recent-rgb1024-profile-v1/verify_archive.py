"""从ZIP只读复核固定1024项备忘筛查；不执行analyze.py、不重新扫描命中。"""
from __future__ import annotations
import argparse
import ast
import datetime
import hashlib
import json
import math
import platform
import sys
import zipfile
from collections import Counter
from pathlib import Path

PINNED = {
    'analyze.py': '59acc137701d53b8de0fb36efe2740386a6f8bcb4fbdc8300250d868796bdd1e',
    'protocol.json': 'e359d4e137cb1519d6ffc550ca34c26e5e1a71af2863b181aef2559e9619bc9d',
    'analysis.json': 'e03d142a6a0c3bb71a3a060df9c3e0875d4252aa628842d00cc94baffa06b84e',
    'exit.json': 'a99d8f980a12828daa94a05c90c343765bcc556916968a5cebcd8384121c2126',
}
COUNT_FIELDS = ('hits', 'misses', 'cold', 'collision', 'repeat_collision', 'first_seen_collision')
RUN_BOUNDS = (8, 16, 32, 64, 128, 256, 1024)


def sha_bytes(value):
    return hashlib.sha256(value).hexdigest()


def sha_file(path):
    with Path(path).open('rb') as handle:
        return hashlib.file_digest(handle, 'sha256').hexdigest()


def close(left, right):
    assert math.isclose(left, right, rel_tol=0, abs_tol=1e-15), (left, right)


def histogram(value):
    result = Counter()
    for key, count in value.items():
        number = int(key)
        assert str(number) == key and number >= 0 and type(count) is int and count > 0
        result[number] = count
    return result


def verify_runs(value, pixels):
    hist = histogram(value['length_histogram'])
    assert all(1 <= length <= 65536 for length in hist)
    assert sum(hist.values()) == value['runs']
    assert sum(length * count for length, count in hist.items()) == pixels == value['pixels']
    assert max(hist, default=0) == value['maximum']
    for numerator, denominator, label in ((1, 2, 'p50'), (9, 10, 'p90'), (99, 100, 'p99')):
        rank = (value['runs'] * numerator + denominator - 1) // denominator
        cumulative, answer = 0, 0
        for length, count in sorted(hist.items()):
            cumulative += count
            if cumulative >= rank:
                answer = length
                break
        assert value['nearest_rank'][label] == (answer if value['runs'] else 0)
    assert value['runs_at_least'] == {str(bound): sum(count for length, count in hist.items() if length >= bound) for bound in RUN_BOUNDS}
    return hist


def verify_counts(row, pixels):
    assert row['pixels'] == pixels
    assert all(type(row[key]) is int and row[key] >= 0 for key in COUNT_FIELDS)
    assert row['hits'] + row['misses'] == pixels
    assert row['cold'] + row['collision'] == row['misses']
    assert row['repeat_collision'] + row['first_seen_collision'] == row['collision']
    close(row['hit_fraction'], row['hits'] / pixels)


def verify_small_reference(record):
    assert record['passed'] is True and record['collision_fixture'] == [0, 610, 1597]
    first, second, third = record['collision_fixture']
    cases = [
        ('unique', list(range(24)), [0] * 24),
        ('same', [0xffffff] * 24, [0] * 24),
        ('alternating_collision', [first, second] * 12, [0] * 24),
        ('clustered_collision', [first] * 6 + [second] * 6 + [first] * 6 + [third] * 6, [0] * 24),
        ('explicit_reset_labels', [first, first, second, first, second, second, first, first] * 3, [0] * 8 + [1] * 8 + [2] * 8),
        ('rgb_boundaries_and_wrap', [0, 0xffffff, 0xff0000, 0x00ff00, 0x0000ff, 0x800000, 0x010101, 0x010101] * 3, [0] * 16 + [1] * 8),
    ]
    assert len(record['cases']) == len(cases)
    for saved, (name, codes, labels) in zip(record['cases'], cases):
        counts = Counter(hit=0, cold=0, collision=0, repeat_collision=0, first_seen_collision=0)
        last_label = None
        for code, label in zip(codes, labels):
            if label != last_label:
                cache, seen = [None] * 1024, set()
                last_label = label
            slot = ((code * 0x9e3779b1) & 0xffffffff) >> 22
            if cache[slot] is None:
                counts['cold'] += 1
            elif cache[slot] == code:
                counts['hit'] += 1
            else:
                counts['collision'] += 1
                counts['repeat_collision' if code in seen else 'first_seen_collision'] += 1
            cache[slot] = code
            seen.add(code)
        assert saved['case'] == name and saved['pixels'] == len(codes)
        assert saved['explicit_synthetic_blocks'] == len(set(labels))
        assert saved['flags_equal'] is True and saved['run_histograms_equal'] is True
        assert saved['counts'] == dict(counts)
    return len(cases)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--repository', type=Path)
    parser.add_argument('--compare-originals', action='store_true')
    parser.add_argument('--rehash-inputs', action='store_true')
    parser.add_argument('--output', type=Path)
    args = parser.parse_args()
    if args.output:
        assert not args.output.exists(), '输出不得覆盖已有证据'
    if args.compare_originals or args.rehash_inputs:
        assert args.repository is not None, '重读工作区需要显式--repository'
    archive = Path(__file__).resolve().parent
    manifest_raw = (archive / 'manifest.json').read_bytes()
    manifest = json.loads(manifest_raw)
    assert manifest['verifier_sha256'] == sha_file(__file__)
    zip_path = archive / 'evidence.zip'
    assert zip_path.stat().st_size == manifest['archive_bytes']
    assert sha_file(zip_path) == manifest['archive_sha256']
    assert len(manifest['files']) == 5
    raw = {}
    with zipfile.ZipFile(zip_path) as z:
        assert len(z.infolist()) == 5 and len(set(z.namelist())) == 5
        assert set(z.namelist()) == set(PINNED) | {'execution-start.json'}
        for item in manifest['files']:
            content = z.read(item['member'])
            assert len(content) == item['bytes'] and sha_bytes(content) == item['sha256']
            if item['member'] in PINNED:
                assert item['sha256'] == PINNED[item['member']]
            if args.compare_originals:
                assert (args.repository / item['source']).read_bytes() == content
            raw[item['member']] = content
    p, a = json.loads(raw['protocol.json']), json.loads(raw['analysis.json'])
    start, end = json.loads(raw['execution-start.json']), json.loads(raw['exit.json'])
    ast.parse(raw['analyze.py'].decode('utf-8'))
    for record in (p, a, start, end):
        assert record['script_sha256'] == sha_bytes(raw['analyze.py'])
    for record in (a, start, end):
        assert record['protocol_sha256'] == sha_bytes(raw['protocol.json'])
    assert end['analysis_sha256'] == sha_bytes(raw['analysis.json'])
    assert end['exit_code'] == 0 and end['analysis_completed'] is True
    assert end['gate_passed'] is False and a['analysis_completed'] is True
    assert datetime.datetime.fromisoformat(p['frozen_utc']) < datetime.datetime.fromisoformat(start['started_utc']) < datetime.datetime.fromisoformat(end['ended_utc'])
    assert start['maximum_analysis_executions'] == p['attempt_policy']['maximum_analysis_executions'] == 1
    assert not any(p['attempt_policy'][key] for key in ('overwrite', 'automatic_retry', 'scan_entries', 'scan_hash', 'scan_reset_window', 'change_gates'))
    assert p['analysis_executions'] == 0
    assert p['cache'] == a['cache'] and p['classification'] == a['classification']
    assert p['cache']['entries'] == 1024 and p['cache']['entry_bytes'] == 8 and p['cache']['bytes_per_cache'] == 8192
    assert p['cache']['hash_multiplier'] == 0x9e3779b1 and p['cache']['hash_shift'] == 22
    assert p['cache']['reset_pixels'] == 65536
    assert p['gate'] == dict(total_hit_fraction_min=.65, any_image_hit_fraction_min=.35, block_internal_transition_fraction_max=.02)
    assert p['inputs'] == a['inputs']
    for record in (p, a, start, end):
        for key in ('native_calls', 'performance_calls', 'compiler_calls', 'model_calls'):
            assert record[key] == 0
    assert a['candidate_native_calls'] == a['new_fits'] == 0
    cases = verify_small_reference(a['small_synthetic_reference'])
    input_rehashes = []
    photo_metadata = None
    if args.rehash_inputs:
        for name, spec in p['inputs'].items():
            path = args.repository / spec['path']
            assert path.stat().st_size == spec['bytes'] and sha_file(path) == spec['sha256']
            input_rehashes.append(dict(name=name, **spec))
        photo_metadata = json.loads((args.repository / p['inputs']['manifest']['path']).read_text(encoding='utf-8'))['images']
        assert len(photo_metadata) == 100
    assert len(a['per_image']) == 100
    total_counts, transition_histogram = Counter(), Counter()
    global_hit_hist, global_miss_hist = Counter(), Counter()
    all_blocks = []
    for index, row in enumerate(a['per_image']):
        assert row['image_index'] == index and row['blocks'] == 12 and len(row['per_block']) == 12
        verify_counts(row, 786432)
        if photo_metadata is not None:
            assert row['image_id'] == photo_metadata[index]['id']
            assert row['input_sha256'] == photo_metadata[index]['evaluation']['pixel_sha256']
        block_counts, block_transitions = Counter(), Counter()
        for block_index, block in enumerate(row['per_block']):
            assert block['image_index'] == index and block['block_index'] == block_index
            assert block['first_pixel'] == block_index * 65536
            verify_counts(block, 65536)
            assert 1 <= block['cold'] <= 1024
            assert block['transition_edges'] == 65535 and 0 <= block['transition_count'] <= 65535
            close(block['transition_fraction'], block['transition_count'] / 65535)
            assert block['hit_runs'] + block['miss_runs'] == block['transition_count'] + 1
            for state, pixels_key in (('hit', 'hits'), ('miss', 'misses')):
                if block[pixels_key] == 0:
                    assert block[state + '_runs'] == block['longest_' + state + '_run'] == 0
                else:
                    assert 1 <= block[state + '_runs'] <= block[pixels_key]
                    assert 1 <= block['longest_' + state + '_run'] <= block[pixels_key]
                    assert block[state + '_runs'] * block['longest_' + state + '_run'] >= block[pixels_key]
            block_counts.update({key: block[key] for key in COUNT_FIELDS})
            block_transitions[block['transition_count']] += 1
            all_blocks.append(block)
        assert dict(block_counts) == {key: row[key] for key in COUNT_FIELDS}
        assert block_transitions == histogram(row['block_transition_count_histogram'])
        transitions = sum(key * count for key, count in block_transitions.items())
        assert row['transition_count'] == transitions and row['transition_edges'] == 12 * 65535
        close(row['transition_fraction'], transitions / row['transition_edges'])
        hit_hist, miss_hist = verify_runs(row['hit_runs'], row['hits']), verify_runs(row['miss_runs'], row['misses'])
        for state in ('hit', 'miss'):
            assert row[state + '_runs']['runs'] == sum(block[state + '_runs'] for block in row['per_block'])
            assert row[state + '_runs']['maximum'] == max(block['longest_' + state + '_run'] for block in row['per_block'])
        assert row['hit_runs']['runs'] + row['miss_runs']['runs'] == transitions + 12
        global_hit_hist.update(hit_hist)
        global_miss_hist.update(miss_hist)
        transition_histogram.update(block_transitions)
        total_counts.update(block_counts)
    total = a['total']
    assert total['images'] == 100 and total['blocks'] == len(all_blocks) == 1200
    verify_counts(total, 78643200)
    assert dict(total_counts) == {key: total[key] for key in COUNT_FIELDS}
    assert transition_histogram == histogram(total['block_transition_count_histogram'])
    transitions = sum(key * count for key, count in transition_histogram.items())
    assert total['transition_count'] == transitions == 12972523
    assert total['transition_edges'] == 1200 * 65535 == 78642000
    close(total['transition_fraction'], transitions / total['transition_edges'])
    assert global_hit_hist == verify_runs(total['hit_runs'], total['hits'])
    assert global_miss_hist == verify_runs(total['miss_runs'], total['misses'])
    assert total['hit_runs']['runs'] + total['miss_runs']['runs'] == transitions + 1200
    worst = min(a['per_image'], key=lambda row: row['hit_fraction'])
    assert total['worst_hit_image_index'] == worst['image_index'] == 49
    assert total['worst_hit_image_id'] == worst['image_id'] == 'div2k-0835'
    close(total['worst_hit_image_fraction'], worst['hit_fraction'])
    close(total['max_image_transition_fraction'], max(row['transition_fraction'] for row in a['per_image']))
    close(total['max_block_transition_fraction'], max(row['transition_fraction'] for row in all_blocks))
    if args.rehash_inputs:
        with (args.repository / p['inputs']['photos']['path']).open('rb') as handle:
            for row in a['per_image']:
                photo = handle.read(2359296)
                assert len(photo) == 2359296 and sha_bytes(photo) == row['input_sha256']
            assert handle.read(1) == b''
    gate = dict(total_hit_fraction=total['hits'] / total['pixels'], total_hit_fraction_min=.65,
        total_hit_pass=total['hits'] / total['pixels'] >= .65,
        any_image_hit_fraction=worst['hits'] / worst['pixels'], any_image_hit_fraction_min=.35,
        per_image_pass=worst['hits'] / worst['pixels'] >= .35,
        block_internal_transition_fraction=transitions / 78642000,
        block_internal_transition_fraction_max=.02, transition_pass=transitions / 78642000 <= .02)
    gate['passed'] = all(gate[key] for key in ('total_hit_pass', 'per_image_pass', 'transition_pass'))
    assert gate == a['gate'] and not any(gate[key] for key in ('total_hit_pass', 'per_image_pass', 'transition_pass', 'passed'))
    report = dict(purpose=__doc__, audit_completed=True, audit_passed=True,
        completed_utc=datetime.datetime.now(datetime.timezone.utc).isoformat(),
        environment=dict(platform=platform.platform(), python=sys.version, executable=sys.executable, dependencies='Python标准库'),
        verifier_sha256=sha_file(__file__), manifest_sha256=sha_bytes(manifest_raw),
        archive_sha256=manifest['archive_sha256'], originals_sha256={name: sha_bytes(value) for name, value in raw.items()},
        originals_byte_comparison=args.compare_originals, input_rehashes=input_rehashes,
        per_image_input_rehashes=100 if args.rehash_inputs else 0,
        verified=dict(images=100, blocks=1200, classification_counts=dict(total_counts),
            transitions=transitions, transition_edges=78642000, exact_per_image_run_histograms=200,
            aggregate_run_histograms_equal=True, per_block_run_counts_and_maxima_equal=True,
            small_reference_cases=cases, saved_numpy_self_test_passed=True,
            fresh_numpy_self_test_execution=False,
            images_below_hit_gate=sum(row['hit_fraction'] < .35 for row in a['per_image']),
            gate=gate, hit_run_quantiles=total['hit_runs']['nearest_rank'],
            miss_run_quantiles=total['miss_runs']['nearest_rank']),
        limitations=['仅复核原件和已有统计，没有重跑全照片命中模拟或原始analyze.py。',
            '逐图精确run长度直方图重新加总为全局；原件逐块只有run数/最长值，不能独立重建逐块精确长度分布。',
            '小合成标准库分类重新计算并核对已存自测结果；没有再次执行原始NumPy排序自测。',
            '没有候选RGB缓存值、原生性能、完整RGB8或实际Skylake验证。',
            '同目录回执证明已存唯一执行链，不证明其他未记录路径没有执行。'],
        original_analysis_executions_added=0, runtime_implementations_added=0, native_calls=0,
        performance_calls=0, compiler_calls=0, model_calls=0, full_domain_calls=0)
    if args.output:
        with args.output.open('x', encoding='utf-8', newline='\n') as handle:
            json.dump(report, handle, ensure_ascii=False, indent=2, allow_nan=False)
            handle.write('\n')
    print(json.dumps(dict(audit_passed=True, original_gate_passed=False, images=100, blocks=1200,
        originals_byte_compared=args.compare_originals, input_rehashes=len(input_rehashes),
        audit_sha256=sha_file(args.output) if args.output else None), ensure_ascii=False))


if __name__ == '__main__':
    main()
