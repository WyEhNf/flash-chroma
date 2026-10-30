#ifndef JSHC_MEMORY_ROM_STORE_H
#define JSHC_MEMORY_ROM_STORE_H
#include "memory_rom.h"
#ifdef __cplusplus
extern "C" {
#endif
/* 与普通C99 apply合同相同；固定8像素ID先读，LE palette前7项写4字节、末项写3字节。 */
JSHC_MEM_API int jshc_mem_apply_store(const jshc_mem_model*,const uint8_t*,uint8_t*,size_t);
#ifdef __cplusplus
}
#endif
#endif
