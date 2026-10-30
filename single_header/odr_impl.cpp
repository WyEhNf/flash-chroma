// 恰好一个翻译单元承载实现。
#define FLASH_CHROMA_IMPLEMENTATION
#include "flash_chroma.hpp"
unsigned fc_odr_backend_mask() { return fc::available_backends(); }
