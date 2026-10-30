// 固定RGB24→u8调色板ID→RGB24的独立AVX2微基准；不改变公共运行时。
#include <immintrin.h>
#include <omp.h>
#include <algorithm>
#include <array>
#include <chrono>
#include <cstdint>
#include <cstring>
#include <fstream>
#include <iomanip>
#include <iostream>
#include <numeric>
#include <stdexcept>
#include <string>
#include <vector>
#include <windows.h>

namespace jshc_channel {
void avx2_chain_pair48_to(const uint32_t*, const uint32_t*, const uint8_t*, uint8_t*, size_t) noexcept;
void avx2_chain_pair48_to_no_prefetch(const uint32_t*, const uint32_t*, const uint8_t*, uint8_t*, size_t) noexcept;
void avx2_chain_pair48_to_t0(const uint32_t*, const uint32_t*, const uint8_t*, uint8_t*, size_t) noexcept;
void avx2_chain_pair48_to_cached(const uint32_t*, const uint32_t*, const uint8_t*, uint8_t*, size_t) noexcept;
void avx2_chain_pair48_to_t0_cached(const uint32_t*, const uint32_t*, const uint8_t*, uint8_t*, size_t) noexcept;
}

namespace {
using Kernel = void (*)(const uint8_t*, const uint32_t*, const uint8_t*, uint8_t*, size_t);

void repo_current(const uint8_t* table, const uint32_t* palette, const uint8_t* source,
                  uint8_t* destination, size_t pixels) {
  jshc_channel::avx2_chain_pair48_to(reinterpret_cast<const uint32_t*>(table), palette,
                                     source, destination, pixels);
}

void repo_no_prefetch(const uint8_t* table, const uint32_t* palette, const uint8_t* source,
                      uint8_t* destination, size_t pixels) {
  jshc_channel::avx2_chain_pair48_to_no_prefetch(reinterpret_cast<const uint32_t*>(table), palette,
                                                 source, destination, pixels);
}

void repo_t0(const uint8_t* table, const uint32_t* palette, const uint8_t* source,
             uint8_t* destination, size_t pixels) {
  jshc_channel::avx2_chain_pair48_to_t0(reinterpret_cast<const uint32_t*>(table), palette,
                                        source, destination, pixels);
}

void repo_cached(const uint8_t* table, const uint32_t* palette, const uint8_t* source,
                 uint8_t* destination, size_t pixels) {
  jshc_channel::avx2_chain_pair48_to_cached(reinterpret_cast<const uint32_t*>(table), palette,
                                            source, destination, pixels);
}

void repo_t0_cached(const uint8_t* table, const uint32_t* palette, const uint8_t* source,
                    uint8_t* destination, size_t pixels) {
  jshc_channel::avx2_chain_pair48_to_t0_cached(reinterpret_cast<const uint32_t*>(table), palette,
                                               source, destination, pixels);
}

inline uint32_t code_at(const uint8_t* p) {
  return uint32_t(p[0]) | (uint32_t(p[1]) << 8) | (uint32_t(p[2]) << 16);
}

inline __attribute__((always_inline)) __m256i read8(const uint8_t* table,
                                                     const uint32_t* palette,
                                                     const uint8_t* p) {
  const auto value = [table, palette, p](size_t offset) {
    uint32_t code;
    std::memcpy(&code, p + offset, 4);
    return int32_t(palette[table[code & 0xffffffu]]);
  };
  const uint32_t i0 = value(0), i1 = value(3), i2 = value(6), i3 = value(9);
  asm volatile("" : : "r"(i0), "r"(i1), "r"(i2), "r"(i3) : "memory");
  const __m128i lo = _mm_setr_epi32(i0, i1, i2, i3);
  const uint32_t i4 = value(12), i5 = value(15), i6 = value(18), i7 = value(21);
  asm volatile("" : : "r"(i4), "r"(i5), "r"(i6), "r"(i7) : "memory");
  const __m128i hi = _mm_setr_epi32(i4, i5, i6, i7);
  return _mm256_inserti128_si256(_mm256_castsi128_si256(lo), hi, 1);
}

inline __attribute__((always_inline)) __m256i pack(__m256i value) {
  const __m256i bytes = _mm256_shuffle_epi8(
      value, _mm256_setr_epi8(0, 1, 2, 4, 5, 6, 8, 9, 10, 12, 13, 14, -1, -1, -1, -1,
                              0, 1, 2, 4, 5, 6, 8, 9, 10, 12, 13, 14, -1, -1, -1, -1));
  return _mm256_permutevar8x32_epi32(bytes, _mm256_setr_epi32(0, 1, 2, 4, 5, 6, 3, 7));
}

inline __attribute__((always_inline)) void output8(uint8_t* p, __m256i value) {
  const __m256i bytes = _mm256_shuffle_epi8(
      value, _mm256_setr_epi8(0, 1, 2, 4, 5, 6, 8, 9, 10, 12, 13, 14, -1, -1, -1, -1,
                              0, 1, 2, 4, 5, 6, 8, 9, 10, 12, 13, 14, -1, -1, -1, -1));
  const __m128i lo = _mm256_castsi256_si128(bytes), hi = _mm256_extracti128_si256(bytes, 1);
  _mm_storeu_si128(reinterpret_cast<__m128i*>(p), _mm_or_si128(lo, _mm_slli_si128(hi, 12)));
  _mm_storel_epi64(reinterpret_cast<__m128i*>(p + 16), _mm_srli_si128(hi, 4));
}

inline __attribute__((always_inline)) void output32(uint8_t* p, __m256i a, __m256i b,
                                                    __m256i c, __m256i d, bool stream) {
  a = pack(a); b = pack(b); c = pack(c); d = pack(d);
  const __m128i a0 = _mm256_castsi256_si128(a), a1 = _mm256_extracti128_si256(a, 1);
  const __m128i b0 = _mm256_castsi256_si128(b), b1 = _mm256_extracti128_si256(b, 1);
  const __m128i c0 = _mm256_castsi256_si128(c), c1 = _mm256_extracti128_si256(c, 1);
  const __m128i d0 = _mm256_castsi256_si128(d), d1 = _mm256_extracti128_si256(d, 1);
  const __m256i s0 = _mm256_inserti128_si256(_mm256_castsi128_si256(a0), _mm_unpacklo_epi64(a1, b0), 1);
  const __m256i s1 = _mm256_inserti128_si256(_mm256_castsi128_si256(_mm_alignr_epi8(b1, b0, 8)), c0, 1);
  const __m256i s2 = _mm256_inserti128_si256(_mm256_castsi128_si256(_mm_unpacklo_epi64(c1, d0)),
                                             _mm_alignr_epi8(d1, d0, 8), 1);
  if (stream) {
    _mm256_stream_si256(reinterpret_cast<__m256i*>(p), s0);
    _mm256_stream_si256(reinterpret_cast<__m256i*>(p + 32), s1);
    _mm256_stream_si256(reinterpret_cast<__m256i*>(p + 64), s2);
  } else {
    _mm256_storeu_si256(reinterpret_cast<__m256i*>(p), s0);
    _mm256_storeu_si256(reinterpret_cast<__m256i*>(p + 32), s1);
    _mm256_storeu_si256(reinterpret_cast<__m256i*>(p + 64), s2);
  }
}

inline void scalar_one(const uint8_t* table, const uint32_t* palette,
                       const uint8_t* source, uint8_t* destination) {
  const uint32_t value = palette[table[code_at(source)]];
  destination[0] = uint8_t(value); destination[1] = uint8_t(value >> 8);
  destination[2] = uint8_t(value >> 16);
}

enum class Prefetch { None, Nta, T0 };

template <Prefetch Hint, bool Stream, bool Reuse>
void run(const uint8_t* table, const uint32_t* palette, const uint8_t* source,
         uint8_t* destination, size_t pixels) {
  size_t p = 0;
  if constexpr (Stream) {
    for (; p < pixels && (reinterpret_cast<uintptr_t>(destination + 3 * p) & 63); ++p)
      scalar_one(table, palette, source + 3 * p, destination + 3 * p);
  }
  uint32_t previous_code = 0xffffffffu, previous_value = 0;
  if constexpr (Reuse) {
    // 分支型相邻同色复用单独测量，不与向量主体混写结论。
    for (; p < pixels; ++p) {
      const uint32_t code = code_at(source + 3 * p);
      const uint32_t value = code == previous_code ? previous_value : palette[table[code]];
      previous_code = code; previous_value = value;
      destination[3 * p] = uint8_t(value); destination[3 * p + 1] = uint8_t(value >> 8);
      destination[3 * p + 2] = uint8_t(value >> 16);
    }
    return;
  }
  bool streamed = false;
  for (; p + 40 <= pixels; p += 32) {
    if constexpr (Hint != Prefetch::None) {
      if (p + 406 <= pixels) {
        const char* future = reinterpret_cast<const char*>(source + 3 * p + 1024);
        if constexpr (Hint == Prefetch::Nta) {
          _mm_prefetch(future, _MM_HINT_NTA); _mm_prefetch(future + 64, _MM_HINT_NTA);
          _mm_prefetch(future + 128, _MM_HINT_NTA); _mm_prefetch(future + 191, _MM_HINT_NTA);
        } else {
          _mm_prefetch(future, _MM_HINT_T0); _mm_prefetch(future + 64, _MM_HINT_T0);
          _mm_prefetch(future + 128, _MM_HINT_T0); _mm_prefetch(future + 191, _MM_HINT_T0);
        }
      }
    }
    const __m256i a = read8(table, palette, source + 3 * p);
    const __m256i b = read8(table, palette, source + 3 * p + 24);
    const __m256i c = read8(table, palette, source + 3 * p + 48);
    const __m256i d = read8(table, palette, source + 3 * p + 72);
    output32(destination + 3 * p, a, b, c, d, Stream); streamed |= Stream;
  }
  if (streamed) _mm_sfence();
  for (; p + 8 <= pixels; p += 8) output8(destination + 3 * p, read8(table, palette, source + 3 * p));
  for (; p < pixels; ++p) scalar_one(table, palette, source + 3 * p, destination + 3 * p);
}

uint64_t hash64(const uint8_t* data, size_t bytes) {
  uint64_t hash = 1469598103934665603ull;
  for (size_t i = 0; i < bytes; ++i) { hash ^= data[i]; hash *= 1099511628211ull; }
  return hash;
}

std::vector<uint8_t> read_file(const std::string& path) {
  std::ifstream input(path, std::ios::binary);
  if (!input) throw std::runtime_error("无法读取输入批次");
  input.seekg(0, std::ios::end); const auto size = input.tellg(); input.seekg(0);
  const auto bytes = static_cast<std::vector<uint8_t>::size_type>(size);
  std::vector<uint8_t> result(bytes);
  input.read(reinterpret_cast<char*>(result.data()), size);
  return result;
}

void parallel_apply(Kernel kernel, const uint8_t* table, const uint32_t* palette,
                    const uint8_t* source, uint8_t* output, size_t pixels, int threads) {
#pragma omp parallel num_threads(threads)
  {
    const size_t tid = size_t(omp_get_thread_num()), count = size_t(omp_get_num_threads());
    static constexpr DWORD_PTR masks[] = {DWORD_PTR{1} << 0, DWORD_PTR{1} << 2,
                                         DWORD_PTR{1} << 4, DWORD_PTR{1} << 6};
    if (tid < std::size(masks)) SetThreadAffinityMask(GetCurrentThread(), masks[tid]);
    const size_t begin = pixels * tid / count, end = pixels * (tid + 1) / count;
    kernel(table, palette, source + 3 * begin, output + 3 * begin, end - begin);
  }
}

double median(std::vector<double> values) {
  std::sort(values.begin(), values.end());
  return values[values.size() / 2];
}
}  // namespace

int main(int argc, char** argv) try {
  if (argc != 2 && argc != 4)
    throw std::runtime_error("用法：bench_direct_avx2 photos.rgb [candidate threads]");
  const bool verify_cube = std::string(argv[1]) == "--verify-cube";
  std::vector<uint8_t> source;
  if (verify_cube) {
    source.resize((size_t{1} << 24) * 3);
    for (uint32_t code = 0; code < (uint32_t{1} << 24); ++code) {
      source[3 * size_t(code)] = uint8_t(code);
      source[3 * size_t(code) + 1] = uint8_t(code >> 8);
      source[3 * size_t(code) + 2] = uint8_t(code >> 16);
    }
  } else {
    source = read_file(argv[1]);
  }
  if (source.empty() || source.size() % 3) throw std::runtime_error("输入必须是紧密RGB8");
  const size_t pixels = source.size() / 3;
  std::vector<uint8_t> table(size_t{1} << 24), output(source.size()), reference(source.size());
  std::array<uint32_t, 256> palette{};
  for (size_t code = 0; code < table.size(); ++code)
    table[code] = uint8_t((code * 0x9e3779b1u + (code >> 7) + (code >> 17)) % 230);
  for (size_t i = 0; i < palette.size(); ++i)
    palette[i] = uint32_t(i) | (uint32_t((i * 73) & 255) << 8) | (uint32_t((i * 151) & 255) << 16);

  const std::array<std::pair<const char*, Kernel>, 10> kernels{{
      {"repo_current", &repo_current},
      {"repo_no_prefetch", &repo_no_prefetch},
      {"repo_t0", &repo_t0},
      {"repo_cached", &repo_cached},
      {"repo_t0_cached", &repo_t0_cached},
      {"nta_nt", &run<Prefetch::Nta, true, false>},
      {"none_nt", &run<Prefetch::None, true, false>},
      {"t0_nt", &run<Prefetch::T0, true, false>},
      {"none_cached", &run<Prefetch::None, false, false>},
      {"adjacent_reuse_scalar", &run<Prefetch::None, false, true>},
  }};
  run<Prefetch::None, false, false>(table.data(), palette.data(), source.data(), reference.data(), pixels);
  const uint64_t expected = hash64(reference.data(), reference.size());
  if (verify_cube) {
    for (const auto& [name, kernel] : kernels) {
      kernel(table.data(), palette.data(), source.data(), output.data(), pixels);
      if (output != reference) throw std::runtime_error(std::string(name) + "完整域输出不一致");
    }
    std::cout << "{\"complete_rgb8\":true,\"pixels\":" << pixels
              << ",\"kernels\":" << kernels.size() << ",\"hash\":" << expected << "}\n";
    return 0;
  }
  if (argc == 4) {
    const std::string requested = argv[2];
    const int threads = std::stoi(argv[3]);
    const auto found = std::find_if(kernels.begin(), kernels.end(), [&](const auto& row) {
      return requested == row.first;
    });
    if (found == kernels.end() || (threads != 1 && threads != 4))
      throw std::runtime_error("配对候选或线程数非法");
    const Kernel baseline = &repo_current, candidate = found->second;
    parallel_apply(baseline, table.data(), palette.data(), source.data(), output.data(), pixels, threads);
    parallel_apply(candidate, table.data(), palette.data(), source.data(), output.data(), pixels, threads);
    if (hash64(output.data(), output.size()) != expected) throw std::runtime_error("候选输出不一致");
    std::vector<double> ratios, baseline_ms, candidate_ms;
    auto timed = [&](Kernel kernel) {
      const auto start = std::chrono::steady_clock::now();
      parallel_apply(kernel, table.data(), palette.data(), source.data(), output.data(), pixels, threads);
      const auto end = std::chrono::steady_clock::now();
      return std::chrono::duration<double, std::milli>(end - start).count();
    };
    for (int cycle = 0; cycle < 8; ++cycle) {
      std::array<double, 2> a{}, b{};
      if ((cycle & 1) == 0) { a[0] = timed(baseline); b[0] = timed(candidate);
                              b[1] = timed(candidate); a[1] = timed(baseline); }
      else { b[0] = timed(candidate); a[0] = timed(baseline);
             a[1] = timed(baseline); b[1] = timed(candidate); }
      const double am = (a[0] + a[1]) / 2, bm = (b[0] + b[1]) / 2;
      baseline_ms.push_back(am); candidate_ms.push_back(bm); ratios.push_back(bm / am);
    }
    std::cout << "{\"candidate\":\"" << requested << "\",\"threads\":" << threads
              << ",\"cycles\":8,\"baseline_median_ms\":" << std::fixed << std::setprecision(6)
              << median(baseline_ms) << ",\"candidate_median_ms\":" << median(candidate_ms)
              << ",\"paired_ratio_median\":" << median(ratios)
              << ",\"paired_ratio_min\":" << *std::min_element(ratios.begin(), ratios.end())
              << ",\"paired_ratio_max\":" << *std::max_element(ratios.begin(), ratios.end())
              << ",\"baseline_cycle_ms\":[";
    for (size_t i = 0; i < baseline_ms.size(); ++i) {
      if (i) std::cout << ',';
      std::cout << baseline_ms[i];
    }
    std::cout << "],\"candidate_cycle_ms\":[";
    for (size_t i = 0; i < candidate_ms.size(); ++i) {
      if (i) std::cout << ',';
      std::cout << candidate_ms[i];
    }
    std::cout << "],\"paired_ratios\":[";
    for (size_t i = 0; i < ratios.size(); ++i) {
      if (i) std::cout << ',';
      std::cout << ratios[i];
    }
    std::cout << "],\"hash\":" << expected << "}\n";
    return 0;
  }
  std::cout << "{\"environment\":{\"pixels\":" << pixels << ",\"bytes\":" << source.size()
            << ",\"openmp_max_threads\":" << omp_get_max_threads() << "},\"results\":[";
  bool first = true;
  for (int threads : {1, 4}) {
    for (const auto& [name, kernel] : kernels) {
      parallel_apply(kernel, table.data(), palette.data(), source.data(), output.data(), pixels, threads);
      if (hash64(output.data(), output.size()) != expected) throw std::runtime_error(std::string(name) + "输出不一致");
      std::vector<double> times;
      for (int repeat = 0; repeat < 9; ++repeat) {
        const auto start = std::chrono::steady_clock::now();
        parallel_apply(kernel, table.data(), palette.data(), source.data(), output.data(), pixels, threads);
        const auto end = std::chrono::steady_clock::now();
        times.push_back(std::chrono::duration<double, std::milli>(end - start).count());
      }
      if (!first) std::cout << ',';
      first = false;
      std::cout << "{\"kernel\":\"" << name << "\",\"threads\":" << threads
                << ",\"median_ms\":" << std::fixed << std::setprecision(6) << median(times)
                << ",\"min_ms\":" << *std::min_element(times.begin(), times.end())
                << ",\"max_ms\":" << *std::max_element(times.begin(), times.end())
                << ",\"hash\":" << expected << "}";
    }
  }
  std::cout << "]}\n";
  return 0;
} catch (const std::exception& error) {
  std::cerr << error.what() << '\n'; return 1;
}
