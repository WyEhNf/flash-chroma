#include "jshc/lut.hpp"

#include <cmath>
#include <cstdio>
#include <cstring>
#include <stdexcept>

#if defined(__AVX2__)
#include <immintrin.h>
#endif
#if defined(_OPENMP)
#include <omp.h>
#endif

namespace jshc {

static std::vector<uint8_t> read_file(const std::string& path) {
  FILE* f = std::fopen(path.c_str(), "rb");
  if (!f) throw std::runtime_error("cannot open " + path);
  std::fseek(f, 0, SEEK_END);
  long sz = std::ftell(f);
  std::fseek(f, 0, SEEK_SET);
  std::vector<uint8_t> buf(static_cast<size_t>(sz));
  if (sz > 0 && std::fread(buf.data(), 1, buf.size(), f) != buf.size()) {
    std::fclose(f);
    throw std::runtime_error("short read " + path);
  }
  std::fclose(f);
  return buf;
}

FullLut FullLut::load(const std::string& path) {
  FullLut L;
  L.data = read_file(path);
  if (L.data.size() != 256u * 256u * 256u * 3u)
    throw std::runtime_error("bad full LUT size: " + path);
  return L;
}

SparseLut SparseLut::load(const std::string& path) {
  auto buf = read_file(path);
  const uint8_t* p = buf.data();
  const uint8_t* end = p + buf.size();
  auto take = [&](void* dst, size_t n) {
    if (p + n > end) throw std::runtime_error("truncated slut: " + path);
    std::memcpy(dst, p, n);
    p += n;
  };
  char magic[4];
  take(magic, 4);
  if (std::memcmp(magic, "SLUT", 4) != 0) throw std::runtime_error("bad magic: " + path);
  uint32_t version, reserved;
  SparseLut L;
  take(&version, 4);
  take(&L.m, 4);
  take(&reserved, 4);
  if (version != 1 || L.m < 2 || L.m > 256) throw std::runtime_error("bad slut header: " + path);
  for (int a = 0; a < 3; ++a) {
    L.grid[a].resize(L.m);
    take(L.grid[a].data(), 4 * L.m);
  }
  take(L.idx, sizeof(L.idx));
  take(L.frac, sizeof(L.frac));
  L.nodes.resize(size_t(L.m) * L.m * L.m * 3);
  take(L.nodes.data(), L.nodes.size());
  for (int a = 0; a < 3; ++a)
    for (int x = 0; x < 256; ++x)
      if (L.idx[a][x] > L.m - 2 || L.frac[a][x] > uint32_t(kOne))
        throw std::runtime_error("bad slut tables: " + path);
  L.prepare();
  return L;
}

void SparseLut::save(const std::string& path) const {
  FILE* f = std::fopen(path.c_str(), "wb");
  if (!f) throw std::runtime_error("cannot write " + path);
  uint32_t version = 1, reserved = 0;
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
  stride[0] = int32_t(m * m);
  stride[1] = int32_t(m);
  stride[2] = 1;
  for (int a = 0; a < 3; ++a)
    for (int x = 0; x < 256; ++x) off[a][x] = int32_t(idx[a][x]) * stride[a];
  size_t n = size_t(m) * m * m;
  packed.resize(n + 8);  // padding keeps gathers in-bounds for any lane
  for (size_t i = 0; i < n; ++i)
    packed[i] = uint32_t(nodes[3 * i]) | (uint32_t(nodes[3 * i + 1]) << 8) |
                (uint32_t(nodes[3 * i + 2]) << 16);
  for (size_t i = n; i < n + 8; ++i) packed[i] = 0;
}

Kernel parse_kernel(const std::string& s) {
  if (s == "tetra" || s == "tetra_scalar") return Kernel::TetraScalar;
  if (s == "tetra_avx2" || s == "avx2") return Kernel::TetraAvx2;
  if (s == "tri" || s == "tri_float") return Kernel::TriFloat;
  throw std::runtime_error("unknown kernel " + s);
}

const char* kernel_name(Kernel k) {
  switch (k) {
    case Kernel::TetraScalar: return "tetra_scalar";
    case Kernel::TetraAvx2: return "tetra_avx2";
    case Kernel::TriFloat: return "tri_float";
  }
  return "?";
}

bool avx2_available() {
#if defined(__AVX2__)
  return true;
#else
  return false;
#endif
}

// ---- tetrahedral, integer Q16 --------------------------------------------------------
// Sorted-fraction formulation: f1>=f2>=f3 are the sorted fractions, c1 adds the axis of
// the largest fraction, c2 adds all axes except the smallest. Ties produce zero weights,
// so the result does not depend on the tie-break rule (Python mirrors this exactly).
static inline void tetra_px(const SparseLut& L, const uint8_t* in, uint8_t* out) {
  const int r = in[0], g = in[1], b = in[2];
  const int32_t base = L.off[0][r] + L.off[1][g] + L.off[2][b];
  const int32_t fr = int32_t(L.frac[0][r]), fg = int32_t(L.frac[1][g]), fb = int32_t(L.frac[2][b]);
  const int32_t sr = L.stride[0], sg = L.stride[1], sb = L.stride[2];
  int32_t f1 = fr, smax = sr;
  if (fg > f1) { f1 = fg; smax = sg; }
  if (fb > f1) { f1 = fb; smax = sb; }
  int32_t f3 = fr, smin = sr;
  if (fg < f3) { f3 = fg; smin = sg; }
  if (fb < f3) { f3 = fb; smin = sb; }
  const int32_t f2 = fr + fg + fb - f1 - f3;
  const int32_t S = sr + sg + sb;
  const uint32_t c0 = L.packed[base], c1 = L.packed[base + smax];
  const uint32_t c2 = L.packed[base + S - smin], c3 = L.packed[base + S];
  const int32_t w0 = kOne - f1, w1 = f1 - f2, w2 = f2 - f3, w3 = f3;
  for (int c = 0; c < 3; ++c) {
    const int sh = 8 * c;
    int32_t acc = int32_t((c0 >> sh) & 255) * w0 + int32_t((c1 >> sh) & 255) * w1 +
                  int32_t((c2 >> sh) & 255) * w2 + int32_t((c3 >> sh) & 255) * w3;
    out[c] = uint8_t((acc + (1 << (kQ - 1))) >> kQ);
  }
}

void tetra_scalar(const SparseLut& L, const uint8_t* in, uint8_t* out, size_t n) {
  for (size_t i = 0; i < n; ++i) tetra_px(L, in + 3 * i, out + 3 * i);
}

#if defined(__AVX2__)
void tetra_avx2(const SparseLut& L, const uint8_t* in, uint8_t* out, size_t n) {
  const __m128i shR0 = _mm_setr_epi8(0, 3, 6, 9, 12, 15, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1);
  const __m128i shR1 = _mm_setr_epi8(-1, -1, -1, -1, -1, -1, 2, 5, -1, -1, -1, -1, -1, -1, -1, -1);
  const __m128i shG0 = _mm_setr_epi8(1, 4, 7, 10, 13, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1);
  const __m128i shG1 = _mm_setr_epi8(-1, -1, -1, -1, -1, 0, 3, 6, -1, -1, -1, -1, -1, -1, -1, -1);
  const __m128i shB0 = _mm_setr_epi8(2, 5, 8, 11, 14, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1);
  const __m128i shB1 = _mm_setr_epi8(-1, -1, -1, -1, -1, 1, 4, 7, -1, -1, -1, -1, -1, -1, -1, -1);
  const __m256i pack = _mm256_setr_epi8(0, 1, 2, 4, 5, 6, 8, 9, 10, 12, 13, 14, -1, -1, -1, -1,
                                        0, 1, 2, 4, 5, 6, 8, 9, 10, 12, 13, 14, -1, -1, -1, -1);
  const __m256i vsr = _mm256_set1_epi32(L.stride[0]);
  const __m256i vsg = _mm256_set1_epi32(L.stride[1]);
  const __m256i vsb = _mm256_set1_epi32(L.stride[2]);
  const __m256i vS = _mm256_set1_epi32(L.stride[0] + L.stride[1] + L.stride[2]);
  const __m256i one = _mm256_set1_epi32(kOne);
  const __m256i half = _mm256_set1_epi32(1 << (kQ - 1));
  const __m256i m255 = _mm256_set1_epi32(255);
  const int* offR = L.off[0];
  const int* offG = L.off[1];
  const int* offB = L.off[2];
  const int* frR = reinterpret_cast<const int*>(L.frac[0]);
  const int* frG = reinterpret_cast<const int*>(L.frac[1]);
  const int* frB = reinterpret_cast<const int*>(L.frac[2]);
  const int* P = reinterpret_cast<const int*>(L.packed.data());

  size_t i = 0;
  // The packed store writes 4 bytes past the 8th pixel: keep 2 pixels of slack.
  for (; i + 10 <= n; i += 8) {
    const uint8_t* p = in + 3 * i;
    __m128i lo = _mm_loadu_si128(reinterpret_cast<const __m128i*>(p));
    __m128i hi = _mm_loadl_epi64(reinterpret_cast<const __m128i*>(p + 16));
    __m256i r = _mm256_cvtepu8_epi32(_mm_or_si128(_mm_shuffle_epi8(lo, shR0), _mm_shuffle_epi8(hi, shR1)));
    __m256i g = _mm256_cvtepu8_epi32(_mm_or_si128(_mm_shuffle_epi8(lo, shG0), _mm_shuffle_epi8(hi, shG1)));
    __m256i b = _mm256_cvtepu8_epi32(_mm_or_si128(_mm_shuffle_epi8(lo, shB0), _mm_shuffle_epi8(hi, shB1)));

    __m256i base = _mm256_add_epi32(_mm256_add_epi32(_mm256_i32gather_epi32(offR, r, 4),
                                                     _mm256_i32gather_epi32(offG, g, 4)),
                                    _mm256_i32gather_epi32(offB, b, 4));
    __m256i fr = _mm256_i32gather_epi32(frR, r, 4);
    __m256i fg = _mm256_i32gather_epi32(frG, g, 4);
    __m256i fb = _mm256_i32gather_epi32(frB, b, 4);

    __m256i f1 = fr, smax = vsr;
    __m256i gt = _mm256_cmpgt_epi32(fg, f1);
    smax = _mm256_blendv_epi8(smax, vsg, gt);
    f1 = _mm256_max_epi32(f1, fg);
    gt = _mm256_cmpgt_epi32(fb, f1);
    smax = _mm256_blendv_epi8(smax, vsb, gt);
    f1 = _mm256_max_epi32(f1, fb);

    __m256i f3 = fr, smin = vsr;
    __m256i lt = _mm256_cmpgt_epi32(f3, fg);
    smin = _mm256_blendv_epi8(smin, vsg, lt);
    f3 = _mm256_min_epi32(f3, fg);
    lt = _mm256_cmpgt_epi32(f3, fb);
    smin = _mm256_blendv_epi8(smin, vsb, lt);
    f3 = _mm256_min_epi32(f3, fb);

    __m256i f2 = _mm256_sub_epi32(_mm256_add_epi32(fr, _mm256_add_epi32(fg, fb)), _mm256_add_epi32(f1, f3));

    __m256i c0 = _mm256_i32gather_epi32(P, base, 4);
    __m256i c1 = _mm256_i32gather_epi32(P, _mm256_add_epi32(base, smax), 4);
    __m256i c2 = _mm256_i32gather_epi32(P, _mm256_sub_epi32(_mm256_add_epi32(base, vS), smin), 4);
    __m256i c3 = _mm256_i32gather_epi32(P, _mm256_add_epi32(base, vS), 4);

    __m256i w0 = _mm256_sub_epi32(one, f1);
    __m256i w1 = _mm256_sub_epi32(f1, f2);
    __m256i w2 = _mm256_sub_epi32(f2, f3);
    __m256i w3 = f3;

    __m256i res = _mm256_setzero_si256();
    for (int c = 0; c < 3; ++c) {
      const __m128i sh = _mm_cvtsi32_si128(8 * c);
      __m256i acc = _mm256_mullo_epi32(_mm256_and_si256(_mm256_srl_epi32(c0, sh), m255), w0);
      acc = _mm256_add_epi32(acc, _mm256_mullo_epi32(_mm256_and_si256(_mm256_srl_epi32(c1, sh), m255), w1));
      acc = _mm256_add_epi32(acc, _mm256_mullo_epi32(_mm256_and_si256(_mm256_srl_epi32(c2, sh), m255), w2));
      acc = _mm256_add_epi32(acc, _mm256_mullo_epi32(_mm256_and_si256(_mm256_srl_epi32(c3, sh), m255), w3));
      acc = _mm256_srli_epi32(_mm256_add_epi32(acc, half), kQ);
      res = _mm256_or_si256(res, _mm256_sll_epi32(acc, sh));
    }
    res = _mm256_shuffle_epi8(res, pack);
    uint8_t* q = out + 3 * i;
    _mm_storeu_si128(reinterpret_cast<__m128i*>(q), _mm256_castsi256_si128(res));
    _mm_storeu_si128(reinterpret_cast<__m128i*>(q + 12), _mm256_extracti128_si256(res, 1));
  }
  for (; i < n; ++i) tetra_px(L, in + 3 * i, out + 3 * i);
}
#else
void tetra_avx2(const SparseLut& L, const uint8_t* in, uint8_t* out, size_t n) {
  tetra_scalar(L, in, out, n);
}
#endif

// ---- trilinear, float ------------------------------------------------------------------
void tri_float(const SparseLut& L, const uint8_t* in, uint8_t* out, size_t n) {
  const int32_t sr = L.stride[0], sg = L.stride[1], sb = L.stride[2];
  const float inv = 1.0f / float(kOne);
  for (size_t i = 0; i < n; ++i) {
    const int r = in[3 * i], g = in[3 * i + 1], b = in[3 * i + 2];
    const int32_t base = L.off[0][r] + L.off[1][g] + L.off[2][b];
    const float x = L.frac[0][r] * inv, y = L.frac[1][g] * inv, z = L.frac[2][b] * inv;
    const uint8_t* N = L.nodes.data();
    for (int c = 0; c < 3; ++c) {
      auto v = [&](int32_t o) { return float(N[3 * (base + o) + c]); };
      float c00 = v(0) + (v(sb) - v(0)) * z;
      float c01 = v(sg) + (v(sg + sb) - v(sg)) * z;
      float c10 = v(sr) + (v(sr + sb) - v(sr)) * z;
      float c11 = v(sr + sg) + (v(sr + sg + sb) - v(sr + sg)) * z;
      float c0 = c00 + (c01 - c00) * y;
      float c1 = c10 + (c11 - c10) * y;
      float val = c0 + (c1 - c0) * x;
      int q = int(std::lround(val));
      out[3 * i + c] = uint8_t(q < 0 ? 0 : (q > 255 ? 255 : q));
    }
  }
}

// ---- chains ----------------------------------------------------------------------------
static void run_kernel(Kernel k, const SparseLut& L, const uint8_t* in, uint8_t* out, size_t n) {
  switch (k) {
    case Kernel::TetraScalar: tetra_scalar(L, in, out, n); break;
    case Kernel::TetraAvx2: tetra_avx2(L, in, out, n); break;
    case Kernel::TriFloat: tri_float(L, in, out, n); break;
  }
}

void apply_chain(const std::vector<const SparseLut*>& chain, uint8_t* rgb, size_t n, Kernel k,
                 int threads) {
  constexpr size_t kBlock = 4096;  // pixels; 12 KiB per buffer, stays in L1/L2
  const size_t nblocks = (n + kBlock - 1) / kBlock;
  const int K = int(chain.size());
#if defined(_OPENMP)
#pragma omp parallel num_threads(threads > 0 ? threads : omp_get_max_threads())
#endif
  {
    alignas(64) uint8_t bufA[kBlock * 3 + 64];
    alignas(64) uint8_t bufB[kBlock * 3 + 64];
#if defined(_OPENMP)
#pragma omp for schedule(static)
#endif
    for (long long bi = 0; bi < (long long)nblocks; ++bi) {
      const size_t s = size_t(bi) * kBlock;
      const size_t len = (s + kBlock <= n) ? kBlock : n - s;
      uint8_t* blk = rgb + 3 * s;
      const uint8_t* src = blk;
      uint8_t* dst = bufA;
      for (int st = 0; st < K; ++st) {
        run_kernel(k, *chain[st], src, dst, len);
        src = dst;
        dst = (dst == bufA) ? bufB : bufA;
      }
      std::memcpy(blk, src, 3 * len);
    }
  }
  (void)threads;
}

void apply_full_chain(const std::vector<const FullLut*>& chain, uint8_t* rgb, size_t n,
                      int threads) {
#if defined(_OPENMP)
#pragma omp parallel for schedule(static) num_threads(threads > 0 ? threads : omp_get_max_threads())
#endif
  for (long long i = 0; i < (long long)n; ++i) {
    uint8_t* p = rgb + 3 * i;
    for (const FullLut* L : chain) {
      const size_t o = ((size_t(p[0]) << 16) | (size_t(p[1]) << 8) | p[2]) * 3;
      p[0] = L->data[o];
      p[1] = L->data[o + 1];
      p[2] = L->data[o + 2];
    }
  }
  (void)threads;
}

}  // namespace jshc
