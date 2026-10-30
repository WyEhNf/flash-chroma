// 独立AVX-512合同：基线ISA驱动，仅在CPUID/OS状态通过后调用候选。
#include "direct_avx512.h"

#include <algorithm>
#include <cstdio>
#include <cstdlib>
#include <cstring>
#include <stdexcept>
#include <vector>
#if defined(_WIN32)
#define WIN32_LEAN_AND_MEAN
#include <windows.h>
#else
#include <sys/mman.h>
#include <unistd.h>
#endif

namespace {
constexpr std::size_t domain = std::size_t(1) << 24;

class Guarded {
public:
  explicit Guarded(std::size_t bytes) : size_(bytes) {
#if defined(_WIN32)
    SYSTEM_INFO info{};
    GetSystemInfo(&info);
    const std::size_t page = info.dwPageSize;
#else
    const std::size_t page = std::size_t(sysconf(_SC_PAGESIZE));
#endif
    const std::size_t body = ((bytes + 64 + page - 1) / page) * page;
    total_ = body + 2 * page;
#if defined(_WIN32)
    base_ = static_cast<std::uint8_t*>(VirtualAlloc(
        nullptr, total_, MEM_RESERVE | MEM_COMMIT, PAGE_NOACCESS));
    DWORD old = 0;
    if (!base_ || !VirtualProtect(base_ + page, body, PAGE_READWRITE, &old))
      throw std::runtime_error("保护页分配失败");
#else
    base_ = static_cast<std::uint8_t*>(mmap(
        nullptr, total_, PROT_NONE, MAP_PRIVATE | MAP_ANONYMOUS, -1, 0));
    if (base_ == MAP_FAILED || mprotect(base_ + page, body, PROT_READ | PROT_WRITE))
      throw std::runtime_error("保护页分配失败");
#endif
    data_ = base_ + page + body - bytes;
    std::memset(data_ - 64, 0xa5, 64);
  }
  ~Guarded() {
#if defined(_WIN32)
    if (base_) VirtualFree(base_, 0, MEM_RELEASE);
#else
    if (base_ && base_ != MAP_FAILED) munmap(base_, total_);
#endif
  }
  Guarded(const Guarded&) = delete;
  Guarded& operator=(const Guarded&) = delete;
  std::uint8_t* data() { return data_; }
  void check() const {
    for (unsigned i = 1; i <= 64; ++i)
      if (data_[-int(i)] != 0xa5) throw std::runtime_error("前哨兵改变");
  }
private:
  std::size_t size_, total_ = 0;
  std::uint8_t *base_ = nullptr, *data_ = nullptr;
};

std::uint32_t id8(std::uint32_t code) {
  return (code * 13u + (code >> 8) * 7u + (code >> 16) * 31u) & 255u;
}
std::uint32_t id16(std::uint32_t code) {
  return (code * 251u + (code >> 7) * 17u + (code >> 15)) & 65535u;
}
std::uint32_t color(std::uint32_t id) {
  return (id * 0x9e3779b1u) ^ (id << 13) ^ 0xa55a39u;
}
std::uint32_t rgb24(std::uint32_t code) {
  return (code * 0x6c8e9cf5u) ^ (code >> 5) ^ 0x12489bu;
}
std::uint32_t output(unsigned format, std::uint32_t code) {
  return format == 8 ? color(id8(code)) : format == 16 ? color(id16(code)) : rgb24(code);
}
void put(std::uint8_t* p, std::uint32_t value) {
  p[0] = std::uint8_t(value);
  p[1] = std::uint8_t(value >> 8);
  p[2] = std::uint8_t(value >> 16);
}
void call(unsigned format, const std::uint8_t* table, const std::uint32_t* palette,
          const std::uint8_t* src, std::uint8_t* dst, std::size_t n) {
  if (format == 8) jshc_channel::avx512_direct_u8(table, palette, src, dst, n);
  else if (format == 16) jshc_channel::avx512_direct_u16(
      reinterpret_cast<const std::uint16_t*>(table), palette, src, dst, n);
  else jshc_channel::avx512_direct_rgb24(table, src, dst, n);
}
void verify(unsigned format, const std::uint8_t* result,
            const std::vector<std::uint32_t>& codes) {
  for (std::size_t i = 0; i < codes.size(); ++i) {
    const std::uint32_t value = output(format, codes[i]);
    for (unsigned c = 0; c < 3; ++c)
      if (result[3 * i + c] != std::uint8_t(value >> (8 * c)))
        throw std::runtime_error("独立整数结果不一致");
  }
}

void run(unsigned format) {
  const std::size_t width = format == 8 ? 1 : format == 16 ? 2 : 3;
  const std::size_t guard = format == 8 ? 0 : 4;
  Guarded table(domain * width + guard);
  Guarded palette_mem((format == 8 ? 256 : 65536) * sizeof(std::uint32_t));
  auto* palette = reinterpret_cast<std::uint32_t*>(palette_mem.data());
  const std::size_t palette_size = format == 8 ? 256 : 65536;
  for (std::size_t i = 0; i < palette_size; ++i) palette[i] = color(std::uint32_t(i));
  for (std::size_t code = 0; code < domain; ++code) {
    if (format == 8) table.data()[code] = std::uint8_t(id8(std::uint32_t(code)));
    else if (format == 16) {
      const std::uint32_t id = id16(std::uint32_t(code));
      table.data()[2 * code] = std::uint8_t(id);
      table.data()[2 * code + 1] = std::uint8_t(id >> 8);
    } else put(table.data() + 3 * code, rgb24(std::uint32_t(code)));
  }
  if (guard) std::memset(table.data() + domain * width, 0x5a, guard);
  call(format, nullptr, nullptr, nullptr, nullptr, 0);
  std::uint32_t state = 0x16a51226u;
  std::size_t finite_calls = 1;
  // 所有0..96长度覆盖各向量边界、全部mod64源/目的非对齐与严格图像末端。
  for (std::size_t n = 1; n <= 96; ++n) {
    Guarded source(3 * n), destination(3 * n), inplace(3 * n);
    std::vector<std::uint32_t> codes(n);
    for (std::size_t i = 0; i < n; ++i) {
      state ^= state << 13; state ^= state >> 17; state ^= state << 5;
      codes[i] = i % 4 == 0 ? 0xffffffu - std::uint32_t(i % 16) : state & 0xffffffu;
      put(source.data() + 3 * i, codes[i]);
    }
    const std::vector<std::uint8_t> original(source.data(), source.data() + 3 * n);
    std::memcpy(inplace.data(), source.data(), 3 * n);
    call(format, table.data(), palette, source.data(), destination.data(), n);
    call(format, table.data(), palette, inplace.data(), inplace.data(), n);
    verify(format, destination.data(), codes);
    verify(format, inplace.data(), codes);
    if (!std::equal(original.begin(), original.end(), source.data()))
      throw std::runtime_error("分离源发生改变");
    source.check(); destination.check(); inplace.check();
    finite_calls += 2;
  }
  // 每种表示独立遍历完整RGB8域，两个实际入口模式均与公式oracle比较。
  constexpr std::size_t chunk = 4096;
  Guarded source(3 * chunk), destination(3 * chunk), inplace(3 * chunk);
  std::vector<std::uint32_t> codes(chunk);
  for (std::size_t begin = 0; begin < domain; begin += chunk) {
    for (std::size_t i = 0; i < chunk; ++i) {
      codes[i] = std::uint32_t(begin + i);
      put(source.data() + 3 * i, codes[i]);
    }
    std::memcpy(inplace.data(), source.data(), 3 * chunk);
    call(format, table.data(), palette, source.data(), destination.data(), chunk);
    call(format, table.data(), palette, inplace.data(), inplace.data(), chunk);
    verify(format, destination.data(), codes);
    verify(format, inplace.data(), codes);
  }
  source.check(); destination.check(); inplace.check(); table.check(); palette_mem.check();
  for (std::size_t i = 0; i < guard; ++i)
    if (table.data()[domain * width + i] != 0x5a) throw std::runtime_error("模型guard改变");
  std::printf("format=%u finite_calls=%zu full_domain_pixels=%zu inout=pass guard=pass\n",
              format, finite_calls, 2 * domain);
}
} // namespace

int main() {
  const bool supported = jshc_channel::cpu_avx512_direct_supported();
  std::printf("avx512_direct_supported=%d\n", int(supported));
  if (!supported) { std::puts("SKIP: 当前CPU/OS不支持所需AVX-512状态"); return 77; }
  try {
    run(8); run(16); run(24);
    std::puts("PASS: 三种表示、完整RGB8域、原地/分离和保护页合同");
  } catch (const std::exception& e) {
    std::fprintf(stderr, "FAIL: %s\n", e.what());
    return 1;
  }
  return 0;
}
