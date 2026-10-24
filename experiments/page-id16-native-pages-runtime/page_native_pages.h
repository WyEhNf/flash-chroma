/* 固定4096个调用者页指针；原ROM与旧Model ABI不变。 */
#ifndef JSHC_PAGE_NATIVE_PAGES_H
#define JSHC_PAGE_NATIVE_PAGES_H
#include "../page-id16-runtime/page_id16.h"
#ifdef __cplusplus
extern "C" {
#endif
typedef struct jshc_p4_pages_view {
    jshc_p4_model base;
    const unsigned char *const *pages;
} jshc_p4_pages_view;
P4_API size_t jshc_p4_pages_view_size(void);
P4_API size_t jshc_p4_pages_pointer_alignment(void);
P4_API size_t jshc_p4_pages_view_alignment(void);
P4_API size_t jshc_p4_pages_slots_bytes(void);
/* 失败保留view和全部槽；成功后ROM/页表由调用者保持不可变。 */
P4_API int jshc_p4_pages_prepare(jshc_p4_pages_view *view, const void *blob,
                                size_t bytes, const unsigned char **page_slots,
                                size_t page_count);
/* 只清零view；不释放或擦除ROM和调用者页表，不允许并发重置。 */
P4_API int jshc_p4_pages_clear(jshc_p4_pages_view *view);
P4_API int jshc_p4_pages_validate_io(const jshc_p4_pages_view *view,
                                   const unsigned char *source,
                                   unsigned char *target, size_t pixels);
P4_API int jshc_p4_pages_apply(const jshc_p4_pages_view *view,
                              const unsigned char *source,
                              unsigned char *target, size_t pixels);
/* 可选OMP适配器只有新C99核，不携带AVX分支。 */
P4_API int jshc_p4_pages_apply_parallel(const jshc_p4_pages_view *view,
                                      const unsigned char *source,
                                      unsigned char *target, size_t pixels,
                                      int threads);
#ifdef __cplusplus
}
#endif
#endif
