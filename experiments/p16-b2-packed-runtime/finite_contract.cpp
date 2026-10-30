// 99私有首级合同：独立四项非负uint64权重oracle，不链接生产C ABI。
#include "b2_plan.hpp"
#include <algorithm>
#include <array>
#include <cstdio>
#include <cstdlib>
#include <cstring>
#include <fstream>
#include <iterator>
#include <stdexcept>
#include <vector>
namespace jshc_channel {
void avx2_b2_first_contract(const uint32_t*,const uint32_t*,uint8_t*,size_t) noexcept;
}
namespace {
void require(bool ok) {if(!ok)throw std::runtime_error("99私有整数合同失败");}
uint32_t u32(const std::vector<uint8_t>& bytes,size_t p) {
  require(p+4<=bytes.size());uint32_t value;std::memcpy(&value,bytes.data()+p,4);return value;
}
void scalar(const jshc_channel::View& v,const uint8_t* src,uint8_t* dst) {
  uint32_t frac[3],idx[3];
  for(int a=0;a<3;++a) {const auto word=v.axes[0][a][src[a]];frac[a]=word&0x1ffff;idx[a]=word>>17;}
  int order[3]={0,1,2};
  if(frac[order[0]]<frac[order[1]])std::swap(order[0],order[1]);
  if(frac[order[1]]<frac[order[2]])std::swap(order[1],order[2]);
  if(frac[order[0]]<frac[order[1]])std::swap(order[0],order[1]);
  const uint64_t w[4]={65536-frac[order[0]],frac[order[0]]-frac[order[1]],frac[order[1]]-frac[order[2]],frac[order[2]]};
  uint64_t accum[3]={0,0,0};
  for(int corner=0;corner<4;++corner) {
    const auto word=v.nodes[(idx[0]*33+idx[1])*33+idx[2]];
    for(int c=0;c<3;++c)accum[c]+=w[corner]*((word>>(8*c))&255);
    if(corner!=3)++idx[order[corner]];
  }
  for(int c=0;c<3;++c)dst[c]=uint8_t((accum[c]+32768)>>16);
}
size_t exhaustive(const jshc_channel::View& view) {
  p16_b2::Tables tables;require(tables.prepare(view));
  require(tables.bytes()==160320 && size_t(tables.axes())%64==0 && size_t(tables.nodes())%64==0);
  require(!tables.prepare(view)); // 不重写已发布owner。
  constexpr size_t batch=65536;
  std::vector<uint8_t> source(batch*3),work(batch*3),expected(batch*3);
  for(size_t begin=0;begin<(size_t{1}<<24);begin+=batch) {
    for(size_t p=0;p<batch;++p) {
      const size_t q=begin+p;source[3*p]=uint8_t(q);source[3*p+1]=uint8_t(q>>8);source[3*p+2]=uint8_t(q>>16);
      scalar(view,source.data()+3*p,expected.data()+3*p);
    }
    work=source;
    jshc_channel::avx2_b2_first_contract(tables.axes(),tables.nodes(),work.data(),batch);
    require(work==expected);
  }
  size_t canaries=0;
  for(size_t offset:{size_t{0},size_t{1},size_t{3},size_t{7},size_t{15},size_t{31}})for(size_t n:{size_t{8},size_t{16},size_t{24}}) {
    std::vector<uint8_t> guarded(offset+3*n+64,173),wanted=guarded;
    for(size_t i=0;i<3*n;++i)guarded[offset+i]=uint8_t(i*83+offset*19+n);
    for(size_t p=0;p<n;++p)scalar(view,guarded.data()+offset+3*p,wanted.data()+offset+3*p);
    jshc_channel::avx2_b2_first_contract(tables.axes(),tables.nodes(),guarded.data()+offset,n);
    require(guarded==wanted);++canaries;
  }
  return canaries;
}
}
int main(int argc,char** argv) {
  try {
    static_assert(sizeof(p16_b2::Tables)==sizeof(void*),"99私有owner对象仅一个指针");
    require(argc==2);
    std::ifstream stream(argv[1],std::ios::binary);require(bool(stream));
    std::vector<uint8_t> bytes((std::istreambuf_iterator<char>(stream)),std::istreambuf_iterator<char>());
    require(bytes.size()==16+12*33+768+3072+33*33*33*3 && u32(bytes,8)==33);
    constexpr size_t start=16+12*33;
    std::array<std::array<uint32_t,256>,3> axis{};
    std::vector<uint32_t> nodes(33*33*33);
    for(size_t i=0;i<nodes.size();++i) {
      const auto* p=bytes.data()+start+768+3072+3*i;nodes[i]=p[0]|(uint32_t(p[1])<<8)|(uint32_t(p[2])<<16);
    }
    for(int a=0;a<3;++a)for(int c=0;c<256;++c)axis[a][c]=(uint32_t(bytes[start+a*256+c])<<17)|u32(bytes,start+768+4*(a*256+c));
    jshc_channel::View v{};v.nodes=nodes.data();v.sr=1089;v.sg=33;v.shared=true;
    for(int c=0;c<3;++c)for(int a=0;a<3;++a)v.axes[c][a]=axis[a].data();
    size_t canaries=exhaustive(v);
    const uint32_t fractional_cases[8]={0,1,16384,32768,32768,49152,65535,65536};
    for(int a=0;a<3;++a)for(int c=0;c<256;++c)axis[a][c]=(uint32_t(c/8)<<17)|fractional_cases[c%8];
    // 确定性任意节点张量，非训练/gold/照片输出。
    for(uint32_t r=0;r<33;++r)for(uint32_t g=0;g<33;++g)for(uint32_t b=0;b<33;++b) {
      const uint32_t red=(17*r+29*g+43*b+3*r*g)%256,green=(113*r+7*g+19*b+5*g*b)%256,blue=(31*r+97*g+11*b+7*b*r)%256;
      nodes[(r*33+g)*33+b]=red|(green<<8)|(blue<<16);
    }
    canaries+=exhaustive(v);
    size_t rejects=0;
    for(int bad=0;bad<8;++bad) {
      auto changed=v;const auto prior=axis[0][0];
      if(bad==0)changed.shared=false;
      if(bad==1)changed.sr=17*17;
      if(bad==2)changed.sg=25;
      if(bad==3)changed.nodes=nullptr;
      if(bad==4)changed.axes[0][0]=nullptr;
      if(bad==5)axis[0][0]=(32u<<17);
      if(bad==6)axis[0][0]=65537;
      if(bad==7)axis[0][0]=0xffffffff;
      p16_b2::Tables table;require(!table.prepare(changed));require(table.empty());axis[0][0]=prior;++rejects;
    }
    std::printf("{\"passed\":true,\"first_stage_u64_pixels\":33554432,\"canary_cases\":%zu,\"private_reject_cases\":%zu,\"owner_size\":%zu,\"requested_aligned_bytes\":160320,\"axis_and_nodes_mod64\":0,\"native_production_abi_changes\":0,\"performance_calls\":0}\n",canaries,rejects,sizeof(p16_b2::Tables));
    return 0;
  } catch(const std::exception& e) {std::fprintf(stderr,"%s\n",e.what());return 1;}
}
