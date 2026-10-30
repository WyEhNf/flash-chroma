"""由冻结288的四种实际像素核产生独立290源；只生成，不构建或计时。"""
from __future__ import annotations
import hashlib
import json
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
BASE=ROOT/'experiments/p16-direct-u16-ilp-runtime'
OUT=ROOT/'experiments/p16-direct-sentinel-runtime'

def replace_once(text: str, old: str, new: str) -> str:
    if text.count(old)!=1:
        raise ValueError(f'唯一文本匹配失败：{old[:100]}')
    return text.replace(old,new,1)

def replace_function(text: str, prefix: str, new: str) -> str:
    begin=text.index(prefix)
    brace=text.index('{',begin)
    depth=1
    end=brace+1
    while depth:
        depth+=(text[end]=='{')-(text[end]=='}')
        end+=1
    return text[:begin]+new+text[end:]

READ='''inline __attribute__((always_inline)) __m256i read(const DirectSentinelView& context,const uint8_t* table,const uint32_t* palette,const uint8_t* p) {
  uint64_t a,b,c;std::memcpy(&a,p,8);std::memcpy(&b,p+8,8);std::memcpy(&c,p+16,8);
  const uint32_t i0=table[uint32_t(a&0xffffff)],i1=table[uint32_t((a>>24)&0xffffff)];
  const uint32_t i2=table[uint32_t(((a>>48)|(b<<16))&0xffffff)],i3=table[uint32_t((b>>8)&0xffffff)];
  const uint32_t i4=table[uint32_t((b>>32)&0xffffff)],i5=table[uint32_t(((b>>56)|(c<<8))&0xffffff)];
  const uint32_t i6=table[uint32_t((c>>16)&0xffffff)],i7=table[uint32_t(c>>40)];
  if(sentinel_any(i0,i1,i2,i3,i4,i5,i6,i7))return sentinel_slow_eight(context,p);
  return _mm256_setr_epi32(int32_t(palette[i0]),int32_t(palette[i1]),int32_t(palette[i2]),int32_t(palette[i3]),int32_t(palette[i4]),int32_t(palette[i5]),int32_t(palette[i6]),int32_t(palette[i7]));
}'''

def kernel(text: str) -> str:
    text=text.replace('// 精确全域uint16索引：四包独立读取先行，按RGB24读取合法对齐词。','// 精确热palette与255哨兵：每8lane检查，miss复用原cache整数链。')
    text=text.replace('#include "direct_u16.hpp"','#include "sentinel_read_avx2.hpp"')
    text=text.replace('direct_u16','direct_sentinel').replace('const uint16_t*','const uint8_t*')
    text=text.replace('const uint8_t* table,const uint32_t* palette,','const DirectSentinelView& context,const uint8_t* table,const uint32_t* palette,')
    text=text.replace('(table,palette,','(context,table,palette,')
    text=replace_function(text,'inline __attribute__((always_inline)) __m256i read(',READ)
    needle='  const __m128i hi=_mm_setr_epi32(int32_t(palette[i4]),int32_t(palette[i5]),'
    text=replace_once(text,needle,'  if(sentinel_any(i0,i1,i2,i3,i4,i5,i6,i7))return sentinel_slow_eight(context,p);\n'+needle)
    text=replace_function(text,'inline __attribute__((always_inline)) void scalar_one(','''inline __attribute__((always_inline)) void scalar_one(const DirectSentinelView& context,const uint8_t* table,const uint32_t* palette,const uint8_t* source,uint8_t* destination) {
  sentinel_scalar_one(context,table,palette,source,destination);
}''')
    return text

PREPARE='''void prepare_direct_sentinel(Handle& h) {
  auto& info=h.direct_sentinel_info;
  info={};info.version=1;info.format=17;info.id_bytes=1;info.guard_bytes=4;info.guaranteed_alignment=1;info.reason=2;
  if(!h.direct_index.empty()){info.reason=1;info.whole_cache_colors=h.palette_info.palette_size;return;}
  if(!domain_fast_enabled(h) || !(jshc_cc_capabilities()&2))return;
  const auto start=std::chrono::steady_clock::now();
  try {
    auto selection=jshc_channel::select_sentinel_palette(h.cache);
    info.whole_cache_colors=uint32_t(selection.distinct);
    info.temporary_peak_bytes=selection.temporary_peak_bytes+sizeof(selection);
    if(!selection.eligible){info.reason=selection.distinct<=255?1:3;info.prepare_seconds=std::chrono::duration<double>(std::chrono::steady_clock::now()-start).count();return;}
    std::vector<uint8_t> table((size_t{1}<<24)+4,0);
    std::vector<uint32_t> palette(selection.palette.begin(),selection.palette.end());
#if defined(_OPENMP)
    const int build_workers=omp_in_parallel()?1:4;
#pragma omp parallel for schedule(static) num_threads(build_workers)
#endif
    for(long long block=0;block<256;++block) {
      const size_t begin=size_t(block)*65536;
      jshc_channel::avx2_compile_direct(h.views.data(),h.cache_view,selection.ids.data(),table.data()+begin,begin,65536);
    }
    // 容量峰值含本选择对象；完整栈帧和已存在模型/cache另由.su与model_bytes报告。
    info.temporary_peak_bytes=std::max(info.temporary_peak_bytes,selection.ids.capacity()*sizeof(uint32_t)+table.capacity()+palette.capacity()*sizeof(uint32_t)+sizeof(selection));
    h.palette_sentinel.swap(palette);h.direct_sentinel.swap(table);
    info.enabled=1;info.reason=0;info.palette_size=256;info.input_entries=size_t{1}<<24;info.raw_words=h.direct_sentinel.size()/4;
    info.table_capacity_bytes=h.direct_sentinel.capacity();info.palette_capacity_bytes=h.palette_sentinel.capacity()*sizeof(uint32_t);
    info.data_mod_64=uint64_t(reinterpret_cast<uintptr_t>(h.direct_sentinel.data())&63);
  }catch(const std::bad_alloc&){info.reason=4;}
  info.prepare_seconds=std::chrono::duration<double>(std::chrono::steady_clock::now()-start).count();
}'''

def runtime(text: str) -> str:
    text=text.replace('#include "direct_u16.hpp"','#include "direct_sentinel.hpp"\n#include "sentinel_prepare.hpp"')
    text=text.replace('direct_u16','direct_sentinel').replace('palette_u16','palette_sentinel').replace('copy_u16_palette','copy_sentinel_palette')
    text=text.replace('std::vector<uint16_t>','std::vector<uint8_t>').replace('sizeof(uint16_t)','sizeof(uint8_t)')
    text=text.replace('h.direct_sentinel.size()/2','h.direct_sentinel.size()/4')
    text=text.replace('"16bit直接表诊断ABI固定为96字节"','"哨兵直接表诊断ABI固定为96字节"')
    text=replace_function(text,'void scalar_direct_sentinel(','''void scalar_direct_sentinel(const Handle& h,const uint8_t* source,uint8_t* target,size_t pixels) noexcept {
  const jshc_channel::DirectSentinelView context{h.views.data(),h.cache_view};
  for(size_t p=0;p<pixels;++p)jshc_channel::sentinel_scalar_one(context,h.direct_sentinel.data(),h.palette_sentinel.data(),source+3*p,target+3*p);
}''')
    text=text.replace('jshc_channel::avx2_direct_sentinel(h.direct_sentinel.data(),','jshc_channel::avx2_direct_sentinel(jshc_channel::DirectSentinelView{h.views.data(),h.cache_view},h.direct_sentinel.data(),')
    text=replace_function(text,'void prepare_direct_sentinel(',PREPARE)
    text=replace_once(text,'return 288; // 从冻结87派生的精确16bit直接ID研究，不修改旧87库。','return 290; // 精确top255哨兵研究，保留原87普通u8优先路线。')
    text=replace_once(text,'*output={1,1,16,0,h.direct_sentinel.size()/4,','*output={1,1,17,0,h.direct_sentinel.size()/4,')
    text=replace_once(text,'return h.andn_normal_supported && !h.direct_index.empty()?1u:0u;','return h.andn_normal_supported && (!h.direct_index.empty() || !h.direct_sentinel.empty())?1u:0u;')
    return text

def dispatch(text: str) -> str:
    text=text.replace('// 288仅替换apply核；表/prepare/vector与287相同，输入地址仍R低/G中/B高。','// 290保留四种原像素布局，哨兵回退上下文显式传入。')
    text=text.replace('direct_u16','direct_sentinel').replace('const uint16_t*','const uint8_t*')
    text=text.replace('(const uint8_t*,const uint32_t*,','(const DirectSentinelView&,const uint8_t*,const uint32_t*,')
    text=text.replace('(const uint8_t* ids,','(const DirectSentinelView& context,const uint8_t* ids,')
    text=text.replace('(ids,palette,','(context,ids,palette,')
    return text

def main() -> None:
    sources={name:(BASE/name).read_bytes() for name in ('channel_runtime.cpp','compile_avx2.cpp','direct_u16_avx2.cpp','linear.cpp','andn_inplace.cpp','andn_outplace.cpp','normal_inplace.cpp','CMakeLists.txt')}
    products={name:kernel(sources[name].decode('utf-8')) for name in ('linear.cpp','andn_inplace.cpp','andn_outplace.cpp','normal_inplace.cpp')}
    products['channel_runtime.cpp']=runtime(sources['channel_runtime.cpp'].decode('utf-8'))
    products['direct_sentinel_avx2.cpp']=dispatch(sources['direct_u16_avx2.cpp'].decode('utf-8'))
    compiler=sources['compile_avx2.cpp'].decode('utf-8')
    begin=compiler.index('bool avx2_compile_direct_u16(')
    compiler=compiler[:begin]+'}\n'
    products['compile_avx2.cpp']=compiler
    cmake=sources['CMakeLists.txt'].decode('utf-8')
    begin=cmake.index('add_executable(p16_direct_u16_ilp_contracts')
    end=cmake.index('set_source_files_properties(',begin)
    cmake=cmake[:begin]+cmake[end:]
    cmake=cmake.replace('direct_u16_ilp','direct_sentinel').replace('direct_u16_avx2.cpp','direct_sentinel_avx2.cpp')
    cmake+='''
add_executable(p16_direct_sentinel_contracts contracts.cpp compile_avx2.cpp direct_sentinel_avx2.cpp linear.cpp andn_inplace.cpp andn_outplace.cpp normal_inplace.cpp
  "${JSHC_ROOT}/experiments/skylake-suffix-cache-runtime/channel_avx2.cpp")
target_include_directories(p16_direct_sentinel_contracts PRIVATE "${BASE}" "${JSHC_ROOT}/experiments/channel-runtime")
target_link_libraries(p16_direct_sentinel_contracts PRIVATE OpenMP::OpenMP_CXX)
target_compile_options(p16_direct_sentinel_contracts PRIVATE -Wall -Wextra -fstack-usage)
'''
    products['CMakeLists.txt']=cmake
    target=ROOT/'artifacts/p16-direct-sentinel-generated-v1.json'
    if target.exists():raise FileExistsError(f'拒绝覆盖既有回执：{target}')
    for name in products:
        if (OUT/name).exists():raise FileExistsError(f'拒绝覆盖既有生成源：{OUT/name}')
    for name,text in products.items():
        if '\r' in text:text=text.replace('\r\n','\n')
        (OUT/name).write_bytes(text.encode('utf-8'))
    receipt={'status':'仅生成源，未构建、未执行数值或性能','sources':{name:hashlib.sha256(data).hexdigest() for name,data in sources.items()},'outputs':{name:hashlib.sha256((OUT/name).read_bytes()).hexdigest() for name in products}}
    target.parent.mkdir(parents=True,exist_ok=True)
    target.write_text(json.dumps(receipt,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    print(json.dumps({'generated_files':len(products),'receipt':str(target),'performance_calls':0},ensure_ascii=False))

if __name__=='__main__':main()
