// 核验实际 .slut 序列化与独立 C99 运行时的桌面位精确互操作。
#include "jshc/lut.hpp"
#include "jshc_embedded.h"
#include <algorithm>
#include <array>
#include <chrono>
#include <cstdio>
#include <cstring>
#include <filesystem>
#include <fstream>
#include <random>
#include <stdexcept>
#include <vector>

static void require(bool value, const char* message) {
  if (!value) throw std::runtime_error(message);
}

int main() try {
  std::mt19937 random(90210);
  std::array<jshc::SparseLut, 4> desktop;
  std::array<std::vector<uint8_t>, 4> files;
  std::array<jshc_embedded_lut, 4> views;
  std::vector<const jshc::SparseLut*> desktop_chain;
  std::array<const jshc_embedded_lut*, 4> embedded_chain;
  const uint32_t sizes[] = {17, 18, 25, 33};
  for (size_t s = 0; s < 4; ++s) {
    auto& lut = desktop[s];
    lut.m = sizes[s];
    for (int a = 0; a < 3; ++a) {
      for (uint32_t i = 0; i < lut.m; ++i) {
        const auto uniform = i * 255 / (lut.m - 1);
        const auto curved = i * i * 255 / ((lut.m - 1) * (lut.m - 1));
        lut.grid[a].push_back(float(a == 1 ? (uniform + curved) / 2 : uniform));
      }
      for (int x = 0; x < 256; ++x) {
        const auto next = std::upper_bound(lut.grid[a].begin(), lut.grid[a].end(), float(x));
        const size_t cell = std::min(size_t(next - lut.grid[a].begin() - 1), size_t(lut.m - 2));
        lut.idx[a][x] = uint8_t(cell);
        const auto lo = uint32_t(lut.grid[a][cell]), hi = uint32_t(lut.grid[a][cell + 1]);
        lut.frac[a][x] = ((x - lo) * 65536 + (hi - lo) / 2) / (hi - lo);
      }
    }
    lut.nodes.resize(size_t(lut.m) * lut.m * lut.m * 3);
    for (auto& node : lut.nodes) node = uint8_t(random());
    lut.prepare();
    const auto stamp = std::chrono::steady_clock::now().time_since_epoch().count();
    const auto path = std::filesystem::temp_directory_path() /
                      ("jshc-embedded-" + std::to_string(stamp) + "-" + std::to_string(s) + ".slut");
    lut.save(path.string());
    {
      std::ifstream input(path, std::ios::binary);
      files[s].push_back(0);  // 故意错位，检查跨平台读取无需对齐。
      files[s].insert(files[s].end(), std::istreambuf_iterator<char>(input), {});
      require(input.eof() || !input.fail(), "读取 .slut 失败");
    }
    std::filesystem::remove(path);
    require(jshc_embedded_init(&views[s], files[s].data() + 1, files[s].size() - 1) ==
            JSHC_EMBEDDED_OK, "无法读取桌面生成的 .slut");
    desktop_chain.push_back(&lut);
    embedded_chain[s] = &views[s];
  }
  // 分块穷举全部 2^24 RGB；不需要整张 50 MiB cube 工作缓冲。
  for (uint32_t start = 0; start < (1u << 24); start += 4096) {
    std::vector<uint8_t> reference(4096 * 3);
    for (uint32_t i = 0; i < 4096; ++i) {
      const auto value = start + i;
      reference[i * 3] = uint8_t(value >> 16);
      reference[i * 3 + 1] = uint8_t(value >> 8);
      reference[i * 3 + 2] = uint8_t(value);
    }
    auto actual = reference;
    jshc::apply_chain(desktop_chain, reference.data(), 4096, jshc::Kernel::TetraScalar, 1);
    require(jshc_embedded_apply(embedded_chain.data(), 4, actual.data(), 4096) ==
            JSHC_EMBEDDED_OK, "四级嵌入式映射失败");
    require(actual == reference, "嵌入式输出与桌面四级输出不同");
    for (const auto kernel : {jshc::Kernel::TetraC99, jshc::Kernel::TetraStructuredAvx2}) {
      if (!jshc::kernel_available(kernel)) continue;
      for (uint32_t i = 0; i < 4096; ++i) {
        const auto value = start + i;
        actual[i * 3] = uint8_t(value >> 16);
        actual[i * 3 + 1] = uint8_t(value >> 8);
        actual[i * 3 + 2] = uint8_t(value);
      }
      jshc::apply_chain(desktop_chain, actual.data(), 4096, kernel, 1);
      require(actual == reference, "portable/结构化路径与相同序列化四级模型不同");
    }
  }
  std::puts("嵌入式/桌面四级全 RGB 色域逐字节一致");
  return 0;
} catch (const std::exception& error) {
  std::fprintf(stderr, "FAIL：%s\n", error.what());
  return 1;
}
