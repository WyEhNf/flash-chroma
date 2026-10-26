#ifndef JSHC_LE16_BLOCK1024_H
#define JSHC_LE16_BLOCK1024_H
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
/* M10L v1固定1024B块与LE16局部ID；不可变借用，不改变SLUT或旧M16D。 */
typedef struct jshc_mem_model {
  const uint8_t* blob;
  size_t blob_bytes;
  const uint8_t* table;
  uint32_t palette[256];
  uint32_t log2_block;
  uint32_t palette_size;
} jshc_mem_model;
/* 0成功；1参数/格式/范围错误。失败清零目标，ROM与目标重叠则保留目标。
   无需堆、浮点、对齐或主机小端；映射接口要求使用成功prepare且未改写的model。 */
JSHC_MEM_API int jshc_mem_prepare(jshc_mem_model*, const void*, size_t);
JSHC_MEM_API int jshc_mem_validate_io(const jshc_mem_model*, const uint8_t*, uint8_t*, size_t);
JSHC_MEM_API int jshc_mem_apply(const jshc_mem_model*, const uint8_t*, uint8_t*, size_t);
JSHC_MEM_API size_t jshc_mem_model_size(void);
/* 可选桌面适配器：kernel=0 C99，1 AVX2；均使用同一ROM。 */
JSHC_MEM_API uint32_t jshc_mem_capabilities(void);
JSHC_MEM_API int jshc_mem_apply_parallel(const jshc_mem_model*,const uint8_t*,uint8_t*,size_t,int,int);
JSHC_MEM_API int jshc_mem_bench(const jshc_mem_model*,const uint8_t*,uint8_t*,size_t,int,int,size_t,double*);
#ifdef __cplusplus
}
#endif
#endif
