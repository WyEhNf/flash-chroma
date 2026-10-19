#include "driver.h"
#include "../channel-runtime/channel_runtime.h"
#include <chrono>
#include <cstdio>
#include <cstring>
#include <limits>
#include <type_traits>
#include <omp.h>
#include <sched.h>

namespace {
static_assert(std::is_same<jshc_sb_apply_fn,decltype(&jshc_cc_apply)>::value,"回调类型必须与现有公开ABI完全一致");
using Clock=std::chrono::steady_clock;
static_assert(Clock::is_steady,"需要单调时钟");
int fail(char* error,size_t capacity,const char* text) {
  if(error && capacity)std::snprintf(error,capacity,"%s",text);
  return 1;
}
bool product(size_t a,size_t b,size_t& result) {
  if(b && a>std::numeric_limits<size_t>::max()/b)return false;
  result=a*b;return true;
}
struct Range { uintptr_t start,end; };
bool range(const void* p,size_t bytes,Range& result) {
  const auto start=reinterpret_cast<uintptr_t>(p);
  if(!p || bytes>std::numeric_limits<uintptr_t>::max()-start)return false;
  result={start,start+bytes};return true;
}
double elapsed(Clock::time_point a,Clock::time_point b) {
  return std::chrono::duration<double>(b-a).count();
}
}

uint32_t jshc_sb_abi_version(void) {return 1;}
int jshc_sb_run(jshc_sb_apply_fn apply,void* handle,
    const uint8_t* source,uint8_t* work,size_t image_bytes,size_t images,
    int kernel,int threads,int mode,size_t repeats,
    double* apply_seconds,double* copy_apply_seconds,double* round_wall_seconds,
    char* error,size_t error_capacity) {
  if(!apply || !handle || !image_bytes || image_bytes%3 || !images || !repeats ||
      (kernel!=0 && kernel!=1) || threads<1 || (mode!=0 && mode!=1))
    return fail(error,error_capacity,"基准参数无效");
  size_t total=0,samples=0,timing_bytes=0,wall_bytes=0;
  const size_t segments=mode?images:1;
  if(!product(image_bytes,images,total) || !product(segments,repeats,samples) ||
      !product(samples,sizeof(double),timing_bytes) || !product(repeats,sizeof(double),wall_bytes))
    return fail(error,error_capacity,"基准长度溢出");
  Range ranges[5];
  if(!range(source,total,ranges[0]) || !range(work,total,ranges[1]) ||
      !range(apply_seconds,timing_bytes,ranges[2]) || !range(copy_apply_seconds,timing_bytes,ranges[3]) ||
      !range(round_wall_seconds,wall_bytes,ranges[4]))
    return fail(error,error_capacity,"基准指针或范围无效");
  for(size_t a=0;a<5;++a)for(size_t b=a+1;b<5;++b)
    if(ranges[a].start<ranges[b].end && ranges[b].start<ranges[a].end)
      return fail(error,error_capacity,"源、工作区与计时数组不得重叠");
  const size_t bytes=mode?image_bytes:total;
  // 循环内不分配内存、不读文件、不哈希；回调包含真实公开C ABI和OpenMP调度成本。
  for(size_t rep=0;rep<repeats;++rep) {
    const auto outer=Clock::now();
    for(size_t image=0;image<segments;++image) {
      const size_t offset=image*bytes,sample=rep*segments+image;
      const auto start=Clock::now();
      std::memcpy(work+offset,source+offset,bytes);
      const auto copied=Clock::now();
      if(apply(handle,work+offset,bytes,kernel,threads,error,error_capacity))return 2;
      const auto done=Clock::now();
      apply_seconds[sample]=elapsed(copied,done);
      copy_apply_seconds[sample]=elapsed(start,done);
    }
    round_wall_seconds[rep]=elapsed(outer,Clock::now());
  }
  return 0;
}

int jshc_sb_probe_team(int requested,int* cpus,size_t capacity,int* actual,char* error,size_t error_capacity) {
  if(requested<1 || !cpus || !actual || capacity<static_cast<size_t>(requested))
    return fail(error,error_capacity,"线程探针参数无效");
  int count=0;
#pragma omp parallel num_threads(requested)
  {
#pragma omp single
    count=omp_get_num_threads();
    const int thread=omp_get_thread_num();
    if(static_cast<size_t>(thread)<capacity)cpus[thread]=sched_getcpu();
  }
  *actual=count;
  return count==requested?0:fail(error,error_capacity,"实际OpenMP团队与请求不同");
}
