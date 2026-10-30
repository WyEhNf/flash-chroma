#pragma once
#include "channel_runtime.h"
#include "channel_views.hpp"

namespace jshc_compact_cache {
struct SuffixCacheView {
  const uint32_t* table = nullptr;
  int32_t r_min = 0, r_max = 0, dg_min = 0, dg_max = 0, db_min = 0, db_max = 0;
  int32_t width_g = 0, width_r = 0;
  int32_t out_dg_base = 0, out_db_base = 0;
  uint32_t compact16 = 0, raw_capacity_bytes = 0;
};
static_assert(sizeof(void*)!=8 || sizeof(SuffixCacheView)==56, "x64格式/偏移/原容量只增加16字节");
void avx2_chain_cached(const View* chain, const SuffixCacheView& cache,
    uint8_t* rgb, size_t pixels) noexcept;
}

extern "C" {
// 只读研究诊断；不改变SLUT格式。reason：0启用、1非四级、2超预算、3无合法槽、4分配失败。
struct jshc_cc_cache_info {
  uint32_t version, enabled, reason, reserved;
  uint64_t entries, valid_entries, table_capacity_bytes, temporary_capacity_bytes;
  double prepare_seconds;
  int32_t r_min, r_max, dg_min, dg_max, db_min, db_max;
};
JSHC_CC_API int jshc_cc_get_cache_info(const void* handle, jshc_cc_cache_info* info, size_t bytes);
// 必须恰好等于entries；失败不写目标。空表仅接受entries=0。
JSHC_CC_API int jshc_cc_copy_cache(const void* handle, uint32_t* table, size_t entries);
// 逐项可逆格式；reason：0编码、1跨度超4位、2无缓存、3编码分配失败保留原表。
struct jshc_cc_cache_encoding {
  uint32_t version, format, reason, reserved;
  int32_t out_dg_base, out_db_base;
  uint64_t logical_entries, storage_words, capacity_bytes, raw_capacity_bytes, peak_payload_capacity_bytes;
};
static_assert(sizeof(jshc_cc_cache_encoding)==64, "只读诊断固定64字节");
JSHC_CC_API int jshc_cc_get_cache_encoding(const void* handle, jshc_cc_cache_encoding* info, size_t bytes);
// 返回真实u32物理词，不把逻辑RGB槽与编码词数混用；长度失败不写。
JSHC_CC_API int jshc_cc_copy_cache_words(const void* handle, uint32_t* words, size_t count);
}
