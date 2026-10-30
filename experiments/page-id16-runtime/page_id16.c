/* 独立标准C99零堆核；执行状态和资格单列于阶段记录。 */
#include "page_id16_internal.h"
#include <string.h>
static int p4_range(const void *p, size_t bytes) {
    uintptr_t address = (uintptr_t)p;
    return bytes == 0 || (p != NULL && bytes <= UINTPTR_MAX - address);
}
static int p4_overlap(const void *a, size_t na, const void *b, size_t nb) {
    uintptr_t x = (uintptr_t)a, y = (uintptr_t)b;
    return na && nb && x < y + nb && y < x + na;
}
static int p4_header(const unsigned char *b, size_t bytes) {
    uint32_t pages, count;
    if (!p4_range(b, bytes) || bytes < P4_POOL_OFFSET + P4_PAGE_BYTES + P4_GUARD_BYTES)
        return 0;
    if (b[0] != 'P' || b[1] != '4' || b[2] != 'I' || b[3] != 'D' ||
        p4_le32(b + 4) != 1 || p4_le32(b + 8) != 12 ||
        p4_le32(b + 16) != UINT32_C(16777216) ||
        p4_le32(b + 24) || p4_le32(b + 28)) return 0;
    count = p4_le32(b + 12); pages = p4_le32(b + 20);
    if (!count || count > 256 || !pages || pages > 4096) return 0;
    return bytes == P4_POOL_OFFSET + (size_t)pages * P4_PAGE_BYTES + P4_GUARD_BYTES;
}
size_t jshc_p4_model_size(void) { return sizeof(jshc_p4_model); }
int jshc_p4_prepare(jshc_p4_model *m, const void *blob, size_t bytes) {
    const unsigned char *b = (const unsigned char *)blob;
    size_t i, pool_bytes;
    uint32_t count, pages;
    jshc_p4_model ready;
    if (!p4_range(m, sizeof(*m))) return 1;
    if (!p4_range(b, bytes)) { memset(m, 0, sizeof(*m)); return 1; }
    if (p4_overlap(m, sizeof(*m), b, bytes)) return 1;
    memset(m, 0, sizeof(*m));
    if (!p4_header(b, bytes)) return 1;
    count = p4_le32(b + 12); pages = p4_le32(b + 20);
    for (i = 0; i < 256; ++i) {
        uint32_t color = p4_le32(b + 32 + 4 * i);
        if (color > UINT32_C(16777215) || (i >= count && color)) return 1;
    }
    for (i = 0; i < 4096; ++i)
        if (p4_le16(b + P4_PREFIX + 2 * i) >= pages) return 1;
    pool_bytes = (size_t)pages * P4_PAGE_BYTES;
    for (i = 0; i < pool_bytes; ++i)
        if (b[P4_POOL_OFFSET + i] >= count) return 1;
    for (i = bytes - P4_GUARD_BYTES; i < bytes; ++i)
        if (b[i]) return 1;
    memset(&ready, 0, sizeof(ready));
    ready.blob = b; ready.blob_bytes = bytes;
    ready.page_ids = b + P4_PREFIX; ready.pool = b + P4_POOL_OFFSET;
    ready.palette = b + 32;
    memcpy(m, &ready, sizeof(ready));
    return 0;
}
int jshc_p4_validate_io(const jshc_p4_model *m, const unsigned char *source,
                        unsigned char *target, size_t pixels) {
    size_t bytes;
    if (!p4_range(m, sizeof(*m)) || !p4_header(m->blob, m->blob_bytes) ||
        m->page_ids != m->blob + P4_PREFIX || m->pool != m->blob + P4_POOL_OFFSET ||
        m->palette != m->blob + 32 || pixels > SIZE_MAX / 3) return 1;
    bytes = pixels * 3;
    if (!p4_range(source, bytes) || !p4_range(target, bytes) ||
        (source != target && p4_overlap(source, bytes, target, bytes)) ||
        p4_overlap(source, bytes, m, sizeof(*m)) ||
        p4_overlap(target, bytes, m, sizeof(*m)) ||
        p4_overlap(source, bytes, m->blob, m->blob_bytes) ||
        p4_overlap(target, bytes, m->blob, m->blob_bytes)) return 1;
    return 0;
}
int jshc_p4_apply(const jshc_p4_model *m, const unsigned char *source,
                  unsigned char *target, size_t pixels) {
    size_t i = 0, lane;
    if (jshc_p4_validate_io(m, source, target, pixels)) return 1;
    while (pixels - i >= 8) {
        uint32_t codes[8];
        unsigned char colors[8][4];
        /* 先读完整组输入，保证完全同址且4B重叠写也不污染下一lane。 */
        for (lane = 0; lane < 8; ++lane) {
            const unsigned char *s = source + 3 * (i + lane);
            codes[lane] = (uint32_t)s[0] | ((uint32_t)s[1] << 8) | ((uint32_t)s[2] << 16);
        }
        for (lane = 0; lane < 8; ++lane) {
            const unsigned char *color = p4_rgb(m, codes[lane]);
            colors[lane][0] = color[0]; colors[lane][1] = color[1];
            colors[lane][2] = color[2]; colors[lane][3] = 0;
        }
        for (lane = 0; lane < 7; ++lane) memcpy(target + 3 * (i + lane), colors[lane], 4);
        memcpy(target + 3 * (i + 7), colors[7], 3);
        i += 8;
    }
    for (; i < pixels; ++i) {
        const unsigned char *s = source + 3 * i;
        uint32_t code = (uint32_t)s[0] | ((uint32_t)s[1] << 8) | ((uint32_t)s[2] << 16);
        const unsigned char *color = p4_rgb(m, code);
        target[3 * i] = color[0]; target[3 * i + 1] = color[1]; target[3 * i + 2] = color[2];
    }
    return 0;
}
