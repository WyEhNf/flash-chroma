#pragma once
#include "channel_runtime.h"
#ifdef __cplusplus
extern "C" {
#endif
// 研究ABI：0保留87完整直接表准备，1只准备精确后缀；调用者显式承担稳态取舍。
// 原jshc_cc_create等价于policy=0，不根据输入图片内容或运行历史自动切换。
JSHC_CC_API int jshc_cc_create_policy(const char* const* paths,const char* const* sidecars,
    size_t stages,uint32_t policy,void** output,char* error,size_t error_bytes);
#ifdef __cplusplus
}
#endif
