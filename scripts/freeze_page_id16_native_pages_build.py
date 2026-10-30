"""构建前冻结唯一页指针候选与完整质量计数；本次只允许构建/布局元数据。"""
import ast
from pathlib import Path
from study_memory_rom import ROOT, read, save, sha


def main():
    output = ROOT / 'experiments/page-id16-native-pages-build-v1.json'
    if output.exists():
        raise FileExistsError('不能覆盖native-pages唯一协议')
    original = ROOT / 'experiments/page-id16-copy4-runtime-v1.json'
    if sha(original) != '9f6b8f226e8ea0bfc1609dae694e8f5b699666d05ba57e1829ed72d2af7919be':
        raise AssertionError('copy4原协议身份不同')
    old = read(original)
    if any(sha(ROOT / name) != expected for name, expected in old['source_sha256'].items()):
        raise AssertionError('旧P4/copy4冻结源改变')
    added = [
        'experiments/page-id16-native-pages-design-v1.md',
        'experiments/page-id16-native-pages-quality-v1.md',
        *['experiments/page-id16-native-pages-runtime/' + name for name in
          ('page_native_pages.h', 'page_native_pages.c', 'page_native_pages_parallel.cpp')],
        *['scripts/' + name for name in ('page_id16_native_pages_build_common.py',
           'freeze_page_id16_native_pages_build.py', 'build_page_id16_native_pages.py')],
    ]
    names = list(old['source_sha256']) + added
    for name in names:
        if name.endswith('.py'):
            ast.parse((ROOT / name).read_text(encoding='utf-8'), filename=name)
    inputs = dict(old['input_sha256'])
    inputs[str(original)] = sha(original)
    old_core = Path(old['old_objects']['core'])
    if sha(old_core) != '4c6b215a054708a6803628bbfa9ea419a262b9447a18ddec658be53b45260216':
        raise AssertionError('旧prepare/validate对象不是封存版本')
    value = dict(
        purpose=__doc__, source_sha256={name: sha(ROOT / name) for name in names},
        input_sha256=inputs, page_rom=old['page_rom'], photos=old['photos'],
        original_copy4_plan_sha256=sha(original), toolchain=old['toolchain'],
        old_core=str(old_core), dependencies=old['dependencies'],
        expected_quality=dict(full_modes=5, photo_modes=5, photos_per_mode=100,
            finite=534, io_rejections=243, format_prepare_rejections=42,
            other_prepare_rejections=64, failure_state_replays=53,
            lifecycle_scenarios=4, clear_rejections=8, image_guards=108,
            rom_guards=20, pointer_table_guards=20, unaligned_rom=40,
            fixture_pointer_equalities=16384),
        build_authorization='只唯一-j1 generic x64 Clang构建、可选GCC OMP胶水与4个sizeof/对齐/表长元数据函数；禁止prepare/apply/clear/validate、有限/完整域/照片/计时/WASM。',
        quality_authorization='预期计数和入口冻结；质量验证器执行源码后续另冻，需root复核机器码后另grant有限native，完整域/照片仍不自动执行。',
        immutable='旧ROM/40B ABI/全部原源与对象不改，不重导出/普查/alias；新视图按值base+caller4096页指针，失败保留原state。',
    )
    save(output, value)
    print(dict(plan=str(output), sha256=sha(output), sources=len(names),
               inputs=len(inputs), expected_quality=value['expected_quality']), flush=True)


if __name__ == '__main__':
    main()
