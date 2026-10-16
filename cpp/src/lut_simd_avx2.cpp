// Explicit AVX2 is isolated here; never compile the baseline dispatcher with
// -mavx2 / -march=native. Every stage preserves integer Q16 round-half-up.
#include "lut_simd_avx2.hpp"

#include <immintrin.h>

namespace jshc::detail {
namespace {

struct Rgb8 { __m256i r, g, b; };
// Keep this over-aligned aggregate behind references. In particular, MinGW's
// Win64 by-value aggregate call lowering may place a temporary at a merely
// 16-byte-aligned stack address while emitting 32-byte vmovdqa stores.

template<bool scalar_gather>
inline __m256i gather(const uint32_t* table, __m256i index) noexcept {
  if constexpr (scalar_gather) {
    alignas(32) uint32_t indices[8];
    _mm256_store_si256(reinterpret_cast<__m256i*>(indices), index);
    return _mm256_setr_epi32(table[indices[0]], table[indices[1]], table[indices[2]], table[indices[3]],
                            table[indices[4]], table[indices[5]], table[indices[6]], table[indices[7]]);
  } else {
    return _mm256_i32gather_epi32(reinterpret_cast<const int*>(table), index, 4);
  }
}

inline void load_rgb8(const uint8_t* p, Rgb8& rgb) noexcept {
  // Two bounded loads cover precisely 24 bytes, including the final vector.
  const __m128i lo = _mm_loadu_si128(reinterpret_cast<const __m128i*>(p));
  const __m128i last = _mm_loadl_epi64(reinterpret_cast<const __m128i*>(p + 16));
  const __m128i hi = _mm_alignr_epi8(last, lo, 12);
  const __m256i raw = _mm256_inserti128_si256(_mm256_castsi128_si256(lo), hi, 1);
  const __m256i shuffle = _mm256_setr_epi8(
      0,1,2,-1,3,4,5,-1,6,7,8,-1,9,10,11,-1,
      0,1,2,-1,3,4,5,-1,6,7,8,-1,9,10,11,-1);
  const __m256i packed = _mm256_shuffle_epi8(raw, shuffle);
  const __m256i mask = _mm256_set1_epi32(255);
  rgb.r = _mm256_and_si256(packed, mask);
  rgb.g = _mm256_and_si256(_mm256_srli_epi32(packed, 8), mask);
  rgb.b = _mm256_srli_epi32(packed, 16);
}

inline void store_rgb8(uint8_t* p, const Rgb8& rgb) noexcept {
  const __m256i packed = _mm256_or_si256(rgb.r, _mm256_or_si256(
      _mm256_slli_epi32(rgb.g, 8), _mm256_slli_epi32(rgb.b, 16)));
  const __m256i shuffle = _mm256_setr_epi8(
      0,1,2,4,5,6,8,9,10,12,13,14,-1,-1,-1,-1,
      0,1,2,4,5,6,8,9,10,12,13,14,-1,-1,-1,-1);
  const __m256i bytes = _mm256_shuffle_epi8(packed, shuffle);
  const __m128i lo = _mm256_castsi256_si128(bytes);
  const __m128i hi = _mm256_extracti128_si256(bytes, 1);
  _mm_storeu_si128(reinterpret_cast<__m128i*>(p),
                  _mm_or_si128(lo, _mm_slli_si128(hi, 12)));
  _mm_storel_epi64(reinterpret_cast<__m128i*>(p + 16), _mm_srli_si128(hi, 4));
}

template<int shift>
inline __m256i channel(__m256i v0, __m256i v1, __m256i v2, __m256i v3,
                       __m256i f1, __m256i f2, __m256i f3) noexcept {
  const __m256i mask = _mm256_set1_epi32(255);
  const __m256i c0 = _mm256_and_si256(_mm256_srli_epi32(v0, shift), mask);
  const __m256i c1 = _mm256_and_si256(_mm256_srli_epi32(v1, shift), mask);
  const __m256i c2 = _mm256_and_si256(_mm256_srli_epi32(v2, shift), mask);
  const __m256i c3 = _mm256_and_si256(_mm256_srli_epi32(v3, shift), mask);
  const __m256i acc = _mm256_add_epi32(_mm256_slli_epi32(c0, 16),
      _mm256_add_epi32(_mm256_mullo_epi32(_mm256_sub_epi32(c1, c0), f1),
      _mm256_add_epi32(_mm256_mullo_epi32(_mm256_sub_epi32(c2, c1), f2),
                      _mm256_mullo_epi32(_mm256_sub_epi32(c3, c2), f3))));
  return _mm256_srli_epi32(_mm256_add_epi32(acc, _mm256_set1_epi32(32768)), 16);
}

template<int shift>
inline __m256i channel_madd(__m256i v0, __m256i v1, __m256i v2, __m256i v3,
                            __m256i high_node, __m256i f12, __m256i f3_signed) noexcept {
  const __m256i byte_mask = _mm256_set1_epi32(255);
  const __m256i c0 = _mm256_and_si256(_mm256_srli_epi32(v0, shift), byte_mask);
  const __m256i c1 = _mm256_and_si256(_mm256_srli_epi32(v1, shift), byte_mask);
  const __m256i c2 = _mm256_and_si256(_mm256_srli_epi32(v2, shift), byte_mask);
  const __m256i c3 = _mm256_and_si256(_mm256_srli_epi32(v3, shift), byte_mask);
  const __m256i d12 = _mm256_or_si256(
      _mm256_and_si256(_mm256_sub_epi32(c1, c0), _mm256_set1_epi32(65535)),
      _mm256_slli_epi32(_mm256_sub_epi32(c2, c1), 16));
  const __m256i high = _mm256_and_si256(_mm256_srli_epi32(high_node, shift), byte_mask);
  const __m256i sum = _mm256_add_epi32(_mm256_slli_epi32(high, 16),
      _mm256_add_epi32(_mm256_madd_epi16(d12, f12),
                       _mm256_mullo_epi32(_mm256_sub_epi32(c3, c2), f3_signed)));
  return _mm256_srli_epi32(_mm256_add_epi32(sum, _mm256_set1_epi32(32768)), 16);
}

template<int shift>
inline __m256i channel_exact_float(__m256i v0, __m256i v1, __m256i v2, __m256i v3,
                                   __m256 w0, __m256 w1, __m256 w2, __m256 w3) noexcept {
  const __m256i mask = _mm256_set1_epi32(255);
  const __m256 c0 = _mm256_cvtepi32_ps(_mm256_and_si256(_mm256_srli_epi32(v0, shift), mask));
  const __m256 c1 = _mm256_cvtepi32_ps(_mm256_and_si256(_mm256_srli_epi32(v1, shift), mask));
  const __m256 c2 = _mm256_cvtepi32_ps(_mm256_and_si256(_mm256_srli_epi32(v2, shift), mask));
  const __m256 c3 = _mm256_cvtepi32_ps(_mm256_and_si256(_mm256_srli_epi32(v3, shift), mask));
  __m256 sum = _mm256_mul_ps(c0, w0);
  sum = _mm256_add_ps(sum, _mm256_mul_ps(c1, w1));
  sum = _mm256_add_ps(sum, _mm256_mul_ps(c2, w2));
  sum = _mm256_add_ps(sum, _mm256_mul_ps(c3, w3));
  sum = _mm256_add_ps(sum, _mm256_set1_ps(32768.0f));
  return _mm256_srli_epi32(_mm256_cvttps_epi32(sum), 16);
}

template<bool use_madd, bool scalar_gather, bool exact_float = false>
inline void transform(const Avx2LutView& L, Rgb8& rgb) noexcept {
  // Combining cell index and Q16 fraction saves three gathers per stage.
  // Seventeen fraction bits preserve the exact endpoint 65536.
  const __m256i ar = gather<scalar_gather>(L.axis, rgb.r);
  const __m256i ag = gather<scalar_gather>(L.axis + 256, rgb.g);
  const __m256i ab = gather<scalar_gather>(L.axis + 512, rgb.b);
  const __m256i sr = _mm256_set1_epi32(L.sr);
  const __m256i sg = _mm256_set1_epi32(L.sg);
  const __m256i sb = _mm256_set1_epi32(1);
  const __m256i total = _mm256_set1_epi32(L.sr + L.sg + 1);
  const __m256i base = _mm256_add_epi32(
      _mm256_mullo_epi32(_mm256_srli_epi32(ar, 17), sr),
      _mm256_add_epi32(_mm256_mullo_epi32(_mm256_srli_epi32(ag, 17), sg),
                       _mm256_srli_epi32(ab, 17)));
  const __m256i mask = _mm256_set1_epi32(0x1ffff);
  const __m256i fr = _mm256_and_si256(ar, mask);
  const __m256i fg = _mm256_and_si256(ag, mask);
  const __m256i fb = _mm256_and_si256(ab, mask);
  __m256i smax = _mm256_blendv_epi8(sr, sg, _mm256_cmpgt_epi32(fg, fr));
  __m256i f1 = _mm256_max_epi32(fr, fg);
  smax = _mm256_blendv_epi8(smax, sb, _mm256_cmpgt_epi32(fb, f1));
  f1 = _mm256_max_epi32(f1, fb);
  __m256i smin = _mm256_blendv_epi8(sr, sg, _mm256_cmpgt_epi32(fr, fg));
  __m256i f3 = _mm256_min_epi32(fr, fg);
  smin = _mm256_blendv_epi8(smin, sb, _mm256_cmpgt_epi32(f3, fb));
  f3 = _mm256_min_epi32(f3, fb);
  const __m256i f2 = _mm256_sub_epi32(_mm256_sub_epi32(
      _mm256_add_epi32(fr, _mm256_add_epi32(fg, fb)), f1), f3);
  const __m256i v0 = gather<scalar_gather>(L.nodes, base);
  const __m256i v1 = gather<scalar_gather>(L.nodes, _mm256_add_epi32(base, smax));
  const __m256i v2 = gather<scalar_gather>(L.nodes,
      _mm256_sub_epi32(_mm256_add_epi32(base, total), smin));
  const __m256i v3 = gather<scalar_gather>(L.nodes, _mm256_add_epi32(base, total));
  if constexpr (exact_float) {
    // All weights are nonnegative integers with sum 65536, so each product
    // AND every partial sum is <= 255*65536. Even the rounded numerator is
    // <= 255*65536+32768 < 2^24. Binary32 therefore represents every operation
    // exactly. This proof depends on RGB8 nodes and the current Q16 format.
    const __m256 w0 = _mm256_cvtepi32_ps(_mm256_sub_epi32(_mm256_set1_epi32(65536), f1));
    const __m256 w1 = _mm256_cvtepi32_ps(_mm256_sub_epi32(f1, f2));
    const __m256 w2 = _mm256_cvtepi32_ps(_mm256_sub_epi32(f2, f3));
    const __m256 w3 = _mm256_cvtepi32_ps(f3);
    rgb.r = channel_exact_float<0>(v0,v1,v2,v3,w0,w1,w2,w3);
    rgb.g = channel_exact_float<8>(v0,v1,v2,v3,w0,w1,w2,w3);
    rgb.b = channel_exact_float<16>(v0,v1,v2,v3,w0,w1,w2,w3);
  } else if constexpr (use_madd) {
    // f = int16(f) + 65536*[f >= 32768], including f == 65536.
    // Sorted f1 >= f2 >= f3 makes the high correction telescope to one
    // packed RGB node, shared by all channels rather than three extra products.
    const __m256i threshold = _mm256_set1_epi32(32767);
    __m256i high = _mm256_blendv_epi8(v0, v1, _mm256_cmpgt_epi32(f1, threshold));
    high = _mm256_blendv_epi8(high, v2, _mm256_cmpgt_epi32(f2, threshold));
    high = _mm256_blendv_epi8(high, v3, _mm256_cmpgt_epi32(f3, threshold));
    const __m256i f12 = _mm256_or_si256(_mm256_and_si256(f1, _mm256_set1_epi32(65535)),
                                       _mm256_slli_epi32(f2, 16));
    const __m256i f3_signed = _mm256_srai_epi32(_mm256_slli_epi32(f3, 16), 16);
    rgb.r = channel_madd<0>(v0,v1,v2,v3,high,f12,f3_signed);
    rgb.g = channel_madd<8>(v0,v1,v2,v3,high,f12,f3_signed);
    rgb.b = channel_madd<16>(v0,v1,v2,v3,high,f12,f3_signed);
  } else {
    rgb.r = channel<0>(v0,v1,v2,v3,f1,f2,f3);
    rgb.g = channel<8>(v0,v1,v2,v3,f1,f2,f3);
    rgb.b = channel<16>(v0,v1,v2,v3,f1,f2,f3);
  }
}

inline void unpack_packed(__m256i value, Rgb8& rgb) noexcept {
  const __m256i mask = _mm256_set1_epi32(255);
  rgb.r = _mm256_and_si256(value, mask);
  rgb.g = _mm256_and_si256(_mm256_srli_epi32(value, 8), mask);
  rgb.b = _mm256_srli_epi32(value, 16);
}

inline void structured_transform(const StructuredLutView& L, Rgb8& rgb) noexcept {
  if (L.path == 3) {
    unpack_packed(_mm256_set1_epi32(static_cast<int32_t>(L.constant_rgb)), rgb);
  } else if (L.path == 1) {
    const __m256i r = gather<true>(L.curves[0], rgb.r);
    const __m256i g = gather<true>(L.curves[1], rgb.g);
    const __m256i b = gather<true>(L.curves[2], rgb.b);
    unpack_packed(_mm256_or_si256(_mm256_or_si256(r, g),
      _mm256_or_si256(b, _mm256_set1_epi32(static_cast<int32_t>(L.constant_rgb)))), rgb);
  } else if (L.path == 2) {
    const auto& V = L.generic;
    const __m256i r = gather<true>(V.axis, rgb.r);
    const __m256i g = gather<true>(V.axis + 256, rgb.g);
    const __m256i b = gather<true>(V.axis + 512, rgb.b);
    // Every reachable fraction is exactly 0 or 65536. Bit 16 therefore
    // chooses the upper endpoint, while bits 17+ retain the lower cell index.
    const __m256i one = _mm256_set1_epi32(1);
    const auto endpoint = [&](const __m256i value) {
      return _mm256_add_epi32(_mm256_srli_epi32(value, 17),
                              _mm256_and_si256(_mm256_srli_epi32(value, 16), one));
    };
    const __m256i index = _mm256_add_epi32(
      _mm256_mullo_epi32(endpoint(r), _mm256_set1_epi32(V.sr)),
      _mm256_add_epi32(_mm256_mullo_epi32(endpoint(g), _mm256_set1_epi32(V.sg)), endpoint(b)));
    unpack_packed(gather<true>(V.nodes, index), rgb);
  } else {
    transform<false, true>(L.generic, rgb);
  }
}

template<bool use_madd, bool scalar_gather, bool exact_float = false>
void chain_impl(const Avx2LutView* chain, size_t stages, const uint8_t* in,
                 uint8_t* out, size_t n) noexcept {
  for (size_t i = 0; i < n; i += 8) {
    Rgb8 rgb;
    load_rgb8(in + 3 * i, rgb);
    // The four-stage submission path never interleaves/deinterleaves between LUTs.
    // Integer rounding inside transform is retained after EACH independent LUT.
    if (stages == 4) {
      transform<use_madd, scalar_gather, exact_float>(chain[0], rgb);
      transform<use_madd, scalar_gather, exact_float>(chain[1], rgb);
      transform<use_madd, scalar_gather, exact_float>(chain[2], rgb);
      transform<use_madd, scalar_gather, exact_float>(chain[3], rgb);
    } else {
      for (size_t s = 0; s < stages; ++s) transform<use_madd, scalar_gather, exact_float>(chain[s], rgb);
    }
    store_rgb8(out + 3 * i, rgb);
  }
}
}  // namespace

void avx2_chain(const Avx2LutView* chain, size_t stages, const uint8_t* in,
                uint8_t* out, size_t n) noexcept {
  chain_impl<false, false>(chain, stages, in, out, n);
}

void avx2_chain_madd(const Avx2LutView* chain, size_t stages, const uint8_t* in,
                     uint8_t* out, size_t n) noexcept {
  chain_impl<true, false>(chain, stages, in, out, n);
}

void avx2_chain_scalar_gather(const Avx2LutView* chain, size_t stages, const uint8_t* in,
                              uint8_t* out, size_t n) noexcept {
  chain_impl<false, true>(chain, stages, in, out, n);
}

void avx2_chain_exact_float(const Avx2LutView* chain, size_t stages, const uint8_t* in,
                            uint8_t* out, size_t n) noexcept {
  chain_impl<false, false, true>(chain, stages, in, out, n);
}

void avx2_structured_chain(const StructuredLutView* chain, const uint8_t* in,
                           uint8_t* out, size_t n) noexcept {
  for (size_t i = 0; i < n; i += 8) {
    Rgb8 rgb;
    load_rgb8(in + 3 * i, rgb);
    structured_transform(chain[0], rgb);
    structured_transform(chain[1], rgb);
    structured_transform(chain[2], rgb);
    structured_transform(chain[3], rgb);
    store_rgb8(out + 3 * i, rgb);
  }
}
}  // namespace jshc::detail
