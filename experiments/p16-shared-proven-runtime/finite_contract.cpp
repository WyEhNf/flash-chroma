// 97私有无检查核的独立整数/边界合同；只在后续授权质量窗口执行。
#include "channel_views.hpp"
#include "suffix_cache.hpp"
#include <algorithm>
#include <array>
#include <cstdint>
#include <cstdio>
#include <stdexcept>
#include <vector>

namespace jshc_channel {
void avx2_chain_domain_shared(const View*,const SuffixCacheView&,uint8_t*,size_t) noexcept;
void avx2_chain_cached(const View*,const SuffixCacheView&,uint8_t*,size_t) noexcept;
}
namespace {
uint8_t oracle(const jshc_channel::View& v,const uint8_t* input) {
  int indices[3],fraction[3],steps[3]={v.sr,v.sg,1};
  for(int a=0;a<3;++a) {
    const uint32_t value=v.axes[0][a][input[a]];
    indices[a]=int(value>>17);fraction[a]=int(value&0x1ffff);
  }
  if(fraction[0]<fraction[1]) {std::swap(fraction[0],fraction[1]);std::swap(steps[0],steps[1]);}
  if(fraction[1]<fraction[2]) {std::swap(fraction[1],fraction[2]);std::swap(steps[1],steps[2]);}
  if(fraction[0]<fraction[1]) {std::swap(fraction[0],fraction[1]);std::swap(steps[0],steps[1]);}
  const size_t base=size_t(indices[0])*size_t(v.sr)+size_t(indices[1])*size_t(v.sg)+size_t(indices[2]);
  const int weights[4]={65536-fraction[0],fraction[0]-fraction[1],fraction[1]-fraction[2],fraction[2]};
  const size_t corners[4]={base,base+size_t(steps[0]),base+size_t(steps[0]+steps[1]),base+size_t(v.sr+v.sg+1)};
  uint64_t sum=0;
  for(int k=0;k<4;++k)sum+=uint64_t(weights[k])*uint64_t(v.nodes[corners[k]]&255u);
  return uint8_t((sum+32768u)/65536u);
}
void require(bool value) {if(!value)throw std::runtime_error("97私有核整数或哨兵合同失败");}
}
int main() {
  try {
    unsigned cases=0;
    uint64_t pixels_checked=0;
    for(const int m:{17,25,33}) {
      std::vector<uint32_t> nodes(size_t(m)*size_t(m)*size_t(m));
      for(int r=0;r<m;++r)for(int g=0;g<m;++g)for(int b=0;b<m;++b) {
        const uint32_t value=uint32_t((19*r+29*g+37*b+3*r*g+5*g*b)&255);
        nodes[(size_t(r)*size_t(m)+size_t(g))*size_t(m)+size_t(b)]=value|(value<<8)|(value<<16);
      }
      std::array<std::array<std::array<uint32_t,256>,3>,3> axes{};
      for(int c=0;c<3;++c)for(int a=0;a<3;++a)for(int code=0;code<256;++code) {
        const int numerator=code*(m-1),index=std::min(numerator/255,m-2);
        const uint32_t fraction=uint32_t(((numerator-index*255)*65536+127)/255);
        axes[c][a][size_t(code)]=(uint32_t(index)<<17)|fraction;
      }
      std::array<uint32_t,256> table{};
      for(unsigned x=0;x<256;++x)table[x]=x|((255u-x)<<8)|(((x*73u)&255u)<<16);
      const jshc_channel::SuffixCacheView cache={table.data(),0,255,0,0,0,0,1,1};
      for(int separate_axes=0;separate_axes<2;++separate_axes) {
        std::array<jshc_channel::View,4> views{};
        for(auto& v:views) {
          v.nodes=nodes.data();v.sr=m*m;v.sg=m;v.shared=true;
          for(int c=0;c<3;++c)for(int a=0;a<3;++a)v.axes[c][a]=axes[separate_axes?c:0][a].data();
        }
        for(const size_t n:{size_t(0),size_t(8),size_t(16),size_t(256),size_t(65536)}) {
          std::vector<uint8_t> source(n*3),expected(n*3);
          uint32_t random=0x97005231u;
          for(size_t i=0;i<source.size();++i) {random=random*1664525u+1013904223u;source[i]=uint8_t(random>>24);}
          for(size_t i=0;i<std::min(n,size_t(8));++i) {
            const uint8_t value=uint8_t(i==0?0:i==1?255:i*31);
            source[3*i]=source[3*i+1]=source[3*i+2]=value;
          }
          for(size_t i=0;i<n;++i) {
            const uint32_t output=table[oracle(views[0],source.data()+3*i)];
            for(int c=0;c<3;++c)expected[3*i+size_t(c)]=uint8_t(output>>(8*c));
          }
          for(const size_t offset:{size_t(0),size_t(1),size_t(7),size_t(31),size_t(63)}) {
            std::vector<uint8_t> fresh(source.size()+128,173),checked=fresh;
            std::copy(source.begin(),source.end(),fresh.begin()+static_cast<std::ptrdiff_t>(offset));checked=fresh;
            jshc_channel::avx2_chain_domain_shared(views.data(),cache,fresh.data()+offset,n);
            jshc_channel::avx2_chain_cached(views.data(),cache,checked.data()+offset,n);
            require(fresh==checked);
            require(std::equal(expected.begin(),expected.end(),fresh.begin()+static_cast<std::ptrdiff_t>(offset)));
            require(std::all_of(fresh.begin(),fresh.begin()+static_cast<std::ptrdiff_t>(offset),[](uint8_t x){return x==173;}));
            require(std::all_of(fresh.begin()+static_cast<std::ptrdiff_t>(offset+source.size()),fresh.end(),[](uint8_t x){return x==173;}));
            ++cases;pixels_checked+=n;
          }
        }
      }
    }
    std::printf("{\"passed\":true,\"cases\":%u,\"pixels_checked\":%llu,\"production_c_abi_changes\":0}\n",
        cases,static_cast<unsigned long long>(pixels_checked));
    return 0;
  } catch(const std::exception& e) {std::fprintf(stderr,"%s\n",e.what());return 1;}
}
