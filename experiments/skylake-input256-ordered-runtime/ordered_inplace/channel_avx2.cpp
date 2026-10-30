// 精确全域字节索引：四包独立读取先行，按RGB24读取合法对齐词。
#include "../suffix_cache.hpp"
#include <immintrin.h>
#include <cstring>
namespace jshc_channel {
namespace {
// 表按R低/G中/B高的输入字节序排列，输出RGB32的字节序保持原样。
inline __attribute__((always_inline)) __m256i read(const uint32_t* table,const uint32_t* palette,const uint8_t* p) {
  uint64_t a,b,c;std::memcpy(&a,p,8);std::memcpy(&b,p+8,8);std::memcpy(&c,p+16,8);
  const auto value=[table,palette](uint32_t code) {return int32_t(palette[reinterpret_cast<const uint8_t*>(table)[code]]);};
  return _mm256_setr_epi32(value(uint32_t(a&0xffffff)),value(uint32_t((a>>24)&0xffffff)),
      value(uint32_t(((a>>48)|(b<<16))&0xffffff)),value(uint32_t((b>>8)&0xffffff)),
      value(uint32_t((b>>32)&0xffffff)),value(uint32_t(((b>>56)|(c<<8))&0xffffff)),
      value(uint32_t((c>>16)&0xffffff)),value(uint32_t(c>>40)));
}
// 仅宽循环调用；32字节载荷由原p+72/p+40窗口保护，精确24字节尾部不调用此函数。
inline __attribute__((always_inline)) __m256i read_wide(const uint32_t* table,const uint32_t* palette,const uint8_t* p) {
  const uint8_t* bytes=reinterpret_cast<const uint8_t*>(table);
  const __m256i raw=_mm256_loadu_si256(reinterpret_cast<const __m256i*>(p));
  const __m256i lanes=_mm256_permutevar8x32_epi32(raw,_mm256_setr_epi32(0,1,2,3,3,4,5,6));
  const __m256i code=_mm256_shuffle_epi8(lanes,
      _mm256_setr_epi8(0,1,2,-1,3,4,5,-1,6,7,8,-1,9,10,11,-1,0,1,2,-1,3,4,5,-1,6,7,8,-1,9,10,11,-1));
  // 低半对应RGB字节0..11；四个精确u8 ID到齐后才读取调色板。
  const __m128i low=_mm256_castsi256_si128(code);
  const uint32_t i0=bytes[uint32_t(_mm_extract_epi32(low,0))],i1=bytes[uint32_t(_mm_extract_epi32(low,1))];
  const uint32_t i2=bytes[uint32_t(_mm_extract_epi32(low,2))],i3=bytes[uint32_t(_mm_extract_epi32(low,3))];
  asm volatile("" : : "r"(i0),"r"(i1),"r"(i2),"r"(i3) : "memory");
  const __m128i lo=_mm_setr_epi32(int32_t(palette[i0]),int32_t(palette[i1]),
      int32_t(palette[i2]),int32_t(palette[i3]));
  // 高半由原字节12..27组成，只消费12..23；后四ID保持同样屏障。
  const __m128i high=_mm256_extracti128_si256(code,1);
  const uint32_t i4=bytes[uint32_t(_mm_extract_epi32(high,0))],i5=bytes[uint32_t(_mm_extract_epi32(high,1))];
  const uint32_t i6=bytes[uint32_t(_mm_extract_epi32(high,2))],i7=bytes[uint32_t(_mm_extract_epi32(high,3))];
  asm volatile("" : : "r"(i4),"r"(i5),"r"(i6),"r"(i7) : "memory");
  const __m128i hi=_mm_setr_epi32(int32_t(palette[i4]),int32_t(palette[i5]),
      int32_t(palette[i6]),int32_t(palette[i7]));
  return _mm256_inserti128_si256(_mm256_castsi128_si256(lo),hi,1);
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
// 按最终输出位置预排qword，普通尾部继续使用原pack。
inline __attribute__((always_inline)) __m256i pack_stream_0(__m256i value) {
  const __m256i bytes=_mm256_shuffle_epi8(value,_mm256_setr_epi8(0,1,2,4,5,6,8,9,10,12,13,14,-1,-1,-1,-1,0,1,2,4,5,6,8,9,10,12,13,14,-1,-1,-1,-1));
  return _mm256_permutevar8x32_epi32(bytes,_mm256_setr_epi32(0,1,2,4,5,6,3,7));
}
inline __attribute__((always_inline)) __m256i pack_stream_1(__m256i value) {
  const __m256i bytes=_mm256_shuffle_epi8(value,_mm256_setr_epi8(0,1,2,4,5,6,8,9,10,12,13,14,-1,-1,-1,-1,0,1,2,4,5,6,8,9,10,12,13,14,-1,-1,-1,-1));
  return _mm256_permutevar8x32_epi32(bytes,_mm256_setr_epi32(2,4,5,6,3,7,0,1));
}
inline __attribute__((always_inline)) __m256i pack_stream_2(__m256i value) {
  const __m256i bytes=_mm256_shuffle_epi8(value,_mm256_setr_epi8(0,1,2,4,5,6,8,9,10,12,13,14,-1,-1,-1,-1,0,1,2,4,5,6,8,9,10,12,13,14,-1,-1,-1,-1));
  return _mm256_permutevar8x32_epi32(bytes,_mm256_setr_epi32(5,6,3,7,0,1,2,4));
}
inline __attribute__((always_inline)) __m256i pack_stream_3(__m256i value) {
  const __m256i bytes=_mm256_shuffle_epi8(value,_mm256_setr_epi8(0,1,2,4,5,6,8,9,10,12,13,14,-1,-1,-1,-1,0,1,2,4,5,6,8,9,10,12,13,14,-1,-1,-1,-1));
  return _mm256_permutevar8x32_epi32(bytes,_mm256_setr_epi32(3,7,0,1,2,4,5,6));
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
  const __m256i s0=_mm256_blend_epi32(v0,v1,0xc0);
  const __m256i s1=_mm256_permute2x128_si256(v1,v2,0x30);
  const __m256i s2=_mm256_blend_epi32(v3,v2,0x03);
  _mm256_stream_si256(reinterpret_cast<__m256i*>(p),s0);
  _mm256_stream_si256(reinterpret_cast<__m256i*>(p+32),s1);
  _mm256_stream_si256(reinterpret_cast<__m256i*>(p+64),s2);
}
inline __attribute__((always_inline)) void scalar_one(const uint32_t* table,const uint32_t* palette,const uint8_t* source,uint8_t* destination) {
  const uint32_t code=uint32_t(source[0])|(uint32_t(source[1])<<8)|(uint32_t(source[2])<<16);
  const uint32_t value=palette[reinterpret_cast<const uint8_t*>(table)[code]];
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
    // 前32像素全部读完后只写首64B整行；其余32B留在pending，不提前写中间行。
    const __m256i r0=pack_stream_0(read_wide(table,palette,source+3*p)),r1=pack_stream_1(read_wide(table,palette,source+3*p+24));
    const __m256i r2=pack_stream_2(read_wide(table,palette,source+3*p+48)),r3=pack_stream_3(read_wide(table,palette,source+3*p+72));
    const __m256i s0=_mm256_blend_epi32(r0,r1,0xc0);
    const __m256i s1=_mm256_permute2x128_si256(r1,r2,0x30);
    const __m256i pending=_mm256_blend_epi32(r3,r2,0x03);
    // 三个最终输出值先就绪；四ID屏障仍只约束各组查表，不代替此输出生命期边界。
    asm volatile("" : : "x"(s0),"x"(s1),"x"(pending) : "memory");
    _mm256_stream_si256(reinterpret_cast<__m256i*>(destination+3*p),s0);
    _mm256_stream_si256(reinterpret_cast<__m256i*>(destination+3*p+32),s1);
    // 阻止第二组输入被编译器前移到首行两次NT之间；这不是硬件栅栏。
    asm volatile("" : : : "memory");
    // 第二组源从96B开始，不读取已写首行；全部读取后补写中间行，再完成末行。
    const __m256i r4=pack_stream_0(read_wide(table,palette,source+3*p+96)),r5=pack_stream_1(read_wide(table,palette,source+3*p+120));
    const __m256i r6=pack_stream_2(read_wide(table,palette,source+3*p+144)),r7=pack_stream_3(read_wide(table,palette,source+3*p+168));
    _mm256_stream_si256(reinterpret_cast<__m256i*>(destination+3*p+64),pending);
    output_four_stream(destination+3*p+96,r4,r5,r6,r7);streamed=true;
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
void avx2_chain_input256_ordered_mt(const uint32_t* table,const uint32_t* palette,uint8_t* data,size_t pixels) noexcept {run(table,palette,data,data,pixels);}
}
