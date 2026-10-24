"""另冻有限执行源与原计数；执行前仍需root明确grant。"""
import ast
from page_id16_native_pages_build_common import ROOT, PLAN, checked_plan, read, save, sha


def main():
    original = checked_plan()
    observer_path = ROOT / 'experiments/page-id16-native-pages-observer-v2.json'
    observer = read(observer_path)
    if sha(observer_path) != 'ae1dbf8d0e5e110f31653704f49456a12f36478b405385b2e83106f9a0195cca':
        raise AssertionError('独立恢复协议不同')
    for name, expected in observer['source_sha256'].items():
        if sha(ROOT / name) != expected:
            raise AssertionError('原冻结源不同')
    for name, expected in observer['input_sha256'].items():
        if sha(name) != expected:
            raise AssertionError('原冻结输入不同')
    output = ROOT / 'experiments/page-id16-native-pages-finite-v1.json'
    if output.exists():
        raise FileExistsError('有限协议不能覆盖')
    added = ['scripts/' + name for name in ('page_id16_native_pages_common.py',
             'verify_page_id16_native_pages_finite.py', 'freeze_page_id16_native_pages_finite.py',
             'run_page_id16_native_pages_finite.py')]
    source = dict(observer['source_sha256'])
    source.update({name: sha(ROOT / name) for name in added})
    # 显式列实际有限入口的本仓桥接，不依赖旧闭包恰好已包含它们。
    local_imports = {
        'scripts/page_id16_native_pages_common.py': ['scripts/page_id16_common.py', 'scripts/study_memory_rom.py'],
        'scripts/verify_page_id16_native_pages_finite.py': ['scripts/page_id16_native_pages_common.py', 'scripts/verify_page_id16.py'],
        'scripts/freeze_page_id16_native_pages_finite.py': ['scripts/page_id16_native_pages_build_common.py'],
        'scripts/run_page_id16_native_pages_finite.py': ['scripts/study_memory_rom.py'],
        'scripts/page_id16_native_pages_build_common.py': ['scripts/study_memory_rom.py'],
        'scripts/page_id16_common.py': ['scripts/win_readonly_rom.py', 'scripts/study_memory_rom.py'],
        'scripts/verify_page_id16.py': ['scripts/page_id16_common.py'],
        'scripts/win_readonly_rom.py': ['scripts/study_memory_rom.py', 'scripts/bench_memory_rom.py'],
        'scripts/bench_memory_rom.py': ['scripts/study_memory_rom.py'],
        'scripts/study_memory_rom.py': [],
    }
    for name in set(local_imports) | {item for items in local_imports.values() for item in items}:
        actual = sha(ROOT / name)
        if name in source and source[name] != actual:
            raise AssertionError('实际桥接源与原闭包不同：' + name)
        source[name] = actual
    for name in source:
        if name.endswith('.py'):
            ast.parse((ROOT / name).read_text(encoding='utf-8'), filename=name)
    build = ROOT / 'artifacts/p16-page-native-pages-observer-v2/build'
    inputs = dict(observer['input_sha256'])
    inputs[str(observer_path)] = sha(observer_path)
    for path in [build / 'build.json', build / 'observer-machine-code-gate.json',
                 *[path for path in build.iterdir() if path.suffix in ('.dll', '.o', '.su')]]:
        inputs[str(path)] = sha(path)
    if inputs[str(build / 'jshc_page_native_pages.dll')] != 'b326a9f3cc6dfa933964b65bf345bf15887d56c62904ad569554b42cf2e93ced' or inputs[str(build / 'jshc_page_native_pages_c99.dll')] != '11860791a48ea49e85c32e1e8277bf7b5ad98fbae3ffc58c5102bbf9da9a80bf':
        raise AssertionError('实际DLL不是复核版本')
    excluded = {'full_modes', 'photo_modes', 'photos_per_mode'}
    expected_counts = {name: count for name, count in original['expected_quality'].items() if name not in excluded}
    old = read(ROOT / 'experiments/page-id16-runtime-v1.json')
    save(output, dict(purpose=__doc__, source_sha256=source, input_sha256=inputs,
        page_rom=original['page_rom'], original_rom=old['original_rom'],
        original_build_plan_sha256=sha(PLAN), observer_plan_sha256=sha(observer_path),
        expected_counts=expected_counts, estimated_peak_bytes=200 * (1 << 20),
        actual_local_imports=local_imports,
        entry_scope='core_out与OMP C99 1/4×in/out为5路径，finite/图像guard加core_in共6；只新符号，旧AVX不作缓存覆盖。',
        authorization='只有root逐字review后grant才运行唯一finite；首失败保存STOP，不修后重采，不自动full/photos/perf/WASM。'))
    print(dict(plan=str(output), sha256=sha(output), sources=len(source), inputs=len(inputs),
               expected_counts=expected_counts), flush=True)


if __name__ == '__main__':
    main()
