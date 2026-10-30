#pragma once
#include "direct_sentinel.hpp"
#include <immintrin.h>

namespace jshc_channel {
namespace {
// Windows x64的外部栈边界仅保证16B。跨noinline调用只传显式输出指针，禁止256bit按值返回。
inline __attribute__((noinline)) void sentinel_slow_eight_words(const DirectSentinelView& context,const uint8_t* source,uint32_t* words) noexcept {
  alignas(32) uint8_t rgb[24];std::memcpy(rgb,source,24);
  avx2_chain_cached(context.chain,context.cache,rgb,8);
  for(size_t i=0;i<8;++i)words[i]=uint32_t(rgb[3*i])|(uint32_t(rgb[3*i+1])<<8)|(uint32_t(rgb[3*i+2])<<16);
}
inline __attribute__((always_inline)) __m256i sentinel_slow_eight(const DirectSentinelView& context,const uint8_t* source) noexcept {
  uint32_t words[8];sentinel_slow_eight_words(context,source,words);
  return _mm256_loadu_si256(reinterpret_cast<const __m256i*>(words));
}
inline __attribute__((always_inline)) bool sentinel_any(uint32_t a,uint32_t b,uint32_t c,uint32_t d,uint32_t e,uint32_t f,uint32_t g,uint32_t h) noexcept {
  return a==255 || b==255 || c==255 || d==255 || e==255 || f==255 || g==255 || h==255;
}
}
}
