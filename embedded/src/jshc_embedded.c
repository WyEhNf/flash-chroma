#include "jshc_embedded.h"

/* 按字节读 little-endian，兼容非对齐地址与不同宿主字节序。 */
static uint32_t read32(const uint8_t *p)
{
    return (uint32_t)p[0] | ((uint32_t)p[1] << 8) |
           ((uint32_t)p[2] << 16) | ((uint32_t)p[3] << 24);
}

jshc_embedded_status jshc_embedded_init(jshc_embedded_lut *out,
                                     const void *data, size_t bytes)
{
    const uint8_t *p = (const uint8_t *)data;
    uint32_t m;
    size_t axis, expected, a, x;
    if (!out) return JSHC_EMBEDDED_ARGUMENT;
    out->m = 0;
    out->idx = out->frac = out->nodes = NULL;
    if (!p) return JSHC_EMBEDDED_ARGUMENT;
    if (bytes < 16 || p[0] != 'S' || p[1] != 'L' || p[2] != 'U' || p[3] != 'T' ||
        read32(p + 4) != 1 || read32(p + 12) != 0)
        return JSHC_EMBEDDED_FORMAT;
    m = read32(p + 8);
    if (m < 2 || m > 256) return JSHC_EMBEDDED_FORMAT;
    axis = 16 + (size_t)12 * m;
    expected = axis + 3 * 256 + 3 * 256 * 4 + (size_t)m * m * m * 3;
    if (bytes != expected) return JSHC_EMBEDDED_FORMAT;
    for (a = 0; a < 3; ++a) {
        for (x = 0; x < 256; ++x) {
            if (p[axis + a * 256 + x] > m - 2 ||
                read32(p + axis + 768 + (a * 256 + x) * 4) > 65536)
                return JSHC_EMBEDDED_FORMAT;
        }
    }
    out->m = m;
    out->idx = p + axis;
    out->frac = out->idx + 768;
    out->nodes = out->frac + 3072;
    return JSHC_EMBEDDED_OK;
}

static void swap_axis(uint32_t *hi, uint32_t *lo, size_t *s_hi, size_t *s_lo)
{
    if (*lo > *hi) {
        uint32_t f = *hi;
        size_t s = *s_hi;
        *hi = *lo; *lo = f;
        *s_hi = *s_lo; *s_lo = s;
    }
}

static void pixel(const jshc_embedded_lut *lut, uint8_t *rgb)
{
    const size_t r = rgb[0], g = rgb[1], b = rgb[2];
    size_t s1 = (size_t)lut->m * lut->m, s2 = lut->m, s3 = 1;
    const size_t base = (size_t)lut->idx[r] * s1 +
                        (size_t)lut->idx[256 + g] * s2 + lut->idx[512 + b];
    uint32_t f1 = read32(lut->frac + r * 4);
    uint32_t f2 = read32(lut->frac + (256 + g) * 4);
    uint32_t f3 = read32(lut->frac + (512 + b) * 4);
    const uint8_t *v0, *v1, *v2, *v3;
    size_t c;
    swap_axis(&f1, &f2, &s1, &s2);
    swap_axis(&f1, &f3, &s1, &s3);
    swap_axis(&f2, &f3, &s2, &s3);
    v0 = lut->nodes + base * 3;
    v1 = v0 + s1 * 3;
    v2 = v1 + s2 * 3;
    v3 = v2 + s3 * 3;
    for (c = 0; c < 3; ++c) {
        /* 非负重心权重和为 65536，最大分子 255*65536+32768，适合 u32。 */
        const uint32_t sum = (65536 - f1) * v0[c] + (f1 - f2) * v1[c] +
                             (f2 - f3) * v2[c] + f3 * v3[c] + 32768;
        rgb[c] = (uint8_t)(sum >> 16);
    }
}

jshc_embedded_status jshc_embedded_apply(const jshc_embedded_lut *const *chain,
                                      size_t stages, uint8_t *rgb, size_t pixels)
{
    size_t i, s;
    if (stages > 4 || (stages && !chain) || (pixels && !rgb) || pixels > SIZE_MAX / 3)
        return JSHC_EMBEDDED_ARGUMENT;
    for (s = 0; s < stages; ++s) {
        const jshc_embedded_lut *lut = chain[s];
        if (!lut || lut->m < 2 || lut->m > 256 || !lut->idx || !lut->frac || !lut->nodes)
            return JSHC_EMBEDDED_ARGUMENT;
    }
    if (!stages) return JSHC_EMBEDDED_OK;
    for (i = 0; i < pixels; ++i)
        for (s = 0; s < stages; ++s) pixel(chain[s], rgb + 3 * i);
    return JSHC_EMBEDDED_OK;
}
