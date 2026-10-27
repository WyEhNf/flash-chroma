"""从可搬移CPU包重放固定模型完整RGB8摘要；验证后端与打包，非重新拟合评分。"""
import argparse
import ctypes as ct
import hashlib
from pathlib import Path

import numpy as np

import p16_submission as submission
import p16_unified_support as native


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--package', type=Path, required=True)
    parser.add_argument('--library', type=Path, required=True)
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    if args.output.exists():
        raise FileExistsError('验证回执已存在，拒绝覆盖')
    manifest, profiles, identity = submission.load_package(args.package)
    native.setup()
    library = native.Library(args.library)
    if library.revision != 102 or library.capabilities & 8:
        raise ValueError('发行验证要求修订102且未编入AVX512的CPU库')
    backend = 'avx2' if library.supported('avx2') else 'scalar'
    rows = []
    for name, profile in profiles.items():
        expected = manifest['profiles'][name].get('oracle_sha256')
        if not expected:
            raise ValueError('完整域验证需要固定的独立预测流SHA：' + name)
        with library.create(profile) as chain:
            # 短尾对独立标量路径，固定每个模型，一次只读一个输入缓冲。
            rng = np.random.default_rng(20261027)
            for count in (0, 1, 15, 16, 17, 65537):
                source = rng.integers(0, 256, (count, 3), np.uint8)
                truth, actual = np.empty_like(source), np.empty_like(source)
                chain.apply(source, truth, 'scalar', 1)
                chain.apply(source, actual, backend, 4)
                if not np.array_equal(truth, actual):
                    raise ValueError('短尾或标量回退不同：' + name)
            # 当前构建没有AVX512对象，即使CPU支持也应明确拒绝且不写。
            error = ct.create_string_buffer(1024)
            target = (ct.c_uint8 * 48)(*([0xa5] * 48))
            before = bytes(target)
            code = library.dll.jshc_cc_apply(chain.handle, target, 48, 2, 1, error, len(error))
            if code != 1 or bytes(target) != before:
                raise ValueError('未编入后端未明确拒绝')
            digest = hashlib.sha256()
            for begin in range(0, 1 << 24, 65536):
                codes = np.arange(begin, begin + 65536, dtype=np.uint32)
                source = np.column_stack((codes >> 16, (codes >> 8) & 255, codes & 255)).astype(np.uint8)
                target = np.empty_like(source)
                chain.apply(source, target, backend, 4)
                digest.update(memoryview(target).cast('B'))
            if digest.hexdigest() != expected:
                raise ValueError('完整RGB8输出摘要不同：' + name)
            rows.append({'profile': name, 'colors': 1 << 24, 'sha256': digest.hexdigest(),
                'backend': backend, 'threads': 4, 'finite_cases': 6, 'unsupported_rejections': 1,
                'state': native.diagnostics(chain)})
    args.output.parent.mkdir(parents=True, exist_ok=True)
    native.save(args.output, {'passed': True, 'package': identity, 'library': library.record(),
        'environment': native.environment(), 'profiles': rows,
        'scope': '固定稀疏模型完整预测流身份、CPU后端和精确打包；不是原始密集LUT色差或目标机速度。'})
    print('CPU交付包完整RGB8通过：', len(rows), '个profile；后端', backend)


if __name__ == '__main__':
    main()
