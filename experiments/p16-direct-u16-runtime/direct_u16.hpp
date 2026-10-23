#pragma once
#include "channel_runtime.h"
#include "channel_views.hpp"
#include "suffix_cache.hpp"
#include <cstdint>
namespace jshc_channel {
inline bool direct_u16_palette_fits(size_t n) noexcept {return n>0 && n<=65536;}
bool avx2_compile_direct_u16(const View*,const SuffixCacheView&,const uint32_t*,uint16_t*,size_t,size_t) noexcept;
void avx2_direct_u16(const uint16_t*,const uint32_t*,const uint8_t*,uint8_t*,size_t) noexcept;
}
extern "C" {
// reason：0启用16bit，1旧8bit优先，2无四级域资格，3超65536，4分配失败，5ID证明失败。
struct p16_direct_u16_info {
  uint32_t version,enabled,format,reason,palette_size,id_bytes,guard_bytes,reserved;
  uint64_t input_entries,raw_words,table_capacity_bytes,palette_capacity_bytes,temporary_peak_bytes;
  uint64_t guaranteed_alignment,data_mod_64;
  double prepare_seconds;
};
JSHC_CC_API int p16_cc_get_direct_u16_info(const void*,p16_direct_u16_info*,size_t);
JSHC_CC_API int p16_cc_copy_u16_palette(const void*,uint32_t*,size_t);
}
