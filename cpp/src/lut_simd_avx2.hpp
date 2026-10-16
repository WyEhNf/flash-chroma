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
struct StructuredLutView {
  Avx2LutView generic;
  const uint32_t* curves[3];  // separate 256-entry packed contribution tables
  uint32_t constant_rgb;
  uint8_t path;           // 0=tetra, 1=curve, 2=vertex, 3=constant
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
// Exactly four stages. Proofs must be prepared before dispatch. Generic stages
// retain Q16 round-half-up; vertex stages require the complete prefix proof.
void avx2_structured_chain(const StructuredLutView* chain, const uint8_t* in,
                           uint8_t* out, size_t n) noexcept;
}  // namespace jshc::detail
