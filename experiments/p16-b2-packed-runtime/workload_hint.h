#pragma once
#include "channel_runtime.h"

#ifdef __cplusplus
extern "C" {
#endif
/* 预计句柄整个生存期会映射的像素数；不按提示读取图像或分配同等大小缓冲区。
   0..UINT64_MAX均合法，仅共享首级资格受固定阈值门控；默认create相当于0。 */
JSHC_CC_API int jshc_cc_create_for_workload(const char* const* models,
    const char* const* fractions, size_t stages, uint64_t expected_pixels,
    void** output, char* error, size_t error_bytes);
JSHC_CC_API uint64_t jshc_cc_workload_threshold(void);
#ifdef __cplusplus
}
#endif
