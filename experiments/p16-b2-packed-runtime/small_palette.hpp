// 仅供direct准备：精确发现至多255色，保留whole-cache与原升序ID。
#pragma once
#include <algorithm>
#include <array>
#include <cstddef>
#include <cstdint>

namespace p16_prepare {
struct SmallPalette {
  static constexpr uint32_t empty=0xffffffffu;
  std::array<uint32_t,512> keys;
  std::array<uint8_t,512> sorted_ids;
  std::array<uint32_t,255> values;
  uint16_t count;

  static size_t initial_slot(uint32_t value) noexcept {
    return size_t(uint32_t(value*0x9e3779b1u)>>23);
  }
  size_t slot(uint32_t value) const noexcept {
    size_t position=initial_slot(value);
    // 最多255个占用槽，512槽中必有空位；完整键比较排除碰撞误认。
    while(keys[position]!=empty && keys[position]!=value)position=(position+1)&511;
    return position;
  }
  bool build(const uint32_t* input,size_t entries) noexcept {
    keys.fill(empty);sorted_ids.fill(255);values.fill(0);count=0;
    for(size_t i=0;i<entries;++i) {
      const uint32_t value=input[i];
      // 原cache由三个RGB8字节或零空洞组成；显式拒绝非RGB24键。
      if(value>0xffffffu)return false;
      const size_t position=slot(value);
      if(keys[position]==value)continue;
      if(count==255)return false; // 第256个不同色不插入、不发布direct。
      keys[position]=value;values[count++]=value;
    }
    std::sort(values.begin(),values.begin()+count);
    for(uint16_t i=0;i<count;++i)sorted_ids[slot(values[i])]=uint8_t(i);
    return true;
  }
  uint8_t id(uint32_t value) const noexcept {
    // 调用者仅查询刚刚build成功的同一whole-cache中的键。
    return sorted_ids[slot(value)];
  }
};
}
