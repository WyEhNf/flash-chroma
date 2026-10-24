"""有限V2及独立日志审计通过后，另冻5完整域/5百图；待grant执行。"""
import ast
from study_memory_rom import ROOT, read, save, sha


def main():
    previous = ROOT / 'experiments/page-id16-native-pages-finite-v2.json'
    if sha(previous) != '907c17b1bf079bf700fd6e7191bf03231ac8be89a86ae3a01b5792ee3215c8a9':
        raise AssertionError('原有限V2身份不同')
    old = read(previous)
    for name, expected in old['source_sha256'].items():
        if sha(ROOT / name) != expected:
            raise AssertionError('旧源被改变')
    for name, expected in old['input_sha256'].items():
        if sha(name) != expected:
            raise AssertionError('旧输入被改变')
    output = ROOT / 'experiments/page-id16-native-pages-full-v1.json'
    if output.exists():
        raise FileExistsError('完整质量协议不能覆盖')
    audit = ROOT / 'artifacts/p16-page-native-pages-finite-v2/independent-audit-v3.json'
    if sha(audit) != 'b9d9cfe79516203cef75d9afd3feabad6ebe57709ca364c7bee531c1faf46d31' or not read(audit)['passed']:
        raise AssertionError('有限独立审计不是已复核版本')
    added = ['scripts/' + name for name in ('verify_page_id16_native_pages_full.py',
             'freeze_page_id16_native_pages_full.py', 'run_page_id16_native_pages_full.py',
             'audit_page_id16_native_pages_finite_v3.py')]
    source = dict(old['source_sha256'])
    source.update({name: sha(ROOT / name) for name in added})
    for name in source:
        if name.endswith('.py'):
            ast.parse((ROOT / name).read_text(encoding='utf-8'), filename=name)
    inputs = dict(old['input_sha256'])
    inputs.update({str(path): sha(path) for path in [previous, audit,
        ROOT / 'artifacts/p16-page-native-pages-finite-v2/run.json',
        ROOT / 'artifacts/p16-page-native-pages-finite-v2/finite/results.json',
        ROOT / 'artifacts/p16-page-native-pages-finite-v2/finite/events.jsonl',
        ROOT / 'artifacts/p16-page-native-pages-finite-v2/finite/observations.json']})
    original = read(ROOT / 'experiments/page-id16-runtime-v1.json')
    save(output, dict(purpose=__doc__, source_sha256=source, input_sha256=inputs,
        page_rom=old['page_rom'], original_rom=old['original_rom'], photos=original['photos'],
        finite_plan_sha256=sha(previous), finite_audit_sha256=sha(audit),
        expected=dict(full_modes=5, full_pixels_per_mode=1 << 24, full_calls_per_mode=64,
                      photo_modes=5, photos_per_mode=100, apply_attempts=820,
                      entry_attempts=dict(core=164, omp_c99=656, prepare=2, clear=2)),
        authorization='只静态编写后供root完整review，另grant才执行唯一质量；首失败STOP不补跑，不拟合/普查/参数扫描或自动性能/WASM。',
        resource_scope='OMP≤4 BLAS1；峰含Python/库/oracle/照片/双借用实例与日志，非prepare峰/物理RAM收益。'))
    print(dict(plan=str(output), sha256=sha(output), sources=len(source), inputs=len(inputs)), flush=True)


if __name__ == '__main__':
    main()
