// 精确16bit输出编码：R占8bit，G-R和B-R相对各自最小值分别占4bit。
#include "suffix_cache.hpp"
#include <immintrin.h>
#include <cstring>
namespace jshc_channel {
namespace {
// 三个精确8字节输入读取，展开八个独立16bit载荷；不读取输入尾部之外。
inline __attribute__((always_inline)) __m256i read(const uint32_t* table,const uint8_t* p) {
  uint64_t a,b,c;std::memcpy(&a,p,8);std::memcpy(&b,p+8,8);std::memcpy(&c,p+16,8);
  a=__builtin_bswap64(a);b=__builtin_bswap64(b);c=__builtin_bswap64(c);
  const auto value=[table](uint32_t code) {uint16_t v;std::memcpy(&v,reinterpret_cast<const uint8_t*>(table)+2*size_t(code),2);return int32_t(v);};
  return _mm256_setr_epi32(value(uint32_t(a>>40)),value(uint32_t((a>>16)&0xffffff)),
      value(uint32_t(((a&0xffff)<<8)|(b>>56))),value(uint32_t((b>>32)&0xffffff)),
      value(uint32_t((b>>8)&0xffffff)),value(uint32_t(((b&255)<<16)|(c>>48))),
      value(uint32_t((c>>24)&0xffffff)),value(uint32_t(c&0xffffff)));
}
inline __attribute__((always_inline)) void output(uint8_t* p,__m256i packed,__m256i dg,__m256i db) {
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
namespace {
inline __attribute__((always_inline)) void run(const uint32_t* table,int32_t dg_min,int32_t db_min,const uint8_t* source,uint8_t* destination,size_t pixels) noexcept {
  const __m256i dg=_mm256_set1_epi32(dg_min),db=_mm256_set1_epi32(db_min);size_t p=0;
  for(;p+32<=pixels;p+=32) {
    const __m256i w0=read(table,source+3*p),w1=read(table,source+3*p+24),w2=read(table,source+3*p+48),w3=read(table,source+3*p+72);
    output(destination+3*p,w0,dg,db);output(destination+3*p+24,w1,dg,db);output(destination+3*p+48,w2,dg,db);output(destination+3*p+72,w3,dg,db);
  }
  for(;p<pixels;p+=8) {output(destination+3*p,read(table,source+3*p),dg,db);}
}
}
void avx2_chain_load16(const uint32_t* table,int32_t dg,int32_t db,uint8_t* data,size_t pixels) noexcept {run(table,dg,db,data,data,pixels);}
void avx2_chain_load16_to(const uint32_t* table,int32_t dg,int32_t db,const uint8_t* source,uint8_t* destination,size_t pixels) noexcept {run(table,dg,db,source,destination,pixels);}
}
