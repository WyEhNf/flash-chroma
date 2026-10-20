#pragma once
#include "channel_runtime.h"
#include "channel_views.hpp"

namespace jshc_domain_cache {
struct SuffixCacheView {
  const uint32_t* table = nullptr;
  int32_t r_min = 0, r_max = 0, dg_min = 0, dg_max = 0, db_min = 0, db_max = 0;
  int32_t width_g = 0, width_b = 0;
};
void avx2_chain_cached(const View* chain, const SuffixCacheView& cache,
    uint8_t* rgb, size_t pixels, bool proven) noexcept;
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
// 每次只读重算；不在模型中持久化大数组，也不进入计时循环。
struct jshc_cc_domain_info {
  uint32_t version, eligible, cache_enabled, reserved;
  uint64_t reachable_cells, unproven_cells;
  int32_t dg_min, dg_max, db_min, db_max;
};
JSHC_CC_API int jshc_cc_get_domain_info(const void* handle, jshc_cc_domain_info* info, size_t bytes);
}
