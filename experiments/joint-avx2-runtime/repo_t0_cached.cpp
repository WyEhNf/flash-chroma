// 当前热核的T0输入预取＋普通缓存写组合，仅用于本地独立筛查。
#include <immintrin.h>
#define _MM_HINT_NTA _MM_HINT_T0
#define _mm256_stream_si256(address, value) _mm256_store_si256((address), (value))
#define _mm_sfence() ((void)0)
#define avx2_chain_pair48_to avx2_chain_pair48_to_t0_cached
#include "../skylake-andn-normal-runtime/andn_outplace/channel_avx2.cpp"
