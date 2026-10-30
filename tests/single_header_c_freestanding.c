/* 用 -ffreestanding -fno-builtin 编译后检查无外部未定义符号。
 * 本翻译单元只提供运行库，不包含测试夹具或宿主 stdio。
 */
#define FC_C_IMPLEMENTATION
#include "flash_chroma_c.h"
