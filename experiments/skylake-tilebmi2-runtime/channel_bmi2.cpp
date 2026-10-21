// 精确全域字节索引：四包独立读取先行，按RGB24读取合法对齐词。
#include "suffix_cache.hpp"
#include <immintrin.h>
#include <cstring>
namespace jshc_channel {
namespace {
inline __attribute__((always_inline)) uint32_t index(uint32_t c) {
  return (_pext_u32(c,0xfcfcfcu)<<6)|_pext_u32(c,0x030303u);
}
// 每条64字节行保存4×4×4输入颜色；输出RGB32字节序保持原样。
// 原表按R低/G中/B高的输入字节序排列，输出RGB32的字节序保持原样。
inline __attribute__((always_inline)) __m256i read(const uint32_t* table,const uint32_t* palette,const uint8_t* p) {
  uint64_t a,b,c;std::memcpy(&a,p,8);std::memcpy(&b,p+8,8);std::memcpy(&c,p+16,8);
  const auto value=[table,palette](uint32_t code) {return int32_t(palette[reinterpret_cast<const uint8_t*>(table)[index(code)]]);};
  return _mm256_setr_epi32(value(uint32_t(a&0xffffff)),value(uint32_t((a>>24)&0xffffff)),
      value(uint32_t(((a>>48)|(b<<16))&0xffffff)),value(uint32_t((b>>8)&0xffffff)),
      value(uint32_t((b>>32)&0xffffff)),value(uint32_t(((b>>56)|(c<<8))&0xffffff)),
      value(uint32_t((c>>16)&0xffffff)),value(uint32_t(c>>40)));
}
// 仅宽循环调用；最后一个32bit输入读取多出的1字节仍在当前线程块内。
inline __attribute__((always_inline)) __m256i read_wide(const uint32_t* table,const uint32_t* palette,const uint8_t* p) {
  const auto value=[table,palette,p](size_t offset) {uint32_t code;std::memcpy(&code,p+offset,4);return int32_t(palette[reinterpret_cast<const uint8_t*>(table)[index(code)]]);};
  return _mm256_setr_epi32(value(0),value(3),value(6),value(9),value(12),value(15),value(18),value(21));
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
void avx2_chain_tilebmi2(const uint32_t* table,const uint32_t* palette,uint8_t* data,size_t pixels) noexcept {run(table,palette,data,data,pixels);}
void avx2_chain_tilebmi2_to(const uint32_t* table,const uint32_t* palette,const uint8_t* source,uint8_t* destination,size_t pixels) noexcept {run(table,palette,source,destination,pixels);}
}
