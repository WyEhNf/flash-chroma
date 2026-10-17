#pragma once

#include "jshc/lut.hpp"

#if defined(JSHC_HAVE_PORTABLE_C)
#include "jshc_portable.h"

namespace jshc {
static_assert(JSHC_P_TETRA == 0 && JSHC_P_CURVE == 1 && JSHC_P_VERTEX == 2 && JSHC_P_CONSTANT == 3,
              "AVX2 structured path numbers must match portable ABI v1");
struct SparseLut::PortableTables {
  std::vector<uint8_t> serialized;
  jshc_p_model model{};
};

namespace detail {
// Model pointers in out borrow the immutable caches of chain, whose lifetime
// and edit contract are identical to the existing AVX2 prepared views.
void prepare_portable_chain(const std::vector<const SparseLut*>& chain, jshc_p_chain& out);
void validate_portable_image(const jshc_p_chain& chain, const RgbImageView& image);
}
}  // namespace jshc
#endif
