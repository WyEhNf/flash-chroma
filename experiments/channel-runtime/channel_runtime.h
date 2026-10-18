#pragma once
#include <stddef.h>
#include <stdint.h>

#if defined(_WIN32)
#define JSHC_CC_API __declspec(dllexport)
#else
#define JSHC_CC_API __attribute__((visibility("default")))
#endif

#ifdef __cplusplus
extern "C" {
#endif
/* 独立实验ABI，不修改SLUT v1。每级可附一个小端u32[3][3][256]侧表。 */
JSHC_CC_API uint32_t jshc_cc_abi_version(void);
JSHC_CC_API uint32_t jshc_cc_revision(void);
/* bit0=标量，bit1=编入且CPU/OS支持AVX2，bit2=OpenMP。 */
JSHC_CC_API uint32_t jshc_cc_capabilities(void);
JSHC_CC_API int jshc_cc_create(const char* const* models, const char* const* fractions,
    size_t stages, void** output, char* error, size_t error_bytes);
JSHC_CC_API void jshc_cc_destroy(void* handle);
JSHC_CC_API size_t jshc_cc_model_bytes(const void* handle);
/* kernel=0标量、1 AVX2。紧密RGB8原地映射，bytes必须是3的倍数。 */
JSHC_CC_API int jshc_cc_apply(void* handle, uint8_t* rgb, size_t bytes,
    int kernel, int threads, char* error, size_t error_bytes);
/* 预加载整组图片合并为连续RGB8；每轮先复制源，再映射。计时不含hash/JIT/IO。 */
JSHC_CC_API int jshc_cc_bench(void* handle, const uint8_t* source, uint8_t* work,
    size_t bytes, int kernel, int threads, size_t repeats, double* apply_seconds,
    double* copy_apply_seconds, char* error, size_t error_bytes);
#ifdef __cplusplus
}
#endif
