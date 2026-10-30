/* 独立纯C99准备视图；不分配堆、不改变旧核或序列化格式。 */
#include "page_native_pages.h"
#include "../page-id16-runtime/page_id16_internal.h"
#include <string.h>

struct p4_pages_pointer_probe { char byte; const unsigned char *value; };
struct p4_pages_view_probe { char byte; jshc_p4_pages_view value; };
static int p4_pages_range(const void *p, size_t bytes) {
    uintptr_t address = (uintptr_t)p;
    return bytes == 0 || (p != NULL && bytes <= UINTPTR_MAX - address);
}
static int p4_pages_overlap(const void *a, size_t na, const void *b, size_t nb) {
    uintptr_t x = (uintptr_t)a, y = (uintptr_t)b;
    return na && nb && x < y + nb && y < x + na;
}
static int p4_pages_aligned(const void *p, size_t alignment) {
    return alignment != 0 && (uintptr_t)p % alignment == 0;
}
size_t jshc_p4_pages_view_size(void) { return sizeof(jshc_p4_pages_view); }
size_t jshc_p4_pages_pointer_alignment(void) {
    return offsetof(struct p4_pages_pointer_probe, value);
}
size_t jshc_p4_pages_view_alignment(void) {
    return offsetof(struct p4_pages_view_probe, value);
}
size_t jshc_p4_pages_slots_bytes(void) {
    return sizeof(const unsigned char *) <= SIZE_MAX / 4096
        ? (size_t)4096 * sizeof(const unsigned char *) : 0;
}
int jshc_p4_pages_prepare(jshc_p4_pages_view *view, const void *blob,
                          size_t bytes, const unsigned char **page_slots,
                          size_t page_count) {
    jshc_p4_model parsed;
    jshc_p4_pages_view ready;
    size_t i, slot_bytes = jshc_p4_pages_slots_bytes();
    if (page_count != 4096 || !slot_bytes ||
        !p4_pages_range(view, sizeof(*view)) ||
        !p4_pages_aligned(view, jshc_p4_pages_view_alignment()) ||
        !p4_pages_range(page_slots, slot_bytes) ||
        !p4_pages_aligned(page_slots, jshc_p4_pages_pointer_alignment()) ||
        !p4_pages_range(blob, bytes) ||
        p4_pages_overlap(view, sizeof(*view), page_slots, slot_bytes) ||
        p4_pages_overlap(view, sizeof(*view), blob, bytes) ||
        p4_pages_overlap(page_slots, slot_bytes, blob, bytes)) return 1;
    /* 所有可返回失败的验证先行；旧prepare只写局部对象。 */
    if (jshc_p4_prepare(&parsed, blob, bytes)) return 1;
    for (i = 0; i < 4096; ++i)
        page_slots[i] = parsed.pool + ((size_t)p4_le16(parsed.page_ids + 2 * i) << 12);
    memset(&ready, 0, sizeof(ready));
    ready.base = parsed;
    ready.pages = page_slots;
    memcpy(view, &ready, sizeof(ready));
    return 0;
}
int jshc_p4_pages_clear(jshc_p4_pages_view *view) {
    if (!p4_pages_range(view, sizeof(*view)) ||
        !p4_pages_aligned(view, jshc_p4_pages_view_alignment())) return 1;
    memset(view, 0, sizeof(*view));
    return 0;
}
int jshc_p4_pages_validate_io(const jshc_p4_pages_view *view,
                             const unsigned char *source,
                             unsigned char *target, size_t pixels) {
    size_t bytes, slot_bytes = jshc_p4_pages_slots_bytes();
    if (!slot_bytes || !p4_pages_range(view, sizeof(*view)) ||
        !p4_pages_aligned(view, jshc_p4_pages_view_alignment()) ||
        jshc_p4_validate_io(&view->base, source, target, pixels)) return 1;
    bytes = pixels * 3;
    if (!p4_pages_range(view->pages, slot_bytes) ||
        !p4_pages_aligned(view->pages, jshc_p4_pages_pointer_alignment()) ||
        p4_pages_overlap(view->pages, slot_bytes, view, sizeof(*view)) ||
        p4_pages_overlap(view->pages, slot_bytes, view->base.blob, view->base.blob_bytes) ||
        p4_pages_overlap(source, bytes, view, sizeof(*view)) ||
        p4_pages_overlap(target, bytes, view, sizeof(*view)) ||
        p4_pages_overlap(source, bytes, view->pages, slot_bytes) ||
        p4_pages_overlap(target, bytes, view->pages, slot_bytes)) return 1;
    return 0;
}
static const unsigned char *p4_pages_rgb(const jshc_p4_pages_view *view,
                                        uint32_t code) {
    const unsigned char *page = view->pages[code >> 12];
    unsigned char id = page[code & 4095u];
    return view->base.palette + 4 * (size_t)id;
}
int jshc_p4_pages_apply(const jshc_p4_pages_view *view,
                        const unsigned char *source,
                        unsigned char *target, size_t pixels) {
    size_t i = 0, lane;
    if (jshc_p4_pages_validate_io(view, source, target, pixels)) return 1;
    while (pixels - i >= 8) {
        uint32_t codes[8];
        unsigned char colors[8][4];
        /* 先读完整组；前7次4B写只覆盖组内下一像素。 */
        for (lane = 0; lane < 8; ++lane) {
            const unsigned char *s = source + 3 * (i + lane);
            codes[lane] = (uint32_t)s[0] | ((uint32_t)s[1] << 8) |
                          ((uint32_t)s[2] << 16);
        }
        for (lane = 0; lane < 8; ++lane) {
            const unsigned char *color = p4_pages_rgb(view, codes[lane]);
            memcpy(colors[lane], color, 4);
        }
        for (lane = 0; lane < 7; ++lane)
            memcpy(target + 3 * (i + lane), colors[lane], 4);
        memcpy(target + 3 * (i + 7), colors[7], 3);
        i += 8;
    }
    for (; i < pixels; ++i) {
        const unsigned char *s = source + 3 * i;
        uint32_t code = (uint32_t)s[0] | ((uint32_t)s[1] << 8) |
                        ((uint32_t)s[2] << 16);
        const unsigned char *color = p4_pages_rgb(view, code);
        target[3 * i] = color[0]; target[3 * i + 1] = color[1];
        target[3 * i + 2] = color[2];
    }
    return 0;
}
