// 290保留四种原像素布局，哨兵回退上下文显式传入。
#include "direct_sentinel.hpp"
namespace jshc_channel {
void avx2_direct_sentinel_linear_to(const DirectSentinelView&,const uint8_t*,const uint32_t*,const uint8_t*,uint8_t*,size_t) noexcept;
void avx2_direct_sentinel_pair48(const DirectSentinelView&,const uint8_t*,const uint32_t*,uint8_t*,size_t) noexcept;
void avx2_direct_sentinel_pair48_to(const DirectSentinelView&,const uint8_t*,const uint32_t*,const uint8_t*,uint8_t*,size_t) noexcept;
void avx2_direct_sentinel_normal_mt(const DirectSentinelView&,const uint8_t*,const uint32_t*,uint8_t*,size_t) noexcept;
void avx2_direct_sentinel(const DirectSentinelView& context,const uint8_t* ids,const uint32_t* palette,const uint8_t* source,uint8_t* output,size_t pixels,uint32_t mode) noexcept {
  if(mode==2 && source==output)avx2_direct_sentinel_normal_mt(context,ids,palette,output,pixels);
  else if(mode==1 && source==output)avx2_direct_sentinel_pair48(context,ids,palette,output,pixels);
  else if(mode==3 || mode==1 || mode==2)avx2_direct_sentinel_pair48_to(context,ids,palette,source,output,pixels);
  else avx2_direct_sentinel_linear_to(context,ids,palette,source,output,pixels);
}
}
