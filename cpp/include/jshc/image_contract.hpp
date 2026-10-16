// Source-container check after a successful stb decode. Indexed PNGs can be
// reported as RGB by the decoder, but the strict input policy requires source
// RGB8, matching Pillow's RGB mode plus the source bit-depth check.
#pragma once
#include <cstdint>
#include <cstring>
#include <fstream>
#include <string>

namespace jshc::detail {
inline bool png_source_rgb8_or_other_container(const std::string& path) {
  std::ifstream input(path, std::ios::binary);
  if (!input) return false;
  uint8_t header[26]{};
  input.read(reinterpret_cast<char*>(header), sizeof(header));
  const auto count = input.gcount();
  constexpr uint8_t signature[] = {137, 80, 78, 71, 13, 10, 26, 10};
  if (count >= 8 && std::memcmp(header, signature, 8) == 0)
    return count >= 26 && header[24] == 8 && header[25] == 2;
  return true; // Other supported containers retain the decoder's checks.
}
}  // namespace jshc::detail
