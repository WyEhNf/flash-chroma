// 此TU保持通用ISA。GCC内建检测包含CPU及OS的扩展状态支持；关闭变量用于回退合同。
#include "channel_views.hpp"
#include <cstdlib>
namespace jshc_evex256 {
bool evex256_enabled() noexcept {
  static const bool enabled=[] {
    __builtin_cpu_init();
    return __builtin_cpu_supports("avx512f") && __builtin_cpu_supports("avx512vl")
        && __builtin_cpu_supports("avx512bw") && __builtin_cpu_supports("avx512dq")
        && std::getenv("JSHC_EVEX256_DISABLE")==nullptr;
  }();
  return enabled;
}
void avx2_chain(const View* v,size_t stages,uint8_t* data,size_t pixels) noexcept {
  if(evex256_enabled())evex256_chain(v,stages,data,pixels);
  else jshc_delta16::avx2_chain(v,stages,data,pixels);
}
}
