// 两库共用同一真实API计时器，计时包括入口验证与所有拷贝/映射，不包含Python。
#include "channel_runtime.h"
#include <chrono>
#include <cstdio>
extern "C" JSHC_CC_API int jshc_cc_apply_to(void*,const uint8_t*,uint8_t*,size_t,int,int,char*,size_t);
extern "C" JSHC_CC_API int jshc_cc_bench_to(void* handle,const uint8_t* source,uint8_t* destination,size_t bytes,int kernel,int threads,size_t repeats,double* seconds,char* error,size_t size) {
  if(!seconds || repeats<1 || repeats>100) {if(error && size)std::snprintf(error,size,"无效输出计时参数");return 1;}
  for(size_t r=0;r<repeats;++r) {
    const auto start=std::chrono::steady_clock::now();
    const int status=jshc_cc_apply_to(handle,source,destination,bytes,kernel,threads,error,size);
    const auto end=std::chrono::steady_clock::now();
    if(status)return status;
    seconds[r]=std::chrono::duration<double>(end-start).count();
  }
  return 0;
}
