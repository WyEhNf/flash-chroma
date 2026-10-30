#pragma once
#include "channel_runtime.h"
#include "channel_views.hpp"
#include "suffix_cache.hpp"
#include <algorithm>
#include <cstdint>
#include <cstring>

namespace jshc_channel {
// 仅借用句柄已有的模型和cache，不拥有或复制表；调用期间句柄必须存活。
struct DirectSentinelView {const View* chain;SuffixCacheView cache;};
inline bool sentinel_palette_eligible(size_t size) noexcept {return size>255 && size<=65536;}
inline void sentinel_scalar_one(const DirectSentinelView& context,const uint8_t* table,
    const uint32_t* palette,const uint8_t* source,uint8_t* destination) noexcept {
  const uint32_t address=uint32_t(source[0])|(uint32_t(source[1])<<8)|(uint32_t(source[2])<<16);
  const uint32_t id=table[address];
  if(id!=255) {
    const uint32_t value=palette[id];
    destination[0]=uint8_t(value);destination[1]=uint8_t(value>>8);destination[2]=uint8_t(value>>16);return;
  }
  uint8_t colour[3];std::memcpy(colour,source,3);
  for(size_t stage=0;stage<4;++stage) {
    const auto& v=context.chain[stage];
    const int base=int(v.axes[0][0][colour[0]]>>17)*v.sr+int(v.axes[0][1][colour[1]]>>17)*v.sg+int(v.axes[0][2][colour[2]]>>17);
    uint8_t next[3];
    for(int c=0;c<3;++c) {
      int x=int(v.axes[c][0][colour[0]]&0x1ffff),y=int(v.axes[c][1][colour[1]]&0x1ffff),z=int(v.axes[c][2][colour[2]]&0x1ffff);
      int a=v.sr,b=v.sg,d=1;
      if(x<y){std::swap(x,y);std::swap(a,b);}
      if(y<z){std::swap(y,z);std::swap(b,d);}
      if(x<y){std::swap(x,y);std::swap(a,b);}
      const uint32_t shift=8*c;
      const int n0=(v.nodes[base]>>shift)&255,n1=(v.nodes[base+a]>>shift)&255;
      const int n2=(v.nodes[base+a+b]>>shift)&255,n3=(v.nodes[base+v.sr+v.sg+1]>>shift)&255;
      next[c]=uint8_t(((65536-x)*n0+(x-y)*n1+(y-z)*n2+z*n3+32768)>>16);
    }
    std::memcpy(colour,next,3);
  }
  std::memcpy(destination,colour,3);
}
void avx2_compile_direct(const View*,const SuffixCacheView&,const uint32_t*,uint8_t*,size_t,size_t) noexcept;
void avx2_direct_sentinel(const DirectSentinelView&,const uint8_t*,const uint32_t*,const uint8_t*,uint8_t*,size_t,uint32_t mode=0) noexcept;
}
extern "C" {
// reason：0启用哨兵，1旧8bit优先，2无四级域资格，3超65536，4分配失败。
struct p16_direct_sentinel_info {
  uint32_t version,enabled,format,reason,palette_size,id_bytes,guard_bytes,whole_cache_colors;
  uint64_t input_entries,raw_words,table_capacity_bytes,palette_capacity_bytes,temporary_peak_bytes;
  uint64_t guaranteed_alignment,data_mod_64;
  double prepare_seconds;
};
JSHC_CC_API int p16_cc_get_direct_sentinel_info(const void*,p16_direct_sentinel_info*,size_t);
JSHC_CC_API int p16_cc_copy_sentinel_palette(const void*,uint32_t*,size_t);
}
