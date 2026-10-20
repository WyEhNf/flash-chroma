// 精确全域字节索引：四包独立读取先行，按RGB24读取合法对齐词。
#include "suffix_cache.hpp"
#include <immintrin.h>
namespace jshc_channel {
namespace {
inline __attribute__((always_inline)) __m256i input(const uint8_t* p) {
  const __m128i lo=_mm_loadu_si128(reinterpret_cast<const __m128i*>(p));
  const __m128i last=_mm_loadl_epi64(reinterpret_cast<const __m128i*>(p+16));
  const __m128i hi=_mm_alignr_epi8(last,lo,12);
  return _mm256_shuffle_epi8(_mm256_inserti128_si256(_mm256_castsi128_si256(lo),hi,1),
    _mm256_setr_epi8(2,1,0,-1,5,4,3,-1,8,7,6,-1,11,10,9,-1,2,1,0,-1,5,4,3,-1,8,7,6,-1,11,10,9,-1));
}
inline __attribute__((always_inline)) __m256i lookup(const uint32_t* table,const uint32_t* dictionary,__m256i code) {
  const __m256i id=_mm256_and_si256(_mm256_i32gather_epi32(reinterpret_cast<const int*>(table),_mm256_srli_epi32(code,3),2),_mm256_set1_epi32(65535));
  const __m256i index=_mm256_or_si256(_mm256_slli_epi32(id,3),_mm256_and_si256(code,_mm256_set1_epi32(7)));
  return _mm256_i32gather_epi32(reinterpret_cast<const int*>(dictionary),index,4);
}
inline __attribute__((always_inline)) void output(uint8_t* p,__m256i value) {
  const __m256i bytes=_mm256_shuffle_epi8(value,_mm256_setr_epi8(0,1,2,4,5,6,8,9,10,12,13,14,-1,-1,-1,-1,0,1,2,4,5,6,8,9,10,12,13,14,-1,-1,-1,-1));
  const __m128i lo=_mm256_castsi256_si128(bytes),hi=_mm256_extracti128_si256(bytes,1);
  _mm_storeu_si128(reinterpret_cast<__m128i*>(p),_mm_or_si128(lo,_mm_slli_si128(hi,12)));
  _mm_storel_epi64(reinterpret_cast<__m128i*>(p+16),_mm_srli_si128(hi,4));
}
}
namespace {
inline __attribute__((always_inline)) void run(const uint32_t* table,const uint32_t* dictionary,const uint8_t* source,uint8_t* destination,size_t pixels) noexcept {
  size_t p=0;
  for(;p+32<=pixels;p+=32) {
    const __m256i c0=input(source+3*p),c1=input(source+3*p+24),c2=input(source+3*p+48),c3=input(source+3*p+72);
    const __m256i r0=lookup(table,dictionary,c0),r1=lookup(table,dictionary,c1),r2=lookup(table,dictionary,c2),r3=lookup(table,dictionary,c3);
    output(destination+3*p,r0);output(destination+3*p+24,r1);output(destination+3*p+48,r2);output(destination+3*p+72,r3);
  }
  for(;p<pixels;p+=8) {const __m256i c=input(source+3*p);output(destination+3*p,lookup(table,dictionary,c));}
}
 }
void avx2_chain_rgbdictionary(const uint32_t* table,const uint32_t* dictionary,uint8_t* data,size_t pixels) noexcept {run(table,dictionary,data,data,pixels);}
void avx2_chain_rgbdictionary_to(const uint32_t* table,const uint32_t* dictionary,const uint8_t* source,uint8_t* destination,size_t pixels) noexcept {run(table,dictionary,source,destination,pixels);}
}
