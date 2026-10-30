#ifndef JSHC_RGB3D7_H
#define JSHC_RGB3D7_H
#include <stddef.h>
#include <stdint.h>
#if defined(_WIN32)
#define JSHC_MEM_API __declspec(dllexport)
#elif defined(__GNUC__) || defined(__clang__)
#define JSHC_MEM_API __attribute__((visibility("default")))
#else
#define JSHC_MEM_API
#endif
#ifdef __cplusplus
extern "C" {
#endif
/* C7BK独立ABI：不可变ROM借用，不复制本地palette。 */
typedef struct jshc_mem_model {const uint8_t* blob;size_t blob_bytes;const uint8_t* table;const uint8_t* palettes;} jshc_mem_model;
/* 成功0；格式失败清零；out与ROM重叠/地址范围无效时无写拒绝。保持ROM存活且不可变。 */
JSHC_MEM_API int jshc_mem_prepare(jshc_mem_model*,const void*,size_t);
JSHC_MEM_API int jshc_mem_validate_io(const jshc_mem_model*,const uint8_t*,uint8_t*,size_t);
JSHC_MEM_API int jshc_mem_apply(const jshc_mem_model*,const uint8_t*,uint8_t*,size_t);
JSHC_MEM_API size_t jshc_mem_model_size(void);
JSHC_MEM_API uint32_t jshc_mem_capabilities(void);
JSHC_MEM_API int jshc_mem_apply_parallel(const jshc_mem_model*,const uint8_t*,uint8_t*,size_t,int,int);
#ifdef __cplusplus
}
#endif
#endif
