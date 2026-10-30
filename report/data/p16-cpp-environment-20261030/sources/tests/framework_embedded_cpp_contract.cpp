/* 同一C++单头文件的嵌入式合同：只读ROM模型、调用者缓冲、四级解析映射。
 * 不包含C交付头，不使用容器、堆、异常、RTTI、文件或标准输出。
 * 独立聚合合同通过FC_TEST_FRAMEWORK_HPP选择实际导出的唯一hpp。
 */
#ifndef FC_TEST_FRAMEWORK_HPP
#define FC_TEST_FRAMEWORK_HPP "flash_chroma.hpp"
#endif
#define FLASH_CHROMA_IMPLEMENTATION
#include FC_TEST_FRAMEWORK_HPP

#define CHECK(value) do { if (!(value)) return __LINE__; } while (false)

static_assert(FLASH_CHROMA_TARGET == FLASH_CHROMA_TARGET_EMBEDDED, "嵌入式别名未设置目标");
static_assert(fc::is_embedded(), "嵌入式C++查询接口必须反映编译目标");
static_assert(FLASH_CHROMA_ENABLE_AVX2 == 0, "嵌入式必须裁剪AVX2");
static_assert(FLASH_CHROMA_ENABLE_OPENMP == 0, "嵌入式必须裁剪OpenMP");
static_assert(FLASH_CHROMA_ENABLE_DIRECT == 0, "嵌入式必须裁剪Direct");
static_assert(FLASH_CHROMA_ENABLE_PREPARE_CACHE == 0, "嵌入式必须裁剪准备缓存");

namespace {
constexpr unsigned m = 17;
constexpr std::size_t model_bytes = 16 + 12 * m + 3840 + 3 * m * m * m;
struct RomModel { std::uint8_t bytes[model_bytes]{}; };
constexpr void put32(RomModel& model, std::size_t at, std::uint32_t value) {
    for (unsigned i = 0; i < 4; ++i) model.bytes[at + i] = static_cast<std::uint8_t>(value >> (i * 8));
}
constexpr std::uint32_t float_bits(unsigned value) {
    if (!value) return 0;
    unsigned exponent = 150;
    while (value < (1u << 23)) { value <<= 1; --exponent; }
    return (exponent << 23) | (value & 0x7fffff);
}
constexpr unsigned knot(unsigned index) { return index == 16 ? 255 : index * 16; }
constexpr RomModel make_model(unsigned stage) {
    RomModel model{};
    model.bytes[0] = 'S'; model.bytes[1] = 'L'; model.bytes[2] = 'U'; model.bytes[3] = 'T';
    put32(model, 4, 1); put32(model, 8, m);
    constexpr std::size_t indices = 16 + 12 * m, fractions = indices + 768, nodes = fractions + 3072;
    for (unsigned axis = 0; axis < 3; ++axis) {
        for (unsigned i = 0; i < m; ++i) put32(model, 16 + 4 * (axis * m + i), float_bits(knot(i)));
        for (unsigned code = 0; code < 256; ++code) {
            unsigned cell = 0;
            while (cell < m - 2 && knot(cell + 1) <= code) ++cell;
            const unsigned width = knot(cell + 1) - knot(cell);
            model.bytes[indices + axis * 256 + code] = static_cast<std::uint8_t>(cell);
            put32(model, fractions + 4 * (axis * 256 + code), ((code - knot(cell)) * 65536 + width / 2) / width);
        }
    }
    for (unsigned r = 0; r < m; ++r) for (unsigned g = 0; g < m; ++g) for (unsigned b = 0; b < m; ++b) {
        const unsigned input[3] = {knot(r), knot(g), knot(b)};
        unsigned output[3]{};
        if (stage == 0) { output[0] = input[1]; output[1] = input[2]; output[2] = input[0]; }
        if (stage == 1) { output[0] = 255 - input[0]; output[1] = input[1]; output[2] = 255 - input[2]; }
        if (stage == 2) { output[0] = input[2]; output[1] = 255 - input[0]; output[2] = input[1]; }
        if (stage == 3) { output[0] = 255 - input[2]; output[1] = input[0]; output[2] = input[1]; }
        const auto at = nodes + ((r * m + g) * m + b) * 3;
        for (unsigned channel = 0; channel < 3; ++channel) model.bytes[at + channel] = static_cast<std::uint8_t>(output[channel]);
    }
    return model;
}
// 编译时生成只读模型；运行时没有初始化代码、源表、节点复制或堆申请。
constexpr RomModel rom[4] = {make_model(0), make_model(1), make_model(2), make_model(3)};
constexpr std::size_t capacity = (257 * 3 + 5) * 3 + 2;
std::uint8_t source[capacity], destination[capacity], in_place[capacity], expected[capacity];
void fill(std::uint8_t* bytes, std::uint8_t value) {
    for (std::size_t i = 0; i < capacity; ++i) bytes[i] = value;
}
bool equal(const std::uint8_t* left, const std::uint8_t* right) {
    for (std::size_t i = 0; i < capacity; ++i) if (left[i] != right[i]) return false;
    return true;
}
}

int main() {
    CHECK(fc::compiled_capabilities() == 1u && fc::available_backends() == 1u);
    fc::ModelBundle bundle{};
    for (unsigned stage = 0; stage < 4; ++stage) bundle.models[stage] = {rom[stage].bytes, model_bytes};
    fc::RuntimeConfig config;
    CHECK(config.target == fc::Target::Embedded && config.threads == 1);
    config.backend = fc::Backend::Scalar; config.max_workspace_bytes = 0; config.block_pixels = 13;
    fc::Requirements resources;
    CHECK(fc::Runtime::requirements(bundle, config, &resources) == fc::Status::Ok);
    CHECK(resources.arena_bytes == 0 && resources.persistent_bytes == 0 && resources.temporary_bytes == 0);
    CHECK(resources.model_bytes == 4 * model_bytes);
    fc::Runtime runtime;
    CHECK(fc::Runtime::prepare(bundle, config, {nullptr, 0}, &runtime) == fc::Status::Ok);
    CHECK(runtime.ready() && runtime.selected_backend() == fc::Backend::Scalar);
    CHECK(runtime.config().target == fc::Target::Embedded && !runtime.prepared_with_suffix_cache());

    // 每级是轴置换或反色，完整四级独立解析结果为(255-B,255-R,G)。
    // 浮点网格不参与oracle；Q16量化误差小于半LSB，因此每码恢复整数恒等映射。
    const unsigned widths[] = {1,2,7,8,15,16,17,31,32,33,63,64,65,255,257};
    for (unsigned width : widths) {
        const std::size_t stride = width * 3 + 5;
        fill(source, 0x6a); fill(destination, 0xa5); fill(expected, 0xa5);
        for (unsigned y = 0; y < 3; ++y) for (unsigned x = 0; x < width; ++x) {
            const auto at = 1 + y * stride + x * 3;
            source[at] = static_cast<std::uint8_t>(x + 11 * y);
            source[at + 1] = static_cast<std::uint8_t>(73 * x + 19 * y);
            source[at + 2] = static_cast<std::uint8_t>(127 * x + 31 * y);
            expected[at] = static_cast<std::uint8_t>(255 - source[at + 2]);
            expected[at + 1] = static_cast<std::uint8_t>(255 - source[at]);
            expected[at + 2] = source[at + 1];
        }
        CHECK(runtime.apply(source + 1, capacity - 2, stride, destination + 1, capacity - 2, stride, width, 3) == fc::Status::Ok);
        CHECK(equal(destination, expected));
        for (std::size_t i = 0; i < capacity; ++i) in_place[i] = source[i];
        CHECK(runtime.apply(in_place + 1, capacity - 2, stride, in_place + 1, capacity - 2, stride, width, 3) == fc::Status::Ok);
        for (std::size_t i = 0; i < capacity; ++i) {
            const bool pixel = i > 0 && (i - 1) / stride < 3 && (i - 1) % stride < width * 3;
            CHECK(in_place[i] == (pixel ? expected[i] : source[i]));
        }
    }
    CHECK(runtime.apply(nullptr, 0, 0, nullptr, 0, 0, 0, 1) == fc::Status::Ok);
    CHECK(runtime.apply(source + 1, capacity - 2, 30, source + 2, capacity - 3, 30, 10, 1) == fc::Status::Overlap);

    // 显式要求被裁剪能力时失败，不能假装满足请求后悄悄回退。
    const fc::Representation representations[] = {fc::Representation::DirectU8, fc::Representation::DirectU16, fc::Representation::DirectRGB24};
    for (auto representation : representations) {
        auto invalid = config; invalid.representation = representation;
        CHECK(fc::Runtime::requirements(bundle, invalid, &resources) == fc::Status::Unsupported);
    }
    const fc::Backend backends[] = {fc::Backend::Avx2, fc::Backend::Avx512};
    for (auto backend : backends) {
        auto invalid = config; invalid.backend = backend;
        CHECK(fc::Runtime::requirements(bundle, invalid, &resources) == fc::Status::Unsupported);
    }
    const fc::Target targets[] = {fc::Target::Desktop, fc::Target::Mobile};
    for (auto target : targets) {
        auto invalid = config; invalid.target = target;
        CHECK(fc::Runtime::requirements(bundle, invalid, &resources) == fc::Status::Unsupported);
    }
    auto invalid = config; invalid.threads = 2;
    CHECK(fc::Runtime::requirements(bundle, invalid, &resources) == fc::Status::Unsupported);

    // 保留C++连续选择器，但不为未计时的嵌入式模型伪造性能证据。
    fc::Candidate candidate;
    candidate.id = "rom"; candidate.context = "embedded-contract"; candidate.model_id = "four-rom-models";
    candidate.evidence = "解析固定值合同"; candidate.config = config;
    candidate.mean_error = candidate.worst_image_mean = 0;
    candidate.runtime_bytes = 4 * model_bytes + sizeof(fc::Runtime);
    candidate.correctness_verified = candidate.accuracy_verified = candidate.resources_verified = true;
    fc::Request request; request.context = candidate.context; request.target = fc::Target::Embedded;
    request.preference = {1,0,0}; request.use_time = false; request.backend_mask = 1; request.max_threads = 1;
    fc::SelectionView selection;
    CHECK(fc::select(&candidate, 1, request, &selection) == fc::SelectionStatus::Ok);
    CHECK(selection.index == 0 && selection.provisional);
    return 0;
}
