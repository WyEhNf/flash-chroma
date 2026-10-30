#pragma once
#include "channel_runtime.h"
#ifdef __cplusplus
extern "C" {
#endif
// 显式0..100个非连续紧密RGB8段；空批允许空数组，空段允许空指针。
// 非空目标必须互不重叠且与全部源不重叠；同址图像继续使用原单段入口。
// 输入/输出指针数组及长度数组在调用期间必须有效；原逐图/同址接口不变。
// 所有范围验证、任务构造和调度都在本入口内完成，失败验证不写任何图像。
JSHC_CC_API int jshc_cc_apply_to_segments(void* handle,const uint8_t* const* sources,
    uint8_t* const* destinations,const size_t* bytes,size_t count,int kernel,int threads,char* error,size_t error_bytes);
#ifdef __cplusplus
}
#endif
