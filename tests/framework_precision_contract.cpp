/* 历史迁移的独立算术、边界、质量证书及联合质量守恒合同。 */
#define FLASH_CHROMA_IMPLEMENTATION
#define FLASH_CHROMA_ENABLE_OPENMP 0
#include "precision_pipeline.hpp"
#include <cstdio>
#include <cstdlib>
using namespace fc_framework;
void check(bool value, const char *message) {
    if (!value) {
        std::fprintf(stderr, "精度合同失败：%s\n", message);
        std::exit(1);
    }
}
std::uint32_t oracle(const Stage &s, std::uint32_t packed) {
    const auto *index = s.blob.data() + 16 + 12 * s.m;
    std::uint32_t result = 0;
    const std::size_t stride[3] = {std::size_t(s.m) * s.m, s.m, 1};
    std::size_t base = 0;
    for (unsigned a = 0; a < 3; ++a)
        base += index[a * 256 + ((packed >> (8 * a)) & 255)] * stride[a];
    for (unsigned c = 0; c < 3; ++c) {
        const auto *f = s.fractions.empty() ? index + 768 : s.fractions.data() + 3072 * c;
        long double fraction[3];
        for (unsigned a = 0; a < 3; ++a)
            fraction[a] =
                fc_core::fc_detail_read32(f + 4 * (a * 256 + ((packed >> (8 * a)) & 255))) / 65536.L;
        long double sum = 0;
        if (s.interpolation == Interpolation::TrilinearQ16) {
            for (unsigned r = 0; r < 2; ++r)
                for (unsigned g = 0; g < 2; ++g)
                    for (unsigned b = 0; b < 2; ++b)
                        sum += s.nodes_data()[3 * (base + r * stride[0] + g * stride[1] + b) + c] *
                               (r ? fraction[0] : 1 - fraction[0]) * (g ? fraction[1] : 1 - fraction[1]) *
                               (b ? fraction[2] : 1 - fraction[2]);
        } else {
            std::array<std::pair<long double, unsigned>, 3> order{
                {{fraction[0], 0}, {fraction[1], 1}, {fraction[2], 2}}};
            std::stable_sort(order.begin(), order.end(), [](auto a, auto b) { return a.first > b.first; });
            std::size_t at = base;
            long double previous = 1;
            for (unsigned i = 0; i < 3; ++i) {
                sum += (previous - order[i].first) * s.nodes_data()[3 * at + c];
                at += stride[order[i].second];
                previous = order[i].first;
            }
            sum += previous * s.nodes_data()[3 * at + c];
        }
        result |= std::uint32_t(std::floor(sum + .5L)) << (8 * c);
    }
    return result;
}
int main() {
    using namespace precision;
    for (unsigned d = 0; d <= max_error_squared; ++d) {
        const auto low = roots().lower[d], high = roots().upper[d];
        const long double exact = std::sqrt(static_cast<long double>(d)) * 16777216.L;
        check(low <= exact && high >= exact && high - low <= 1, "Q24全误差域无溢出上下界");
    }
    Histogram a, b;
    for (unsigned i = 0; i < 100; ++i) {
        a.add(i == 99 ? 100 : 1, 1);
        b.add(i == 99 ? 121 : 1, 1);
    }
    check(std::abs(a.quality().p99 - 1.09) < 1e-12 && a.quality().cvar == 10 && a.quality().sse == 199,
          "历史线性分位p99及固定top1%尾部");
    check(certified_mean_leq(a, b) && !certified_mean_leq(b, a), "整数证书比较");
    check(accepts(a, b, Guard{}) && !accepts(b, a, Guard{}), "多指标锚点不可倒置");
    std::vector<std::uint16_t> raw(dense_values);
    for (std::uint32_t i = 0; i < dense_nodes; ++i)
        for (unsigned c = 0; c < 3; ++c)
            raw[3 * i + 2 - c] = std::uint16_t((i >> (8 * c) & 255) * 16);
    Models models;
    const unsigned sizes[4] = {17, 18, 25, 33};
    for (unsigned s = 0; s < 4; ++s) {
        FitOptions fit;
        fit.axes = fixed_axes(sizes[s], Grid::UniformRounded);
        fit.prove_structure = false;
        models[s] = prepare_stage(raw, sizes[s], fit);
        auto &stage = models[s];
        auto *nodes = stage.blob.data() + (stage.nodes_data() - stage.blob.data());
        for (std::size_t i = 0; i < stage.node_bytes(); ++i)
            nodes[i] = std::uint8_t(i * 73 + i / 17 + s * 29);
        initialize_sidecar(stage);
        for (unsigned c = 0; c < 3; ++c)
            for (unsigned at = 0; at < 768; ++at)
                detail::put32(stage.fractions, 3072 * c + 4 * at, (at * 47 + c * 8191) % 65537);
        if (s % 2)
            stage.interpolation = Interpolation::TrilinearQ16;
    }
    std::vector<std::uint8_t> input(262147 * 3), expected(input.size()), output(input.size());
    std::uint32_t random = 42;
    for (std::size_t i = 0; i < input.size(); i += 3) {
        random = random * 1664525u + 1013904223u;
        auto value = random & 0xffffffu;
        for (unsigned c = 0; c < 3; ++c)
            input[i + c] = std::uint8_t(value >> (8 * c));
        for (const auto &s : models)
            value = oracle(s, value);
        for (unsigned c = 0; c < 3; ++c)
            expected[i + c] = std::uint8_t(value >> (8 * c));
    }
    const std::array<const Stage *, 4> pointers{{&models[0], &models[1], &models[2], &models[3]}};
    Chain chain;
    fc_framework::Options options;
    options.structure = false;
    options.backend = fc::Backend::Scalar;
    check(chain.prepare(pointers, options) == fc::Status::Ok, "混合基础Sparse准备");
    check(chain.apply(input.data(), output.data(), input.size() / 3) == fc::Status::Ok && output == expected,
          "混合插值/非均匀轴/分输出坐标独立oracle");
    output = input;
    check(chain.apply(output.data(), output.data(), output.size() / 3) == fc::Status::Ok &&
              output == expected,
          "混合精确原地");
    check(chain.apply(input.data(), input.data() + 1, 16) == fc::Status::Overlap, "混合部分重叠拒绝");
    options.representation = fc::Representation::DirectU8;
    check(chain.prepare(pointers, options) == fc::Status::Unsupported && !chain.ready(),
          "不支持的palette失败失效");
    options.representation = fc::Representation::DirectRGB24;
    options.max_workspace_bytes = 1;
    check(chain.prepare(pointers, options) == fc::Status::Budget && !chain.ready(), "工作区失败属于预算");
    options.max_workspace_bytes = 64 * fc::MiB;
    options.backend = fc::Backend::Auto;
    check(chain.prepare(pointers, options) == fc::Status::Ok, "混合RGB24准备");
    check(chain.apply(input.data(), output.data(), input.size() / 3) == fc::Status::Ok && output == expected,
          "混合RGB24实际后端/短尾");
    for (unsigned offset = 0; offset < 65; ++offset)
        for (unsigned n = 0; n < 130; ++n)
            check(chain.apply(input.data() + 3 * offset, output.data(), n) == fc::Status::Ok &&
                      std::equal(output.begin(), output.begin() + 3 * n, expected.begin() + 3 * offset),
                  "所有短尾与相位");
    FitReport fit_report;
    bool rejected = false;
    try {
        fit_full(raw, models[0], fit_report);
    } catch (const std::invalid_argument &) {
        rejected = true;
    }
    check(rejected, "旧LS不得忽略分输出坐标");
    Stage stage = models[0];
    stage.fractions.clear();
    stage.interpolation = Interpolation::TetraQ16;
    auto *nodes = stage.blob.data() + (stage.nodes_data() - stage.blob.data());
    std::fill(nodes, nodes + stage.node_bytes(), 0);
    for (auto &model : models)
        model = stage;
    const std::vector<std::uint32_t> gold(dense_nodes, 1);
    auto anchor = evaluate(models, gold);
    Support support(models, gold, 3);
    check(support.points.size() == 1 && support.points[0].mass == dense_nodes &&
              support.histogram.sse == dense_nodes,
          "联合支撑完整质量归并");
    BoxReport box;
    const auto fitted = box_fit(models[3], support.points, Weight::Uniform, box);
    check(box.converged && oracle(fitted, 0) == 1, "box-KKT及实际整数输出");
    auto boxed = models;
    const auto box_search =
        exact_integer_box(boxed, gold, 3, {{0, 0, 1}, {0, 1, 1}}, anchor, Guard{}, Objective::Mean, 4);
    check(box_search.proposals == 4 && box_search.after.sse == 0, "冻结整数箱完整4叶及真实最优");
    const auto protected_search =
        optimize_nodes(models, gold, 3, anchor, Guard{}, Objective::Mean, 1, 1, &raw, 2);
    check(protected_search.accepted == 0, "本级加后缀双loss拒绝过度源损失");
    const auto searched = optimize_nodes(models, gold, 3, anchor, Guard{}, Objective::Mean, 1, 1);
    check(searched.accepted > 0 && searched.after.sse == 0 && evaluate(models, gold).sse == 0,
          "完整域增量节点搜索与重新遍历一致");
    check(!models[3].separable_proven, "搜索后清除源曲线证明");
    const auto axes = dp_axes(raw, 17, 2);
    for (const auto &axis : axes) {
        check(axis.front() == 0 && axis.back() == 255, "DP端点");
        for (unsigned i = 1; i < 17; ++i)
            check(axis[i] >= axis[i - 1] + 2, "DP最小间距");
    }
    auto identity = prepare_stage(raw, 17);
    MonotoneReport proof;
    const auto calibrated = exact_monotone(raw, identity, proof);
    check(proof.source_proven && proof.nodes_proven && proof.feasible, "完整结构及精确单调可行域");
    for (unsigned i = 0; i < 256; ++i)
        check(oracle(calibrated, i | i << 8 | i << 16) == (i | i << 8 | i << 16), "单调精确曲线逐码");
    const auto error_grid = error_axes(raw, 17);
    for (const auto &axis : error_grid)
        check(axis.size() == 17 && axis[0] == 0 && axis[16] == 255, "误差驱动网格端点");
    std::puts("精度合同通过：Q24全误差域、独立混合oracle、尾部与预算、联合支撑、box及整数重放");
}
