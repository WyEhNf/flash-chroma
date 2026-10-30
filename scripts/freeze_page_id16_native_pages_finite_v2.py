"""另冻V2唯一自重叠修正和追加观察；旧V1/核心/预期计数不变。"""
import ast
from study_memory_rom import ROOT, read, save, sha


def main():
    original_path = ROOT / 'experiments/page-id16-native-pages-finite-v1.json'
    if sha(original_path) != '42767efa39f1e4dbb409cd747ad7948cdaaa54dc3651754a2af85d07915454a7':
        raise AssertionError('原finite V1身份不同')
    old = read(original_path)
    for name, expected in old['source_sha256'].items():
        if sha(ROOT / name) != expected:
            raise AssertionError('原四脚本/源被改变：' + name)
    for name, expected in old['input_sha256'].items():
        if sha(name) != expected:
            raise AssertionError('原输入不同：' + name)
    output = ROOT / 'experiments/page-id16-native-pages-finite-v2.json'
    if output.exists():
        raise FileExistsError('V2协议不能覆盖')
    added = ['scripts/' + name for name in ('verify_page_id16_native_pages_finite_v2.py',
             'run_page_id16_native_pages_finite_v2.py', 'freeze_page_id16_native_pages_finite_v2.py')]
    source = dict(old['source_sha256'])
    source.update({name: sha(ROOT / name) for name in added})
    for name in source:
        if name.endswith('.py'):
            ast.parse((ROOT / name).read_text(encoding='utf-8'), filename=name)
    inputs = dict(old['input_sha256'])
    before = ROOT / 'artifacts/p16-page-native-pages-finite-v1'
    inputs.update({str(path): sha(path) for path in
                   [original_path, before / 'run.json', before / 'stdout.txt', before / 'stderr.txt']})
    local_imports = dict(old['actual_local_imports'])
    local_imports.update({
        'scripts/verify_page_id16_native_pages_finite_v2.py': ['scripts/page_id16_native_pages_common.py', 'scripts/verify_page_id16.py'],
        'scripts/run_page_id16_native_pages_finite_v2.py': ['scripts/study_memory_rom.py'],
        'scripts/freeze_page_id16_native_pages_finite_v2.py': ['scripts/study_memory_rom.py'],
    })
    save(output, dict(purpose=__doc__, source_sha256=source, input_sha256=inputs,
        original_finite_plan_sha256=sha(original_path), expected_counts=old['expected_counts'],
        page_rom=old['page_rom'], original_rom=old['original_rom'], actual_local_imports=local_imports,
        change='只将6路径slots-view指向新bad自身，并代理原入口逐native尝试前/返回及逐receipt追加flush JSONL，finally累计/入口/快照。未改C/旧对象/ROM/DLL/原四脚本/计数。',
        authorization='源码供root逐字review后明确grant一次；首错STOP保留，不自动full/photos/perf/WASM。native硬fault可能不执行finally，已flush尝试不等于返回成功。'))
    print(dict(plan=str(output), sha256=sha(output), sources=len(source), inputs=len(inputs),
               expected_counts=old['expected_counts']), flush=True)


if __name__ == '__main__':
    main()
