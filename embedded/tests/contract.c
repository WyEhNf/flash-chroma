/* 宿主与 FreeRTOS 共用的确定性契约测试；不需要堆、文件或外部数据。 */
#include "jshc_embedded.h"
#ifdef JSHC_EMBEDDED_SINGLE_HEADER_PARITY
#include "flash_chroma_c.h"
static fc_model single_models[4];
static fc_chain single_chain;
static uint8_t single_rgb[3 * 257 + 2];
/* 仅为合同制造非对齐分输出侧表；生产模型可位于只读ROM。 */
static uint8_t single_sidecars[4][FC_C_SIDECAR_BYTES + 1];
#endif
#ifdef JSHC_EMBEDDED_PORTABLE_PARITY
#include "jshc_portable.h"
static jshc_p_model portable_models[4];
static jshc_p_chain portable_chains[2];
static uint8_t portable_rgb[2][3 * 257 + 2];
#endif

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

#ifdef JSHC_EMBEDDED_SINGLE_HEADER_PARITY
/* 分输出独立参考：按轴排名选择顶点，逐通道u64累加后同时更新RGB。
 * 只读取旧嵌入式视图和原始侧表，不调用新运行库的私有字段或排序函数。
 */
static void single_oracle(const jshc_embedded_lut *lut, const uint8_t *sidecar, uint8_t *rgb)
{
    const size_t stride[3] = {(size_t)lut->m * lut->m, lut->m, 1};
    size_t base = 0;
    uint8_t next[3];
    unsigned c, a, b;
    for (a = 0; a < 3; ++a) base += lut->idx[a * 256 + rgb[a]] * stride[a];
    for (c = 0; c < 3; ++c) {
        const uint8_t *fractions = sidecar ? sidecar + c * 3072 : lut->frac;
        uint32_t f[3], weights[4];
        unsigned order[3];
        size_t vertex[4];
        uint64_t sum = 32768;
        for (a = 0; a < 3; ++a) f[a] = read32(fractions + 4 * (a * 256 + rgb[a]));
        for (a = 0; a < 3; ++a) {
            unsigned rank = 0;
            for (b = 0; b < 3; ++b)
                if (f[b] > f[a] || (f[b] == f[a] && b < a)) ++rank;
            order[rank] = a;
        }
        vertex[0] = base;
        for (a = 0; a < 3; ++a) vertex[a + 1] = vertex[a] + stride[order[a]];
        weights[0] = 65536 - f[order[0]];
        weights[1] = f[order[0]] - f[order[1]];
        weights[2] = f[order[1]] - f[order[2]];
        weights[3] = f[order[2]];
        for (a = 0; a < 4; ++a) sum += (uint64_t)weights[a] * lut->nodes[3 * vertex[a] + c];
        next[c] = (uint8_t)(sum / 65536);
    }
    for (c = 0; c < 3; ++c) rgb[c] = next[c];
}
#endif

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
#ifdef JSHC_EMBEDDED_SINGLE_HEADER_PARITY
    {
        const fc_model *views[4];
        const fc_bytes absent = {NULL, 0};
        for (s = 0; s < 4; ++s) {
            const fc_bytes blob = {models[s] + 1, bytes[s]};
            CHECK(fc_model_init(&single_models[s], blob, absent) == FC_OK);
            views[s] = &single_models[s];
        }
        CHECK(fc_chain_init(&single_chain, views) == FC_OK);
    }
#endif
#ifdef JSHC_EMBEDDED_PORTABLE_PARITY
    {
        const jshc_p_model *views[4];
        for (s = 0; s < 4; ++s) {
            CHECK(jshc_p_model_prepare(&portable_models[s], models[s] + 1, bytes[s]) == JSHC_P_OK);
            views[s] = &portable_models[s];
        }
        CHECK(jshc_p_chain_prepare(&portable_chains[0], views, 0) == JSHC_P_OK);
        CHECK(jshc_p_chain_prepare(&portable_chains[1], views, JSHC_P_FORCE_GENERIC) == JSHC_P_OK);
    }
#endif
    for (len = 0; len <= 257; ++len) {
        for (i = 0; i < sizeof(rgb); ++i) {
            seed = seed * 1664525u + 1013904223u;
            expected[i] = rgb[i] = (uint8_t)(seed >> 24);
#ifdef JSHC_EMBEDDED_SINGLE_HEADER_PARITY
            single_rgb[i] = rgb[i];
#endif
#ifdef JSHC_EMBEDDED_PORTABLE_PARITY
            portable_rgb[0][i] = portable_rgb[1][i] = rgb[i];
#endif
        }
        for (i = 0; i < len; ++i)
            for (s = 0; s < 4; ++s) oracle(chain[s], expected + 1 + i * 3);
        CHECK(jshc_embedded_apply(chain, 4, rgb + 1, len) == JSHC_EMBEDDED_OK);
        for (i = 0; i < sizeof(rgb); ++i) CHECK(rgb[i] == expected[i]);
#ifdef JSHC_EMBEDDED_SINGLE_HEADER_PARITY
        CHECK(fc_apply_rgb8(&single_chain, single_rgb + 1, sizeof(rgb) - 2, len * 3,
            single_rgb + 1, sizeof(rgb) - 2, len * 3, len, 1) == FC_OK);
        for (i = 0; i < sizeof(rgb); ++i) CHECK(single_rgb[i] == expected[i]);
#endif
#ifdef JSHC_EMBEDDED_PORTABLE_PARITY
        for (s = 0; s < 2; ++s) {
            CHECK(jshc_p_apply_rgb8(&portable_chains[s],
                portable_rgb[s] + 1, sizeof(rgb) - 2, len * 3,
                portable_rgb[s] + 1, sizeof(rgb) - 2, len * 3, len, 1) == JSHC_P_OK);
            for (i = 0; i < sizeof(rgb); ++i) CHECK(portable_rgb[s][i] == expected[i]);
        }
#endif
        if (checkpoint && len % 32 == 0) checkpoint();
    }
#ifdef JSHC_EMBEDDED_SINGLE_HEADER_PARITY
    /* 首级侧表和四级侧表分别验收；覆盖端点、半值、通道不同次序及非对齐。 */
    {
        const uint32_t fractions[7] = {0, 1, 32767, 32768, 32769, 65535, 65536};
        const fc_model *views[4];
        size_t mode, c, a, x;
        for (s = 0; s < 4; ++s)
            for (c = 0; c < 3; ++c) for (a = 0; a < 3; ++a) for (x = 0; x < 256; ++x)
                write32(single_sidecars[s] + 1 + 4 * ((c * 3 + a) * 256 + x), fractions[(x + a + c + s) % 7]);
        for (mode = 0; mode < 2; ++mode) {
            for (s = 0; s < 4; ++s) {
                const fc_bytes blob = {models[s] + 1, bytes[s]};
                const fc_bytes side = {(mode || !s) ? single_sidecars[s] + 1 : NULL,
                    (mode || !s) ? FC_C_SIDECAR_BYTES : 0};
                CHECK(fc_model_init(&single_models[s], blob, side) == FC_OK);
                views[s] = &single_models[s];
            }
            CHECK(fc_chain_init(&single_chain, views) == FC_OK);
            for (len = 0; len <= 257; ++len) {
                for (i = 0; i < sizeof(rgb); ++i) {
                    seed = seed * 1664525u + 1013904223u;
                    expected[i] = single_rgb[i] = (uint8_t)(seed >> 24);
                }
                for (i = 0; i < len; ++i)
                    for (s = 0; s < 4; ++s)
                        single_oracle(chain[s], (mode || !s) ? single_sidecars[s] + 1 : NULL, expected + 1 + 3 * i);
                CHECK(fc_apply_rgb8(&single_chain, single_rgb + 1, sizeof(rgb) - 2, len * 3,
                    single_rgb + 1, sizeof(rgb) - 2, len * 3, len, 1) == FC_OK);
                for (i = 0; i < sizeof(rgb); ++i) CHECK(single_rgb[i] == expected[i]);
                if (checkpoint && len % 32 == 0) checkpoint();
            }
        }
        {
            fc_model bad_model;
            const fc_bytes blob = {models[0] + 1, bytes[0]};
            const fc_bytes absent = {NULL, 0};
            const fc_bytes side = {single_sidecars[0] + 1, FC_C_SIDECAR_BYTES};
            const uint32_t saved_grid = read32(models[0] + 1 + 16);
            const uint32_t saved_fraction = read32(single_sidecars[0] + 1);
            write32(models[0] + 1 + 16, UINT32_C(0x7fc00000));
            CHECK(fc_model_init(&bad_model, blob, absent) == FC_FORMAT);
            write32(models[0] + 1 + 16, saved_grid);
            write32(single_sidecars[0] + 1, 65537);
            CHECK(fc_model_init(&bad_model, blob, side) == FC_RANGE);
            write32(single_sidecars[0] + 1, saved_fraction);
        }
        for (i = 0; i < sizeof(rgb); ++i) expected[i] = single_rgb[i];
        CHECK(fc_apply_rgb8(&single_chain, single_rgb, sizeof(single_rgb), 3,
            single_rgb + 1, sizeof(single_rgb) - 1, 3, 1, 1) == FC_OVERLAP);
        for (i = 0; i < sizeof(rgb); ++i) CHECK(single_rgb[i] == expected[i]);
    }
#endif
#ifdef JSHC_EMBEDDED_PORTABLE_PARITY
    /* 随机夹具通常只走通用路径；另用曲线和常量夹具确实触发结构捷径。 */
    {
        const jshc_p_model *views[4];
        size_t pattern, mode, c;
        for (pattern = 0; pattern < 2; ++pattern) {
            for (s = 0; s < 4; ++s) {
                const size_t m = sizes[s];
                uint8_t *nodes = models[s] + 1 + 16 + 12 * m + 3840;
                for (i = 0; i < m * m * m; ++i) {
                    const size_t coordinate[3] = {i / (m * m), (i / m) % m, i % m};
                    for (c = 0; c < 3; ++c)
                        nodes[i * 3 + c] = pattern ? (uint8_t)(17 + s * 31 + c)
                            : (uint8_t)((coordinate[c] * (37 + 2 * s) + s * 13 + c * 5) % 256);
                }
                CHECK(jshc_p_model_prepare(&portable_models[s], models[s] + 1, bytes[s]) == JSHC_P_OK);
                views[s] = &portable_models[s];
            }
            CHECK(jshc_p_chain_prepare(&portable_chains[0], views, 0) == JSHC_P_OK);
            CHECK(jshc_p_chain_prepare(&portable_chains[1], views, JSHC_P_FORCE_GENERIC) == JSHC_P_OK);
            CHECK(portable_chains[0].path[0] == (pattern ? JSHC_P_CONSTANT : JSHC_P_CURVE));
            for (i = 0; i < sizeof(rgb); ++i) {
                seed = seed * 1664525u + 1013904223u;
                expected[i] = rgb[i] = portable_rgb[0][i] = portable_rgb[1][i] = (uint8_t)(seed >> 24);
            }
            for (i = 0; i < 257; ++i)
                for (s = 0; s < 4; ++s) oracle(chain[s], expected + 1 + i * 3);
            CHECK(jshc_embedded_apply(chain, 4, rgb + 1, 257) == JSHC_EMBEDDED_OK);
            for (i = 0; i < sizeof(rgb); ++i) CHECK(rgb[i] == expected[i]);
            for (mode = 0; mode < 2; ++mode) {
                CHECK(jshc_p_apply_rgb8(&portable_chains[mode],
                    portable_rgb[mode] + 1, sizeof(rgb) - 2, 257 * 3,
                    portable_rgb[mode] + 1, sizeof(rgb) - 2, 257 * 3, 257, 1) == JSHC_P_OK);
                for (i = 0; i < sizeof(rgb); ++i) CHECK(portable_rgb[mode][i] == expected[i]);
            }
            if (checkpoint) checkpoint();
        }
    }
#endif
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
