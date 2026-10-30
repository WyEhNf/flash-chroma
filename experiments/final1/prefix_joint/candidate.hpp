/* 前中层真实整数搜索与末层重拟合；预算预先固定，输入只包含原 LUT。 */
#ifndef ZMX_PREFIX_JOINT_CANDIDATE_HPP
#define ZMX_PREFIX_JOINT_CANDIDATE_HPP
#include "precision_pipeline.hpp"
#include <iostream>

namespace candidate {
using namespace fc_framework;
using namespace fc_framework::precision;

inline std::vector<std::string> variants() {
    return {"prefix_nodes", "prefix_nodes_refit"};
}

struct PrefixSummary {
    std::uint64_t distinct = 0, minimum_integer_sse = 0;
};

// 固定前三层后，每个到达颜色允许选择任意 RGB8 输出，给出末层 SSE 的宽松下界。
inline PrefixSummary prefix_summary(const Models& models,
                                    const std::vector<std::uint32_t>& gold) {
    struct Aggregate {
        std::uint32_t count = 0;
        std::array<std::uint32_t, 3> sum{};
    };
    static_assert(sizeof(Aggregate) == 16, "聚合内存预算变化");
    std::vector<Aggregate> groups(dense_nodes);
    Evaluator evaluator(models);
    std::int64_t total_squared = 0;
    for (std::uint32_t input = 0; input < dense_nodes; ++input) {
        auto& group = groups[evaluator.map(input, 0, 3)];
        ++group.count;
        for (unsigned c = 0; c < 3; ++c) {
            const auto value = component(gold[input], c);
            group.sum[c] += value;
            total_squared += value * value;
        }
    }
    PrefixSummary result;
    for (const auto& group : groups) {
        if (!group.count) continue;
        ++result.distinct;
        for (unsigned c = 0; c < 3; ++c) {
            const std::int64_t mass = group.count, sum = group.sum[c];
            const std::int64_t best = (2 * sum + mass) / (2 * mass);
            total_squared += mass * best * best - 2 * best * sum;
        }
    }
    if (total_squared < 0) throw std::runtime_error("前缀下界计算出现负 SSE");
    result.minimum_integer_sse = std::uint64_t(total_squared);
    return result;
}

inline Models run(const Sources& raw, const Models& baseline,
                  const std::vector<std::uint32_t>& gold, const std::string& variant,
                  std::string& details_json) {
    if (variant != "prefix_nodes" && variant != "prefix_nodes_refit")
        throw std::invalid_argument("未知前中层实验变体");
    if (gold.size() != dense_nodes) throw std::invalid_argument("完整域参考长度不符");
    for (unsigned s = 0; s < 4; ++s) {
        if (raw[s].size() != dense_values || baseline[s].m != 33 ||
            !baseline[s].fractions.empty() || baseline[s].interpolation != Interpolation::TetraQ16)
            throw std::invalid_argument("本实验仅接受四级33立方共享坐标四面体基线");
    }
    const Guard guard{};
    const Histogram anchor = evaluate(baseline, gold);
    Histogram current = anchor;
    Models best = baseline;
    Report report;
    report.baseline = anchor.quality();
    report.result = report.baseline;
    report.configuration = "{\"variant\":\"" + variant +
        "\",\"stage_order_zero_based\":[2,1],\"nodes_per_stage\":32,\"sweeps\":1,"
        "\"rgb_directions\":26,\"steps\":[1,2,4],\"all_five_guards\":true,"
        "\"reads_photos\":false,\"prefix_diagnostic_peak_bytes\":268435456}";
    std::vector<std::uint64_t> support_rows;

    for (const unsigned stage : {2u, 1u}) {
        std::cerr << "前中层节点搜索：第" << stage + 1 << "级" << std::endl;
        Record row;
        row.name = "prefix_stage_" + std::to_string(stage + 1);
        const auto start = fit_detail::seconds();
        Models proposed = best;
        const auto search = optimize_nodes(proposed, gold, stage, anchor, guard,
                                            Objective::Mean, 32, 1);
        support_rows.push_back(search.support_rows);
        const auto measured = evaluate(proposed, gold);
        if (measured.sse != search.after.sse ||
            std::abs(measured.quality().mean - search.after.mean) > 1e-12)
            throw std::runtime_error("前中层增量评估与完整色域重放不符");
        row.proposals = search.proposals;
        row.updates = search.accepted;
        row.quality = measured.quality();
        row.accepted = accepts(measured, anchor, guard) && better(measured, current, Objective::Mean);
        if (row.accepted) { best = std::move(proposed); current = measured; }
        row.seconds = fit_detail::seconds() - start;
        report.records.push_back(row);
        report.result = current.quality();
    }

    FitReport fit;
    bool refit_attempted = false;
    if (variant == "prefix_nodes_refit") {
        std::cerr << "冻结更新后前三层，重拟合第4级" << std::endl;
        refit_attempted = true;
        Record row;
        row.name = "refit_stage_4";
        const auto start = fit_detail::seconds();
        Models proposed = best;
        FitExperimentOptions options;
        // 返回原始提议，由下方完整五项门控裁决，以保留被拒绝结果的指标。
        options.guard_full_domain = false;
        proposed[3] = fit_chain_last(raw, best, fit, options);
        row.converged = true;
        for (const auto& channel : fit.channels) row.converged &= channel.converged;
        const auto measured = evaluate(proposed, gold);
        row.quality = measured.quality();
        row.updates = fit.changed_nodes;
        row.proposals = 1;
        row.accepted = row.converged && accepts(measured, anchor, guard) &&
                       better(measured, current, Objective::Mean);
        if (!row.converged) row.error = "末级拟合未达到既定CG收敛阈值，保留重拟合前候选";
        if (row.accepted) { best = std::move(proposed); current = measured; }
        row.seconds = fit_detail::seconds() - start;
        report.records.push_back(row);
        report.result = current.quality();
    }
    std::cerr << "计算基线和候选的固定前缀下界" << std::endl;
    const auto before_prefix = prefix_summary(baseline, gold);
    const auto after_prefix = prefix_summary(best, gold);
    std::ostringstream extra;
    extra << std::setprecision(17) << "{\"report\":" << json(report)
          << ",\"support_rows\":[" << support_rows[0] << ',' << support_rows[1] << ']'
          << ",\"prefix_before\":{\"distinct\":" << before_prefix.distinct
          << ",\"minimum_integer_sse\":" << before_prefix.minimum_integer_sse << '}'
          << ",\"prefix_after\":{\"distinct\":" << after_prefix.distinct
          << ",\"minimum_integer_sse\":" << after_prefix.minimum_integer_sse << '}'
          << ",\"refit_attempted\":" << (refit_attempted ? "true" : "false")
          << ",\"refit_channels\":[";
    for (unsigned c = 0; c < 3; ++c) {
        if (c) extra << ',';
        extra << "{\"iterations\":" << fit.channels[c].iterations
              << ",\"relative_residual\":" << fit.channels[c].relative_residual
              << ",\"converged\":" << (fit.channels[c].converged ? "true" : "false") << '}';
    }
    extra << "],\"photos_used_for_selection\":false}";
    details_json = extra.str();
    return best;
}
} // namespace candidate
#endif
