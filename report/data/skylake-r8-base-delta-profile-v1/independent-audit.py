"""仅以标准库重哈希输入并复算已有JSON；不导入或执行原始profile。"""
from __future__ import annotations
import argparse
import ast
import datetime
import hashlib
import json
import math
import platform
import re
import struct
import sys
from pathlib import Path

FROZEN = {
    'analyze.py': 'c88f0113f4c1d6e68b4185cdb55f2140f04aa5ecacaf8e2aa390dc45269516ef',
    'freeze.py': '0f9d1f0d5c07e7aa15085ee436e93d537a32bd787e17a2d415a1ed2e85dba871',
    'history.json': '5ff8da38c49e8d4ec208177f901c1f8bbb5b3f68cf344ae27f56675762f78a72',
    'protocol.json': '4a6dd2693d75ce092c509400d164c63c409099eb54da55c54550c6354aca1192',
    'analysis.json': '31dcb62f0ca647b64554206e46ed761bcbb10e0b83475159af3681ab266d4783',
    'exit.json': '89909f3a06ace5fc4e83af330460e73cdfe7232bc1fa07f886c70561f49ec946',
}


def sha(path):
    with Path(path).open('rb') as handle:
        return hashlib.file_digest(handle, 'sha256').hexdigest()


def read(path):
    return json.loads(Path(path).read_text(encoding='utf-8'))


def same_float(left, right):
    assert math.isclose(left, right, rel_tol=0, abs_tol=1e-15), (left, right)


def integer_histogram(value, length):
    assert len(value) == length
    assert all(type(x) is int and x >= 0 for x in value)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--repository', type=Path, default=Path(__file__).resolve().parents[3])
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    root, archive = args.repository.resolve(), Path(__file__).resolve().parent
    assert not args.output.exists(), '新审计输出不得覆盖已有文件'
    manifest = read(archive / 'manifest.json')
    assert len(manifest['files']) == 8
    originals = {}
    for item in manifest['files']:
        source, copy = root / item['source'], archive / item['archive']
        assert source.stat().st_size == copy.stat().st_size == item['bytes']
        assert sha(source) == sha(copy) == item['sha256']
        name = copy.name
        assert name not in originals
        if name in FROZEN:
            assert item['sha256'] == FROZEN[name]
        originals[name] = item['sha256']
    expected_names = set(FROZEN) | {'preparation.json', 'execution-start.json'}
    assert set(originals) == expected_names
    orig = archive / 'original'
    p, a = read(orig / 'protocol.json'), read(orig / 'analysis.json')
    h, preparation = read(orig / 'history.json'), read(orig / 'preparation.json')
    start, end = read(orig / 'execution-start.json'), read(orig / 'exit.json')
    for filename in ('analyze.py', 'freeze.py'):
        ast.parse((orig / filename).read_text(encoding='utf-8'))
    for record in (p, a, start, end):
        assert record['script_sha256'] == originals['analyze.py']
    for record in (a, preparation, start, end):
        assert record['protocol_sha256'] == originals['protocol.json']
    for record in (p, a, preparation):
        assert record['history_sha256'] == originals['history.json']
    assert p['freeze_script_sha256'] == preparation['freeze_sha256'] == originals['freeze.py']
    assert preparation['analyze_sha256'] == originals['analyze.py']
    assert preparation['ast_parse_passed'] and preparation['analysis_executions'] == 0
    assert end['analysis_sha256'] == originals['analysis.json']
    assert end['exit_code'] == 0 and end['analysis_completed'] and a['analysis_completed']
    assert not end['gate_passed']
    assert datetime.datetime.fromisoformat(p['frozen_utc']) < datetime.datetime.fromisoformat(start['started_utc']) < datetime.datetime.fromisoformat(end['ended_utc'])
    assert p['attempt_policy'] == dict(maximum_analysis_executions=1, overwrite=False,
        automatic_retry=False, scan_bits=False, scan_block_size=False, scan_channel_order=False,
        failure_action='停止；保留原始失败与退出回执，不重新分配位数重扫')
    assert start['maximum_analysis_executions'] == 1
    assert p['encoding']['delta_bits'] == [2, 2, 1]
    assert p['encoding']['input_block_pixels'] == 8
    assert p['gate'] == dict(exception_packet8_fraction_max=.05,
        any_image_exception_packet8_fraction_max=.20, exception_pool_bytes_max=2097152)
    assert a['inputs'] == p['inputs'] and a['encoding'] == p['encoding']
    for record in (p, a, preparation, start, end):
        for key in ('native_calls', 'performance_calls', 'compiler_calls'):
            assert record[key] == 0
    assert a['new_fits'] == 0
    checked_inputs = []
    for name, item in p['inputs'].items():
        path = root / item['path']
        assert path.stat().st_size == item['bytes']
        assert sha(path) == item['sha256']
        checked_inputs.append(dict(name=name, **item))
    previous = p['previous_profile_identity']
    assert sha(root / previous['path']) == previous['sha256']
    assert not h['direct_equivalent_found']
    for item in h['sources']:
        assert sha(root / item['path']) == item['sha256']
    cache = (root / p['inputs']['cache_gold']['path']).read_bytes()
    palette = sorted(set(value[0] for value in struct.iter_unpack('<I', cache)))
    old = [value[0] for value in struct.iter_unpack('<I', (root / p['inputs']['old_palette_crosscheck']['path']).read_bytes())]
    assert len(palette) == 230 and all(0 <= x <= 0xffffff for x in palette)
    assert len(old) == 256 and old[:230] == palette and old[230:] == [0] * 26
    cross = a['palette_crosscheck']
    assert cross['entries'] == 230 and cross['values_rgb32'] == palette
    integer_histogram(cross['cube_frequency'], 230)
    assert sum(cross['cube_frequency']) == 16777216
    assert cross['used_cube_entries'] == sum(x != 0 for x in cross['cube_frequency']) == 221
    generation = read(root / p['inputs']['cache_generation']['path'])
    assert generation['generation_completed'] and generation['gold_sha256'] == p['inputs']['cache_gold']['sha256']
    f = a['full_domain']
    assert f['colors'] == 16777216 and f['blocks'] == 2097152
    reasons = ['base_R_outside_0_255', 'base_G_outside_0_255', 'base_B_outside_0_255',
        'base_RGB_equals_ffffff', 'delta_R_outside_0_3', 'delta_G_minus_R_outside_0_3', 'delta_B_minus_R_outside_0_1']
    assert f['failure_reasons'] == reasons
    histogram = f['failure_reason_bitmask_histogram']
    integer_histogram(histogram, 128)
    assert sum(histogram) == f['blocks']
    assert histogram[0] == f['normal_blocks'] == 1151995
    assert sum(histogram[1:]) == f['exception_blocks'] == f['sentinel_count'] == 945157
    counts = {name: sum(value for code, value in enumerate(histogram) if code & (1 << bit)) for bit, name in enumerate(reasons)}
    assert counts == f['failure_reason_counts_overlapping']
    overlaps = [[sum(value for code, value in enumerate(histogram) if code & (1 << left) and code & (1 << right)) for right in range(7)] for left in range(7)]
    assert overlaps == f['failure_reason_pairwise_overlap']
    assert f['base_white_blocks'] == f['all_white_blocks'] == counts['base_RGB_equals_ffffff'] == 0
    spans = f['span_histograms']
    for name, bounds in [('R', 'delta_R'), ('G_minus_R', 'delta_DG'), ('B_minus_R', 'delta_DB')]:
        integer_histogram(spans[name], 511)
        assert sum(spans[name]) == f['blocks']
        assert f['value_ranges'][bounds] == [0, max(index for index, count in enumerate(spans[name]) if count)]
    assert sum(spans['R'][4:]) == counts[reasons[4]] == 931518
    assert sum(spans['G_minus_R'][4:]) == counts[reasons[5]] == 0
    assert sum(spans['B_minus_R'][2:]) == counts[reasons[6]] == 242230
    for name, bounds in f['value_ranges'].items():
        assert len(bounds) == 2 and bounds[0] <= bounds[1]
        if name.startswith('normal_') or name.startswith('source_'):
            assert 0 <= bounds[0] <= bounds[1] <= 255
    for key in ('inverse_mismatches', 'main_table_line_mismatches', 'decoded_pixel_differences',
                'decoded_byte_differences', 'normal_channel_carry_violations'):
        assert f[key] == 0
    assert f['decoded_output_sha256'] == p['inputs']['cube']['sha256']
    assert f['pool_ordinals_contiguous'] is True
    assert f['main_table_bytes'] == f['blocks'] * 8 == 16777216
    assert f['exception_pool_bytes'] == f['exception_blocks'] * 32 == 30245024
    assert f['total_payload_bytes'] == f['main_table_bytes'] + f['exception_pool_bytes'] == 47022240
    same_float(f['exception_block_fraction'], f['exception_blocks'] / f['blocks'])
    for key in ('linear_rgb32_sha256', 'main_table_sha256', 'exception_pool_sha256'):
        assert re.fullmatch('[0-9a-f]{64}', f[key])
    photo_manifest = read(root / p['inputs']['manifest']['path'])['images']
    rows, totals = a['per_image'], a['photos']
    assert len(rows) == len(photo_manifest) == totals['images'] == 100
    aggregate_histogram, all_photo_hash = [0] * 9, hashlib.sha256()
    with (root / p['inputs']['photos']['path']).open('rb') as photo_file:
        for index, (row, image) in enumerate(zip(rows, photo_manifest)):
            assert row['image_index'] == index and row['image_id'] == image['id']
            raw = photo_file.read(1024 * 768 * 3)
            assert len(raw) == 1024 * 768 * 3
            actual_sha = hashlib.sha256(raw).hexdigest()
            all_photo_hash.update(raw)
            assert actual_sha == row['input_sha256'] == image['evaluation']['pixel_sha256']
            assert row['pixels'] == 786432 and row['packets8'] == 98304
            photo_histogram = row['exception_pixels_per_packet8_histogram']
            integer_histogram(photo_histogram, 9)
            assert sum(photo_histogram) == row['packets8']
            assert sum(photo_histogram[1:]) == row['exception_packets8']
            assert sum(hits * count for hits, count in enumerate(photo_histogram)) == row['exception_pixels']
            same_float(row['exception_packet8_fraction'], row['exception_packets8'] / row['packets8'])
            same_float(row['exception_pixel_fraction'], row['exception_pixels'] / row['pixels'])
            assert row['decoded_pixel_differences'] == row['decoded_byte_differences'] == 0
            assert re.fullmatch('[0-9a-f]{64}', row['decoded_output_sha256'])
            aggregate_histogram = [x + y for x, y in zip(aggregate_histogram, photo_histogram)]
        assert photo_file.read(1) == b''
    assert all_photo_hash.hexdigest() == p['inputs']['photos']['sha256']
    assert aggregate_histogram == totals['exception_pixels_per_packet8_histogram']
    for key in ('pixels', 'packets8', 'exception_packets8', 'exception_pixels', 'decoded_pixel_differences', 'decoded_byte_differences'):
        assert totals[key] == sum(row[key] for row in rows)
    same_float(totals['exception_packet8_fraction'], totals['exception_packets8'] / totals['packets8'])
    same_float(totals['exception_pixel_fraction'], totals['exception_pixels'] / totals['pixels'])
    worst = max(rows, key=lambda row: row['exception_packet8_fraction'])
    assert totals['worst_image_index'] == worst['image_index'] == 31
    assert totals['worst_image_id'] == worst['image_id'] == 'div2k-0814'
    same_float(totals['worst_image_exception_packet8_fraction'], worst['exception_packet8_fraction'])
    over = [row['image_index'] for row in rows if row['exception_packet8_fraction'] > p['gate']['any_image_exception_packet8_fraction_max']]
    assert totals['images_over_individual_gate'] == over and len(over) == 96
    assert totals['decoded_output_sha256'] == p['expected_photo_output_sha256']
    gate = dict(full_domain_exact=all(f[key] == 0 for key in ('inverse_mismatches', 'main_table_line_mismatches', 'decoded_pixel_differences', 'decoded_byte_differences', 'normal_channel_carry_violations')) and f['decoded_output_sha256'] == p['inputs']['cube']['sha256'],
        photos_exact=totals['decoded_pixel_differences'] == totals['decoded_byte_differences'] == 0 and totals['decoded_output_sha256'] == p['expected_photo_output_sha256'],
        exception_packet8_fraction=totals['exception_packets8'] / totals['packets8'], exception_packet8_fraction_max=.05,
        exception_packets_pass=totals['exception_packets8'] / totals['packets8'] <= .05,
        any_image_exception_packet8_fraction=worst['exception_packet8_fraction'], any_image_exception_packet8_fraction_max=.20,
        per_image_pass=worst['exception_packet8_fraction'] <= .20,
        exception_pool_bytes=f['exception_blocks'] * 32, exception_pool_bytes_max=2097152,
        exception_pool_pass=f['exception_blocks'] * 32 <= 2097152)
    gate['passed'] = all(gate[key] for key in ('full_domain_exact', 'photos_exact', 'exception_packets_pass', 'per_image_pass', 'exception_pool_pass'))
    assert gate == a['gate'] and not gate['passed']
    assert [key for key in ('exception_packets_pass', 'per_image_pass', 'exception_pool_pass') if not gate[key]] == ['exception_packets_pass', 'per_image_pass', 'exception_pool_pass']
    greater = {name: sum(spans[name][bound + 1:]) for name, bound in [('R', 7), ('G_minus_R', 3), ('B_minus_R', 3)]}
    assert greater == {'R': 475327, 'G_minus_R': 0, 'B_minus_R': 31783}
    lower_blocks, upper_blocks = max(greater.values()), sum(greater.values())
    assert lower_blocks * 32 == 15210464 > p['gate']['exception_pool_bytes_max']
    resource_bound = dict(purpose='仅复用已有跨度直方图，不构造或执行7bit拆平面方案',
        hypothetical_format='16MiB主表：baseR8加八个3+2+2bit差分；2MiB平面：baseDG4/baseDB3/例外标志；例外块32B',
        blocks_exceeding_deltas=greater, residual_exception_union_lower_blocks=lower_blocks,
        residual_exception_union_upper_blocks=upper_blocks, exception_pool_lower_bytes=lower_blocks * 32,
        residual_exception_pool_upper_bytes=upper_blocks * 32, exception_pool_gate_bytes=2097152,
        fixed_planes_bytes=18 * 1048576, payload_lower_bytes=18 * 1048576 + lower_blocks * 32,
        decision='异常池下界已超过2MiB；不实现、不另跑profile；不把上界当作完整格式的精确池大小')
    result = dict(purpose=__doc__, audit_completed=True, passed=True,
        completed_utc=datetime.datetime.now(datetime.timezone.utc).isoformat(),
        environment=dict(platform=platform.platform(), python=sys.version, executable=sys.executable, dependencies='Python标准库；不导入NumPy'),
        audit_script_sha256=sha(__file__), manifest_sha256=sha(archive / 'manifest.json'), originals=originals,
        original_byte_copies=8, input_rehashes=checked_inputs, history_source_rehashes=len(h['sources']), previous_profile_rehashed=previous,
        source_review=dict(identity_frozen=True, ast_parse_passed=True,
            coverage='人工审阅固定int32符号差分、uint64打包、coarse/fine映射、正常通道累加进位及完整R切片/100图循环；审计未调用原脚本函数',
            full_domain_reconstruction_in_original='16,777,216色，R从0到255，每片G/B完整笛卡尔积；索引逆映射、主表行等式及实际通道加法超255检查',
            photo_reconstruction_in_original='100图各786432像素；像素0起不重叠8包，无偏移扫描；逐图像素/字节及输出SHA，合并完整输出SHA'),
        summary=dict(full_domain_blocks=f['blocks'], normal_blocks=f['normal_blocks'], exception_blocks=f['exception_blocks'],
            failure_reason_counts_overlapping=counts, full_domain_total_bytes=f['total_payload_bytes'], photos_images=100,
            photo_packets8=totals['packets8'], photo_exception_packets8=totals['exception_packets8'],
            per_image_input_hashes_verified=100, worst_image_index=31, images_over_gate=len(over),
            full_domain_histograms_recomputed_from_raw_cube=False, photo_exception_histograms_recomputed_from_pixels=False),
        original_gate_recomputed=gate, split_plane_7bit_resource_bound=resource_bound,
        limitations=['审计独立重哈希大cube/photos及全部照片输入分片，但未重新编码或解码完整色域、照片。',
            '完整域/逐图零差与输出SHA核对属于冻结原结果及算法覆盖审阅，不是第二次独立执行的完整精度结论。',
            '主表、线性RGB32和异常池仅在原profile内存存在；当前只有其SHA与大小，未保存或重建二进制。',
            '原件x模式回执限定同目录单次执行；不证明未记录的其他路径执行次数，也不构成性能计时证据。',
            '历史差异判断只覆盖history.json列出的小源码与阶段说明，不能证明全部历史或业界不存在相同机制。',
            '新7bit方案只得出差分异常并集资源下界，未计算联合直方图、逐图异常率或实现性能。',
            '没有候选原生、编译、性能、拟合或实际Skylake测试；全局目标仍未达成。'],
        original_analysis_executions_added=0, native_calls=0, performance_calls=0, compiler_calls=0, new_fits=0)
    with args.output.open('x', encoding='utf-8', newline='\n') as handle:
        json.dump(result, handle, ensure_ascii=False, indent=2, allow_nan=False)
        handle.write('\n')
    print(json.dumps(dict(audit_passed=True, original_gate_passed=False,
        original_copies=8, photo_inputs_rehashed=100, audit_sha256=sha(args.output)), ensure_ascii=False))


if __name__ == '__main__':
    main()
