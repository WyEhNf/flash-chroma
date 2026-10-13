// Kernel self-tests: AVX2 == scalar bit-exactly, identity lattice is exact, chain fusion
// equals sequential application, multithreading does not change results.
#include <cstdio>
#include <cstdlib>
#include <cstring>
#include <random>
#include <vector>

#include "jshc/lut.hpp"

using namespace jshc;

static int failures = 0;
#define CHECK(cond, msg)                                   \
  do {                                                     \
    if (!(cond)) {                                         \
      std::fprintf(stderr, "FAIL %s:%d %s\n", __FILE__, __LINE__, msg); \
      ++failures;                                          \
    }                                                      \
  } while (0)

static SparseLut make_lut(uint32_t m, bool identity, uint32_t seed) {
  SparseLut L;
  L.m = m;
  for (int a = 0; a < 3; ++a) {
    L.grid[a].resize(m);
    for (uint32_t i = 0; i < m; ++i) L.grid[a][i] = float(i * 255.0 / (m - 1));
    for (int x = 0; x < 256; ++x) {
      double pos = x * double(m - 1) / 255.0;
      int i = int(pos);
      if (i > int(m) - 2) i = int(m) - 2;
      L.idx[a][x] = uint8_t(i);
      L.frac[a][x] = uint32_t((pos - i) * kOne + 0.5);
    }
  }
  L.nodes.resize(size_t(m) * m * m * 3);
  std::mt19937 rng(seed);
  for (uint32_t i = 0; i < m; ++i)
    for (uint32_t j = 0; j < m; ++j)
      for (uint32_t k = 0; k < m; ++k) {
        uint8_t* p = &L.nodes[((size_t(i) * m + j) * m + k) * 3];
        if (identity) {
          p[0] = uint8_t(i * 255 / (m - 1));
          p[1] = uint8_t(j * 255 / (m - 1));
          p[2] = uint8_t(k * 255 / (m - 1));
        } else {
          for (int c = 0; c < 3; ++c) p[c] = uint8_t(rng() & 255);
        }
      }
  L.prepare();
  return L;
}

int main() {
  const size_t n = size_t(1) << 24;
  std::vector<uint8_t> cube(n * 3);
  for (size_t i = 0; i < n; ++i) {
    cube[3 * i] = uint8_t(i >> 16);
    cube[3 * i + 1] = uint8_t(i >> 8);
    cube[3 * i + 2] = uint8_t(i);
  }

  // 1. identity lattice with integer node positions (m=18 -> spacing 15) is exact.
  {
    SparseLut I = make_lut(18, true, 0);
    std::vector<uint8_t> out(n * 3);
    tetra_scalar(I, cube.data(), out.data(), n);
    CHECK(std::memcmp(out.data(), cube.data(), out.size()) == 0, "identity tetra_scalar");
    tri_float(I, cube.data(), out.data(), n);
    CHECK(std::memcmp(out.data(), cube.data(), out.size()) == 0, "identity tri_float");
  }
  // 2. C++26 <simd>, Zig @Vector, and Rust std::simd equal scalar bit-exactly over the whole 2^24 cube.
  for (uint32_t m : {17u, 25u, 33u}) {
    SparseLut R = make_lut(m, false, 1234 + m);
    std::vector<uint8_t> ref(n * 3), out_cpp(n * 3), out_zig(n * 3), out_rust(n * 3);
    tetra_scalar(R, cube.data(), ref.data(), n);
    tetra_cpp_simd(R, cube.data(), out_cpp.data(), n);
    tetra_zig_simd(R, cube.data(), out_zig.data(), n);
    CHECK(std::memcmp(ref.data(), out_zig.data(), ref.size()) == 0, "zig default vs scalar");
    tetra_zig_simd_lanes(R, cube.data(), out_zig.data(), n, 4);
    CHECK(std::memcmp(ref.data(), out_zig.data(), ref.size()) == 0, "zig 4 lanes vs scalar");
    tetra_zig_simd_lanes(R, cube.data(), out_zig.data(), n, 8);
    CHECK(std::memcmp(ref.data(), out_zig.data(), ref.size()) == 0, "zig 8 lanes vs scalar");
    tetra_zig_simd_lanes(R, cube.data(), out_zig.data(), n, 16);
    tetra_rust_simd(R, cube.data(), out_rust.data(), n);
    CHECK(std::memcmp(ref.data(), out_cpp.data(), ref.size()) == 0, "cpp26_simd vs scalar");
    CHECK(std::memcmp(ref.data(), out_zig.data(), ref.size()) == 0, "zig_simd vs scalar");
    CHECK(std::memcmp(ref.data(), out_rust.data(), ref.size()) == 0, "rust_simd vs scalar");
    // odd lengths exercise tails and check for buffer overruns
    for (size_t len : {1, 7, 9, 10, 11, 17, 1001}) {
      std::vector<uint8_t> x(len * 3 + 16, 0xAB);
      std::vector<uint8_t> y_cpp(len * 3 + 16, 0xAB);
      std::vector<uint8_t> y_zig(len * 3 + 16, 0xAB);
      std::vector<uint8_t> y_rust(len * 3 + 16, 0xAB);
      tetra_scalar(R, cube.data() + 3 * 12345, x.data(), len);
      tetra_cpp_simd(R, cube.data() + 3 * 12345, y_cpp.data(), len);
      tetra_zig_simd(R, cube.data() + 3 * 12345, y_zig.data(), len);
      tetra_rust_simd(R, cube.data() + 3 * 12345, y_rust.data(), len);
      CHECK(std::memcmp(x.data(), y_cpp.data(), x.size()) == 0, "cpp26_simd tail / no overrun");
      CHECK(std::memcmp(x.data(), y_zig.data(), x.size()) == 0, "zig_simd tail / no overrun");
      for (size_t lanes : {4u, 8u, 16u}) {
        tetra_zig_simd_lanes(R, cube.data() + 3 * 12345, y_zig.data(), len, lanes);
        CHECK(std::memcmp(x.data(), y_zig.data(), x.size()) == 0, "zig lane tail / no overrun");
      }
      CHECK(std::memcmp(x.data(), y_rust.data(), x.size()) == 0, "rust_simd tail / no overrun");
    }
  }
  // 3. fused chain == sequential across all portable SIMD backends, threads do not matter.
  {
    SparseLut A = make_lut(33, false, 7), B = make_lut(17, false, 8);
    std::vector<uint8_t> seq(cube), f_cpp(cube), f_zig(cube), f_rust(cube), tmp(n * 3);
    tetra_scalar(A, seq.data(), tmp.data(), n);
    tetra_scalar(B, tmp.data(), seq.data(), n);
    apply_chain({&A, &B}, f_cpp.data(), n, Kernel::TetraCppSimd, 8);
    apply_chain({&A, &B}, f_zig.data(), n, Kernel::TetraZigSimd, 8);
    apply_chain({&A, &B}, f_rust.data(), n, Kernel::TetraRustSimd, 8);
    CHECK(std::memcmp(seq.data(), f_cpp.data(), seq.size()) == 0, "chain cpp_simd vs sequential");
    CHECK(std::memcmp(seq.data(), f_zig.data(), seq.size()) == 0, "chain zig_simd vs sequential");
    CHECK(std::memcmp(seq.data(), f_rust.data(), seq.size()) == 0, "chain rust_simd vs sequential");
  }
  // 4. fit_r14 native C++ offline solver on identity 256^3 LUT.
  {
    FullLut F;
    F.data = cube;
    SparseLut S = fit_r14({&F, &F}, 18, 4, false);
    std::vector<uint8_t> out(n * 3);
    tetra_asm(S, cube.data(), out.data(), n);
    CHECK(std::memcmp(out.data(), cube.data(), out.size()) == 0, "fit_r14 identity exactness");
  }
  std::printf("%s (%d failures)\n", failures ? "FAILED" : "OK", failures);
  return failures ? 1 : 0;
}
