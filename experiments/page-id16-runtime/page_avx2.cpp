/* 固定P4查表，复用原LE16四包独立读取和AVX2写出；x86专用。 */
#include "page_id16_internal.h"
#include <immintrin.h>
#include <cstring>
namespace {
inline __attribute__((always_inline)) uint32_t rgb(const jshc_p4_model *m, uint32_t code) {
    uint32_t value;
    std::memcpy(&value, p4_rgb(m, code), 4);
    return value;
}
inline __attribute__((always_inline)) __m256i read_exact(const jshc_p4_model *m, const unsigned char *p) {
    uint64_t a, b, c;
    std::memcpy(&a, p, 8); std::memcpy(&b, p + 8, 8); std::memcpy(&c, p + 16, 8);
    return _mm256_setr_epi32(int32_t(rgb(m, uint32_t(a & 0xffffff))),
        int32_t(rgb(m, uint32_t((a >> 24) & 0xffffff))),
        int32_t(rgb(m, uint32_t(((a >> 48) | (b << 16)) & 0xffffff))),
        int32_t(rgb(m, uint32_t((b >> 8) & 0xffffff))),
        int32_t(rgb(m, uint32_t((b >> 32) & 0xffffff))),
        int32_t(rgb(m, uint32_t(((b >> 56) | (c << 8)) & 0xffffff))),
        int32_t(rgb(m, uint32_t((c >> 16) & 0xffffff))), int32_t(rgb(m, uint32_t(c >> 40))));
}
inline __attribute__((always_inline)) __m256i read_wide(const jshc_p4_model *m, const unsigned char *p) {
    const auto id = [m,p](size_t offset) {
        uint32_t code; std::memcpy(&code, p + offset, 4);
        const uint32_t page = p4_le16(m->page_ids + 2 * (size_t)((code & 0xffffff) >> 12));
        return m->pool[(size_t)page * 4096 + (code & 4095)];
    };
    const auto color = [m](uint32_t index) {
        uint32_t value; std::memcpy(&value, m->palette + 4 * index, 4); return int32_t(value);
    };
    const uint32_t i0 = id(0), i1 = id(3), i2 = id(6), i3 = id(9);
    asm volatile("" : : "r"(i0), "r"(i1), "r"(i2), "r"(i3) : "memory");
    const __m128i lo = _mm_setr_epi32(color(i0), color(i1), color(i2), color(i3));
    const uint32_t i4 = id(12), i5 = id(15), i6 = id(18), i7 = id(21);
    asm volatile("" : : "r"(i4), "r"(i5), "r"(i6), "r"(i7) : "memory");
    const __m128i hi = _mm_setr_epi32(color(i4), color(i5), color(i6), color(i7));
    return _mm256_inserti128_si256(_mm256_castsi128_si256(lo), hi, 1);
}
inline __attribute__((always_inline)) __m256i bytes(__m256i value) {
    return _mm256_shuffle_epi8(value, _mm256_setr_epi8(0,1,2,4,5,6,8,9,10,12,13,14,-1,-1,-1,-1,0,1,2,4,5,6,8,9,10,12,13,14,-1,-1,-1,-1));
}
inline __attribute__((always_inline)) __m256i pack(__m256i value) {
    return _mm256_permutevar8x32_epi32(bytes(value), _mm256_setr_epi32(0,1,2,4,5,6,3,7));
}
inline __attribute__((always_inline)) __m256i stream0(__m256i value) { return pack(value); }
inline __attribute__((always_inline)) __m256i stream1(__m256i value) {
    return _mm256_permutevar8x32_epi32(bytes(value), _mm256_setr_epi32(2,4,5,6,3,7,0,1));
}
inline __attribute__((always_inline)) __m256i stream2(__m256i value) {
    return _mm256_permutevar8x32_epi32(bytes(value), _mm256_setr_epi32(5,6,3,7,0,1,2,4));
}
inline __attribute__((always_inline)) __m256i stream3(__m256i value) {
    return _mm256_permutevar8x32_epi32(bytes(value), _mm256_setr_epi32(3,7,0,1,2,4,5,6));
}
inline __attribute__((always_inline)) void output(unsigned char *p, __m256i value) {
    const __m256i packed = bytes(value);
    const __m128i lo = _mm256_castsi256_si128(packed), hi = _mm256_extracti128_si256(packed, 1);
    _mm_storeu_si128(reinterpret_cast<__m128i *>(p), _mm_or_si128(lo, _mm_slli_si128(hi, 12)));
    _mm_storel_epi64(reinterpret_cast<__m128i *>(p + 16), _mm_srli_si128(hi, 4));
}
inline __attribute__((always_inline)) void four(unsigned char *p, __m256i v0, __m256i v1, __m256i v2, __m256i v3) {
    const __m128i a = _mm256_castsi256_si128(v0), b = _mm256_extracti128_si256(v0,1);
    const __m128i c = _mm256_castsi256_si128(v1), d = _mm256_extracti128_si256(v1,1);
    const __m128i e = _mm256_castsi256_si128(v2), f = _mm256_extracti128_si256(v2,1);
    const __m128i g = _mm256_castsi256_si128(v3), h = _mm256_extracti128_si256(v3,1);
    _mm256_storeu_si256(reinterpret_cast<__m256i *>(p), _mm256_inserti128_si256(_mm256_castsi128_si256(a), _mm_unpacklo_epi64(b,c),1));
    _mm256_storeu_si256(reinterpret_cast<__m256i *>(p + 32), _mm256_inserti128_si256(_mm256_castsi128_si256(_mm_alignr_epi8(d,c,8)),e,1));
    _mm256_storeu_si256(reinterpret_cast<__m256i *>(p + 64), _mm256_inserti128_si256(_mm256_castsi128_si256(_mm_unpacklo_epi64(f,g)),_mm_alignr_epi8(h,g,8),1));
}
inline __attribute__((always_inline)) void four_stream(unsigned char *p, __m256i a, __m256i b, __m256i c, __m256i d) {
    _mm256_stream_si256(reinterpret_cast<__m256i *>(p), _mm256_blend_epi32(a,b,0xc0));
    _mm256_stream_si256(reinterpret_cast<__m256i *>(p + 32), _mm256_permute2x128_si256(b,c,0x30));
    _mm256_stream_si256(reinterpret_cast<__m256i *>(p + 64), _mm256_blend_epi32(d,c,0x03));
}
inline void one(const jshc_p4_model *m, const unsigned char *s, unsigned char *d) {
    const uint32_t code = uint32_t(s[0]) | (uint32_t(s[1]) << 8) | (uint32_t(s[2]) << 16);
    const uint32_t value = rgb(m, code);
    d[0] = uint8_t(value); d[1] = uint8_t(value >> 8); d[2] = uint8_t(value >> 16);
}
}
void jshc_p4_avx2_unchecked(const jshc_p4_model *m, const unsigned char *s,
                            unsigned char *d, size_t pixels) {
    size_t p = 0;
    const size_t initial = pixels * 3 < 1024 ? pixels * 3 : 1024;
    for (size_t offset = 0; offset < initial; offset += 64) _mm_prefetch(reinterpret_cast<const char *>(s + offset), _MM_HINT_NTA);
    for (; p < pixels && (reinterpret_cast<uintptr_t>(d + 3 * p) & 63); ++p) one(m, s + 3 * p, d + 3 * p);
    bool streamed = false;
    for (; pixels - p >= 72; p += 64) {
        if (pixels - p >= 406) {
            const unsigned char *future = s + 3 * p + 1024;
            _mm_prefetch(reinterpret_cast<const char *>(future), _MM_HINT_NTA);
            _mm_prefetch(reinterpret_cast<const char *>(future + 64), _MM_HINT_NTA);
            _mm_prefetch(reinterpret_cast<const char *>(future + 128), _MM_HINT_NTA);
            _mm_prefetch(reinterpret_cast<const char *>(future + 191), _MM_HINT_NTA);
        }
        const __m256i r0=stream0(read_wide(m,s+3*p)), r1=stream1(read_wide(m,s+3*p+24));
        const __m256i r2=stream2(read_wide(m,s+3*p+48)), r3=stream3(read_wide(m,s+3*p+72));
        const __m256i r4=stream0(read_wide(m,s+3*p+96)), r5=stream1(read_wide(m,s+3*p+120));
        const __m256i r6=stream2(read_wide(m,s+3*p+144)), r7=stream3(read_wide(m,s+3*p+168));
        four_stream(d+3*p,r0,r1,r2,r3); four_stream(d+3*p+96,r4,r5,r6,r7); streamed=true;
    }
    if (streamed) _mm_sfence();
    for (; pixels - p >= 40; p += 32) {
        const __m256i a=read_wide(m,s+3*p), b=read_wide(m,s+3*p+24);
        const __m256i c=read_wide(m,s+3*p+48), e=read_wide(m,s+3*p+72);
        four(d+3*p,pack(a),pack(b),pack(c),pack(e));
    }
    for (; pixels - p >= 8; p += 8) output(d+3*p,read_exact(m,s+3*p));
    for (; p < pixels; ++p) one(m,s+3*p,d+3*p);
}
