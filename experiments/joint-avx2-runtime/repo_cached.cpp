// 复用当前仓库热核，只把非临时输出换成对齐普通写并移除对应sfence。
#include <immintrin.h>
#define _mm256_stream_si256(address, value) _mm256_store_si256((address), (value))
#define _mm_sfence() ((void)0)
#define avx2_chain_pair48_to avx2_chain_pair48_to_cached
#include "../skylake-andn-normal-runtime/andn_outplace/channel_avx2.cpp"
