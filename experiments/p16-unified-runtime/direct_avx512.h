#pragma once

#include <cstddef>
#include <cstdint>

#if defined(_MSC_VER) && (defined(_M_X64) || defined(_M_IX86))
#include <intrin.h>
#elif defined(__x86_64__) || defined(__i386__)
#include <cpuid.h>
#endif

namespace jshc_channel {

// 本函数须由基线ISA的调用方编译；检查OS保存状态后才执行XGETBV。
// 显式要求目标Skylake-SP全部已用特性，不依赖VBMI/VBMI2/VNNI。
inline bool cpu_avx512_direct_supported() noexcept {
#if defined(_MSC_VER) && (defined(_M_X64) || defined(_M_IX86))
  int regs[4]{};
  __cpuidex(regs, 0, 0);
  if (regs[0] < 7) return false;
  __cpuidex(regs, 1, 0);
  constexpr unsigned required1 = (1u << 26) | (1u << 27) | (1u << 28);
  if ((static_cast<unsigned>(regs[2]) & required1) != required1) return false;
  const std::uint64_t xcr0 = _xgetbv(0);
  if ((xcr0 & 0xe6u) != 0xe6u) return false;
  __cpuidex(regs, 7, 0);
  constexpr unsigned required7 = (1u << 5) | (1u << 16) | (1u << 17) |
                                 (1u << 30) | (1u << 31);
  return (static_cast<unsigned>(regs[1]) & required7) == required7;
#elif defined(__x86_64__) || defined(__i386__)
  unsigned eax = 0, ebx = 0, ecx = 0, edx = 0;
  if (__get_cpuid_max(0, nullptr) < 7) return false;
  __cpuid_count(1, 0, eax, ebx, ecx, edx);
  constexpr unsigned required1 = (1u << 26) | (1u << 27) | (1u << 28);
  if ((ecx & required1) != required1) return false;
  unsigned xcr0_low = 0, xcr0_high = 0;
  __asm__ volatile("xgetbv" : "=a"(xcr0_low), "=d"(xcr0_high) : "c"(0));
  if ((xcr0_low & 0xe6u) != 0xe6u) return false;
  __cpuid_count(7, 0, eax, ebx, ecx, edx);
  constexpr unsigned required7 = (1u << 5) | (1u << 16) | (1u << 17) |
                                 (1u << 30) | (1u << 31);
  return (ebx & required7) == required7;
#else
  return false;
#endif
}

// 三种表均按R低8位/G中8位/B高8位索引完整256^3输入域。
// u8表无需guard；u16/RGB24载荷之后至少有4个可读guard字节。
// palette须覆盖全部有效ID。
// RGB32 palette的低三字节为RGB，最高字节被忽略。
// source/output支持精确原地或完全分离，部分重叠不属于接口合同。
// 图像无需padding或对齐。pixels=0时不读取表、palette或图像指针。
// 调用方必须先检查cpu_avx512_direct_supported()；这些入口不自行分派。
void avx512_direct_u8(const std::uint8_t* ids, const std::uint32_t* palette,
                      const std::uint8_t* source, std::uint8_t* output,
                      std::size_t pixels) noexcept;
void avx512_direct_u16(const std::uint16_t* ids, const std::uint32_t* palette,
                       const std::uint8_t* source, std::uint8_t* output,
                       std::size_t pixels) noexcept;
void avx512_direct_rgb24(const std::uint8_t* table, const std::uint8_t* source,
                         std::uint8_t* output, std::size_t pixels) noexcept;

} // namespace jshc_channel
