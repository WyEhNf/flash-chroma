#include "memory_rom.h"
#include <algorithm>
#include <chrono>
#if defined(_OPENMP)
#include <omp.h>
#endif
#if defined(JSHC_MEM_AVX2)
namespace jshc_le16_10 {void avx2_chain_adaptive_linear_to(const uint8_t*,const uint32_t*,const uint8_t*,uint8_t*,size_t) noexcept;}
#endif
uint32_t jshc_mem_capabilities(void) {
  uint32_t result=1;
#if defined(JSHC_MEM_AVX2)
  if(__builtin_cpu_supports("avx2"))result|=2;
#endif
#if defined(_OPENMP)
  result|=4;
#endif
  return result;
}
int jshc_mem_apply_parallel(const jshc_mem_model* m,const uint8_t* src,uint8_t* dst,size_t pixels,int kernel,int threads) {
  if((kernel!=0 && kernel!=1) || threads<1 || threads>256 ||
     (kernel==1 && !(jshc_mem_capabilities()&2)) || jshc_mem_validate_io(m,src,dst,pixels))return 1;
  const size_t blocks=pixels/65536+(pixels%65536!=0);
  if(!blocks)return 0;
#if defined(JSHC_MEM_AVX2)
  using Fn=void(*)(const uint8_t*,const uint32_t*,const uint8_t*,uint8_t*,size_t) noexcept;
  Fn fn=nullptr;
  switch(m->log2_block) {
    case 10:fn=jshc_le16_10::avx2_chain_adaptive_linear_to;break;
    default:return 1;
  }
#endif
#if defined(_OPENMP)
  const int workers=omp_in_parallel()?1:static_cast<int>(std::min(blocks,size_t(threads)));
#pragma omp parallel for schedule(static) num_threads(workers)
#endif
  for(long long b=0;b<static_cast<long long>(blocks);++b) {
    const size_t start=size_t(b)*65536,n=std::min(size_t(65536),pixels-start);
#if defined(JSHC_MEM_AVX2)
    if(kernel==1) {
      fn(m->table,m->palette,src+3*start,dst+3*start,n);
    }
    else
#endif
      jshc_mem_apply(m,src+3*start,dst+3*start,n);
  }
  return 0;
}
int jshc_mem_bench(const jshc_mem_model* m,const uint8_t* src,uint8_t* dst,size_t pixels,int kernel,int threads,size_t repeats,double* times) {
  if(!times || repeats<1 || repeats>100 || jshc_mem_validate_io(m,src,dst,pixels))return 1;
  for(size_t r=0;r<repeats;++r) {
    const auto start=std::chrono::steady_clock::now();
    if(jshc_mem_apply_parallel(m,src,dst,pixels,kernel,threads))return 1;
    times[r]=std::chrono::duration<double>(std::chrono::steady_clock::now()-start).count();
  }
  return 0;
}
