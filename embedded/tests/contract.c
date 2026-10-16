/* 宿主与 FreeRTOS 共用的确定性契约测试；不需要堆、文件或外部数据。 */
#include "jshc_embedded.h"

#define MAX_MODEL (16 + 12 * 33 + 3840 + 33 * 33 * 33 * 3)
#define CHECK(x) do { if (!(x)) return __LINE__; } while (0)
static uint8_t models[4][MAX_MODEL + 3];
static jshc_embedded_lut luts[4];
static const jshc_embedded_lut *chain[4];

static void write32(uint8_t *p, uint32_t v)
{
    size_t i;
    for (i = 0; i < 4; ++i) p[i] = (uint8_t)(v >> (8 * i));
}

static uint32_t read32(const uint8_t *p)
{
    return (uint32_t)p[0] | ((uint32_t)p[1] << 8) |
           ((uint32_t)p[2] << 16) | ((uint32_t)p[3] << 24);
}

static uint32_t grid(uint32_t i, uint32_t m, size_t axis)
{
    const uint32_t uniform = i * 255 / (m - 1);
    return axis == 1 ? (uniform + i * i * 255 / ((m - 1) * (m - 1))) / 2 : uniform;
}

static size_t make_model(uint8_t *p, uint32_t m, uint32_t seed)
{
    const size_t axis = 16 + 12 * m;
    const size_t bytes = axis + 3840 + (size_t)m * m * m * 3;
    size_t i, a, x;
    for (i = 0; i < bytes; ++i) p[i] = 0;
    p[0] = 'S'; p[1] = 'L'; p[2] = 'U'; p[3] = 'T';
    write32(p + 4, 1); write32(p + 8, m);
    for (a = 0; a < 3; ++a) {
        /* 元数据编码为整数网格的 IEEE754 binary32，不执行浮点计算。 */
        for (i = 0; i < m; ++i) {
            uint32_t value = grid((uint32_t)i, m, a), exponent = 127 + 23;
            if (value) {
                while (value < (1u << 23)) { value <<= 1; --exponent; }
                value = (exponent << 23) | (value & 0x7fffff);
            }
            write32(p + 16 + (a * m + i) * 4, value);
        }
        for (x = 0; x < 256; ++x) {
            uint32_t cell = 0;
            uint32_t lo, hi;
            while (cell < m - 2 && grid(cell + 1, m, a) <= x) ++cell;
            lo = grid(cell, m, a); hi = grid(cell + 1, m, a);
            p[axis + a * 256 + x] = (uint8_t)cell;
            write32(p + axis + 768 + (a * 256 + x) * 4,
                    ((uint32_t)(x - lo) * 65536 + (hi - lo) / 2) / (hi - lo));
        }
    }
    for (i = axis + 3840; i < bytes; ++i) {
        seed = seed * 1664525u + 1013904223u;
        p[i] = (uint8_t)(seed >> 24);
    }
    return bytes;
}

/* 独立参考：按轴排名挑选四个顶点，使用 u64 重心累加。
 * 不调用生产排序网络、pixel 或任何桌面内核。 */
static void oracle(const jshc_embedded_lut *lut, uint8_t *rgb)
{
    size_t order[3] = {0, 1, 2}, i, j, c;
    const size_t stride[3] = {(size_t)lut->m * lut->m, lut->m, 1};
    uint32_t f[3];
    size_t vertices[4];
    uint32_t weights[4];
    vertices[0] = 0;
    for (i = 0; i < 3; ++i) {
        vertices[0] += lut->idx[i * 256 + rgb[i]] * stride[i];
        f[i] = read32(lut->frac + (i * 256 + rgb[i]) * 4);
    }
    for (i = 0; i < 3; ++i)
        for (j = i + 1; j < 3; ++j)
            if (f[order[j]] > f[order[i]]) {
                size_t tmp = order[i]; order[i] = order[j]; order[j] = tmp;
            }
    for (i = 0; i < 3; ++i) vertices[i + 1] = vertices[i] + stride[order[i]];
    weights[0] = 65536 - f[order[0]];
    weights[1] = f[order[0]] - f[order[1]];
    weights[2] = f[order[1]] - f[order[2]];
    weights[3] = f[order[2]];
    for (c = 0; c < 3; ++c) {
        uint64_t sum = 32768;
        for (i = 0; i < 4; ++i) sum += (uint64_t)weights[i] * lut->nodes[vertices[i] * 3 + c];
        rgb[c] = (uint8_t)(sum / 65536);
    }
}

int jshc_embedded_contract(void (*checkpoint)(void))
{
    const uint32_t sizes[4] = {17, 18, 25, 33};
    size_t bytes[4], s, i, len;
    uint8_t rgb[3 * 257 + 2], expected[3 * 257 + 2];
    jshc_embedded_lut bad;
    uint32_t seed = 9;
    for (s = 0; s < 4; ++s) {
        /* 模型从 +1 地址开始，保证 frac 也不对齐。 */
        bytes[s] = make_model(models[s] + 1, sizes[s], (uint32_t)s + 41);
        CHECK(jshc_embedded_init(&luts[s], models[s] + 1, bytes[s]) == JSHC_EMBEDDED_OK);
        chain[s] = &luts[s];
    }
    for (len = 0; len <= 257; ++len) {
        for (i = 0; i < sizeof(rgb); ++i) {
            seed = seed * 1664525u + 1013904223u;
            expected[i] = rgb[i] = (uint8_t)(seed >> 24);
        }
        for (i = 0; i < len; ++i)
            for (s = 0; s < 4; ++s) oracle(chain[s], expected + 1 + i * 3);
        CHECK(jshc_embedded_apply(chain, 4, rgb + 1, len) == JSHC_EMBEDDED_OK);
        for (i = 0; i < sizeof(rgb); ++i) CHECK(rgb[i] == expected[i]);
        if (checkpoint && len % 32 == 0) checkpoint();
    }
    /* 覆盖 Q16 端点、半值、六种轴次序、恒 255 及极端节点。 */
    {
        const uint32_t fractions[7] = {0, 1, 32767, 32768, 32769, 65535, 65536};
        size_t a, x, r, g, b, pattern;
        uint8_t *p = models[0] + 1;
        bytes[0] = make_model(p, 2, 1);
        for (a = 0; a < 3; ++a)
            for (x = 0; x < 256; ++x)
                write32(p + 40 + 768 + (a * 256 + x) * 4, fractions[x % 7]);
        CHECK(jshc_embedded_init(&luts[0], p, bytes[0]) == JSHC_EMBEDDED_OK);
        for (pattern = 0; pattern < 2; ++pattern) {
            for (i = 40 + 3840; i < bytes[0]; ++i) p[i] = pattern ? (uint8_t)(i % 2 ? 255 : 0) : 255;
            for (r = 0; r < 7; ++r) for (g = 0; g < 7; ++g) for (b = 0; b < 7; ++b) {
                expected[0] = rgb[0] = (uint8_t)r;
                expected[1] = rgb[1] = (uint8_t)g;
                expected[2] = rgb[2] = (uint8_t)b;
                oracle(&luts[0], expected);
                CHECK(jshc_embedded_apply(chain, 1, rgb, 1) == JSHC_EMBEDDED_OK);
                for (i = 0; i < 3; ++i) CHECK(rgb[i] == expected[i]);
            }
        }
    }
    CHECK(jshc_embedded_init(NULL, models[0] + 1, bytes[0]) == JSHC_EMBEDDED_ARGUMENT);
    CHECK(jshc_embedded_init(&bad, NULL, 0) == JSHC_EMBEDDED_ARGUMENT);
    for (i = 0; i < bytes[0]; ++i) {
        CHECK(jshc_embedded_init(&bad, models[0] + 1, i) == JSHC_EMBEDDED_FORMAT);
        CHECK(bad.m == 0 && bad.nodes == NULL);
    }
    CHECK(jshc_embedded_init(&bad, models[0] + 1, bytes[0] + 1) == JSHC_EMBEDDED_FORMAT);
    /* 损坏头部、非法 cell、Q16 超界。每次恢复原字节。 */
    {
        const size_t offsets[] = {0, 4, 8, 12, 40, 40 + 768 + 3};
        for (i = 0; i < sizeof(offsets) / sizeof(offsets[0]); ++i) {
            uint8_t *p = models[0] + 1 + offsets[i], saved = *p;
            *p = 255;
            CHECK(jshc_embedded_init(&bad, models[0] + 1, bytes[0]) == JSHC_EMBEDDED_FORMAT);
            *p = saved;
        }
    }
    CHECK(jshc_embedded_apply(chain, 4, NULL, 0) == JSHC_EMBEDDED_OK);
    CHECK(jshc_embedded_apply(NULL, 0, NULL, 0) == JSHC_EMBEDDED_OK);
    CHECK(jshc_embedded_apply(chain, 5, rgb, 1) == JSHC_EMBEDDED_ARGUMENT);
    CHECK(jshc_embedded_apply(NULL, 1, rgb, 1) == JSHC_EMBEDDED_ARGUMENT);
    CHECK(jshc_embedded_apply(chain, 4, NULL, 1) == JSHC_EMBEDDED_ARGUMENT);
    CHECK(jshc_embedded_apply(chain, 4, rgb, SIZE_MAX / 3 + 1) == JSHC_EMBEDDED_ARGUMENT);
    for (i = 0; i < sizeof(rgb); ++i) expected[i] = rgb[i];
    CHECK(jshc_embedded_apply(NULL, 0, rgb, sizeof(rgb) / 3) == JSHC_EMBEDDED_OK);
    for (i = 0; i < sizeof(rgb); ++i) CHECK(rgb[i] == expected[i]);
    chain[3] = &bad;
    CHECK(jshc_embedded_apply(chain, 4, rgb, 1) == JSHC_EMBEDDED_ARGUMENT);
    for (i = 0; i < sizeof(rgb); ++i) CHECK(rgb[i] == expected[i]);
    return 0;
}
