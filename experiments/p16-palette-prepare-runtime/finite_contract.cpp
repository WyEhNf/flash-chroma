// 固定有限合同：独立std::sort真值，不执行真实模型或性能计时。
#include "small_palette.hpp"
#include <algorithm>
#include <cstdio>
#include <stdexcept>
#include <vector>

namespace {
void require(bool good,const char* message) {
  if(!good)throw std::runtime_error(message);
}
void check(const std::vector<uint32_t>& input,bool expected,size_t expected_count) {
  auto truth=input;
  std::sort(truth.begin(),truth.end());
  truth.erase(std::unique(truth.begin(),truth.end()),truth.end());
  require(truth.size()==expected_count,"合同色数与独立sort真值不同");
  p16_prepare::SmallPalette dictionary;
  const bool accepted=dictionary.build(input.data(),input.size());
  require(accepted==expected,"255边界资格不同");
  if(!accepted)return;
  require(dictionary.count==truth.size(),"去重数量不同");
  require(std::equal(truth.begin(),truth.end(),dictionary.values.begin()),"升序palette不同");
  for(uint32_t value:input) {
    const auto id=std::lower_bound(truth.begin(),truth.end(),value)-truth.begin();
    require(dictionary.id(value)==id,"完整键/排序ID映射不同");
  }
  for(size_t i=truth.size();i<dictionary.values.size();++i)
    require(dictionary.values[i]==0,"未用palette元素没有保留零");
}
}
int main() {
  try {
    check({},true,0);
    check({0,0,0},true,1);
    check({0xffffffu,0,0xffffffu,0,1},true,3);
    std::vector<uint32_t> ascending;
    for(uint32_t i=0;i<255;++i)ascending.push_back(i*65793u);
    check(ascending,true,255);
    std::reverse(ascending.begin(),ascending.end());
    check(ascending,true,255);
    ascending.push_back(0xffffffu);check(ascending,false,256);
    std::vector<uint32_t> conflicts;
    for(uint32_t key=0;key<=0xffffffu && conflicts.size()<256;++key)
      if(p16_prepare::SmallPalette::initial_slot(key)==510)conflicts.push_back(key);
    require(conflicts.size()==256,"未建立固定同槽碰撞合同");
    std::vector<uint32_t> first255(conflicts.begin(),conflicts.begin()+255);
    check(first255,true,255);
    p16_prepare::SmallPalette dictionary;
    require(dictionary.build(first255.data(),first255.size()),"255最坏碰撞被拒绝");
    for(size_t i=0;i<255;++i)
      require(dictionary.keys[(510+i)&511]==first255[i],"最坏线性探测/环绕未完整覆盖");
    check(conflicts,false,256);
    std::reverse(conflicts.begin(),conflicts.end());check(conflicts,false,256);
    std::vector<uint32_t> holes(4096,0);
    for(uint32_t i=1;i<255;++i)holes[7*i]=i*511u;
    check(holes,true,255);
    // 255个非零输出自身合格，但完整cache的零空洞构成第256色，必须拒绝。
    holes[2047]=255u*511u;check(holes,false,256);
    std::vector<uint32_t> mixed;
    for(uint32_t i=0;i<8192;++i)mixed.push_back(((i*73u)%253u)*65537u);
    check(mixed,true,253);
    const uint32_t invalid=0xffffffffu;
    require(!dictionary.build(&invalid,1),"空哨兵不能冒充合法RGB24");
    std::printf("{\"passed\":true,\"finite_cases\":13,\"fixed_array_bytes\":3580,\"scratch_object_bytes\":%zu,\"worst_same_bucket_distinct_keys\":256,\"whole_cache_hole_boundary\":true}\n",sizeof(dictionary));
    return 0;
  } catch(const std::exception& error) {
    std::fprintf(stderr,"%s\n",error.what());return 1;
  }
}
