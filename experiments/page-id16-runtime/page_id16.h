/* 固定4KiB页/LE16索引的借用ROM；此新API不兼容旧M16D Model。 */
#ifndef JSHC_PAGE_ID16_H
#define JSHC_PAGE_ID16_H
#include <stddef.h>
#include <stdint.h>
#if defined(P4_STATIC)
#define P4_API
#elif defined(_WIN32)
#define P4_API __declspec(dllexport)
#elif defined(__GNUC__) || defined(__clang__)
#define P4_API __attribute__((visibility("default")))
#else
#define P4_API
#endif
#ifdef __cplusplus
extern "C" {
#endif
typedef struct jshc_p4_model {
    const unsigned char *blob;
    size_t blob_bytes;
    const unsigned char *page_ids;
    const unsigned char *pool;
    const unsigned char *palette;
} jshc_p4_model;
P4_API size_t jshc_p4_model_size(void);
P4_API int jshc_p4_prepare(jshc_p4_model *model, const void *blob, size_t bytes);
P4_API int jshc_p4_apply(const jshc_p4_model *model, const unsigned char *source,
                       unsigned char *target, size_t pixels);
/* OMP/AVX2适配器另编译；纯C99不依赖这个可选入口。 */
P4_API int jshc_p4_apply_parallel(const jshc_p4_model *model,
                                const unsigned char *source,
                                unsigned char *target, size_t pixels,
                                int kernel, int threads);
#ifdef __cplusplus
}
#endif
#endif
