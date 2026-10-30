// 独立有限合同：固定top255、dummy不输出、任意lane miss、四种原像素布局与保护页。
#define NOMINMAX
#include "direct_sentinel.hpp"
#include "sentinel_prepare.hpp"
#include <windows.h>
#include <array>
#include <iostream>
#include <map>
#include <stdexcept>
#include <vector>

namespace {
void require(bool value,const char* text){if(!value)throw std::runtime_error(text);}
struct Guarded {
  uint8_t* allocation=nullptr;uint8_t* data=nullptr;
  explicit Guarded(size_t bytes) {
    SYSTEM_INFO info;GetSystemInfo(&info);const size_t page=info.dwPageSize;
    const size_t accessible=(bytes+page-1)/page*page;
    allocation=static_cast<uint8_t*>(VirtualAlloc(nullptr,accessible+page,MEM_RESERVE|MEM_COMMIT,PAGE_READWRITE));
    require(allocation,"保护页分配失败");DWORD old=0;
    require(VirtualProtect(allocation+accessible,page,PAGE_NOACCESS,&old)!=0,"设置保护页失败");data=allocation+accessible-bytes;
  }
  ~Guarded(){if(allocation)VirtualFree(allocation,0,MEM_RELEASE);}
  Guarded(const Guarded&)=delete;Guarded& operator=(const Guarded&)=delete;
};
void check_selection(const std::vector<uint32_t>& cache) {
  const auto actual=jshc_channel::select_sentinel_palette(cache);
  std::map<uint32_t,uint64_t> histogram;
  for(uint32_t value:cache)++histogram[value];
  require(actual.distinct==histogram.size(),"完整RGB键或去重错误");
  const bool eligible=histogram.size()>255 && histogram.size()<=65536;
  require(actual.eligible==eligible,"palette边界资格错误");
  if(!eligible){require(actual.ids.empty(),"无资格仍产生哨兵ID");return;}
  std::vector<std::pair<uint64_t,uint32_t>> ranking;
  for(const auto& item:histogram)ranking.emplace_back(item.second,item.first);
  std::sort(ranking.begin(),ranking.end(),[](const auto& a,const auto& b){return a.first!=b.first?a.first>b.first:a.second<b.second;});
  std::map<uint32_t,uint32_t> expected;
  for(size_t i=0;i<255;++i)expected[ranking[i].second]=0;
  uint32_t next=0;for(auto& item:expected)item.second=next++;
  require(actual.ids.size()==cache.size() && actual.palette[255]==0,"ID长度或dummy初始化错误");
  for(size_t i=0;i<cache.size();++i) {
    const auto found=expected.find(cache[i]);
    require(actual.ids[i]==(found==expected.end()?255:found->second),"固定top255编码错误");
    if(actual.ids[i]!=255)require(actual.palette[actual.ids[i]]==cache[i],"热palette不精确");
  }
}
}

int main() {
  try {
    using namespace jshc_channel;
    size_t selection_cases=0;
    for(size_t size:{0u,1u,254u,255u,256u,257u,65536u,65537u}) {
      std::vector<uint32_t> cache(size);for(size_t i=0;i<size;++i)cache[i]=uint32_t(i);
      check_selection(cache);++selection_cases;
    }
    std::vector<uint32_t> adversarial;
    for(uint32_t value=0;value<257;++value)for(size_t count=0;count<(value<255?3u:1u);++count)adversarial.push_back(value);
    adversarial.push_back(0xffffff);adversarial.push_back(0xffffff);adversarial.push_back(0xffffff);adversarial.push_back(0xffffff);
    std::reverse(adversarial.begin(),adversarial.end());check_selection(adversarial);++selection_cases;

    constexpr uint32_t fallback=0x786543;
    uint32_t axes[256]{};uint32_t nodes[8];std::fill(nodes,nodes+8,fallback);
    std::array<View,4> chain{};
    for(auto& view:chain) {
      for(int c=0;c<3;++c)for(int a=0;a<3;++a)view.axes[c][a]=axes;
      view.nodes=nodes;view.sr=4;view.sg=2;view.shared=false;
    }
    SuffixCacheView cache{};cache.table=&fallback;cache.r_min=cache.r_max=67;
    cache.dg_min=cache.dg_max=34;cache.db_min=cache.db_max=53;cache.width_g=cache.width_b=1;
    const DirectSentinelView cached_context{chain.data(),cache};
    for(uint32_t id:{0u,254u,255u}) {
      std::array<uint8_t,8> compiled{};
      avx2_compile_direct(chain.data(),cache,&id,compiled.data(),0,8);
      for(uint8_t value:compiled)require(value==id,"编译hot/sentinel ID错误");
    }
    constexpr size_t count=size_t{1}<<24;
    Guarded table(count+4);
    std::memset(table.data,0,count+4);
    std::array<uint32_t,256> palette{};
    for(size_t i=0;i<255;++i)palette[i]=uint32_t((i*65537+17)&0xffffff);
    palette[255]=0x112233; // 故意不是回退值；任何dummy外泄均应失败。
    const std::array<uint32_t,8> addresses={0,1,255,256,65535,65536,0xfffffe,0xffffff};
    size_t guarded_cases=0,scalar_cases=0;
    // 先独立覆盖真实cache命中；随后用恒等链覆盖mixed包中各lane不同的输出。
    table.data[0]=255;uint8_t cached_input[24]{},cached_output[24]{};
    avx2_direct_sentinel(cached_context,table.data,palette.data(),cached_input,cached_output,8,0);
    for(size_t i=0;i<8;++i)for(int c=0;c<3;++c)require(cached_output[3*i+c]==uint8_t(fallback>>(8*c)),"8lane cache命中回退错误");
    for(size_t i=0;i<256;++i)axes[i]=uint32_t(i*65536/255);
    for(size_t corner=0;corner<8;++corner)nodes[corner]=((corner&4)?255u:0u)|((corner&2)?65280u:0u)|((corner&1)?16711680u:0u);
    cache.r_min=256;cache.r_max=255; // 所有lane均在cache外，必须执行三层后缀。
    const DirectSentinelView context{chain.data(),cache};
    for(uint32_t pattern:{0u,1u,2u,4u,8u,16u,32u,64u,128u,255u}) {
      std::array<uint8_t,24> original{},expected{};
      for(size_t lane=0;lane<8;++lane) {
        const uint32_t address=addresses[lane];const uint8_t id=pattern&(1u<<lane)?255:uint8_t(lane==7?254:lane);
        table.data[address]=id;if(id!=255)palette[id]=address;const uint32_t value=address;
        for(int c=0;c<3;++c){original[3*lane+c]=uint8_t(address>>(8*c));expected[3*lane+c]=uint8_t(value>>(8*c));}
      }
      for(size_t lane=0;lane<8;++lane) {
        uint8_t output[3];sentinel_scalar_one(context,table.data,palette.data(),original.data()+3*lane,output);
        require(std::memcmp(output,expected.data()+3*lane,3)==0,"scalar哨兵或Q16四级错误");++scalar_cases;
      }
      for(uint32_t mode=0;mode<4;++mode) {
        if(mode && !__builtin_cpu_supports("bmi"))continue;
        for(size_t length:{1u,7u,8u,9u,31u,32u,39u,40u,63u,64u,71u,72u,73u,4095u,4096u,4097u,65535u,65536u,65537u}) {
          Guarded input(length*3),output(length*3);
          std::vector<uint8_t> wanted(length*3),saved(length*3);
          for(size_t i=0;i<length;++i){std::memcpy(input.data+3*i,original.data()+3*(i%8),3);std::memcpy(wanted.data()+3*i,expected.data()+3*(i%8),3);}
          std::memcpy(saved.data(),input.data,saved.size());
          avx2_direct_sentinel(context,table.data,palette.data(),input.data,output.data,length,mode);
          require(std::memcmp(output.data,wanted.data(),wanted.size())==0,"分离像素核的哨兵/写包错误");
          require(std::memcmp(input.data,saved.data(),saved.size())==0,"分离像素核改变源");
          avx2_direct_sentinel(context,table.data,palette.data(),input.data,input.data,length,mode);
          require(std::memcmp(input.data,wanted.data(),wanted.size())==0,"原地像素核的哨兵/写包错误");guarded_cases+=2;
        }
      }
    }
    for(size_t i=0;i<4;++i)require(table.data[count+i]==0,"自有guard被修改");
    std::cout<<"{\"passed\":true,\"selection_cases\":"<<selection_cases<<",\"compile_id_cases\":3,\"scalar_cases\":"<<scalar_cases<<",\"guarded_cases\":"<<guarded_cases<<",\"table_data_mod64\":"<<(reinterpret_cast<uintptr_t>(table.data)&63)<<",\"performance_calls\":0}"<<std::endl;
    return 0;
  }catch(const std::exception& error){std::cerr<<error.what()<<std::endl;return 1;}
}
