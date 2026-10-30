// 独立有限合同：类型边界、10bit最大1023、末ID guard及恰好24B输入输出。
#define NOMINMAX
#include "direct_u10.hpp"
#include <windows.h>
#include <array>
#include <cstring>
#include <iostream>
#include <new>
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
    require(VirtualProtect(allocation+accessible,page,PAGE_NOACCESS,&old)!=0,"guard page失败");
    data=allocation+accessible-bytes;
  }
  ~Guarded(){if(allocation)VirtualFree(allocation,0,MEM_RELEASE);}
  Guarded(const Guarded&)=delete;Guarded& operator=(const Guarded&)=delete;
};
}
int main() {
  try {
    using namespace jshc_channel;
    require(!direct_u10_palette_fits(0) && direct_u10_palette_fits(1) && direct_u10_palette_fits(255)
        && direct_u10_palette_fits(256) && direct_u10_palette_fits(1024) && !direct_u10_palette_fits(1025),"palette边界合同失败");
    uint32_t axes[256]{};uint32_t nodes[8]{};View view{};
    for(int c=0;c<3;++c)for(int a=0;a<3;++a)view.axes[c][a]=axes;
    view.nodes=nodes;view.sr=4;view.sg=2;view.shared=false;
    SuffixCacheView cache{};cache.width_g=cache.width_b=1;
    for(uint32_t id:{0u,255u,256u,1023u,1024u,65535u,0xffffffffu}) {
      std::array<uint8_t,10> result;result.fill(123);
      const bool ok=avx2_compile_direct_u10(&view,cache,&id,result.data(),0,8);
      require(ok==(id<1024),"编译10bit ID范围证明失败");
      if(ok)for(uint32_t i=0;i<8;++i)require(direct_u10_id(result.data(),i)==id,"10bit编译序列错误");
      else for(uint8_t value:result)require(value==123,"非法ID仍改写输出");
    }
    constexpr size_t count=size_t{1}<<24,payload=count*5/4;
    Guarded table(payload+4),source(24),target(24);
    uint8_t* ids=table.data;std::memset(ids,0,payload+4);
    std::vector<uint32_t> palette(1024);
    for(size_t i=0;i<palette.size();++i)palette[i]=uint32_t((i*257+13)&0xffffff);
    const std::array<uint32_t,8> addresses={0,3,4,255,65535,0xfffffc,0xfffffe,0xffffff};
    const std::array<uint32_t,8> wanted={0,255,256,1023,256,255,1023,1023};
    uint8_t expected[24];
    for(size_t i=0;i<8;++i) {
      const size_t base=size_t(addresses[i]>>2)*5;const uint32_t shift=10*(addresses[i]&3u);
      uint64_t word=0;for(size_t j=0;j<5;++j)word|=uint64_t(ids[base+j])<<(8*j);
      word=(word&~(uint64_t(1023)<<shift))|(uint64_t(wanted[i])<<shift);
      for(size_t j=0;j<5;++j)ids[base+j]=uint8_t(word>>(8*j));
      const uint32_t a=addresses[i],v=palette[wanted[i]];
      for(int c=0;c<3;++c){source.data[3*i+c]=uint8_t(a>>(8*c));expected[3*i+c]=uint8_t(v>>(8*c));}
    }
    uint8_t original[24];std::memcpy(original,source.data,24);
    size_t guarded_cases=0;
    for(uint32_t mode=0;mode<4;++mode) {
      if(mode && !__builtin_cpu_supports("bmi"))continue;
      for(size_t length:{8u,31u,32u,39u,40u,64u,71u,72u,4095u,4096u,4097u}) {
        Guarded input(length*3),output(length*3);
        std::vector<uint8_t> wanted_rgb(length*3);
        for(size_t i=0;i<length;++i){std::memcpy(input.data+3*i,original+3*(i%8),3);std::memcpy(wanted_rgb.data()+3*i,expected+3*(i%8),3);}
        avx2_direct_u10(ids,palette.data(),input.data,output.data,length,mode);
        require(std::memcmp(output.data,wanted_rgb.data(),length*3)==0,"分离读包/索引/guard错误");
        avx2_direct_u10(ids,palette.data(),input.data,input.data,length,mode);
        require(std::memcmp(input.data,wanted_rgb.data(),length*3)==0,"原地读包/索引/guard错误");
        guarded_cases+=2;
      }
    }
    require(ids[payload]==0 && ids[payload+1]==0 && ids[payload+2]==0 && ids[payload+3]==0,"尾guard被写入");
    std::cout<<"{\"passed\":true,\"palette_boundary_cases\":6,\"compile_id_cases\":7,\"guard_bytes\":4,\"input_address_max\":16777215,\"id_max\":1023,\"guarded_cases\":"<<guarded_cases<<",\"bmi_supported\":"<<(__builtin_cpu_supports("bmi")?"true":"false")<<",\"table_data_mod64\":"
        <<(reinterpret_cast<uintptr_t>(ids)&63)<<",\"performance_calls\":0}"<<std::endl;
    return 0;
  }catch(const std::exception& e){std::cerr<<e.what()<<std::endl;return 1;}
}
