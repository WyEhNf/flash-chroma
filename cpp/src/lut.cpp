#include "jshc/lut.hpp"

#include <algorithm>
#include <cmath>
#include <cstdio>
#include <cstring>
#include <cstdlib>
#include <stdexcept>
#include <utility>

#if defined(_OPENMP)
#include <omp.h>
#endif

namespace jshc {

namespace {

std::vector<uint8_t> read_binary_file(const std::string& path) {
  FILE* f = std::fopen(path.c_str(), "rb");
  if (!f) throw std::runtime_error("cannot open " + path);
  if (std::fseek(f, 0, SEEK_END) != 0) {
    std::fclose(f);
    throw std::runtime_error("cannot seek " + path);
  }
  const long sz = std::ftell(f);
  if (sz < 0 || std::fseek(f, 0, SEEK_SET) != 0) {
    std::fclose(f);
    throw std::runtime_error("cannot size " + path);
  }
  std::vector<uint8_t> buf(static_cast<size_t>(sz));
  if (sz > 0 && std::fread(buf.data(), 1, buf.size(), f) != buf.size()) {
    std::fclose(f);
    throw std::runtime_error("short read " + path);
  }
  std::fclose(f);
  return buf;
}

inline void compare_and_swap_axis(int32_t& f_hi, int32_t& s_hi, int32_t& f_lo, int32_t& s_lo) {
  if (f_lo > f_hi) {
    std::swap(f_hi, f_lo);
    std::swap(s_hi, s_lo);
  }
}

// Algebraic telescoping of tetrahedral barycentric weights:
//   c0*(kOne - f1) + c1*(f1 - f2) + c2*(f2 - f3) + c3*f3
// = (c0 << kQ) + (c1 - c0)*f1 + (c2 - c1)*f2 + (c3 - c2)*f3
inline uint8_t interpolate_channel(int32_t c0, int32_t c1, int32_t c2, int32_t c3,
                                   int32_t f1, int32_t f2, int32_t f3) {
  const int32_t acc = (c0 << kQ) + (c1 - c0) * f1 + (c2 - c1) * f2 + (c3 - c2) * f3;
  return static_cast<uint8_t>((acc + kHalf) >> kQ);
}

inline void tetra_pixel(const SparseLut& L, const uint8_t* __restrict__ in,
                        uint8_t* __restrict__ out) {
  const uint8_t r = in[0];
  const uint8_t g = in[1];
  const uint8_t b = in[2];

  const int32_t base = L.off[0][r] + L.off[1][g] + L.off[2][b];

  int32_t f1 = static_cast<int32_t>(L.frac[0][r]);
  int32_t f2 = static_cast<int32_t>(L.frac[1][g]);
  int32_t f3 = static_cast<int32_t>(L.frac[2][b]);

  int32_t s1 = L.stride[0];
  int32_t s2 = L.stride[1];
  int32_t s3 = L.stride[2];

  // 3-comparator sorting network orders (f1 >= f2 >= f3) and their grid strides (s1, s2, s3)
  compare_and_swap_axis(f1, s1, f2, s2);
  compare_and_swap_axis(f1, s1, f3, s3);
  compare_and_swap_axis(f2, s2, f3, s3);

  const RgbaNode* __restrict__ nodes = L.rgba_nodes.data() + base;
  const RgbaNode v0 = nodes[0];
  const RgbaNode v1 = nodes[s1];
  const RgbaNode v2 = nodes[s1 + s2];
  const RgbaNode v3 = nodes[s1 + s2 + s3];

  out[0] = interpolate_channel(v0.r, v1.r, v2.r, v3.r, f1, f2, f3);
  out[1] = interpolate_channel(v0.g, v1.g, v2.g, v3.g, f1, f2, f3);
  out[2] = interpolate_channel(v0.b, v1.b, v2.b, v3.b, f1, f2, f3);
}

}  // namespace

// ---- File I/O & Table Preparation -----------------------------------------------------

FullLut FullLut::load(const std::string& path) {
  FullLut L;
  L.data = read_binary_file(path);
  if (L.data.size() != 256u * 256u * 256u * 3u) {
    throw std::runtime_error("bad full LUT size: " + path);
  }
  return L;
}

SparseLut SparseLut::load(const std::string& path) {
  const auto buf = read_binary_file(path);
  if (buf.size() < 16) throw std::runtime_error("truncated slut: " + path);
  const uint8_t* p = buf.data();
  const uint8_t* const end = p + buf.size();

  auto take = [&](void* dst, size_t n) {
    if (n > static_cast<size_t>(end - p)) throw std::runtime_error("truncated slut: " + path);
    std::memcpy(dst, p, n);
    p += n;
  };

  char magic[4];
  take(magic, 4);
  if (std::memcmp(magic, "SLUT", 4) != 0) throw std::runtime_error("bad magic: " + path);

  uint32_t version = 0, reserved = 0;
  SparseLut L;
  take(&version, 4);
  take(&L.m, 4);
  take(&reserved, 4);
  if (version != 1 || reserved != 0 || L.m < 2 || L.m > 256)
    throw std::runtime_error("bad slut header: " + path);

  for (int a = 0; a < 3; ++a) {
    L.grid[a].resize(L.m);
    take(L.grid[a].data(), 4 * L.m);
  }
  take(L.idx, sizeof(L.idx));
  take(L.frac, sizeof(L.frac));

  L.nodes.resize(static_cast<size_t>(L.m) * L.m * L.m * 3);
  take(L.nodes.data(), L.nodes.size());
  if (p != end) throw std::runtime_error("trailing slut data: " + path);

  for (int a = 0; a < 3; ++a) {
    for (int x = 0; x < 256; ++x) {
      if (L.idx[a][x] > L.m - 2 || L.frac[a][x] > static_cast<uint32_t>(kOne)) {
        throw std::runtime_error("bad slut tables: " + path);
      }
    }
  }
  L.prepare();
  return L;
}

void SparseLut::save(const std::string& path) const {
  FILE* f = std::fopen(path.c_str(), "wb");
  if (!f) throw std::runtime_error("cannot write " + path);
  const uint32_t version = 1, reserved = 0;
  std::fwrite("SLUT", 1, 4, f);
  std::fwrite(&version, 4, 1, f);
  std::fwrite(&m, 4, 1, f);
  std::fwrite(&reserved, 4, 1, f);
  for (int a = 0; a < 3; ++a) std::fwrite(grid[a].data(), 4, m, f);
  std::fwrite(idx, 1, sizeof(idx), f);
  std::fwrite(frac, 1, sizeof(frac), f);
  std::fwrite(nodes.data(), 1, nodes.size(), f);
  std::fclose(f);
}

void SparseLut::prepare() {
  stride[0] = static_cast<int32_t>(m * m);
  stride[1] = static_cast<int32_t>(m);
  stride[2] = 1;

  for (int a = 0; a < 3; ++a) {
    for (int x = 0; x < 256; ++x) {
      off[a][x] = static_cast<int32_t>(idx[a][x]) * stride[a];
    }
  }

  const size_t n = static_cast<size_t>(m) * m * m;
  rgba_nodes.resize(n + 16);
  packed.resize(n + 16, 0);
  for (size_t i = 0; i < n; ++i) {
    const uint8_t r = nodes[3 * i];
    const uint8_t g = nodes[3 * i + 1];
    const uint8_t b = nodes[3 * i + 2];
    rgba_nodes[i] = RgbaNode{r, g, b, 0};
    packed[i] = static_cast<uint32_t>(r) | (static_cast<uint32_t>(g) << 8) |
                (static_cast<uint32_t>(b) << 16);
  }
}

// ---- External Portable SIMD Symbols (C++26 <simd>, Zig @Vector, Rust std::simd) -------

extern "C" {
void jshc_tetra_cpp_simd(const int32_t* off_table, const uint32_t* frac_table,
                         const int32_t* strides, const uint32_t* packed_nodes,
                         const uint8_t* in_rgb, uint8_t* out_rgb, size_t n) noexcept;
void jshc_tetra_zig_simd(const int32_t* off_table, const uint32_t* frac_table,
                         const int32_t* strides, const uint32_t* packed_nodes,
                         const uint8_t* in_rgb, uint8_t* out_rgb, size_t n) noexcept;
void jshc_tetra_zig_simd4(const int32_t*, const uint32_t*, const int32_t*, const uint32_t*,
                          const uint8_t*, uint8_t*, size_t) noexcept;
void jshc_tetra_zig_simd16(const int32_t*, const uint32_t*, const int32_t*, const uint32_t*,
                           const uint8_t*, uint8_t*, size_t) noexcept;
void jshc_tetra_rust_simd(const int32_t* off_table, const uint32_t* frac_table,
                          const int32_t* strides, const uint32_t* packed_nodes,
                          size_t packed_len, const uint8_t* in_rgb, uint8_t* out_rgb,
                          size_t n) noexcept;
}

// ---- Kernel Dispatch & Portable Implementations ---------------------------------------

Kernel parse_kernel(const std::string& s) {
  if (s == "tetra" || s == "tetra_scalar" || s == "portable" || s == "tetra_portable") {
    return Kernel::TetraScalar;
  }
  if (s == "tetra_cpp_simd" || s == "cpp_simd" || s == "cpp26_simd") return Kernel::TetraCppSimd;
  if (s == "tetra_zig_simd" || s == "zig_simd" || s == "zig") return Kernel::TetraZigSimd;
  if (s == "tetra_zig_simd4") return Kernel::TetraZigSimd4;
  if (s == "tetra_zig_simd16") return Kernel::TetraZigSimd16;
  if (s == "tetra_rust_simd" || s == "rust_simd" || s == "rust") return Kernel::TetraRustSimd;
  if (s == "tetra_avx2" || s == "avx2") return Kernel::TetraAvx2;
  if (s == "tetra_asm" || s == "asm") return Kernel::TetraAsm;
  if (s == "tri" || s == "tri_float") return Kernel::TriFloat;
  throw std::runtime_error("unknown kernel " + s);
}

const char* kernel_name(Kernel k) {
  switch (k) {
    case Kernel::TetraScalar: return "tetra_scalar";
    case Kernel::TetraCppSimd: return "tetra_cpp_simd";
    case Kernel::TetraZigSimd: return "tetra_zig_simd";
    case Kernel::TetraZigSimd4: return "tetra_zig_simd4";
    case Kernel::TetraZigSimd16: return "tetra_zig_simd16";
    case Kernel::TetraRustSimd: return "tetra_rust_simd";
    case Kernel::TetraAvx2: return "tetra_avx2";
    case Kernel::TetraAsm: return "tetra_asm";
    case Kernel::TriFloat: return "tri_float";
  }
  return "?";
}

bool avx2_available() { return false; }

void tetra_scalar(const SparseLut& L, const uint8_t* in, uint8_t* out, size_t n) {
  for (size_t i = 0; i < n; ++i) {
    tetra_pixel(L, in + 3 * i, out + 3 * i);
  }
}

void tetra_cpp_simd(const SparseLut& L, const uint8_t* in, uint8_t* out, size_t n) {
  const size_t vec_n = n & ~static_cast<size_t>(7);
  if (vec_n > 0) {
    jshc_tetra_cpp_simd(&L.off[0][0], &L.frac[0][0], L.stride, L.packed.data(), in, out, vec_n);
  }
  if (vec_n < n) {
    tetra_scalar(L, in + 3 * vec_n, out + 3 * vec_n, n - vec_n);
  }
}

void tetra_zig_simd_lanes(const SparseLut& L, const uint8_t* in, uint8_t* out, size_t n,
                          size_t lanes) {
  const size_t vec_n = n - n % lanes;
  if (vec_n > 0) {
    auto fn = lanes == 4 ? jshc_tetra_zig_simd4 :
              lanes == 16 ? jshc_tetra_zig_simd16 : jshc_tetra_zig_simd;
    fn(&L.off[0][0], &L.frac[0][0], L.stride, L.packed.data(), in, out, vec_n);
  }
  if (vec_n < n) {
    tetra_scalar(L, in + 3 * vec_n, out + 3 * vec_n, n - vec_n);
  }
}

void tetra_zig_simd(const SparseLut& L, const uint8_t* in, uint8_t* out, size_t n) {
  tetra_zig_simd_lanes(L, in, out, n, 8);
}

void tetra_rust_simd(const SparseLut& L, const uint8_t* in, uint8_t* out, size_t n) {
  const size_t vec_n = n & ~static_cast<size_t>(7);
  if (vec_n > 0) {
    jshc_tetra_rust_simd(&L.off[0][0], &L.frac[0][0], L.stride, L.packed.data(), L.packed.size(),
                         in, out, vec_n);
  }
  if (vec_n < n) {
    tetra_scalar(L, in + 3 * vec_n, out + 3 * vec_n, n - vec_n);
  }
}

void tetra_avx2(const SparseLut& L, const uint8_t* in, uint8_t* out, size_t n) {
  tetra_cpp_simd(L, in, out, n);
}

void tetra_asm(const SparseLut& L, const uint8_t* in, uint8_t* out, size_t n) {
  tetra_cpp_simd(L, in, out, n);
}

void tri_float(const SparseLut& L, const uint8_t* in, uint8_t* out, size_t n) {
  const int32_t sr = L.stride[0], sg = L.stride[1], sb = L.stride[2];
  const float inv = 1.0f / static_cast<float>(kOne);
  const uint8_t* const N = L.nodes.data();

  for (size_t i = 0; i < n; ++i) {
    const int r = in[3 * i], g = in[3 * i + 1], b = in[3 * i + 2];
    const int32_t base = L.off[0][r] + L.off[1][g] + L.off[2][b];
    const float x = static_cast<float>(L.frac[0][r]) * inv;
    const float y = static_cast<float>(L.frac[1][g]) * inv;
    const float z = static_cast<float>(L.frac[2][b]) * inv;

    for (int c = 0; c < 3; ++c) {
      auto sample = [&](int32_t offset) { return static_cast<float>(N[3 * (base + offset) + c]); };
      const float c00 = sample(0) + (sample(sb) - sample(0)) * z;
      const float c01 = sample(sg) + (sample(sg + sb) - sample(sg)) * z;
      const float c10 = sample(sr) + (sample(sr + sb) - sample(sr)) * z;
      const float c11 = sample(sr + sg) + (sample(sr + sg + sb) - sample(sr + sg)) * z;
      const float c0 = c00 + (c01 - c00) * y;
      const float c1 = c10 + (c11 - c10) * y;
      const int q = static_cast<int>(std::lround(c0 + (c1 - c0) * x));
      out[3 * i + c] = static_cast<uint8_t>(std::clamp(q, 0, 255));
    }
  }
}

// ---- Multi-Stage Chain Execution ------------------------------------------------------

static void run_kernel(Kernel k, const SparseLut& L, const uint8_t* in, uint8_t* out, size_t n) {
  switch (k) {
    case Kernel::TetraScalar:
      tetra_scalar(L, in, out, n);
      break;
    case Kernel::TetraCppSimd:
    case Kernel::TetraAvx2:
    case Kernel::TetraAsm:
      tetra_cpp_simd(L, in, out, n);
      break;
    case Kernel::TetraZigSimd:
      tetra_zig_simd(L, in, out, n);
      break;
    case Kernel::TetraZigSimd4:
      tetra_zig_simd_lanes(L, in, out, n, 4);
      break;
    case Kernel::TetraZigSimd16:
      tetra_zig_simd_lanes(L, in, out, n, 16);
      break;
    case Kernel::TetraRustSimd:
      tetra_rust_simd(L, in, out, n);
      break;
    case Kernel::TriFloat:
      tri_float(L, in, out, n);
      break;
  }
}

void apply_chain(const std::vector<const SparseLut*>& chain, uint8_t* rgb, size_t n, Kernel k,
                 int threads) {
  const size_t num_stages = chain.size();
  if (num_stages == 0 || n == 0) return;

  // Bounded portable tuning knob. The default matches the archived baseline.
  const size_t kBlockPixels = [] {
    const char* raw = std::getenv("JSHC_BLOCK_PIXELS");
    if (!raw) return size_t{4096};
    const int v = std::atoi(raw);
    if (v != 1024 && v != 4096 && v != 8192) throw std::runtime_error("JSHC_BLOCK_PIXELS must be 1024, 4096 or 8192");
    return static_cast<size_t>(v);
  }();
  const size_t num_blocks = (n + kBlockPixels - 1) / kBlockPixels;

#if defined(_OPENMP)
  const int num_threads = (threads > 0) ? threads : omp_get_max_threads();
  if (std::getenv("OMP_SCHEDULE") == nullptr) omp_set_schedule(omp_sched_dynamic, 1);
#pragma omp parallel num_threads(num_threads)
#endif
  {
    std::array<uint8_t, 8192 * 3> buf_a{};
    std::array<uint8_t, 8192 * 3> buf_b{};

#if defined(_OPENMP)
#pragma omp for schedule(runtime)
#endif
    for (long long bi = 0; bi < static_cast<long long>(num_blocks); ++bi) {
      const size_t start = static_cast<size_t>(bi) * kBlockPixels;
      const size_t len = std::min(kBlockPixels, n - start);
      uint8_t* const block_rgb = rgb + 3 * start;

      if (num_stages == 1) {
        run_kernel(k, *chain[0], block_rgb, block_rgb, len);
        continue;
      }

      const uint8_t* src = block_rgb;
      uint8_t* dst = buf_a.data();
      for (size_t stage = 0; stage < num_stages; ++stage) {
        uint8_t* const out_ptr = (stage + 1 == num_stages) ? block_rgb : dst;
        run_kernel(k, *chain[stage], src, out_ptr, len);
        src = out_ptr;
        dst = (dst == buf_a.data()) ? buf_b.data() : buf_a.data();
      }
    }
  }
  (void)threads;
}

void apply_full_chain(const std::vector<const FullLut*>& chain, uint8_t* rgb, size_t n,
                      int threads) {
#if defined(_OPENMP)
  const int num_threads = (threads > 0) ? threads : omp_get_max_threads();
#pragma omp parallel for schedule(static) num_threads(num_threads)
#endif
  for (long long i = 0; i < static_cast<long long>(n); ++i) {
    uint8_t* const p = rgb + 3 * i;
    for (const FullLut* L : chain) {
      const size_t offset =
          ((static_cast<size_t>(p[0]) << 16) | (static_cast<size_t>(p[1]) << 8) | p[2]) * 3;
      p[0] = L->data[offset];
      p[1] = L->data[offset + 1];
      p[2] = L->data[offset + 2];
    }
  }
  (void)threads;
}

}  // namespace jshc
