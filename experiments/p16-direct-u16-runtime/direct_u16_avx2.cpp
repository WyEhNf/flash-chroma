// uint16输入ID以scale2读取4字节，构造器必须提供末尾至少2字节，本实现预留4B。
#include "direct_u16.hpp"
#include <immintrin.h>
#include <cstring>
namespace jshc_channel {
void avx2_direct_u16(const uint16_t* ids,const uint32_t* palette,const uint8_t* source,uint8_t* output,size_t pixels) noexcept {
  const __m256i byte_mask=_mm256_set1_epi32(0xffffff),id_mask=_mm256_set1_epi32(65535);
  const __m256i unpack=_mm256_setr_epi8(0,1,2,-1,3,4,5,-1,6,7,8,-1,9,10,11,-1,0,1,2,-1,3,4,5,-1,6,7,8,-1,9,10,11,-1);
  const __m256i pack=_mm256_setr_epi8(0,1,2,4,5,6,8,9,10,12,13,14,-1,-1,-1,-1,0,1,2,4,5,6,8,9,10,12,13,14,-1,-1,-1,-1);
  for(size_t p=0;p<pixels;p+=8) {
    const uint8_t* in=source+3*p;uint8_t* out=output+3*p;
    // 24B恰好8像素；先读全包后写，允许原地，不借用第25字节。
    const __m128i lo=_mm_loadu_si128(reinterpret_cast<const __m128i*>(in));
    const __m128i end=_mm_loadl_epi64(reinterpret_cast<const __m128i*>(in+16));
    const __m128i hi=_mm_alignr_epi8(end,lo,12);
    const __m256i raw=_mm256_inserti128_si256(_mm256_castsi128_si256(lo),hi,1);
    const __m256i address=_mm256_and_si256(_mm256_shuffle_epi8(raw,unpack),byte_mask);
    const __m256i index=_mm256_and_si256(_mm256_i32gather_epi32(reinterpret_cast<const int*>(ids),address,2),id_mask);
    const __m256i rgb=_mm256_i32gather_epi32(reinterpret_cast<const int*>(palette),index,4);
    const __m256i bytes=_mm256_shuffle_epi8(rgb,pack);
    const __m128i low=_mm256_castsi256_si128(bytes),high=_mm256_extracti128_si256(bytes,1);
    _mm_storeu_si128(reinterpret_cast<__m128i*>(out),_mm_or_si128(low,_mm_slli_si128(high,12)));
    _mm_storel_epi64(reinterpret_cast<__m128i*>(out+16),_mm_srli_si128(high,4));
  }
}
}
