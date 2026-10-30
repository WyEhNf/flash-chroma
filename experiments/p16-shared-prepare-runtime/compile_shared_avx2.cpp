// 仅prepare按共享坐标分派；复用已存在的两种精确整数transform。
#include "../skylake-domain-isolated-runtime/channel_avx2.cpp"
#include <cstring>
namespace jshc_channel {
namespace {
template<bool Shared>
void compile_direct(const View* chain,const SuffixCacheView& cache,
    const uint32_t* ids,uint8_t* destination,size_t begin,size_t pixels) noexcept {
  const __m256i mask=_mm256_set1_epi32(255);
  const __m256i shuffle=_mm256_setr_epi8(0,4,8,12,-1,-1,-1,-1,-1,-1,-1,-1,-1,-1,-1,-1,
      0,4,8,12,-1,-1,-1,-1,-1,-1,-1,-1,-1,-1,-1,-1);
  for(size_t p=0;p<pixels;p+=8) {
    const __m256i address=_mm256_add_epi32(_mm256_set1_epi32(int(begin+p)),
        _mm256_setr_epi32(0,1,2,3,4,5,6,7));
    Rgb rgb;
    rgb.r=_mm256_and_si256(address,mask);
    rgb.g=_mm256_and_si256(_mm256_srli_epi32(address,8),mask);
    rgb.b=_mm256_srli_epi32(address,16);
    transform<Shared>(chain[0],rgb);
    const __m256i dg=_mm256_sub_epi32(rgb.g,rgb.r),db=_mm256_sub_epi32(rgb.b,rgb.r);
    const __m256i index=_mm256_add_epi32(
        _mm256_mullo_epi32(_mm256_sub_epi32(rgb.r,_mm256_set1_epi32(cache.r_min)),_mm256_set1_epi32(cache.width_g*cache.width_b)),
        _mm256_add_epi32(_mm256_mullo_epi32(_mm256_sub_epi32(dg,_mm256_set1_epi32(cache.dg_min)),_mm256_set1_epi32(cache.width_b)),
            _mm256_sub_epi32(db,_mm256_set1_epi32(cache.db_min))));
    const __m256i packed=_mm256_shuffle_epi8(gather(ids,index),shuffle);
    const uint64_t lo=uint32_t(_mm_cvtsi128_si32(_mm256_castsi256_si128(packed)));
    const uint64_t hi=uint32_t(_mm_cvtsi128_si32(_mm256_extracti128_si256(packed,1)));
    const uint64_t word=lo|(hi<<32);
    std::memcpy(destination+p,&word,sizeof(word));
  }
}
}
void avx2_compile_direct(const View* chain,const SuffixCacheView& cache,
    const uint32_t* ids,uint8_t* destination,size_t begin,size_t pixels) noexcept {
  // 分派在每个65536像素批入口，只读构造时已验证的共享标志。
  if(chain[0].shared)compile_direct<true>(chain,cache,ids,destination,begin,pixels);
  else compile_direct<false>(chain,cache,ids,destination,begin,pixels);
}
}
