"""从冻结288生成292紧密RGB24输出表；不构建、不运行像素，不覆盖已有目录。"""
from __future__ import annotations
import hashlib
import json
from pathlib import Path
import re

ROOT = Path(__file__).resolve().parents[1]


def sha(path):
    with Path(path).open('rb') as stream:
        return hashlib.file_digest(stream, 'sha256').hexdigest()


def once(text, old, new):
    if text.count(old) != 1:
        raise ValueError('预期唯一的源码标记失配：' + old)
    return text.replace(old, new, 1)


def save(path, value):
    if path.exists():
        raise FileExistsError('不覆盖证据：' + str(path))
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')


def main():
    old = ROOT / 'experiments/p16-direct-u16-ilp-runtime'
    target = ROOT / 'experiments/p16-direct-rgb24-runtime'
    frozen = ROOT / 'artifacts/p16-direct-rgb24-source-v1'
    if target.exists() or frozen.exists():
        raise FileExistsError('不覆盖292生成或原冻结')
    sources = list(old.iterdir()) + [Path(__file__), ROOT / 'AGENTS.md', ROOT / 'experiments/p16-direct-rgb24-plan-v1.md']
    frozen.mkdir(parents=True)
    identities = {}
    for path in sources:
        if not path.is_file():
            continue
        name = path.relative_to(ROOT).as_posix()
        snapshot = frozen / 'sources' / name
        snapshot.parent.mkdir(parents=True, exist_ok=True)
        snapshot.write_bytes(path.read_bytes())
        identities[name] = {'sha256': sha(path), 'bytes': path.stat().st_size}
    save(frozen / 'frozen.json', {'purpose': '只冻结292生成的288输入与协议，尚未构建或质量', 'sources': identities,
                                 'performance_calls': 0, 'mechanism': '完整50331648B RGB24输出加4B guard；旧8bit优先'})
    target.mkdir()
    outputs = {}
    for path in sorted(old.iterdir()):
        if not path.is_file() or path.name in ('contracts.cpp', 'direct_u16.hpp'):
            continue
        text = path.read_text(encoding='utf-8')
        text = text.replace('direct_u16', 'direct_rgb24').replace('palette_u16', 'palette_rgb24')
        text = text.replace('copy_u16_palette', 'copy_rgb24_palette')
        text = text.replace('const uint16_t*', 'const uint8_t*')
        if path.name in ('linear.cpp', 'andn_inplace.cpp', 'andn_outplace.cpp', 'normal_inplace.cpp'):
            text = text.replace('palette[table[code]]', 'direct_rgb24_word(table,code)')
            text = re.sub(r'bytes\[([^\]]+)\]', r'direct_rgb24_word(bytes,\1)', text)
            for index in range(8):
                text = text.replace(f'palette[i{index}]', f'i{index}')
            text = text.replace('精确全域uint16索引', '精确全域RGB24输出')
        elif path.name == 'channel_runtime.cpp':
            text = once(text, 'return 288;', 'return 292;')
            text = text.replace('std::vector<uint16_t> direct_rgb24;', 'std::vector<uint8_t> direct_rgb24;')
            text = once(text, 'const uint32_t value=h.palette_rgb24[h.direct_rgb24[address]];', 'const uint32_t value=jshc_channel::direct_rgb24_word(h.direct_rgb24.data(),address);')
            begin = text.index('void prepare_direct_rgb24(Handle& h) {')
            end = text.index('\n}\n}', begin) + 2
            text = text[:begin] + PREPARE + text[end:]
            text = text.replace('h.direct_rgb24.capacity()*sizeof(uint16_t)', 'h.direct_rgb24.capacity()')
            text = text.replace('h.direct_rgb24.size()/2', 'h.direct_rgb24.size()/4')
            text = text.replace('*output={1,1,16,0,h.direct_rgb24.size()/4', '*output={1,1,18,0,h.direct_rgb24.size()/4')
            text = text.replace('16bit直接表诊断ABI固定为96字节', 'RGB24直接表诊断ABI固定为96字节')
        elif path.name == 'compile_avx2.cpp':
            begin = text.index('bool avx2_compile_direct_rgb24(')
            prefix = text[:begin]
            body = text[begin:]
            body = body.replace('uint16_t* destination', 'uint8_t* destination')
            body = body.replace('_mm256_srli_epi32(values,16)', '_mm256_srli_epi32(values,24)')
            start = body.index('    // 无符号65535')
            body = body[:start] + COMPILE_OUTPUT + '\n  }\n  return true;\n}\n}\n'
            text = prefix + body
        elif path.name == 'CMakeLists.txt':
            text = text.replace('direct_rgb24_ilp', 'direct_rgb24')
        filename = path.name.replace('direct_u16', 'direct_rgb24')
        output = target / filename
        output.write_text(text, encoding='utf-8', newline='\n')
        outputs[filename] = sha(output)
    for name, text in [('direct_rgb24.hpp', HEADER), ('contracts.cpp', CONTRACTS)]:
        (target / name).write_text(text, encoding='utf-8', newline='\n')
        outputs[name] = sha(target / name)
    save(frozen / 'generated.json', {'outputs': outputs, 'source_frozen_sha256': sha(frozen / 'frozen.json'), 'performance_calls': 0})
    print(json.dumps({'generated': len(outputs), 'source_count': len(identities), 'performance_calls': 0}, ensure_ascii=False))


PREPARE = '''void prepare_direct_rgb24(Handle& h) {
  auto& info=h.direct_rgb24_info;
  info={};info.version=1;info.format=18;info.id_bytes=3;info.guard_bytes=4;
  info.guaranteed_alignment=alignof(uint8_t);
  if(!h.direct_index.empty() || h.palette_info.enabled){info.reason=1;return;}
  if(!domain_fast_enabled(h) || !(jshc_cc_capabilities()&2)){info.reason=2;return;}
  const auto start=std::chrono::steady_clock::now();
  try {
    std::vector<uint8_t> table((size_t{3}<<24)+4,0);
    size_t bad=0;
#if defined(_OPENMP)
    const int build_workers=omp_in_parallel()?1:4;
#pragma omp parallel for schedule(static) num_threads(build_workers) reduction(+:bad)
#endif
    for(long long block=0;block<256;++block) {
      const size_t begin=size_t(block)*65536;
      bad+=!jshc_channel::avx2_compile_direct_rgb24(h.views.data(),h.cache_view,h.cache.data(),table.data()+3*begin,begin,65536);
    }
    info.temporary_peak_bytes=table.capacity();
    if(bad){info.reason=5;info.prepare_seconds=std::chrono::duration<double>(std::chrono::steady_clock::now()-start).count();return;}
    h.direct_rgb24.swap(table);
    info.enabled=1;info.reason=0;info.input_entries=size_t{1}<<24;info.raw_words=h.direct_rgb24.size()/4;
    info.table_capacity_bytes=h.direct_rgb24.capacity();info.palette_capacity_bytes=0;
    info.data_mod_64=uint64_t(reinterpret_cast<uintptr_t>(h.direct_rgb24.data())&63);
  }catch(const std::bad_alloc&){info.reason=4;}
  info.prepare_seconds=std::chrono::duration<double>(std::chrono::steady_clock::now()-start).count();
}'''

COMPILE_OUTPUT = '''    // RGB32高8位必须为0；禁止将完整RGB色误当uint16 ID截断。
    const __m256i high=_mm256_srli_epi32(values,24);
    if(!_mm256_testz_si256(high,high))return false;
    const __m256i bytes=_mm256_shuffle_epi8(values,_mm256_setr_epi8(0,1,2,4,5,6,8,9,10,12,13,14,-1,-1,-1,-1,0,1,2,4,5,6,8,9,10,12,13,14,-1,-1,-1,-1));
    const __m128i lo=_mm256_castsi256_si128(bytes),hi=_mm256_extracti128_si256(bytes,1);
    // 恰24B；不能跨65536输入块写32B并发覆盖邻块。
    _mm_storeu_si128(reinterpret_cast<__m128i*>(destination+3*p),_mm_or_si128(lo,_mm_slli_si128(hi,12)));
    _mm_storel_epi64(reinterpret_cast<__m128i*>(destination+3*p+16),_mm_srli_si128(hi,4));'''

HEADER = '''#pragma once
#include "channel_runtime.h"
#include "channel_views.hpp"
#include "suffix_cache.hpp"
#include <cstdint>
#include <cstring>
namespace jshc_channel {
inline __attribute__((always_inline)) uint32_t direct_rgb24_word(const uint8_t* table,uint32_t code) noexcept {
  uint32_t word;std::memcpy(&word,table+size_t{3}*code,4);return word&0xffffffu;
}
bool avx2_compile_direct_rgb24(const View*,const SuffixCacheView&,const uint32_t*,uint8_t*,size_t,size_t) noexcept;
void avx2_direct_rgb24(const uint8_t*,const uint32_t*,const uint8_t*,uint8_t*,size_t,uint32_t mode=0) noexcept;
}
extern "C" {
// 保留96B ABI；id_bytes在format18表示每个直接RGB值的三字节长度，palette为空。
struct p16_direct_rgb24_info {
  uint32_t version,enabled,format,reason,palette_size,id_bytes,guard_bytes,reserved;
  uint64_t input_entries,raw_words,table_capacity_bytes,palette_capacity_bytes,temporary_peak_bytes;
  uint64_t guaranteed_alignment,data_mod_64;
  double prepare_seconds;
};
JSHC_CC_API int p16_cc_get_direct_rgb24_info(const void*,p16_direct_rgb24_info*,size_t);
JSHC_CC_API int p16_cc_copy_rgb24_palette(const void*,uint32_t*,size_t);
}
'''

CONTRACTS = '''// 完整RGB24色值、恰长输入/输出、表末guard的独立有限合同。
#define NOMINMAX
#include "direct_rgb24.hpp"
#include <windows.h>
#include <array>
#include <cstring>
#include <iostream>
#include <stdexcept>
#include <vector>
namespace {
void require(bool value,const char* text){if(!value)throw std::runtime_error(text);}
struct Guarded {
  uint8_t* allocation=nullptr;uint8_t* data=nullptr;
  explicit Guarded(size_t bytes) {
    SYSTEM_INFO s;GetSystemInfo(&s);const size_t page=s.dwPageSize;
    const size_t accessible=(bytes+page-1)/page*page;
    allocation=static_cast<uint8_t*>(VirtualAlloc(nullptr,accessible+page,MEM_RESERVE|MEM_COMMIT,PAGE_READWRITE));
    require(allocation,"VirtualAlloc失败");DWORD old=0;
    require(VirtualProtect(allocation+accessible,page,PAGE_NOACCESS,&old)!=0,"guard失败");
    data=allocation+accessible-bytes;
  }
  ~Guarded(){if(allocation)VirtualFree(allocation,0,MEM_RELEASE);}
  Guarded(const Guarded&)=delete;Guarded& operator=(const Guarded&)=delete;
};
}
int main(){try{
  using namespace jshc_channel;
  uint32_t axes[256]{},nodes[8]{};View view{};
  for(int c=0;c<3;++c)for(int a=0;a<3;++a)view.axes[c][a]=axes;
  view.nodes=nodes;view.sr=4;view.sg=2;view.shared=false;
  SuffixCacheView cache{};cache.width_g=cache.width_b=1;
  size_t compile_cases=0;
  for(uint32_t color:{0u,255u,256u,65535u,65536u,0xffffffu,0x1000000u}){
    std::array<uint8_t,24> output;output.fill(123);
    const bool ok=avx2_compile_direct_rgb24(&view,cache,&color,output.data(),0,8);
    require(ok==(color<=0xffffffu),"编译RGB24范围失败");
    for(size_t i=0;i<24;++i)require(output[i]==(ok?uint8_t(color>>(8*(i%3))):123),"RGB截断或失败写入");
    ++compile_cases;
  }
  constexpr size_t count=size_t{1}<<24;
  Guarded table(3*count+4);std::memset(table.data,0,3*count+4);
  const std::array<uint32_t,8> addresses={0,1,255,256,65535,65536,0xfffffe,0xffffff};
  const std::array<uint32_t,8> colors={0,0xffffff,0x800000,0x008000,0x000080,0x010203,0xfedcba,0xabcdef};
  for(size_t i=0;i<8;++i)for(int c=0;c<3;++c)table.data[3*addresses[i]+c]=uint8_t(colors[i]>>(8*c));
  size_t guarded_cases=0;
  for(uint32_t mode=0;mode<4;++mode){
    if(mode&&!__builtin_cpu_supports("bmi"))continue;
    for(size_t length:{0u,1u,7u,8u,9u,31u,32u,39u,40u,64u,71u,72u,73u,4095u,4096u,4097u,65535u,65536u,65537u}){
      Guarded source(3*length),target(3*length);std::vector<uint8_t> expected(3*length),original(3*length);
      for(size_t i=0;i<length;++i)for(int c=0;c<3;++c){original[3*i+c]=uint8_t(addresses[i%8]>>(8*c));expected[3*i+c]=uint8_t(colors[i%8]>>(8*c));}
      if(length)std::memcpy(source.data,original.data(),3*length);
      avx2_direct_rgb24(table.data,nullptr,source.data,target.data,length,mode);
      require(!length||std::memcmp(target.data,expected.data(),3*length)==0,"分离恰长RGB24错误");
      avx2_direct_rgb24(table.data,nullptr,source.data,source.data,length,mode);
      require(!length||std::memcmp(source.data,expected.data(),3*length)==0,"原地恰长RGB24错误");
      guarded_cases+=2;
    }
  }
  for(size_t i=0;i<4;++i)require(table.data[3*count+i]==0,"末guard被写入");
  std::cout<<"{\\"passed\\":true,\\"compile_color_cases\\":"<<compile_cases<<",\\"guarded_cases\\":"<<guarded_cases<<",\\"guard_bytes\\":4,\\"performance_calls\\":0}"<<std::endl;
  return 0;
}catch(const std::exception& e){std::cerr<<e.what()<<std::endl;return 1;}}
'''


if __name__ == '__main__':
    main()
