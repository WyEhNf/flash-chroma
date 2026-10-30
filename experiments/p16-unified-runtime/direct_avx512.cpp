#include "direct_avx512.h"

#include <immintrin.h>

#if defined(_MSC_VER)
#define P16_ALWAYS_INLINE __forceinline
#else
#define P16_ALWAYS_INLINE inline __attribute__((always_inline))
#endif

namespace jshc_channel {
namespace {

constexpr __mmask64 image_mask48 = (__mmask64(1) << 48) - 1;

// 只读取当前16像素的48字节。四个128bit lane分别重排连续四像素。
P16_ALWAYS_INLINE __m512i input_codes16(const std::uint8_t* p) noexcept {
  const __m512i bytes = _mm512_maskz_loadu_epi8(image_mask48, p);
  const __m512i grouped = _mm512_permutexvar_epi32(
      _mm512_setr_epi32(0, 1, 2, 3, 3, 4, 5, 6,
                        6, 7, 8, 9, 9, 10, 11, 12), bytes);
  const __m128i expand = _mm_setr_epi8(
      0, 1, 2, -1, 3, 4, 5, -1, 6, 7, 8, -1, 9, 10, 11, -1);
  return _mm512_shuffle_epi8(grouped, _mm512_broadcast_i32x4(expand));
}

// RGB32压缩为48字节，掩码写严格落在当前16像素范围内。
P16_ALWAYS_INLINE void output_rgb16(std::uint8_t* p, __m512i rgb) noexcept {
  const __m128i compress = _mm_setr_epi8(
      0, 1, 2, 4, 5, 6, 8, 9, 10, 12, 13, 14, -1, -1, -1, -1);
  const __m512i lane_rgb = _mm512_shuffle_epi8(
      rgb, _mm512_broadcast_i32x4(compress));
  const __m512i packed = _mm512_permutexvar_epi32(
      _mm512_setr_epi32(0, 1, 2, 4, 5, 6, 8, 9,
                        10, 12, 13, 14, 0, 0, 0, 0), lane_rgb);
  _mm512_mask_storeu_epi8(p, image_mask48, packed);
}

P16_ALWAYS_INLINE std::uint32_t input_code1(const std::uint8_t* p) noexcept {
  return std::uint32_t(p[0]) | (std::uint32_t(p[1]) << 8) |
         (std::uint32_t(p[2]) << 16);
}

P16_ALWAYS_INLINE void output_rgb1(std::uint8_t* p, std::uint32_t value) noexcept {
  p[0] = std::uint8_t(value);
  p[1] = std::uint8_t(value >> 8);
  p[2] = std::uint8_t(value >> 16);
}

template <unsigned Format>
P16_ALWAYS_INLINE __m512i lookup_ids16(const void* table, __m512i codes) noexcept {
  if constexpr (Format == 8) {
    // 完整256^3字节表不需要guard：取包含目标ID的对齐DWORD后移位。
    const __m512i words = _mm512_i32gather_epi32(
        _mm512_srli_epi32(codes, 2), table, 4);
    const __m512i shifts = _mm512_slli_epi32(
        _mm512_and_si512(codes, _mm512_set1_epi32(3)), 3);
    return _mm512_and_si512(
        _mm512_srlv_epi32(words, shifts), _mm512_set1_epi32(255));
  } else {
    // 最末ID的DWORD读取最多借用2个guard字节。
    return _mm512_and_si512(
        _mm512_i32gather_epi32(codes, table, 2), _mm512_set1_epi32(65535));
  }
}

template <unsigned Format>
P16_ALWAYS_INLINE __m512i lookup16(const void* table,
                                  const std::uint32_t* palette,
                                  __m512i codes) noexcept {
  if constexpr (Format == 24) {
    // RGB24最末项仅借用1个guard字节，最高字节不会输出。
    const __m512i offsets = _mm512_add_epi32(codes, _mm512_slli_epi32(codes, 1));
    return _mm512_i32gather_epi32(offsets, table, 1);
  } else {
    return _mm512_i32gather_epi32(lookup_ids16<Format>(table, codes), palette, 4);
  }
}

// 仅编译器屏障，无运行指令。明确保留四组独立请求的阶段边界，避免
// GCC把源码展开重新串回每16像素的ID->palette依赖链；不访问额外内存。
P16_ALWAYS_INLINE void stage_four(__m512i& a, __m512i& b,
                                  __m512i& c, __m512i& d) noexcept {
#if defined(_MSC_VER)
  _ReadWriteBarrier();
  (void)a; (void)b; (void)c; (void)d;
#else
  __asm__ volatile("" : "+v"(a), "+v"(b), "+v"(c), "+v"(d) : : "memory");
#endif
}

template <unsigned Format>
P16_ALWAYS_INLINE std::uint32_t lookup1(const void* table,
                                       const std::uint32_t* palette,
                                       std::uint32_t code) noexcept {
  if constexpr (Format == 8) {
    return palette[static_cast<const std::uint8_t*>(table)[code]];
  } else if constexpr (Format == 16) {
    // 字节读取同时支持非对齐的显式LE16载荷。
    const auto* p = static_cast<const std::uint8_t*>(table) + 2 * code;
    return palette[std::uint32_t(p[0]) | (std::uint32_t(p[1]) << 8)];
  } else {
    return input_code1(static_cast<const std::uint8_t*>(table) + 3 * code);
  }
}

template <unsigned Format>
P16_ALWAYS_INLINE void transform(const void* table, const std::uint32_t* palette,
                                 const std::uint8_t* source,
                                 std::uint8_t* output,
                                 std::size_t pixels) noexcept {
  // 差值门避免pixels接近SIZE_MAX时p+16溢出；调用方仍须提供合法图像长度。
  std::size_t p = 0;
  if constexpr (Format != 24) {
    for (; pixels - p >= 64; p += 64) {
      const std::uint8_t* input = source + 3 * p;
      __m512i a = input_codes16(input), b = input_codes16(input + 48);
      __m512i c = input_codes16(input + 96), d = input_codes16(input + 144);
      stage_four(a, b, c, d);
      // 四个ID请求互不依赖，先发齐请求再读取对应palette。
      a = lookup_ids16<Format>(table, a); b = lookup_ids16<Format>(table, b);
      c = lookup_ids16<Format>(table, c); d = lookup_ids16<Format>(table, d);
      stage_four(a, b, c, d);
      a = _mm512_i32gather_epi32(a, palette, 4);
      b = _mm512_i32gather_epi32(b, palette, 4);
      c = _mm512_i32gather_epi32(c, palette, 4);
      d = _mm512_i32gather_epi32(d, palette, 4);
      stage_four(a, b, c, d);
      // 64像素已全部读取，四个48B写入在原地和完全分离时均安全。
      std::uint8_t* destination = output + 3 * p;
      output_rgb16(destination, a); output_rgb16(destination + 48, b);
      output_rgb16(destination + 96, c); output_rgb16(destination + 144, d);
    }
  }
  for (; pixels - p >= 16; p += 16) {
    const __m512i codes = input_codes16(source + 3 * p);
    const __m512i rgb = lookup16<Format>(table, palette, codes);
    // 同一批16像素全部读取后才写回，因此source==output保持正确。
    output_rgb16(output + 3 * p, rgb);
  }
  for (; p < pixels; ++p) {
    const std::uint32_t code = input_code1(source + 3 * p);
    output_rgb1(output + 3 * p, lookup1<Format>(table, palette, code));
  }
}

} // namespace

void avx512_direct_u8(const std::uint8_t* ids, const std::uint32_t* palette,
                      const std::uint8_t* source, std::uint8_t* output,
                      std::size_t pixels) noexcept {
  transform<8>(ids, palette, source, output, pixels);
}

void avx512_direct_u16(const std::uint16_t* ids, const std::uint32_t* palette,
                       const std::uint8_t* source, std::uint8_t* output,
                       std::size_t pixels) noexcept {
  transform<16>(ids, palette, source, output, pixels);
}

void avx512_direct_rgb24(const std::uint8_t* table, const std::uint8_t* source,
                         std::uint8_t* output, std::size_t pixels) noexcept {
  transform<24>(table, nullptr, source, output, pixels);
}

} // namespace jshc_channel
