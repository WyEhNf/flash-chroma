#pragma once
#include "../skylake-delta16-runtime/channel_views.hpp"
namespace jshc_evex256 {
using View=jshc_delta16::View;
bool evex256_enabled() noexcept;
void evex256_chain(const View*,size_t,uint8_t*,size_t) noexcept;
void avx2_chain(const View*,size_t,uint8_t*,size_t) noexcept;
}
