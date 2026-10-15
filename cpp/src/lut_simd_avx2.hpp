#pragma once

#include <cstddef>
#include <cstdint>

namespace jshc::detail {
struct Avx2LutView {
  const uint32_t* axis;
  const uint32_t* nodes;
  int32_t sr;
  int32_t sg;
};

// n must be a multiple of 8. Input/output may be identical; exactly 3*n bytes
// are read and written. Called only after both build and CPU/OS capability checks.
void avx2_chain(const Avx2LutView* chain, size_t stages, const uint8_t* in,
                uint8_t* out, size_t n) noexcept;
void avx2_chain_madd(const Avx2LutView* chain, size_t stages, const uint8_t* in,
                     uint8_t* out, size_t n) noexcept;
void avx2_chain_scalar_gather(const Avx2LutView* chain, size_t stages, const uint8_t* in,
                              uint8_t* out, size_t n) noexcept;
void avx2_chain_exact_float(const Avx2LutView* chain, size_t stages, const uint8_t* in,
                            uint8_t* out, size_t n) noexcept;
}  // namespace jshc::detail
