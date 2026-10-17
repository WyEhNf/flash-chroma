#include "portable_bridge.hpp"

#include <atomic>
#include <cstring>
#include <limits>
#include <stdexcept>

namespace jshc {
namespace {
void put32(uint8_t* out, uint32_t value) {
  out[0] = static_cast<uint8_t>(value);
  out[1] = static_cast<uint8_t>(value >> 8);
  out[2] = static_cast<uint8_t>(value >> 16);
  out[3] = static_cast<uint8_t>(value >> 24);
}
}

const SparseLut::PortableTables& SparseLut::portable_tables() const {
  auto cached = std::atomic_load(&portable_cache_);
  if (cached) return *cached;
  if (m < 17 || m > 33 || nodes.size() != size_t(m) * m * m * 3)
    throw std::runtime_error("C99/structured kernels require 17 <= m <= 33");
  static_assert(sizeof(float) == 4 && std::numeric_limits<float>::is_iec559,
                "SLUT metadata requires IEEE binary32");
  auto tables = std::make_shared<PortableTables>();
  auto& bytes = tables->serialized;
  bytes.resize(16 + 12 * m + sizeof(idx) + sizeof(frac) + nodes.size());
  std::memcpy(bytes.data(), "SLUT", 4);
  put32(bytes.data() + 4, 1); put32(bytes.data() + 8, m); put32(bytes.data() + 12, 0);
  size_t offset = 16;
  for (const auto& axis : grid) {
    if (axis.size() != m) throw std::runtime_error("invalid C99 bridge grid shape");
    for (float value : axis) {
      uint32_t bits;
      std::memcpy(&bits, &value, 4);
      put32(bytes.data() + offset, bits); offset += 4;
    }
  }
  std::memcpy(bytes.data() + offset, idx, sizeof(idx)); offset += sizeof(idx);
  for (const auto& axis : frac) for (uint32_t value : axis) {
    put32(bytes.data() + offset, value); offset += 4;
  }
  std::memcpy(bytes.data() + offset, nodes.data(), nodes.size());
  const auto status = jshc_p_model_prepare(&tables->model, bytes.data(), bytes.size());
  if (status != JSHC_P_OK)
    throw std::runtime_error(std::string("C99 model preparation: ") + jshc_p_status_string(status));
  std::shared_ptr<const PortableTables> desired = tables;
  if (std::atomic_compare_exchange_strong(&portable_cache_, &cached, desired)) return *desired;
  return *cached;
}

namespace detail {
void prepare_portable_chain(const std::vector<const SparseLut*>& chain, jshc_p_chain& out) {
  if (chain.size() != JSHC_P_STAGES)
    throw std::runtime_error("C99/structured kernels require exactly four sparse LUTs");
  const jshc_p_model* models[JSHC_P_STAGES];
  for (size_t s = 0; s < chain.size(); ++s) {
    if (!chain[s]) throw std::runtime_error("null sparse LUT in C99 chain");
    models[s] = &chain[s]->portable_tables().model;
  }
  const auto status = jshc_p_chain_prepare(&out, models, 0);
  if (status != JSHC_P_OK)
    throw std::runtime_error(std::string("C99 chain preparation: ") + jshc_p_status_string(status));
}

void validate_portable_image(const jshc_p_chain& chain, const RgbImageView& image) {
  if (!image.pixels) return;
  const uintptr_t begin = reinterpret_cast<uintptr_t>(image.rgb);
  if (!image.rgb || image.pixels > std::numeric_limits<size_t>::max() / 3 ||
      begin > std::numeric_limits<uintptr_t>::max() - image.pixels * 3)
    throw std::runtime_error("invalid C99 RGB image span");
  const uintptr_t end = begin + image.pixels * 3;
  auto overlaps = [&](const void* pointer, size_t bytes) {
    const uintptr_t other = reinterpret_cast<uintptr_t>(pointer);
    return begin < other + bytes && other < end;
  };
  if (overlaps(&chain, sizeof(chain))) throw std::runtime_error("RGB pixels overlap prepared C99 chain");
  for (const auto* model : chain.models)
    if (overlaps(model, sizeof(*model)) || overlaps(model->blob, model->blob_bytes))
      throw std::runtime_error("RGB pixels overlap prepared C99 model");
}
}

StructuredChainPlan inspect_structured_chain(const std::vector<const SparseLut*>& chain) {
  jshc_p_chain prepared;
  detail::prepare_portable_chain(chain, prepared);
  StructuredChainPlan result;
  result.prepared_workspace_bytes = sizeof(prepared) + 4 * sizeof(jshc_p_model);
  for (size_t s = 0; s < 4; ++s) {
    result.path[s] = prepared.path[s];
    result.effective_one_hot[s] = prepared.effective_one_hot[s];
    result.model_flags[s] = prepared.models[s]->flags;
    result.serialized_copy_bytes += chain[s]->portable_tables().serialized.size();
  }
  return result;
}
}  // namespace jshc
