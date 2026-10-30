// 23参考的真实分离输入/输出语义：先复制，再调用未改动的原映射。
#include "channel_runtime.h"
#include <cstdint>
#include <cstdio>
#include <cstring>
#include <limits>
extern "C" JSHC_CC_API int jshc_cc_apply_to(void* handle,const uint8_t* source,uint8_t* destination,size_t bytes,int kernel,int threads,char* error,size_t size) {
  if(jshc_cc_apply(handle,nullptr,0,kernel,threads,error,size))return 1;
  if(!bytes)return 0;
  const uintptr_t src=reinterpret_cast<uintptr_t>(source),dst=reinterpret_cast<uintptr_t>(destination);
  if(bytes%3 || !source || !destination || bytes>std::numeric_limits<uintptr_t>::max()-src || bytes>std::numeric_limits<uintptr_t>::max()-dst || (source!=destination && src<dst+bytes && dst<src+bytes)) {
    if(error && size)std::snprintf(error,size,"RGB输入/输出范围无效或部分重叠");return 1;
  }
  if(source!=destination)std::memcpy(destination,source,bytes);
  return jshc_cc_apply(handle,destination,bytes,kernel,threads,error,size);
}
