#ifndef JSHC_COLOR_DICTIONARY_H
#define JSHC_COLOR_DICTIONARY_H
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
/* 独立M16C格式：LE24 map指向64B RGB32块，无运行时palette依赖。
   新ABI仅三个地址/长度及两个32bit字段，Windows x64为32B。 */
typedef struct jshc_mem_model {
  const uint8_t* blob;
  size_t blob_bytes;
  const uint8_t* table;
  uint32_t log2_block;
  uint32_t palette_size;
} jshc_mem_model;
/* 不可变ROM借用，无堆/浮点/ROM对齐或外部padding要求；失败清零。
   out与ROM重叠或ROM地址范围非法时无写返回。 */
JSHC_MEM_API int jshc_mem_prepare(jshc_mem_model*,const void*,size_t);
JSHC_MEM_API int jshc_mem_validate_io(const jshc_mem_model*,const uint8_t*,uint8_t*,size_t);
JSHC_MEM_API int jshc_mem_apply(const jshc_mem_model*,const uint8_t*,uint8_t*,size_t);
JSHC_MEM_API size_t jshc_mem_model_size(void);
JSHC_MEM_API uint32_t jshc_mem_capabilities(void);
JSHC_MEM_API int jshc_mem_apply_parallel(const jshc_mem_model*,const uint8_t*,uint8_t*,size_t,int,int);
JSHC_MEM_API int jshc_mem_bench(const jshc_mem_model*,const uint8_t*,uint8_t*,size_t,int,int,size_t,double*);
#ifdef __cplusplus
}
#endif
#endif
