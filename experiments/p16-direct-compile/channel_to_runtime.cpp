// 独立真分离输出入口：复用原句柄、构造和原地API，不增加模型容量。
#include "../channel-runtime/channel_runtime.cpp"
namespace jshc_channel {
void avx2_chain_to(const View*,size_t,const uint8_t*,uint8_t*,size_t) noexcept;
}
extern "C" JSHC_CC_API uint32_t jshc_cc_outplace_revision(void) {return 86;}
extern "C" JSHC_CC_API int jshc_cc_apply_to(void* handle,const uint8_t* source,uint8_t* destination,
    size_t bytes,int kernel,int threads,char* error,size_t size) {
  try {
    if(!handle)throw std::runtime_error("空研究句柄");
    auto& h=*static_cast<Handle*>(handle);
    apply(h,nullptr,0,kernel,threads);
    if(!bytes) {message(error,size,"");return 0;}
    const uintptr_t src=reinterpret_cast<uintptr_t>(source),dst=reinterpret_cast<uintptr_t>(destination);
    if(bytes%3 || !source || !destination || bytes>std::numeric_limits<uintptr_t>::max()-src ||
        bytes>std::numeric_limits<uintptr_t>::max()-dst || (source!=destination && src<dst+bytes && dst<src+bytes))
      throw std::runtime_error("RGB输入/输出范围无效或部分重叠");
    if(source==destination) {apply(h,destination,bytes,kernel,threads);message(error,size,"");return 0;}
    const size_t pixels=bytes/3,blocks=pixels/4096+(pixels%4096!=0);
    if(blocks>size_t(std::numeric_limits<long long>::max()))throw std::runtime_error("块计数溢出");
#if defined(_OPENMP)
    const int workers=omp_in_parallel()?1:static_cast<int>(std::min(blocks,size_t(threads)));
#pragma omp parallel for schedule(static) num_threads(workers)
#endif
    for(long long block=0;block<static_cast<long long>(blocks);++block) {
      const size_t begin=size_t(block)*4096,n=std::min(size_t{4096},pixels-begin);
      size_t vectorized=0;
#if defined(JSHC_CC_HAVE_AVX2)
      if(kernel==1) {
        vectorized=n&~size_t{7};
        jshc_channel::avx2_chain_to(h.views.data(),h.views.size(),source+3*begin,destination+3*begin,vectorized);
      }
#endif
      if(vectorized!=n) {
        std::memcpy(destination+3*(begin+vectorized),source+3*(begin+vectorized),3*(n-vectorized));
        scalar(h.views.data(),h.views.size(),destination+3*(begin+vectorized),n-vectorized);
      }
    }
    message(error,size,"");return 0;
  }catch(const std::exception& e) {message(error,size,e.what());return 1;}
}
