"""单头文件完整RGB8身份、C99 sidecar及部署约束验证；不做性能评分。"""
from __future__ import annotations
import argparse
import hashlib
from pathlib import Path
import numpy as np
import flash_chroma_support as support


def verify(library, model, config, expected):
    rng = np.random.default_rng(20261027)
    finite = 0
    with library.create(model, config) as engine:
        for count in (0, 1, 7, 8, 15, 16, 17, 65, 257, 65537):
            source = rng.integers(0, 256, (count, 3), dtype=np.uint8)
            truth, target = np.empty_like(source), np.empty_like(source)
            if library.c_apply(model, source, truth):
                raise AssertionError('独立C99映射失败')
            engine.apply(source, target)
            np.testing.assert_array_equal(target, truth)
            engine.apply(source, source)
            np.testing.assert_array_equal(source, truth)
            finite += 2
        stream, c_stream = hashlib.sha256(), hashlib.sha256()
        for begin in range(0, 1 << 24, 65536):
            values = np.arange(begin, begin+65536, dtype=np.uint32)
            source = np.column_stack((values >> 16, (values >> 8) & 255, values & 255)).astype(np.uint8)
            target = np.empty_like(source)
            engine.apply(source, target)
            stream.update(memoryview(target))
            # 标量零arena的C++分支与独立C99包分别遍历全域。
            if config['backend'] == 'scalar' and config['representation'] == 'sparse':
                if library.c_apply(model, source, target):
                    raise AssertionError('C99完整域映射失败')
                c_stream.update(memoryview(target))
        actual = stream.hexdigest()
        if expected and actual != expected:
            raise AssertionError('完整RGB8输出不一致：' + str(config))
        if config['backend'] == 'scalar' and config['representation'] == 'sparse' and c_stream.hexdigest() != actual:
            raise AssertionError('独立C99包与C++包全域不同')
        return {'config': config, 'resources': engine.info, 'full_rgb8_sha256': actual,
                'expected_sha256': expected, 'colors': 1 << 24, 'finite_comparisons': finite,
                'independent_c99_full_rgb8': config['backend'] == 'scalar' and config['representation'] == 'sparse'}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--library', type=Path, required=True)
    parser.add_argument('--manifest', type=Path, default=support.ROOT/'data/p16-score-models/manifest.json')
    parser.add_argument('--profiles', nargs='+')
    parser.add_argument('--output', type=Path, required=True)
    parser.add_argument('--all-representations', action='store_true')
    args = parser.parse_args()
    if args.output.exists():
        raise FileExistsError('拒绝覆盖已有验证回执')
    value, models = support.load_models(args.manifest, args.profiles)
    library = support.Library(args.library)
    rows = []
    for name, model in models.items():
        configs = [support.configuration(backend='scalar', target='portable')]
        if library.capabilities & 2:
            configs.append(support.configuration(backend='avx2', threads=4))
        representation = 'direct_u8' if name == 'default' else 'direct_u16'
        configs.append(support.configuration(representation, threads=4,
            backend='avx2' if library.capabilities & 2 else 'scalar'))
        if args.all_representations:
            configs.append(support.configuration('direct_rgb24', backend='auto', threads=4))
        for config in configs:
            row = verify(library, model, config, model.profile.get('oracle_sha256'))
            row['profile'] = name
            rows.append(row)
            print('完整RGB8通过', name, config['representation'], config['backend'], flush=True)
    support.write_json(args.output, {'passed': True, 'library': library.record(),
        'manifest': {'path': str(args.manifest.resolve()), 'sha256': support.digest(args.manifest)},
        'environment': support.native.environment(), 'records': rows,
        'scope': '固定四级模型的全色域输出身份、C99 sidecar、标量/SIMD及资源报告；非官方色差或目标机性能。'})


if __name__ == '__main__':
    main()
