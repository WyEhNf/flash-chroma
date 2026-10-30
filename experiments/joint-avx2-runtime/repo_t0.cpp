// 复用当前仓库热核，只把NTA输入预取替换为T0并改名。
#include <immintrin.h>
#define _MM_HINT_NTA _MM_HINT_T0
#define avx2_chain_pair48_to avx2_chain_pair48_to_t0
#include "../skylake-andn-normal-runtime/andn_outplace/channel_avx2.cpp"
