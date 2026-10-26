"""封存292 RGB24、固定G分bank负例及293/294新域资格；不重跑native或性能。"""
import ast
import hashlib
import json
from pathlib import Path
import zipfile
from archive_direct_sentinel import pack, sha, read, write

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / 'report/data/p16-direct-cache2-20261024'


def stage_paths():
    names = ['scripts/' + n for n in [
        'generate_direct_rgb24.py', 'build_direct_rgb24.py', 'check_direct_rgb24_contracts.py',
        'prepare_direct_rgb24_quality.py', 'check_direct_rgb24_native.py', 'check_direct_rgb24_full_mt.py',
        'census_direct_gbank8.py', 'observe_gbank8_max41.py', 'audit_direct_gbank8_partial.py',
        'generate_direct_cache2.py', 'build_direct_cache2.py', 'observe_direct_cache2.py',
        'check_direct_cache2_contracts.py', 'prepare_direct_cache2_cmake_v2.py',
        'build_direct_cache2_cmake_v2.py', 'observe_direct_cache2_cmake_v2.py',
        'check_direct_cache2_contracts_cmake_v2.py', 'check_direct_cache2_quality.py',
        'audit_direct_cache2_quality.py', 'prepare_direct_cache2_audit_v2.py',
        'audit_direct_cache2_quality_v2.py', 'archive_direct_cache2.py', 'audit_direct_cache2_git.py']]
    names += ['experiments/' + n for n in ['p16-direct-rgb24-plan-v1.md', 'p16-direct-gbank8-plan-v1.md',
        'p16-direct-cache2-plan-v1.md', 'p16-direct-cache2-performance-draft-v1.md',
        'p16-minimax-literature-20261024.md']]
    names += ['docs/stages/2026-10-24-p16-direct-cache2.md']
    for folder in ['p16-direct-rgb24-runtime', 'p16-direct-u16-cache2-runtime',
                   'p16-direct-rgb24-cache2-runtime', 'p16-direct-rgb24-cache2-v2-runtime']:
        names += [p.relative_to(ROOT).as_posix() for p in (ROOT / 'experiments' / folder).iterdir() if p.is_file()]
    assert len(names) == len(set(names))
    return sorted(names)


def main():
    if OUT.exists():
        raise FileExistsError('不覆盖292/293/294归档')
    artifacts = ROOT / 'artifacts'
    q_path = artifacts / 'p16-direct-cache2-quality-v1/results.json'
    q = read(q_path)
    a_path = artifacts / 'p16-direct-cache2-quality-v1/independent-check-v2.json'
    a = read(a_path)
    assert q['passed'] and a['passed'] and a['results_sha256'] == sha(q_path)
    assert q['full_stream_count'] == 24 and len(q['photos']) == 800 and len(q['whole4t_streams']) == 8
    assert q['short_pattern_backend_cases'] == 972 and len(q['read_only_team_snapshots']) == 16
    original = read(artifacts / 'p16-direct-rgb24-quality-v1/results.json')
    original_mt = read(artifacts / 'p16-direct-rgb24-full-mt-v1/results.json')
    assert original['passed'] and len(original['full_matrix']) == 30 and len(original['photo_matrix']) == 800
    assert original_mt['passed'] and len(original_mt['outputs']) == 10
    census = read(artifacts / 'p16-direct-gbank8-partial-audit-v1.json')
    assert census['passed'] and [r['maximum_colors'] for r in census['models_completed']] == [294, 338, 299]
    assert read(artifacts / 'p16-direct-rgb24-cache2-build-v1/configure-receipt.json')['returncode'] == 1
    assert not (artifacts / 'p16-direct-rgb24-cache2-build-v1/build-check.json').exists()
    frozen_path = artifacts / 'p16-direct-cache2-quality-frozen-v1/frozen.json'
    frozen = read(frozen_path)
    assert a['frozen_sha256'] == sha(frozen_path)
    sources = {}
    for name, expected in frozen['sources_sha256'].items():
        assert sha(ROOT / name) == expected, name
        sources[name] = ROOT / name
    for name, expected in frozen['inputs_sha256'].items():
        assert sha(name) == expected, name
    for name in stage_paths() + ['scripts/archive_direct_sentinel.py']:
        sources[name] = ROOT / name
    for name, path in sources.items():
        if path.suffix == '.py':
            ast.parse(path.read_text(encoding='utf-8-sig'), filename=name)
    prefixes = ['p16-direct-rgb24-', 'p16-direct-u16-cache2-', 'p16-direct-cache2-quality-',
                'p16-direct-gbank8-']
    raw = {}
    for directory in artifacts.iterdir():
        if directory.is_dir() and any(directory.name.startswith(p) for p in prefixes):
            for path in directory.rglob('*'):
                if path.is_file():
                    raw[directory.name + '/' + path.relative_to(directory).as_posix()] = path
        elif directory.is_file() and any(directory.name.startswith(p) for p in prefixes):
            raw[directory.name] = directory
    assert 'p16-direct-gbank8-census-driver-v1.log' in raw
    assert 'p16-direct-gbank8-partial-audit-v1.json' in raw
    assert 'p16-direct-cache2-quality-audit-v2/protocol.json' in raw
    model_members = {}
    specs = dict(read(artifacts / 'p16-direct-rgb24-quality-frozen-v1/frozen.json')['roles'])
    specs['max41'] = frozen['models']['max41']
    for role, spec in specs.items():
        for index, path in enumerate(spec['models']):
            model_members[f'{role}/stage{index+1}.slut'] = Path(path)
        for index, path in enumerate(spec['sidecars']):
            if path:
                model_members[f'{role}/stage{index+1}-sidecar.bin'] = Path(path)
    OUT.mkdir(parents=True)
    hashes = {name: pack(OUT / name, members) for name, members in
              [('source.zip', sources), ('raw.zip', raw), ('models.zip', model_members)]}
    write(OUT / 'quality-independent.json', a)
    write(OUT / 'gbank-partial-audit.json', census)
    result = {'passed': True, 'purpose': __doc__, 'source_members': len(sources), 'raw_members': len(raw),
        'model_members': len(model_members), 'source_sha256': {n: sha(p) for n, p in sources.items()},
        'zip_members_sha256': hashes, 'old_rgb24_full_streams': 40, 'old_rgb24_photo_comparisons': 800,
        'new_cache2_full_streams': 24, 'new_cache2_photo_comparisons': 800,
        'new_cache2_short_cases': 972, 'new_cache2_capacity': q['capacity'],
        'performance_calls': 0, 'native_reruns_during_archive': 0,
        'known_gaps': ['尚无293/294正式性能、fresh RSS、bad_alloc或无AVX2注入',
            '294首次CMake文件名生成失败保留，机械v2仅改三处源文件名，全部C++原字节',
            '离线audit首次to12标签KeyError未保存本地stdout，单列工具输出来源；v2不重跑native',
            'Gbank前三模型不可表示，第四max41旧288前置失败，不计为其bank基数结论',
            '官方阈值/派生表许可/指定Intel性能及未见照片泛化仍未验证']}
    write(OUT / 'independent-check.json', result)
    write(OUT / 'manifest.json', {'files': {p.name: sha(p) for p in OUT.iterdir()},
        'scope': '质量/容量及负例封存，尚无新正式速度资格，不能把预算差8312B称总内存增量'})
    whitelist = stage_paths() + [p.relative_to(ROOT).as_posix() for p in OUT.iterdir()]
    write(OUT / 'git-whitelist.json', {'paths': sorted(whitelist + [str((OUT / 'git-whitelist.json').relative_to(ROOT)).replace('\\', '/')])})
    print(json.dumps({'passed': True, 'source_members': len(sources), 'raw_members': len(raw),
                      'model_members': len(model_members), 'stage_paths': len(whitelist)+1}, ensure_ascii=False))


if __name__ == '__main__':
    main()
