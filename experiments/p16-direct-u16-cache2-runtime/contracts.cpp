// 独立有限合同：类型边界、无符号65535、末ID guard及恰好24B输入输出。
#define NOMINMAX
#include "direct_u16.hpp"
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
    require(!direct_u16_palette_fits(0) && direct_u16_palette_fits(1) && direct_u16_palette_fits(255)
        && direct_u16_palette_fits(256) && direct_u16_palette_fits(65536) && !direct_u16_palette_fits(65537),"palette边界合同失败");
    uint32_t axes[256]{};uint32_t nodes[8]{};View view{};
    for(int c=0;c<3;++c)for(int a=0;a<3;++a)view.axes[c][a]=axes;
    view.nodes=nodes;view.sr=4;view.sg=2;view.shared=false;
    SuffixCacheView cache{};cache.width_g=cache.width_b=1;
    for(uint32_t id:{0u,255u,256u,65535u,65536u}) {
      std::array<uint16_t,8> result;result.fill(12345);
      const bool ok=avx2_compile_direct_u16(&view,cache,&id,result.data(),0,result.size());
      require(ok==(id<65536),"编译ID范围证明失败");
      for(uint16_t value:result)require(value==(ok?id:12345),"编译ID截断或越界写入");
    }
    constexpr size_t count=size_t{1}<<24;
    Guarded table(count*sizeof(uint16_t)+4),source(24),target(24);
    auto* ids=reinterpret_cast<uint16_t*>(table.data);
    require((reinterpret_cast<uintptr_t>(ids)%alignof(uint16_t))==0,"u16对象对齐不足");
    // VirtualAlloc返回原始存储；placement new建立实际uint16对象，非uint32别名写入。
    for(size_t i=0;i<count+2;++i)new(ids+i) uint16_t(0);
    std::vector<uint32_t> palette(65536);
    for(size_t i=0;i<palette.size();++i)palette[i]=uint32_t((i*257+13)&0xffffff);
    const std::array<uint32_t,8> addresses={0,1,255,256,65535,65536,0xfffffe,0xffffff};
    const std::array<uint16_t,8> wanted={0,255,256,65535,256,255,65535,65535};
    uint8_t expected[24];
    for(size_t i=0;i<8;++i) {
      ids[addresses[i]]=wanted[i];
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
        avx2_direct_u16(ids,palette.data(),input.data,output.data,length,mode);
        require(std::memcmp(output.data,wanted_rgb.data(),length*3)==0,"分离读包/索引/guard错误");
        avx2_direct_u16(ids,palette.data(),input.data,input.data,length,mode);
        require(std::memcmp(input.data,wanted_rgb.data(),length*3)==0,"原地读包/索引/guard错误");
        guarded_cases+=2;
      }
    }
    require(ids[count]==0 && ids[count+1]==0,"尾guard被写入");
    std::cout<<"{\"passed\":true,\"palette_boundary_cases\":6,\"compile_id_cases\":5,\"guard_bytes\":4,\"input_address_max\":16777215,\"id_max\":65535,\"guarded_cases\":"<<guarded_cases<<",\"bmi_supported\":"<<(__builtin_cpu_supports("bmi")?"true":"false")<<",\"table_data_mod64\":"
        <<(reinterpret_cast<uintptr_t>(ids)&63)<<",\"performance_calls\":0}"<<std::endl;
    return 0;
  }catch(const std::exception& e){std::cerr<<e.what()<<std::endl;return 1;}
}
