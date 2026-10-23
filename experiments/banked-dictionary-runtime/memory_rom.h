#ifndef JSHC_BANKED_DICTIONARY_H
#define JSHC_BANKED_DICTIONARY_H
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
/* 独立M16B实验格式：四个连续bank，LE16局部ID，保留256合法palette。
   独立bases[4]缓存已验证pool base，model较旧格式增加16B；log2_block为4。 */
typedef struct jshc_mem_model {
  const uint8_t* blob;
  size_t blob_bytes;
  const uint8_t* table;
  uint32_t palette[256];
  uint32_t log2_block;
  uint32_t palette_size;
  uint32_t bases[4];
} jshc_mem_model;
/* ROM由调用者保持不可变；不需堆/浮点/主机小端/ROM对齐或外部padding。
   失败清零out；out与ROM重叠或地址范围非法时保持out。 */
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
