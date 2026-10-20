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
// 仅在后续至少还剩8像素时调用，32字节载荷严格落在当前线程块内。
inline __attribute__((always_inline)) __m256i input_wide(const uint8_t* p) {
  const __m256i raw=_mm256_loadu_si256(reinterpret_cast<const __m256i*>(p));
  const __m256i lanes=_mm256_permutevar8x32_epi32(raw,_mm256_setr_epi32(0,1,2,0,3,4,5,0));
  return _mm256_shuffle_epi8(lanes,_mm256_setr_epi8(2,1,0,-1,5,4,3,-1,8,7,6,-1,11,10,9,-1,2,1,0,-1,5,4,3,-1,8,7,6,-1,11,10,9,-1));
}
inline __attribute__((always_inline)) __m256i ids(const uint32_t* table,__m256i code) {
  const __m256i word=_mm256_i32gather_epi32(reinterpret_cast<const int*>(table),_mm256_srli_epi32(code,2),4);
  const __m256i shift=_mm256_slli_epi32(_mm256_and_si256(code,_mm256_set1_epi32(3)),3);
  return _mm256_and_si256(_mm256_srlv_epi32(word,shift),_mm256_set1_epi32(255));
}
inline __attribute__((always_inline)) __m256i rgb(const uint32_t* palette,__m256i index) {
  return _mm256_i32gather_epi32(reinterpret_cast<const int*>(palette),index,4);
}
inline __attribute__((always_inline)) void output(uint8_t* p,__m256i value) {
  const __m256i bytes=_mm256_shuffle_epi8(value,_mm256_setr_epi8(0,1,2,4,5,6,8,9,10,12,13,14,-1,-1,-1,-1,0,1,2,4,5,6,8,9,10,12,13,14,-1,-1,-1,-1));
  const __m128i lo=_mm256_castsi256_si128(bytes),hi=_mm256_extracti128_si256(bytes,1);
  _mm_storeu_si128(reinterpret_cast<__m128i*>(p),_mm_or_si128(lo,_mm_slli_si128(hi,12)));
  _mm_storel_epi64(reinterpret_cast<__m128i*>(p+16),_mm_srli_si128(hi,4));
}
}
namespace {
inline __attribute__((always_inline)) __m256i pack(__m256i value) {
  const __m256i bytes=_mm256_shuffle_epi8(value,_mm256_setr_epi8(0,1,2,4,5,6,8,9,10,12,13,14,-1,-1,-1,-1,0,1,2,4,5,6,8,9,10,12,13,14,-1,-1,-1,-1));
  return _mm256_permutevar8x32_epi32(bytes,_mm256_setr_epi32(0,1,2,4,5,6,3,7));
}
inline __attribute__((always_inline)) void output_four(uint8_t* p,__m256i v0,__m256i v1,__m256i v2,__m256i v3) {
  const __m128i a=_mm256_castsi256_si128(v0),b=_mm256_extracti128_si256(v0,1);
  const __m128i c=_mm256_castsi256_si128(v1),d=_mm256_extracti128_si256(v1,1);
  const __m128i e=_mm256_castsi256_si128(v2),f=_mm256_extracti128_si256(v2,1);
  const __m128i g=_mm256_castsi256_si128(v3),h=_mm256_extracti128_si256(v3,1);
  const __m256i s0=_mm256_inserti128_si256(_mm256_castsi128_si256(a),_mm_unpacklo_epi64(b,c),1);
  const __m256i s1=_mm256_inserti128_si256(_mm256_castsi128_si256(_mm_alignr_epi8(d,c,8)),e,1);
  const __m256i s2=_mm256_inserti128_si256(_mm256_castsi128_si256(_mm_unpacklo_epi64(f,g)),_mm_alignr_epi8(h,g,8),1);
  _mm256_storeu_si256(reinterpret_cast<__m256i*>(p),s0);
  _mm256_storeu_si256(reinterpret_cast<__m256i*>(p+32),s1);
  _mm256_storeu_si256(reinterpret_cast<__m256i*>(p+64),s2);
}
inline __attribute__((always_inline)) void run(const uint32_t* table,const uint32_t* palette,const uint8_t* source,uint8_t* destination,size_t pixels) noexcept {
  size_t p=0;
  for(;p+40<=pixels;p+=32) {
    const __m256i c0=input_wide(source+3*p),c1=input_wide(source+3*p+24),c2=input_wide(source+3*p+48),c3=input_wide(source+3*p+72);
    const __m256i i0=ids(table,c0),i1=ids(table,c1),i2=ids(table,c2),i3=ids(table,c3);
    const __m256i r0=rgb(palette,i0),r1=rgb(palette,i1),r2=rgb(palette,i2),r3=rgb(palette,i3);
    output_four(destination+3*p,pack(r0),pack(r1),pack(r2),pack(r3));
  }
  for(;p<pixels;p+=8) {const __m256i c=input(source+3*p);output(destination+3*p,rgb(palette,ids(table,c)));}
}
 }
void avx2_chain_pack32(const uint32_t* table,const uint32_t* palette,uint8_t* data,size_t pixels) noexcept {run(table,palette,data,data,pixels);}
void avx2_chain_pack32_to(const uint32_t* table,const uint32_t* palette,const uint8_t* source,uint8_t* destination,size_t pixels) noexcept {run(table,palette,source,destination,pixels);}
}
