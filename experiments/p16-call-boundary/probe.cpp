#include <chrono>
#include <cstddef>
#include <cstdint>
#include <cstdio>
#include <limits>
#if defined(_WIN32)
#define API __declspec(dllexport)
#else
#define API __attribute__((visibility("default")))
#endif
using ApplyTo=int (*)(void*,const uint8_t*,uint8_t*,size_t,int,int,char*,size_t);
// 诊断已有入口的调用/块分配边界，不是新的像素或批处理实现。
extern "C" API int jshc_call_boundary(ApplyTo function,void* handle,const uint8_t* source,uint8_t* destination,
    size_t image_bytes,size_t images,int mode,int threads,size_t repeats,double* seconds,char* error,size_t error_bytes) {
  const auto fail=[&](const char* text){if(error && error_bytes)std::snprintf(error,error_bytes,"%s",text);return 1;};
  if(!function || !handle || !source || !destination || !image_bytes || image_bytes%3 || !images || images>100 ||
      image_bytes>std::numeric_limits<size_t>::max()/images || (mode!=0 && mode!=1) || threads<1 || threads>256 ||
      !repeats || repeats>256 || !seconds)return fail("调用边界探针参数非法");
  const size_t bytes=image_bytes*images;
  const uintptr_t src=reinterpret_cast<uintptr_t>(source),dst=reinterpret_cast<uintptr_t>(destination);
  if(bytes>std::numeric_limits<uintptr_t>::max()-src || bytes>std::numeric_limits<uintptr_t>::max()-dst ||
      (src<dst+bytes && dst<src+bytes))return fail("调用边界探针要求完整不重叠源/目标范围");
  for(size_t repeat=0;repeat<repeats;++repeat) {
    const auto begin=std::chrono::steady_clock::now();
    if(mode==0) {
      const int rc=function(handle,source,destination,bytes,1,threads,error,error_bytes);
      if(rc)return rc;
    }else {
      for(size_t image=0;image<images;++image) {
        const size_t offset=image*image_bytes;
        const int rc=function(handle,source+offset,destination+offset,image_bytes,1,threads,error,error_bytes);
        if(rc)return rc;
      }
    }
    seconds[repeat]=std::chrono::duration<double>(std::chrono::steady_clock::now()-begin).count();
  }
  if(error && error_bytes)error[0]=0;
  return 0;
}
