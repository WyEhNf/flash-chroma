#pragma once
#include "channel_runtime.h"
#include <cstdint>
#include <algorithm>
#include <cstddef>
// 独立typed研究元数据，不修改SLUT文件或旧默认入口。
struct p16_bubble_config {uint32_t version,enabled,kappa,count,cells[2],masks[2];};
struct p16_bubble_info {uint32_t version,enabled,hit_record_bytes,max_records;uint64_t maximum_hit_stack_bytes;};
extern "C" JSHC_CC_API int p16_cc_set_bubble(void*,const p16_bubble_config*,char*,size_t);
extern "C" JSHC_CC_API int p16_cc_get_bubble_info(const void*,p16_bubble_info*,char*,size_t);
namespace p16_bubble {
inline int64_t acc(const jshc_channel::View& v,int r,int g,int b,int c,bool flip) {
  int base=int(v.axes[0][0][r]>>17)*v.sr+int(v.axes[0][1][g]>>17)*v.sg+int(v.axes[0][2][b]>>17);
  int x=int(v.axes[c][0][r]&0x1ffff),y=int(v.axes[c][1][g]&0x1ffff),z=int(v.axes[c][2][b]&0x1ffff);
  int a=v.sr,d=v.sg,e=1;
  if(flip){base+=a;a=-a;x=65536-x;}
  const int last=base+a+d+e;
  if(x<y){std::swap(x,y);std::swap(a,d);}
  if(y<z){std::swap(y,z);std::swap(d,e);}
  if(x<y){std::swap(x,y);std::swap(a,d);}
  const int shift=8*c;
  return int64_t(65536-x)*((v.nodes[base]>>shift)&255)+int64_t(x-y)*((v.nodes[base+a]>>shift)&255)
      +int64_t(y-z)*((v.nodes[base+a+d]>>shift)&255)+int64_t(z)*((v.nodes[last]>>shift)&255);
}
struct Hit {uint16_t offset;uint8_t rgb[3];};
constexpr size_t max_records=4096;
inline bool hit(const jshc_channel::View& v,int r,int g,int b) {
  return (v.axes[0][0][r]>>17)==30 && (v.axes[0][1][g]>>17)==31
      && ((v.axes[0][2][b]>>17)==13 || (v.axes[0][2][b]>>17)==14);
}
// 不内联，使禁用功能的旧路径不承担密集命中数组的栈帧。
__attribute__((noinline)) inline void block(const jshc_channel::View& v,uint8_t* rgb,size_t pixels,int kernel) {
  Hit hits[max_records];size_t count=0;
  for(size_t p=0;p<pixels;++p) {
    const int r=rgb[3*p],g=rgb[3*p+1],b=rgb[3*p+2];
    if(!hit(v,r,g,b))continue;
    auto& h=hits[count++];h.offset=uint16_t(p);
    for(int c=0;c<3;++c) {
      const int x=int(v.axes[c][0][r]&0x1ffff),y=int(v.axes[c][1][g]&0x1ffff),z=int(v.axes[c][2][b]&0x1ffff);
      const int t=std::min({x,y,z,65536-x,65536-y,65536-z}),w=std::min(65536,3*t);
      const int64_t mixed=int64_t(65536-w)*acc(v,r,g,b,c,false)+int64_t(w)*acc(v,r,g,b,c,true);
      h.rgb[c]=uint8_t((mixed+(int64_t(1)<<31))>>32);
    }
  }
  const size_t vectorized=kernel==1?(pixels&~size_t{7}):0;
  if(vectorized)jshc_channel::avx2_chain(&v,1,rgb,vectorized);
  for(size_t p=vectorized;p<pixels;++p) {
    const int r=rgb[3*p],g=rgb[3*p+1],b=rgb[3*p+2];uint8_t out[3];
    for(int c=0;c<3;++c)out[c]=uint8_t((acc(v,r,g,b,c,false)+32768)>>16);
    for(int c=0;c<3;++c)rgb[3*p+c]=out[c];
  }
  for(size_t n=0;n<count;++n)for(int c=0;c<3;++c)rgb[3*hits[n].offset+c]=hits[n].rgb[c];
}
}
