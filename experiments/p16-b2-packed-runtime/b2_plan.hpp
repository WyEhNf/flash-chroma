#pragma once
// 99唯一64B对齐owner：轴3072B和节点roundup157248B一次申请。
#include "channel_views.hpp"
#include <cstddef>
#include <cstdint>
#include <memory>
#include <new>
namespace p16_b2 {
class Tables {
  struct Delete {
    void operator()(uint32_t* pointer) const noexcept {
      ::operator delete(pointer,std::align_val_t{64});
    }
  };
  uint32_t* pointer_=nullptr;
public:
  static constexpr size_t axis_words=768,node_words=34*34*34;
  static constexpr size_t node_rounded_words=(node_words+15)/16*16;
  static constexpr size_t allocation_bytes=(axis_words+node_rounded_words)*4;
  Tables()=default;
  Tables(const Tables&)=delete;
  Tables& operator=(const Tables&)=delete;
  ~Tables() {Delete{}(pointer_);}
  bool empty() const noexcept {return !pointer_;}
  size_t bytes() const noexcept {return pointer_?allocation_bytes:0;}
  const uint32_t* axes() const noexcept {return pointer_;}
  const uint32_t* nodes() const noexcept {return pointer_?pointer_+axis_words:nullptr;}
  bool prepare(const jshc_channel::View& v) {
    if(pointer_ || !v.shared || v.sr!=1089 || v.sg!=33 || !v.nodes)return false;
    for(int a=0;a<3;++a) {
      if(!v.axes[0][a])return false;
      for(int code=0;code<256;++code) {
        const uint32_t word=v.axes[0][a][code];
        if((word>>17)>=32 || (word&0x1ffff)>65536)return false;
      }
    }
    // 发布前唯一可能抛出点；失败仍由原97完整路径处理。
    std::unique_ptr<uint32_t,Delete> pending(static_cast<uint32_t*>(
        ::operator new(allocation_bytes,std::align_val_t{64})));
    const uint32_t scale[3]={2312,136,8},parity[3]={4,2,1};
    for(int a=0;a<3;++a)for(int code=0;code<256;++code) {
      const uint32_t old=v.axes[0][a][code],fraction=old&0x1ffff;
      const uint32_t index=(old>>17)+(fraction==65536);
      const uint32_t contribution=(index/2)*scale[a]+(index%2)*parity[a];
      pending.get()[a*256+code]=(contribution<<16)|(fraction==65536?0:fraction);
    }
    for(size_t i=axis_words;i<axis_words+node_rounded_words;++i)pending.get()[i]=0;
    for(uint32_t r=0;r<34;++r)for(uint32_t g=0;g<34;++g)for(uint32_t b=0;b<34;++b) {
      const uint32_t slot=(((r/2)*17+g/2)*17+b/2)*8+(r%2)*4+(g%2)*2+b%2;
      const uint32_t rr=r>32?32:r,gg=g>32?32:g,bb=b>32?32:b;
      pending.get()[axis_words+slot]=v.nodes[(rr*33+gg)*33+bb];
    }
    pointer_=pending.release();return true;
  }
};
static_assert(Tables::allocation_bytes==160320,"99固定新增申请字节");
}
