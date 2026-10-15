#include "jshc/lut.hpp"
#include "lut_simd_avx2.hpp"

#include <algorithm>
#include <atomic>
#include <cmath>
#include <cstdio>
#include <cstring>
#include <cstdlib>
#include <limits>
#include <stdexcept>
#include <utility>

#if defined(_MSC_VER) && (defined(_M_X64) || defined(_M_IX86))
#include <intrin.h>
#elif defined(__x86_64__) || defined(__i386__)
#include <cpuid.h>
#endif

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

inline void tetra_pixel(const SparseLut& L, const uint8_t* in, uint8_t* out) {
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

  const uint8_t* const nodes = L.nodes.data() + 3 * base;
  const uint8_t* const v0 = nodes;
  const uint8_t* const v1 = nodes + 3 * s1;
  const uint8_t* const v2 = nodes + 3 * (s1 + s2);
  const uint8_t* const v3 = nodes + 3 * (s1 + s2 + s3);
  for (int c = 0; c < 3; ++c)
    out[c] = interpolate_channel(v0[c], v1[c], v2[c], v3[c], f1, f2, f3);
}

void scalar_chain(const std::vector<const SparseLut*>& chain, uint8_t* rgb, size_t n) {
  for (size_t i = 0; i < n; ++i) {
    uint8_t pixel[3] = {rgb[3 * i], rgb[3 * i + 1], rgb[3 * i + 2]};
    for (const SparseLut* L : chain) tetra_pixel(*L, pixel, pixel);
    std::memcpy(rgb + 3 * i, pixel, 3);
  }
}

size_t block_pixels() {
  const char* raw = std::getenv("JSHC_BLOCK_PIXELS");
  if (!raw) return 4096;
  if (std::strcmp(raw, "1024") == 0) return 1024;
  if (std::strcmp(raw, "4096") == 0) return 4096;
  if (std::strcmp(raw, "8192") == 0) return 8192;
  throw std::runtime_error("JSHC_BLOCK_PIXELS must be 1024, 4096 or 8192");
}

bool is_avx2_kernel(Kernel k) {
  return k == Kernel::TetraAvx2 || k == Kernel::TetraAvx2Madd ||
         k == Kernel::TetraAvx2ScalarGather || k == Kernel::TetraAvx2ExactFloat;
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
  if (m < 2 || m > 256 || nodes.size() != static_cast<size_t>(m) * m * m * 3)
    throw std::runtime_error("cannot save malformed sparse LUT: " + path);
  for (const auto& axis : grid)
    if (axis.size() != m) throw std::runtime_error("cannot save malformed grid: " + path);
  FILE* f = std::fopen(path.c_str(), "wb");
  if (!f) throw std::runtime_error("cannot write " + path);
  bool written = true;
  auto write = [&](const void* data, size_t bytes) {
    if (written && std::fwrite(data, 1, bytes, f) != bytes) written = false;
  };
  const uint32_t version = 1, reserved = 0;
  write("SLUT", 4);
  write(&version, 4);
  write(&m, 4);
  write(&reserved, 4);
  for (const auto& axis : grid) write(axis.data(), 4 * m);
  write(idx, sizeof(idx));
  write(frac, sizeof(frac));
  write(nodes.data(), nodes.size());
  const int close_result = std::fclose(f);
  if (!written || close_result != 0) throw std::runtime_error("short write or close failure: " + path);
}

void SparseLut::prepare() {
  if (m < 2 || m > 256 || nodes.size() != static_cast<size_t>(m) * m * m * 3)
    throw std::runtime_error("bad sparse LUT shape");
  stride[0] = static_cast<int32_t>(m * m);
  stride[1] = static_cast<int32_t>(m);
  stride[2] = 1;

  for (int a = 0; a < 3; ++a) {
    for (int x = 0; x < 256; ++x) {
      if (idx[a][x] > m - 2 || frac[a][x] > static_cast<uint32_t>(kOne))
        throw std::runtime_error("bad sparse LUT axis table");
      off[a][x] = static_cast<int32_t>(idx[a][x]) * stride[a];
    }
  }

  std::atomic_store(&packed_cache_, std::shared_ptr<const PackedTables>{});
}

const SparseLut::PackedTables& SparseLut::packed_tables() const {
  auto cached = std::atomic_load(&packed_cache_);
  if (cached) return *cached;
  auto tables = std::make_shared<PackedTables>();
  for (int a = 0; a < 3; ++a)
    for (int x = 0; x < 256; ++x)
      tables->axis[256 * a + x] = (static_cast<uint32_t>(idx[a][x]) << 17) | frac[a][x];
  const size_t n = nodes.size() / 3;
  tables->nodes.resize(n);
  for (size_t i = 0; i < n; ++i) {
    const uint8_t r = nodes[3 * i];
    const uint8_t g = nodes[3 * i + 1];
    const uint8_t b = nodes[3 * i + 2];
    tables->nodes[i] = static_cast<uint32_t>(r) | (static_cast<uint32_t>(g) << 8) |
                (static_cast<uint32_t>(b) << 16);
  }
  std::shared_ptr<const PackedTables> desired = tables;
  if (std::atomic_compare_exchange_strong(&packed_cache_, &cached, desired)) return *desired;
  return *cached;
}

size_t SparseLut::runtime_bytes() const {
  size_t bytes = sizeof(*this) + nodes.capacity();
  for (const auto& axis : grid) bytes += axis.capacity() * sizeof(float);
  const auto tables = std::atomic_load(&packed_cache_);
  if (tables) bytes += sizeof(PackedTables) + tables->nodes.capacity() * sizeof(uint32_t);
  return bytes;
}

// ---- External Portable SIMD Symbols (C++26 <simd>, Zig @Vector, Rust std::simd) -------

extern "C" {
#if defined(JSHC_HAVE_CPP_SIMD)
void jshc_tetra_cpp_simd(const int32_t* off_table, const uint32_t* frac_table,
                         const int32_t* strides, const uint32_t* packed_nodes,
                         const uint8_t* in_rgb, uint8_t* out_rgb, size_t n) noexcept;
#endif
#if defined(JSHC_HAVE_ZIG)
void jshc_tetra_zig_simd(const int32_t* off_table, const uint32_t* frac_table,
                         const int32_t* strides, const uint32_t* packed_nodes,
                         const uint8_t* in_rgb, uint8_t* out_rgb, size_t n) noexcept;
void jshc_tetra_zig_simd4(const int32_t*, const uint32_t*, const int32_t*, const uint32_t*,
                          const uint8_t*, uint8_t*, size_t) noexcept;
void jshc_tetra_zig_simd16(const int32_t*, const uint32_t*, const int32_t*, const uint32_t*,
                           const uint8_t*, uint8_t*, size_t) noexcept;
#endif
#if defined(JSHC_HAVE_RUST)
void jshc_tetra_rust_simd(const int32_t* off_table, const uint32_t* frac_table,
                          const int32_t* strides, const uint32_t* packed_nodes,
                          size_t packed_len, const uint8_t* in_rgb, uint8_t* out_rgb,
                          size_t n) noexcept;
#endif
}

// ---- Kernel Dispatch & Portable Implementations ---------------------------------------

Kernel parse_kernel(const std::string& s) {
  if (s == "auto" || s == "tetra_auto") return Kernel::TetraAuto;
  if (s == "tetra" || s == "tetra_scalar" || s == "portable" || s == "tetra_portable") {
    return Kernel::TetraScalar;
  }
  if (s == "tetra_cpp_simd" || s == "cpp_simd" || s == "cpp26_simd") return Kernel::TetraCppSimd;
  if (s == "tetra_zig_simd" || s == "zig_simd" || s == "zig") return Kernel::TetraZigSimd;
  if (s == "tetra_zig_simd4") return Kernel::TetraZigSimd4;
  if (s == "tetra_zig_simd8") return Kernel::TetraZigSimd8;
  if (s == "tetra_zig_simd16") return Kernel::TetraZigSimd16;
  if (s == "tetra_rust_simd" || s == "rust_simd" || s == "rust") return Kernel::TetraRustSimd;
  if (s == "tetra_avx2" || s == "avx2") return Kernel::TetraAvx2;
  if (s == "tetra_avx2_madd" || s == "avx2_madd") return Kernel::TetraAvx2Madd;
  if (s == "tetra_avx2_scalar_gather" || s == "avx2_scalar_gather") return Kernel::TetraAvx2ScalarGather;
  if (s == "tetra_avx2_exact_float" || s == "avx2_exact_float") return Kernel::TetraAvx2ExactFloat;
  if (s == "tetra_asm" || s == "asm") return Kernel::TetraAsm;
  if (s == "tri" || s == "tri_float") return Kernel::TriFloat;
  throw std::runtime_error("unknown kernel " + s);
}

const char* kernel_name(Kernel k) {
  switch (k) {
    case Kernel::TetraAuto: return "auto";
    case Kernel::TetraScalar: return "tetra_scalar";
    case Kernel::TetraCppSimd: return "tetra_cpp_simd";
    case Kernel::TetraZigSimd: return "tetra_zig_simd";
    case Kernel::TetraZigSimd4: return "tetra_zig_simd4";
    case Kernel::TetraZigSimd8: return "tetra_zig_simd8";
    case Kernel::TetraZigSimd16: return "tetra_zig_simd16";
    case Kernel::TetraRustSimd: return "tetra_rust_simd";
    case Kernel::TetraAvx2: return "tetra_avx2";
    case Kernel::TetraAvx2Madd: return "tetra_avx2_madd";
    case Kernel::TetraAvx2ScalarGather: return "tetra_avx2_scalar_gather";
    case Kernel::TetraAvx2ExactFloat: return "tetra_avx2_exact_float";
    case Kernel::TetraAsm: return "tetra_asm";
    case Kernel::TriFloat: return "tri_float";
  }
  return "?";
}

bool avx2_available() {
  static const bool available = [] {
#if defined(_MSC_VER) && (defined(_M_X64) || defined(_M_IX86))
    int regs[4]{};
    __cpuid(regs, 0);
    if (regs[0] < 7) return false;
    __cpuidex(regs, 1, 0);
    if ((regs[2] & ((1 << 27) | (1 << 28))) != ((1 << 27) | (1 << 28))) return false;
    if ((_xgetbv(0) & 6) != 6) return false;
    __cpuidex(regs, 7, 0);
    return (regs[1] & (1 << 5)) != 0;
#elif defined(__x86_64__) || defined(__i386__)
    unsigned a = 0, b = 0, c = 0, d = 0;
    if (__get_cpuid_max(0, nullptr) < 7) return false;
    __get_cpuid(1, &a, &b, &c, &d);
    if ((c & ((1u << 27) | (1u << 28))) != ((1u << 27) | (1u << 28))) return false;
    unsigned xlo = 0, xhi = 0;
    __asm__ volatile("xgetbv" : "=a"(xlo), "=d"(xhi) : "c"(0));
    if ((xlo & 6) != 6) return false;
    __get_cpuid_count(7, 0, &a, &b, &c, &d);
    return (b & (1u << 5)) != 0;
#else
    return false;
#endif
  }();
  return available;
}

bool kernel_available(Kernel k) {
  switch (k) {
    case Kernel::TetraAuto:
    case Kernel::TetraScalar:
    case Kernel::TriFloat: return true;
#if defined(JSHC_HAVE_AVX2)
    case Kernel::TetraAvx2:
    case Kernel::TetraAvx2Madd:
    case Kernel::TetraAvx2ScalarGather:
    case Kernel::TetraAvx2ExactFloat: return avx2_available();
#endif
#if defined(JSHC_HAVE_CPP_SIMD)
    case Kernel::TetraCppSimd: return true;
#endif
#if defined(JSHC_HAVE_ZIG)
    case Kernel::TetraZigSimd:
    case Kernel::TetraZigSimd4:
    case Kernel::TetraZigSimd8:
    case Kernel::TetraZigSimd16: return true;
#endif
#if defined(JSHC_HAVE_RUST)
    case Kernel::TetraRustSimd: return true;
#endif
    default: return false;
  }
}

Kernel default_kernel() {
  for (Kernel k : {Kernel::TetraAvx2, Kernel::TetraZigSimd, Kernel::TetraCppSimd})
    if (kernel_available(k)) return k;
  return Kernel::TetraScalar;
}

Kernel resolve_kernel(Kernel k) {
  if (k == Kernel::TetraAuto) return default_kernel();
  if (!kernel_available(k)) {
    if (k == Kernel::TetraAsm)
      throw std::runtime_error("tetra_asm has no assembly implementation; use auto or tetra_avx2");
    throw std::runtime_error(std::string("kernel unavailable in this build or CPU/OS: ") + kernel_name(k));
  }
  return k;
}

size_t kernel_scratch_bytes(Kernel k) {
  k = resolve_kernel(k);
  return (k == Kernel::TetraScalar || is_avx2_kernel(k)) ? 0 : 2 * block_pixels() * 3;
}

void tetra_scalar(const SparseLut& L, const uint8_t* in, uint8_t* out, size_t n) {
  for (size_t i = 0; i < n; ++i) {
    tetra_pixel(L, in + 3 * i, out + 3 * i);
  }
}

void tetra_cpp_simd(const SparseLut& L, const uint8_t* in, uint8_t* out, size_t n) {
  (void)resolve_kernel(Kernel::TetraCppSimd);
#if defined(JSHC_HAVE_CPP_SIMD)
  if (in == out && n) {
    std::vector<uint8_t> tmp(n * 3);
    tetra_cpp_simd(L, in, tmp.data(), n);
    std::memcpy(out, tmp.data(), n * 3);
    return;
  }
  const size_t vec_n = n & ~static_cast<size_t>(7);
  if (vec_n > 0) {
    jshc_tetra_cpp_simd(&L.off[0][0], &L.frac[0][0], L.stride, L.packed_tables().nodes.data(), in, out, vec_n);
  }
  if (vec_n < n) {
    tetra_scalar(L, in + 3 * vec_n, out + 3 * vec_n, n - vec_n);
  }
#else
  (void)L; (void)in; (void)out; (void)n;
#endif
}

void tetra_zig_simd_lanes(const SparseLut& L, const uint8_t* in, uint8_t* out, size_t n,
                          size_t lanes) {
  if (lanes != 4 && lanes != 8 && lanes != 16) throw std::runtime_error("Zig lane count must be 4, 8 or 16");
  (void)resolve_kernel(Kernel::TetraZigSimd);
#if defined(JSHC_HAVE_ZIG)
  if (in == out && n) {
    std::vector<uint8_t> tmp(n * 3);
    tetra_zig_simd_lanes(L, in, tmp.data(), n, lanes);
    std::memcpy(out, tmp.data(), n * 3);
    return;
  }
  const size_t vec_n = n - n % lanes;
  if (vec_n > 0) {
    auto fn = lanes == 4 ? jshc_tetra_zig_simd4 :
              lanes == 16 ? jshc_tetra_zig_simd16 : jshc_tetra_zig_simd;
    fn(&L.off[0][0], &L.frac[0][0], L.stride, L.packed_tables().nodes.data(), in, out, vec_n);
  }
  if (vec_n < n) {
    tetra_scalar(L, in + 3 * vec_n, out + 3 * vec_n, n - vec_n);
  }
#else
  (void)L; (void)in; (void)out; (void)n;
#endif
}

void tetra_zig_simd(const SparseLut& L, const uint8_t* in, uint8_t* out, size_t n) {
  tetra_zig_simd_lanes(L, in, out, n, 16);
}

void tetra_rust_simd(const SparseLut& L, const uint8_t* in, uint8_t* out, size_t n) {
  (void)resolve_kernel(Kernel::TetraRustSimd);
#if defined(JSHC_HAVE_RUST)
  if (in == out && n) {
    std::vector<uint8_t> tmp(n * 3);
    tetra_rust_simd(L, in, tmp.data(), n);
    std::memcpy(out, tmp.data(), n * 3);
    return;
  }
  const size_t vec_n = n & ~static_cast<size_t>(7);
  if (vec_n > 0) {
    const auto& packed = L.packed_tables().nodes;
    jshc_tetra_rust_simd(&L.off[0][0], &L.frac[0][0], L.stride, packed.data(), packed.size(),
                         in, out, vec_n);
  }
  if (vec_n < n) {
    tetra_scalar(L, in + 3 * vec_n, out + 3 * vec_n, n - vec_n);
  }
#else
  (void)L; (void)in; (void)out; (void)n;
#endif
}

void tetra_avx2(const SparseLut& L, const uint8_t* in, uint8_t* out, size_t n) {
  (void)resolve_kernel(Kernel::TetraAvx2);
#if defined(JSHC_HAVE_AVX2)
  const auto& packed = L.packed_tables();
  const detail::Avx2LutView view{packed.axis.data(), packed.nodes.data(), L.stride[0], L.stride[1]};
  const size_t vec_n = n & ~size_t{7};
  detail::avx2_chain(&view, 1, in, out, vec_n);
  tetra_scalar(L, in + 3 * vec_n, out + 3 * vec_n, n - vec_n);
#else
  (void)L; (void)in; (void)out; (void)n;
#endif
}

void tetra_asm(const SparseLut& L, const uint8_t* in, uint8_t* out, size_t n) {
  (void)L; (void)in; (void)out; (void)n;
  (void)resolve_kernel(Kernel::TetraAsm);
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
      tetra_cpp_simd(L, in, out, n);
      break;
    case Kernel::TetraAvx2:
      tetra_avx2(L, in, out, n);
      break;
    case Kernel::TetraZigSimd:
      tetra_zig_simd(L, in, out, n);
      break;
    case Kernel::TetraZigSimd4:
      tetra_zig_simd_lanes(L, in, out, n, 4);
      break;
    case Kernel::TetraZigSimd8:
      tetra_zig_simd_lanes(L, in, out, n, 8);
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
    default: throw std::runtime_error("kernel must be resolved before dispatch");
  }
}

static void apply_images(const std::vector<const SparseLut*>& chain,
                          const RgbImageView* images, size_t image_count,
                          Kernel k, int threads) {
  k = resolve_kernel(k);
  const size_t num_stages = chain.size();
  if (num_stages == 0 || image_count == 0) return;
  const size_t kBlockPixels = block_pixels();
  // A prefix of virtual block indices avoids concatenating image bytes or
  // allocating one descriptor for each 4096-pixel task. Empty views are legal.
  std::vector<size_t> prefix;
  if (image_count > 1) prefix.resize(image_count + 1);
  size_t num_blocks = 0;
  std::vector<std::pair<uintptr_t, uintptr_t>> ranges;
  if (image_count > 1) ranges.reserve(image_count);
  for (size_t i = 0; i < image_count; ++i) {
    const auto& image = images[i];
    if (image.pixels > std::numeric_limits<size_t>::max() / 3 || (!image.rgb && image.pixels))
      throw std::runtime_error("invalid RGB image view");
    const size_t blocks = image.pixels / kBlockPixels + (image.pixels % kBlockPixels != 0);
    if (blocks > static_cast<size_t>(std::numeric_limits<long long>::max()) - num_blocks)
      throw std::runtime_error("image batch is too large");
    num_blocks += blocks;
    if (image_count > 1) {
      prefix[i + 1] = num_blocks;
      if (image.pixels) {
        const uintptr_t begin = reinterpret_cast<uintptr_t>(image.rgb);
        const size_t bytes = image.pixels * 3;
        if (begin > std::numeric_limits<uintptr_t>::max() - bytes)
          throw std::runtime_error("invalid RGB view address range");
        ranges.emplace_back(begin, begin + bytes);
      }
    }
  }
  std::sort(ranges.begin(), ranges.end());
  for (size_t i = 1; i < ranges.size(); ++i)
    if (ranges[i].first < ranges[i - 1].second)
      throw std::runtime_error("batch RGB image views must not overlap");
  if (num_blocks == 0) return;
  const bool fused = k == Kernel::TetraScalar || is_avx2_kernel(k);
  std::vector<detail::Avx2LutView> views;
  if (is_avx2_kernel(k)) views.reserve(num_stages);
  for (const SparseLut* L : chain) {
    if (!L) throw std::runtime_error("null sparse LUT in chain");
    if (k != Kernel::TetraScalar && k != Kernel::TriFloat) {
      // Prepare once before entering OpenMP: no first-use allocations/locks in
      // AVX2 pixel loops, and all worker references remain stable.
      const auto& packed = L->packed_tables();
      if (is_avx2_kernel(k))
        views.push_back({packed.axis.data(), packed.nodes.data(), L->stride[0], L->stride[1]});
    }
  }

#if defined(JSHC_HAVE_AVX2)
  const auto avx2_fn = k == Kernel::TetraAvx2Madd ? detail::avx2_chain_madd :
      k == Kernel::TetraAvx2ScalarGather ? detail::avx2_chain_scalar_gather :
      k == Kernel::TetraAvx2ExactFloat ? detail::avx2_chain_exact_float : detail::avx2_chain;
#endif

#if defined(_OPENMP)
  const int requested_threads = (threads > 0) ? threads : omp_get_max_threads();
  const int num_threads = omp_in_parallel() ? 1 :
      static_cast<int>(std::min(num_blocks, static_cast<size_t>(requested_threads)));
  if (std::getenv("OMP_SCHEDULE") == nullptr) omp_set_schedule(omp_sched_static, 0);
#pragma omp parallel num_threads(num_threads)
#endif
  {
    // Fused kernels need no per-worker block buffers. Other kernels write every
    // byte before reading it; value-initialization would just clear unused data.
    std::unique_ptr<uint8_t[]> scratch;
    if (!fused) scratch.reset(new uint8_t[2 * kBlockPixels * 3]);
    uint8_t* const buf_a = scratch.get();
    uint8_t* const buf_b = fused ? nullptr : buf_a + kBlockPixels * 3;

#if defined(_OPENMP)
#pragma omp for schedule(runtime)
#endif
    for (long long bi = 0; bi < static_cast<long long>(num_blocks); ++bi) {
      const size_t block = static_cast<size_t>(bi);
      const size_t image_index = image_count == 1 ? 0 :
          static_cast<size_t>(std::upper_bound(prefix.begin(), prefix.end(), block) - prefix.begin() - 1);
      const size_t image_block = block - (image_count == 1 ? 0 : prefix[image_index]);
      const size_t start = image_block * kBlockPixels;
      const size_t len = std::min(kBlockPixels, images[image_index].pixels - start);
      uint8_t* const block_rgb = images[image_index].rgb + 3 * start;

      if (k == Kernel::TetraScalar) {
        scalar_chain(chain, block_rgb, len);
        continue;
      }
#if defined(JSHC_HAVE_AVX2)
      if (is_avx2_kernel(k)) {
        const size_t vec_n = len & ~size_t{7};
        avx2_fn(views.data(), views.size(), block_rgb, block_rgb, vec_n);
        scalar_chain(chain, block_rgb + 3 * vec_n, len - vec_n);
        continue;
      }
#endif

      if (num_stages == 1) {
        // External SIMD backends declare restricted input/output pointers.
        run_kernel(k, *chain[0], block_rgb, buf_a, len);
        std::memcpy(block_rgb, buf_a, 3 * len);
        continue;
      }

      const uint8_t* src = block_rgb;
      uint8_t* dst = buf_a;
      for (size_t stage = 0; stage < num_stages; ++stage) {
        uint8_t* const out_ptr = (stage + 1 == num_stages) ? block_rgb : dst;
        run_kernel(k, *chain[stage], src, out_ptr, len);
        src = out_ptr;
        dst = (dst == buf_a) ? buf_b : buf_a;
      }
    }
  }
  (void)threads;
}

void apply_chain(const std::vector<const SparseLut*>& chain, uint8_t* rgb, size_t n, Kernel k,
                 int threads) {
  const RgbImageView image{rgb, n};
  apply_images(chain, &image, 1, k, threads);
}

void apply_chain_batch(const std::vector<const SparseLut*>& chain,
                       const std::vector<RgbImageView>& images, Kernel k, int threads) {
  apply_images(chain, images.data(), images.size(), k, threads);
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
