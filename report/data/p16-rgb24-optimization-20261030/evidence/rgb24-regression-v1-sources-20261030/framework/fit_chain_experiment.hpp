// 完整RGB域链拟合：固定前三层，以原始四层链输出拟合第四层。
#ifndef FLASH_CHROMA_FRAMEWORK_FIT_CHAIN_EXPERIMENT_HPP
#define FLASH_CHROMA_FRAMEWORK_FIT_CHAIN_EXPERIMENT_HPP
#include "fit_experiment.hpp"

namespace fc_framework {
namespace fit_chain_detail {
using Color = std::array<unsigned, 3>;
inline Color apply_nodes(const fit_detail::Coordinates& coordinates, const Stage& stage, const Color& color) {
    const auto geometry = coordinates.at(color[0], color[1], color[2]);
    Color result{};
    for (unsigned c = 0; c != 3; ++c) {
        std::uint64_t sum = 32768;
        for (unsigned i = 0; i != 4; ++i) sum += std::uint64_t(geometry.weight[i]) * stage.nodes_data()[geometry.node[i] * 3 + c];
        result[c] = static_cast<unsigned>(sum >> 16);
    }
    return result;
}
inline Color target(const std::array<std::vector<std::uint16_t>, 4>& raw, Color color) {
    for (const auto& table : raw) {
        const auto at = ((std::size_t(color[2]) * 256 + color[1]) * 256 + color[0]) * 3;
        color = {static_cast<std::uint8_t>(table[at + 2] / 16), static_cast<std::uint8_t>(table[at + 1] / 16),
                 static_cast<std::uint8_t>(table[at] / 16)};
    }
    return color;
}
} // namespace fit_chain_detail

inline Stage fit_chain_last(const std::array<std::vector<std::uint16_t>, 4>& raw,
                            const std::array<Stage, 4>& sampled, FitReport& report,
                            FitExperimentOptions options = {}) {
    for (const auto& table : raw) if (table.size() != dense_values) throw std::invalid_argument("链拟合要求完整四级LUT");
    if (!options.cg_max_iterations || options.cg_max_iterations > 1000 || options.integer_sweeps > 64 ||
        !std::isfinite(options.regularization) || options.regularization <= 0 ||
        !std::isfinite(options.relative_tolerance) || options.relative_tolerance <= 0 || options.relative_tolerance >= 1)
        throw std::invalid_argument("链拟合参数非法");
    report = {}; report.m = sampled[3].m; report.samples = dense_nodes;
    const std::array<fit_detail::Coordinates, 4> coordinates = {
        fit_detail::Coordinates(sampled[0]), fit_detail::Coordinates(sampled[1]),
        fit_detail::Coordinates(sampled[2]), fit_detail::Coordinates(sampled[3])};
    fit_detail::Normal matrix(coordinates[3]);
    auto result = sampled[3];
    const double start = fit_detail::seconds();
    // 输入均为算法枚举的完整RGB域；这里不存在图片、直方图或抽样权重。
    for (unsigned r = 0; r != 256; ++r) for (unsigned g = 0; g != 256; ++g) for (unsigned b = 0; b != 256; ++b) {
        const fit_chain_detail::Color input = {r, g, b};
        const auto expected = fit_chain_detail::target(raw, input);
        auto prefix = input;
        for (unsigned i = 0; i != 3; ++i) prefix = fit_chain_detail::apply_nodes(coordinates[i], sampled[i], prefix);
        const auto geometry = coordinates[3].at(prefix[0], prefix[1], prefix[2]);
        for (unsigned c = 0; c != 3; ++c) matrix.target_squared_sum += double(expected[c]) * expected[c];
        for (unsigned i = 0; i != 4; ++i) {
            const double own = double(geometry.weight[i]) / 65536;
            if (!own) continue;
            for (unsigned c = 0; c != 3; ++c) matrix.rhs[geometry.node[i]][c] += own * expected[c];
            for (unsigned j = i; j != 4; ++j)
                matrix.h[geometry.node[i]][geometry.mask[i] ^ geometry.mask[j]] += own * (double(geometry.weight[j]) / 65536);
        }
    }
    report.assembly_seconds = fit_detail::seconds() - start;
    report.matrix_bytes = matrix.h.size() * sizeof(matrix.h[0]);
    report.temporary_bytes = report.matrix_bytes + matrix.rhs.size() * sizeof(matrix.rhs[0]) +
                             matrix.count * (3 * 2 + 7) * sizeof(double) + sizeof(coordinates);
    std::vector<std::array<double, 3>> first(matrix.count), solution(matrix.count);
    for (std::size_t i = 0; i != matrix.count; ++i) for (unsigned c = 0; c != 3; ++c) first[i][c] = sampled[3].nodes_data()[i * 3 + c];
    report.linear_sse_before = matrix.sse(first);
    const double solve_start = fit_detail::seconds();
    for (unsigned c = 0; c != 3; ++c) {
        const auto solved = fit_detail::solve_channel(matrix, c, first, options, report.channels[c]);
        for (std::size_t i = 0; i != matrix.count; ++i) solution[i][c] = fit_detail::integer(solved[i]);
    }
    for (unsigned sweep = 0; sweep != options.integer_sweeps; ++sweep) {
        std::size_t changed = 0;
        for (std::size_t i = 0; i != matrix.count; ++i) for (unsigned c = 0; c != 3; ++c) {
            const double reg = options.regularization * (matrix.h[i][0] + 1);
            const double next = fit_detail::integer((matrix.rhs[i][c] + reg * first[i][c] - matrix.row_off_diagonal(i, solution, c)) / (matrix.h[i][0] + reg));
            changed += next != solution[i][c]; solution[i][c] = next;
        }
        ++report.integer_sweeps; if (!changed) break;
    }
    report.linear_sse_after = matrix.sse(solution);
    auto* nodes = result.blob.data() + (result.nodes_data() - result.blob.data());
    for (std::size_t i = 0; i != matrix.count; ++i) {
        bool changed = false;
        for (unsigned c = 0; c != 3; ++c) { nodes[i * 3 + c] = static_cast<std::uint8_t>(solution[i][c]); changed = changed || nodes[i * 3 + c] != sampled[3].nodes_data()[i * 3 + c]; }
        report.changed_nodes += changed;
    }
    report.solve_seconds = fit_detail::seconds() - solve_start;
    const double evaluate_start = fit_detail::seconds();
    for (unsigned r = 0; r != 256; ++r) for (unsigned g = 0; g != 256; ++g) for (unsigned b = 0; b != 256; ++b) {
        const fit_chain_detail::Color input = {r, g, b};
        const auto expected = fit_chain_detail::target(raw, input);
        auto prefix = input;
        for (unsigned i = 0; i != 3; ++i) prefix = fit_chain_detail::apply_nodes(coordinates[i], sampled[i], prefix);
        const auto geometry = coordinates[3].at(prefix[0], prefix[1], prefix[2]);
        unsigned squared[2]{}; double linear_squared[2]{};
        for (unsigned c = 0; c != 3; ++c) {
            std::uint64_t sums[2] = {32768, 32768};
            for (unsigned i = 0; i != 4; ++i) {
                sums[0] += std::uint64_t(geometry.weight[i]) * sampled[3].nodes_data()[geometry.node[i] * 3 + c];
                sums[1] += std::uint64_t(geometry.weight[i]) * result.nodes_data()[geometry.node[i] * 3 + c];
            }
            for (unsigned v = 0; v != 2; ++v) {
                const int error = int(sums[v] >> 16) - int(expected[c]); squared[v] += unsigned(error * error);
                const double linear_error = double(sums[v] - 32768) / 65536 - expected[c]; linear_squared[v] += linear_error * linear_error;
            }
        }
        report.baseline.sse += squared[0]; report.candidate.sse += squared[1];
        report.baseline.mean += std::sqrt(double(squared[0])); report.candidate.mean += std::sqrt(double(squared[1]));
        report.baseline.linear_sse += linear_squared[0]; report.candidate.linear_sse += linear_squared[1];
        report.baseline.max_squared = (std::max)(report.baseline.max_squared, squared[0]);
        report.candidate.max_squared = (std::max)(report.candidate.max_squared, squared[1]);
    }
    report.baseline.mean /= dense_nodes; report.candidate.mean /= dense_nodes;
    const auto matches = [](double direct, double quadratic) { return std::abs(direct - quadratic) <= (std::max)(1.0, direct * 1e-8); };
    if (!matches(report.baseline.linear_sse, report.linear_sse_before) || !matches(report.candidate.linear_sse, report.linear_sse_after))
        throw std::runtime_error("链拟合逐点误差与正规矩阵二次型不同");
    report.evaluation_seconds = fit_detail::seconds() - evaluate_start;
    report.candidate_used = !options.guard_full_domain ||
        (report.candidate.sse <= report.baseline.sse && report.candidate.mean <= report.baseline.mean);
    // 链目标与原末层函数不同，修改后不得沿用原曲线资格绕过拟合节点。
    if (report.candidate_used && report.changed_nodes) {
        result.separable_proven = false; result.proof_nodes = 0; result.curves = {};
    }
    return report.candidate_used ? result : sampled[3];
}
} // namespace fc_framework
#endif
