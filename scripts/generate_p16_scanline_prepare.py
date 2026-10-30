"""100静态生成：克隆97私有包装器，保留八个旧核来源，不执行构建。"""
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def main():
    source = ROOT/'experiments/p16-shared-proven-runtime'
    target = ROOT/'experiments/p16-scanline-prepare-runtime'
    target.mkdir(exist_ok=False)
    runtime = (source/'channel_runtime.cpp').read_bytes()
    assert runtime.count(b'avx2_compile_direct(') == 2
    assert runtime.count(b'return 97;') == 1
    runtime = runtime.replace(b'avx2_compile_direct(', b'avx2_compile_direct_scanline(').replace(b'return 97;', b'return 100;')
    (target/'channel_runtime.cpp').write_bytes(runtime)
    for name in ('compile_shared_avx2.cpp', 'small_palette.hpp', 'workload_hint.h'):
        (target/name).write_bytes((source/name).read_bytes())
    (target/'compile_scanline_avx2.cpp').write_bytes((ROOT/'experiments/p16-scanline-prepare-draft/compile_scanline_avx2.cpp').read_bytes())
    (target/'finite_contract.cpp').write_bytes((ROOT/'experiments/p16-scanline-prepare-draft/finite_contract.cpp').read_bytes())
    cmake = (source/'CMakeLists.txt').read_text(encoding='utf-8')
    cmake = cmake[:cmake.index('# 独立有限合同')]
    cmake = cmake.replace('jshc_shared_proven', 'jshc_scanline_prepare')
    cmake = cmake.replace('# 97仅新增隔离shared已证域像素入口；准备/字典/旧checked对象来源保持95。',
        '# 100仅新增固定B批扫描线准备器；原97八对象和公开apply路径保持。')
    cmake = cmake.replace('channel_runtime.cpp compile_shared_avx2.cpp', 'channel_runtime.cpp compile_shared_avx2.cpp compile_scanline_avx2.cpp')
    cmake = cmake.replace('set_source_files_properties(compile_shared_avx2.cpp', 'set_source_files_properties(compile_shared_avx2.cpp compile_scanline_avx2.cpp')
    cmake += '''\n# 私有有限合同包含原97入口和新扫描线入口，不链接模型核心。\nadd_executable(p16_scanline_contract finite_contract.cpp compile_shared_avx2.cpp compile_scanline_avx2.cpp)\ntarget_include_directories(p16_scanline_contract PRIVATE "${BASE}" "${JSHC_ROOT}/experiments/channel-runtime")\ntarget_compile_options(p16_scanline_contract PRIVATE -Wall -Wextra -mavx2 -mtune=skylake -ffp-contract=off -fstack-usage)\n'''
    (target/'CMakeLists.txt').write_text(cmake, encoding='utf-8', newline='\n')


if __name__ == '__main__':
    main()
