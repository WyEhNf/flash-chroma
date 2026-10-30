#pragma once
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
