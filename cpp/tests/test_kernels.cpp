// A single phase gate: independent 64-bit barycentric oracle, enabled backends,
// full RGB cube with --full, nonuniform grids, tails and four integer stages.
#include "jshc/lut.hpp"

#include <algorithm>
#include <chrono>
#include <cmath>
#include <cstdio>
#include <cstring>
#include <filesystem>
#include <limits>
#include <random>
#include <stdexcept>
#include <vector>

using namespace jshc;
static int failures = 0;
#define CHECK(cond, msg) do { if (!(cond)) { \
  std::fprintf(stderr, "FAIL %s:%d %s\n", __FILE__, __LINE__, msg); ++failures; \
} } while (0)

static SparseLut make_lut(uint32_t m, bool identity, uint32_t seed, bool nonuniform = false) {
  SparseLut L;
  L.m = m;
  for (int a = 0; a < 3; ++a) {
    L.grid[a].resize(m);
    for (uint32_t i = 0; i < m; ++i) {
      const double t = double(i) / (m - 1);
      L.grid[a][i] = float(255.0 * (nonuniform ? std::pow(t, 1.2 + 0.3 * a) : t));
    }
    for (int x = 0; x < 256; ++x) {
      const auto next = std::upper_bound(L.grid[a].begin(), L.grid[a].end(), float(x));
      const size_t i = std::min(size_t(next - L.grid[a].begin() - 1), size_t(m - 2));
      L.idx[a][x] = uint8_t(i);
      const double f = (x - double(L.grid[a][i])) / (double(L.grid[a][i + 1]) - L.grid[a][i]);
      L.frac[a][x] = uint32_t(std::floor(f * kOne + 0.5));
    }
  }
  L.nodes.resize(size_t(m) * m * m * 3);
  std::mt19937 rng(seed);
  for (uint32_t i = 0; i < m; ++i)
    for (uint32_t j = 0; j < m; ++j)
      for (uint32_t k = 0; k < m; ++k) {
        uint8_t* p = &L.nodes[((size_t(i) * m + j) * m + k) * 3];
        if (identity) {
          p[0] = uint8_t(i * 255 / (m - 1));
          p[1] = uint8_t(j * 255 / (m - 1));
          p[2] = uint8_t(k * 255 / (m - 1));
        } else {
          for (int c = 0; c < 3; ++c) p[c] = uint8_t(rng());
        }
      }
  L.prepare();
  return L;
}

// Deliberately does not use off/packed caches, the production sorting network,
// telescoping weights, or 32-bit arithmetic for the weighted colour sum.
static void oracle(const SparseLut& L, const uint8_t* in, uint8_t* out, size_t n) {
  for (size_t i = 0; i < n; ++i) {
    const int r = in[3*i], g = in[3*i+1], b = in[3*i+2];
    const uint32_t f[3] = {L.frac[0][r], L.frac[1][g], L.frac[2][b]};
    int a, z;
    if (f[0] >= f[1]) {
      if (f[1] >= f[2]) { a = 0; z = 2; }
      else if (f[0] >= f[2]) { a = 0; z = 1; }
      else { a = 2; z = 1; }
    } else {
      if (f[0] >= f[2]) { a = 1; z = 2; }
      else if (f[1] >= f[2]) { a = 1; z = 0; }
      else { a = 2; z = 0; }
    }
    const int mid = 3 - a - z;
    const size_t stride[3] = {size_t(L.m)*L.m, L.m, 1};
    const size_t base = (size_t(L.idx[0][r])*L.m + L.idx[1][g])*L.m + L.idx[2][b];
    const size_t v[4] = {base, base+stride[a], base+stride[a]+stride[mid],
                         base+stride[0]+stride[1]+stride[2]};
    const uint32_t w[4] = {uint32_t(kOne)-f[a], f[a]-f[mid], f[mid]-f[z], f[z]};
    for (int c = 0; c < 3; ++c) {
      uint64_t sum = 32768;
      for (int j = 0; j < 4; ++j) sum += uint64_t(w[j]) * L.nodes[3*v[j]+c];
      out[3*i+c] = uint8_t(sum / 65536);
    }
  }
}

static std::vector<Kernel> enabled_backends() {
  std::vector<Kernel> result;
  for (Kernel k : {Kernel::TetraScalar, Kernel::TetraAvx2, Kernel::TetraCppSimd,
                   Kernel::TetraAvx2Madd, Kernel::TetraAvx2ScalarGather,
                   Kernel::TetraAvx2ExactFloat,
                   Kernel::TetraZigSimd4, Kernel::TetraZigSimd8,
                   Kernel::TetraZigSimd16, Kernel::TetraRustSimd}) {
    if (kernel_available(k)) result.push_back(k);
    else {
      bool rejected = false;
      try { (void)resolve_kernel(k); } catch (const std::runtime_error&) { rejected = true; }
      CHECK(rejected, "unavailable backend must fail explicitly");
    }
  }
  return result;
}

int main(int argc, char** argv) try {
  const bool full = argc == 2 && std::strcmp(argv[1], "--full") == 0;
  const size_t n = size_t(1) << (full ? 24 : 16);
  const auto backends = enabled_backends();
  auto chain_backends = backends;
  for (Kernel k : {Kernel::TetraC99, Kernel::TetraStructuredAvx2}) {
    if (kernel_available(k)) {
      chain_backends.push_back(k);
      CHECK(kernel_scratch_bytes(k) == 0, "structured paths need no block scratch");
    } else {
      bool rejected = false;
      try { (void)resolve_kernel(k); } catch (const std::runtime_error&) { rejected = true; }
      CHECK(rejected, "disabled structured backend must fail explicitly");
    }
  }
  CHECK(kernel_available(default_kernel()), "auto resolves to an available backend");
  CHECK(resolve_kernel(Kernel::TetraAuto) == default_kernel(), "auto dispatch");
  CHECK(!kernel_available(Kernel::TetraAsm), "no fake assembly backend");
  std::printf("mode=%s pixels=%zu default=%s avx2_cpu_os=%s\n", full ? "full" : "sampled", n,
              kernel_name(default_kernel()), avx2_available() ? "true" : "false");
  std::vector<uint8_t> cube(n * 3);
  for (size_t i = 0; i < n; ++i) {
    const uint32_t c = full ? uint32_t(i) : uint32_t(i * 2654435761u);
    cube[3*i] = uint8_t(c >> 16); cube[3*i+1] = uint8_t(c >> 8); cube[3*i+2] = uint8_t(c);
  }
  if (!full) std::fill(cube.end() - 3, cube.end(), uint8_t(255));

  // An integer-spacing identity is exact in both interpolation families.
  {
    const auto I = make_lut(18, true, 0);
    std::vector<uint8_t> out(n * 3);
    tetra_scalar(I, cube.data(), out.data(), n);
    CHECK(out == cube, "m18 identity tetrahedral interpolation");
    tri_float(I, cube.data(), out.data(), n);
    CHECK(out == cube, "m18 identity trilinear interpolation");
  }

  // Four official-range sizes, plus one independent nonuniform-axis lattice.
  for (uint32_t m : {17u, 18u, 25u, 33u, 26u}) {
    const auto R = make_lut(m, false, 1234 + m, m == 26);
    std::vector<uint8_t> ref(n * 3), out;
    oracle(R, cube.data(), ref.data(), n);
    for (Kernel k : backends) {
      out = cube;
      apply_chain({&R}, out.data(), n, k, 1);
      CHECK(out == ref, kernel_name(k));
      // Guards, short vectors and odd lengths across the 4096-pixel block edge.
      for (size_t len : {size_t(0),size_t(1),size_t(7),size_t(8),size_t(9),size_t(15),
                         size_t(16),size_t(17),size_t(31),size_t(1001),size_t(4097)}) {
        std::vector<uint8_t> guarded(len * 3 + 32, 0xAB);
        for (size_t j = 0; j < 3 * len; ++j) guarded[3 + j] = cube[3 * 12345 + j];
        std::vector<uint8_t> expected(guarded);
        oracle(R, guarded.data() + 3, expected.data() + 3, len);
        apply_chain({&R}, guarded.data() + 3, len, k, 4);
        CHECK(guarded == expected, "unaligned tails and no overwrite");
      }
    }
    std::printf("m=%u nonuniform=%s oracle equality passed for %zu enabled backends\n",
                m, m == 26 ? "true" : "false", backends.size());
  }

  // Four DIFFERENT LUTs and mixed lattice sizes, with per-stage integer rounding.
  {
    const auto A = make_lut(33, false, 7);
    const auto B = make_lut(18, false, 8, true);
    const auto C = make_lut(25, false, 9);
    const auto D = make_lut(26, false, 10, true);
    const std::vector<const SparseLut*> chain{&A, &B, &C, &D};
    std::vector<uint8_t> ref(cube), tmp(n * 3), out;
    for (const auto* L : chain) { oracle(*L, ref.data(), tmp.data(), n); ref.swap(tmp); }
    for (Kernel k : chain_backends) {
      for (int threads : {1, 4}) {
        out = cube;
        apply_chain(chain, out.data(), n, k, threads);
        CHECK(out == ref, "four-stage fusion / threading vs independent oracle");
      }
    }
  }

  // Target every signed-16 split boundary and the exact-float maximum numerator.
  {
    auto L = make_lut(2, false, 19);
    const uint32_t fractions[] = {0, 1, 32767, 32768, 32769, 65535, 65536};
    for (int a = 0; a < 3; ++a)
      for (int x = 0; x < 256; ++x) {
        L.idx[a][x] = 0;
        L.frac[a][x] = fractions[x % 7];
      }
    std::vector<uint8_t> input;
    for (uint8_t r = 0; r < 7; ++r)
      for (uint8_t g = 0; g < 7; ++g)
        for (uint8_t b = 0; b < 7; ++b) input.insert(input.end(), {r, g, b});
    for (int pattern = 0; pattern < 3; ++pattern) {
      for (size_t i = 0; i < L.nodes.size(); ++i)
        L.nodes[i] = pattern == 0 ? 255 : pattern == 1 ? uint8_t(i % 2 ? 255 : 0) : uint8_t(i % 3 ? 254 : 1);
      L.prepare();
      std::vector<uint8_t> expected(input.size());
      oracle(L, input.data(), expected.data(), input.size() / 3);
      for (Kernel k : backends) {
        auto out = input;
        apply_chain({&L}, out.data(), input.size() / 3, k, 1);
        CHECK(out == expected, "Q16 signed split / exact-float endpoint numerator");
      }
    }
  }

  // Batched scheduling must preserve independent images and safe vector tails.
  {
    const auto A = make_lut(17, false, 71, true);
    const auto B = make_lut(18, false, 72);
    const auto C = make_lut(25, false, 73, true);
    const auto D = make_lut(33, false, 74);
    const std::vector<const SparseLut*> chain{&A, &B, &C, &D};
    const std::vector<size_t> lengths{0, 1, 7, 8, 15, 17, 4095, 4096, 4097, 8193};
    std::vector<std::vector<uint8_t>> inputs, expected;
    for (size_t len : lengths) {
      // Separate allocations, guards and unequal sizes exercise virtual block
      // indexing; the same tests also run in builds with OpenMP disabled.
      inputs.emplace_back(3 * len + 32, 0xCD);
      auto& input = inputs.back();
      for (size_t i = 0; i < 3 * len; ++i) input[i + 3] = cube[i + 123];
      expected.push_back(input);
      auto& output = expected.back();
      for (const auto* L : chain) oracle(*L, output.data() + 3, output.data() + 3, len);
    }
    for (Kernel k : chain_backends) {
      for (int threads : {1, 4}) {
        auto outputs = inputs;
        std::vector<RgbImageView> views;
        for (size_t i = 0; i < outputs.size(); ++i)
          views.push_back({outputs[i].data() + 3, lengths[i]});
        apply_chain_batch(chain, views, k, threads);
        CHECK(outputs == expected, "batch noncontiguous / mixed sizes / guards / threading");
      }
    }
    bool rejected = false;
    try {
      apply_chain_batch(chain, {{inputs.back().data(), 8}, {inputs.back().data() + 3, 8}},
                        Kernel::TetraAuto, 4);
    } catch (const std::runtime_error&) { rejected = true; }
    CHECK(rejected, "overlapping batch views must be rejected before parallel mutation");
  }

  // A complete-node curve proof, global one-hot selection, prefix-only one-hot
  // proof and generic stage in the same four-stage chain. The oracle remains
  // unaware of these shortcuts and compares all RGB inputs in the phase gate.
  if (kernel_available(Kernel::TetraC99)) {
    auto A = make_lut(17, false, 351, true);
    auto B = make_lut(18, false, 352);
    auto C = make_lut(25, false, 353, true);
    auto D = make_lut(33, false, 354);
    for (size_t node = 0; node < A.nodes.size() / 3; ++node) {
      const uint32_t g = static_cast<uint32_t>((node / A.m) % A.m);
      A.nodes[3 * node] = static_cast<uint8_t>(13 * g + 17);
      A.nodes[3 * node + 1] = static_cast<uint8_t>(7 * g + 23);
      A.nodes[3 * node + 2] = 51;
    }
    for (auto& channel : B.nodes) channel = channel & 1 ? 255 : 0;
    for (auto& axis : B.frac) for (size_t x = 0; x < 256; ++x)
      axis[x] = x & 1 ? kOne : 0;
    A.prepare(); B.prepare();
    const std::vector<const SparseLut*> chain{&A, &B, &C, &D};
    const auto plan = inspect_structured_chain(chain);
    CHECK((plan.path == std::array<uint8_t, 4>{1, 2, 2, 0}), "curve/vertex/prefix-vertex/tetra routing");
    CHECK((plan.effective_one_hot == std::array<uint8_t, 4>{0, 1, 1, 0}), "prefix proof never becomes a global model flag");
    std::vector<uint8_t> ref(cube), tmp(n * 3);
    for (const auto* L : chain) { oracle(*L, ref.data(), tmp.data(), n); ref.swap(tmp); }
    for (Kernel k : {Kernel::TetraC99, Kernel::TetraStructuredAvx2}) if (kernel_available(k)) {
      for (int threads : {1, 4}) {
        auto out = cube;
        apply_chain(chain, out.data(), n, k, threads);
        CHECK(out == ref, "all structured routes / full RGB / integer oracle");
      }
      const std::vector<uint8_t> before(cube.begin(), cube.begin() + 3 * 32);
      auto unchanged = before;
      bool rejected = false;
      try { apply_chain({&A}, unchanged.data(), 7, k, 4); }
      catch (const std::runtime_error&) { rejected = true; }
      CHECK(rejected && unchanged == before, "four-stage requirement rejects before any write");
      auto illegal = make_lut(2, false, 355);
      rejected = false;
      try { apply_chain({&A, &B, &illegal, &D}, unchanged.data(), 7, k, 4); }
      catch (const std::runtime_error&) { rejected = true; }
      CHECK(rejected && unchanged == before, "C99 size requirement rejects before any write");
    }
    // Broadcast is also checked with an odd tail and a canonical metadata cache
    // invalidation: the C99 and packed caches must both rebuild after editing.
    for (size_t node = 0; node < D.nodes.size() / 3; ++node) {
      D.nodes[3 * node] = 255; D.nodes[3 * node + 1] = 0; D.nodes[3 * node + 2] = 129;
    }
    D.prepare();
    CHECK(inspect_structured_chain(chain).path[3] == 3, "edited model re-proves constant path");
    for (Kernel k : {Kernel::TetraC99, Kernel::TetraStructuredAvx2}) if (kernel_available(k)) {
      auto out = cube;
      apply_chain(chain, out.data(), 4097, k, 4);
      bool exact = true;
      for (size_t i = 0; i < 4097; ++i)
        exact = exact && out[3*i] == 255 && out[3*i+1] == 0 && out[3*i+2] == 129;
      CHECK(exact && std::equal(out.begin() + 3 * 4097, out.end(), cube.begin() + 3 * 4097),
            "constant broadcast / tail / no overwrite / cache invalidation");
    }
  }

  // Lazy cache invalidation and serialization preserve the authoritative Q16 tables.
  {
    auto L = make_lut(18, false, 99, true);
    const size_t scalar_bytes = L.runtime_bytes();
    (void)L.packed_tables();
    CHECK(L.runtime_bytes() > scalar_bytes, "SIMD nodes materialize lazily");
    if (kernel_available(Kernel::TetraC99)) (void)L.portable_tables();
    L.nodes[0] ^= 255;
    L.prepare();
    CHECK(L.runtime_bytes() == scalar_bytes, "prepare releases stale derived tables");
    CHECK((L.packed_tables().nodes[0] & 255) == L.nodes[0], "rebuilt cache uses edited nodes");
    const auto stamp = std::chrono::steady_clock::now().time_since_epoch().count();
    const auto path = std::filesystem::temp_directory_path() / ("jshc-kernel-" + std::to_string(stamp) + ".slut");
    L.save(path.string());
    const auto roundtrip = SparseLut::load(path.string());
    std::filesystem::remove(path);
    CHECK(L.nodes == roundtrip.nodes, "node serialization");
    CHECK(std::memcmp(L.frac, roundtrip.frac, sizeof(L.frac)) == 0, "Q16 table serialization");
    CHECK(std::memcmp(L.idx, roundtrip.idx, sizeof(L.idx)) == 0, "cell table serialization");
  }

  // Invalid metadata must fail before preparation or opening a destination file.
  // Axis tables remain authoritative; this never recomputes their fractions.
  {
    const auto stamp = std::chrono::steady_clock::now().time_since_epoch().count();
    const auto path = std::filesystem::temp_directory_path() / ("jshc-invalid-grid-" + std::to_string(stamp) + ".slut");
    for (int kind = 0; kind < 6; ++kind) {
      auto bad = make_lut(17, false, 93);
      if (kind == 0) bad.grid[0][3] = std::numeric_limits<float>::quiet_NaN();
      if (kind == 1) bad.grid[1][3] = std::numeric_limits<float>::infinity();
      if (kind == 2) bad.grid[2][3] = bad.grid[2][2];
      if (kind == 3) bad.grid[0][0] = 1;
      if (kind == 4) bad.grid[1].back() = 254;
      if (kind == 5) bad.grid[2].clear();
      bool prepare_rejected = false, save_rejected = false;
      try { bad.prepare(); } catch (const std::runtime_error&) { prepare_rejected = true; }
      try { bad.save(path.string()); } catch (const std::runtime_error&) { save_rejected = true; }
      CHECK(prepare_rejected, "prepare rejects invalid grid metadata");
      CHECK(save_rejected && !std::filesystem::exists(path), "invalid save does not create an output");
      if (std::filesystem::exists(path)) std::filesystem::remove(path);
    }
  }

  // Preserve the pre-existing native fitter acceptance check in the full phase gate.
  if (full) {
    FullLut F; F.data = cube;
    const auto S = fit_r14({&F, &F}, 18, 4, false);
    std::vector<uint8_t> out(cube);
    apply_chain({&S}, out.data(), n, Kernel::TetraAuto, 4);
    CHECK(out == cube, "native fit_r14 identity exactness");
  }
  std::printf("%s (%d failures)\n", failures ? "FAILED" : "OK", failures);
  return failures ? 1 : 0;
} catch (const std::exception& e) {
  std::fprintf(stderr, "FAIL unexpected exception: %s\n", e.what());
  return 1;
}
