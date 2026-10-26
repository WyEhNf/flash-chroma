#ifndef P16_STORE_WASM_STRING_H
#define P16_STORE_WASM_STRING_H
#include <stddef.h>
/* 本独立夹具补全新存储核所需的标准C99函数声明。 */
void *memset(void *, int, size_t);
int memcmp(const void *, const void *, size_t);
void *memcpy(void *restrict, const void *restrict, size_t);
#endif
