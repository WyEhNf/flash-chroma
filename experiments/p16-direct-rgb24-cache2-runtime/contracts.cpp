// 完整RGB24色值、恰长输入/输出、表末guard的独立有限合同。
#define NOMINMAX
#include "direct_rgb24.hpp"
#include <windows.h>
#include <array>
#include <cstring>
#include <iostream>
#include <stdexcept>
#include <vector>
namespace {
void require(bool value,const char* text){if(!value)throw std::runtime_error(text);}
struct Guarded {
  uint8_t* allocation=nullptr;uint8_t* data=nullptr;
  explicit Guarded(size_t bytes) {
    SYSTEM_INFO s;GetSystemInfo(&s);const size_t page=s.dwPageSize;
    const size_t accessible=(bytes+page-1)/page*page;
    allocation=static_cast<uint8_t*>(VirtualAlloc(nullptr,accessible+page,MEM_RESERVE|MEM_COMMIT,PAGE_READWRITE));
    require(allocation,"VirtualAlloc失败");DWORD old=0;
    require(VirtualProtect(allocation+accessible,page,PAGE_NOACCESS,&old)!=0,"guard失败");
    data=allocation+accessible-bytes;
  }
  ~Guarded(){if(allocation)VirtualFree(allocation,0,MEM_RELEASE);}
  Guarded(const Guarded&)=delete;Guarded& operator=(const Guarded&)=delete;
};
}
int main(){try{
  using namespace jshc_channel;
  uint32_t axes[256]{},nodes[8]{};View view{};
  for(int c=0;c<3;++c)for(int a=0;a<3;++a)view.axes[c][a]=axes;
  view.nodes=nodes;view.sr=4;view.sg=2;view.shared=false;
  SuffixCacheView cache{};cache.width_g=cache.width_b=1;
  size_t compile_cases=0;
  for(uint32_t color:{0u,255u,256u,65535u,65536u,0xffffffu,0x1000000u}){
    std::array<uint8_t,24> output;output.fill(123);
    const bool ok=avx2_compile_direct_rgb24(&view,cache,&color,output.data(),0,8);
    require(ok==(color<=0xffffffu),"编译RGB24范围失败");
    for(size_t i=0;i<24;++i)require(output[i]==(ok?uint8_t(color>>(8*(i%3))):123),"RGB截断或失败写入");
    ++compile_cases;
  }
  constexpr size_t count=size_t{1}<<24;
  Guarded table(3*count+4);std::memset(table.data,0,3*count+4);
  const std::array<uint32_t,8> addresses={0,1,255,256,65535,65536,0xfffffe,0xffffff};
  const std::array<uint32_t,8> colors={0,0xffffff,0x800000,0x008000,0x000080,0x010203,0xfedcba,0xabcdef};
  for(size_t i=0;i<8;++i)for(int c=0;c<3;++c)table.data[3*addresses[i]+c]=uint8_t(colors[i]>>(8*c));
  size_t guarded_cases=0;
  for(uint32_t mode=0;mode<4;++mode){
    if(mode&&!__builtin_cpu_supports("bmi"))continue;
    for(size_t length:{0u,1u,7u,8u,9u,31u,32u,39u,40u,64u,71u,72u,73u,4095u,4096u,4097u,65535u,65536u,65537u}){
      Guarded source(3*length),target(3*length);std::vector<uint8_t> expected(3*length),original(3*length);
      for(size_t i=0;i<length;++i)for(int c=0;c<3;++c){original[3*i+c]=uint8_t(addresses[i%8]>>(8*c));expected[3*i+c]=uint8_t(colors[i%8]>>(8*c));}
      if(length)std::memcpy(source.data,original.data(),3*length);
      avx2_direct_rgb24(table.data,nullptr,source.data,target.data,length,mode);
      require(!length||std::memcmp(target.data,expected.data(),3*length)==0,"分离恰长RGB24错误");
      avx2_direct_rgb24(table.data,nullptr,source.data,source.data,length,mode);
      require(!length||std::memcmp(source.data,expected.data(),3*length)==0,"原地恰长RGB24错误");
      guarded_cases+=2;
    }
  }
  for(size_t i=0;i<4;++i)require(table.data[3*count+i]==0,"末guard被写入");
  std::cout<<"{\"passed\":true,\"compile_color_cases\":"<<compile_cases<<",\"guarded_cases\":"<<guarded_cases<<",\"guard_bytes\":4,\"performance_calls\":0}"<<std::endl;
  return 0;
}catch(const std::exception& e){std::cerr<<e.what()<<std::endl;return 1;}}
