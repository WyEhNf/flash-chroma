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
  // 2. AVX2 equals scalar on random lattices over the whole cube, for several m.
  for (uint32_t m : {17u, 25u, 33u}) {
    SparseLut R = make_lut(m, false, 1234 + m);
    std::vector<uint8_t> a(n * 3), b(n * 3);
    tetra_scalar(R, cube.data(), a.data(), n);
    tetra_avx2(R, cube.data(), b.data(), n);
    CHECK(std::memcmp(a.data(), b.data(), a.size()) == 0, "avx2 vs scalar");
    // odd lengths exercise tails
    for (size_t len : {1, 7, 9, 10, 11, 17, 1001}) {
      std::vector<uint8_t> x(len * 3 + 16, 0xAB), y(len * 3 + 16, 0xAB);
      tetra_scalar(R, cube.data() + 3 * 12345, x.data(), len);
      tetra_avx2(R, cube.data() + 3 * 12345, y.data(), len);
      CHECK(std::memcmp(x.data(), y.data(), x.size()) == 0, "avx2 tail / no overrun");
    }
  }
  // 3. fused chain == sequential, threads do not matter.
  {
    SparseLut A = make_lut(33, false, 7), B = make_lut(17, false, 8);
    std::vector<uint8_t> seq(cube), fused1(cube), fused8(cube), tmp(n * 3);
    tetra_scalar(A, seq.data(), tmp.data(), n);
    tetra_scalar(B, tmp.data(), seq.data(), n);
    apply_chain({&A, &B}, fused1.data(), n, Kernel::TetraAvx2, 1);
    apply_chain({&A, &B}, fused8.data(), n, Kernel::TetraAvx2, 8);
    CHECK(std::memcmp(seq.data(), fused1.data(), seq.size()) == 0, "chain vs sequential");
    CHECK(std::memcmp(fused1.data(), fused8.data(), seq.size()) == 0, "threads determinism");
  }
  std::printf("%s (%d failures)\n", failures ? "FAILED" : "OK", failures);
  return failures ? 1 : 0;
}
