#include <array>
#include <chrono>
#include <cstddef>
#include <cstdint>
#include <cstdio>
#include <cstring>
#include <limits>
#if defined(_WIN32)
#define API __declspec(dllexport)
#else
#define API __attribute__((visibility("default")))
#endif
using ApplyTo=int (*)(void*,const uint8_t*,uint8_t*,size_t,int,int,char*,size_t);
using Segments=int (*)(void*,const uint8_t* const*,uint8_t* const*,const size_t*,size_t,int,int,char*,size_t);
// role0=旧87逐图，role1=旧87连续bulk（非连续布局含pack/scatter），role2=新显式segments。
// 全部函数指针调用、必要适配、目标入口验证及调度均在每轮计时内，目标内存由调用者持有。
extern "C" API int jshc_segment_driver(ApplyTo old_api,Segments new_api,void* old_handle,void* new_handle,
    const uint8_t* const* sources,uint8_t* const* destinations,size_t image_bytes,size_t images,
    uint8_t* packed_source,uint8_t* packed_destination,int layout,int role,int threads,size_t repeats,
    double* seconds,char* error,size_t error_bytes) {
  const auto fail=[&](const char* text){if(error && error_bytes)std::snprintf(error,error_bytes,"%s",text);return 1;};
  if(!old_api || !new_api || !old_handle || !new_handle || !sources || !destinations ||
      !packed_source || !packed_destination || !image_bytes || image_bytes%3 || !images || images>100 ||
      image_bytes>std::numeric_limits<size_t>::max()/images || (layout!=0 && layout!=1) || role<0 || role>2 ||
      threads<1 || threads>256 || !repeats || repeats>256 || !seconds)return fail("分段计时驱动参数非法");
  std::array<size_t,100> lengths{};
  for(size_t i=0;i<images;++i) {
    if(!sources[i] || !destinations[i])return fail("计时非空图像指针无效");
    lengths[i]=image_bytes;
    if(!layout && (sources[i]!=packed_source+i*image_bytes || destinations[i]!=packed_destination+i*image_bytes))
      return fail("连续对照要求三角色使用相同源/目标缓冲");
  }
  for(size_t repeat=0;repeat<repeats;++repeat) {
    const auto begin=std::chrono::steady_clock::now();int rc=0;
    if(role==0) {
      for(size_t i=0;i<images;++i) {rc=old_api(old_handle,sources[i],destinations[i],image_bytes,1,threads,error,error_bytes);if(rc)return rc;}
    }else if(role==1) {
      if(layout)for(size_t i=0;i<images;++i)std::memcpy(packed_source+i*image_bytes,sources[i],image_bytes);
      rc=old_api(old_handle,packed_source,packed_destination,image_bytes*images,1,threads,error,error_bytes);if(rc)return rc;
      if(layout)for(size_t i=0;i<images;++i)std::memcpy(destinations[i],packed_destination+i*image_bytes,image_bytes);
    }else {
      rc=new_api(new_handle,sources,destinations,lengths.data(),images,1,threads,error,error_bytes);if(rc)return rc;
    }
    seconds[repeat]=std::chrono::duration<double>(std::chrono::steady_clock::now()-begin).count();
  }
  if(error && error_bytes)error[0]=0;
  return 0;
}
