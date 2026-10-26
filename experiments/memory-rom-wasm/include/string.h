#ifndef P16_WASM_STRING_H
#define P16_WASM_STRING_H
#include <stddef.h>
/* freestanding探针仅声明本C99核心使用的两个标准函数，实现在minilib.c。 */
void *memset(void *, int, size_t);
int memcmp(const void *, const void *, size_t);
#endif
