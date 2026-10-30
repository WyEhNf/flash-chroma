/* 独立合同：连续权重、非凸前沿、资源和能力过滤，不执行性能测量。 */
#define FLASH_CHROMA_IMPLEMENTATION
#include "flash_chroma.hpp"
#include <cassert>
#include <cstdio>
#include <limits>

static fc::Candidate point(const char* id, double error, double time, std::size_t bytes) {
    fc::Candidate c;
    c.id = id; c.context = "fixture"; c.model_id = "fixed-four-luts"; c.evidence = "independent-contract";
    c.config.target = fc::Target::Desktop; c.config.backend = fc::Backend::Scalar;
    c.config.representation = fc::Representation::Sparse; c.config.threads = 1;
    c.mean_error = error; c.worst_image_mean = error + .05; c.batch_ms = time;
    c.runtime_bytes = bytes; c.workspace_bytes = 0;
    c.correctness_verified = c.accuracy_verified = c.resources_verified = c.time_verified = c.time_stable = true;
    return c;
}

int main() {
#if FLASH_CHROMA_TARGET >= 3
    fc::Candidate forbidden = point("desktop", .1, 1, 1);
    fc::Request limited;
    limited.context = "fixture"; limited.target = fc::Target::Desktop;
    fc::SelectionView checked;
    assert(fc::select(&forbidden, 1, limited, &checked) == fc::SelectionStatus::NoFeasible);
    forbidden.config.target = static_cast<fc::Target>(FLASH_CHROMA_TARGET);
    limited.target = forbidden.config.target;
    assert(fc::select(&forbidden, 1, limited, &checked) == fc::SelectionStatus::Ok);
    puts("部署编译目标的选择隔离合同通过");
    return 0;
#endif
    fc::Candidate points[] = {point("accurate", .1, 10, 100), point("nonconvex", .6, 6, 100),
                             point("fast", 1, 1, 100), point("dominated", 2, 20, 200)};
    fc::Request request;
    request.context = "fixture"; request.target = fc::Target::Desktop;
    assert((request.backend_mask & ~3u) == 0);
    fc::SelectionView default_result;
    assert(fc::select(points, 4, request, &default_result) == fc::SelectionStatus::Ok);
    fc::Candidate direct = point("direct", .1, 1, 100);
    direct.config.representation = fc::Representation::DirectU8;
#if FLASH_CHROMA_ENABLE_DIRECT
    assert(fc::select(&direct, 1, request, &default_result) == fc::SelectionStatus::Ok);
#else
    assert(fc::select(&direct, 1, request, &default_result) == fc::SelectionStatus::NoFeasible);
#endif
    request.backend_mask = 1; request.max_threads = 1;
    std::size_t indices[4] = {99,99,99,99}, needed = 0;
    assert(fc::frontier(points, 4, request, indices, 1, &needed) == fc::SelectionStatus::BufferTooSmall);
    assert(needed == 3 && indices[0] == 99);
    assert(fc::frontier(points, 4, request, indices, 4, &needed) == fc::SelectionStatus::Ok);
    assert(needed == 3 && indices[0] == 0 && indices[1] == 1 && indices[2] == 2);
    fc::SelectionView result;
    request.goal = fc::Goal::Fastest; request.has_error_limit = true; request.max_image_mean_error = .7;
    assert(fc::select(points, 4, request, &result) == fc::SelectionStatus::Ok && result.index == 1);
    request.max_image_mean_error = points[0].worst_image_mean;
    assert(fc::select(points, 4, request, &result) == fc::SelectionStatus::NoFeasible);
    request.has_error_limit = false; request.goal = fc::Goal::Balanced;
    request.preference = {.999, .001, 0};
    assert(fc::select(points, 4, request, &result) == fc::SelectionStatus::Ok && result.index == 0);
    request.preference = {.001, .999, 0};
    assert(fc::select(points, 4, request, &result) == fc::SelectionStatus::Ok && result.index == 2);
    request.preference = {0,0,0};
    assert(fc::select(points, 4, request, &result) == fc::SelectionStatus::InvalidRequest);
    request.preference = {1, std::numeric_limits<double>::infinity(), 0};
    assert(fc::select(points, 4, request, &result) == fc::SelectionStatus::InvalidRequest);
    request.preference = {1,1,1};
    for (auto& c: points) c.time_stable = false;
    assert(fc::select(points, 4, request, &result) == fc::SelectionStatus::NoFeasible);
    request.require_stable_time = false;
    assert(fc::select(points, 4, request, &result) == fc::SelectionStatus::Ok && result.provisional);
    for (auto& c: points) { c.time_verified = false; c.batch_ms = std::numeric_limits<double>::quiet_NaN(); }
    assert(fc::select(points, 4, request, &result) == fc::SelectionStatus::NoFeasible);
    request.use_time = false; request.goal = fc::Goal::Accurate;
    assert(fc::select(points, 4, request, &result) == fc::SelectionStatus::Ok && result.index == 0 && result.provisional);
    request.max_runtime_bytes = 99;
    assert(fc::select(points, 4, request, &result) == fc::SelectionStatus::NoFeasible);
    request.max_runtime_bytes = 100; request.target = fc::Target::Embedded;
    assert(fc::select(points, 4, request, &result) == fc::SelectionStatus::NoFeasible);
    request.target = fc::Target::Desktop;
    points[0].config.backend = fc::Backend::Avx2;
    assert(fc::select(points, 4, request, &result) == fc::SelectionStatus::Ok && result.index == 1);
    points[0].config.backend = fc::Backend::Scalar;
    points[0].mean_error = std::numeric_limits<double>::quiet_NaN();
    assert(fc::select(points, 4, request, &result) == fc::SelectionStatus::InvalidCandidate);
    puts("连续目标与三维前沿C++合同通过");
}
