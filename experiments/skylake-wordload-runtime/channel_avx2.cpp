// 精确主词索引：GPR加载后用AVX2解码，例外池与调色板仍为精确读取。
#include "suffix_cache.hpp"
#include <immintrin.h>
#include <cstring>
namespace jshc_channel {
namespace {
// 首层用八个独立GPR加载，避免对8MiB主表执行硬件gather。
template<bool Wide> inline __attribute__((always_inline)) uint32_t word_at(const uint32_t* table,const uint8_t* p) {
  uint32_t code;
  if constexpr(Wide) {std::memcpy(&code,p,4);code=__builtin_bswap32(code)>>8;}
  else code=(uint32_t(p[0])<<16)|(uint32_t(p[1])<<8)|p[2];
  return table[code>>3];
}
template<bool Wide> inline __attribute__((always_inline)) __m256i read_words(const uint32_t* table,const uint32_t* exceptions,const uint32_t* palette,const uint8_t* p) {
  const __m256i words=_mm256_setr_epi32(word_at<Wide>(table,p),word_at<Wide>(table,p+3),word_at<Wide>(table,p+6),word_at<Wide>(table,p+9),word_at<Wide>(table,p+12),word_at<Wide>(table,p+15),word_at<Wide>(table,p+18),word_at<Wide>(table,p+21));
  const __m128i lo=_mm_loadu_si128(reinterpret_cast<const __m128i*>(p));
  const __m128i last=_mm_loadl_epi64(reinterpret_cast<const __m128i*>(p+16));
  const __m256i raw=_mm256_inserti128_si256(_mm256_castsi128_si256(lo),_mm_alignr_epi8(last,lo,12),1);
  const __m256i code=_mm256_shuffle_epi8(raw,_mm256_setr_epi8(2,1,0,-1,5,4,3,-1,8,7,6,-1,11,10,9,-1,2,1,0,-1,5,4,3,-1,8,7,6,-1,11,10,9,-1));
  const __m256i mask255=_mm256_set1_epi32(255),base=_mm256_and_si256(words,mask255);
  const __m256i offset=_mm256_and_si256(code,_mm256_set1_epi32(7));
  const __m256i shift=_mm256_add_epi32(_mm256_add_epi32(offset,_mm256_slli_epi32(offset,1)),_mm256_set1_epi32(8));
  __m256i ids=_mm256_add_epi32(base,_mm256_and_si256(_mm256_srlv_epi32(words,shift),_mm256_set1_epi32(7)));
  const __m256i exceptional=_mm256_cmpeq_epi32(base,mask255);
  if(_mm256_movemask_epi8(exceptional)) {
    const __m256i index=_mm256_add_epi32(_mm256_and_si256(_mm256_srli_epi32(words,8),exceptional),_mm256_and_si256(_mm256_srli_epi32(code,2),_mm256_set1_epi32(1)));
    const __m256i packed=_mm256_i32gather_epi32(reinterpret_cast<const int*>(exceptions),index,4);
    const __m256i byte_shift=_mm256_slli_epi32(_mm256_and_si256(code,_mm256_set1_epi32(3)),3);
    const __m256i exact=_mm256_and_si256(_mm256_srlv_epi32(packed,byte_shift),mask255);
    ids=_mm256_blendv_epi8(ids,exact,exceptional);
  }
  return _mm256_i32gather_epi32(reinterpret_cast<const int*>(palette),ids,4);
}
inline __attribute__((always_inline)) __m256i read(const uint32_t* table,const uint32_t* exceptions,const uint32_t* palette,const uint8_t* p) {return read_words<false>(table,exceptions,palette,p);}
// 宽循环的最后一次4字节输入读取仍位于当前线程块内。
inline __attribute__((always_inline)) __m256i read_wide(const uint32_t* table,const uint32_t* exceptions,const uint32_t* palette,const uint8_t* p) {return read_words<true>(table,exceptions,palette,p);}
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
inline __attribute__((always_inline)) void scalar_one(const uint32_t* table,const uint32_t* exceptions,const uint32_t* palette,const uint8_t* source,uint8_t* destination) {
  const uint32_t code=(uint32_t(source[0])<<16)|(uint32_t(source[1])<<8)|source[2],word=table[code>>3],base=word&255;
  const uint32_t id=base==255?((exceptions[(word>>8)+((code>>2)&1)]>>((code&3)*8))&255):base+((word>>(8+(code&7)*3))&7);
  const uint32_t value=palette[id];
  destination[0]=uint8_t(value);destination[1]=uint8_t(value>>8);destination[2]=uint8_t(value>>16);
}
inline __attribute__((always_inline)) void run(const uint32_t* table,const uint32_t* exceptions,const uint32_t* palette,const uint8_t* source,uint8_t* destination,size_t pixels) noexcept {
  size_t p=0;
  // 初始窗口只形成有效输入范围内的地址；NTA为提示，CPU可以忽略。
  const size_t initial=pixels*3<1024?pixels*3:1024;
  for(size_t offset=0;offset<initial;offset+=64)_mm_prefetch(reinterpret_cast<const char*>(source+offset),_MM_HINT_NTA);
  // 对齐到完整64字节缓存行，避免前缀普通写与非临时写共享同一行。
  for(;p<pixels && (reinterpret_cast<uintptr_t>(destination+3*p)&63);++p)scalar_one(table,exceptions,palette,source+3*p,destination+3*p);
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
    const __m256i r0=pack(read_wide(table,exceptions,palette,source+3*p)),r1=pack(read_wide(table,exceptions,palette,source+3*p+24));
    const __m256i r2=pack(read_wide(table,exceptions,palette,source+3*p+48)),r3=pack(read_wide(table,exceptions,palette,source+3*p+72));
    const __m256i r4=pack(read_wide(table,exceptions,palette,source+3*p+96)),r5=pack(read_wide(table,exceptions,palette,source+3*p+120));
    const __m256i r6=pack(read_wide(table,exceptions,palette,source+3*p+144)),r7=pack(read_wide(table,exceptions,palette,source+3*p+168));
    output_four_stream(destination+3*p,r0,r1,r2,r3);output_four_stream(destination+3*p+96,r4,r5,r6,r7);streamed=true;
  }
  // 在普通尾部、调用方读取和OpenMP barrier之前发布非临时写入。
  if(streamed)_mm_sfence();
  for(;p+40<=pixels;p+=32) {
    const __m256i r0=read_wide(table,exceptions,palette,source+3*p),r1=read_wide(table,exceptions,palette,source+3*p+24),r2=read_wide(table,exceptions,palette,source+3*p+48),r3=read_wide(table,exceptions,palette,source+3*p+72);
    output_four(destination+3*p,pack(r0),pack(r1),pack(r2),pack(r3));
  }
  for(;p+8<=pixels;p+=8)output(destination+3*p,read(table,exceptions,palette,source+3*p));
  for(;p<pixels;++p)scalar_one(table,exceptions,palette,source+3*p,destination+3*p);

}
 }
void avx2_chain_wordload(const uint32_t* table,const uint32_t* exceptions,const uint32_t* palette,uint8_t* data,size_t pixels) noexcept {run(table,exceptions,palette,data,data,pixels);}
void avx2_chain_wordload_to(const uint32_t* table,const uint32_t* exceptions,const uint32_t* palette,const uint8_t* source,uint8_t* destination,size_t pixels) noexcept {run(table,exceptions,palette,source,destination,pixels);}
}
