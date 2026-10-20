// 精确16bit输出编码：R占8bit，G-R和B-R相对各自最小值分别占4bit。
#include "suffix_cache.hpp"
#include <immintrin.h>
namespace jshc_channel {
namespace {
inline __attribute__((always_inline)) __m256i input(const uint8_t* p) {
  const __m128i lo=_mm_loadu_si128(reinterpret_cast<const __m128i*>(p));
  const __m128i last=_mm_loadl_epi64(reinterpret_cast<const __m128i*>(p+16));
  const __m128i hi=_mm_alignr_epi8(last,lo,12);
  const __m256i raw=_mm256_inserti128_si256(_mm256_castsi128_si256(lo),hi,1);
  return _mm256_shuffle_epi8(raw,_mm256_setr_epi8(2,1,0,-1,5,4,3,-1,8,7,6,-1,11,10,9,-1,2,1,0,-1,5,4,3,-1,8,7,6,-1,11,10,9,-1));
}
inline __attribute__((always_inline)) __m256i lookup(const uint32_t* table,__m256i code) {
  return _mm256_i32gather_epi32(reinterpret_cast<const int*>(table),_mm256_srli_epi32(code,1),4);
}
inline __attribute__((always_inline)) void output(uint8_t* p,__m256i code,__m256i word,__m256i dg,__m256i db) {
  const __m256i packed=_mm256_srlv_epi32(word,_mm256_slli_epi32(_mm256_and_si256(code,_mm256_set1_epi32(1)),4));
  const __m256i r=_mm256_and_si256(packed,_mm256_set1_epi32(255));
  const __m256i g=_mm256_add_epi32(r,_mm256_add_epi32(dg,_mm256_and_si256(_mm256_srli_epi32(packed,8),_mm256_set1_epi32(15))));
  const __m256i b=_mm256_add_epi32(r,_mm256_add_epi32(db,_mm256_and_si256(_mm256_srli_epi32(packed,12),_mm256_set1_epi32(15))));
  const __m256i value=_mm256_or_si256(r,_mm256_or_si256(_mm256_slli_epi32(g,8),_mm256_slli_epi32(b,16)));
  const __m256i bytes=_mm256_shuffle_epi8(value,_mm256_setr_epi8(0,1,2,4,5,6,8,9,10,12,13,14,-1,-1,-1,-1,0,1,2,4,5,6,8,9,10,12,13,14,-1,-1,-1,-1));
  const __m128i bottom=_mm256_castsi256_si128(bytes),top=_mm256_extracti128_si256(bytes,1);
  _mm_storeu_si128(reinterpret_cast<__m128i*>(p),_mm_or_si128(bottom,_mm_slli_si128(top,12)));
  _mm_storel_epi64(reinterpret_cast<__m128i*>(p+16),_mm_srli_si128(top,4));
}
}
void avx2_chain_direct16(const uint32_t* table,int32_t dg_min,int32_t db_min,uint8_t* data,size_t pixels) noexcept {
  const __m256i dg=_mm256_set1_epi32(dg_min),db=_mm256_set1_epi32(db_min);size_t p=0;
  for(;p+16<=pixels;p+=16) {
    const __m256i c0=input(data+3*p),c1=input(data+3*p+24);
    const __m256i w0=lookup(table,c0),w1=lookup(table,c1);
    output(data+3*p,c0,w0,dg,db);output(data+3*p+24,c1,w1,dg,db);
  }
  if(p<pixels) {const __m256i c=input(data+3*p);output(data+3*p,c,lookup(table,c),dg,db);}
}
}
