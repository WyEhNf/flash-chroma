"""一次集中合同：首级分通道/后三共享四级热路径及混合共享fallback，独立u64真值。"""
from __future__ import annotations
import argparse
import itertools
import json
from pathlib import Path
import sys
import zipfile

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT/'python')); sys.path.insert(0, str(ROOT/'experiments/channel-runtime'))
import numpy as np
from lutlab import channel_coordinates as cc, io, study_provenance
from channel_native import Library, digest
from native_provenance import verify_dependencies
from verify_channel_coordinates import integer_oracle


def read(path): return json.loads(Path(path).read_text(encoding='utf-8'))


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--plan', type=Path, default=ROOT/'experiments/channel-runtime-specialized-v1.json')
    parser.add_argument('--library', type=Path, required=True)
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args(); plan = read(args.plan); out = args.output.resolve()
    if out.exists(): raise ValueError('不覆盖一次集中合同')
    if any(digest(ROOT/n) != h for n, h in plan['source_sha256'].items()): raise ValueError('冻结源码不同')
    build = read(args.library.parent/'build.json')
    if build['plan_sha256'] != digest(args.plan) or build['source_sha256'] != plan['source_sha256']:
        raise ValueError('新构建没有绑定本轮冻结计划')
    lib = Library(args.library, build['files']['jshc_channel_specialized.dll'])
    if lib.capabilities != 7 or lib.revision != 2: raise ValueError('本轮要求ABI1/revision2及标量/AVX2/OpenMP')
    dependencies = verify_dependencies(args.library, build, loaded=True)
    inherited = plan['build_inputs']['inherited_abi_contract']
    if digest(ROOT/inherited['path']) != inherited['sha256'] or not read(ROOT/inherited['path'])['pass']:
        raise ValueError('既有ABI异常合同来源不同')
    rng = np.random.default_rng(plan['contract']['seed']); paths = []; ordinary = []; extended = []; sides = []
    out.mkdir(parents=True)
    for stage, m in enumerate(plan['contract']['mixed_m']):
        nodes = rng.integers(0, 256, (m, m, m, 3), np.uint8)
        nodes[0, 0, 0] = 0; nodes[-1, -1, -1] = 255
        sparse = io.SparseLut(io.uniform_grid(m), nodes)
        path = out/f'model{stage}.slut'; io.save_sparse(path, sparse); paths.append(path)
        sparse = io.load_sparse(path, competition=True)
        ordinary.append(cc.from_sparse(sparse)); altered = cc.from_sparse(sparse)
        # 每单元用不同幂函数单调重分配，制造真正不同的三输出几何；冻结0/65536端点。
        for channel in range(3):
            for axis in range(3):
                exponent = .5+.25*((channel*3+axis)%7)
                fractions = np.floor(io.ONE*np.power(altered.channel_frac[channel, axis]/float(io.ONE), exponent)+.5).astype(np.uint32)
                fractions[[0, 255]] = [0, io.ONE]
                altered.channel_frac[channel, axis] = fractions
        cc.validate(altered)
        if np.array_equal(altered.channel_frac[0], altered.channel_frac[1]): raise AssertionError('没有分通道几何')
        side = out/f'fraction{stage}.bin'; altered.channel_frac.astype('<u4').tofile(side)
        sides.append(side); extended.append(altered)
    equal_side = out/'equal-fractions0.bin'; ordinary[0].channel_frac.astype('<u4').tofile(equal_side)
    cases = [
        ('specialized_4_unshared_shared_shared_shared', [sides[0], None, None, None], [extended[0], *ordinary[1:]], paths),
        ('fallback_4_shared_unshared_shared_unshared', [None, sides[1], None, sides[3]], [ordinary[0], extended[1], ordinary[2], extended[3]], paths),
        ('fallback_4_equal_sidecar_all_shared', [equal_side, None, None, None], ordinary, paths),
        ('fallback_3_unshared_shared_shared', [sides[0], None, None], [extended[0], *ordinary[1:3]], paths[:3])]
    anchors = np.array(list(itertools.product([0, 255], repeat=3))+list(itertools.product([1, 254], repeat=3)), np.uint8)
    records = []
    for label, fractions, models, model_paths in cases:
        with lib.chain(model_paths, fractions) as chain:
            for length in plan['contract']['lengths']:
                source = rng.integers(0, 256, (length, 3), np.uint8)
                source[:min(length, len(anchors))] = anchors[:min(length, len(anchors))]
                expected = source.copy()
                for model in models: expected = integer_oracle(model, expected)
                for kernel, threads in [('scalar', 1), ('avx2', 1), ('avx2', 4)]:
                    for offset in plan['contract']['byte_offsets']:
                        storage = np.full(length*3+offset+17, 0xa7, np.uint8)
                        view = storage[offset:offset+length*3].reshape(length, 3); view[:] = source
                        chain.apply(view, kernel=kernel, threads=threads)
                        np.testing.assert_array_equal(view, expected)
                        if np.any(storage[:offset] != 0xa7) or np.any(storage[offset+length*3:] != 0xa7):
                            raise AssertionError('24字节读写或非对齐尾部覆盖哨兵')
                records.append({'path': label, 'stages': len(model_paths), 'mixed_m': [m.m for m in models],
                    'pixels': length, 'backend_threads': [['scalar', 1], ['avx2', 1], ['avx2', 4]],
                    'byte_offsets': plan['contract']['byte_offsets'], 'integer_oracle_mismatches': 0,
                    'sentinel_mismatches': 0, 'model_accounting_bytes': chain.model_bytes})
    names = [*plan['source_sha256'], args.plan.resolve().relative_to(ROOT).as_posix()]
    sources = {name: digest(ROOT/name) for name in names}
    if any(digest(ROOT/n) != h for n, h in plan['source_sha256'].items()): raise ValueError('合同期间冻结源码变化')
    with zipfile.ZipFile(out/'measured-source.zip', 'w', zipfile.ZIP_DEFLATED) as archive:
        for name in sources: archive.write(ROOT/name, name)
    result = {'pass': True, 'purpose': __doc__, 'environment': study_provenance.environment_fingerprint(),
        'library_sha256': lib.sha256, 'abi': 1, 'revision': lib.revision, 'capabilities': lib.capabilities,
        'build_sha256': digest(args.library.parent/'build.json'), 'plan_sha256': digest(args.plan),
        'source_sha256': sources, 'loaded_dependency_sources': dependencies, 'seed': plan['contract']['seed'],
        'cases': records, 'inherited_abi_exception_contract': inherited,
        'scope': '一次有限合成正确性合同。没有运行新完整域、百图、测速或拟合；ABI输入/异常路径来自原封标量壳及既有集中合同，不冒称本次重测。'}
    (out/'results.json').write_text(json.dumps(result, ensure_ascii=False, indent=2, allow_nan=False)+'\n', encoding='utf-8')
    print(json.dumps({'pass': True, 'cases': len(records), 'library_sha256': lib.sha256}, ensure_ascii=False))


if __name__ == '__main__': main()
