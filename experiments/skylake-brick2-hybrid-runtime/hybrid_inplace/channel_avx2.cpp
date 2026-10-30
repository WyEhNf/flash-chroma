// 正常2³输入块直接恢复RGB，异常八像素包回退原精确字节索引。
#include "../suffix_cache.hpp"
#include <immintrin.h>
namespace jshc_channel {
namespace {
inline __attribute__((always_inline)) __m256i input24(const uint8_t* p) {
  const __m128i head=_mm_loadu_si128(reinterpret_cast<const __m128i*>(p));
  const __m128i tail=_mm_loadl_epi64(reinterpret_cast<const __m128i*>(p+16));
  const __m128i high=_mm_alignr_epi8(tail,head,12);
  const __m256i packed=_mm256_inserti128_si256(_mm256_castsi128_si256(head),high,1);
  return _mm256_shuffle_epi8(packed,_mm256_setr_epi8(
      0,1,2,-1,3,4,5,-1,6,7,8,-1,9,10,11,-1,
      0,1,2,-1,3,4,5,-1,6,7,8,-1,9,10,11,-1));
}
inline __attribute__((always_inline)) __m256i read4(const uint64_t* table,__m128i q) {
  return _mm256_setr_epi64x(table[uint32_t(_mm_extract_epi32(q,0))],
      table[uint32_t(_mm_extract_epi32(q,1))],table[uint32_t(_mm_extract_epi32(q,2))],
      table[uint32_t(_mm_extract_epi32(q,3))]);
}
inline __attribute__((always_inline)) __m256i even32(__m256i a,__m256i b) {
  const __m256i permutation=_mm256_setr_epi32(0,2,4,6,0,2,4,6);
  const __m128i low=_mm256_castsi256_si128(_mm256_permutevar8x32_epi32(a,permutation));
  const __m128i high=_mm256_castsi256_si128(_mm256_permutevar8x32_epi32(b,permutation));
  return _mm256_inserti128_si256(_mm256_castsi128_si256(low),high,1);
}
inline __attribute__((always_inline)) __m256i exact8(const uint32_t* direct,const uint32_t* palette,__m256i code) {
  const uint8_t* bytes=reinterpret_cast<const uint8_t*>(direct);
  const __m128i low=_mm256_castsi256_si128(code),high=_mm256_extracti128_si256(code,1);
  const uint32_t i0=bytes[uint32_t(_mm_extract_epi32(low,0))],i1=bytes[uint32_t(_mm_extract_epi32(low,1))];
  const uint32_t i2=bytes[uint32_t(_mm_extract_epi32(low,2))],i3=bytes[uint32_t(_mm_extract_epi32(low,3))];
  asm volatile("" : : "r"(i0),"r"(i1),"r"(i2),"r"(i3) : "memory");
  const __m128i a=_mm_setr_epi32(palette[i0],palette[i1],palette[i2],palette[i3]);
  const uint32_t i4=bytes[uint32_t(_mm_extract_epi32(high,0))],i5=bytes[uint32_t(_mm_extract_epi32(high,1))];
  const uint32_t i6=bytes[uint32_t(_mm_extract_epi32(high,2))],i7=bytes[uint32_t(_mm_extract_epi32(high,3))];
  asm volatile("" : : "r"(i4),"r"(i5),"r"(i6),"r"(i7) : "memory");
  const __m128i b=_mm_setr_epi32(palette[i4],palette[i5],palette[i6],palette[i7]);
  return _mm256_inserti128_si256(_mm256_castsi128_si256(a),b,1);
}
inline __attribute__((always_inline)) void output24(uint8_t* p,__m256i value) {
  const __m256i bytes=_mm256_shuffle_epi8(value,_mm256_setr_epi8(
      0,1,2,4,5,6,8,9,10,12,13,14,-1,-1,-1,-1,
      0,1,2,4,5,6,8,9,10,12,13,14,-1,-1,-1,-1));
  const __m128i lo=_mm256_castsi256_si128(bytes),hi=_mm256_extracti128_si256(bytes,1);
  _mm_storeu_si128(reinterpret_cast<__m128i*>(p),_mm_or_si128(lo,_mm_slli_si128(hi,12)));
  _mm_storel_epi64(reinterpret_cast<__m128i*>(p+16),_mm_srli_si128(hi,4));
}
}
void avx2_chain_brick2_hybrid(const uint64_t* words,const uint32_t* direct,const uint32_t* palette,
                            int32_t minDG,int32_t minDB,uint8_t* data,size_t pixels) noexcept {
  // 最终RGB各通道已由构造器证明有效；有符号偏置以32位模加法恢复。
  const __m256i bias=_mm256_set1_epi32(minDG*256+minDB*65536);
  size_t p=0;
  for(;p+8<=pixels;p+=8) {
    const __m256i code=input24(data+3*p);
    const __m256i q=_mm256_or_si256(_mm256_or_si256(
        _mm256_and_si256(_mm256_srli_epi32(code,1),_mm256_set1_epi32(0x7f)),
        _mm256_and_si256(_mm256_srli_epi32(code,2),_mm256_set1_epi32(0x3f80))),
        _mm256_and_si256(_mm256_srli_epi32(code,3),_mm256_set1_epi32(0x1fc000)));
    const __m256i a=read4(words,_mm256_castsi256_si128(q));
    const __m256i b=read4(words,_mm256_extracti128_si256(q,1));
    __m256i value;
    if(_mm256_movemask_pd(_mm256_castsi256_pd(_mm256_or_si256(a,b)))) {
      value=exact8(direct,palette,code);
    } else {
      const __m256i lowbits=_mm256_and_si256(code,_mm256_set1_epi32(0x010101));
      const __m256i weighted=_mm256_maddubs_epi16(lowbits,_mm256_set1_epi32(0x00180c06));
      const __m256i shifts=_mm256_add_epi32(_mm256_madd_epi16(weighted,_mm256_set1_epi16(1)),_mm256_set1_epi32(15));
      const __m256i ca=_mm256_srlv_epi64(a,_mm256_cvtepu32_epi64(_mm256_castsi256_si128(shifts)));
      const __m256i cb=_mm256_srlv_epi64(b,_mm256_cvtepu32_epi64(_mm256_extracti128_si256(shifts,1)));
      const __m256i h=even32(a,b),c=even32(ca,cb);
      const __m256i red=_mm256_add_epi32(_mm256_and_si256(h,_mm256_set1_epi32(255)),_mm256_and_si256(c,_mm256_set1_epi32(7)));
      const __m256i gray=_mm256_shuffle_epi8(red,_mm256_setr_epi8(
          0,0,0,-1,4,4,4,-1,8,8,8,-1,12,12,12,-1,
          0,0,0,-1,4,4,4,-1,8,8,8,-1,12,12,12,-1));
      const __m256i dg=_mm256_add_epi32(_mm256_and_si256(h,_mm256_set1_epi32(0xf00)),
          _mm256_slli_epi32(_mm256_and_si256(c,_mm256_set1_epi32(24)),5));
      const __m256i db=_mm256_add_epi32(_mm256_slli_epi32(_mm256_and_si256(h,_mm256_set1_epi32(0x7000)),4),
          _mm256_slli_epi32(_mm256_and_si256(c,_mm256_set1_epi32(32)),11));
      value=_mm256_add_epi32(_mm256_add_epi32(gray,bias),_mm256_add_epi32(dg,db));
    }
    output24(data+3*p,value);
  }
  for(;p<pixels;++p) {
    uint8_t* at=data+3*p;
    const uint32_t code=uint32_t(at[0])|(uint32_t(at[1])<<8)|(uint32_t(at[2])<<16);
    const uint32_t value=palette[reinterpret_cast<const uint8_t*>(direct)[code]];
    at[0]=uint8_t(value);at[1]=uint8_t(value>>8);at[2]=uint8_t(value>>16);
  }
}
}
