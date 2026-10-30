/* 比赛框架的单线程适配：只用原始LUT做准备，不读取任何图像。
 * 一个翻译单元须在包含本文件前定义FLASH_CHROMA_IMPLEMENTATION。
 * Stage在Chain使用期间必须保持有效、地址稳定且内容不变。
 */
#ifndef FLASH_CHROMA_FRAMEWORK_ADAPTER_HPP
#define FLASH_CHROMA_FRAMEWORK_ADAPTER_HPP

#if defined(FLASH_CHROMA_ENABLE_OPENMP) && FLASH_CHROMA_ENABLE_OPENMP
#error "比赛框架禁止多线程；本适配不得启用OpenMP"
#endif
#ifndef FLASH_CHROMA_ENABLE_OPENMP
#define FLASH_CHROMA_ENABLE_OPENMP 0
#endif
#include "flash_chroma.hpp"
#include <array>
#include <algorithm>
#include <limits>
#include <stdexcept>
#include <vector>

namespace fc_framework {

constexpr std::size_t dense_nodes = std::size_t{256} * 256 * 256;
constexpr std::size_t dense_values = dense_nodes * 3;
enum class Grid { FrameworkStep, UniformRounded };
enum class Interpolation { TetraQ16, TrilinearQ16 };
struct FitOptions {
    Grid grid = Grid::UniformRounded;
    bool prove_structure = true;
    // 自定义三轴只由LUT预处理生成；空数组保持原来的固定网格。
    std::array<std::vector<unsigned>, 3> axes;
};

struct Stage {
    unsigned m = 0;
    std::vector<std::uint8_t> blob;
    std::vector<std::uint8_t> fractions;
    Interpolation interpolation = Interpolation::TetraQ16;
    bool separable_proven = false;
    std::array<std::array<std::uint8_t, 256>, 3> curves{};
    std::size_t proof_nodes = 0;
    std::size_t model_bytes() const noexcept { return blob.size() + fractions.size(); }
    std::size_t sidecar_bytes() const noexcept { return fractions.size() + (separable_proven ? 3u * 256u : 0u); }
    const std::uint8_t* nodes_data() const noexcept {
        return blob.empty() ? nullptr : blob.data() + 16u + 12u * m + 3840u;
    }
    std::size_t node_bytes() const noexcept { return std::size_t(m) * m * m * 3; }
};

namespace detail {
inline void put32(std::vector<std::uint8_t>& bytes, std::size_t at, std::uint32_t value) {
    for (unsigned i = 0; i != 4; ++i) bytes[at + i] = static_cast<std::uint8_t>(value >> (8 * i));
}
inline std::uint8_t source(const std::vector<std::uint16_t>& raw,
                           unsigned r, unsigned g, unsigned b, unsigned channel) noexcept {
    const std::size_t at = ((std::size_t(b) * 256 + g) * 256 + r) * 3 + 2 - channel;
    return static_cast<std::uint8_t>(raw[at] / 16);
}
inline bool overlaps(const void* a, std::size_t an, const void* b, std::size_t bn) noexcept {
    return fc_core::fc_detail_intersects(a, an, b, bn) != 0;
}
} // namespace detail

inline Stage prepare_stage(const std::vector<std::uint16_t>& raw, unsigned m,
                           FitOptions options = {}) {
    if (raw.size() != dense_values) throw std::invalid_argument("原始LUT必须含256³个三通道节点");
    if (m < 17 || m > 33) throw std::invalid_argument("每级稀疏尺寸必须在17..33内");
    if (options.grid != Grid::FrameworkStep && options.grid != Grid::UniformRounded)
        throw std::invalid_argument("未知网格策略");
    Stage result;
    result.m = m;
    result.separable_proven = options.prove_structure;
    if (options.prove_structure) {
        for (unsigned code = 0; code != 256; ++code) {
            result.curves[0][code] = detail::source(raw, code, 0, 0, 0);
            result.curves[1][code] = detail::source(raw, 0, code, 0, 1);
            result.curves[2][code] = detail::source(raw, 0, 0, code, 2);
        }
    }
    // 检查每个原节点，不以采样、文件名或样图代替结构证明。
    // 忠实保留框架的uint16除16再转uint8语义，包括大于4095时的回绕。
    if (options.prove_structure) for (unsigned b = 0; b != 256; ++b) for (unsigned g = 0; g != 256; ++g) {
        const auto* row = raw.data() + ((std::size_t(b) * 256 + g) * 256) * 3;
        for (unsigned r = 0; r != 256; ++r) {
            const auto v0 = static_cast<std::uint8_t>(row[r * 3] / 16);
            const auto v1 = static_cast<std::uint8_t>(row[r * 3 + 1] / 16);
            const auto v2 = static_cast<std::uint8_t>(row[r * 3 + 2] / 16);
            ++result.proof_nodes;
            if (v2 != result.curves[0][r] || v1 != result.curves[1][g] || v0 != result.curves[2][b])
                result.separable_proven = false;
        }
    }
    std::array<std::array<unsigned, 33>, 3> grids{};
    const bool custom = !options.axes[0].empty() || !options.axes[1].empty() || !options.axes[2].empty();
    for (unsigned a = 0; a != 3; ++a) {
        if (custom) {
            const auto& axis = options.axes[a];
            if (axis.size() != m || axis.front() != 0 || axis.back() != 255)
                throw std::invalid_argument("自定义轴必须有m个整数节点并包含0和255");
            for (unsigned i = 1; i != m; ++i) if (axis[i] <= axis[i-1] || axis[i] > 255)
                throw std::invalid_argument("自定义轴必须严格递增且在RGB8域内");
            std::copy(axis.begin(), axis.end(), grids[a].begin());
        } else {
            for (unsigned i = 0; i != m; ++i)
                grids[a][i] = options.grid == Grid::FrameworkStep ? i * (256 / (m - 1))
                    : (i * 255 + (m - 1) / 2) / (m - 1);
            grids[a][m - 1] = 255;
        }
    }
    const std::size_t nodes_at = 16u + 12u * m + 3840u;
    result.blob.resize(nodes_at + std::size_t(m) * m * m * 3);
    auto& bytes = result.blob;
    bytes[0] = 'S'; bytes[1] = 'L'; bytes[2] = 'U'; bytes[3] = 'T';
    detail::put32(bytes, 4, 1); detail::put32(bytes, 8, m);
    for (unsigned axis = 0; axis != 3; ++axis) {
        const auto& grid = grids[axis];
        for (unsigned i = 0; i != m; ++i) {
            const float value = static_cast<float>(grid[i]);
            std::uint32_t bits; std::memcpy(&bits, &value, 4);
            detail::put32(bytes, 16 + (axis * m + i) * 4, bits);
        }
        unsigned cell = 0;
        for (unsigned code = 0; code != 256; ++code) {
            while (cell + 1 < m - 1 && code >= grid[cell + 1]) ++cell;
            const unsigned span = grid[cell + 1] - grid[cell];
            const unsigned fraction = ((code - grid[cell]) * 65536u + span / 2) / span;
            bytes[16 + 12 * m + axis * 256 + code] = static_cast<std::uint8_t>(cell);
            detail::put32(bytes, 16 + 12 * m + 768 + (axis * 256 + code) * 4, fraction);
        }
    }
    for (unsigned r = 0; r != m; ++r) for (unsigned g = 0; g != m; ++g)
        for (unsigned b = 0; b != m; ++b) for (unsigned c = 0; c != 3; ++c)
            bytes[nodes_at + ((std::size_t(r) * m + g) * m + b) * 3 + c] =
                detail::source(raw, grids[0][r], grids[1][g], grids[2][b], c);
    fc_core::fc_model checked{};
    if (fc_core::fc_model_init(&checked, {bytes.data(), bytes.size()}, {nullptr, 0}) != fc_core::FC_OK)
        throw std::runtime_error("稀疏模型序列化未通过运行库校验");
    return result;
}

namespace detail {
inline fc_core::fc_bytes sidecar(const Stage& stage) noexcept {
    return {stage.fractions.empty() ? nullptr : stage.fractions.data(), stage.fractions.size()};
}
inline fc_core::fc_model view(const Stage& stage) {
    fc_core::fc_model result{};
    if ((stage.interpolation != Interpolation::TetraQ16 && stage.interpolation != Interpolation::TrilinearQ16) ||
        fc_core::fc_model_init(&result, {stage.blob.data(), stage.blob.size()}, sidecar(stage)) != fc_core::FC_OK || result.m != stage.m)
        throw std::invalid_argument("精度模型的节点、坐标或插值类型非法");
    return result;
}
inline std::uint32_t code(const std::uint8_t* c) noexcept {
    return std::uint32_t(c[0]) | (std::uint32_t(c[1]) << 8) | (std::uint32_t(c[2]) << 16);
}
// 两种插值都在每一级末尾只舍入一次；三线性使用精确48位权重。
inline std::uint32_t map(const fc_core::fc_model& m, Interpolation kind, std::uint32_t input) noexcept {
    const unsigned colour[3] = {input & 255u, (input >> 8) & 255u, input >> 16};
    const std::size_t stride[3] = {std::size_t(m.m)*m.m, m.m, 1};
    const std::size_t base = m.index[colour[0]]*stride[0] + m.index[256+colour[1]]*stride[1] + m.index[512+colour[2]];
    std::uint32_t output = 0;
    for (unsigned c = 0; c != 3; ++c) {
        const auto* table = m.sidecar.data ? m.sidecar.data + c*3072 : m.fraction_le;
        std::uint32_t f[3];
        for (unsigned a = 0; a != 3; ++a) f[a] = fc_core::fc_detail_read32(table + (a*256+colour[a])*4);
        std::uint64_t sum = 0;
        if (kind == Interpolation::TrilinearQ16) {
            for (unsigned mask = 0; mask != 8; ++mask) {
                std::size_t node = base; std::uint64_t weight = 1;
                for (unsigned a = 0; a != 3; ++a) {
                    const bool hi = (mask & (4u >> a)) != 0;
                    node += hi ? stride[a] : 0; weight *= hi ? f[a] : 65536u-f[a];
                }
                sum += weight*m.nodes[node*3+c];
            }
            output |= std::uint32_t((sum+(std::uint64_t{1}<<47))>>48) << (c*8);
        } else {
            std::size_t d[3] = {stride[0],stride[1],1};
            if(f[0]<f[1]){std::swap(f[0],f[1]);std::swap(d[0],d[1]);}
            if(f[1]<f[2]){std::swap(f[1],f[2]);std::swap(d[1],d[2]);}
            if(f[0]<f[1]){std::swap(f[0],f[1]);std::swap(d[0],d[1]);}
            sum = std::uint64_t(65536-f[0])*m.nodes[base*3+c] + std::uint64_t(f[0]-f[1])*m.nodes[(base+d[0])*3+c]
                + std::uint64_t(f[1]-f[2])*m.nodes[(base+d[0]+d[1])*3+c] + std::uint64_t(f[2])*m.nodes[(base+stride[0]+stride[1]+1)*3+c];
            output |= std::uint32_t((sum+32768)>>16) << (c*8);
        }
    }
    return output;
}
} // namespace detail

struct Options {
    fc::Backend backend = fc::Backend::Auto;
    fc::Representation representation = fc::Representation::Sparse;
    bool structure = true;
    unsigned threads = 1;
    std::size_t block_pixels = 65536;
    std::size_t max_workspace_bytes = 64 * fc::MiB;
};
struct Info {
    bool structured = false;
    fc::Backend backend = fc::Backend::Scalar;
    fc::Representation representation = fc::Representation::Sparse;
    unsigned threads = 1;
    std::size_t model_bytes = 0, sidecar_bytes = 0, arena_bytes = 0, object_bytes = 0;
    std::size_t proof_nodes = 0;
    std::uint32_t palette_entries = 0;
    // sidecar_bytes含model_bytes中的分输出坐标及object_bytes内曲线，不重复相加。
};

class Chain {
public:
    Chain() = default;
    Chain(const Chain&) = delete;
    Chain& operator=(const Chain&) = delete;
    Chain(Chain&&) = delete;
    Chain& operator=(Chain&&) = delete;

    fc::Status prepare(const std::array<const Stage*, 4>& stages, Options options = {}) {
        ready_ = false; info_ = {}; stages_ = {};
        mixed_ = false;
        std::vector<std::uint8_t>().swap(arena_);
        if (options.threads != 1) return fc::Status::Unsupported;
        if (!options.block_pixels) return fc::Status::Range;
        if (options.backend != fc::Backend::Auto && options.backend != fc::Backend::Scalar &&
            options.backend != fc::Backend::Avx2) return fc::Status::Unsupported;
        if (options.backend == fc::Backend::Avx2 && !(fc::available_backends() & 2u))
            return fc::Status::Unsupported;
        if (options.representation != fc::Representation::Sparse &&
            options.representation != fc::Representation::DirectU8 &&
            options.representation != fc::Representation::DirectU16 &&
            options.representation != fc::Representation::DirectRGB24) return fc::Status::Range;
        fc::ModelBundle bundle{};
        const fc_core::fc_model* pointers[4]{};
        bool structured = options.structure;
        for (unsigned i = 0; i != 4; ++i) {
            if (!stages[i]) return fc::Status::Null;
            const auto& stage = *stages[i];
            bundle.models[i] = {stage.blob.data(), stage.blob.size()};
            bundle.sidecars[i] = detail::sidecar(stage);
            const auto status = fc_core::fc_model_init(models_.data() + i, bundle.models[i], bundle.sidecars[i]);
            if (status != fc_core::FC_OK) return static_cast<fc::Status>(status);
            if (stage.m != models_[i].m) return fc::Status::Format;
            if (stage.interpolation != Interpolation::TetraQ16 && stage.interpolation != Interpolation::TrilinearQ16) return fc::Status::Format;
            mixed_ = mixed_ || stage.interpolation == Interpolation::TrilinearQ16;
            pointers[i] = models_.data() + i;
            structured = structured && stage.separable_proven && stage.proof_nodes == dense_nodes;
            info_.model_bytes += stage.model_bytes();
            info_.sidecar_bytes += stage.sidecar_bytes();
            info_.proof_nodes += stage.proof_nodes;
        }
        const auto status = fc_core::fc_chain_init(&validation_chain_, pointers);
        if (status != fc_core::FC_OK) return static_cast<fc::Status>(status);
        stages_ = stages;
        info_.object_bytes = sizeof(Chain) + 4 * sizeof(Stage);
        if (structured) {
            for (unsigned c = 0; c != 3; ++c) for (unsigned code = 0; code != 256; ++code) {
                unsigned value = code;
                for (const auto* stage : stages) value = stage->curves[c][value];
                composed_[c][code] = static_cast<std::uint8_t>(value);
            }
            info_.structured = true;
            info_.backend = fc::Backend::Scalar;
            info_.representation = fc::Representation::Sparse;
            info_.sidecar_bytes += 3 * 256;
            ready_ = true;
            return fc::Status::Ok;
        }
        if (mixed_) {
            if (options.representation != fc::Representation::Sparse && options.representation != fc::Representation::DirectRGB24)
                return fc::Status::Unsupported;
            info_.representation = options.representation;
            info_.backend = fc::Backend::Scalar;
            if (options.representation == fc::Representation::DirectRGB24) {
                const std::size_t bytes = dense_values + 4;
                if (bytes > options.max_workspace_bytes) return fc::Status::Budget;
                arena_.resize(bytes);
                for (std::uint32_t input = 0; input != dense_nodes; ++input) {
                    auto value = input;
                    for (unsigned s = 0; s != 4; ++s) value = detail::map(models_[s],stages_[s]->interpolation,value);
                    for(unsigned c=0;c!=3;++c)arena_[std::size_t(input)*3+c]=std::uint8_t(value>>(c*8));
                }
#if FLASH_CHROMA_ENABLE_AVX2
                if (options.backend != fc::Backend::Scalar && (fc::available_backends() & 2u)) info_.backend=fc::Backend::Avx2;
#endif
                info_.arena_bytes=arena_.size();
            }
            ready_=true;return fc::Status::Ok;
        }
        fc::RuntimeConfig config;
        config.threads = 1; config.backend = options.backend;
        config.representation = options.representation; config.block_pixels = options.block_pixels;
        config.max_workspace_bytes = options.max_workspace_bytes;
        fc::Requirements requirements;
        auto runtime_status = fc::Runtime::requirements(bundle, config, &requirements);
        if (runtime_status != fc::Status::Ok) return runtime_status;
        arena_.resize(requirements.arena_bytes);
        runtime_status = fc::Runtime::prepare(bundle, config, {arena_.data(), arena_.size()}, &runtime_);
        if (runtime_status != fc::Status::Ok) { std::vector<std::uint8_t>().swap(arena_); return runtime_status; }
        info_.backend = runtime_.selected_backend();
        info_.representation = config.representation;
        info_.arena_bytes = requirements.arena_bytes;
        info_.palette_entries = runtime_.palette_entries();
        ready_ = true;
        return fc::Status::Ok;
    }

    fc::Status apply(const std::uint8_t* input, std::uint8_t* output, std::size_t pixels) const noexcept {
        if (!ready_) return fc::Status::State;
        if (pixels > (std::numeric_limits<std::size_t>::max)() / 3) return fc::Status::Overflow;
        const std::size_t bytes = pixels * 3;
        const auto validation = fc_core::fc_validate_rgb8(&validation_chain_, input, bytes, bytes,
                                                         output, bytes, bytes, pixels, 1);
        if (validation != fc_core::FC_OK) return static_cast<fc::Status>(validation);
        if (!pixels) return fc::Status::Ok;
        if (detail::overlaps(output, bytes, this, sizeof(*this))) return fc::Status::Overlap;
        for (const Stage* stage : stages_)
            if (detail::overlaps(output, bytes, stage, sizeof(*stage))) return fc::Status::Overlap;
        if (!info_.structured && mixed_) {
            if(detail::overlaps(output,bytes,arena_.data(),arena_.size()))return fc::Status::Overlap;
#if FLASH_CHROMA_ENABLE_AVX2
            if(info_.representation==fc::Representation::DirectRGB24 && info_.backend==fc::Backend::Avx2){
                fc::detail::direct_rgb24_run(arena_.data(),input,output,pixels);return fc::Status::Ok;
            }
#endif
            for(std::size_t i=0;i<pixels;++i){
                auto value=detail::code(input+3*i);
                if(info_.representation==fc::Representation::DirectRGB24)value=detail::code(arena_.data()+std::size_t(value)*3);
                else for(unsigned s=0;s<4;++s)value=detail::map(models_[s],stages_[s]->interpolation,value);
                for(unsigned c=0;c<3;++c)output[3*i+c]=std::uint8_t(value>>(8*c));
            }
            return fc::Status::Ok;
        }
        if (!info_.structured)
            return runtime_.apply(input, bytes, bytes, output, bytes, bytes, pixels, 1);
        const auto* r = composed_[0].data();
        const auto* g = composed_[1].data();
        const auto* b = composed_[2].data();
        for (std::size_t i = 0; i != pixels; ++i) {
            output[i * 3] = r[input[i * 3]];
            output[i * 3 + 1] = g[input[i * 3 + 1]];
            output[i * 3 + 2] = b[input[i * 3 + 2]];
        }
        return fc::Status::Ok;
    }
    const Info& info() const noexcept { return info_; }
    bool ready() const noexcept { return ready_; }
private:
    bool ready_ = false;
    bool mixed_ = false;
    Info info_{};
    std::array<const Stage*, 4> stages_{};
    std::array<fc_core::fc_model, 4> models_{};
    fc_core::fc_chain validation_chain_{};
    std::array<std::array<std::uint8_t, 256>, 3> composed_{};
    std::vector<std::uint8_t> arena_;
    fc::Runtime runtime_;
};

} // namespace fc_framework
#endif
