"""固定B=2的纯节点地址stencil普查；不映射16M颜色，不加载原生库。"""
import argparse
import hashlib
import itertools
import json
from pathlib import Path
import struct
import numpy as np


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def tiled(coordinates, tiles):
    r, g, b = np.moveaxis(coordinates, -1, 0)
    return (((r//2)*tiles + g//2)*tiles + b//2)*8 + (r%2)*4 + (g%2)*2 + b%2


def touched(offsets, base, unit):
    # 每个uint32的四个字节都计入；对非4B对齐假设也不遗漏跨线字节。
    starts = (offsets + base)//unit
    ends = (offsets + base + 3)//unit
    assert np.all(starts[:, 1:] >= ends[:, :-1])
    return (ends-starts).sum(axis=1) + 1 + (starts[:, 1:] > ends[:, :-1]).sum(axis=1)


def page_totals(offsets, unit):
    # 对全部base mod4096精确累计。每4B范围跨页是长度3的环区间；
    # 相邻字范围间是否新开一页也是一个环区间，避免4096次全数组扫描。
    delta = np.zeros(unit + 1, np.int64)
    delta[0] = len(offsets)

    def add_intervals(starts, lengths):
        starts = np.asarray(starts, np.int64).reshape(-1)
        lengths = np.broadcast_to(lengths, starts.shape)
        ends = starts + lengths
        delta[:] += np.bincount(starts, minlength=unit + 1)
        delta[:] -= np.bincount(np.minimum(ends, unit), minlength=unit + 1)
        wrapped = ends > unit
        delta[0] += int(wrapped.sum())
        delta[:] -= np.bincount(ends[wrapped]-unit, minlength=unit + 1)

    add_intervals((unit-(offsets % unit)-3) % unit, 3)
    previous_end = offsets[:, :-1]+3
    gap = offsets[:, 1:]-previous_end
    always = gap >= unit
    delta[0] += int(always.sum());delta[unit] -= int(always.sum())
    partial = ~always
    add_intervals((unit-gap[partial]-(previous_end[partial] % unit)) % unit, gap[partial])
    values = np.cumsum(delta)[:-1]
    for base in (0, 1, 63, 64, 2047, 4095):
        assert int(values[base]) == int(touched(offsets, base, unit).sum())
    return values


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--plan', required=True, type=Path)
    p.add_argument('--output', required=True, type=Path)
    a = p.parse_args()
    plan = json.loads(a.plan.read_text(encoding='utf-8'))
    assert sha(Path(__file__)) == plan['script_sha256'] and plan['block_side'] == 2
    if a.output.exists():
        raise FileExistsError('固定B2地址普查不覆盖')
    a.output.mkdir(parents=True)
    results = []
    for spec in plan['models']:
        path = Path(spec['path']);assert sha(path) == spec['sha256']
        raw = path.read_bytes();magic, version, m, reserved = struct.unpack('<4sIII', raw[:16])
        assert magic == b'SLUT' and version == 1 and reserved == 0 and m == spec['m']
        assert len(raw) == 16+12*m+768+3072+3*m**3
        rgb = np.frombuffer(raw, np.uint8, 3*m**3, 16+12*m+768+3072).reshape(-1, 3).astype(np.uint32)
        words = rgb[:, 0] | (rgb[:, 1]<<8) | (rgb[:, 2]<<16)
        tiles = (m+1)//2
        coordinates = np.stack(np.indices((m, m, m), dtype=np.int64), axis=-1).reshape(-1, 3)
        address = tiled(coordinates, tiles)
        assert len(np.unique(address)) == m**3
        payload = np.full(tiles**3*8, 0xdeadbeef, np.uint32)
        payload[address] = words
        assert np.array_equal(payload[address], words)
        labels = np.full_like(payload, 0xffffffff);labels[address] = np.arange(m**3, dtype=np.uint32)
        assert np.array_equal(labels[address], np.arange(m**3, dtype=np.uint32))
        valid = np.zeros(len(payload), bool);valid[address] = True
        assert np.all(payload[~valid] == 0xdeadbeef)
        lower = np.stack(np.indices((m-1, m-1, m-1), dtype=np.int64), axis=-1).reshape(-1, 3)
        old, new = [], []
        for order in itertools.permutations(range(3)):
            vertices = [lower.copy()]
            current = lower.copy()
            for axis in order:
                current = current.copy();current[:, axis] += 1;vertices.append(current)
            vertices = np.stack(vertices, axis=1)
            r, g, b = np.moveaxis(vertices, -1, 0)
            linear = (r*m+g)*m+b
            blocked = tiled(vertices, tiles)
            assert np.array_equal(payload[blocked], words[linear])
            assert np.array_equal(labels[blocked], linear.astype(np.uint32))
            old.append(linear*4);new.append(blocked*4)
        old, new = np.concatenate(old), np.concatenate(new)
        assert np.all(np.diff(old, axis=1)>0) and np.all(np.diff(new, axis=1)>0)
        pages_old, pages_new = page_totals(old, 4096), page_totals(new, 4096)
        line_rows = []
        for base in range(64):
            x, y = touched(old, base, 64), touched(new, base, 64)
            px, py = pages_old[base::64], pages_new[base::64]
            line_rows.append({'base_mod64': base, 'uint32_aligned': base%4 == 0,
                'old_total_line_touches': int(x.sum()), 'new_total_line_touches': int(y.sum()),
                'old_mean': float(x.mean()), 'new_mean': float(y.mean()),
                'old_per_stencil_min_max': [int(x.min()), int(x.max())], 'new_per_stencil_min_max': [int(y.min()), int(y.max())],
                'paired_improved': int((y<x).sum()), 'paired_equal': int((y==x).sum()), 'paired_regressed': int((y>x).sum()),
                'old_page_touches_min_max_given_mod64': [int(px.min()), int(px.max())],
                'new_page_touches_min_max_given_mod64': [int(py.min()), int(py.max())],
                'paired_page_total_ratio_min_max_given_mod64': [float((py/px).min()), float((py/px).max())]})
        result = {'model': spec, 'm': m, 'stencils': len(old), 'all_nodes_restored_uint32': True,
            'all_stencil_nodes_and_unique_labels_restored': True, 'odd_padding_slots': int((~valid).sum()),
            'padding_sentinel_unchanged': True, 'old_node_payload_bytes': int(words.nbytes), 'new_node_payload_bytes': int(payload.nbytes),
            'old_payload_align64_roundup': (int(words.nbytes)+63)//64*64, 'new_payload_align64_roundup': (int(payload.nbytes)+63)//64*64,
            'all_base_mod64': line_rows, 'genuinely_align64_case': line_rows[0],
            'all_page_base_mod4096': {'old_total_touches': pages_old.tolist(), 'new_total_touches': pages_new.tolist(),
                'same_base_new_old_ratio_min_max': [float((pages_new/pages_old).min()), float((pages_new/pages_old).max())]},
            'scope': '全部cell×6合法tetra路径，无fraction分布权重，不是16M颜色或照片概率；所有0..63含非4对齐界，实际4对齐子集另标。64对齐仍有64种page相位，不等于4096对齐；逻辑payload/roundup不是实际owner/RSS。'}
        results.append(result)
        print(json.dumps({'m':m,'stencils':len(old),'align64_old_new_mean':[line_rows[0]['old_mean'],line_rows[0]['new_mean']],
            'all_page_same_base_ratio_min_max':result['all_page_base_mod4096']['same_base_new_old_ratio_min_max'],
            'payload_old_new':[words.nbytes,payload.nbytes]}, ensure_ascii=False), flush=True)
    (a.output/'results.json').write_text(json.dumps({'block_side':2,'models':results,'scope':plan['scope']},ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    (a.output/'executed-plan.json').write_bytes(a.plan.read_bytes())


if __name__ == '__main__':
    main()
