/* 两个执行核共用合同，只有C99实现导出定义；无host端序读写。 */
#ifndef JSHC_PAGE_ID16_INTERNAL_H
#define JSHC_PAGE_ID16_INTERNAL_H
#include "page_id16.h"
#include <limits.h>
#if CHAR_BIT != 8
#error P4_requires_8_bit_bytes
#endif
#define P4_PREFIX ((size_t)1056)
#define P4_MAP_BYTES ((size_t)8192)
#define P4_POOL_OFFSET ((size_t)9248)
#define P4_PAGE_BYTES ((size_t)4096)
#define P4_GUARD_BYTES ((size_t)4)
static uint32_t p4_le16(const unsigned char *p) {
    return (uint32_t)p[0] | ((uint32_t)p[1] << 8);
}
static uint32_t p4_le32(const unsigned char *p) {
    return (uint32_t)p[0] | ((uint32_t)p[1] << 8) |
           ((uint32_t)p[2] << 16) | ((uint32_t)p[3] << 24);
}
static const unsigned char *p4_rgb(const jshc_p4_model *m, uint32_t code) {
    uint32_t page = p4_le16(m->page_ids + 2 * (size_t)(code >> 12));
    unsigned char id = m->pool[(size_t)page * P4_PAGE_BYTES + (code & 4095u)];
    return m->palette + 4 * (size_t)id;
}
#ifdef __cplusplus
extern "C" {
#endif
int jshc_p4_validate_io(const jshc_p4_model *, const unsigned char *,
                        unsigned char *, size_t);
void jshc_p4_avx2_unchecked(const jshc_p4_model *, const unsigned char *,
                           unsigned char *, size_t);
#ifdef __cplusplus
}
#endif
#endif
