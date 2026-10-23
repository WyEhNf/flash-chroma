#ifndef JSHC_TAGGED_BLOCK16_H
#define JSHC_TAGGED_BLOCK16_H
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
/* M16T：LE32条目bit31为直接RGB24，否则为16B ID块偏移；不可变ROM借用。 */
typedef struct jshc_mem_model {
  const uint8_t* blob;
  size_t blob_bytes;
  const uint8_t* table;
  uint32_t palette[256];
  uint32_t log2_block;
  uint32_t palette_size;
} jshc_mem_model;
/* 成功0；失败清零，out/ROM重叠无写拒绝。无堆/浮点/对齐/padding或端序要求。
   使用成功且未改写的model，调用者保持ROM存活与不可变。 */
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
