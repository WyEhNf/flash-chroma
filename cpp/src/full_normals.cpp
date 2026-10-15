// Exact uint64 Q16 moments over every RGB8 input. Portable C++17; no pixel
// runtime dependency. Even/odd R-cell slabs own disjoint pairs of node planes.
#include "jshc/full_normals.h"
#include <algorithm>
#include <array>
#include <cstdio>
#include <limits>
#include <stdexcept>
#include <vector>
#if defined(_OPENMP)
#include <omp.h>
#endif
#ifndef JSHC_FULL_FIT_SOURCE_SHA256
#error Build the jshc_full_fit CMake target to embed its source fingerprint.
#endif

uint32_t jshc_full_normals_abi_v1(void) noexcept { return 1; }
uint32_t jshc_full_normals_openmp_v1(void) noexcept {
#if defined(_OPENMP)
  return 1;
#else
  return 0;
#endif
}
const char* jshc_full_normals_source_v1(void) noexcept { return JSHC_FULL_FIT_SOURCE_SHA256; }

int jshc_full_normals_v1(
    const uint8_t* rgb, uint64_t rgb_bytes, const uint8_t* indices,
    const uint32_t* fractions, uint32_t m, uint32_t threads,
    uint64_t* diagonal, uint64_t diagonal_count, uint64_t* upper, uint64_t upper_count,
    uint64_t* rhs, uint64_t rhs_count, uint64_t* metadata, uint64_t metadata_count,
    char* error, uint64_t error_capacity) noexcept {
  if (error && error_capacity) error[0] = '\0';
  try {
    constexpr uint32_t one = 1u << 16;
    constexpr uint64_t colors = 1ull << 24;
    if (m < 17 || m > 33 || threads < 1 || threads > 256)
      throw std::invalid_argument("expected 17<=m<=33 and 1<=threads<=256");
    const size_t M = static_cast<size_t>(m) * m * m;
    if (!rgb || !indices || !fractions || !diagonal || !upper || !rhs || !metadata ||
        rgb_bytes != colors * 3 || diagonal_count != M || upper_count != 7 * M ||
        rhs_count != 3 * M || metadata_count != 7)
      throw std::invalid_argument("invalid/null full-LUT, axis or output buffer");
    for (size_t i = 0; i < 768; ++i)
      if (indices[i] > m - 2 || fractions[i] > one)
        throw std::invalid_argument("axis index or Q16 fraction out of range");
    // No output is modified until all input ranges and lengths are checked.
    std::fill_n(diagonal, M, uint64_t{0});
    std::fill_n(upper, 7 * M, uint64_t{0});
    std::fill_n(rhs, 3 * M, uint64_t{0});
    std::fill_n(metadata, 7, uint64_t{0});
    std::vector<std::vector<uint16_t>> red_values(m - 1);
    for (uint16_t r = 0; r < 256; ++r) red_values[indices[r]].push_back(r);
    std::vector<std::array<uint64_t, 4>> slab_stats(m - 1);
    const int32_t sr = static_cast<int32_t>(m * m), sg = static_cast<int32_t>(m);
    uint64_t actual_threads = 1;
    for (int parity = 0; parity < 2; ++parity) {
#if defined(_OPENMP)
#pragma omp parallel num_threads(threads)
#endif
      {
#if defined(_OPENMP)
#pragma omp single
        actual_threads = std::max(actual_threads, static_cast<uint64_t>(omp_get_num_threads()));
#pragma omp for schedule(dynamic, 1)
#endif
        for (int cr = parity; cr < static_cast<int>(m) - 1; cr += 2) {
          std::array<uint64_t, 3> square_sum{};
          for (const uint16_t r : red_values[cr]) {
            const int32_t off_r = cr * sr;
            const uint32_t fr = fractions[r];
            for (int g = 0; g < 256; ++g) {
              const int32_t base_rg = off_r + static_cast<int32_t>(indices[256 + g]) * sg;
              const uint32_t fg = fractions[256 + g];
              const uint8_t* row = rgb + ((static_cast<size_t>(r) * 256 + g) * 256) * 3;
              for (int b = 0; b < 256; ++b) {
                struct Axis { uint32_t f; int32_t stride; unsigned bit; };
                std::array<Axis, 3> order{{{fr, sr, 4}, {fg, sg, 2}, {fractions[512 + b], 1, 1}}};
                if (order[1].f > order[0].f) std::swap(order[0], order[1]);
                if (order[2].f > order[0].f) std::swap(order[0], order[2]);
                if (order[2].f > order[1].f) std::swap(order[1], order[2]);
                const int32_t u = base_rg + indices[512 + b];
                const std::array<int32_t, 4> vertex{{u, u + order[0].stride,
                    u + order[0].stride + order[1].stride, u + sr + sg + 1}};
                const std::array<unsigned, 4> mask{{0, order[0].bit, order[0].bit | order[1].bit, 7}};
                const std::array<uint32_t, 4> w{{one - order[0].f, order[0].f - order[1].f,
                                                order[1].f - order[2].f, order[2].f}};
                const uint8_t* y = row + 3 * b;
                for (int c = 0; c < 3; ++c) square_sum[c] += static_cast<uint64_t>(y[c]) * y[c];
                for (int a = 0; a < 4; ++a) {
                  if (!w[a]) continue;
                  const size_t v = static_cast<size_t>(vertex[a]);
                  const uint64_t wa = w[a];
                  diagonal[v] += wa * wa;
                  for (int c = 0; c < 3; ++c) rhs[3 * v + c] += wa * y[c];
                  for (int e = a + 1; e < 4; ++e)
                    if (w[e]) upper[7 * v + (mask[e] - mask[a] - 1)] += wa * w[e];
                }
              }
            }
          }
          slab_stats[cr] = {{static_cast<uint64_t>(red_values[cr].size()) * 65536,
                            square_sum[0], square_sum[1], square_sum[2]}};
        }
      }
    }
    // w<=2^16 and N=2^24 imply any H accumulator<=2^56, any rhs<2^48,
    // and sum(y_c^2)<2^40. All intermediate products and sums fit uint64.
    for (const auto& slab : slab_stats) {
      metadata[0] += slab[0];
      for (int c = 0; c < 3; ++c) metadata[4 + c] += slab[1 + c];
    }
    metadata[1] = actual_threads; metadata[2] = m - 1; metadata[3] = 1;
    if (metadata[0] != colors) throw std::runtime_error("full-domain color coverage failed");
    return 0;
  } catch (const std::exception& exception) {
    if (error && error_capacity)
      std::snprintf(error, static_cast<size_t>(std::min<uint64_t>(error_capacity,
          std::numeric_limits<size_t>::max())), "%s", exception.what());
    return 1;
  } catch (...) {
    if (error && error_capacity)
      std::snprintf(error, static_cast<size_t>(std::min<uint64_t>(error_capacity,
          std::numeric_limits<size_t>::max())), "unknown full-domain assembly failure");
    return 2;
  }
}
