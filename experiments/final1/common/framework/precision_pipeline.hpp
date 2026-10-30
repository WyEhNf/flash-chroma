/* 有界历史能力迁移：候选在读图前确定，所有接收判定基于原四LUT完整域。 */
#ifndef FLASH_CHROMA_FRAMEWORK_PRECISION_PIPELINE_HPP
#define FLASH_CHROMA_FRAMEWORK_PRECISION_PIPELINE_HPP
#include "precision_fit.hpp"
#include <sstream>
#include <iomanip>
namespace fc_framework {
namespace precision {
struct Options {
    bool grids = true, independent = true, matched_basis = true, box = true, irls = true, tail_fit = true;
    bool integer_chain = true, shared_coordinates = true, output_coordinates = true, tail_search = true;
    bool separable_calibration = true, finite_box = true;
    unsigned node_budget = 32, coordinate_budget = 12, sweeps = 1, dp_probes = 24, irls_rounds = 2;
    double local_fidelity_weight = 0;
    // 混合容量由调用者给出候选，空列表只保持输入容量。不得按测试图改预算。
    std::vector<std::array<unsigned, 4>> capacities;
    Guard guard{};
    Objective objective = Objective::Mean;
    std::function<void(const std::string &)> progress;
};
struct Record {
    std::string name, error;
    bool accepted = false;
    Quality quality{};
    std::uint64_t proposals = 0, updates = 0;
    double seconds = 0, kkt = 0;
    bool converged = true;
};
struct Report {
    Quality baseline{}, result{};
    std::vector<Record> records;
    std::string configuration = "{}";
};
inline std::string quality_json(const Quality &q) {
    std::ostringstream s;
    s << std::setprecision(17) << "{\"pixels\":" << q.pixels << ",\"mean\":" << q.mean << ",\"sse\":" << q.sse
      << ",\"rms\":" << q.rms << ",\"p99\":" << q.p99 << ",\"max\":" << q.max << ",\"cvar01\":" << q.cvar
      << '}';
    return s.str();
}
inline std::string json(const Report &r) {
    std::ostringstream s;
    s << std::setprecision(17) << "{\"schema\":\"lut-history-v2\",\"configuration\":" << r.configuration
      << ",\"baseline\":" << quality_json(r.baseline) << ",\"result\":" << quality_json(r.result)
      << ",\"steps\":[";
    for (std::size_t i = 0; i < r.records.size(); ++i) {
        if (i)
            s << ',';
        const auto &x = r.records[i];
        s << "{\"name\":" << std::quoted(x.name) << ",\"accepted\":" << (x.accepted ? "true" : "false")
          << ",\"quality\":" << quality_json(x.quality) << ",\"proposals\":" << x.proposals
          << ",\"updates\":" << x.updates << ",\"seconds\":" << x.seconds << ",\"kkt\":" << x.kkt
          << ",\"converged\":" << (x.converged ? "true" : "false") << ",\"error\":" << std::quoted(x.error)
          << '}';
    }
    s << "]}";
    return s.str();
}
inline Models migrate(const Sources &raw, const Models &sampled, Report &report,
                      const Options &options = {}) {
    if (!options.sweeps || options.dp_probes < 2 || options.dp_probes > 64 || options.irls_rounds > 8 ||
        !std::isfinite(options.local_fidelity_weight) || options.local_fidelity_weight < 0)
        throw std::invalid_argument("历史迁移预算非法");
    const auto gold = truth(raw);
    Models best = sampled;
    FitReport baseline_fit;
    best[3] = fit_chain_last(raw, best, baseline_fit);
    Histogram anchor = evaluate(best, gold), current = anchor;
    report = {};
    report.baseline = anchor.quality();
    {
        std::ostringstream c;
        c << std::setprecision(17) << "{\"node_budget\":" << options.node_budget
          << ",\"coordinate_budget\":" << options.coordinate_budget << ",\"sweeps\":" << options.sweeps
          << ",\"dp_probes\":" << options.dp_probes << ",\"irls_rounds\":" << options.irls_rounds
          << ",\"local_fidelity_weight\":" << options.local_fidelity_weight
          << ",\"objective\":" << unsigned(options.objective) << ",\"grids\":" << options.grids
          << ",\"independent\":" << options.independent << ",\"matched_basis\":" << options.matched_basis
          << ",\"box\":" << options.box << ",\"irls\":" << options.irls
          << ",\"tail_fit\":" << options.tail_fit << ",\"integer_chain\":" << options.integer_chain
          << ",\"shared_coordinates\":" << options.shared_coordinates
          << ",\"output_coordinates\":" << options.output_coordinates
          << ",\"tail_search\":" << options.tail_search
          << ",\"separable_calibration\":" << options.separable_calibration
          << ",\"finite_box\":" << options.finite_box << ",\"guard\":[" << options.guard.mean << ','
          << options.guard.sse << ',' << options.guard.maximum << ',' << options.guard.p99 << ','
          << options.guard.cvar << ',' << options.guard.pointwise << "],\"capacities\":[";
        for (std::size_t i = 0; i < options.capacities.size(); ++i) {
            if (i)
                c << ',';
            const auto &m = options.capacities[i];
            c << '[' << m[0] << ',' << m[1] << ',' << m[2] << ',' << m[3] << ']';
        }
        c << "]}";
        report.configuration = c.str();
        report.result = anchor.quality();
    }
    auto attempt = [&](const std::string &name, const std::function<void(Models &, Record &)> &operation) {
        if (options.progress)
            options.progress(name);
        Models candidate = best;
        Record r;
        r.name = name;
        const double start = fit_detail::seconds();
        try {
            operation(candidate, r);
        } catch (const std::runtime_error &e) {
            r.error = e.what();
            r.converged = false;
            r.quality = current.quality();
            r.seconds = fit_detail::seconds() - start;
            report.records.push_back(std::move(r));
            return;
        }
        const auto measured = evaluate(candidate, gold);
        r.quality = measured.quality();
        r.accepted = r.converged && accepts(measured, anchor, options.guard) &&
                     better(measured, current, options.objective);
        if (r.accepted && options.guard.pointwise) {
            Evaluator a(best), b(candidate);
            for (std::uint32_t i = 0; i < dense_nodes; ++i)
                if (distance(b.map(i), gold[i]) > distance(a.map(i), gold[i])) {
                    r.accepted = false;
                    break;
                }
        }
        if (r.accepted) {
            best = std::move(candidate);
            current = measured;
        }
        r.seconds = fit_detail::seconds() - start;
        report.records.push_back(std::move(r));
        report.result = current.quality();
    };
    // 固定保护锚点是已有chain_ls基线；任何新能力均不能放松其尾部上限。
    if (options.independent)
        attempt("independent_ls", [&](Models &m, Record &) {
            m = sampled;
            for (unsigned s = 0; s < 4; ++s) {
                FitReport f;
                m[s] = fit_full(raw[s], m[s], f);
            }
            FitReport f;
            m[3] = fit_chain_last(raw, m, f);
        });
    auto grid_candidate = [&](const std::array<unsigned, 4> &sizes, const std::string &grid) {
        std::string id = grid;
        for (auto m : sizes)
            id += '-' + std::to_string(m);
        attempt(id, [&](Models &m, Record &) {
            for (unsigned s = 0; s < 4; ++s) {
                bool reused = false;
                for (unsigned k = 0; k < s; ++k)
                    if (sizes[k] == sizes[s] && raw[k] == raw[s]) {
                        m[s] = m[k];
                        reused = true;
                        break;
                    }
                if (reused)
                    continue;
                FitOptions f;
                f.prove_structure = true;
                if (grid == "curvature")
                    f.axes = curvature_axes(raw[s], sizes[s]);
                else if (grid == "dp")
                    f.axes = dp_axes(raw[s], sizes[s], options.dp_probes);
                else if (grid == "error")
                    f.axes = error_axes(raw[s], sizes[s]);
                else
                    f.grid = grid == "framework" ? Grid::FrameworkStep : Grid::UniformRounded;
                m[s] = prepare_stage(raw[s], sizes[s], f);
            }
            FitReport f;
            m[3] = fit_chain_last(raw, m, f);
        });
    };
    std::array<unsigned, 4> sizes;
    for (unsigned s = 0; s < 4; ++s)
        sizes[s] = sampled[s].m;
    if (options.grids)
        for (const char *name : {"uniform", "framework", "curvature", "dp", "error"})
            grid_candidate(sizes, name);
    for (const auto &capacity : options.capacities) {
        for (auto m : capacity)
            if (m < 17 || m > 33)
                throw std::invalid_argument("混合容量越界");
        grid_candidate(capacity, "dp");
    }
    if (options.separable_calibration)
        for (unsigned s = 0; s < 4; ++s)
            attempt("exact_monotone_" + std::to_string(s), [&](Models &m, Record &r) {
                MonotoneReport proof;
                m[s] = exact_monotone(raw[s], m[s], proof);
                if (!proof.feasible)
                    r.error = "源结构、节点或单调舍入区间不满足，保留原候选";
            });
    if (options.matched_basis)
        for (unsigned stage = 0; stage < 4; ++stage)
            attempt("matched_trilinear_" + std::to_string(stage), [&](Models &m, Record &r) {
                m[stage].interpolation = Interpolation::TrilinearQ16;
                clear_proof(m[stage]);
                BoxReport b;
                if (stage == 3) {
                    Support support(m, gold, 3);
                    m[3] = box_fit(m[3], support.points, Weight::Uniform, b);
                } else
                    m[stage] = fit_source_box(raw[stage], m[stage], Weight::Uniform, b);
                r.kkt = b.kkt;
                r.converged = b.converged;
            });
    auto weighted = [&](Weight weight, const std::string &name) {
        attempt(name, [&](Models &m, Record &r) {
            Support support(m, gold, 3);
            BoxReport b;
            m[3] = box_fit(m[3], support.points, weight, b);
            r.kkt = b.kkt;
            r.converged = b.converged;
        });
    };
    if (options.box)
        weighted(Weight::Uniform, "chain_box");
    if (options.irls)
        for (unsigned i = 0; i < options.irls_rounds; ++i)
            weighted(Weight::Lp6, "chain_irls_" + std::to_string(i));
    if (options.tail_fit)
        weighted(Weight::Tail, "chain_tail_weight");
    auto nodes = [&](Objective objective, const std::string &name) {
        for (unsigned stage : {3u, 2u, 1u, 0u})
            attempt(name + '_' + std::to_string(stage), [&](Models &m, Record &r) {
                const auto x =
                    optimize_nodes(m, gold, stage, anchor, options.guard, objective, options.node_budget,
                                   options.sweeps, &raw[stage], options.local_fidelity_weight);
                r.proposals = x.proposals;
                r.updates = x.accepted;
            });
    };
    if (options.integer_chain)
        nodes(options.objective, "integer_rgb_joint");
    if (options.shared_coordinates)
        for (unsigned s = 0; s < 4; ++s)
            attempt("shared_coordinate_" + std::to_string(s), [&](Models &m, Record &r) {
                const auto x = calibrate_coordinates(m, gold, s, anchor, options.guard, options.objective,
                                                     options.coordinate_budget, false, &raw[s],
                                                     options.local_fidelity_weight);
                r.proposals = x.proposals;
                r.updates = x.accepted;
            });
    if (options.output_coordinates)
        for (unsigned s = 0; s < 4; ++s)
            attempt("output_coordinate_" + std::to_string(s), [&](Models &m, Record &r) {
                const auto x = calibrate_coordinates(m, gold, s, anchor, options.guard, options.objective,
                                                     options.coordinate_budget, true, &raw[s],
                                                     options.local_fidelity_weight);
                r.proposals = x.proposals;
                r.updates = x.accepted;
            });
    if (options.tail_search) {
        nodes(Objective::Maximum, "minimax");
        nodes(Objective::P99, "p99");
        nodes(Objective::CVaR, "cvar");
    }
    if (options.finite_box)
        attempt("frozen_integer_box", [&](Models &m, Record &r) {
            Support support(m, gold, 3);
            const auto found =
                std::max_element(support.points.begin(), support.points.end(),
                                 [](const Point &a, const Point &b) { return a.error < b.error; });
            const auto g = geometry(detail::view(m[3]), m[3].interpolation, found->rgb, 0);
            const auto node =
                g.node[std::max_element(g.weight.begin(), g.weight.begin() + g.count) - g.weight.begin()];
            const auto x = exact_integer_box(m, gold, 3, {{node, 0, 1}, {node, 1, 1}, {node, 2, 1}}, anchor,
                                             options.guard, options.objective, 27);
            r.proposals = x.proposals;
            r.updates = x.accepted;
        });
    report.result = current.quality();
    return best;
}
} // namespace precision
} // namespace fc_framework
#endif
