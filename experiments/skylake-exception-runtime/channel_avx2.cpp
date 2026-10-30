// 修订23：原3bit块不变，例外块使用精确8bit ID池，混合包只增加一次gather。
#include "suffix_cache.hpp"
#include <immintrin.h>
namespace jshc_channel {
namespace {
inline __attribute__((always_inline)) __m256i gather(const uint32_t* data,__m256i index) {
  return _mm256_i32gather_epi32(reinterpret_cast<const int*>(data),index,4);
}
}
void avx2_chain_exception(const uint32_t* blocks,const uint32_t* exceptions,const uint32_t* palette,
    uint8_t* data,size_t pixels) noexcept {
  const __m256i input_shuffle=_mm256_setr_epi8(2,1,0,-1,5,4,3,-1,8,7,6,-1,11,10,9,-1,2,1,0,-1,5,4,3,-1,8,7,6,-1,11,10,9,-1);
  const __m256i output_shuffle=_mm256_setr_epi8(0,1,2,4,5,6,8,9,10,12,13,14,-1,-1,-1,-1,0,1,2,4,5,6,8,9,10,12,13,14,-1,-1,-1,-1);
  const __m256i mask255=_mm256_set1_epi32(255);
  for(size_t p=0;p<pixels;p+=8) {
    uint8_t* dst=data+3*p;
    const __m128i lo=_mm_loadu_si128(reinterpret_cast<const __m128i*>(dst));
    const __m128i last=_mm_loadl_epi64(reinterpret_cast<const __m128i*>(dst+16));
    const __m128i hi=_mm_alignr_epi8(last,lo,12);
    const __m256i raw=_mm256_inserti128_si256(_mm256_castsi128_si256(lo),hi,1);
    const __m256i code=_mm256_shuffle_epi8(raw,input_shuffle);
    const __m256i words=gather(blocks,_mm256_srli_epi32(code,3));
    const __m256i base=_mm256_and_si256(words,mask255);
    const __m256i offset=_mm256_and_si256(code,_mm256_set1_epi32(7));
    const __m256i shift=_mm256_add_epi32(_mm256_add_epi32(offset,_mm256_slli_epi32(offset,1)),_mm256_set1_epi32(8));
    __m256i ids=_mm256_add_epi32(base,_mm256_and_si256(_mm256_srlv_epi32(words,shift),_mm256_set1_epi32(7)));
    const __m256i exceptional=_mm256_cmpeq_epi32(base,mask255);
    if(_mm256_movemask_epi8(exceptional)) {
      // 非例外lane只读两个零词，不使用主块载荷构造任意例外地址。
      const __m256i index=_mm256_add_epi32(_mm256_and_si256(_mm256_srli_epi32(words,8),exceptional),
          _mm256_and_si256(_mm256_srli_epi32(code,2),_mm256_set1_epi32(1)));
      const __m256i packed=gather(exceptions,index);
      const __m256i byte_shift=_mm256_slli_epi32(_mm256_and_si256(code,_mm256_set1_epi32(3)),3);
      const __m256i exact=_mm256_and_si256(_mm256_srlv_epi32(packed,byte_shift),mask255);
      ids=_mm256_blendv_epi8(ids,exact,exceptional);
    }
    const __m256i value=gather(palette,ids);
    const __m256i bytes=_mm256_shuffle_epi8(value,output_shuffle);
    const __m128i bottom=_mm256_castsi256_si128(bytes),top=_mm256_extracti128_si256(bytes,1);
    _mm_storeu_si128(reinterpret_cast<__m128i*>(dst),_mm_or_si128(bottom,_mm_slli_si128(top,12)));
    _mm_storel_epi64(reinterpret_cast<__m128i*>(dst+16),_mm_srli_si128(top,4));
  }
}
}
