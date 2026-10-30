"""99从97原字节生成隔离包装器；不修改旧源，不执行构建或质量。"""
import hashlib
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DEST = ROOT/'experiments/p16-b2-packed-runtime'
BASE = ROOT/'experiments/p16-shared-proven-runtime'
sha = lambda raw: hashlib.sha256(raw).hexdigest()
path = DEST/'channel_runtime.cpp'
if path.exists():
    raise FileExistsError('99生成源不覆盖')
raw = (BASE/'channel_runtime.cpp').read_bytes()
assert sha(raw) == '5cef4041462ef5354b8fde11a50c32dac5efb5d58eb2114a964bad83da39e199'
text = raw.decode('utf-8')
changes = [
    ('#include "small_palette.hpp"', '#include "small_palette.hpp"\n#include "b2_plan.hpp"'),
    ('namespace jshc_channel {\r\nvoid avx2_chain_domain_shared', 'namespace jshc_channel {\r\nvoid avx2_chain_domain_b2(const uint32_t*,const uint32_t*,const SuffixCacheView&,uint8_t*,size_t) noexcept;\r\nvoid avx2_chain_domain_shared'),
    ('  std::vector<jshc::SparseLut> models;', '  p16_b2::Tables b2_tables; // 独立64B对齐owner，空时只增加一个指针。\n  std::vector<jshc::SparseLut> models;'),
    ('return 97;', 'return 99;'),
    ('        else if(shared_domain_pixel)', '        else if(!h.b2_tables.empty())jshc_channel::avx2_chain_domain_b2(h.b2_tables.axes(),h.b2_tables.nodes(),h.cache_view,data,vectorized);\n        else if(shared_domain_pixel)'),
    ('    if(h->direct_index.empty())prepare_palette(*h);', '    if(h->direct_index.empty())prepare_palette(*h);\n    // 全部旧prepare先完成；只有97私有资格+m33才申请新表，失败不发布。\n    if((jshc_cc_capabilities()&2) && shared_domain_pixel_enabled(*h) && h->models[0].m==33) {\n      try {h->b2_tables.prepare(h->views[0]);}catch(const std::bad_alloc&) {}\n    }'),
    ('+h.direct_index.bytes();\r\n  return bytes;', '+h.direct_index.bytes()+h.b2_tables.bytes();\r\n  return bytes;')]
for old, new in changes:
    assert text.count(old) == 1, old
    text = text.replace(old, new)
path.write_bytes(text.encode('utf-8'))
for name, expected in [('compile_shared_avx2.cpp','85602f2aa5439d07bce33348d328f0ee70a1a9a02cd866aaf49b1157236b0d01'),
        ('small_palette.hpp',None),('workload_hint.h',None)]:
    raw=(BASE/name).read_bytes()
    if expected is not None:assert sha(raw)==expected
    assert not (DEST/name).exists();(DEST/name).write_bytes(raw)
cmake=(BASE/'CMakeLists.txt').read_bytes()
assert sha(cmake)=='67ea8c3421299d6cfa5eb02c2079af9c6694366067761b4ff490a3e3d917811f'
text=cmake.decode('utf-8').split('# 独立有限合同')[0]
text=text.replace('jshc_shared_proven','jshc_b2_packed').replace('channel_runtime.cpp compile_shared_avx2.cpp','channel_runtime.cpp compile_shared_avx2.cpp b2_shared_avx2.cpp')
text=text.replace('set_source_files_properties(compile_shared_avx2.cpp','set_source_files_properties(compile_shared_avx2.cpp b2_shared_avx2.cpp')
text+='\ntarget_compile_features(jshc_b2_packed PRIVATE cxx_std_17)\n'
assert not (DEST/'CMakeLists.txt').exists();(DEST/'CMakeLists.txt').write_bytes(text.encode('utf-8'))
print('99生产源静态生成完成；未构建、未加载、未计时。')
