#pragma once
#include "channel_runtime.h"
#include "../p16-scanline-prepare-runtime/workload_hint.h"

/* 统一实验ABI仍为1，revision=102。capabilities新增bit3=AVX512。
   kernel：0=标量，1=AVX2，2=显式AVX512 direct；默认调用方继续选择1。
   AVX512要求CPU/OS通过检查且模型已有精确direct表，否则拒绝且不写图像。
   每级模型及侧表在create时冻结，不根据单张图像改变稀疏化参数。
   RGB8允许原地或完全分离；部分重叠拒绝。图像不需要padding或对齐。 */
#ifdef __cplusplus
extern "C" {
#endif
JSHC_CC_API int jshc_cc_apply_to(void* handle, const uint8_t* source,
    uint8_t* destination, size_t bytes, int kernel, int threads,
    char* error, size_t error_bytes);
#ifdef __cplusplus
}
#endif
