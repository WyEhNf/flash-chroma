// C++26 Standard Library SIMD (<simd>) implementation of 8-lane tetrahedral LUT interpolation.
// Strictly portable standard C++: no architecture-specific intrinsics (<immintrin.h>) or inline ASM.
// Supports C++26 std::simd (<simd>, P1928) with seamless fallback to TSv2 (<experimental/simd>).

#include <cstddef>
#include <cstdint>

#if __has_include(<simd>) && __cplusplus >= 202400L
#include <simd>
#define JSHC_CPP_SIMD_BACKEND "C++26 std::simd (<simd>)"
namespace jshc_simd {
using i32x8 = std::simd::vec<int32_t, 8>;
using std::simd::max;
using std::simd::min;
using std::simd::select;
}  // namespace jshc_simd
#elif __has_include(<experimental/simd>)
#include <experimental/simd>
#define JSHC_CPP_SIMD_BACKEND "C++ TSv2 std::experimental::simd (<experimental/simd>)"
namespace jshc_simd {
namespace stx = std::experimental;
using i32x8 = stx::simd<int32_t, stx::simd_abi::deduce_t<int32_t, 8>>;
using stx::max;
using stx::min;
inline i32x8 select(typename i32x8::mask_type mask, i32x8 a, i32x8 b) noexcept {
  stx::where(mask, b) = a;
  return b;
}
}  // namespace jshc_simd
#else
#error "Neither C++26 <simd> nor <experimental/simd> is available"
#endif

namespace {

constexpr int kQ = 16;
constexpr int32_t kHalf = 1 << (kQ - 1);

using jshc_simd::i32x8;
using jshc_simd::max;
using jshc_simd::min;
using jshc_simd::select;

template <typename T>
inline i32x8 gather8(const T* __restrict__ table, const i32x8& idx) noexcept {
  return i32x8([&](int lane) noexcept -> int32_t {
    return static_cast<int32_t>(table[idx[lane]]);
  });
}

inline i32x8 interp_channel(const i32x8& v0, const i32x8& v1, const i32x8& v2, const i32x8& v3,
                            const i32x8& f1, const i32x8& f2, const i32x8& f3, int shift) noexcept {
  const i32x8 mask(0xFF);
  const i32x8 half(kHalf);
  const i32x8 c0 = (v0 >> shift) & mask;
  const i32x8 c1 = (v1 >> shift) & mask;
  const i32x8 c2 = (v2 >> shift) & mask;
  const i32x8 c3 = (v3 >> shift) & mask;

  const i32x8 acc = (c0 << kQ) + (c1 - c0) * f1 + (c2 - c1) * f2 + (c3 - c2) * f3;
  return (acc + half) >> kQ;
}

}  // namespace

extern "C" const char* jshc_cpp_simd_backend_name() noexcept {
  return JSHC_CPP_SIMD_BACKEND;
}

extern "C" void jshc_tetra_cpp_simd(const int32_t* __restrict__ off_table,
                                    const uint32_t* __restrict__ frac_table,
                                    const int32_t* __restrict__ strides,
                                    const uint32_t* __restrict__ packed_nodes,
                                    const uint8_t* __restrict__ in_rgb,
                                    uint8_t* __restrict__ out_rgb,
                                    size_t n) noexcept {
  const int32_t* __restrict__ off_r = off_table;
  const int32_t* __restrict__ off_g = off_table + 256;
  const int32_t* __restrict__ off_b = off_table + 512;

  const uint32_t* __restrict__ frac_r = frac_table;
  const uint32_t* __restrict__ frac_g = frac_table + 256;
  const uint32_t* __restrict__ frac_b = frac_table + 512;

  const i32x8 sr(strides[0]);
  const i32x8 sg(strides[1]);
  const i32x8 sb(strides[2]);
  const i32x8 s_tot = sr + sg + sb;

  size_t i = 0;
  for (; i + 8 <= n; i += 8) {
    const uint8_t* __restrict__ p_in = in_rgb + 3 * i;
    const i32x8 r([&](int lane) noexcept -> int32_t { return p_in[3 * lane + 0]; });
    const i32x8 g([&](int lane) noexcept -> int32_t { return p_in[3 * lane + 1]; });
    const i32x8 b([&](int lane) noexcept -> int32_t { return p_in[3 * lane + 2]; });

    const i32x8 base = gather8(off_r, r) + gather8(off_g, g) + gather8(off_b, b);
    const i32x8 fr = gather8(frac_r, r);
    const i32x8 fg = gather8(frac_g, g);
    const i32x8 fb = gather8(frac_b, b);

    i32x8 f1 = fr;
    i32x8 smax = sr;
    smax = select(fg > f1, sg, smax);
    f1 = max(f1, fg);
    smax = select(fb > f1, sb, smax);
    f1 = max(f1, fb);

    i32x8 f3 = fr;
    i32x8 smin = sr;
    smin = select(fg < f3, sg, smin);
    f3 = min(f3, fg);
    smin = select(fb < f3, sb, smin);
    f3 = min(f3, fb);

    const i32x8 f2 = (fr + fg + fb) - f1 - f3;

    const i32x8 v0 = gather8(packed_nodes, base);
    const i32x8 v1 = gather8(packed_nodes, base + smax);
    const i32x8 v2 = gather8(packed_nodes, base + s_tot - smin);
    const i32x8 v3 = gather8(packed_nodes, base + s_tot);

    const i32x8 out_r = interp_channel(v0, v1, v2, v3, f1, f2, f3, 0);
    const i32x8 out_g = interp_channel(v0, v1, v2, v3, f1, f2, f3, 8);
    const i32x8 out_b = interp_channel(v0, v1, v2, v3, f1, f2, f3, 16);

    uint8_t* __restrict__ p_out = out_rgb + 3 * i;
    for (int lane = 0; lane < 8; ++lane) {
      p_out[3 * lane + 0] = static_cast<uint8_t>(out_r[lane]);
      p_out[3 * lane + 1] = static_cast<uint8_t>(out_g[lane]);
      p_out[3 * lane + 2] = static_cast<uint8_t>(out_b[lane]);
    }
  }
}
