"""只读实际导出表，以独立乘法位地址逐16M项核重编号及RGB，不加载native。"""
from __future__ import annotations
from collections import Counter
import hashlib
import json
from pathlib import Path
import struct

ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT / 'artifacts/p16-direct-active-packed-v2'


def sha(path):
    with Path(path).open('rb') as stream:
        return hashlib.file_digest(stream, 'sha256').hexdigest()


def main():
    output = BASE / 'independent.json'
    if output.exists():
        raise FileExistsError('不覆盖独立实际颜色/位表审计')
    frozen = json.loads((BASE / 'frozen.json').read_text(encoding='utf-8'))
    result = json.loads((BASE / 'results.json').read_text(encoding='utf-8'))
    assert sha(BASE / 'frozen.json') == 'ba77cb94813346b1906f696c30637933be7b62d738221331d725af34142268d4'
    assert result['passed'] and result['frozen_sha256'] == sha(BASE / 'frozen.json')
    for name, expected in frozen['source_sha256'].items():
        assert sha(ROOT / name) == expected, name
    for name, expected in frozen['inputs_sha256'].items():
        assert sha(name) == expected, name
    for name, expected in result['artifacts'].items():
        assert (BASE / name).stat().st_size == expected['bytes'] and sha(BASE / name) == expected['sha256']
    ids = (BASE / 'physical-ids-u16-with-guard.bin').read_bytes()
    packed = (BASE / 'packed-ids-with-guard.bin').read_bytes()
    old = [row[0] for row in struct.iter_unpack('<I', (BASE / 'whole-palette-u32.bin').read_bytes())]
    colors = [row[0] for row in struct.iter_unpack('<I', (BASE / 'active-palette-u32.bin').read_bytes())]
    n, bits = 1 << 24, result['packed_bits']
    assert len(ids) == n * 2 + 4 and ids[-4:] == bytes(4)
    assert len(packed) == n * bits // 8 + 4 and packed[-4:] == bytes(4)
    assert len(old) == 613 and old == sorted(set(old))
    selected = result['active_old_palette_ids']
    assert len(selected) == result['active_colors'] == len(colors) == 344
    assert selected == sorted(set(selected)) and colors == [old[i] for i in selected]
    rank = {old_id: new_id for new_id, old_id in enumerate(selected)}
    counts = Counter()
    decoded_count = 0
    for code, (old_id,) in enumerate(struct.iter_unpack('<H', memoryview(ids)[:-4])):
        bit = code * bits
        address, shift = divmod(bit, 8)
        word = packed[address] | (packed[address + 1] << 8)
        compact_id = (word >> shift) & ((1 << bits) - 1)
        assert compact_id == rank[old_id] and colors[compact_id] == old[old_id], code
        counts[old_id] += 1
        decoded_count += 1
    assert decoded_count == n and [counts[i] for i in range(len(old))] == result['whole_id_frequencies']
    assert set(counts) == set(selected) and sum(counts.values()) == n
    assert bits == (9 if len(colors) <= 512 else 10) == 9
    assert result['candidate_table_and_palette_bytes'] == len(packed) + 4 * len(colors) == 18875748
    assert result['native_prepare_calls'] == 1 and result['native_apply_calls'] == result['performance_samples'] == 0
    finite = json.loads((BASE / 'finite.json').read_text(encoding='utf-8'))
    assert finite['passed'] and finite['cases_count'] == len(finite['cases']) == 344
    value = dict(passed=True, script_sha256=sha(Path(__file__)), frozen_sha256=sha(BASE / 'frozen.json'),
        results_sha256=sha(BASE / 'results.json'), independently_decoded_entries=decoded_count,
        active_colors=len(colors), bits=bits, packed_and_palette_bytes=len(packed) + 4 * len(colors),
        checked_sources=len(frozen['source_sha256']), checked_inputs=len(frozen['inputs_sha256']),
        native_calls=0, performance_samples=0,
        scope='标准库逐项使用code*bits/divmod位址，不复用生产位址/向量pack函数，完整核oldID→activeID→精确RGB与频数；仅离线位表，非native packed速度、prepare峰或可移植实机。')
    output.write_text(json.dumps(value, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    print(value, flush=True)


if __name__ == '__main__':
    main()
