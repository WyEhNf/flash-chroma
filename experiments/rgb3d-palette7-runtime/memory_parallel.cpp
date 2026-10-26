#include "memory_rom.h"
#include <algorithm>
#if defined(_OPENMP)
#include <omp.h>
#endif
namespace jshc_rgb3d7 {void avx2_chain_adaptive_linear_to(const uint8_t*,const uint8_t*,const uint8_t*,uint8_t*,size_t) noexcept;}
uint32_t jshc_mem_capabilities(void) {
  uint32_t result=1;
  if(__builtin_cpu_supports("avx2"))result|=2;
#if defined(_OPENMP)
  result|=4;
#endif
  return result;
}
int jshc_mem_apply_parallel(const jshc_mem_model* m,const uint8_t* src,uint8_t* dst,size_t pixels,int kernel,int threads) {
  if((kernel!=0 && kernel!=1) || threads<1 || threads>256 || (kernel && !(jshc_mem_capabilities()&2)) || jshc_mem_validate_io(m,src,dst,pixels))return 1;
  const size_t blocks=pixels/65536+(pixels%65536!=0);
  if(!blocks)return 0;
#if defined(_OPENMP)
  const int workers=omp_in_parallel()?1:static_cast<int>(std::min(blocks,size_t(threads)));
#pragma omp parallel for schedule(static) num_threads(workers)
#endif
  for(long long b=0;b<static_cast<long long>(blocks);++b) {
    const size_t start=size_t(b)*65536,n=std::min(size_t(65536),pixels-start);
    if(kernel)jshc_rgb3d7::avx2_chain_adaptive_linear_to(m->table,m->palettes,src+3*start,dst+3*start,n);
    else jshc_mem_apply(m,src+3*start,dst+3*start,n);
  }
  return 0;
}
