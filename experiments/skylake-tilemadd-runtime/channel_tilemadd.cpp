// 精确全域字节索引：四包独立读取先行，按RGB24读取合法对齐词。
#include "suffix_cache.hpp"
#include <immintrin.h>
#include <cstring>
namespace jshc_channel {
namespace {
inline __attribute__((always_inline)) uint32_t index(uint32_t c) {
  return ((c&0xfcu)<<4)|((c&0xfc00u)<<2)|(c&0xfc0000u)|(c&3u)|((c>>6)&12u)|((c>>12)&48u);
}
inline __attribute__((always_inline)) __m256i input(const uint8_t* p) {
  const __m128i lo=_mm_loadu_si128(reinterpret_cast<const __m128i*>(p));
  const __m128i last=_mm_loadl_epi64(reinterpret_cast<const __m128i*>(p+16));
  const __m128i hi=_mm_alignr_epi8(last,lo,12);
  return _mm256_shuffle_epi8(_mm256_inserti128_si256(_mm256_castsi128_si256(lo),hi,1),
    _mm256_setr_epi8(0,1,2,-1,3,4,5,-1,6,7,8,-1,9,10,11,-1,0,1,2,-1,3,4,5,-1,6,7,8,-1,9,10,11,-1));
}
inline __attribute__((always_inline)) __m256i indices(__m256i c) {
  // R/G展开为无符号16位，再以64/4096系数组成索引高位；值均≤63。
  const __m256i rg=_mm256_shuffle_epi8(c,_mm256_setr_epi8(0,-1,1,-1,4,-1,5,-1,8,-1,9,-1,12,-1,13,-1,0,-1,1,-1,4,-1,5,-1,8,-1,9,-1,12,-1,13,-1));
  const __m256i high_rg=_mm256_madd_epi16(_mm256_srli_epi16(rg,2),_mm256_set1_epi32(0x10000040));
  // 低2位的加权和最大63，PMADDUBSW的两个16位部分和分别≤15及≤48，不饱和。
  const __m256i low=_mm256_madd_epi16(_mm256_maddubs_epi16(_mm256_and_si256(c,_mm256_set1_epi32(0x030303)),_mm256_set1_epi32(0x00100401)),_mm256_set1_epi16(1));
  const __m256i high_b=_mm256_and_si256(c,_mm256_set1_epi32(0xfc0000));
  return _mm256_or_si256(_mm256_or_si256(high_rg,high_b),low);
}
// 先以AVX2计算8个地址，再用普通GPR字节加载，避免硬件gather及逐像素PEXT。
inline __attribute__((always_inline)) __m256i read(const uint32_t* table,const uint32_t* palette,const uint8_t* p) {
  const __m256i code=indices(input(p));
  const auto value=[table,palette](uint32_t i) {return int32_t(palette[reinterpret_cast<const uint8_t*>(table)[i]]);};
  return _mm256_setr_epi32(value(_mm256_extract_epi32(code,0)),value(_mm256_extract_epi32(code,1)),
    value(_mm256_extract_epi32(code,2)),value(_mm256_extract_epi32(code,3)),value(_mm256_extract_epi32(code,4)),
    value(_mm256_extract_epi32(code,5)),value(_mm256_extract_epi32(code,6)),value(_mm256_extract_epi32(code,7)));
}
inline __attribute__((always_inline)) __m256i read_wide(const uint32_t* table,const uint32_t* palette,const uint8_t* p) {
  return read(table,palette,p);
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
inline __attribute__((always_inline)) void output_four_stream(uint8_t* p,__m256i v0,__m256i v1,__m256i v2,__m256i v3) {
  const __m128i a=_mm256_castsi256_si128(v0),b=_mm256_extracti128_si256(v0,1);
  const __m128i c=_mm256_castsi256_si128(v1),d=_mm256_extracti128_si256(v1,1);
  const __m128i e=_mm256_castsi256_si128(v2),f=_mm256_extracti128_si256(v2,1);
  const __m128i g=_mm256_castsi256_si128(v3),h=_mm256_extracti128_si256(v3,1);
  const __m256i s0=_mm256_inserti128_si256(_mm256_castsi128_si256(a),_mm_unpacklo_epi64(b,c),1);
  const __m256i s1=_mm256_inserti128_si256(_mm256_castsi128_si256(_mm_alignr_epi8(d,c,8)),e,1);
  const __m256i s2=_mm256_inserti128_si256(_mm256_castsi128_si256(_mm_unpacklo_epi64(f,g)),_mm_alignr_epi8(h,g,8),1);
  _mm256_stream_si256(reinterpret_cast<__m256i*>(p),s0);
  _mm256_stream_si256(reinterpret_cast<__m256i*>(p+32),s1);
  _mm256_stream_si256(reinterpret_cast<__m256i*>(p+64),s2);
}
inline __attribute__((always_inline)) void scalar_one(const uint32_t* table,const uint32_t* palette,const uint8_t* source,uint8_t* destination) {
  const uint32_t code=uint32_t(source[0])|(uint32_t(source[1])<<8)|(uint32_t(source[2])<<16);
  const uint32_t value=palette[reinterpret_cast<const uint8_t*>(table)[index(code)]];
  destination[0]=uint8_t(value);destination[1]=uint8_t(value>>8);destination[2]=uint8_t(value>>16);
}
inline __attribute__((always_inline)) void run(const uint32_t* table,const uint32_t* palette,const uint8_t* source,uint8_t* destination,size_t pixels) noexcept {
  size_t p=0;
  // 初始窗口只形成有效输入范围内的地址；NTA为提示，CPU可以忽略。
  const size_t initial=pixels*3<1024?pixels*3:1024;
  for(size_t offset=0;offset<initial;offset+=64)_mm_prefetch(reinterpret_cast<const char*>(source+offset),_MM_HINT_NTA);
  // 对齐到完整64字节缓存行，避免前缀普通写与非临时写共享同一行。
  for(;p<pixels && (reinterpret_cast<uintptr_t>(destination+3*p)&63);++p)scalar_one(table,palette,source+3*p,destination+3*p);
  bool streamed=false;
  for(;p+72<=pixels;p+=64) {
    // 固定16缓存行前瞻；四个地址覆盖未来192字节，包括非对齐源末行。
    if(p+406<=pixels) {
      const uint8_t* future=source+3*p+1024;
      _mm_prefetch(reinterpret_cast<const char*>(future),_MM_HINT_NTA);
      _mm_prefetch(reinterpret_cast<const char*>(future+64),_MM_HINT_NTA);
      _mm_prefetch(reinterpret_cast<const char*>(future+128),_MM_HINT_NTA);
      _mm_prefetch(reinterpret_cast<const char*>(future+191),_MM_HINT_NTA);
    }
    // 全部64像素先读后写，主体输出恰好192字节即三条完整缓存行。
    const __m256i r0=pack(read_wide(table,palette,source+3*p)),r1=pack(read_wide(table,palette,source+3*p+24));
    const __m256i r2=pack(read_wide(table,palette,source+3*p+48)),r3=pack(read_wide(table,palette,source+3*p+72));
    const __m256i r4=pack(read_wide(table,palette,source+3*p+96)),r5=pack(read_wide(table,palette,source+3*p+120));
    const __m256i r6=pack(read_wide(table,palette,source+3*p+144)),r7=pack(read_wide(table,palette,source+3*p+168));
    output_four_stream(destination+3*p,r0,r1,r2,r3);output_four_stream(destination+3*p+96,r4,r5,r6,r7);streamed=true;
  }
  // 在普通尾部、调用方读取和OpenMP barrier之前发布非临时写入。
  if(streamed)_mm_sfence();
  for(;p+40<=pixels;p+=32) {
    const __m256i r0=read_wide(table,palette,source+3*p),r1=read_wide(table,palette,source+3*p+24),r2=read_wide(table,palette,source+3*p+48),r3=read_wide(table,palette,source+3*p+72);
    output_four(destination+3*p,pack(r0),pack(r1),pack(r2),pack(r3));
  }
  for(;p+8<=pixels;p+=8)output(destination+3*p,read(table,palette,source+3*p));
  for(;p<pixels;++p)scalar_one(table,palette,source+3*p,destination+3*p);

}
 }
void avx2_chain_tilemadd(const uint32_t* table,const uint32_t* palette,uint8_t* data,size_t pixels) noexcept {run(table,palette,data,data,pixels);}
void avx2_chain_tilemadd_to(const uint32_t* table,const uint32_t* palette,const uint8_t* source,uint8_t* destination,size_t pixels) noexcept {run(table,palette,source,destination,pixels);}
}
