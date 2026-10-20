// 精确全域字节索引：四包独立读取先行，按RGB24读取合法对齐词。
#include "suffix_cache.hpp"
#include <immintrin.h>
#include <cstring>
namespace jshc_channel {
namespace {
// 精确读取24字节输入；八个独立字节ID与RGB32载荷，不使用硬件gather。
inline __attribute__((always_inline)) __m256i read(const uint32_t* table,const uint32_t* palette,const uint8_t* p) {
  uint64_t a,b,c;std::memcpy(&a,p,8);std::memcpy(&b,p+8,8);std::memcpy(&c,p+16,8);
  a=__builtin_bswap64(a);b=__builtin_bswap64(b);c=__builtin_bswap64(c);
  const auto value=[table,palette](uint32_t code) {return int32_t(palette[reinterpret_cast<const uint8_t*>(table)[code]]);};
  return _mm256_setr_epi32(value(uint32_t(a>>40)),value(uint32_t((a>>16)&0xffffff)),
      value(uint32_t(((a&0xffff)<<8)|(b>>56))),value(uint32_t((b>>32)&0xffffff)),
      value(uint32_t((b>>8)&0xffffff)),value(uint32_t(((b&255)<<16)|(c>>48))),
      value(uint32_t((c>>24)&0xffffff)),value(uint32_t(c&0xffffff)));
}
inline __attribute__((always_inline)) void output(uint8_t* p,__m256i value) {
  const __m256i bytes=_mm256_shuffle_epi8(value,_mm256_setr_epi8(0,1,2,4,5,6,8,9,10,12,13,14,-1,-1,-1,-1,0,1,2,4,5,6,8,9,10,12,13,14,-1,-1,-1,-1));
  const __m128i lo=_mm256_castsi256_si128(bytes),hi=_mm256_extracti128_si256(bytes,1);
  _mm_storeu_si128(reinterpret_cast<__m128i*>(p),_mm_or_si128(lo,_mm_slli_si128(hi,12)));
  _mm_storel_epi64(reinterpret_cast<__m128i*>(p+16),_mm_srli_si128(hi,4));
}
}
namespace {
inline __attribute__((always_inline)) void run(const uint32_t* table,const uint32_t* palette,const uint8_t* source,uint8_t* destination,size_t pixels) noexcept {
  size_t p=0;
  for(;p+32<=pixels;p+=32) {
    const __m256i r0=read(table,palette,source+3*p),r1=read(table,palette,source+3*p+24),r2=read(table,palette,source+3*p+48),r3=read(table,palette,source+3*p+72);
    output(destination+3*p,r0);output(destination+3*p+24,r1);output(destination+3*p+48,r2);output(destination+3*p+72,r3);
  }
  for(;p<pixels;p+=8) {output(destination+3*p,read(table,palette,source+3*p));}
}
 }
void avx2_chain_loadindex(const uint32_t* table,const uint32_t* palette,uint8_t* data,size_t pixels) noexcept {run(table,palette,data,data,pixels);}
void avx2_chain_loadindex_to(const uint32_t* table,const uint32_t* palette,const uint8_t* source,uint8_t* destination,size_t pixels) noexcept {run(table,palette,source,destination,pixels);}
}
