#pragma once
#include <cstddef>
#include <cstdint>
namespace jshc_axis_preweight {
struct View {
  const uint32_t* axes[3][3]; // idx<<17 | Q16，保留65536端点。
  const uint32_t* nodes;
  int32_t sr, sg;
  bool shared;
  bool delta16; // 非共享且全部G-R/B-R位于int16；axes[1]存双差值，axes[2]不使用。
  bool preweighted; // 共享轴高16位存idx*stride；低16位用65535表示唯一的码255端点。
};
static_assert(sizeof(void*) != 8 || sizeof(View) == 96, "x64私有视图不得因新标志增大");
void avx2_chain(const View* chain, size_t stages, uint8_t* rgb, size_t pixels) noexcept;
}
