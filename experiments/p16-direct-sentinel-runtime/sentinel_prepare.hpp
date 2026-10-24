#pragma once
#include "direct_sentinel.hpp"
#include <array>
#include <numeric>
#include <vector>

namespace jshc_channel {
struct SentinelSelection {
  std::vector<uint32_t> ids;
  std::array<uint32_t,256> palette{};
  size_t distinct=0;
  size_t temporary_peak_bytes=0;
  bool eligible=false;
};
// 只接收稀疏模型产生的whole-cache；频数含所有槽，合法零和未填充零同等计数。
inline SentinelSelection select_sentinel_palette(const std::vector<uint32_t>& cache) {
  SentinelSelection result;
  {
    std::vector<uint32_t> values=cache;
    std::sort(values.begin(),values.end());values.erase(std::unique(values.begin(),values.end()),values.end());
    result.distinct=values.size();
    result.temporary_peak_bytes=values.capacity()*sizeof(uint32_t);
    if(!sentinel_palette_eligible(values.size()))return result;
    std::vector<uint64_t> frequency(values.size(),0);
    for(uint32_t value:cache)++frequency[size_t(std::lower_bound(values.begin(),values.end(),value)-values.begin())];
    std::vector<uint32_t> order(values.size());std::iota(order.begin(),order.end(),0u);
    std::sort(order.begin(),order.end(),[&](uint32_t a,uint32_t b){return frequency[a]!=frequency[b]?frequency[a]>frequency[b]:values[a]<values[b];});
    result.temporary_peak_bytes=std::max(result.temporary_peak_bytes,values.capacity()*sizeof(uint32_t)+frequency.capacity()*sizeof(uint64_t)+order.capacity()*sizeof(uint32_t));
    for(size_t i=0;i<255;++i)result.palette[i]=values[order[i]];
    std::sort(result.palette.begin(),result.palette.begin()+255);
  }
  // 上述排序工作区在分配cache ID前释放。palette[255]只作dummy，永不输出。
  result.ids.resize(cache.size(),255);
  for(size_t i=0;i<cache.size();++i) {
    const auto found=std::lower_bound(result.palette.begin(),result.palette.begin()+255,cache[i]);
    if(found!=result.palette.begin()+255 && *found==cache[i])result.ids[i]=uint32_t(found-result.palette.begin());
  }
  result.temporary_peak_bytes=std::max(result.temporary_peak_bytes,result.ids.capacity()*sizeof(uint32_t));
  result.eligible=true;return result;
}
}
