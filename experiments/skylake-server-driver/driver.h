#pragma once
#include <stddef.h>
#include <stdint.h>
#define JSHC_SB_API __attribute__((visibility("default")))
#ifdef __cplusplus
extern "C" {
#endif

typedef int (*jshc_sb_apply_fn)(void*, uint8_t*, size_t, int, int, char*, size_t);
JSHC_SB_API uint32_t jshc_sb_abi_version(void);
// mode=0整批调用，mode=1逐图调用；两个时间数组长度为repeats*(mode?images:1)，wall为repeats。
// 源、工作区和三个时间数组必须分离；每轮从原始源重新复制，创建/校验不计入计时。
JSHC_SB_API int jshc_sb_run(jshc_sb_apply_fn apply, void* handle,
    const uint8_t* source, uint8_t* work, size_t image_bytes, size_t images,
    int kernel, int threads, int mode, size_t repeats,
    double* apply_seconds, double* copy_apply_seconds, double* round_wall_seconds,
    char* error, size_t error_capacity);
// 使用与后端同一个OpenMP运行库核验实际团队与CPU；不推断CPU型号或修改系统设置。
JSHC_SB_API int jshc_sb_probe_team(int requested, int* cpus, size_t capacity,
    int* actual, char* error, size_t error_capacity);
#ifdef __cplusplus
}
#endif
