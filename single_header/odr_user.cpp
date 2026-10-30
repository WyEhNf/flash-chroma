// 第二个翻译单元只包含声明，核验链接与对象布局契约。
#include "flash_chroma.hpp"
unsigned fc_odr_backend_mask();
int main() { fc::Runtime runtime; return runtime.ready() || !(fc_odr_backend_mask() & 1u); }
