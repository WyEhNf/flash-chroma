#pragma once
#include "channel_runtime.h"
#include "channel_views.hpp"
#include "suffix_cache.hpp"
#include <cstdint>
namespace jshc_channel {
// 四ID/5B小端编码；标量读取只访问本ID的两个合法数据字节。
inline uint32_t direct_u10_id(const uint8_t* table,uint32_t address) noexcept {
  const size_t position=size_t(address>>2)*5+(address&3u);
  const uint32_t word=uint32_t(table[position])|(uint32_t(table[position+1])<<8);
  return (word>>(2*(address&3u)))&1023u;
}

inline bool direct_u10_palette_fits(size_t n) noexcept {return n>0 && n<=1024;}
bool avx2_compile_direct_u10(const View*,const SuffixCacheView&,const uint32_t*,uint8_t*,size_t,size_t) noexcept;
void avx2_direct_u10(const uint8_t*,const uint32_t*,const uint8_t*,uint8_t*,size_t,uint32_t mode=0) noexcept;
}
extern "C" {
// reason：0启用10bit，1旧8bit优先，2无四级域资格，3超1024，4分配失败，5ID证明失败。
struct p16_direct_u10_info {
  uint32_t version,enabled,format,reason,palette_size,id_bytes,guard_bytes,reserved;
  uint64_t input_entries,raw_words,table_capacity_bytes,palette_capacity_bytes,temporary_peak_bytes;
  uint64_t guaranteed_alignment,data_mod_64;
  double prepare_seconds;
};
JSHC_CC_API int p16_cc_get_direct_u10_info(const void*,p16_direct_u10_info*,size_t);
JSHC_CC_API int p16_cc_copy_u10_palette(const void*,uint32_t*,size_t);
}
