#ifndef JSHC_MEMORY_ROM_ILP_H
#define JSHC_MEMORY_ROM_ILP_H
#include "memory_rom.h"
#ifdef __cplusplus
extern "C" {
#endif
/* 与普通C99 apply合同相同；固定8像素批先读全部ID，再取值、批写。 */
JSHC_MEM_API int jshc_mem_apply_ilp(const jshc_mem_model*,const uint8_t*,uint8_t*,size_t);
#ifdef __cplusplus
}
#endif
#endif
