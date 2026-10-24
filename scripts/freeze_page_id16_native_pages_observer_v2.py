"""冻结机械误判后的独立观察器；唯一核心不重编，模型API仍禁止。"""
import ast
from page_id16_native_pages_build_common import ROOT, PLAN, checked_plan, save, sha


def main():
    original = checked_plan()
    if sha(PLAN) != '65838f3968302872b8fbd7dfb734cb3d8ca7a1cd2410f02c9885a8e5bb41a997':
        raise AssertionError('原构建协议不同')
    output = ROOT / 'experiments/page-id16-native-pages-observer-v2.json'
    if output.exists():
        raise FileExistsError('独立观察器协议不能覆盖')
    names = ['scripts/finalize_page_id16_native_pages_observer_v2.py',
             'scripts/freeze_page_id16_native_pages_observer_v2.py']
    for name in names:
        ast.parse((ROOT / name).read_text(encoding='utf-8'), filename=name)
    source = dict(original['source_sha256'])
    source.update({name: sha(ROOT / name) for name in names})
    before = ROOT / 'artifacts/p16-page-native-pages-v1/build'
    inputs = dict(original['input_sha256'])
    inputs.update({str(path): sha(path) for path in [PLAN, *[before / name for name in
                   ('page_native_pages.o', 'page_native_pages.su', 'apply-assembly.txt',
                    'all-assembly.txt', 'machine-code-gate.json', 'commands.json')]]})
    if inputs[str(before / 'page_native_pages.o')] != 'ac60efa6170af82cf9d285697f3b2a82123a32a908be8e29a4e680d0aedbb6bd':
        raise AssertionError('唯一Clang对象不是复核版本')
    if inputs[str(before / 'apply-assembly.txt')] != '4a780e1cfa496b69555e432b28f776c4cab3cbdea548eb149df49e144475d99d':
        raise AssertionError('原apply汇编不同')
    save(output, dict(purpose=__doc__, source_sha256=source, input_sha256=inputs,
        original_plan_sha256=sha(PLAN),
        authorization='root已独立review原实码与观察器：只复用ac60efa唯一对象，首次OMP胶水/链接和4layout metadata；不重编核心、不改C、不覆盖原false gate。',
        stop='首身份/观察器/编译/链接/布局错误保存STOP，不补跑；prepare/apply/validate/clear/有限/full/photos/性能/WASM均未授权。'))
    print(dict(plan=str(output), sha256=sha(output), sources=len(source), inputs=len(inputs)), flush=True)


if __name__ == '__main__':
    main()
