"""定向验证域证书成立但精确调色板超过255项时，修订22退回16；不计时或搜索种子。"""
import argparse
from pathlib import Path
import numpy as np
from skylake_support import build_libraries, claim, digest, save, unchanged
from palette_support import info as palette_info
from domain_cache_support import info as domain_info
from suffix_cache_support import cache_info
from lutlab import channel_coordinates as cc, io
from verify_channel_coordinates import integer_oracle


def main():
    p = argparse.ArgumentParser(description=__doc__)
    for name in ('plan', 'build', 'output'):
        p.add_argument('--'+name, type=Path, required=True)
    args = p.parse_args()
    plan, build, libraries, loaded = build_libraries(args.plan, args.build)
    out, identity = claim(args.output, args.plan,
        [*plan['source_sha256'], 'scripts/verify_skylake_palette_fallback.py',
         'scripts/palette_support.py', 'scripts/domain_cache_support.py',
         'scripts/suffix_cache_support.py', 'scripts/verify_channel_coordinates.py'],
        {'purpose': __doc__, 'build_sha256': digest(args.build/'build.json'),
         'loaded_libraries': loaded, 'seed': 2026102024, 'm': 17,
         'coordinate_delta_q16': 1, 'random_pixels': 4097, 'byte_offsets': [0, 1, 3],
         'backends': [['scalar', 1], ['avx2', 1], ['avx2', 4]]})
    rng = np.random.default_rng(2026102024)
    grey = rng.integers(0, 256, (17, 17, 17), np.uint8)
    first = out/'first.slut'
    io.save_sparse(first, io.SparseLut(io.uniform_grid(17), np.repeat(grey[..., None], 3, axis=3)))
    model = cc.from_sparse(io.load_sparse(first, competition=True))
    f = model.channel_frac[1]
    mask = (f > 0) & (f < 65536)
    f[mask] += 1
    cc.validate(model)
    side = out/'first.bin'; model.channel_frac.astype('<u4').tofile(side)
    grid = io.uniform_grid(17)
    axes = np.meshgrid(grid[0], grid[1], grid[2], indexing='ij')
    suffix = out/'identity.slut'
    io.save_sparse(suffix, io.SparseLut(grid, np.stack(axes, axis=-1).astype(np.uint8)))
    suffix_model = cc.from_sparse(io.load_sparse(suffix, competition=True))
    source = np.concatenate([rng.integers(0, 256, (4097, 3), np.uint8),
        np.array([[r, g, b] for r in (0, 255) for g in (0, 255) for b in (0, 255)], np.uint8)])
    truth = integer_oracle(model, source)
    for _ in range(3):
        truth = integer_oracle(suffix_model, truth)
    records = {}; comparisons = 0
    for role, library in libraries.items():
        with library.chain([first, suffix, suffix, suffix], [side, None, None, None]) as handle:
            records[role] = {'model_bytes': handle.model_bytes, 'domain': domain_info(handle),
                             'cache': cache_info(handle), 'palette': palette_info(handle)}
            assert records[role]['domain']['fast_path_enabled'] == 1
            if role == 'candidate':
                state = records[role]['palette']
                assert state['reason'] == 2 and state['palette_size'] > 255
                assert state['enabled'] == state['table_capacity_bytes'] == state['blocks'] == 0
            for backend, threads in (('scalar', 1), ('avx2', 1), ('avx2', 4)):
                for offset in (0, 1, 3):
                    guard = np.full(source.nbytes+offset+17, 0xa7, np.uint8)
                    actual = guard[offset:offset+source.nbytes].reshape(-1, 3); actual[:] = source
                    handle.apply(actual, kernel=backend, threads=threads)
                    np.testing.assert_array_equal(actual, truth)
                    assert np.all(guard[:offset] == 0xa7) and np.all(guard[offset+source.nbytes:] == 0xa7)
                    comparisons += 1
    assert records['candidate']['model_bytes']-records['reference']['model_bytes'] == 1104
    unchanged(identity)
    save(out/'results.json', {'pass': True, 'purpose': __doc__, 'records': records,
        'plan_sha256': digest(args.plan), 'build_sha256': digest(args.build/'build.json'),
        'libraries': build['libraries'], 'pixels_per_comparison': len(source), 'comparisons': comparisons,
        'byte_mismatches': 0, 'sentinel_mismatches': 0, 'performance_calls': 0,
        'allocation_failure_injected': False, 'scope': '一个固定构造的有限补验；不代替实际模型完整色域验收'})
    print('大调色板拒绝分支通过：', comparisons, '比较；每组', len(source), '像素')


if __name__ == '__main__':
    main()
