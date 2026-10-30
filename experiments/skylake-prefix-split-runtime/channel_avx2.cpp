// 依据布局只拆一次：复杂非共享首级单独遍历当前块，三个共享后缀继续按像素融合。
#include "channel_views.hpp"
#include <immintrin.h>

namespace jshc_channel {
namespace {
struct Rgb {__m256i r,g,b;}; // Win64只经引用传递，避免按值对齐临时对象。
inline void load(const uint8_t* p,Rgb& rgb) {
  const __m128i lo=_mm_loadu_si128(reinterpret_cast<const __m128i*>(p));
  const __m128i last=_mm_loadl_epi64(reinterpret_cast<const __m128i*>(p+16));
  const __m128i hi=_mm_alignr_epi8(last,lo,12);
  const __m256i raw=_mm256_inserti128_si256(_mm256_castsi128_si256(lo),hi,1);
  const __m256i shuffle=_mm256_setr_epi8(0,1,2,-1,3,4,5,-1,6,7,8,-1,9,10,11,-1,0,1,2,-1,3,4,5,-1,6,7,8,-1,9,10,11,-1);
  const __m256i packed=_mm256_shuffle_epi8(raw,shuffle), mask=_mm256_set1_epi32(255);
  rgb.r=_mm256_and_si256(packed,mask);rgb.g=_mm256_and_si256(_mm256_srli_epi32(packed,8),mask);rgb.b=_mm256_srli_epi32(packed,16);
}
inline void store(uint8_t* p,const Rgb& rgb) {
  const __m256i packed=_mm256_or_si256(rgb.r,_mm256_or_si256(_mm256_slli_epi32(rgb.g,8),_mm256_slli_epi32(rgb.b,16)));
  const __m256i shuffle=_mm256_setr_epi8(0,1,2,4,5,6,8,9,10,12,13,14,-1,-1,-1,-1,0,1,2,4,5,6,8,9,10,12,13,14,-1,-1,-1,-1);
  const __m256i bytes=_mm256_shuffle_epi8(packed,shuffle);const __m128i lo=_mm256_castsi256_si128(bytes),hi=_mm256_extracti128_si256(bytes,1);
  _mm_storeu_si128(reinterpret_cast<__m128i*>(p),_mm_or_si128(lo,_mm_slli_si128(hi,12)));
  _mm_storel_epi64(reinterpret_cast<__m128i*>(p+16),_mm_srli_si128(hi,4));
}
inline __m256i gather(const uint32_t* data,const __m256i& index) {
  return _mm256_i32gather_epi32(reinterpret_cast<const int*>(data),index,4);
}
template<int C>
inline __m256i interpolate(const __m256i& v0,const __m256i& v1,const __m256i& v2,const __m256i& v3,
    const __m256i& x,const __m256i& y,const __m256i& z) {
  const __m256i mask=_mm256_set1_epi32(255);
  const __m256i n0=_mm256_and_si256(_mm256_srli_epi32(v0,8*C),mask),n1=_mm256_and_si256(_mm256_srli_epi32(v1,8*C),mask);
  const __m256i n2=_mm256_and_si256(_mm256_srli_epi32(v2,8*C),mask),n3=_mm256_and_si256(_mm256_srli_epi32(v3,8*C),mask);
  const __m256i acc=_mm256_add_epi32(_mm256_slli_epi32(n0,16),_mm256_add_epi32(
      _mm256_mullo_epi32(_mm256_sub_epi32(n1,n0),x),_mm256_add_epi32(_mm256_mullo_epi32(_mm256_sub_epi32(n2,n1),y),_mm256_mullo_epi32(_mm256_sub_epi32(n3,n2),z))));
  return _mm256_srli_epi32(_mm256_add_epi32(acc,_mm256_set1_epi32(32768)),16);
}
// 高/低轴只需四次stride选择；相等分量对应零重心权重，不影响整数结果。
inline void geometry(const View& v,const __m256i& x,const __m256i& y,const __m256i& z,
    __m256i& high,__m256i& middle,__m256i& low,__m256i& first,__m256i& last) {
  const __m256i sr=_mm256_set1_epi32(v.sr),sg=_mm256_set1_epi32(v.sg),one=_mm256_set1_epi32(1);
  first=_mm256_blendv_epi8(sr,sg,_mm256_cmpgt_epi32(y,x));high=_mm256_max_epi32(x,y);
  first=_mm256_blendv_epi8(first,one,_mm256_cmpgt_epi32(z,high));high=_mm256_max_epi32(high,z);
  last=_mm256_blendv_epi8(sr,sg,_mm256_cmpgt_epi32(x,y));low=_mm256_min_epi32(x,y);
  last=_mm256_blendv_epi8(last,one,_mm256_cmpgt_epi32(low,z));low=_mm256_min_epi32(low,z);
  middle=_mm256_sub_epi32(_mm256_add_epi32(_mm256_add_epi32(x,y),z),_mm256_add_epi32(high,low));
}
template<int C>
inline __m256i channel(const View& v,const __m256i& base,const __m256i& n0,const __m256i& n3,
    const __m256i& x,const __m256i& y,const __m256i& z) {
  __m256i high,middle,low,first,last;geometry(v,x,y,z,high,middle,low,first,last);
  const __m256i n1=gather(v.nodes,_mm256_add_epi32(base,first));
  const __m256i n2=gather(v.nodes,_mm256_add_epi32(base,_mm256_sub_epi32(_mm256_set1_epi32(v.sr+v.sg+1),last)));
  return interpolate<C>(n0,n1,n2,n3,high,middle,low);
}
template<bool Shared>
inline void transform(const View& v,Rgb& rgb) {
  const __m256i ar=gather(v.axes[0][0],rgb.r),ag=gather(v.axes[0][1],rgb.g),ab=gather(v.axes[0][2],rgb.b);
  const __m256i base=_mm256_add_epi32(_mm256_mullo_epi32(_mm256_srli_epi32(ar,17),_mm256_set1_epi32(v.sr)),
      _mm256_add_epi32(_mm256_mullo_epi32(_mm256_srli_epi32(ag,17),_mm256_set1_epi32(v.sg)),_mm256_srli_epi32(ab,17)));
  const __m256i mask=_mm256_set1_epi32(0x1ffff),x=_mm256_and_si256(ar,mask),y=_mm256_and_si256(ag,mask),z=_mm256_and_si256(ab,mask);
  const __m256i n0=gather(v.nodes,base),n3=gather(v.nodes,_mm256_add_epi32(base,_mm256_set1_epi32(v.sr+v.sg+1)));
  if constexpr(Shared) {
    __m256i high,middle,low,first,last;geometry(v,x,y,z,high,middle,low,first,last);
    const __m256i n1=gather(v.nodes,_mm256_add_epi32(base,first));
    const __m256i n2=gather(v.nodes,_mm256_add_epi32(base,_mm256_sub_epi32(_mm256_set1_epi32(v.sr+v.sg+1),last)));
    rgb.r=interpolate<0>(n0,n1,n2,n3,high,middle,low);rgb.g=interpolate<1>(n0,n1,n2,n3,high,middle,low);rgb.b=interpolate<2>(n0,n1,n2,n3,high,middle,low);
    return;
  }
  const __m256i r=channel<0>(v,base,n0,n3,x,y,z);
  const __m256i g=channel<1>(v,base,n0,n3,_mm256_and_si256(gather(v.axes[1][0],rgb.r),mask),
      _mm256_and_si256(gather(v.axes[1][1],rgb.g),mask),_mm256_and_si256(gather(v.axes[1][2],rgb.b),mask));
  const __m256i b=channel<2>(v,base,n0,n3,_mm256_and_si256(gather(v.axes[2][0],rgb.r),mask),
      _mm256_and_si256(gather(v.axes[2][1],rgb.g),mask),_mm256_and_si256(gather(v.axes[2][2],rgb.b),mask));
  rgb.r=r;rgb.g=g;rgb.b=b;
}
__attribute__((noinline))
void first_stage(const View& source,uint8_t* data,size_t pixels) noexcept {
  const View view=source;
  for(size_t p=0;p<pixels;p+=8) {
    Rgb rgb;load(data+3*p,rgb);transform<false>(view,rgb);store(data+3*p,rgb);
  }
}
__attribute__((noinline))
void suffix_stages(const View* chain,uint8_t* data,size_t pixels) noexcept {
  // 三个共享后缀连续完成，不把每一级都变成一次额外块读写。
  const View& v1=chain[1];const View& v2=chain[2];const View& v3=chain[3];
  for(size_t p=0;p<pixels;p+=8) {
    Rgb rgb;load(data+3*p,rgb);
    transform<true>(v1,rgb);transform<true>(v2,rgb);transform<true>(v3,rgb);
    store(data+3*p,rgb);
  }
}
}
void avx2_chain(const View* chain,size_t stages,uint8_t* data,size_t pixels) noexcept {
  // 只在4096像素批入口判断布局。Rgb继续只经引用传递，不引入过对齐按值临时对象。
  if(stages==4 && !chain[0].shared && chain[1].shared && chain[2].shared && chain[3].shared) {
    first_stage(chain[0],data,pixels);
    suffix_stages(chain,data,pixels);
    return;
  }
  // 其它级数或共享布局仍按原语义逐级派发；不改变加载、公式和尾部处理。
  for(size_t p=0;p<pixels;p+=8) {
    Rgb rgb;load(data+3*p,rgb);
    for(size_t s=0;s<stages;++s) {
      if(chain[s].shared)transform<true>(chain[s],rgb);
      else transform<false>(chain[s],rgb);
    }
    store(data+3*p,rgb);
  }
}
}
