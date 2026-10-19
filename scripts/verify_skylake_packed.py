"""Skylake候选的一次集中整数合同：真实混合几何、Q16边界、尾部与非对齐，不测性能。"""
from __future__ import annotations
import argparse
import itertools
from pathlib import Path
import sys
import numpy as np
from skylake_support import ROOT, build_libraries, claim, digest, save, unchanged
from lutlab import channel_coordinates as cc, io
from verify_channel_coordinates import integer_oracle


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--plan', type=Path, required=True)
    parser.add_argument('--build', type=Path, required=True)
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    plan, build, libraries, loaded = build_libraries(args.plan, args.build)
    out, identity = claim(args.output, args.plan,
        [*plan['source_sha256'], 'scripts/verify_skylake_packed.py', 'scripts/verify_channel_coordinates.py',
         'python/lutlab/channel_coordinates.py', 'python/lutlab/io.py'],
        {'purpose': __doc__, 'build_sha256': digest(args.build/'build.json'), 'loaded_libraries': loaded})
    rng = np.random.default_rng(plan['contract']['seed'])
    edges = np.array([[0, 1, 32767, 32768, 32769, 65535, 65536],
                      [0, 1, 2, 32767, 32768, 65535, 65536],
                      [0, 32767, 32768, 32769, 65534, 65535, 65536]], np.uint32)
    ordinary = []; extended = []; paths = []; sides = []
    for stage, m in enumerate(plan['contract']['mixed_m']):
        sparse = io.SparseLut(io.uniform_grid(m), rng.integers(0, 256, (m, m, m, 3), np.uint8))
        p = out/f'model{stage}.slut'; io.save_sparse(p, sparse)
        sparse = io.load_sparse(p, competition=True); paths.append(p)
        base = cc.from_sparse(sparse); altered = cc.from_sparse(sparse)
        for a in range(3):
            for cell in np.unique(altered.idx[a]):
                codes = np.flatnonzero(altered.idx[a] == cell)
                select = np.minimum(np.arange(len(codes))*7//len(codes), 6)
                for c in range(3):
                    altered.channel_frac[c, a, codes] = edges[(c+a)%3, select]
        altered.channel_frac[:, :, 0] = 0; altered.channel_frac[:, :, 255] = io.ONE
        cc.validate(altered)
        side = out/f'fractions{stage}.bin'; altered.channel_frac.astype('<u4').tofile(side)
        ordinary.append(base); extended.append(altered); sides.append(side)
    equal = cc.from_sparse(io.load_sparse(paths[0], competition=True))
    equal.channel_frac[:] = extended[0].channel_frac[0]
    cc.validate(equal)
    assert not np.array_equal(equal.channel_frac, ordinary[0].channel_frac)
    equal_side = out/'equal-but-changed.bin'; equal.channel_frac.astype('<u4').tofile(equal_side)
    cases = [
        ('unshared_shared_shared_shared', paths, [sides[0], None, None, None], [extended[0], *ordinary[1:]]),
        ('shared_unshared_shared_unshared', paths, [None, sides[1], None, sides[3]], [ordinary[0], extended[1], ordinary[2], extended[3]]),
        ('equal_sidecar_different_base', paths, [equal_side, None, None, None], [equal, *ordinary[1:]]),
        ('single_unshared', paths[:1], sides[:1], extended[:1]),
        ('three_unshared', paths[:3], sides[:3], extended[:3])]
    anchors = np.array(list(itertools.product([0, 255], repeat=3)), np.uint8)
    all_codes = np.column_stack([np.roll(np.arange(256), k) for k in range(3)]).astype(np.uint8)
    records = []
    for label, model_paths, fractions, models in cases:
        handles = {name: lib.chain(model_paths, fractions) for name, lib in libraries.items()}
        try:
            for length in plan['contract']['lengths']:
                source = rng.integers(0, 256, (length, 3), np.uint8)
                probes = np.concatenate([anchors, all_codes])
                source[:min(length, len(probes))] = probes[:min(length, len(probes))]
                truth = source.copy()
                for model in models:
                    truth = integer_oracle(model, truth)
                for name, handle in handles.items():
                    for kernel, threads in plan['contract']['backend_threads']:
                        for offset in plan['contract']['byte_offsets']:
                            storage = np.full(offset+3*length+17, 0xa7, np.uint8)
                            actual = storage[offset:offset+3*length].reshape(length, 3); actual[:] = source
                            handle.apply(actual, kernel=kernel, threads=threads)
                            np.testing.assert_array_equal(actual, truth)
                            if np.any(storage[:offset] != 0xa7) or np.any(storage[offset+3*length:] != 0xa7):
                                raise AssertionError('非对齐/末向量/尾部写越界')
                records.append({'layout': label, 'pixels': length, 'byte_mismatches': 0, 'sentinel_mismatches': 0,
                    'model_bytes': {name: h.model_bytes for name, h in handles.items()}})
        finally:
            for handle in handles.values():
                handle.close()
    negative = []
    invalid = extended[0].channel_frac.copy(); invalid[0, 0, 128] = 65537
    bad = out/'invalid-17bit.bin'; invalid.astype('<u4').tofile(bad)
    short = out/'truncated.bin'; short.write_bytes(b'\x00'*9215)
    unordered = extended[0].channel_frac.copy(); unordered[0, 0, 0] = 1
    endpoint = out/'invalid-endpoint.bin'; unordered.astype('<u4').tofile(endpoint)
    for name, lib in libraries.items():
        for p in (bad, short, endpoint):
            try:
                with lib.chain(paths[:1], [p]):
                    raise AssertionError('非法侧表被接受')
            except RuntimeError as error:
                negative.append({'library': name, 'fixture': p.name, 'rejected': True, 'reason': str(error)})
    unchanged(identity)
    result = {'pass': True, 'purpose': __doc__, 'build_sha256': digest(args.build/'build.json'),
        'plan_sha256': digest(args.plan), 'libraries': build['libraries'], 'cases': records, 'negative_inputs': negative,
        'unique_layout_length_cases': len(records), 'integer_oracle_mismatches': 0, 'sentinel_mismatches': 0,
        'performance_calls': 0, 'new_fits': 0,
        'scope': '有限合成合同，不冒称完整域、百图、Skylake实机或性能通过。'}
    save(out/'results.json', result)
    print('集中整数合同通过：', len(records), '组；非法侧表拒绝：', len(negative), flush=True)


if __name__ == '__main__':
    main()
