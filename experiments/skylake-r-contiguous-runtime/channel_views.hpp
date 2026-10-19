#pragma once
#include <cstddef>
#include <cstdint>
namespace jshc_r_contiguous {
struct View {
  const uint32_t* axes[3][3]; // idx<<17 | Q16，保留65536端点。
  const uint32_t* nodes;
  int32_t sr, sg;
  bool shared;
};
void avx2_chain(const View* chain, size_t stages, uint8_t* rgb, size_t pixels) noexcept;
}
