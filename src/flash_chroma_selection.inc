/* 连续目标到离散执行计划的无堆选择器；所有误差及时间结论仅属于绑定的验证上下文。 */
#ifndef FLASH_CHROMA_SELECTION_INCLUDED
#define FLASH_CHROMA_SELECTION_INCLUDED
#include <limits>

namespace fc {

enum class Goal { Balanced, Fastest, Accurate, Compact };
enum class SelectionStatus { Ok, InvalidRequest, InvalidCandidate, NoFeasible, BufferTooSmall };

struct Preference {
    double accuracy = 1.0;
    double speed = 1.0;
    double compactness = 1.0;
};

struct Candidate {
    const char* id = nullptr;
    const char* context = nullptr;
    const char* model_id = nullptr;
    const char* evidence = nullptr;
    RuntimeConfig config{};
    double mean_error = std::numeric_limits<double>::quiet_NaN();
    double worst_image_mean = std::numeric_limits<double>::quiet_NaN();
    double batch_ms = std::numeric_limits<double>::quiet_NaN();
    std::size_t runtime_bytes = 0;
    std::size_t workspace_bytes = 0;
    bool correctness_verified = false;
    bool accuracy_verified = false;
    bool resources_verified = false;
    bool time_verified = false;
    bool time_stable = false;
};

struct Request {
    const char* context = nullptr;
    Target target = RuntimeConfig{}.target;
    Goal goal = Goal::Balanced;
    Preference preference{};
    unsigned backend_mask = available_backends() & 3u;
    unsigned max_threads = (compiled_capabilities() & 4u) ? 256u : 1u;
    bool use_time = true;
    bool require_stable_time = true;
    bool has_error_limit = false;
    double max_image_mean_error = 0;
    bool has_time_limit = false;
    double max_batch_ms = 0;
    std::size_t max_runtime_bytes = (std::numeric_limits<std::size_t>::max)();
    std::size_t max_workspace_bytes = (std::numeric_limits<std::size_t>::max)();
};

struct RejectionCounts {
    std::size_t context = 0, target = 0, capability = 0;
    std::size_t unverified = 0, unstable_time = 0, budget = 0;
};

struct SelectionView {
    std::size_t index = (std::numeric_limits<std::size_t>::max)();
    double score = 0;
    bool provisional = false;
    std::size_t eligible = 0;
    std::size_t frontier_size = 0;
    RejectionCounts rejected{};
};

namespace selection_detail {
inline bool text(const char* value) { return value && *value; }
inline bool number(double value) {
    return value >= 0 && value <= (std::numeric_limits<double>::max)();
}
inline int compare(const char* a, const char* b) {
    while (*a && *a == *b) { ++a; ++b; }
    const unsigned char x = static_cast<unsigned char>(*a), y = static_cast<unsigned char>(*b);
    return x < y ? -1 : (x > y ? 1 : 0);
}
inline bool valid_target(Target value) {
    return value == Target::Desktop || value == Target::Mobile ||
           value == Target::Embedded || value == Target::Portable;
}
inline bool valid_request(const Request& r) {
    const auto& w = r.preference;
    if (!text(r.context) || !valid_target(r.target) || !r.backend_mask || (r.backend_mask & ~3u) ||
        !r.max_threads || r.max_threads > 256 ||
        !number(w.accuracy) || !number(w.speed) || !number(w.compactness) ||
        w.accuracy > 1 || w.speed > 1 || w.compactness > 1 ||
        !(w.accuracy + w.speed + w.compactness > 0) ||
        (r.has_error_limit && !number(r.max_image_mean_error)) ||
        (r.has_time_limit && !number(r.max_batch_ms))) return false;
    if (r.goal != Goal::Balanced && r.goal != Goal::Fastest &&
        r.goal != Goal::Accurate && r.goal != Goal::Compact) return false;
    return r.use_time || (r.goal != Goal::Fastest && !r.has_time_limit &&
                         (r.goal != Goal::Balanced || w.speed == 0));
}
inline bool valid_candidate(const Candidate& c) {
    if (!text(c.id) || !text(c.context) || !text(c.model_id) || !text(c.evidence) ||
        !valid_target(c.config.target) || !c.config.threads || c.config.threads > 256 ||
        !c.config.block_pixels || (c.config.backend != Backend::Scalar && c.config.backend != Backend::Avx2) ||
        (c.config.representation != Representation::Sparse && c.config.representation != Representation::DirectU8 &&
         c.config.representation != Representation::DirectU16 && c.config.representation != Representation::DirectRGB24)) return false;
    if (c.accuracy_verified && (!number(c.mean_error) || !number(c.worst_image_mean) ||
                               c.worst_image_mean < c.mean_error)) return false;
    if (c.time_verified && (!number(c.batch_ms) || c.batch_ms == 0)) return false;
    if (c.time_stable && !c.time_verified) return false;
    if (c.resources_verified && (c.workspace_bytes > c.runtime_bytes ||
                                c.workspace_bytes > c.config.max_workspace_bytes)) return false;
    if ((c.config.target == Target::Embedded || c.config.target == Target::Portable) &&
        (c.config.backend != Backend::Scalar || c.config.representation != Representation::Sparse ||
         c.config.threads != 1)) return false;
    return true;
}
inline bool eligible(const Candidate& c, const Request& r, RejectionCounts* counts = nullptr) {
    if (compare(c.context, r.context)) { if (counts) ++counts->context; return false; }
    if (c.config.target != r.target) { if (counts) ++counts->target; return false; }
    const unsigned bit = c.config.backend == Backend::Avx2 ? 2u : 1u;
    bool compiled_plan = true;
#if FLASH_CHROMA_TARGET >= 3
    if (c.config.target == Target::Desktop || c.config.target == Target::Mobile) compiled_plan = false;
#endif
#if !FLASH_CHROMA_ENABLE_DIRECT
    if (c.config.representation != Representation::Sparse) compiled_plan = false;
#endif
    if (c.config.block_pixels > (std::numeric_limits<std::size_t>::max)()/3) compiled_plan = false;
    if (!compiled_plan || !(bit & r.backend_mask & available_backends()) || c.config.threads > r.max_threads ||
        (c.config.threads > 1 && !(compiled_capabilities() & 4u))) {
        if (counts) ++counts->capability;
        return false;
    }
    if (!c.correctness_verified || !c.accuracy_verified || !c.resources_verified ||
        (r.use_time && !c.time_verified)) { if (counts) ++counts->unverified; return false; }
    if (r.use_time && r.require_stable_time && !c.time_stable) {
        if (counts) ++counts->unstable_time;
        return false;
    }
    if ((r.has_error_limit && !(c.worst_image_mean < r.max_image_mean_error)) ||
        (r.has_time_limit && c.batch_ms > r.max_batch_ms) ||
        c.runtime_bytes > r.max_runtime_bytes || c.workspace_bytes > r.max_workspace_bytes) {
        if (counts) ++counts->budget;
        return false;
    }
    return true;
}
inline bool dominates(const Candidate& a, const Candidate& b, const Request& r) {
    /* 先应用逐图/工作区预算，再计算三维前沿；原catalog须保留所有候选以便改变预算重选。 */
    return a.mean_error <= b.mean_error && (!r.use_time || a.batch_ms <= b.batch_ms) &&
           a.runtime_bytes <= b.runtime_bytes &&
           (a.mean_error < b.mean_error || (r.use_time && a.batch_ms < b.batch_ms) ||
            a.runtime_bytes < b.runtime_bytes);
}
inline bool on_frontier(const Candidate* c, std::size_t count, std::size_t index, const Request& r) {
    if (!eligible(c[index], r)) return false;
    for (std::size_t j = 0; j < count; ++j)
        if (j != index && eligible(c[j], r) && dominates(c[j], c[index], r)) return false;
    return true;
}
inline SelectionStatus validate(const Candidate* c, std::size_t n, const Request& r) {
    if (!valid_request(r) || (n && !c)) return SelectionStatus::InvalidRequest;
    for (std::size_t i = 0; i < n; ++i) {
        if (!valid_candidate(c[i])) return SelectionStatus::InvalidCandidate;
        for (std::size_t j = 0; j < i; ++j)
            if (!compare(c[j].id, c[i].id)) return SelectionStatus::InvalidCandidate;
    }
    return SelectionStatus::Ok;
}
inline double normalized(double value, double minimum, double maximum) {
    if (!(maximum > minimum)) return 0;
    /* 所有量非负，因此差值不溢出；直接相减还能保留相邻浮点数的尺度。 */
    return (value - minimum) / (maximum - minimum);
}
inline bool tie_less(const Candidate& a, const Candidate& b, const Request& r) {
    if (a.mean_error != b.mean_error) return a.mean_error < b.mean_error;
    if (a.worst_image_mean != b.worst_image_mean) return a.worst_image_mean < b.worst_image_mean;
    if (r.use_time && a.batch_ms != b.batch_ms) return a.batch_ms < b.batch_ms;
    if (a.runtime_bytes != b.runtime_bytes) return a.runtime_bytes < b.runtime_bytes;
    if (a.workspace_bytes != b.workspace_bytes) return a.workspace_bytes < b.workspace_bytes;
    return compare(a.id, b.id) < 0;
}
} // namespace selection_detail

/* 查询需要容量时可传nullptr/0；容量不足不修改indices。 */
inline SelectionStatus frontier(const Candidate* candidates, std::size_t count, const Request& request,
                                std::size_t* indices, std::size_t capacity, std::size_t* required) {
    if (!required || (capacity && !indices)) return SelectionStatus::InvalidRequest;
    const auto status = selection_detail::validate(candidates, count, request);
    if (status != SelectionStatus::Ok) return status;
    std::size_t needed = 0;
    for (std::size_t i = 0; i < count; ++i)
        if (selection_detail::on_frontier(candidates, count, i, request)) ++needed;
    *required = needed;
    if (!needed) return SelectionStatus::NoFeasible;
    if (capacity < needed) return SelectionStatus::BufferTooSmall;
    std::size_t out = 0;
    for (std::size_t i = 0; i < count; ++i)
        if (selection_detail::on_frontier(candidates, count, i, request)) indices[out++] = i;
    return SelectionStatus::Ok;
}

inline SelectionStatus select(const Candidate* candidates, std::size_t count,
                              const Request& request, SelectionView* output) {
    if (!output) return SelectionStatus::InvalidRequest;
    const auto status = selection_detail::validate(candidates, count, request);
    if (status != SelectionStatus::Ok) return status;
    SelectionView result;
    double min_e = (std::numeric_limits<double>::max)(), max_e = 0;
    double min_t = min_e, max_t = 0;
    std::size_t min_m = (std::numeric_limits<std::size_t>::max)(), max_m = 0;
    for (std::size_t i = 0; i < count; ++i) {
        const auto& c = candidates[i];
        if (!selection_detail::eligible(c, request, &result.rejected)) continue;
        ++result.eligible;
        if (c.mean_error < min_e) min_e = c.mean_error;
        if (c.mean_error > max_e) max_e = c.mean_error;
        if (request.use_time && c.batch_ms < min_t) min_t = c.batch_ms;
        if (request.use_time && c.batch_ms > max_t) max_t = c.batch_ms;
        if (c.runtime_bytes < min_m) min_m = c.runtime_bytes;
        if (c.runtime_bytes > max_m) max_m = c.runtime_bytes;
    }
    if (!result.eligible) { *output = result; return SelectionStatus::NoFeasible; }
    Preference weights = request.preference;
    if (request.goal == Goal::Fastest) weights = {0, 1, 0};
    else if (request.goal == Goal::Accurate) weights = {1, 0, 0};
    else if (request.goal == Goal::Compact) weights = {0, 0, 1};
    const double sum = weights.accuracy + weights.speed + weights.compactness;
    double best = (std::numeric_limits<double>::max)();
    for (std::size_t i = 0; i < count; ++i) {
        if (!selection_detail::on_frontier(candidates, count, i, request)) continue;
        ++result.frontier_size;
        const auto& c = candidates[i];
        const double error = selection_detail::normalized(c.mean_error, min_e, max_e);
        const double time = request.use_time ? selection_detail::normalized(c.batch_ms, min_t, max_t) : 0;
        const double memory = max_m > min_m ? double(c.runtime_bytes - min_m) / double(max_m - min_m) : 0;
        const double score = (weights.accuracy * error + weights.speed * time + weights.compactness * memory) / sum;
        if (score < best || (score == best && selection_detail::tie_less(c, candidates[result.index], request))) {
            best = score; result.index = i;
        }
    }
    result.score = best;
    result.provisional = !request.use_time || !candidates[result.index].time_stable;
    *output = result;
    return SelectionStatus::Ok;
}

inline const char* selection_status_string(SelectionStatus status) {
    switch (status) {
    case SelectionStatus::Ok: return "已选择绑定上下文的可执行配置";
    case SelectionStatus::InvalidRequest: return "请求非法：检查连续权重、上下文、目标与预算";
    case SelectionStatus::InvalidCandidate: return "候选记录非法：检查唯一身份、指标及执行配置";
    case SelectionStatus::NoFeasible: return "无满足验证、能力和预算要求的候选";
    case SelectionStatus::BufferTooSmall: return "前沿输出容量不足，未写入索引";
    }
    return "未知选择状态";
}
} // namespace fc
#endif
