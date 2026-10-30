/* 图像无关的完整RGB域Q16四面体最小二乘实验。
 * 只修改Stage的m³节点；轴表、执行库及精确曲线证明保持原样。
 * 此文件目前是独立候选，不自动替换比赛适配器的采样路径。
 */
#ifndef FLASH_CHROMA_FRAMEWORK_FIT_EXPERIMENT_HPP
#define FLASH_CHROMA_FRAMEWORK_FIT_EXPERIMENT_HPP
#include "flash_chroma_adapter.hpp"
#include <cmath>
#include <chrono>

namespace fc_framework {
struct FitExperimentOptions {
    unsigned cg_max_iterations = 160;
    unsigned integer_sweeps = 8;
    double relative_tolerance = 1e-8;
    double regularization = 1e-5;
    bool guard_full_domain = true;
};
struct FitChannelReport {
    unsigned iterations = 0;
    double relative_residual = 0;
    bool converged = false;
};
struct FitError {
    std::uint64_t sse = 0;
    double mean = 0, linear_sse = 0;
    unsigned max_squared = 0;
};
struct FitReport {
    unsigned m = 0;
    std::size_t samples = 0, matrix_bytes = 0, temporary_bytes = 0;
    unsigned integer_sweeps = 0;
    std::size_t changed_nodes = 0;
    bool source_separable_skipped = false, candidate_used = false;
    std::array<FitChannelReport, 3> channels{};
    FitError baseline{}, candidate{};
    double linear_sse_before = 0, linear_sse_after = 0;
    double assembly_seconds = 0, solve_seconds = 0, evaluation_seconds = 0;
};

namespace fit_detail {
inline double seconds() {
    return std::chrono::duration<double>(std::chrono::steady_clock::now().time_since_epoch()).count();
}
inline std::uint32_t u32(const std::uint8_t* p) {
    return std::uint32_t(p[0]) | (std::uint32_t(p[1]) << 8) |
           (std::uint32_t(p[2]) << 16) | (std::uint32_t(p[3]) << 24);
}
struct Geometry {
    std::size_t node[4]{};
    unsigned mask[4]{};
    std::uint32_t weight[4]{};
};
struct Coordinates {
    std::array<std::array<unsigned, 256>, 3> index{};
    std::array<std::array<std::uint32_t, 256>, 3> fraction{};
    std::array<std::size_t, 8> delta{};
    unsigned m = 0;
    explicit Coordinates(const Stage& stage) : m(stage.m) {
        fc_core::fc_model checked{};
        if (fc_core::fc_model_init(&checked, {stage.blob.data(), stage.blob.size()}, {nullptr, 0}) != fc_core::FC_OK || checked.m != stage.m)
            throw std::invalid_argument("完整域拟合的初始Stage非法");
        for (unsigned a = 0; a != 3; ++a) for (unsigned v = 0; v != 256; ++v) {
            index[a][v] = checked.index[a * 256 + v];
            fraction[a][v] = u32(checked.fraction_le + (a * 256 + v) * 4);
        }
        for (unsigned mask = 0; mask != 8; ++mask)
            delta[mask] = ((mask & 4) ? std::size_t(m) * m : 0) + ((mask & 2) ? m : 0) + ((mask & 1) ? 1 : 0);
    }
    Geometry at(unsigned r, unsigned g, unsigned b) const {
        const std::size_t base = (std::size_t(index[0][r]) * m + index[1][g]) * m + index[2][b];
        std::uint32_t f[3] = {fraction[0][r], fraction[1][g], fraction[2][b]};
        unsigned mask[3] = {4, 2, 1};
        if (f[0] < f[1]) { std::swap(f[0], f[1]); std::swap(mask[0], mask[1]); }
        if (f[1] < f[2]) { std::swap(f[1], f[2]); std::swap(mask[1], mask[2]); }
        if (f[0] < f[1]) { std::swap(f[0], f[1]); std::swap(mask[0], mask[1]); }
        Geometry result;
        result.mask[0] = 0; result.mask[1] = mask[0]; result.mask[2] = mask[0] | mask[1]; result.mask[3] = 7;
        for (unsigned i = 0; i != 4; ++i) result.node[i] = base + delta[result.mask[i]];
        result.weight[0] = 65536 - f[0]; result.weight[1] = f[0] - f[1];
        result.weight[2] = f[1] - f[2]; result.weight[3] = f[2];
        return result;
    }
};

// 同一四面体任意两个顶点的位移仅含同号的轴步长，故每行只需15个邻居。
// 只存对角及7个正向邻居，上三角总量m³*8，矩阵乘法对称更新另半边。
struct Normal {
    std::size_t count;
    std::array<std::size_t, 8> delta;
    std::vector<std::array<double, 8>> h;
    std::vector<std::array<double, 3>> rhs;
    double target_squared_sum = 0;
    explicit Normal(const Coordinates& coordinates)
        : count(std::size_t(coordinates.m) * coordinates.m * coordinates.m), delta(coordinates.delta), h(count), rhs(count) {}
    void multiply(const std::vector<double>& x, std::vector<double>& out,
                  const std::vector<double>& regularizer) const {
        out.resize(count);
        for (std::size_t i = 0; i != count; ++i) out[i] = (h[i][0] + regularizer[i]) * x[i];
        for (std::size_t i = 0; i != count; ++i) for (unsigned k = 1; k != 8; ++k) {
            const double value = h[i][k];
            if (value == 0) continue;
            const std::size_t j = i + delta[k];
            if (j >= count) throw std::runtime_error("正规矩阵邻接越界");
            out[i] += value * x[j]; out[j] += value * x[i];
        }
    }
    double row_off_diagonal(std::size_t i, const std::vector<std::array<double, 3>>& x, unsigned channel) const {
        double sum = 0;
        for (unsigned k = 1; k != 8; ++k) {
            const std::size_t step = delta[k];
            if (i + step < count) sum += h[i][k] * x[i + step][channel];
            if (i >= step) sum += h[i - step][k] * x[i - step][channel];
        }
        return sum;
    }
    double sse(const std::vector<std::array<double, 3>>& x) const {
        double result = target_squared_sum;
        for (std::size_t i = 0; i != count; ++i) for (unsigned c = 0; c != 3; ++c) {
            result += h[i][0] * x[i][c] * x[i][c] - 2 * rhs[i][c] * x[i][c];
            for (unsigned k = 1; k != 8; ++k) if (i + delta[k] < count)
                result += 2 * h[i][k] * x[i][c] * x[i + delta[k]][c];
        }
        return result;
    }
};

inline void assemble(const std::vector<std::uint16_t>& raw, const Coordinates& coordinates, Normal& matrix) {
    constexpr double inverse = 1.0 / 65536.0;
    for (unsigned b = 0; b != 256; ++b) for (unsigned g = 0; g != 256; ++g) {
        const auto* row = raw.data() + ((std::size_t(b) * 256 + g) * 256) * 3;
        for (unsigned r = 0; r != 256; ++r) {
            const auto geometry = coordinates.at(r, g, b);
            const unsigned target[3] = {static_cast<std::uint8_t>(row[r * 3 + 2] / 16),
                                        static_cast<std::uint8_t>(row[r * 3 + 1] / 16),
                                        static_cast<std::uint8_t>(row[r * 3] / 16)};
            for (unsigned c = 0; c != 3; ++c) matrix.target_squared_sum += double(target[c]) * target[c];
            for (unsigned i = 0; i != 4; ++i) {
                const double own = geometry.weight[i] * inverse;
                if (own == 0) continue;
                for (unsigned c = 0; c != 3; ++c) matrix.rhs[geometry.node[i]][c] += own * target[c];
                for (unsigned j = i; j != 4; ++j) {
                    const unsigned edge = geometry.mask[i] ^ geometry.mask[j];
                    matrix.h[geometry.node[i]][edge] += own * (geometry.weight[j] * inverse);
                }
            }
        }
    }
}

inline double dot(const std::vector<double>& a, const std::vector<double>& b) {
    double value = 0;
    for (std::size_t i = 0; i != a.size(); ++i) value += a[i] * b[i];
    return value;
}
inline std::vector<double> solve_channel(const Normal& matrix, unsigned channel,
                                        const std::vector<std::array<double, 3>>& initial,
                                        const FitExperimentOptions& options, FitChannelReport& report) {
    const auto n = matrix.count;
    std::vector<double> x(n), rhs(n), reg(n), r(n), z(n), direction(n), product(n);
    for (std::size_t i = 0; i != n; ++i) {
        x[i] = initial[i][channel]; reg[i] = options.regularization * (matrix.h[i][0] + 1);
        rhs[i] = matrix.rhs[i][channel] + reg[i] * x[i];
    }
    matrix.multiply(x, product, reg);
    for (std::size_t i = 0; i != n; ++i) {
        r[i] = rhs[i] - product[i];
        z[i] = r[i] / (matrix.h[i][0] + reg[i]); direction[i] = z[i];
    }
    const double rhs_squared = dot(rhs, rhs);
    const double target = options.relative_tolerance * options.relative_tolerance * (std::max)(rhs_squared, 1e-60);
    double rz = dot(r, z);
    for (unsigned step = 0; step != options.cg_max_iterations && dot(r, r) > target; ++step) {
        matrix.multiply(direction, product, reg);
        const double denominator = dot(direction, product);
        if (!(denominator > 0) || !std::isfinite(denominator) || !std::isfinite(rz))
            throw std::runtime_error("完整域CG遇到非正或非有限方向");
        const double alpha = rz / denominator;
        for (std::size_t i = 0; i != n; ++i) { x[i] += alpha * direction[i]; r[i] -= alpha * product[i]; }
        ++report.iterations;
        if (dot(r, r) <= target) break;
        for (std::size_t i = 0; i != n; ++i) z[i] = r[i] / (matrix.h[i][0] + reg[i]);
        const double next = dot(r, z), beta = next / rz;
        for (std::size_t i = 0; i != n; ++i) direction[i] = z[i] + beta * direction[i];
        rz = next;
    }
    // 最终残差用原矩阵重新计算，不能只信递推残差或迭代退出。
    matrix.multiply(x, product, reg);
    for (std::size_t i = 0; i != n; ++i) r[i] = rhs[i] - product[i];
    report.relative_residual = std::sqrt(dot(r, r) / (std::max)(rhs_squared, 1e-60));
    report.converged = std::isfinite(report.relative_residual) && report.relative_residual <= options.relative_tolerance * 2;
    if (!report.converged) throw std::runtime_error("完整域CG未达到预设残差阈值，候选不发布");
    return x;
}
inline unsigned integer(double value) {
    if (!std::isfinite(value)) throw std::runtime_error("拟合节点非有限");
    return static_cast<unsigned>((std::max)(0.0, (std::min)(255.0, std::floor(value + .5))));
}
inline void evaluate(const std::vector<std::uint16_t>& raw, const Coordinates& coordinates,
                     const std::uint8_t* baseline, const std::uint8_t* candidate,
                     FitError& before, FitError& after) {
    for (unsigned b = 0; b != 256; ++b) for (unsigned g = 0; g != 256; ++g) {
        const auto* row = raw.data() + ((std::size_t(b) * 256 + g) * 256) * 3;
        for (unsigned r = 0; r != 256; ++r) {
            const auto geometry = coordinates.at(r, g, b);
            unsigned squared[2]{};
            double linear_squared[2]{};
            for (unsigned c = 0; c != 3; ++c) {
                std::uint64_t sums[2] = {32768, 32768};
                for (unsigned i = 0; i != 4; ++i) {
                    sums[0] += std::uint64_t(geometry.weight[i]) * baseline[geometry.node[i] * 3 + c];
                    sums[1] += std::uint64_t(geometry.weight[i]) * candidate[geometry.node[i] * 3 + c];
                }
                const int target = static_cast<std::uint8_t>(row[r * 3 + 2 - c] / 16);
                for (unsigned variant = 0; variant != 2; ++variant) {
                    const int error = static_cast<int>(sums[variant] >> 16) - target;
                    squared[variant] += static_cast<unsigned>(error * error);
                    const double linear_error = double(sums[variant] - 32768) / 65536 - target;
                    linear_squared[variant] += linear_error * linear_error;
                }
            }
            before.sse += squared[0]; after.sse += squared[1];
            before.linear_sse += linear_squared[0]; after.linear_sse += linear_squared[1];
            before.mean += std::sqrt(double(squared[0])); after.mean += std::sqrt(double(squared[1]));
            before.max_squared = (std::max)(before.max_squared, squared[0]);
            after.max_squared = (std::max)(after.max_squared, squared[1]);
        }
    }
    before.mean /= dense_nodes; after.mean /= dense_nodes;
}
} // namespace fit_detail

inline Stage fit_full(const std::vector<std::uint16_t>& raw, const Stage& initial, FitReport& report,
                      FitExperimentOptions options = {}) {
    report = {}; report.m = initial.m;
    if (raw.size() != dense_values) throw std::invalid_argument("完整域拟合要求256³三通道uint16源");
    if (!options.cg_max_iterations || options.cg_max_iterations > 1000 || options.integer_sweeps > 64 ||
        !std::isfinite(options.regularization) || options.regularization <= 0 ||
        !std::isfinite(options.relative_tolerance) || options.relative_tolerance <= 0 || options.relative_tolerance >= 1)
        throw std::invalid_argument("完整域拟合参数非法");
    const fit_detail::Coordinates coordinates(initial);
    if (initial.separable_proven && initial.proof_nodes == dense_nodes) {
        report.source_separable_skipped = true;
        return initial;
    }
    Stage result = initial;
    const double start = fit_detail::seconds();
    fit_detail::Normal matrix(coordinates);
    fit_detail::assemble(raw, coordinates, matrix);
    report.samples = dense_nodes;
    report.matrix_bytes = matrix.h.size() * sizeof(matrix.h[0]);
    report.temporary_bytes = report.matrix_bytes + matrix.rhs.size() * sizeof(matrix.rhs[0]) +
                             matrix.count * (3 * 2 + 7) * sizeof(double) + sizeof(coordinates);
    report.assembly_seconds = fit_detail::seconds() - start;
    std::vector<std::array<double, 3>> first(matrix.count), solution(matrix.count);
    for (std::size_t i = 0; i != matrix.count; ++i) for (unsigned c = 0; c != 3; ++c)
        first[i][c] = initial.nodes_data()[i * 3 + c];
    report.linear_sse_before = matrix.sse(first);
    const double solve_start = fit_detail::seconds();
    for (unsigned c = 0; c != 3; ++c) {
        const auto channel = fit_detail::solve_channel(matrix, c, first, options, report.channels[c]);
        for (std::size_t i = 0; i != matrix.count; ++i) solution[i][c] = fit_detail::integer(channel[i]);
    }
    // 固定最大次数的整数坐标下降，目标是同一个完整域正规方程，不看图像。
    for (unsigned sweep = 0; sweep != options.integer_sweeps; ++sweep) {
        std::size_t changed = 0;
        for (std::size_t i = 0; i != matrix.count; ++i) for (unsigned c = 0; c != 3; ++c) {
            const double reg = options.regularization * (matrix.h[i][0] + 1);
            const double next = fit_detail::integer((matrix.rhs[i][c] + reg * first[i][c] -
                    matrix.row_off_diagonal(i, solution, c)) / (matrix.h[i][0] + reg));
            changed += next != solution[i][c]; solution[i][c] = next;
        }
        ++report.integer_sweeps;
        if (!changed) break;
    }
    report.linear_sse_after = matrix.sse(solution);
    auto* nodes = result.blob.data() + (result.nodes_data() - result.blob.data());
    for (std::size_t i = 0; i != matrix.count; ++i) {
        bool changed = false;
        for (unsigned c = 0; c != 3; ++c) {
            nodes[i * 3 + c] = static_cast<std::uint8_t>(solution[i][c]);
            changed = changed || nodes[i * 3 + c] != initial.nodes_data()[i * 3 + c];
        }
        report.changed_nodes += changed;
    }
    report.solve_seconds = fit_detail::seconds() - solve_start;
    const double evaluate_start = fit_detail::seconds();
    fit_detail::evaluate(raw, coordinates, initial.nodes_data(), result.nodes_data(), report.baseline, report.candidate);
    // 独立逐点线性误差应与正规矩阵二次型一致，用来审计稀疏邻接装配。
    const auto matches = [](double direct, double matrix_value) {
        return std::abs(direct - matrix_value) <= (std::max)(1.0, direct * 1e-8);
    };
    if (!matches(report.baseline.linear_sse, report.linear_sse_before) ||
        !matches(report.candidate.linear_sse, report.linear_sse_after))
        throw std::runtime_error("完整域逐点误差与正规矩阵二次型不一致，候选不发布");
    report.evaluation_seconds = fit_detail::seconds() - evaluate_start;
    report.candidate_used = !options.guard_full_domain ||
        (report.candidate.sse <= report.baseline.sse && report.candidate.mean <= report.baseline.mean);
    return report.candidate_used ? result : initial;
}
} // namespace fc_framework
#endif
