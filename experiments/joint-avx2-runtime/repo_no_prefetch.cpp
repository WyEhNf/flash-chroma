// 复用当前仓库热核，只屏蔽软件预取并改名，便于同源A/B；不进入公共运行时。
#include <immintrin.h>
inline void p16_no_prefetch(const void*, _mm_hint) noexcept {}
#define _mm_prefetch(address, hint) p16_no_prefetch((address), (hint))
#define avx2_chain_pair48_to avx2_chain_pair48_to_no_prefetch
#include "../skylake-andn-normal-runtime/andn_outplace/channel_avx2.cpp"
