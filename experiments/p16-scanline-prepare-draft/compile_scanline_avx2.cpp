// 修订100静态草稿：仅完整枚举prepare的R扫描线，不改变任意输入apply。
#include "channel_views.hpp"
#include "suffix_cache.hpp"
#include <immintrin.h>
#include <cstring>
namespace jshc_channel {
// 原97 TU逐字链接；非完整B批次保持原入口行为。
void avx2_compile_direct(const View*,const SuffixCacheView&,const uint32_t*,uint8_t*,size_t,size_t) noexcept;
namespace {
struct LineRgb {__m256i r,g,b;};
inline __attribute__((always_inline)) __m256i line_gather(const uint32_t* data,const __m256i& index) {
  return _mm256_i32gather_epi32(reinterpret_cast<const int*>(data),index,4);
}
template<int C>
inline __attribute__((always_inline)) __m256i line_interpolate(const __m256i& v0,const __m256i& v1,const __m256i& v2,const __m256i& v3,
    const __m256i& x,const __m256i& y,const __m256i& z) {
  const __m256i mask=_mm256_set1_epi32(255);
  const __m256i n0=_mm256_and_si256(_mm256_srli_epi32(v0,8*C),mask),n1=_mm256_and_si256(_mm256_srli_epi32(v1,8*C),mask);
  const __m256i n2=_mm256_and_si256(_mm256_srli_epi32(v2,8*C),mask),n3=_mm256_and_si256(_mm256_srli_epi32(v3,8*C),mask);
  const __m256i acc=_mm256_add_epi32(_mm256_slli_epi32(n0,16),_mm256_add_epi32(
      _mm256_mullo_epi32(_mm256_sub_epi32(n1,n0),x),_mm256_add_epi32(
          _mm256_mullo_epi32(_mm256_sub_epi32(n2,n1),y),_mm256_mullo_epi32(_mm256_sub_epi32(n3,n2),z))));
  return _mm256_srli_epi32(_mm256_add_epi32(acc,_mm256_set1_epi32(32768)),16);
}
inline __attribute__((always_inline)) void line_geometry(const View& v,const __m256i& x,const __m256i& y,const __m256i& z,
    __m256i& high,__m256i& middle,__m256i& low,__m256i& first,__m256i& last) {
  const __m256i sr=_mm256_set1_epi32(v.sr),sg=_mm256_set1_epi32(v.sg),one=_mm256_set1_epi32(1);
  first=_mm256_blendv_epi8(sr,sg,_mm256_cmpgt_epi32(y,x));high=_mm256_max_epi32(x,y);
  first=_mm256_blendv_epi8(first,one,_mm256_cmpgt_epi32(z,high));high=_mm256_max_epi32(high,z);
  last=_mm256_blendv_epi8(sr,sg,_mm256_cmpgt_epi32(x,y));low=_mm256_min_epi32(x,y);
  last=_mm256_blendv_epi8(last,one,_mm256_cmpgt_epi32(low,z));low=_mm256_min_epi32(low,z);
  middle=_mm256_sub_epi32(_mm256_add_epi32(_mm256_add_epi32(x,y),z),_mm256_add_epi32(high,low));
}
template<int C>
inline __attribute__((always_inline)) __m256i line_channel(const View& v,const __m256i& base,const __m256i& n0,const __m256i& n3,
    const __m256i& x,const __m256i& y,const __m256i& z) {
  __m256i high,middle,low,first,last;line_geometry(v,x,y,z,high,middle,low,first,last);
  const __m256i n1=line_gather(v.nodes,_mm256_add_epi32(base,first));
  const __m256i n2=line_gather(v.nodes,_mm256_add_epi32(base,_mm256_sub_epi32(_mm256_set1_epi32(v.sr+v.sg+1),last)));
  return line_interpolate<C>(n0,n1,n2,n3,high,middle,low);
}
template<bool Shared>
inline __attribute__((always_inline)) void line_transform(const View& v,size_t red,const uint32_t* green,const uint32_t* blue,LineRgb& rgb) {
  // red为0/8/.../248，最后一次loadu只读axis[248..255]。
  const __m256i ar=_mm256_loadu_si256(reinterpret_cast<const __m256i*>(v.axes[0][0]+red));
  const __m256i ag=_mm256_set1_epi32(int(green[0])),ab=_mm256_set1_epi32(int(blue[0]));
  const __m256i base=_mm256_add_epi32(_mm256_mullo_epi32(_mm256_srli_epi32(ar,17),_mm256_set1_epi32(v.sr)),
      _mm256_add_epi32(_mm256_mullo_epi32(_mm256_srli_epi32(ag,17),_mm256_set1_epi32(v.sg)),_mm256_srli_epi32(ab,17)));
  const __m256i mask=_mm256_set1_epi32(0x1ffff),x=_mm256_and_si256(ar,mask),y=_mm256_and_si256(ag,mask),z=_mm256_and_si256(ab,mask);
  const __m256i n0=line_gather(v.nodes,base),n3=line_gather(v.nodes,_mm256_add_epi32(base,_mm256_set1_epi32(v.sr+v.sg+1)));
  if constexpr(Shared) {
    __m256i high,middle,low,first,last;line_geometry(v,x,y,z,high,middle,low,first,last);
    const __m256i n1=line_gather(v.nodes,_mm256_add_epi32(base,first));
    const __m256i n2=line_gather(v.nodes,_mm256_add_epi32(base,_mm256_sub_epi32(_mm256_set1_epi32(v.sr+v.sg+1),last)));
    rgb.r=line_interpolate<0>(n0,n1,n2,n3,high,middle,low);
    rgb.g=line_interpolate<1>(n0,n1,n2,n3,high,middle,low);
    rgb.b=line_interpolate<2>(n0,n1,n2,n3,high,middle,low);
  } else {
    const __m256i r=line_channel<0>(v,base,n0,n3,x,y,z);
    // 非shared各自读取R轴、广播各自G/B，绝不重用别的输出坐标/排序。
    const __m256i g=line_channel<1>(v,base,n0,n3,
        _mm256_and_si256(_mm256_loadu_si256(reinterpret_cast<const __m256i*>(v.axes[1][0]+red)),mask),
        _mm256_and_si256(_mm256_set1_epi32(int(green[1])),mask),_mm256_and_si256(_mm256_set1_epi32(int(blue[1])),mask));
    const __m256i b=line_channel<2>(v,base,n0,n3,
        _mm256_and_si256(_mm256_loadu_si256(reinterpret_cast<const __m256i*>(v.axes[2][0]+red)),mask),
        _mm256_and_si256(_mm256_set1_epi32(int(green[2])),mask),_mm256_and_si256(_mm256_set1_epi32(int(blue[2])),mask));
    rgb.r=r;rgb.g=g;rgb.b=b;
  }
}
template<bool Shared>
void compile_scanline(const View& first,const SuffixCacheView& cache,const uint32_t* ids,uint8_t* destination,size_t blue_code) noexcept {
  constexpr int channels=Shared?1:3;
  uint32_t blues[channels];
  for(int c=0;c<channels;++c)blues[c]=first.axes[c][2][blue_code];
  const __m256i shuffle=_mm256_setr_epi8(0,4,8,12,-1,-1,-1,-1,-1,-1,-1,-1,-1,-1,-1,-1,
      0,4,8,12,-1,-1,-1,-1,-1,-1,-1,-1,-1,-1,-1,-1);
  for(size_t green_code=0;green_code<256;++green_code) {
    uint32_t greens[channels];
    for(int c=0;c<channels;++c)greens[c]=first.axes[c][1][green_code];
    for(size_t red_code=0;red_code<256;red_code+=8) {
      LineRgb rgb;line_transform<Shared>(first,red_code,greens,blues,rgb);
      const __m256i dg=_mm256_sub_epi32(rgb.g,rgb.r),db=_mm256_sub_epi32(rgb.b,rgb.r);
      const __m256i index=_mm256_add_epi32(
          _mm256_mullo_epi32(_mm256_sub_epi32(rgb.r,_mm256_set1_epi32(cache.r_min)),_mm256_set1_epi32(cache.width_g*cache.width_b)),
          _mm256_add_epi32(_mm256_mullo_epi32(_mm256_sub_epi32(dg,_mm256_set1_epi32(cache.dg_min)),_mm256_set1_epi32(cache.width_b)),
              _mm256_sub_epi32(db,_mm256_set1_epi32(cache.db_min))));
      const __m256i packed=_mm256_shuffle_epi8(line_gather(ids,index),shuffle);
      const uint64_t lo=uint32_t(_mm_cvtsi128_si32(_mm256_castsi256_si128(packed)));
      const uint64_t hi=uint32_t(_mm_cvtsi128_si32(_mm256_extracti128_si256(packed,1)));
      const uint64_t word=lo|(hi<<32);
      std::memcpy(destination+green_code*256+red_code,&word,sizeof(word));
    }
  }
}
}
void avx2_compile_direct_scanline(const View* chain,const SuffixCacheView& cache,
    const uint32_t* ids,uint8_t* destination,size_t begin,size_t pixels) noexcept {
  if((begin&65535) || pixels!=65536 || begin>=(size_t{1}<<24)) {
    avx2_compile_direct(chain,cache,ids,destination,begin,pixels);return;
  }
  if(chain[0].shared)compile_scanline<true>(chain[0],cache,ids,destination,begin>>16);
  else compile_scanline<false>(chain[0],cache,ids,destination,begin>>16);
}
}
