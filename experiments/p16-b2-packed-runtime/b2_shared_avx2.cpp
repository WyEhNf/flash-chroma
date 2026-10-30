// 99只改变shared已证域首级节点/轴布局，原97/checked/direct TU保持独立。
#include "suffix_cache.hpp"
#include <immintrin.h>
namespace jshc_channel {
namespace {
struct B2Rgb {__m256i r,g,b;};
inline __attribute__((always_inline)) __m256i b2_gather(const uint32_t* p,const __m256i& i) {
  return _mm256_i32gather_epi32(reinterpret_cast<const int*>(p),i,4);
}
inline __attribute__((always_inline)) void b2_load(const uint8_t* p,B2Rgb& rgb) {
  const __m128i lo=_mm_loadu_si128(reinterpret_cast<const __m128i*>(p));
  const __m128i last=_mm_loadl_epi64(reinterpret_cast<const __m128i*>(p+16));
  const __m128i hi=_mm_alignr_epi8(last,lo,12);
  const __m256i raw=_mm256_inserti128_si256(_mm256_castsi128_si256(lo),hi,1);
  const __m256i shuffle=_mm256_setr_epi8(0,1,2,-1,3,4,5,-1,6,7,8,-1,9,10,11,-1,0,1,2,-1,3,4,5,-1,6,7,8,-1,9,10,11,-1);
  const __m256i packed=_mm256_shuffle_epi8(raw,shuffle),mask=_mm256_set1_epi32(255);
  rgb.r=_mm256_and_si256(packed,mask);rgb.g=_mm256_and_si256(_mm256_srli_epi32(packed,8),mask);rgb.b=_mm256_srli_epi32(packed,16);
}
inline __attribute__((always_inline)) void b2_store(uint8_t* p,const B2Rgb& rgb) {
  const __m256i packed=_mm256_or_si256(rgb.r,_mm256_or_si256(_mm256_slli_epi32(rgb.g,8),_mm256_slli_epi32(rgb.b,16)));
  const __m256i shuffle=_mm256_setr_epi8(0,1,2,4,5,6,8,9,10,12,13,14,-1,-1,-1,-1,0,1,2,4,5,6,8,9,10,12,13,14,-1,-1,-1,-1);
  const __m256i bytes=_mm256_shuffle_epi8(packed,shuffle);
  const __m128i lo=_mm256_castsi256_si128(bytes),hi=_mm256_extracti128_si256(bytes,1);
  _mm_storeu_si128(reinterpret_cast<__m128i*>(p),_mm_or_si128(lo,_mm_slli_si128(hi,12)));
  _mm_storel_epi64(reinterpret_cast<__m128i*>(p+16),_mm_srli_si128(hi,4));
}
template<int C>
inline __attribute__((always_inline)) __m256i b2_interpolate(const __m256i& v0,const __m256i& v1,const __m256i& v2,const __m256i& v3,
    const __m256i& high,const __m256i& middle,const __m256i& low) {
  const __m256i mask=_mm256_set1_epi32(255);
  const __m256i n0=_mm256_and_si256(_mm256_srli_epi32(v0,8*C),mask),n1=_mm256_and_si256(_mm256_srli_epi32(v1,8*C),mask);
  const __m256i n2=_mm256_and_si256(_mm256_srli_epi32(v2,8*C),mask),n3=_mm256_and_si256(_mm256_srli_epi32(v3,8*C),mask);
  const __m256i acc=_mm256_add_epi32(_mm256_slli_epi32(n0,16),_mm256_add_epi32(
      _mm256_mullo_epi32(_mm256_sub_epi32(n1,n0),high),_mm256_add_epi32(
          _mm256_mullo_epi32(_mm256_sub_epi32(n2,n1),middle),_mm256_mullo_epi32(_mm256_sub_epi32(n3,n2),low))));
  return _mm256_srli_epi32(_mm256_add_epi32(acc,_mm256_set1_epi32(32768)),16);
}
inline __attribute__((always_inline)) void b2_transform(const uint32_t* axes,const uint32_t* nodes,B2Rgb& rgb) {
  const __m256i ar=b2_gather(axes,rgb.r),ag=b2_gather(axes+256,rgb.g),ab=b2_gather(axes+512,rgb.b);
  const __m256i cr=_mm256_srli_epi32(ar,16),cg=_mm256_srli_epi32(ag,16),cb=_mm256_srli_epi32(ab,16);
  const __m256i base=_mm256_add_epi32(cr,_mm256_add_epi32(cg,cb));
  const __m256i mask=_mm256_set1_epi32(65535);
  const __m256i x=_mm256_and_si256(ar,mask),y=_mm256_and_si256(ag,mask),z=_mm256_and_si256(ab,mask);
  const __m256i zero=_mm256_setzero_si256();
  const __m256i dr=_mm256_blendv_epi8(_mm256_set1_epi32(4),_mm256_set1_epi32(2308),
      _mm256_cmpgt_epi32(_mm256_and_si256(cr,_mm256_set1_epi32(4)),zero));
  const __m256i dg=_mm256_blendv_epi8(_mm256_set1_epi32(2),_mm256_set1_epi32(134),
      _mm256_cmpgt_epi32(_mm256_and_si256(cg,_mm256_set1_epi32(2)),zero));
  const __m256i db=_mm256_blendv_epi8(_mm256_set1_epi32(1),_mm256_set1_epi32(7),
      _mm256_cmpgt_epi32(_mm256_and_si256(cb,_mm256_set1_epi32(1)),zero));
  __m256i first=_mm256_blendv_epi8(dr,dg,_mm256_cmpgt_epi32(y,x)),high=_mm256_max_epi32(x,y);
  first=_mm256_blendv_epi8(first,db,_mm256_cmpgt_epi32(z,high));high=_mm256_max_epi32(high,z);
  __m256i last=_mm256_blendv_epi8(dr,dg,_mm256_cmpgt_epi32(x,y)),low=_mm256_min_epi32(x,y);
  last=_mm256_blendv_epi8(last,db,_mm256_cmpgt_epi32(low,z));low=_mm256_min_epi32(low,z);
  const __m256i middle=_mm256_sub_epi32(_mm256_add_epi32(_mm256_add_epi32(x,y),z),_mm256_add_epi32(high,low));
  const __m256i total=_mm256_add_epi32(dr,_mm256_add_epi32(dg,db));
  const __m256i n0=b2_gather(nodes,base),n1=b2_gather(nodes,_mm256_add_epi32(base,first));
  const __m256i n2=b2_gather(nodes,_mm256_add_epi32(base,_mm256_sub_epi32(total,last))),n3=b2_gather(nodes,_mm256_add_epi32(base,total));
  rgb.r=b2_interpolate<0>(n0,n1,n2,n3,high,middle,low);
  rgb.g=b2_interpolate<1>(n0,n1,n2,n3,high,middle,low);
  rgb.b=b2_interpolate<2>(n0,n1,n2,n3,high,middle,low);
}
}
void avx2_chain_domain_b2(const uint32_t* axes,const uint32_t* nodes,const SuffixCacheView& cache,uint8_t* data,size_t pixels) noexcept {
  for(size_t p=0;p<pixels;p+=8) {
    B2Rgb rgb;b2_load(data+3*p,rgb);b2_transform(axes,nodes,rgb);
    const __m256i dg=_mm256_sub_epi32(rgb.g,rgb.r),db=_mm256_sub_epi32(rgb.b,rgb.r);
    const __m256i index=_mm256_add_epi32(
        _mm256_mullo_epi32(_mm256_sub_epi32(rgb.r,_mm256_set1_epi32(cache.r_min)),_mm256_set1_epi32(cache.width_g*cache.width_b)),
        _mm256_add_epi32(_mm256_mullo_epi32(_mm256_sub_epi32(dg,_mm256_set1_epi32(cache.dg_min)),_mm256_set1_epi32(cache.width_b)),
            _mm256_sub_epi32(db,_mm256_set1_epi32(cache.db_min))));
    const __m256i value=b2_gather(cache.table,index),mask=_mm256_set1_epi32(255);
    rgb.r=_mm256_and_si256(value,mask);rgb.g=_mm256_and_si256(_mm256_srli_epi32(value,8),mask);rgb.b=_mm256_srli_epi32(value,16);
    b2_store(data+3*p,rgb);
  }
}
#if defined(P16_B2_CONTRACT)
// 仅独立质量可调用首级；生产库没有新增C ABI。
void avx2_b2_first_contract(const uint32_t* axes,const uint32_t* nodes,uint8_t* data,size_t pixels) noexcept {
  for(size_t p=0;p<pixels;p+=8) {B2Rgb rgb;b2_load(data+3*p,rgb);b2_transform(axes,nodes,rgb);b2_store(data+3*p,rgb);}
}
#endif
}
