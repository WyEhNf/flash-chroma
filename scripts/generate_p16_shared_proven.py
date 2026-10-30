"""97只生成隔离shared无检查候选源码；不构建、不加载DLL、不运行质量。"""
import hashlib
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT / 'experiments/p16-palette-prepare-runtime'
OUT = ROOT / 'experiments/p16-shared-proven-runtime'


def main():
    if OUT.exists():
        raise FileExistsError('97单版源码不覆盖')
    runtime = (BASE / 'channel_runtime.cpp').read_bytes()
    pixel = (BASE / 'compile_shared_avx2.cpp').read_bytes()
    assert hashlib.sha256(runtime).hexdigest() == 'c1f1727b693b95ad99014518d0ea653ae16c20b2bff995ba29092a7d0987c507'
    assert hashlib.sha256(pixel).hexdigest() == 'c353955bf92852436e9498a525ada55086b0347530d985d0806825939e1a9abc'
    nl = b'\r\n' if b'\r\n' in runtime else b'\n'

    def replace(before, after):
        nonlocal runtime
        old = before.replace('\n', nl.decode()).encode('utf-8')
        new = after.replace('\n', nl.decode()).encode('utf-8')
        assert runtime.count(old) == 1, before
        runtime = runtime.replace(old, new)

    replace('void avx2_compile_direct(',
        'void avx2_chain_domain_shared(const View*,const SuffixCacheView&,uint8_t*,size_t) noexcept;\nvoid avx2_compile_direct(')
    replace('int64_t floor_q16(int64_t x) noexcept {',
        '// 仅像素私有资格；不修改原domain_fast_enabled及构造器direct门控。\n'
        'bool shared_domain_pixel_enabled(const Handle& h) noexcept {\n'
        '  return h.domain_proven && h.views[0].shared && h.views[1].shared &&\n'
        '      h.views[2].shared && h.views[3].shared && h.direct_index.empty() && h.compiled.empty();\n'
        '}\nint64_t floor_q16(int64_t x) noexcept {')
    replace('  const bool domain_fast=domain_fast_enabled(h);',
        '  const bool domain_fast=domain_fast_enabled(h);\n  const bool shared_domain_pixel=shared_domain_pixel_enabled(h);')
    replace('        else jshc_channel::avx2_chain_cached(h.views.data(),h.cache_view,data,vectorized);',
        '        else if(shared_domain_pixel)jshc_channel::avx2_chain_domain_shared(h.views.data(),h.cache_view,data,vectorized);\n'
        '        else jshc_channel::avx2_chain_cached(h.views.data(),h.cache_view,data,vectorized);')
    replace('uint32_t jshc_cc_revision(void) {return 95;}', 'uint32_t jshc_cc_revision(void) {return 97;}')
    addition = '''
// 97沿修订16隔离结构补共享首级；原checked TU及非共享domain函数保留。
namespace jshc_channel {
void avx2_chain_domain_shared(const View* chain,const SuffixCacheView& cache,uint8_t* data,size_t pixels) noexcept {
  for(size_t p=0;p<pixels;p+=8) {
    Rgb rgb;load(data+3*p,rgb);transform<true>(chain[0],rgb);
    const __m256i dg=_mm256_sub_epi32(rgb.g,rgb.r),db=_mm256_sub_epi32(rgb.b,rgb.r);
    const __m256i index=_mm256_add_epi32(
        _mm256_mullo_epi32(_mm256_sub_epi32(rgb.r,_mm256_set1_epi32(cache.r_min)),_mm256_set1_epi32(cache.width_g*cache.width_b)),
        _mm256_add_epi32(_mm256_mullo_epi32(_mm256_sub_epi32(dg,_mm256_set1_epi32(cache.dg_min)),_mm256_set1_epi32(cache.width_b)),
            _mm256_sub_epi32(db,_mm256_set1_epi32(cache.db_min))));
    const __m256i value=gather(cache.table,index),mask=_mm256_set1_epi32(255);
    rgb.r=_mm256_and_si256(value,mask);rgb.g=_mm256_and_si256(_mm256_srli_epi32(value,8),mask);rgb.b=_mm256_srli_epi32(value,16);
    store(data+3*p,rgb);
  }
}
}
'''
    pixel += addition.replace('\n', '\r\n' if b'\r\n' in pixel else '\n').encode('utf-8')
    cmake = (BASE / 'CMakeLists.txt').read_bytes()
    assert cmake.count(b'jshc_palette_prepare') == 6
    cmake = cmake.replace(b'jshc_palette_prepare', b'jshc_shared_proven')
    comment = '# 95仅替换direct资格段的whole-cache去重及ID映射；复用94共享编译/旧回退。'.encode('utf-8')
    assert cmake.count(comment) == 1
    cmake = cmake.replace(comment, '# 97仅新增隔离shared已证域像素入口；准备/字典/旧checked对象来源保持95。'.encode('utf-8'))
    # 字典有限合同不变，仍显式引用95原文件，不复制或修改它。
    cmake = cmake.replace(b'finite_contract.cpp)', b'"${JSHC_ROOT}/experiments/p16-palette-prepare-runtime/finite_contract.cpp")')
    cmake = cmake.replace(b'target_compile_options(p16_palette_contract',
        b'target_include_directories(p16_palette_contract PRIVATE "${JSHC_ROOT}/experiments/p16-palette-prepare-runtime")\n'
        b'target_compile_options(p16_palette_contract')
    cmake += '''
# 私有核质量入口显式调用新函数，独立四项凸权重uint64真值，不新增生产C ABI。
add_executable(p16_shared_proven_contract finite_contract.cpp compile_shared_avx2.cpp
  "${JSHC_ROOT}/experiments/skylake-suffix-cache-runtime/channel_avx2.cpp")
target_include_directories(p16_shared_proven_contract PRIVATE "${BASE}")
target_compile_options(p16_shared_proven_contract PRIVATE -Wall -Wextra -mavx2 -mtune=skylake -ffp-contract=off -fstack-usage)
'''.encode('utf-8')
    OUT.mkdir()
    for name, data in (('channel_runtime.cpp', runtime), ('compile_shared_avx2.cpp', pixel), ('CMakeLists.txt', cmake),
            ('workload_hint.h', (BASE / 'workload_hint.h').read_bytes()), ('small_palette.hpp', (BASE / 'small_palette.hpp').read_bytes())):
        (OUT / name).write_bytes(data)
    print('97静态源码已生成；没有构建/模型/质量/性能调用')


if __name__ == '__main__':
    main()
