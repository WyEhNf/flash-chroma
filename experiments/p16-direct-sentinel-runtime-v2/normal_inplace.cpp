// 精确热palette与255哨兵：每8lane检查，miss复用原cache整数链。
#include "sentinel_read_avx2.hpp"
#include <immintrin.h>
#include <cstring>
namespace jshc_channel {
namespace {
// 表按R低/G中/B高的输入字节序排列，输出RGB32的字节序保持原样。
inline __attribute__((always_inline)) __m256i read(const DirectSentinelView& context,const uint8_t* table,const uint32_t* palette,const uint8_t* p) {
  uint64_t a,b,c;std::memcpy(&a,p,8);std::memcpy(&b,p+8,8);std::memcpy(&c,p+16,8);
  const uint32_t i0=table[uint32_t(a&0xffffff)],i1=table[uint32_t((a>>24)&0xffffff)];
  const uint32_t i2=table[uint32_t(((a>>48)|(b<<16))&0xffffff)],i3=table[uint32_t((b>>8)&0xffffff)];
  const uint32_t i4=table[uint32_t((b>>32)&0xffffff)],i5=table[uint32_t(((b>>56)|(c<<8))&0xffffff)];
  const uint32_t i6=table[uint32_t((c>>16)&0xffffff)],i7=table[uint32_t(c>>40)];
  if(sentinel_any(i0,i1,i2,i3,i4,i5,i6,i7))return sentinel_slow_eight(context,p);
  return _mm256_setr_epi32(int32_t(palette[i0]),int32_t(palette[i1]),int32_t(palette[i2]),int32_t(palette[i3]),int32_t(palette[i4]),int32_t(palette[i5]),int32_t(palette[i6]),int32_t(palette[i7]));
}
// 仅宽循环调用；最后一个32bit输入读取多出的1字节仍在当前线程块内。
inline __attribute__((always_inline)) __m256i read_wide(const DirectSentinelView& context,const uint8_t* table,const uint32_t* palette,const uint8_t* p) {
  const uint8_t* bytes=table;
  // GNU低对齐可别名类型只描述原有合法4字节输入；不得用于精确24字节尾部。
  typedef uint32_t unaligned_alias_u32 __attribute__((aligned(1),may_alias));
  const uint32_t high_mask=0xff000000u;
  const auto id=[bytes,p,high_mask](size_t offset) {
    // 输出声明覆盖整个地址寄存器；x86-64写%k0会同时清零其高32位。
    uintptr_t code;
    // AT&T源顺序：内存、取反掩码、目标；结果为~high_mask & input32。
    // 精确memory operand与cc描述依赖，不额外阻止四ID组间调度。
    asm("andn %1, %k2, %k0" : "=r"(code)
        : "m"(*reinterpret_cast<const unaligned_alias_u32*>(p+offset)),"r"(high_mask) : "cc");
    return bytes[code];
  };
  const uint32_t i0=id(0),i1=id(3),i2=id(6),i3=id(9);
  asm volatile("" : : "r"(i0),"r"(i1),"r"(i2),"r"(i3) : "memory");
  const __m128i lo=_mm_setr_epi32(int32_t(palette[i0]),int32_t(palette[i1]),
      int32_t(palette[i2]),int32_t(palette[i3]));
  const uint32_t i4=id(12),i5=id(15),i6=id(18),i7=id(21);
  asm volatile("" : : "r"(i4),"r"(i5),"r"(i6),"r"(i7) : "memory");
  if(sentinel_any(i0,i1,i2,i3,i4,i5,i6,i7))return sentinel_slow_eight(context,p);
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
// 保留既有预排与三条合并；本副本的stream命名沿用原函数，但存储已为普通对齐写。
inline __attribute__((always_inline)) void output_four_stream(uint8_t* p,__m256i v0,__m256i v1,__m256i v2,__m256i v3) {
  const __m256i s0=_mm256_blend_epi32(v0,v1,0xc0);
  const __m256i s1=_mm256_permute2x128_si256(v1,v2,0x30);
  const __m256i s2=_mm256_blend_epi32(v3,v2,0x03);
  _mm256_store_si256(reinterpret_cast<__m256i*>(p),s0);
  _mm256_store_si256(reinterpret_cast<__m256i*>(p+32),s1);
  _mm256_store_si256(reinterpret_cast<__m256i*>(p+64),s2);
}
inline __attribute__((always_inline)) void scalar_one(const DirectSentinelView& context,const uint8_t* table,const uint32_t* palette,const uint8_t* source,uint8_t* destination) {
  sentinel_scalar_one(context,table,palette,source,destination);
}
inline __attribute__((always_inline)) void run(const DirectSentinelView& context,const uint8_t* table,const uint32_t* palette,const uint8_t* source,uint8_t* destination,size_t pixels) noexcept {
  size_t p=0;
  // 初始窗口只形成有效输入范围内的地址；T0为提示，CPU可以忽略。
  const size_t initial=pixels*3<1024?pixels*3:1024;
  for(size_t offset=0;offset<initial;offset+=64)_mm_prefetch(reinterpret_cast<const char*>(source+offset),_MM_HINT_T0);
  // 保持原64字节目标对齐，六个普通32字节写恰好覆盖三个完整缓存行。
  for(;p<pixels && (reinterpret_cast<uintptr_t>(destination+3*p)&63);++p)scalar_one(context,table,palette,source+3*p,destination+3*p);
  for(;p+72<=pixels;p+=64) {
    // 固定16缓存行前瞻；四个地址覆盖未来192字节，包括非对齐源末行。
    if(p+406<=pixels) {
      const uint8_t* future=source+3*p+1024;
      _mm_prefetch(reinterpret_cast<const char*>(future),_MM_HINT_T0);
      _mm_prefetch(reinterpret_cast<const char*>(future+64),_MM_HINT_T0);
      _mm_prefetch(reinterpret_cast<const char*>(future+128),_MM_HINT_T0);
      _mm_prefetch(reinterpret_cast<const char*>(future+191),_MM_HINT_T0);
    }
    // 全部64像素先读后写，主体输出恰好192字节即三条完整缓存行。
    const __m256i r0=pack_stream_0(read_wide(context,table,palette,source+3*p)),r1=pack_stream_1(read_wide(context,table,palette,source+3*p+24));
    const __m256i r2=pack_stream_2(read_wide(context,table,palette,source+3*p+48)),r3=pack_stream_3(read_wide(context,table,palette,source+3*p+72));
    const __m256i r4=pack_stream_0(read_wide(context,table,palette,source+3*p+96)),r5=pack_stream_1(read_wide(context,table,palette,source+3*p+120));
    const __m256i r6=pack_stream_2(read_wide(context,table,palette,source+3*p+144)),r7=pack_stream_3(read_wide(context,table,palette,source+3*p+168));
    output_four_stream(destination+3*p,r0,r1,r2,r3);output_four_stream(destination+3*p+96,r4,r5,r6,r7);
  }
  // 此独立路径只有普通写，没有NT发布需要；原pair48路径仍保留自己的SFENCE。
  for(;p+40<=pixels;p+=32) {
    const __m256i r0=read_wide(context,table,palette,source+3*p),r1=read_wide(context,table,palette,source+3*p+24),r2=read_wide(context,table,palette,source+3*p+48),r3=read_wide(context,table,palette,source+3*p+72);
    output_four(destination+3*p,pack(r0),pack(r1),pack(r2),pack(r3));
  }
  for(;p+8<=pixels;p+=8)output(destination+3*p,read(context,table,palette,source+3*p));
  for(;p<pixels;++p)scalar_one(context,table,palette,source+3*p,destination+3*p);

}
 }
void avx2_direct_sentinel_normal_mt(const DirectSentinelView& context,const uint8_t* table,const uint32_t* palette,uint8_t* data,size_t pixels) noexcept {run(context,table,palette,data,data,pixels);}
}
