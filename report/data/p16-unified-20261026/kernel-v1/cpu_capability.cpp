#include "direct_avx512.h"
#include <cstdio>
int main(){std::printf("avx512_direct_supported=%d\n", int(jshc_channel::cpu_avx512_direct_supported()));}
