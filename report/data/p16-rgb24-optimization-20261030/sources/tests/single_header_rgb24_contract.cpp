/* RGB24独立正确性合同：完整24位域、4B表尾guard、图像保护页与全部64种对齐。
 * 普通AVX2内核由运行时能力保护；不需要BMI，不进行性能计时。
 * 参考严格逐3字节取地址及读表；测试在内核返回后立即读取输出，不额外执行fence。
 */
#define FLASH_CHROMA_IMPLEMENTATION
#include "flash_chroma.hpp"
#include <algorithm>
#include <cstdio>
#include <cstdlib>
#include <cstring>
#include <vector>
#if defined(_WIN32)
#ifndef NOMINMAX
#define NOMINMAX
#endif
#include <windows.h>
#elif defined(__unix__) || defined(__APPLE__)
#include <sys/mman.h>
#include <unistd.h>
#endif

#if FLASH_CHROMA_ENABLE_DIRECT && FLASH_CHROMA_ENABLE_AVX2
namespace {
constexpr std::size_t colours = std::size_t{1} << 24;
constexpr std::size_t table_bytes = colours * 3;
constexpr std::uint8_t sentinel = 0xa5;
std::size_t comparisons = 0;
void require(bool passed, const char* message) {
    if (!passed) { std::fprintf(stderr, "RGB24合同失败：%s\n", message); std::exit(1); }
}

// 可读写区两端均紧邻NOACCESS；table尾部仅承诺4B，图像尾部不承诺任何padding。
class ProtectedBuffer {
    std::uint8_t* base_ = nullptr;
    std::size_t page_ = 0, usable_ = 0, total_ = 0;
public:
    explicit ProtectedBuffer(std::size_t bytes) {
#if defined(_WIN32)
        SYSTEM_INFO info; GetSystemInfo(&info); page_ = info.dwPageSize;
        usable_ = (bytes + page_ - 1) / page_ * page_; total_ = usable_ + 2 * page_;
        base_ = static_cast<std::uint8_t*>(VirtualAlloc(nullptr, total_, MEM_RESERVE | MEM_COMMIT, PAGE_NOACCESS));
        require(base_ != nullptr, "Windows保护页分配失败");
        DWORD previous = 0;
        require(VirtualProtect(base_ + page_, usable_, PAGE_READWRITE, &previous) != 0, "Windows保护页设置失败");
#elif defined(__unix__) || defined(__APPLE__)
        const auto page = sysconf(_SC_PAGESIZE); require(page > 0, "POSIX页大小查询失败"); page_ = std::size_t(page);
        usable_ = (bytes + page_ - 1) / page_ * page_; total_ = usable_ + 2 * page_;
        void* allocation = mmap(nullptr, total_, PROT_NONE, MAP_PRIVATE | MAP_ANONYMOUS, -1, 0);
        require(allocation != MAP_FAILED, "POSIX保护页分配失败"); base_ = static_cast<std::uint8_t*>(allocation);
        require(mprotect(base_ + page_, usable_, PROT_READ | PROT_WRITE) == 0, "POSIX保护页设置失败");
#else
        (void)bytes;
#endif
    }
    ~ProtectedBuffer() {
#if defined(_WIN32)
        if (base_) VirtualFree(base_, 0, MEM_RELEASE);
#elif defined(__unix__) || defined(__APPLE__)
        if (base_) munmap(base_, total_);
#endif
    }
    ProtectedBuffer(const ProtectedBuffer&) = delete;
    ProtectedBuffer& operator=(const ProtectedBuffer&) = delete;
    bool available() const { return base_ != nullptr; }
    std::uint8_t* head() { return base_ + page_; }
    std::uint8_t* tail(std::size_t bytes) {
        require(bytes <= usable_, "保护区容量不足"); return base_ + page_ + usable_ - bytes;
    }
};

using Kernel = void (*)(const std::uint8_t*, const std::uint8_t*, std::uint8_t*, std::size_t);
struct NamedKernel { const char* name; Kernel run; };
const NamedKernel kernels[] = {
    {"gather基线", fc::detail::direct_rgb24_gather_run},
    {"普通AVX2缓存写入", fc::detail::direct_rgb24_block_run<false>},
    {"普通AVX2流式写入", fc::detail::direct_rgb24_block_run<true>},
    {"默认RGB24入口", fc::detail::direct_rgb24_run}
};

void store3(std::uint8_t* bytes, std::uint32_t value) {
    bytes[0] = std::uint8_t(value); bytes[1] = std::uint8_t(value >> 8); bytes[2] = std::uint8_t(value >> 16);
}
void reference(const std::uint8_t* table, const std::uint8_t* input, std::uint8_t* output, std::size_t pixels) {
    for (std::size_t i = 0; i < pixels; ++i) {
        const std::size_t code = std::size_t(input[i * 3]) + std::size_t(input[i * 3 + 1]) * 256 +
                                 std::size_t(input[i * 3 + 2]) * 65536;
        for (unsigned c = 0; c < 3; ++c) output[i * 3 + c] = table[code * 3 + c];
    }
}
std::size_t aligned_at(const std::vector<std::uint8_t>& bytes, unsigned phase) {
    const auto p = reinterpret_cast<std::uintptr_t>(bytes.data());
    return std::size_t(((p + 127) & ~std::uintptr_t{63}) - p) + phase;
}
void window(const std::vector<std::uint8_t>& buffer, std::size_t start, const std::uint8_t* expected, std::size_t bytes) {
    if (bytes) require(std::memcmp(buffer.data() + start, expected, bytes) == 0, "像素输出不符");
    require(std::all_of(buffer.begin(), buffer.begin() + start, [](auto x) { return x == sentinel; }), "输出前哨兵被修改");
    require(std::all_of(buffer.begin() + start + bytes, buffer.end(), [](auto x) { return x == sentinel; }), "输出后哨兵被修改");
}
void aligned_case(Kernel run, const std::uint8_t* table, const std::vector<std::uint8_t>& source,
                  const std::vector<std::uint8_t>& expected, std::size_t pixels, unsigned input_phase, unsigned output_phase) {
    const auto bytes = pixels * 3;
    std::vector<std::uint8_t> input(bytes + 256, sentinel), output(bytes + 256, sentinel);
    const auto input_at = aligned_at(input, input_phase), output_at = aligned_at(output, output_phase);
    if (bytes) std::memcpy(input.data() + input_at, source.data(), bytes);
    run(table, input.data() + input_at, output.data() + output_at, pixels);
    // 普通读紧随流式写函数返回；测试自身没有sfence或其他发布屏障。
    window(output, output_at, expected.data(), bytes);
    window(input, input_at, source.data(), bytes);
    run(table, input.data() + input_at, input.data() + input_at, pixels);
    window(input, input_at, expected.data(), bytes);
    comparisons += 2;
}

void all_colours(const std::uint8_t* table) {
    std::vector<std::uint8_t> source(table_bytes), expected(table_bytes), storage(table_bytes + 256, sentinel);
    // 奇数乘法在模2^24下双射：每个输入恰出现一次，访问顺序不依赖相邻颜色。
    for (std::size_t i = 0; i < colours; ++i) store3(source.data() + i * 3, std::uint32_t(i * 0xc2b2adu + 0x1f327bu) & 0xffffffu);
    reference(table, source.data(), expected.data(), colours);
    for (const auto& kernel : kernels) {
        const auto at = aligned_at(storage, 0);
        std::fill(storage.begin(), storage.end(), sentinel);
        kernel.run(table, source.data(), storage.data() + at, colours);
        window(storage, at, expected.data(), table_bytes);
        std::memcpy(storage.data() + at, source.data(), table_bytes);
        kernel.run(table, storage.data() + at, storage.data() + at, colours);
        window(storage, at, expected.data(), table_bytes);
        comparisons += 2;
        std::printf("%s：16777216输入分离/原地逐字节通过\n", kernel.name);
    }
    for (std::size_t i = 0; i < colours; ++i) {
        const auto code = std::uint32_t(i * 0xc2b2adu + 0x1f327bu) & 0xffffffu;
        require(source[i * 3] == std::uint8_t(code) && source[i * 3 + 1] == std::uint8_t(code >> 8) &&
                source[i * 3 + 2] == std::uint8_t(code >> 16), "完整域分离执行修改源输入");
    }
}

void boundary_cases(const std::uint8_t* table) {
    constexpr std::size_t maximum = 65537;
    std::vector<std::uint8_t> source(maximum * 3), expected(source.size());
    std::uint32_t random = 0x63f29a15;
    for (auto& byte : source) { random ^= random << 13; random ^= random >> 17; random ^= random << 5; byte = std::uint8_t(random); }
    for (std::size_t i = 0; i < maximum; i += 7) store3(source.data() + i * 3, 0xffffffu);
    reference(table, source.data(), expected.data(), maximum);
    std::vector<std::size_t> counts;
    for (std::size_t n = 0; n <= 257; ++n) counts.push_back(n);
    for (auto n : {511u,512u,513u,1023u,1024u,1025u,4095u,4096u,4097u,65535u,65536u,65537u}) counts.push_back(n);
    ProtectedBuffer input(source.size()), output(source.size());
    require(input.available() && output.available(), "当前平台缺少保护页能力，不能宣称边界验收通过");
    for (const auto& kernel : kernels) {
        kernel.run(table, nullptr, nullptr, 0);
        for (auto count : counts) for (unsigned phase = 0; phase < 64; ++phase)
            aligned_case(kernel.run, table, source, expected, count, phase, (phase * 17 + 13) & 63);
        // 独立覆盖全部64×64输入/输出相位，避免只验证固定对齐关系。
        for (unsigned in = 0; in < 64; ++in) for (unsigned out = 0; out < 64; ++out)
            aligned_case(kernel.run, table, source, expected, 257, in, out);
        for (auto count : counts) {
            if (!count) continue;
            const auto bytes = count * 3;
            auto* src = input.tail(bytes); auto* dst = output.tail(bytes);
            std::memcpy(src, source.data(), bytes);
            // 末像素命中最后表项，向量读取和标量尾部均需遵守表guard契约。
            store3(src + bytes - 3, 0xffffffu);
            std::vector<std::uint8_t> exact(bytes); reference(table, src, exact.data(), count);
            kernel.run(table, src, dst, count);
            require(std::memcmp(dst, exact.data(), bytes) == 0, "输入/输出尾保护页分离结果错误");
            kernel.run(table, src, src, count);
            require(std::memcmp(src, exact.data(), bytes) == 0, "输入尾保护页原地结果错误");
            src = input.head(); dst = output.head(); std::memcpy(src, source.data(), bytes);
            kernel.run(table, src, dst, count);
            require(std::memcmp(dst, expected.data(), bytes) == 0, "输入/输出首保护页结果错误");
            comparisons += 3;
        }
    }
}
}
#endif

int main() {
#if !(FLASH_CHROMA_ENABLE_DIRECT && FLASH_CHROMA_ENABLE_AVX2)
    std::puts("本构建关闭direct或AVX2，RGB24快核合同未执行"); return 77;
#else
    if (!(fc::available_backends() & 2u)) { std::puts("CPU不支持AVX2，RGB24快核合同未执行"); return 77; }
    ProtectedBuffer memory(table_bytes + 4);
    if (!memory.available()) { std::puts("当前平台缺少保护页支持，RGB24合同未执行"); return 77; }
    auto* table = memory.tail(table_bytes + 4);
    // 奇数仿射置换恰有2^24种输出颜色，不能退化为U8/U16低调色板测试。
    for (std::size_t code = 0; code < colours; ++code)
        store3(table + code * 3, std::uint32_t(code * 0x5bd1e995u + 0xabcdefu) & 0xffffffu);
    const std::uint8_t guard[] = {0x7d, 0x3a, 0xb2, 0xe1};
    std::memcpy(table + table_bytes, guard, sizeof(guard));
    all_colours(table); boundary_cases(table);
    require(std::memcmp(table + table_bytes, guard, sizeof(guard)) == 0, "RGB24四字节guard被修改");
    for (std::size_t code = 0; code < colours; ++code) {
        const auto value = std::uint32_t(code * 0x5bd1e995u + 0xabcdefu) & 0xffffffu;
        require(table[code * 3] == std::uint8_t(value) && table[code * 3 + 1] == std::uint8_t(value >> 8) &&
                table[code * 3 + 2] == std::uint8_t(value >> 16), "RGB24表内容被修改");
    }
    std::printf("RGB24完整域与边界合同通过：%zu项比较；普通AVX2入口，无BMI要求\n", comparisons);
    return 0;
#endif
}
