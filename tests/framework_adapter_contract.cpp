/* 框架适配的独立合同：原uint16/轴序、完整结构证明、混合网格和失败语义。
 * 数据由解析公式产生，不使用比赛图片或具体LUT文件。
 */
#define FLASH_CHROMA_IMPLEMENTATION
#include "flash_chroma_adapter.hpp"
#include <cstdio>
#include <cstdlib>

namespace {
void check(bool passed, const char* message) {
    if (!passed) { std::fprintf(stderr, "框架适配合同失败：%s\n", message); std::exit(1); }
}
unsigned curve(unsigned stage, unsigned channel, unsigned x) {
    if (stage == 0) return channel == 0 ? (x * x + 127) / 255 : channel == 1 ? (x * 3 + 47) % 256 : 255 - x;
    if (stage == 1) return channel == 0 ? (std::min)(255u, (x * 3 + 1) / 2) : channel == 1 ? (x + 29) % 256 : x / 2;
    if (stage == 2) return channel == 0 ? (x ^ 85) : channel == 1 ? (x * x + 127) / 255 : (x * 5 + 11) % 256;
    return channel == 0 ? x / 2 + 31 : channel == 1 ? 255 - x : (x + 67) % 256;
}
unsigned coupled(unsigned stage, unsigned channel, unsigned r, unsigned g, unsigned b) {
    const unsigned a = 2 + stage, d = 3 + channel;
    if (channel == 0) return (a * r + d * g + b) / (a + d + 1);
    if (channel == 1) return (r + a * g + d * b) / (a + d + 1);
    return (d * r + g + a * b) / (a + d + 1);
}
void fill(std::vector<std::uint16_t>& raw, unsigned stage, bool separable) {
    for (unsigned b = 0; b != 256; ++b) for (unsigned g = 0; g != 256; ++g)
        for (unsigned r = 0; r != 256; ++r) {
            const unsigned rgb[3] = {r, g, b};
            for (unsigned c = 0; c != 3; ++c) {
                const auto value = separable ? curve(stage, c, rgb[c]) : coupled(stage, c, r, g, b);
                raw[((std::size_t(b) * 256 + g) * 256 + r) * 3 + 2 - c] =
                    static_cast<std::uint16_t>(value * 16 + ((r + g + b + c) & 15));
            }
        }
}
std::uint32_t read32(const std::uint8_t* p) {
    return std::uint32_t(p[0]) | (std::uint32_t(p[1]) << 8) |
           (std::uint32_t(p[2]) << 16) | (std::uint32_t(p[3]) << 24);
}
// 与被测C++/C99循环分开编写的u64重心算术，读取已序列化坐标和节点。
void oracle(const std::array<fc_framework::Stage, 4>& stages, const std::uint8_t* input, std::uint8_t* output) {
    unsigned rgb[3] = {input[0], input[1], input[2]};
    for (const auto& stage : stages) {
        const auto* index = stage.blob.data() + 16 + 12 * stage.m;
        const auto* fractions = index + 768;
        const auto* nodes = stage.nodes_data();
        std::size_t strides[3] = {std::size_t(stage.m) * stage.m, stage.m, 1};
        std::uint32_t f[3];
        std::size_t base = 0;
        for (unsigned axis = 0; axis != 3; ++axis) {
            base += strides[axis] * index[axis * 256 + rgb[axis]];
            f[axis] = read32(fractions + (axis * 256 + rgb[axis]) * 4);
        }
        for (unsigned i = 0; i != 2; ++i) for (unsigned j = i + 1; j != 3; ++j)
            if (f[j] > f[i]) { std::swap(f[i], f[j]); std::swap(strides[i], strides[j]); }
        const std::size_t positions[4] = {base, base + strides[0], base + strides[0] + strides[1],
                                          base + strides[0] + strides[1] + strides[2]};
        const std::uint32_t weights[4] = {65536 - f[0], f[0] - f[1], f[1] - f[2], f[2]};
        unsigned next[3]{};
        for (unsigned c = 0; c != 3; ++c) {
            std::uint64_t sum = 32768;
            for (unsigned vertex = 0; vertex != 4; ++vertex)
                sum += std::uint64_t(weights[vertex]) * nodes[positions[vertex] * 3 + c];
            next[c] = static_cast<unsigned>(sum >> 16);
        }
        for (unsigned c = 0; c != 3; ++c) rgb[c] = next[c];
    }
    for (unsigned c = 0; c != 3; ++c) output[c] = static_cast<std::uint8_t>(rgb[c]);
}
std::array<const fc_framework::Stage*, 4> pointers(const std::array<fc_framework::Stage, 4>& stages) {
    return {{&stages[0], &stages[1], &stages[2], &stages[3]}};
}
}

int main() {
    using namespace fc_framework;
    check((fc::compiled_capabilities() & 4u) == 0, "适配编译不含OpenMP能力");
    std::vector<std::uint16_t> raw(dense_values);
    std::array<Stage, 4> stages;
    const unsigned sizes[4] = {17, 18, 25, 33};
    for (unsigned i = 0; i != 4; ++i) {
        fill(raw, i, true);
        stages[i] = prepare_stage(raw, sizes[i]);
        check(stages[i].separable_proven && stages[i].proof_nodes == dense_nodes, "量化后全节点结构证明");
        check(stages[i].node_bytes() == std::size_t(sizes[i]) * sizes[i] * sizes[i] * 3, "保留真实m³节点");
    }
    std::vector<std::uint8_t> input(1031 * 3), expected(input.size()), output(input.size());
    for (std::size_t i = 0; i != input.size(); ++i) input[i] = static_cast<std::uint8_t>(i * 73 + 19);
    for (std::size_t i = 0; i != input.size(); i += 3) for (unsigned c = 0; c != 3; ++c) {
        unsigned value = input[i + c];
        for (unsigned stage = 0; stage != 4; ++stage) value = curve(stage, c, value);
        expected[i + c] = static_cast<std::uint8_t>(value);
    }
    Chain chain;
    check(chain.prepare(pointers(stages)) == fc::Status::Ok && chain.info().structured, "准备精确曲线链");
    check(chain.apply(input.data(), output.data(), input.size() / 3) == fc::Status::Ok && output == expected,
          "结构链匹配独立解析公式，覆盖所有256码及短尾");
    auto in_place = input;
    check(chain.apply(in_place.data(), in_place.data(), in_place.size() / 3) == fc::Status::Ok && in_place == expected, "精确原地");
    auto unchanged = input;
    check(chain.apply(input.data(), input.data() + 1, 100) == fc::Status::Overlap && input == unchanged, "部分重叠拒绝");
    check(chain.apply(nullptr, nullptr, 0) == fc::Status::Ok, "空图无操作");
    check(chain.apply(nullptr, output.data(), 1) == fc::Status::Null, "空源拒绝");
    check(chain.apply(input.data(), output.data(), (std::numeric_limits<std::size_t>::max)() / 3 + 1) == fc::Status::Overflow, "像素尺寸溢出拒绝");
    Options invalid; invalid.threads = 2;
    check(chain.prepare(pointers(stages), invalid) == fc::Status::Unsupported && !chain.ready(), "任何多线程请求拒绝并失效");
    check(chain.apply(input.data(), output.data(), 1) == fc::Status::State, "准备失败后不得执行旧链");

    // 非采样节点的一次扰动也必须使全表证明失败。
    fill(raw, 0, true);
    Stage before = prepare_stage(raw, 17);
    raw[((std::size_t(197) * 256 + 131) * 256 + 73) * 3 + 2] ^= 16;
    Stage changed = prepare_stage(raw, 17);
    check(!changed.separable_proven && changed.proof_nodes == dense_nodes && changed.blob == before.blob,
          "未采样节点的结构反例不可漏过");

    // 原参考使用uint16/16后uint8转换，4096与65535不能被误钳制。
    std::fill(raw.begin(), raw.end(), 0);
    for (std::size_t node = 0; node != dense_nodes; ++node) {
        raw[node * 3] = 4095; raw[node * 3 + 1] = 4096; raw[node * 3 + 2] = 65535;
    }
    const Stage boundary = prepare_stage(raw, 17);
    check(boundary.separable_proven && boundary.curves[0][23] == 255 && boundary.curves[1][23] == 0 &&
          boundary.curves[2][23] == 255, "uint16量化边界与通道反序");
    check(boundary.nodes_data()[0] == 255 && boundary.nodes_data()[1] == 0 && boundary.nodes_data()[2] == 255,
          "节点同步保留截断与回绕");

    for (unsigned i = 0; i != 4; ++i) {
        fill(raw, i, false);
        FitOptions fit; fit.grid = i % 2 ? Grid::FrameworkStep : Grid::UniformRounded;
        stages[i] = prepare_stage(raw, sizes[i], fit);
        check(!stages[i].separable_proven, "交叉通道源不得使用精确曲线");
        const unsigned end = sizes[i] - 1;
        const auto* corner = stages[i].nodes_data() + ((std::size_t(end) * sizes[i] + end) * sizes[i] + end) * 3;
        check(corner[0] == 255 && corner[1] == 255 && corner[2] == 255, "两种网格覆盖255端点");
    }
    for (std::size_t i = 0; i != input.size(); i += 3) oracle(stages, input.data() + i, expected.data() + i);
    Options scalar; scalar.backend = fc::Backend::Scalar;
    check(chain.prepare(pointers(stages), scalar) == fc::Status::Ok && !chain.info().structured, "非可分离表自动通用回退");
    check(chain.apply(input.data(), output.data(), input.size() / 3) == fc::Status::Ok && output == expected, "混合m标量匹配独立u64四面体");
    if (fc::available_backends() & 2u) {
        Options avx2; avx2.backend = fc::Backend::Avx2;
        check(chain.prepare(pointers(stages), avx2) == fc::Status::Ok && chain.info().backend == fc::Backend::Avx2, "运行时AVX2可用");
        check(chain.apply(input.data(), output.data(), input.size() / 3) == fc::Status::Ok && output == expected, "AVX2匹配独立u64四面体");
        avx2.max_workspace_bytes = 0;
        check(chain.prepare(pointers(stages), avx2) == fc::Status::Budget && !chain.ready(), "工作区预算严格拒绝");
    }
    Options disabled; disabled.structure = false; disabled.backend = fc::Backend::Scalar;
    check(chain.prepare(pointers(stages), disabled) == fc::Status::Ok && !chain.info().structured, "结构路径可显式关闭");
    check(prepare_stage(raw, 17, {Grid::FrameworkStep, false}).proof_nodes == 0, "禁证明不伪造全域证明记录");
    bool rejected = false;
    try { (void)prepare_stage(raw, 16); } catch (const std::invalid_argument&) { rejected = true; }
    check(rejected, "尺寸16拒绝");
    rejected = false;
    try { (void)prepare_stage(std::vector<std::uint16_t>{0}, 17); } catch (const std::invalid_argument&) { rejected = true; }
    check(rejected, "截断原表拒绝");
    std::puts("框架适配合同通过：独立解析曲线、全节点反例、uint16边界、混合网格u64/标量/AVX2及单线程拒绝");
    return 0;
}
