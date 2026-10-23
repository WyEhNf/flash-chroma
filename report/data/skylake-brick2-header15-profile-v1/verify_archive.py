"""只读核验2³输入/header15残差6/tag63的ZIP证据；不执行原分析或重建主词与池。"""
import argparse, ast, datetime, hashlib, json, math, platform, re, struct, sys, zipfile
from pathlib import Path

PINNED = {
    'analyze.py': '1ee565baae333ecf40b0af0ca295e741d38138ab6dd255fd9cb4ef9517cc7a6f',
    'protocol.json': 'f852982dedc149a53a22576a90fb4ba46ae891ff5e380677cba888e7cb0ec15a',
    'execution-start.json': '1d417489212c1af129b0b57bcf6ec1398054160d6728d0cc133d4eef27c9072b',
    'analysis.json': 'efaa960d621ecbdbdc6732ed23e8b803a1ebf73cd533fe83bcb118d699243a16',
    'exit.json': 'eeba4e08074f6d5f8354d285d79e047f2360d9844dbbff6cef6e57cfa5d62a97',
}

def digest(data): return hashlib.sha256(data).hexdigest()

def file_sha(path):
    with Path(path).open('rb') as handle: return hashlib.file_digest(handle, 'sha256').hexdigest()

def close(left, right): assert math.isclose(left, right, rel_tol=0, abs_tol=1e-15), (left, right)

def histogram(values, length):
    assert len(values) == length and all(type(value) is int and value >= 0 for value in values)

def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--repository', type=Path)
    parser.add_argument('--compare-originals', action='store_true')
    parser.add_argument('--rehash-inputs', action='store_true')
    parser.add_argument('--output', type=Path)
    args = parser.parse_args()
    if args.output: assert not args.output.exists(), '不得覆盖已有审计'
    if args.compare_originals or args.rehash_inputs: assert args.repository is not None
    folder = Path(__file__).resolve().parent
    manifest_raw = (folder / 'manifest.json').read_bytes(); manifest = json.loads(manifest_raw)
    assert manifest['verifier_sha256'] == file_sha(__file__)
    zpath = folder / 'evidence.zip'
    assert zpath.stat().st_size == manifest['archive_bytes'] and file_sha(zpath) == manifest['archive_sha256']
    assert len(manifest['files']) == 5
    raw = {}
    with zipfile.ZipFile(zpath) as z:
        assert len(z.infolist()) == len(set(z.namelist())) == 5 and set(z.namelist()) == set(PINNED)
        for item in manifest['files']:
            content = z.read(item['member'])
            assert len(content) == item['bytes'] and digest(content) == item['sha256'] == PINNED[item['member']]
            if args.compare_originals: assert (args.repository / item['source']).read_bytes() == content
            raw[item['member']] = content
    p, a = json.loads(raw['protocol.json']), json.loads(raw['analysis.json'])
    start, end = json.loads(raw['execution-start.json']), json.loads(raw['exit.json'])
    ast.parse(raw['analyze.py'].decode('utf-8'))
    for record in (p, a, start, end): assert record['script_sha256'] == PINNED['analyze.py']
    for record in (a, start, end): assert record['protocol_sha256'] == PINNED['protocol.json']
    assert end['analysis_sha256'] == PINNED['analysis.json']
    assert a['analysis_completed'] and end['analysis_completed'] and end['exit_code'] == 0 and not end['gate_passed']
    assert datetime.datetime.fromisoformat(p['frozen_utc']) < datetime.datetime.fromisoformat(start['started_utc']) < datetime.datetime.fromisoformat(end['ended_utc'])
    assert p['analysis_executions'] == 0 and start['maximum_analysis_executions'] == p['attempt_policy']['maximum_analysis_executions'] == 1
    assert not any(p['attempt_policy'][key] for key in ('overwrite', 'automatic_retry', 'scan_bits', 'scan_geometry', 'scan_channel_order', 'change_gates'))
    global_keys = ('global_minDG', 'global_minDB', 'global_spanDG', 'global_spanDB')
    derived = {key: a['encoding'][key] for key in global_keys}
    assert all(type(value) is int for value in derived.values())
    assert a['encoding'] == dict(p['encoding'], **derived) and p['encoding']['input_block_shape'] == [2, 2, 2]
    assert p['encoding']['input_block_pixels'] == 8 and p['encoding']['delta_bits'] == [3, 2, 1]
    assert p['encoding']['format'] == 'brick2-header15-residual6-tag63-v1'
    assert 0 <= derived['global_spanDG'] <= 15 and 0 <= derived['global_spanDB'] <= 7
    assert a['prior_profile'] == p['prior_profile'] and a['mathematical_bound'] == p['mathematical_bound']
    assert p['prior_profile']['sha256'] == '9da1460d4836af7d4831b21ac73e8c14e46c15144e1dbd0ba39d312a4ea9b779'
    bound = p['mathematical_bound']
    assert bound['source_result_sha256'] == p['prior_profile']['sha256']
    assert bound['old_geometry_reason_counts'] == dict(R_span_greater_7=102, DG_span_greater_3=0, DB_span_greater_1=63542, synthetic_base_outside_RGB8=0, synthetic_base_white=0)
    lower, upper = max(102, 0, 63542), 102 + 0 + 63542
    assert bound['union_lower_blocks'] == lower and bound['union_upper_blocks'] == upper
    assert bound['exception_pool_lower_bytes'] == lower * 32 == 2033344
    assert bound['exception_pool_upper_bytes'] == upper * 32 == 2036608
    assert bound['exception_pool_gate_bytes'] == 2097152 and bound['upper_margin_bytes'] == 2097152 - upper * 32 == 60544
    assert bound['palette_observed_bounds'] == dict(R=[0, 240], DG=[-11, 0], DB=[-6, 0], spanDG=11, spanDB=6)
    assert derived == dict(global_minDG=-11, global_minDB=-6, global_spanDG=11, global_spanDB=6)
    assert p['encoding']['main_table_bytes'] == 16777216
    limits = dict(exception_pool_bytes_max=2097152, exception_packet8_fraction_max=.05, any_image_exception_packet8_fraction_max=.20)
    assert p['gate'] == limits and p['inputs'] == a['inputs'] and len(p['inputs']) == 6
    for record in (p, a, start, end):
        for key in ('native_calls', 'performance_calls', 'compiler_calls', 'model_calls'): assert record[key] == 0
    assert a['new_fits'] == 0 and a['palette_crosscheck'] == dict(entries=230, direct_rgb=True)
    rehashes, metadata, prior, palette_bounds = [], None, None, None
    if args.compare_originals or args.rehash_inputs:
        prior_path = args.repository / p['prior_profile']['path']
        assert file_sha(prior_path) == p['prior_profile']['sha256']
        prior = json.loads(prior_path.read_text(encoding='utf-8'))['full_domain']
        assert [sum(prior['span_histograms'][name][start:]) for name, start in [('R', 8), ('G_minus_R', 4), ('B_minus_R', 2)]] == [102, 0, 63542]
        assert all(prior['failure_reason_counts_overlapping'][name] == 0 for name in prior['failure_reasons'][:4])
    if args.rehash_inputs:
        for name, item in p['inputs'].items():
            path = args.repository / item['path']
            assert path.stat().st_size == item['bytes'] and file_sha(path) == item['sha256']
            rehashes.append(dict(name=name, **item))
        metadata = json.loads((args.repository / p['inputs']['manifest']['path']).read_text(encoding='utf-8'))['images']
        assert len(metadata) == 100
        gold = (args.repository / p['inputs']['cache_gold']['path']).read_bytes()
        palette = sorted(set(item[0] for item in struct.iter_unpack('<I', gold)))
        old_palette = [item[0] for item in struct.iter_unpack('<I', (args.repository / p['inputs']['old_palette_crosscheck']['path']).read_bytes())]
        assert len(palette) == 230 and old_palette[:230] == palette and old_palette[230:] == [0] * 26
        rr = [value & 255 for value in palette]; gg = [(value >> 8) & 255 for value in palette]; bb = [(value >> 16) & 255 for value in palette]
        dg = [g - r for r, g in zip(rr, gg)]; db = [b - r for r, b in zip(rr, bb)]
        palette_bounds = dict(R=[min(rr), max(rr)], DG=[min(dg), max(dg)], DB=[min(db), max(db)], spanDG=max(dg)-min(dg), spanDB=max(db)-min(db))
        assert palette_bounds == bound['palette_observed_bounds']
        assert derived == dict(global_minDG=min(dg), global_minDB=min(db), global_spanDG=max(dg)-min(dg), global_spanDB=max(db)-min(db))
    f, photos, rows = a['full_domain'], a['photos'], a['per_image']
    assert f['colors'] == 16777216 and f['blocks'] == 2097152
    if prior is not None: assert f['span_histograms'] == prior['span_histograms']
    reasons = ['base_R_outside_0_255', 'base_G_outside_0_255', 'base_B_outside_0_255', 'base_RGB_equals_ffffff',
               'delta_R_outside_0_7', 'delta_G_minus_R_outside_0_3', 'delta_B_minus_R_outside_0_1']
    assert f['failure_reasons'] == reasons
    rh = f['failure_reason_bitmask_histogram']; histogram(rh, 128)
    assert sum(rh) == f['blocks'] and rh[0] == f['normal_blocks'] == 2033554
    assert sum(rh[1:]) == f['exception_blocks'] == f['sentinel_count'] == 63598
    reason_counts = {name: sum(count for code, count in enumerate(rh) if code & (1 << bit)) for bit, name in enumerate(reasons)}
    assert reason_counts == f['failure_reason_counts_overlapping']
    span_ranges = {}
    for name, reason, span_limit in [('R', reasons[4], 7), ('G_minus_R', reasons[5], 3), ('B_minus_R', reasons[6], 1)]:
        values = f['span_histograms'][name]; histogram(values, 511)
        assert sum(values) == f['blocks'] and sum(values[span_limit + 1:]) == reason_counts[reason]
        span_ranges[name] = dict(minimum=min(i for i, value in enumerate(values) if value), maximum=max(i for i, value in enumerate(values) if value))
    assert reason_counts[reasons[4]] == 102 and reason_counts[reasons[5]] == 0 and reason_counts[reasons[6]] == 63542
    assert all(reason_counts[name] == 0 for name in reasons[:4])
    for key in ('decoded_pixel_differences', 'decoded_byte_differences', 'inverse_mismatches'): assert f[key] == 0
    assert f['normal_channel_carry_violations'] == [0, 0, 0]
    assert f['decoded_output_sha256'] == p['inputs']['cube']['sha256']
    assert f['main_table_bytes'] == 16777216 and f['exception_pool_bytes'] == 32 * f['exception_blocks'] == 2035136
    assert f['total_payload_bytes'] == f['main_table_bytes'] + f['exception_pool_bytes'] == 18812352
    assert f['pool_ordinals_contiguous'] is True
    assert bound['exception_pool_lower_bytes'] <= f['exception_pool_bytes'] <= bound['exception_pool_upper_bytes'] <= 2097152
    close(f['exception_block_fraction'], f['exception_blocks'] / f['blocks'])
    for key in ('main_table_sha256', 'exception_pool_sha256'): assert re.fullmatch('[0-9a-f]{64}', f[key])
    assert len(rows) == photos['images'] == 100
    combined_hist, combined_carry = [0] * 9, [0] * 3
    for index, row in enumerate(rows):
        assert row['image_index'] == index and row['pixels'] == 786432 and row['packets8'] == 98304
        if metadata is not None:
            assert row['image_id'] == metadata[index]['id'] and row['input_sha256'] == metadata[index]['evaluation']['pixel_sha256']
        hist = row['exception_pixels_per_packet8_histogram']; histogram(hist, 9)
        assert sum(hist) == row['packets8'] and sum(hist[1:]) == row['exception_packets8']
        assert sum(hits * count for hits, count in enumerate(hist)) == row['exception_pixels']
        close(row['exception_packet8_fraction'], row['exception_packets8'] / row['packets8'])
        for key in ('decoded_pixel_differences', 'decoded_byte_differences', 'inverse_mismatches'): assert row[key] == 0
        assert row['normal_channel_carry_violations'] == [0, 0, 0]
        assert re.fullmatch('[0-9a-f]{64}', row['decoded_output_sha256'])
        combined_hist = [left + right for left, right in zip(combined_hist, hist)]
        combined_carry = [left + right for left, right in zip(combined_carry, row['normal_channel_carry_violations'])]
    assert combined_hist == photos['exception_pixels_per_packet8_histogram']
    assert combined_carry == photos['normal_channel_carry_violations'] == [0, 0, 0]
    for key in ('pixels', 'packets8', 'exception_pixels', 'exception_packets8', 'decoded_pixel_differences', 'decoded_byte_differences', 'inverse_mismatches'):
        assert photos[key] == sum(row[key] for row in rows)
    assert photos['pixels'] == 78643200 and photos['packets8'] == 9830400
    close(photos['exception_packet8_fraction'], photos['exception_packets8'] / photos['packets8'])
    assert photos['decoded_output_sha256'] == p['expected_photo_output_sha256']
    worst = max(rows, key=lambda row: row['exception_packet8_fraction'])
    assert photos['worst_image_index'] == worst['image_index'] == 88
    assert photos['worst_image_id'] == worst['image_id'] == 'div2k-0885'
    close(photos['worst_image_fraction'], worst['exception_packet8_fraction'])
    over = [row['image_index'] for row in rows if row['exception_packet8_fraction'] > .20]
    assert photos['images_over_gate'] == over
    if args.rehash_inputs:
        with (args.repository / p['inputs']['photos']['path']).open('rb') as handle:
            for row in rows:
                data = handle.read(2359296)
                assert len(data) == 2359296 and digest(data) == row['input_sha256']
            assert handle.read(1) == b''
    gate = dict(full_domain_exact=all(f[key] == 0 for key in ('decoded_pixel_differences', 'decoded_byte_differences', 'inverse_mismatches')) and f['normal_channel_carry_violations'] == [0, 0, 0] and f['decoded_output_sha256'] == p['inputs']['cube']['sha256'],
        photos_exact=all(photos[key] == 0 for key in ('decoded_pixel_differences', 'decoded_byte_differences', 'inverse_mismatches')) and combined_carry == [0, 0, 0] and photos['decoded_output_sha256'] == p['expected_photo_output_sha256'],
        exception_pool_bytes=f['exception_blocks'] * 32, exception_pool_pass=f['exception_blocks'] * 32 <= limits['exception_pool_bytes_max'],
        exception_packet8_fraction=photos['exception_packets8'] / photos['packets8'], exception_packets_pass=photos['exception_packets8'] / photos['packets8'] <= .05,
        any_image_exception_packet8_fraction=worst['exception_packet8_fraction'], per_image_pass=worst['exception_packet8_fraction'] <= .20, limits=limits)
    gate['passed'] = all(gate[key] for key in ('full_domain_exact', 'photos_exact', 'exception_pool_pass', 'exception_packets_pass', 'per_image_pass'))
    assert gate == a['gate'] and gate['full_domain_exact'] and gate['photos_exact']
    assert gate['exception_pool_pass'] is True
    assert all(not gate[key] for key in ('exception_packets_pass', 'per_image_pass', 'passed'))
    report = dict(purpose=__doc__, audit_completed=True, audit_passed=True, completed_utc=datetime.datetime.now(datetime.timezone.utc).isoformat(),
        environment=dict(platform=platform.platform(), python=sys.version, executable=sys.executable, dependencies='Python标准库'),
        verifier_sha256=file_sha(__file__), manifest_sha256=digest(manifest_raw), archive_sha256=manifest['archive_sha256'],
        originals_sha256={name: digest(value) for name, value in raw.items()}, originals_byte_compared=args.compare_originals,
        input_rehashes=rehashes, per_image_input_rehashes=100 if args.rehash_inputs else 0,
        prior_profile_rehashed=prior is not None, prior_profile=p['prior_profile'], mathematical_bound=bound,
        palette_bounds_recomputed=palette_bounds, encoding_global_bounds=derived,
        verified=dict(reason_histogram_entries=128, reasons_recomputed=reason_counts, span_histograms=3, span_entries_each=511,
            span_ranges=span_ranges, full_domain_colors=16777216, full_domain_blocks=2097152, image_histograms=100,
            images_over_gate=len(over), photo_packets8=9830400, gate=gate),
        source_review=dict(scope='人工审阅冻结172行原分析并AST解析；未导入或执行其函数',
            construction='按Bcoarse分片，几何不变；header15放baseR8/DGoffset4/DBoffset3，残差3+2+1位移15+6k，bit63单独tag',
            signed_decode='DG/DB全局min由palette求得；int32恢复base及三通道，先检查<0或>255，再转byte；例外以低63bit序号直接取池',
            original_correctness='按R=0..255完整G/B笛卡尔积解码全部16M，与cube逐字节及SHA比较；100图以cube直接RGB索引比较；两者每色正逆映射及RGB三项真实进位检查'),
        limitations=['原分析完整色域/100图通过是冻结离线编码重建结果，不是候选原生完整域。',
            '本审计只重哈希输入和复算已有统计，未独立重建colorword、pool或重新编码/解码完整色域/照片。',
            '16MiB主表及异常池二进制没有归档；原件仅保存大小/SHA和连续序号布尔结果，不能独立重哈希不存在的二进制。',
            'ZIP单独复核只核对已存palette bounds与prior身份；加--rehash-inputs时才从输入palette重新推导，并从prior文件复算旧跨度尾部。',
            '逐图输出SHA只核对格式及冻结完整输出SHA，未从照片重新产生输出。',
            '没有缓存行门槛或吞吐结论，也未重评旧ID-3bit/R8失败。'],
        original_analysis_executions_added=0, runtime_implementations_added=0, native_calls=0, performance_calls=0,
        compiler_calls=0, model_calls=0, full_domain_calls=0)
    if args.output:
        with args.output.open('x', encoding='utf-8', newline='\n') as handle:
            json.dump(report, handle, ensure_ascii=False, indent=2, allow_nan=False); handle.write('\n')
    print(json.dumps(dict(audit_passed=True, original_gate_passed=False, originals=5, image_histograms=100,
        input_rehashes=len(rehashes), audit_sha256=file_sha(args.output) if args.output else None), ensure_ascii=False))

if __name__ == '__main__': main()
