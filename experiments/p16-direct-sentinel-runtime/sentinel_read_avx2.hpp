#pragma once
#include "direct_sentinel.hpp"
#include <immintrin.h>

namespace jshc_channel {
namespace {
// 逐8lane精确回退。先完整复制24B，因此原地写不会破坏本包的输入。
inline __attribute__((noinline)) __m256i sentinel_slow_eight(const DirectSentinelView& context,const uint8_t* source) noexcept {
  alignas(32) uint8_t rgb[24];std::memcpy(rgb,source,24);
  avx2_chain_cached(context.chain,context.cache,rgb,8);
  const auto word=[&](size_t i){return int32_t(uint32_t(rgb[3*i])|(uint32_t(rgb[3*i+1])<<8)|(uint32_t(rgb[3*i+2])<<16));};
  return _mm256_setr_epi32(word(0),word(1),word(2),word(3),word(4),word(5),word(6),word(7));
}
inline __attribute__((always_inline)) bool sentinel_any(uint32_t a,uint32_t b,uint32_t c,uint32_t d,uint32_t e,uint32_t f,uint32_t g,uint32_t h) noexcept {
  return a==255 || b==255 || c==255 || d==255 || e==255 || f==255 || g==255 || h==255;
}
}
}
