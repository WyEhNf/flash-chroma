#pragma once
#include "../skylake-delta16-runtime/channel_views.hpp"
namespace jshc_grid33 {
using View=jshc_delta16::View;
void avx2_chain(const View*,size_t,uint8_t*,size_t) noexcept;
}
