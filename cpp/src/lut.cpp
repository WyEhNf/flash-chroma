#include "jshc/lut.hpp"

#include <atomic>
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
  for (int a = 0; a < 3; ++a) {
    for (int x = 0; x < 256; ++x) {
      off[a][x] = int32_t(idx[a][x]) * stride[a];
      uint32_t i_norm = idx[a][x];
      uint32_t f_norm = frac[a][x];
      if (f_norm >= uint32_t(kOne)) {
        i_norm += 1;
        f_norm = 0;
      }
      uint32_t o_norm = i_norm * uint32_t(stride[a]);
      uint16_t f_tilde = static_cast<uint16_t>(static_cast<int16_t>(int32_t(f_norm) - 32768));
      of_pack[a][x] =
          (static_cast<int32_t>(f_tilde) << 16) | static_cast<int32_t>(o_norm & 0xFFFFu);
    }
  }
  size_t n = size_t(m) * m * m;
  size_t pad = size_t(stride[0] + stride[1] + stride[2]) + 16;
  packed.resize(n + pad);  // padding keeps gathers in-bounds for any lane / boundary cell
  for (size_t i = 0; i < n; ++i)
    packed[i] = uint32_t(nodes[3 * i]) | (uint32_t(nodes[3 * i + 1]) << 8) |
                (uint32_t(nodes[3 * i + 2]) << 16);
  for (size_t i = n; i < n + pad; ++i) packed[i] = 0;
}

Kernel parse_kernel(const std::string& s) {
  if (s == "tetra" || s == "tetra_scalar") return Kernel::TetraScalar;
  if (s == "tetra_avx2" || s == "avx2") return Kernel::TetraAvx2;
  if (s == "tetra_asm" || s == "asm") return Kernel::TetraAsm;
  if (s == "tri" || s == "tri_float") return Kernel::TriFloat;
  throw std::runtime_error("unknown kernel " + s);
}

const char* kernel_name(Kernel k) {
  switch (k) {
    case Kernel::TetraScalar: return "tetra_scalar";
    case Kernel::TetraAvx2: return "tetra_avx2";
    case Kernel::TetraAsm: return "tetra_asm";
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
  if (L.m > 40) {
    tetra_scalar(L, in, out, n);
    return;
  }
  const __m256i shR = _mm256_setr_epi8(0, -1, -1, -1, 3, -1, -1, -1, 6, -1, -1, -1, 9, -1, -1, -1,
                                       0, -1, -1, -1, 3, -1, -1, -1, 6, -1, -1, -1, 9, -1, -1, -1);
  const __m256i pack = _mm256_setr_epi8(0, 1, 2, 4, 5, 6, 8, 9, 10, 12, 13, 14, -1, -1, -1, -1,
                                        0, 1, 2, 4, 5, 6, 8, 9, 10, 12, 13, 14, -1, -1, -1, -1);
  const __m256i vsr = _mm256_set1_epi32(L.stride[0]);
  const __m256i vsg = _mm256_set1_epi32(L.stride[1]);
  const __m256i vsb = _mm256_set1_epi32(L.stride[2]);
  const __m256i vS = _mm256_set1_epi32(L.stride[0] + L.stride[1] + L.stride[2]);
  const __m256i mFFFF = _mm256_set1_epi32(0x0000FFFF);
  const __m256i mRB = _mm256_set1_epi32(0x00FF00FF);
  const __m256i v_neg32768 = _mm256_set1_epi32(static_cast<int32_t>(0x80000000u));
  const __m256i v_neg1_16 = _mm256_set1_epi16(-1);

  const int* ofR = L.of_pack[0];
  const int* ofG = L.of_pack[1];
  const int* ofB = L.of_pack[2];
  const int* P = reinterpret_cast<const int*>(L.packed.data());

  size_t i = 0;
  for (; i + 10 <= n; i += 8) {
    const uint8_t* p = in + 3 * i;
    __m256i raw = _mm256_set_m128i(_mm_loadu_si128(reinterpret_cast<const __m128i*>(p + 12)),
                                   _mm_loadu_si128(reinterpret_cast<const __m128i*>(p)));
    __m256i r = _mm256_shuffle_epi8(raw, shR);
    __m256i g = _mm256_shuffle_epi8(_mm256_bsrli_epi128(raw, 1), shR);
    __m256i b = _mm256_shuffle_epi8(_mm256_bsrli_epi128(raw, 2), shR);

    // 3 combined axis gathers: hi16 = frac - 32768, lo16 = off
    __m256i rf = _mm256_i32gather_epi32(ofR, r, 4);
    __m256i gf = _mm256_i32gather_epi32(ofG, g, 4);
    __m256i bf = _mm256_i32gather_epi32(ofB, b, 4);

    __m256i base = _mm256_and_si256(_mm256_add_epi32(rf, _mm256_add_epi32(gf, bf)), mFFFF);
    __m256i base_S = _mm256_add_epi32(base, vS);

    // Replace lo16 with stride[a] and run 6-op branchless sorting network on (frac_tilde << 16 | stride)
    __m256i ka = _mm256_blend_epi16(rf, vsr, 0x55);
    __m256i kb = _mm256_blend_epi16(gf, vsg, 0x55);
    __m256i kc = _mm256_blend_epi16(bf, vsb, 0x55);

    __m256i t0 = _mm256_max_epi32(ka, kb);
    __m256i t1 = _mm256_min_epi32(ka, kb);
    __m256i hi = _mm256_max_epi32(t0, kc);
    __m256i t2 = _mm256_min_epi32(t0, kc);
    __m256i mid = _mm256_max_epi32(t1, t2);
    __m256i lo = _mm256_min_epi32(t1, t2);

    __m256i smax = _mm256_and_si256(hi, mFFFF);
    __m256i smin = _mm256_and_si256(lo, mFFFF);

    // Pack shared signed 16-bit weight pairs: f12 = (f2_tilde << 16) | f1_tilde, f30 = (-32768 << 16) | f3_tilde
    __m256i f12 = _mm256_blend_epi16(_mm256_srli_epi32(hi, 16), mid, 0xAA);
    __m256i f30 = _mm256_blend_epi16(_mm256_srli_epi32(lo, 16), v_neg32768, 0xAA);

    __m256i c0 = _mm256_i32gather_epi32(P, base, 4);
    __m256i c1 = _mm256_i32gather_epi32(P, _mm256_add_epi32(base, smax), 4);
    __m256i c2 = _mm256_i32gather_epi32(P, _mm256_sub_epi32(base_S, smin), 4);
    __m256i c3 = _mm256_i32gather_epi32(P, base_S, 4);

    // Extract R (lo16) and B (hi16) simultaneously via 0x00FF00FF mask
    __m256i rb0 = _mm256_and_si256(c0, mRB);
    __m256i rb1 = _mm256_and_si256(c1, mRB);
    __m256i rb2 = _mm256_and_si256(c2, mRB);
    __m256i rb3 = _mm256_and_si256(c3, mRB);

    __m256i d1_rb = _mm256_sub_epi16(rb1, rb0);
    __m256i d2_rb = _mm256_sub_epi16(rb2, rb1);
    __m256i d3_rb = _mm256_sub_epi16(rb3, rb2);
    __m256i d0_rb = _mm256_sub_epi16(v_neg1_16, _mm256_add_epi16(rb0, rb3));

    __m256i d12_R = _mm256_blend_epi16(d1_rb, _mm256_slli_epi32(d2_rb, 16), 0xAA);
    __m256i d30_R = _mm256_blend_epi16(d3_rb, _mm256_slli_epi32(d0_rb, 16), 0xAA);
    __m256i d12_B = _mm256_blend_epi16(_mm256_srli_epi32(d1_rb, 16), d2_rb, 0xAA);
    __m256i d30_B = _mm256_blend_epi16(_mm256_srli_epi32(d3_rb, 16), d0_rb, 0xAA);

    // Extract G via 16-bit right shift by 8 (clears top 8 bits of each 16-bit word automatically!)
    __m256i g0 = _mm256_srli_epi16(c0, 8);
    __m256i g1 = _mm256_srli_epi16(c1, 8);
    __m256i g2 = _mm256_srli_epi16(c2, 8);
    __m256i g3 = _mm256_srli_epi16(c3, 8);

    __m256i d12_G = _mm256_blend_epi16(_mm256_sub_epi16(g1, g0),
                                       _mm256_slli_epi32(_mm256_sub_epi16(g2, g1), 16), 0xAA);
    __m256i d30_G = _mm256_blend_epi16(
        _mm256_sub_epi16(g3, g2),
        _mm256_slli_epi32(_mm256_sub_epi16(v_neg1_16, _mm256_add_epi16(g0, g3)), 16), 0xAA);

    __m256i accR = _mm256_srli_epi32(
        _mm256_add_epi32(_mm256_madd_epi16(d12_R, f12), _mm256_madd_epi16(d30_R, f30)), 16);
    __m256i accG = _mm256_slli_epi32(
        _mm256_srli_epi32(
            _mm256_add_epi32(_mm256_madd_epi16(d12_G, f12), _mm256_madd_epi16(d30_G, f30)), 16),
        8);
    __m256i accB = _mm256_add_epi32(_mm256_madd_epi16(d12_B, f12), _mm256_madd_epi16(d30_B, f30));

    __m256i res = _mm256_or_si256(_mm256_blend_epi16(accR, accB, 0xAA), accG);
    res = _mm256_shuffle_epi8(res, pack);

    __m128i res_lo = _mm256_castsi256_si128(res);
    __m128i res_hi = _mm256_extracti128_si256(res, 1);
    uint8_t* q = out + 3 * i;
    _mm_storeu_si128(reinterpret_cast<__m128i*>(q), _mm_or_si128(res_lo, _mm_slli_si128(res_hi, 12)));
    _mm_storel_epi64(reinterpret_cast<__m128i*>(q + 16), _mm_srli_si128(res_hi, 4));
  }
  for (; i < n; ++i) tetra_px(L, in + 3 * i, out + 3 * i);
}

void tetra_asm(const SparseLut& L, const uint8_t* in, uint8_t* out, size_t n) {
  if (L.m > 40) {
    tetra_scalar(L, in, out, n);
    return;
  }
  alignas(64) struct AsmConsts {
    __m256i vsr;
    __m256i vsg;
    __m256i vsb;
    __m256i vS;
    __m256i v_neg32768;
    __m256i pack;
    __m256i v_ones;
  } C;
  C.vsr = _mm256_set1_epi32(L.stride[0]);
  C.vsg = _mm256_set1_epi32(L.stride[1]);
  C.vsb = _mm256_set1_epi32(L.stride[2]);
  C.vS = _mm256_set1_epi32(L.stride[0] + L.stride[1] + L.stride[2]);
  C.v_neg32768 = _mm256_set1_epi32(static_cast<int32_t>(0x80000000u));
  C.pack = _mm256_setr_epi8(0, 1, 2, 4, 5, 6, 8, 9, 10, 12, 13, 14, -1, -1, -1, -1,
                            0, 1, 2, 4, 5, 6, 8, 9, 10, 12, 13, 14, -1, -1, -1, -1);
  C.v_ones = _mm256_set1_epi16(-1);

  const __m256i shR = _mm256_setr_epi8(0, -1, -1, -1, 3, -1, -1, -1, 6, -1, -1, -1, 9, -1, -1, -1,
                                       0, -1, -1, -1, 3, -1, -1, -1, 6, -1, -1, -1, 9, -1, -1, -1);
  const __m256i mFFFF = _mm256_set1_epi32(0x0000FFFF);
  const __m256i mRB = _mm256_set1_epi32(0x00FF00FF);
  const __m256i perm_out = _mm256_setr_epi32(0, 1, 2, 4, 5, 6, 3, 7);

  size_t i = 0;
  if (n >= 10) {
    size_t vec_n = ((n - 2) & ~size_t(7));
    const uint8_t* p_in = in;
    uint8_t* p_out = out;
    const uint8_t* p_end = in + 3 * vec_n;
    const int* ofR = L.of_pack[0];
    const int* ofG = L.of_pack[1];
    const int* ofB = L.of_pack[2];
    const int* P = reinterpret_cast<const int*>(L.packed.data());
    const AsmConsts* c_ptr = &C;

    __asm__ volatile(
        "vmovdqa %[shR], %%ymm15\n\t"
        "vmovdqa %[mFFFF], %%ymm14\n\t"
        "vmovdqa %[mRB], %%ymm13\n\t"
        "vmovdqa %[perm_out], %%ymm12\n\t"
        ".p2align 6\n\t"
        "1:\n\t"
        // 1. Dual 128-bit load & single-mask RGB byte unpack
        "vmovdqu (%[in]), %%xmm0\n\t"
        "vinserti128 $1, 12(%[in]), %%ymm0, %%ymm0\n\t"
        "vpsrldq $1, %%ymm0, %%ymm1\n\t"
        "vpsrldq $2, %%ymm0, %%ymm2\n\t"
        "vpshufb %%ymm15, %%ymm0, %%ymm0\n\t"
        "vpshufb %%ymm15, %%ymm1, %%ymm1\n\t"
        "vpshufb %%ymm15, %%ymm2, %%ymm2\n\t"

        // 2. 3 combined axis gathers (frac_tilde << 16 | off_norm)
        "vpcmpeqd %%ymm9, %%ymm9, %%ymm9\n\t"
        "vpgatherdd %%ymm9, (%[ofR], %%ymm0, 4), %%ymm3\n\t"
        "vpcmpeqd %%ymm10, %%ymm10, %%ymm10\n\t"
        "vpgatherdd %%ymm10, (%[ofG], %%ymm1, 4), %%ymm4\n\t"
        "vpcmpeqd %%ymm11, %%ymm11, %%ymm11\n\t"
        "vpgatherdd %%ymm11, (%[ofB], %%ymm2, 4), %%ymm5\n\t"

        // 3. Base offsets + early launch of c0 and c3 gathers to overlap with sorting network
        "vpaddd %%ymm4, %%ymm5, %%ymm6\n\t"
        "vpaddd %%ymm3, %%ymm6, %%ymm6\n\t"
        "vpand %%ymm14, %%ymm6, %%ymm6\n\t"
        "vpaddd 96(%[c]), %%ymm6, %%ymm7\n\t"
        "vpcmpeqd %%ymm10, %%ymm10, %%ymm10\n\t"
        "vpgatherdd %%ymm10, (%[P], %%ymm6, 4), %%ymm8\n\t"
        "vpcmpeqd %%ymm11, %%ymm11, %%ymm11\n\t"
        "vpgatherdd %%ymm11, (%[P], %%ymm7, 4), %%ymm9\n\t"

        // 4. 6-op branchless sorting network on (frac_tilde << 16 | stride)
        "vpblendw $0x55, 0(%[c]), %%ymm3, %%ymm3\n\t"
        "vpblendw $0x55, 32(%[c]), %%ymm4, %%ymm4\n\t"
        "vpblendw $0x55, 64(%[c]), %%ymm5, %%ymm5\n\t"
        "vpmaxsd %%ymm4, %%ymm3, %%ymm0\n\t"
        "vpminsd %%ymm4, %%ymm3, %%ymm1\n\t"
        "vpmaxsd %%ymm5, %%ymm0, %%ymm2\n\t"
        "vpminsd %%ymm5, %%ymm0, %%ymm0\n\t"
        "vpmaxsd %%ymm0, %%ymm1, %%ymm3\n\t"
        "vpminsd %%ymm0, %%ymm1, %%ymm4\n\t"

        // 5. Extract smax, smin and launch c1, c2 gathers
        "vpand %%ymm14, %%ymm2, %%ymm0\n\t"
        "vpand %%ymm14, %%ymm4, %%ymm1\n\t"
        "vpaddd %%ymm0, %%ymm6, %%ymm0\n\t"
        "vpsubd %%ymm1, %%ymm7, %%ymm1\n\t"
        "vpcmpeqd %%ymm5, %%ymm5, %%ymm5\n\t"
        "vpgatherdd %%ymm5, (%[P], %%ymm0, 4), %%ymm6\n\t"
        "vpcmpeqd %%ymm5, %%ymm5, %%ymm5\n\t"
        "vpgatherdd %%ymm5, (%[P], %%ymm1, 4), %%ymm7\n\t"

        // 6. Pack weight pairs f12, f30 and process c0, c3 while c1, c2 finish gathering
        "vpsrld $16, %%ymm2, %%ymm2\n\t"
        "vpblendw $0xAA, %%ymm3, %%ymm2, %%ymm10\n\t"
        "vpsrld $16, %%ymm4, %%ymm4\n\t"
        "vpblendw $0xAA, 128(%[c]), %%ymm4, %%ymm11\n\t"
        "vpand %%ymm13, %%ymm8, %%ymm0\n\t"
        "vpand %%ymm13, %%ymm9, %%ymm1\n\t"
        "vpaddw %%ymm1, %%ymm0, %%ymm2\n\t"
        "vpxor 192(%[c]), %%ymm2, %%ymm2\n\t"
        "vpsrlw $8, %%ymm8, %%ymm8\n\t"
        "vpsrlw $8, %%ymm9, %%ymm9\n\t"

        // 7. Consume c1, c2 and compute R & B channels via parallel vpmaddwd tree
        "vpand %%ymm13, %%ymm6, %%ymm3\n\t"
        "vpand %%ymm13, %%ymm7, %%ymm4\n\t"
        "vpsubw %%ymm0, %%ymm3, %%ymm0\n\t"
        "vpsubw %%ymm3, %%ymm4, %%ymm3\n\t"
        "vpsubw %%ymm4, %%ymm1, %%ymm1\n\t"

        "vpslld $16, %%ymm3, %%ymm4\n\t"
        "vpblendw $0xAA, %%ymm4, %%ymm0, %%ymm4\n\t"
        "vpslld $16, %%ymm2, %%ymm5\n\t"
        "vpblendw $0xAA, %%ymm5, %%ymm1, %%ymm5\n\t"
        "vpmaddwd %%ymm10, %%ymm4, %%ymm4\n\t"
        "vpmaddwd %%ymm11, %%ymm5, %%ymm5\n\t"
        "vpaddd %%ymm5, %%ymm4, %%ymm4\n\t"
        "vpsrld $16, %%ymm4, %%ymm4\n\t"

        "vpsrld $16, %%ymm0, %%ymm0\n\t"
        "vpblendw $0xAA, %%ymm3, %%ymm0, %%ymm0\n\t"
        "vpsrld $16, %%ymm1, %%ymm1\n\t"
        "vpblendw $0xAA, %%ymm2, %%ymm1, %%ymm1\n\t"
        "vpmaddwd %%ymm10, %%ymm0, %%ymm0\n\t"
        "vpmaddwd %%ymm11, %%ymm1, %%ymm1\n\t"
        "vpaddd %%ymm1, %%ymm0, %%ymm0\n\t"
        "vpblendw $0xAA, %%ymm0, %%ymm4, %%ymm0\n\t"

        // 8. Compute G channel, merge RGB, vpshufb + vpermd 24-byte store
        "vpsrlw $8, %%ymm6, %%ymm6\n\t"
        "vpsrlw $8, %%ymm7, %%ymm7\n\t"
        "vpaddw %%ymm9, %%ymm8, %%ymm1\n\t"
        "vpxor 192(%[c]), %%ymm1, %%ymm1\n\t"
        "vpslld $16, %%ymm1, %%ymm1\n\t"
        "vpsubw %%ymm8, %%ymm6, %%ymm2\n\t"
        "vpsubw %%ymm6, %%ymm7, %%ymm3\n\t"
        "vpslld $16, %%ymm3, %%ymm3\n\t"
        "vpblendw $0xAA, %%ymm3, %%ymm2, %%ymm2\n\t"
        "vpsubw %%ymm7, %%ymm9, %%ymm3\n\t"
        "vpblendw $0xAA, %%ymm1, %%ymm3, %%ymm3\n\t"
        "vpmaddwd %%ymm10, %%ymm2, %%ymm2\n\t"
        "vpmaddwd %%ymm11, %%ymm3, %%ymm3\n\t"
        "vpaddd %%ymm3, %%ymm2, %%ymm2\n\t"
        "vpsrld $16, %%ymm2, %%ymm2\n\t"
        "vpslld $8, %%ymm2, %%ymm2\n\t"
        "vpor %%ymm2, %%ymm0, %%ymm0\n\t"
        "vpshufb 160(%[c]), %%ymm0, %%ymm0\n\t"
        "vpermd %%ymm0, %%ymm12, %%ymm0\n\t"
        "vmovdqu %%xmm0, (%[out])\n\t"
        "vextracti128 $1, %%ymm0, %%xmm1\n\t"
        "vmovq %%xmm1, 16(%[out])\n\t"

        "addq $24, %[in]\n\t"
        "addq $24, %[out]\n\t"
        "cmpq %[in_end], %[in]\n\t"
        "jb 1b\n\t"
        : [in] "+r"(p_in), [out] "+r"(p_out)
        : [in_end] "r"(p_end), [ofR] "r"(ofR), [ofG] "r"(ofG), [ofB] "r"(ofB), [P] "r"(P),
          [c] "r"(c_ptr), [shR] "m"(shR), [mFFFF] "m"(mFFFF), [mRB] "m"(mRB),
          [perm_out] "m"(perm_out)
        : "cc", "memory", "ymm0", "ymm1", "ymm2", "ymm3", "ymm4", "ymm5", "ymm6", "ymm7",
          "ymm8", "ymm9", "ymm10", "ymm11", "ymm12", "ymm13", "ymm14", "ymm15");
    i = vec_n;
  }
  for (; i < n; ++i) tetra_px(L, in + 3 * i, out + 3 * i);
}
#else
void tetra_avx2(const SparseLut& L, const uint8_t* in, uint8_t* out, size_t n) {
  tetra_scalar(L, in, out, n);
}
void tetra_asm(const SparseLut& L, const uint8_t* in, uint8_t* out, size_t n) {
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
    case Kernel::TetraAsm: tetra_asm(L, in, out, n); break;
    case Kernel::TriFloat: tri_float(L, in, out, n); break;
  }
}

void apply_chain(const std::vector<const SparseLut*>& chain, uint8_t* rgb, size_t n, Kernel k,
                 int threads) {
  const int K = int(chain.size());
  if (K == 0 || n == 0) return;

#if defined(_OPENMP)
  const int hw = omp_get_max_threads();
  // On hybrid Intel CPUs (P+E cores), default (threads <= 0) uses 10 threads (1 per physical core)
  const int nth = (threads > 0) ? threads : ((hw >= 16) ? (hw / 2) : hw);
#else
  const int nth = 1;
  (void)threads;
#endif

  if (nth <= 1) {
    if (K == 1) {
      run_kernel(k, *chain[0], rgb, rgb, n);
      return;
    }
    constexpr size_t kBlock = 4096;
    alignas(64) uint8_t bufA[kBlock * 3 + 64];
    alignas(64) uint8_t bufB[kBlock * 3 + 64];
    for (size_t s = 0; s < n; s += kBlock) {
      const size_t len = (s + kBlock <= n) ? kBlock : (n - s);
      uint8_t* blk = rgb + 3 * s;
      const uint8_t* src = blk;
      uint8_t* dst = bufA;
      for (int st = 0; st < K; ++st) {
        uint8_t* out_ptr = (st == K - 1) ? blk : dst;
        run_kernel(k, *chain[st], src, out_ptr, len);
        src = out_ptr;
        dst = (dst == bufA) ? bufB : bufA;
      }
    }
    return;
  }

  constexpr size_t kBlock = 4096;  // 12 KiB per block, stays in L1d (48 KiB)
  const size_t nblocks = (n + kBlock - 1) / kBlock;
  std::atomic<size_t> next_blk{0};

#if defined(_OPENMP)
#pragma omp parallel num_threads(nth)
#endif
  {
    if (K == 1) {
      const SparseLut& L0 = *chain[0];
      while (true) {
        size_t bi = next_blk.fetch_add(2, std::memory_order_relaxed);
        if (bi >= nblocks) break;
        size_t s = bi * kBlock;
        size_t len = (s + 2 * kBlock <= n) ? (2 * kBlock) : (n - s);
        run_kernel(k, L0, rgb + 3 * s, rgb + 3 * s, len);
      }
    } else {
      alignas(64) uint8_t bufA[kBlock * 3 + 64];
      alignas(64) uint8_t bufB[kBlock * 3 + 64];
      while (true) {
        size_t bi = next_blk.fetch_add(1, std::memory_order_relaxed);
        if (bi >= nblocks) break;
        const size_t s = bi * kBlock;
        const size_t len = (s + kBlock <= n) ? kBlock : (n - s);
        uint8_t* blk = rgb + 3 * s;
        const uint8_t* src = blk;
        uint8_t* dst = bufA;
        for (int st = 0; st < K; ++st) {
          uint8_t* out_ptr = (st == K - 1) ? blk : dst;
          run_kernel(k, *chain[st], src, out_ptr, len);
          src = out_ptr;
          dst = (dst == bufA) ? bufB : bufA;
        }
      }
    }
  }
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

// ---- Native C++17 + OpenMP + AVX2 R14 Offline Fitting Solver -------------------------
static inline void eval_chain_pixel(const std::vector<const FullLut*>& chain, uint8_t r, uint8_t g,
                                    uint8_t b, uint8_t* out) {
  for (const FullLut* F : chain) {
    const size_t o = ((size_t(r) << 16) | (size_t(g) << 8) | b) * 3;
    r = F->data[o];
    g = F->data[o + 1];
    b = F->data[o + 2];
  }
  out[0] = r;
  out[1] = g;
  out[2] = b;
}

// Invert small symmetric positive-definite matrix A (m x m) in-place via Cholesky / Gauss-Jordan
static void invert_spd(std::vector<double>& A, int m) {
  std::vector<double> L(m * m, 0.0);
  for (int i = 0; i < m; ++i) {
    for (int j = 0; j <= i; ++j) {
      double s = A[i * m + j];
      for (int k = 0; k < j; ++k) s -= L[i * m + k] * L[j * m + k];
      if (i == j) {
        L[i * m + j] = std::sqrt(s > 1e-12 ? s : 1e-12);
      } else {
        L[i * m + j] = s / L[j * m + j];
      }
    }
  }
  // Invert L in-place
  std::vector<double> Linv(m * m, 0.0);
  for (int i = 0; i < m; ++i) {
    Linv[i * m + i] = 1.0 / L[i * m + i];
    for (int j = i + 1; j < m; ++j) {
      double s = 0.0;
      for (int k = i; k < j; ++k) s -= L[j * m + k] * Linv[k * m + i];
      Linv[j * m + i] = s / L[j * m + j];
    }
  }
  // A^{-1} = Linv^T * Linv
  for (int i = 0; i < m; ++i) {
    for (int j = 0; j <= i; ++j) {
      double s = 0.0;
      for (int k = i; k < m; ++k) s += Linv[k * m + i] * Linv[k * m + j];
      A[i * m + j] = A[j * m + i] = s;
    }
  }
}

SparseLut fit_r14(const std::vector<const FullLut*>& chain, uint32_t m, int threads,
                  bool adaptive) {
  if (chain.empty() || m < 2 || m > 256) throw std::runtime_error("invalid fit_r14 args");
#if defined(_OPENMP)
  const int hw = omp_get_max_threads();
  const int nth = (threads > 0) ? threads : ((hw >= 16) ? (hw / 2) : hw);
#else
  const int nth = 1;
  (void)threads;
#endif

  SparseLut L;
  L.m = m;
  std::vector<double> grid_d[3];
  for (int a = 0; a < 3; ++a) {
    L.grid[a].resize(m);
    grid_d[a].resize(m);
  }

  // 1. Curvature-adaptive knot placement (streaming 3 * 16 * 16 lines of 256 pixels in L1d)
  if (adaptive) {
    uint64_t global_d2[3][256] = {{0}};
#if defined(_OPENMP)
#pragma omp parallel num_threads(nth)
#endif
    {
      uint64_t local_d2[3][256] = {{0}};
      uint8_t line[256 * 3];
#if defined(_OPENMP)
#pragma omp for schedule(static)
#endif
      for (int lid = 0; lid < 3 * 16 * 16; ++lid) {
        const int a = lid >> 8;
        const uint8_t u = uint8_t(((lid >> 4) & 15) * 16);
        const uint8_t v = uint8_t((lid & 15) * 16);
        if (a == 0) {
          for (int x = 0; x < 256; ++x) {
            line[3 * x] = uint8_t(x);
            line[3 * x + 1] = u;
            line[3 * x + 2] = v;
          }
        } else if (a == 1) {
          for (int x = 0; x < 256; ++x) {
            line[3 * x] = u;
            line[3 * x + 1] = uint8_t(x);
            line[3 * x + 2] = v;
          }
        } else {
          for (int x = 0; x < 256; ++x) {
            line[3 * x] = u;
            line[3 * x + 1] = v;
            line[3 * x + 2] = uint8_t(x);
          }
        }
        for (const FullLut* F : chain) {
          const uint8_t* tab = F->data.data();
          for (int x = 0; x < 256; ++x) {
            const size_t o =
                ((size_t(line[3 * x]) << 16) | (size_t(line[3 * x + 1]) << 8) | line[3 * x + 2]) *
                3;
            line[3 * x] = tab[o];
            line[3 * x + 1] = tab[o + 1];
            line[3 * x + 2] = tab[o + 2];
          }
        }
        for (int x = 1; x < 255; ++x) {
          int d0 = std::abs(int(line[3 * (x + 1)]) - 2 * int(line[3 * x]) + int(line[3 * (x - 1)]));
          int d1 = std::abs(int(line[3 * (x + 1) + 1]) - 2 * int(line[3 * x + 1]) +
                            int(line[3 * (x - 1) + 1]));
          int d2 = std::abs(int(line[3 * (x + 1) + 2]) - 2 * int(line[3 * x + 2]) +
                            int(line[3 * (x - 1) + 2]));
          local_d2[a][x] += uint64_t(d0 + d1 + d2);
        }
      }
#if defined(_OPENMP)
#pragma omp critical
#endif
      {
        for (int a = 0; a < 3; ++a)
          for (int x = 1; x < 255; ++x) global_d2[a][x] += local_d2[a][x];
      }
    }

    for (int a = 0; a < 3; ++a) {
      double prof[256], dens[256], cdf[256];
      const double inv_cnt = 1.0 / (16.0 * 16.0 * 3.0);
      for (int x = 1; x < 255; ++x) prof[x] = double(global_d2[a][x]) * inv_cnt;
      prof[0] = prof[1];
      prof[255] = prof[254];
      double mean_dens = 0.0;
      for (int x = 0; x < 256; ++x) {
        dens[x] = std::pow(prof[x], 0.4);
        mean_dens += dens[x];
      }
      mean_dens /= 256.0;
      for (int x = 0; x < 256; ++x) dens[x] = 0.5 * dens[x] / (mean_dens + 1e-8) + 0.5;
      cdf[0] = 0.0;
      for (int x = 1; x < 256; ++x) cdf[x] = cdf[x - 1] + 0.5 * (dens[x] + dens[x - 1]);
      const double cdf_end = cdf[255];
      for (int x = 0; x < 256; ++x) cdf[x] /= cdf_end;

      for (uint32_t i = 0; i < m; ++i) {
        double t = double(i) / double(m - 1);
        int k = 0;
        while (k + 1 < 255 && cdf[k + 1] < t) ++k;
        double denom = cdf[k + 1] - cdf[k];
        grid_d[a][i] = (denom > 1e-12) ? (double(k) + (t - cdf[k]) / denom) : double(k);
      }
      grid_d[a][0] = 0.0;
      grid_d[a][m - 1] = 255.0;
      for (uint32_t i = 1; i < m; ++i)
        if (grid_d[a][i] < grid_d[a][i - 1] + 2.0) grid_d[a][i] = grid_d[a][i - 1] + 2.0;
      for (uint32_t i = 0; i < m; ++i) {
        double ub = 255.0 - 2.0 * double(m - 1 - i);
        if (grid_d[a][i] > ub) grid_d[a][i] = ub;
        L.grid[a][i] = float(grid_d[a][i]);
        grid_d[a][i] = double(L.grid[a][i]);  // match float32 round-trip
      }
    }
  } else {
    for (int a = 0; a < 3; ++a) {
      for (uint32_t i = 0; i < m; ++i) {
        grid_d[a][i] = double(i) * 255.0 / double(m - 1);
        L.grid[a][i] = float(grid_d[a][i]);
      }
    }
  }

  // 2. Build idx[3][256] and frac[3][256] matching Python io.axis_tables
  for (int a = 0; a < 3; ++a) {
    for (int x = 0; x < 256; ++x) {
      int i = 0;
      while (i + 1 < int(m) - 1 && double(x) >= grid_d[a][i + 1]) ++i;
      double f = (double(x) - grid_d[a][i]) / (grid_d[a][i + 1] - grid_d[a][i]);
      int32_t fq = int32_t(std::floor(f * double(kOne) + 0.5));
      if (fq < 0) fq = 0;
      if (fq > kOne) fq = kOne;
      L.idx[a][x] = uint8_t(i);
      L.frac[a][x] = uint32_t(fq);
    }
  }

  // 3. Evaluate 4-stage chain on the 64^3 subgrid (stride=4)
  uint8_t v_coord[64];
  for (int q = 0; q < 64; ++q) v_coord[q] = uint8_t(std::floor(q * 255.0 / 63.0 + 0.5));

  std::vector<uint8_t> Y_sub(64 * 64 * 64 * 3);
#if defined(_OPENMP)
#pragma omp parallel for schedule(static) num_threads(nth)
#endif
  for (int qr = 0; qr < 64; ++qr) {
    const uint8_t r0 = v_coord[qr];
    for (int qg = 0; qg < 64; ++qg) {
      const uint8_t g0 = v_coord[qg];
      uint8_t* out_row = &Y_sub[((qr * 64 + qg) * 64) * 3];
      for (int qb = 0; qb < 64; ++qb) {
        eval_chain_pixel(chain, r0, g0, v_coord[qb], out_row + 3 * qb);
      }
    }
  }

  // 4. Separable 1D Hat-basis initial guess x0 on the 64^3 subgrid
  float P_mat[3][256 * 64];  // m x 64 per axis
  for (int a = 0; a < 3; ++a) {
    std::vector<double> B(64 * m, 0.0);
    for (int q = 0; q < 64; ++q) {
      int x = v_coord[q];
      int idx_q = L.idx[a][x];
      double f = double(L.frac[a][x]) / double(kOne);
      B[q * m + idx_q] += 1.0 - f;
      B[q * m + idx_q + 1] += f;
    }
    std::vector<double> BtB(m * m, 0.0);
    for (uint32_t i = 0; i < m; ++i) {
      for (uint32_t j = 0; j < m; ++j) {
        double s = (i == j) ? 1e-6 : 0.0;
        for (int q = 0; q < 64; ++q) s += B[q * m + i] * B[q * m + j];
        BtB[i * m + j] = s;
      }
    }
    invert_spd(BtB, int(m));
    for (uint32_t i = 0; i < m; ++i) {
      for (int q = 0; q < 64; ++q) {
        double s = 0.0;
        for (uint32_t j = 0; j < m; ++j) s += BtB[i * m + j] * B[q * m + j];
        P_mat[a][i * 64 + q] = float(s);
      }
    }
  }

  const size_t M = size_t(m) * m * m;
  std::vector<float> T1(size_t(m) * 64 * 64 * 3, 0.0f);
  std::vector<float> T2(size_t(m) * m * 64 * 3, 0.0f);
  std::vector<float> x0(M * 3, 0.0f);

#if defined(_OPENMP)
#pragma omp parallel num_threads(nth)
#endif
  {
    // Contract axis 0: (m x 64) * (64 x 64*64*3)
#if defined(_OPENMP)
#pragma omp for schedule(static)
#endif
    for (int i = 0; i < int(m); ++i) {
      float* dst = &T1[size_t(i) * 64 * 64 * 3];
      for (int qr = 0; qr < 64; ++qr) {
        const float p = P_mat[0][i * 64 + qr];
        if (std::abs(p) < 1e-9f) continue;
        const uint8_t* src = &Y_sub[qr * 64 * 64 * 3];
        for (int k = 0; k < 64 * 64 * 3; ++k) dst[k] += p * float(src[k]);
      }
    }
    // Contract axis 1: (m x 64) * (m x 64 x 64*3)
#if defined(_OPENMP)
#pragma omp for schedule(static)
#endif
    for (int ij = 0; ij < int(m * m); ++ij) {
      const int i = ij / int(m), j = ij % int(m);
      float* dst = &T2[size_t(ij) * 64 * 3];
      for (int qg = 0; qg < 64; ++qg) {
        const float p = P_mat[1][j * 64 + qg];
        if (std::abs(p) < 1e-9f) continue;
        const float* src = &T1[(size_t(i) * 64 + qg) * 64 * 3];
        for (int k = 0; k < 64 * 3; ++k) dst[k] += p * src[k];
      }
    }
    // Contract axis 2: (m x 64) * (m*m x 64 x 3)
#if defined(_OPENMP)
#pragma omp for schedule(static)
#endif
    for (int ij = 0; ij < int(m * m); ++ij) {
      const float* src = &T2[size_t(ij) * 64 * 3];
      for (uint32_t k = 0; k < m; ++k) {
        float s0 = 0.0f, s1 = 0.0f, s2 = 0.0f;
        for (int qb = 0; qb < 64; ++qb) {
          const float p = P_mat[2][k * 64 + qb];
          s0 += p * src[3 * qb];
          s1 += p * src[3 * qb + 1];
          s2 += p * src[3 * qb + 2];
        }
        float* dst = &x0[(size_t(ij) * m + k) * 3];
        dst[0] = s0;
        dst[1] = s1;
        dst[2] = s2;
      }
    }
  }

  // 5. Assemble 15-point Lovasz stencil H and RHS b using 2-pass Even/Odd R-slab decomposition
  const int32_t sr = int32_t(m * m), sg = int32_t(m), sb = 1;
  const int32_t delta[7] = {sb, sg, sg + sb, sr, sr + sb, sr + sg, sr + sg + sb};
  const int32_t max_delta = sr + sg + sb;

  std::vector<float> H_diag(M, 0.0f);
  std::vector<float> H_up(M * 7, 0.0f);
  std::vector<float> b_vec(M * 3, 0.0f);

  std::vector<int> cell_q_start(m, 64), cell_q_end(m, 0);
  for (int q = 0; q < 64; ++q) {
    int c = L.idx[0][v_coord[q]];
    if (q < cell_q_start[c]) cell_q_start[c] = q;
    if (q + 1 > cell_q_end[c]) cell_q_end[c] = q + 1;
  }

  const float inv_one = 1.0f / float(kOne);
  for (int parity = 0; parity < 2; ++parity) {
#if defined(_OPENMP)
#pragma omp parallel for schedule(dynamic, 1) num_threads(nth)
#endif
    for (int cr = parity; cr < int(m) - 1; cr += 2) {
      const int q_beg = cell_q_start[cr], q_end = cell_q_end[cr];
      for (int qr = q_beg; qr < q_end; ++qr) {
        const uint8_t r = v_coord[qr];
        const int32_t off_r = int32_t(L.idx[0][r]) * sr;
        const int32_t fr = int32_t(L.frac[0][r]);
        for (int qg = 0; qg < 64; ++qg) {
          const uint8_t g = v_coord[qg];
          const int32_t off_rg = off_r + int32_t(L.idx[1][g]) * sg;
          const int32_t fg = int32_t(L.frac[1][g]);
          const uint8_t* y_row = &Y_sub[((qr * 64 + qg) * 64) * 3];
          for (int qb = 0; qb < 64; ++qb) {
            const uint8_t b = v_coord[qb];
            const int32_t u0 = off_rg + int32_t(L.idx[2][b]);
            const int32_t fb = int32_t(L.frac[2][b]);

            int32_t f1 = fr, f2 = fg, f3 = fb;
            int b1 = 4, b2 = 2, b3 = 1;
            int32_t s1 = sr, s2 = sg, s3 = sb;
            if (f2 > f1) { std::swap(f1, f2); std::swap(b1, b2); std::swap(s1, s2); }
            if (f3 > f1) { std::swap(f1, f3); std::swap(b1, b3); std::swap(s1, s3); }
            if (f3 > f2) { std::swap(f2, f3); std::swap(b2, b3); std::swap(s2, s3); }

            const int32_t v_idx[4] = {u0, u0 + s1, u0 + s1 + s2, u0 + max_delta};
            const int m_mask[4] = {0, b1, b1 | b2, 7};
            const float w[4] = {float(kOne - f1) * inv_one, float(f1 - f2) * inv_one,
                                float(f2 - f3) * inv_one, float(f3) * inv_one};
            const float yr = float(y_row[3 * qb]);
            const float yg = float(y_row[3 * qb + 1]);
            const float yb = float(y_row[3 * qb + 2]);

            for (int a = 0; a < 4; ++a) {
              const float wa = w[a];
              if (wa == 0.0f) continue;
              const int32_t va = v_idx[a];
              H_diag[va] += wa * wa;
              b_vec[3 * va] += wa * yr;
              b_vec[3 * va + 1] += wa * yg;
              b_vec[3 * va + 2] += wa * yb;
              for (int e = a + 1; e < 4; ++e) {
                const float we = w[e];
                if (we == 0.0f) continue;
                const int slot = (m_mask[e] - m_mask[a]) - 1;
                H_up[va * 7 + slot] += wa * we;
              }
            }
          }
        }
      }
    }
  }

  // Symmetrize into contiguous 14-neighbor table H_nb[M * 14]
  std::vector<float> H_nb(M * 14, 0.0f);
#if defined(_OPENMP)
#pragma omp parallel for schedule(static) num_threads(nth)
#endif
  for (long long u = 0; u < (long long)M; ++u) {
    float* dst = &H_nb[u * 14];
    for (int k = 0; k < 7; ++k) {
      dst[k] = H_up[u * 7 + k];
      dst[7 + k] = (u >= delta[k]) ? H_up[(u - delta[k]) * 7 + k] : 0.0f;
    }
  }

  // 6. 3-Channel Simultaneous Jacobi-Preconditioned Conjugate Gradient (solve_spd)
  constexpr float kLam = 1e-4f;
  std::vector<float> A_diag(M), P_inv(M), rhs(M * 3);
  std::vector<float> x_buf((M + 2 * size_t(max_delta)) * 3, 0.0f);
  std::vector<float> p_buf((M + 2 * size_t(max_delta)) * 3, 0.0f);
  float* x = x_buf.data() + size_t(max_delta) * 3;
  float* p = p_buf.data() + size_t(max_delta) * 3;
  std::vector<float> r(M * 3), z(M * 3), Ap(M * 3);

  for (size_t u = 0; u < M; ++u) {
    const float d = H_diag[u];
    const float D = d + 1.0f;
    A_diag[u] = d + kLam * D;
    P_inv[u] = 1.0f / A_diag[u];
    for (int c = 0; c < 3; ++c) {
      rhs[3 * u + c] = b_vec[3 * u + c] + kLam * D * x0[3 * u + c];
      x[3 * u + c] = x0[3 * u + c];
    }
  }

  auto spmv = [&](const float* vec_in, float* vec_out) {
#if defined(_OPENMP)
#pragma omp parallel for schedule(static) num_threads(nth)
#endif
    for (long long u = 0; u < (long long)M; ++u) {
      const float ad = A_diag[u];
      float s0 = ad * vec_in[3 * u];
      float s1 = ad * vec_in[3 * u + 1];
      float s2 = ad * vec_in[3 * u + 2];
      const float* h = &H_nb[u * 14];
      for (int k = 0; k < 7; ++k) {
        const float wu = h[k];
        const float wd = h[7 + k];
        const float* vu = vec_in + 3 * (u + delta[k]);
        const float* vd = vec_in + 3 * (u - delta[k]);
        s0 += wu * vu[0] + wd * vd[0];
        s1 += wu * vu[1] + wd * vd[1];
        s2 += wu * vu[2] + wd * vd[2];
      }
      vec_out[3 * u] = s0;
      vec_out[3 * u + 1] = s1;
      vec_out[3 * u + 2] = s2;
    }
  };

  spmv(x, Ap.data());
  double rz[3] = {0.0, 0.0, 0.0}, rhs_norm2[3] = {0.0, 0.0, 0.0};
  for (size_t u = 0; u < M; ++u) {
    const float pinv = P_inv[u];
    for (int c = 0; c < 3; ++c) {
      float rc = rhs[3 * u + c] - Ap[3 * u + c];
      float zc = pinv * rc;
      r[3 * u + c] = rc;
      z[3 * u + c] = zc;
      p[3 * u + c] = zc;
      rz[c] += double(rc) * double(zc);
      rhs_norm2[c] += double(rhs[3 * u + c]) * double(rhs[3 * u + c]);
    }
  }

  for (int iter = 0; iter < 20; ++iter) {
    spmv(p, Ap.data());
    double pAp0 = 0.0, pAp1 = 0.0, pAp2 = 0.0;
    for (size_t u = 0; u < M; ++u) {
      pAp0 += double(p[3 * u]) * double(Ap[3 * u]);
      pAp1 += double(p[3 * u + 1]) * double(Ap[3 * u + 1]);
      pAp2 += double(p[3 * u + 2]) * double(Ap[3 * u + 2]);
    }
    const float a0 = (pAp0 > 1e-20) ? float(rz[0] / pAp0) : 0.0f;
    const float a1 = (pAp1 > 1e-20) ? float(rz[1] / pAp1) : 0.0f;
    const float a2 = (pAp2 > 1e-20) ? float(rz[2] / pAp2) : 0.0f;

    double rz0 = 0.0, rz1 = 0.0, rz2 = 0.0;
    double rn0 = 0.0, rn1 = 0.0, rn2 = 0.0;
    for (size_t u = 0; u < M; ++u) {
      const float pinv = P_inv[u];
      x[3 * u] += a0 * p[3 * u];
      x[3 * u + 1] += a1 * p[3 * u + 1];
      x[3 * u + 2] += a2 * p[3 * u + 2];
      const float r0 = r[3 * u] - a0 * Ap[3 * u];
      const float r1 = r[3 * u + 1] - a1 * Ap[3 * u + 1];
      const float r2 = r[3 * u + 2] - a2 * Ap[3 * u + 2];
      const float z0 = pinv * r0, z1 = pinv * r1, z2 = pinv * r2;
      r[3 * u] = r0;
      r[3 * u + 1] = r1;
      r[3 * u + 2] = r2;
      z[3 * u] = z0;
      z[3 * u + 1] = z1;
      z[3 * u + 2] = z2;
      rz0 += double(r0) * double(z0);
      rz1 += double(r1) * double(z1);
      rz2 += double(r2) * double(z2);
      rn0 += double(r0) * double(r0);
      rn1 += double(r1) * double(r1);
      rn2 += double(r2) * double(r2);
    }
    if (rn0 <= 1e-9 * rhs_norm2[0] && rn1 <= 1e-9 * rhs_norm2[1] && rn2 <= 1e-9 * rhs_norm2[2])
      break;
    const float b0 = (rz[0] > 1e-20) ? float(rz0 / rz[0]) : 0.0f;
    const float b1 = (rz[1] > 1e-20) ? float(rz1 / rz[1]) : 0.0f;
    const float b2 = (rz[2] > 1e-20) ? float(rz2 / rz[2]) : 0.0f;
    rz[0] = rz0;
    rz[1] = rz1;
    rz[2] = rz2;
    for (size_t u = 0; u < M; ++u) {
      p[3 * u] = z[3 * u] + b0 * p[3 * u];
      p[3 * u + 1] = z[3 * u + 1] + b1 * p[3 * u + 1];
      p[3 * u + 2] = z[3 * u + 2] + b2 * p[3 * u + 2];
    }
  }

  // 7. 8-Colour Checkerboard Integer Coordinate Descent (int_refine, 1 stencil pass per sweep)
  for (size_t u = 0; u < M * 3; ++u) {
    float v = std::floor(x[u] + 0.5f);
    x[u] = v < 0.0f ? 0.0f : (v > 255.0f ? 255.0f : v);
  }

  for (int sw = 0; sw < 4; ++sw) {
    int changed = 0;
    for (int col = 0; col < 8; ++col) {
      const uint32_t pi = (col >> 2) & 1, pj = (col >> 1) & 1, pk = col & 1;
#if defined(_OPENMP)
#pragma omp parallel for schedule(static) reduction(+ : changed) num_threads(nth)
#endif
      for (uint32_t i = pi; i < m; i += 2) {
        for (uint32_t j = pj; j < m; j += 2) {
          for (uint32_t k = pk; k < m; k += 2) {
            const long long u = (static_cast<long long>(i) * m + j) * m + k;
            const float d = H_diag[u];
            if (d <= 0.0f) continue;
            const float half_d = 0.5f * d;
            float g0 = d * x[3 * u] - b_vec[3 * u];
            float g1 = d * x[3 * u + 1] - b_vec[3 * u + 1];
            float g2 = d * x[3 * u + 2] - b_vec[3 * u + 2];
            const float* h = &H_nb[u * 14];
            for (int nb = 0; nb < 7; ++nb) {
              const float wu = h[nb];
              const float wd = h[7 + nb];
              const float* vu = x + 3 * (u + delta[nb]);
              const float* vd = x + 3 * (u - delta[nb]);
              g0 += wu * vu[0] + wd * vd[0];
              g1 += wu * vu[1] + wd * vd[1];
              g2 += wu * vu[2] + wd * vd[2];
            }
            float g[3] = {g0, g1, g2};
            for (int c = 0; c < 3; ++c) {
              if (g[c] + half_d < -1e-6f && x[3 * u + c] + 1.0f <= 255.0f) {
                x[3 * u + c] += 1.0f;
                ++changed;
              } else if (-g[c] + half_d < -1e-6f && x[3 * u + c] - 1.0f >= 0.0f) {
                x[3 * u + c] -= 1.0f;
                ++changed;
              }
            }
          }
        }
      }
    }
    if (changed == 0) break;
  }

  L.nodes.resize(M * 3);
  for (size_t u = 0; u < M * 3; ++u) L.nodes[u] = uint8_t(int(x[u]));
  L.prepare();
  return L;
}

}  // namespace jshc
