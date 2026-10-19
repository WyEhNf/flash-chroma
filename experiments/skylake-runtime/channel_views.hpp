#pragma once
#include <cstddef>
#include <cstdint>

namespace jshc_channel {
// 每轴的共享表仍是idx<<17|frac；非共享表把三份17位frac及5位idx压入56位。
// m<=33，所以最大的下单元idx为31；frac=65536的端点单独保留第17位。
struct View {
  const uint32_t* axes[3];
  const uint64_t* triples[3];
  const uint32_t* nodes;
  int32_t sr, sg;
  bool shared;
};
void avx2_chain(const View* chain, size_t stages, uint8_t* rgb, size_t pixels) noexcept;
}
