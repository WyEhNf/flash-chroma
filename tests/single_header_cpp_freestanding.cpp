/* 只编译完整实现；检查目标裁剪后的对象不依赖堆、异常、RTTI或宿主库。
 * 默认embedded，可用 -DFLASH_CHROMA_TARGET=4 检查portable。
 */
#ifndef FLASH_CHROMA_TARGET
#define FLASH_CHROMA_TARGET FLASH_CHROMA_TARGET_EMBEDDED
#endif
#define FLASH_CHROMA_IMPLEMENTATION
#include "flash_chroma.hpp"
