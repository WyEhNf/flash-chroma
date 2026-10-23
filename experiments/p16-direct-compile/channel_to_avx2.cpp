// 沿用已验四级专门化算式，只把输入地址与输出地址分开。
#include "../channel-runtime-specialized/channel_avx2.cpp"
namespace jshc_channel {
void avx2_chain_to(const View* chain,size_t stages,const uint8_t* source,uint8_t* destination,size_t pixels) noexcept {
  if(stages==4 && !chain[0].shared && chain[1].shared && chain[2].shared && chain[3].shared) {
    const View& v0=chain[0];const View& v1=chain[1];const View& v2=chain[2];const View& v3=chain[3];
    for(size_t p=0;p<pixels;p+=8) {
      Rgb rgb;load(source+3*p,rgb);
      transform<false>(v0,rgb);transform<true>(v1,rgb);transform<true>(v2,rgb);transform<true>(v3,rgb);
      store(destination+3*p,rgb);
    }
    return;
  }
  for(size_t p=0;p<pixels;p+=8) {
    Rgb rgb;load(source+3*p,rgb);
    for(size_t s=0;s<stages;++s) {
      if(chain[s].shared)transform<true>(chain[s],rgb);
      else transform<false>(chain[s],rgb);
    }
    store(destination+3*p,rgb);
  }
}
}
