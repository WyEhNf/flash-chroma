// 288仅替换apply核；表/prepare/vector与287相同，输入地址仍R低/G中/B高。
#include "direct_u10.hpp"
namespace jshc_channel {
void avx2_direct_u10_linear_to(const uint8_t*,const uint32_t*,const uint8_t*,uint8_t*,size_t) noexcept;
void avx2_direct_u10_pair48(const uint8_t*,const uint32_t*,uint8_t*,size_t) noexcept;
void avx2_direct_u10_pair48_to(const uint8_t*,const uint32_t*,const uint8_t*,uint8_t*,size_t) noexcept;
void avx2_direct_u10_normal_mt(const uint8_t*,const uint32_t*,uint8_t*,size_t) noexcept;
void avx2_direct_u10(const uint8_t* ids,const uint32_t* palette,const uint8_t* source,uint8_t* output,size_t pixels,uint32_t mode) noexcept {
  if(mode==2 && source==output)avx2_direct_u10_normal_mt(ids,palette,output,pixels);
  else if(mode==1 && source==output)avx2_direct_u10_pair48(ids,palette,output,pixels);
  else if(mode==3 || mode==1 || mode==2)avx2_direct_u10_pair48_to(ids,palette,source,output,pixels);
  else avx2_direct_u10_linear_to(ids,palette,source,output,pixels);
}
}
