#ifndef FLASH_CHROMA_FRAMEWORK_IO_HPP
#define FLASH_CHROMA_FRAMEWORK_IO_HPP

// 框架输入层：保留3DL文本行序；轴与通道变换由数值适配器负责。
#include <array>
#include <algorithm>
#include <cerrno>
#include <cstdio>
#include <cstdint>
#include <cstring>
#include <fstream>
#include <limits>
#include <stdexcept>
#include <string>
#include <vector>

namespace fc_framework_io {
constexpr std::size_t kLutValues = std::size_t{256} * 256 * 256 * 3;

inline bool space(char c) { return c == ' ' || c == '\t' || c == '\r'; }

inline void read_3dl(const std::string& path, std::vector<std::uint16_t>& out,
                     std::size_t expected_values = kLutValues) {
    if (!expected_values || expected_values % 3) throw std::runtime_error("3DL预期元素数非法");
    std::ifstream f;
    std::vector<char> buffer(1024 * 1024);
    f.rdbuf()->pubsetbuf(buffer.data(), static_cast<std::streamsize>(buffer.size()));
    f.open(path);
    if (!f) throw std::runtime_error("不能打开3DL：" + path);
    std::vector<std::uint16_t> parsed;
    parsed.reserve(expected_values);
    std::string line;
    line.reserve(128);
    std::size_t line_number = 0;
    while (std::getline(f, line)) {
        ++line_number;
        std::size_t pos = 0;
        while (pos < line.size() && space(line[pos])) ++pos;
        if (pos == line.size() || line[pos] == '#') continue;
        std::array<std::uint16_t, 3> row{};
        for (unsigned channel = 0; channel < 3; ++channel) {
            while (pos < line.size() && space(line[pos])) ++pos;
            if (pos < line.size() && line[pos] == '+') ++pos;
            if (pos == line.size() || line[pos] < '0' || line[pos] > '9')
                throw std::runtime_error("3DL必须每行三个无符号整数，行" + std::to_string(line_number));
            unsigned value = 0;
            while (pos < line.size() && line[pos] >= '0' && line[pos] <= '9') {
                value = value * 10 + static_cast<unsigned>(line[pos++] - '0');
                if (value > 65535) throw std::runtime_error("3DL数值超出uint16，行" + std::to_string(line_number));
            }
            row[channel] = static_cast<std::uint16_t>(value);
            if (channel != 2 && (pos == line.size() || !space(line[pos])))
                throw std::runtime_error("3DL通道之间缺少空白，行" + std::to_string(line_number));
        }
        while (pos < line.size() && space(line[pos])) ++pos;
        if (pos != line.size() && line[pos] != '#')
            throw std::runtime_error("3DL数据行存在额外字段，行" + std::to_string(line_number));
        if (parsed.size() > expected_values - 3) throw std::runtime_error("3DL数据多于256立方节点");
        parsed.insert(parsed.end(), row.begin(), row.end());
    }
    if (f.bad() || parsed.size() != expected_values) throw std::runtime_error("3DL读取失败或节点数不完整");
    out.swap(parsed);
}

inline std::vector<std::uint8_t> read_rgb_file(const std::string& path, std::size_t expected_bytes) {
    std::ifstream f(path, std::ios::binary | std::ios::ate);
    if (!f) throw std::runtime_error("不能打开输入文件：" + path);
    const auto length = f.tellg();
    if (length < 0 || static_cast<std::uint64_t>(length) != expected_bytes)
        throw std::runtime_error("输入文件字节数不符：" + path);
    if (expected_bytes > static_cast<std::size_t>((std::numeric_limits<std::streamsize>::max)()))
        throw std::runtime_error("输入文件超出流读取范围");
    std::vector<std::uint8_t> result(expected_bytes);
    f.seekg(0);
    if (expected_bytes && !f.read(reinterpret_cast<char*>(result.data()), static_cast<std::streamsize>(expected_bytes)))
        throw std::runtime_error("输入文件未读完整：" + path);
    return result;
}

inline void write_rgb_file_new(const std::string& path, const std::vector<std::uint8_t>& bytes) {
    std::FILE* file = std::fopen(path.c_str(), "wbx");
    if (!file) throw std::runtime_error("输出文件已存在或无法创建：" + path);
    const bool ok = bytes.empty() || std::fwrite(bytes.data(), 1, bytes.size(), file) == bytes.size();
    const int closed = std::fclose(file);
    if (!ok || closed) throw std::runtime_error("输出写入失败，已保留片段：" + path);
}

inline void read_u16_cache(const std::string& path, std::vector<std::uint16_t>& out,
                          std::size_t expected_values = kLutValues) {
    if (expected_values > (std::numeric_limits<std::size_t>::max)() / 2)
        throw std::runtime_error("缓存元素数溢出");
    auto bytes = read_rgb_file(path, expected_values * 2);
    std::vector<std::uint16_t> parsed(expected_values);
    for (std::size_t i = 0; i < expected_values; ++i)
        parsed[i] = static_cast<std::uint16_t>(bytes[2 * i] | (unsigned(bytes[2 * i + 1]) << 8));
    out.swap(parsed);
}

inline void write_u16_cache_new(const std::string& path, const std::vector<std::uint16_t>& values) {
    std::FILE* file = std::fopen(path.c_str(), "wbx");
    if (!file) throw std::runtime_error("缓存已存在或无法创建：" + path);
    std::array<std::uint8_t, 65536> block{};
    bool ok = true;
    for (std::size_t start = 0; start < values.size() && ok; start += block.size() / 2) {
        const std::size_t count = (std::min)(block.size() / 2, values.size() - start);
        for (std::size_t i = 0; i < count; ++i) {
            block[2 * i] = static_cast<std::uint8_t>(values[start + i]);
            block[2 * i + 1] = static_cast<std::uint8_t>(values[start + i] >> 8);
        }
        ok = std::fwrite(block.data(), 2, count, file) == count;
    }
    const int closed = std::fclose(file);
    if (!ok || closed) throw std::runtime_error("缓存写入失败，已保留片段：" + path);
}
} // namespace fc_framework_io
#endif
