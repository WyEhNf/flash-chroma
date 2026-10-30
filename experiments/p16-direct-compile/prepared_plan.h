#pragma once
#include "channel_runtime.h"
#ifdef __cplusplus
extern "C" {
#endif
typedef struct jshc_cc_plan_info {
    uint32_t version;
    uint32_t reserved;
    uint64_t generation;
    uint64_t owners;
} jshc_cc_plan_info;
// 查询/获取期间调用者必须持有存活owner；每次成功acquire须匹配一次destroy。
// 返回同一不可变准备对象；各owner可并发处理互不重叠图像，禁止最后destroy后继续使用。
// generation只标识库实例内的一次snapshot，不是文件SHA；文件变化需显式重新create。
JSHC_CC_API int jshc_cc_get_plan_info(const void* handle,jshc_cc_plan_info* output,size_t bytes);
JSHC_CC_API int jshc_cc_acquire_plan(void* handle,uint64_t expected_generation,void** output,char* error,size_t error_bytes);
#ifdef __cplusplus
}
#endif
