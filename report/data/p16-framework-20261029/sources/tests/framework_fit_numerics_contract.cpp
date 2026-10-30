/* 拟合数值契约：独立Q16几何、小型设计矩阵和整数边界。
 * 不读取赛事图片，不运行完整色域拟合或性能计时。
 */
#define FLASH_CHROMA_IMPLEMENTATION
#include "fit_chain_experiment.hpp"
#include <cstdio>
#include <cstdlib>

namespace {
void require(bool value, const char* message) {
    if (!value) { std::fprintf(stderr, "拟合数值契约失败：%s\n", message); std::exit(1); }
}
void close(double actual, double expected, const char* message) {
    require(std::abs(actual - expected) <= 1e-8 * (1 + std::abs(expected)), message);
}
using Color = fc_framework::fit_chain_detail::Color;
struct Fixture {
    fc_framework::Stage stage;
    std::array<std::array<unsigned, 17>, 3> knots{};
};
void put32(std::vector<std::uint8_t>& bytes, std::size_t at, std::uint32_t value) {
    for (unsigned i = 0; i < 4; ++i) bytes[at + i] = static_cast<std::uint8_t>(value >> (i * 8));
}
Fixture fixture() {
    Fixture result;
    auto& stage = result.stage; stage.m = 17;
    const std::size_t indices = 16 + 12 * 17, fractions = indices + 768, nodes = fractions + 3072;
    stage.blob.resize(nodes + 17 * 17 * 17 * 3);
    auto& bytes = stage.blob;
    bytes[0] = 'S'; bytes[1] = 'L'; bytes[2] = 'U'; bytes[3] = 'T';
    put32(bytes, 4, 1); put32(bytes, 8, 17);
    for (unsigned axis = 0; axis < 3; ++axis) {
        for (unsigned i = 0; i < 17; ++i) {
            unsigned knot = (i * 255 + 8) / 16;
            if (axis == 1 && i < 16) knot = i * 16;
            if (axis == 2 && i > 0 && i < 16) knot = i % 2 ? knot + 1 : knot - 1;
            result.knots[axis][i] = knot;
            const float value = static_cast<float>(knot);
            std::uint32_t bits; std::memcpy(&bits, &value, 4);
            put32(bytes, 16 + (axis * 17 + i) * 4, bits);
        }
        for (unsigned value = 0; value < 256; ++value) {
            unsigned cell = 0;
            while (cell < 15 && result.knots[axis][cell + 1] <= value) ++cell;
            const unsigned width = result.knots[axis][cell + 1] - result.knots[axis][cell];
            bytes[indices + axis * 256 + value] = static_cast<std::uint8_t>(cell);
            put32(bytes, fractions + (axis * 256 + value) * 4,
                  ((value - result.knots[axis][cell]) * 65536 + width / 2) / width);
        }
    }
    for (std::size_t i = 0; i < 17 * 17 * 17; ++i) for (unsigned c = 0; c < 3; ++c)
        bytes[nodes + i * 3 + c] = static_cast<std::uint8_t>((i * (19 + c * 2) + (i / 17) * 7 + c * 31) % 256);
    return result;
}
// 直接从浮点轴对应的整数结点重建几何，不调用被测坐标/运行时插值。
fc_framework::fit_detail::Geometry geometry(const Fixture& fixture, const Color& color) {
    unsigned cells[3]{}, fractions[3]{}, order[3] = {0, 1, 2};
    const std::size_t stride[3] = {17 * 17, 17, 1};
    for (unsigned axis = 0; axis < 3; ++axis) {
        const auto& knots = fixture.knots[axis];
        for (unsigned i = 1; i < 16; ++i) if (color[axis] >= knots[i]) cells[axis] = i;
        const unsigned width = knots[cells[axis] + 1] - knots[cells[axis]];
        fractions[axis] = static_cast<unsigned>(std::floor(double(color[axis] - knots[cells[axis]]) / width * 65536 + .5));
    }
    std::stable_sort(order, order + 3, [&](unsigned a, unsigned b) { return fractions[a] > fractions[b]; });
    fc_framework::fit_detail::Geometry result;
    result.node[0] = cells[0] * stride[0] + cells[1] * stride[1] + cells[2];
    for (unsigned i = 0; i < 3; ++i) {
        result.mask[i + 1] = result.mask[i] | (4u >> order[i]);
        result.node[i + 1] = result.node[i] + stride[order[i]];
    }
    result.weight[0] = 65536 - fractions[order[0]];
    result.weight[1] = fractions[order[0]] - fractions[order[1]];
    result.weight[2] = fractions[order[1]] - fractions[order[2]];
    result.weight[3] = fractions[order[2]];
    return result;
}
Color interpolate(const Fixture& fixture, const Color& color) {
    const auto g = geometry(fixture, color);
    Color out{};
    for (unsigned c = 0; c < 3; ++c) {
        std::uint64_t sum = 32768;
        for (unsigned i = 0; i < 4; ++i) sum += std::uint64_t(g.weight[i]) * fixture.stage.nodes_data()[g.node[i] * 3 + c];
        out[c] = static_cast<unsigned>(sum / 65536);
    }
    return out;
}
void geometry_contract(const Fixture& fixture) {
    const fc_framework::fit_detail::Coordinates coordinates(fixture.stage);
    std::vector<std::uint8_t> input, expected;
    const unsigned values[] = {0, 1, 14, 15, 16, 17, 31, 32, 63, 127, 128, 239, 240, 254, 255};
    for (unsigned r : values) for (unsigned g : values) for (unsigned b : values) {
        Color color = {r, g, b};
        const auto actual = coordinates.at(r, g, b), reference = geometry(fixture, color);
        unsigned sum = 0;
        for (unsigned i = 0; i < 4; ++i) {
            require(actual.node[i] == reference.node[i] && actual.mask[i] == reference.mask[i] &&
                    actual.weight[i] == reference.weight[i], "Q16端点、等权和轴排序不符");
            sum += actual.weight[i];
        }
        require(sum == 65536, "重心权重不守恒");
        require(fc_framework::fit_chain_detail::apply_nodes(coordinates, fixture.stage, color) == interpolate(fixture, color),
                "链拟合的前缀整数插值不符");
        input.insert(input.end(), {static_cast<std::uint8_t>(r), static_cast<std::uint8_t>(g), static_cast<std::uint8_t>(b)});
        for (unsigned i = 0; i < 4; ++i) color = interpolate(fixture, color);
        for (auto channel : color) expected.push_back(static_cast<std::uint8_t>(channel));
    }
    fc_framework::Chain chain; fc_framework::Options options; options.backend = fc::Backend::Scalar;
    require(chain.prepare({&fixture.stage, &fixture.stage, &fixture.stage, &fixture.stage}, options) == fc::Status::Ok,
            "小型几何运行链准备失败");
    std::vector<std::uint8_t> output(input.size());
    require(chain.apply(input.data(), output.data(), input.size() / 3) == fc::Status::Ok && output == expected,
            "独立四级Q16与实际标量执行结果不符");
}
void matrix_contract(const Fixture& fixture) {
    // 只将正规矩阵夹具缩为3³；不把该尺寸传给比赛Stage或运行时。
    fc_framework::fit_detail::Coordinates coordinates(fixture.stage); coordinates.m = 3;
    for (unsigned k = 0; k < 8; ++k) coordinates.delta[k] = (k & 4 ? 9 : 0) + (k & 2 ? 3 : 0) + (k & 1 ? 1 : 0);
    fc_framework::fit_detail::Normal matrix(coordinates);
    constexpr std::size_t n = 27;
    std::array<std::array<double, n>, n> dense{};
    std::array<std::array<double, 3>, n> rhs{};
    std::vector<std::array<double, 3>> points(n);
    double direct_sse = 0;
    for (std::size_t i = 0; i < n; ++i) for (unsigned c = 0; c < 3; ++c) points[i][c] = double((i * 13 + c * 29) % 251);
    const unsigned orders[6][3] = {{4,2,1},{4,1,2},{2,4,1},{2,1,4},{1,4,2},{1,2,4}};
    for (unsigned r = 0; r < 2; ++r) for (unsigned g = 0; g < 2; ++g) for (unsigned b = 0; b < 2; ++b)
        for (const auto& order : orders) {
            const unsigned masks[] = {0, order[0], order[0] | order[1], 7};
            const double weights[] = {.125, .375, .25, .25};
            const std::size_t base = (r * 3 + g) * 3 + b;
            std::array<double, n> row{};
            for (unsigned i = 0; i < 4; ++i) row[base + coordinates.delta[masks[i]]] = weights[i];
            for (unsigned c = 0; c < 3; ++c) {
                const double target = double(5 + r * 51 + g * 27 + b * 13 + c * 31);
                matrix.target_squared_sum += target * target;
                double prediction = 0;
                for (std::size_t i = 0; i < n; ++i) { rhs[i][c] += row[i] * target; prediction += row[i] * points[i][c]; }
                direct_sse += (prediction - target) * (prediction - target);
            }
            for (std::size_t i = 0; i < n; ++i) for (std::size_t j = 0; j < n; ++j) dense[i][j] += row[i] * row[j];
            for (unsigned i = 0; i < 4; ++i) for (unsigned j = i; j < 4; ++j)
                matrix.h[base + coordinates.delta[masks[i]]][masks[i] ^ masks[j]] += weights[i] * weights[j];
        }
    matrix.rhs.assign(rhs.begin(), rhs.end());
    std::vector<double> x(n), regularizer(n), product;
    for (std::size_t i = 0; i < n; ++i) { x[i] = points[i][1]; regularizer[i] = .125 + i / 100.0; }
    matrix.multiply(x, product, regularizer);
    for (std::size_t i = 0; i < n; ++i) {
        double expected = regularizer[i] * x[i], off = 0;
        for (std::size_t j = 0; j < n; ++j) { expected += dense[i][j] * x[j]; if (i != j) off += dense[i][j] * x[j]; }
        close(product[i], expected, "稀疏上三角对称乘法与显式设计矩阵不符");
        close(matrix.row_off_diagonal(i, points, 1), off, "整数坐标下降非对角项不符");
    }
    close(matrix.sse(points), direct_sse, "正规矩阵二次型与逐样本误差不符");
    // 无数据支持的节点靠正则保留初始值，不能把未观测区域变成零。
    fc_framework::fit_detail::Normal empty(coordinates);
    fc_framework::FitExperimentOptions options; fc_framework::FitChannelReport report;
    const auto solved = fc_framework::fit_detail::solve_channel(empty, 1, points, options, report);
    require(report.converged, "纯正则问题未收敛");
    for (std::size_t i = 0; i < n; ++i) close(solved[i], points[i][1], "无支持节点未保留初值");
}
}
int main() {
    const auto data = fixture(); geometry_contract(data); matrix_contract(data);
    require(fc_framework::fit_detail::integer(-1) == 0 && fc_framework::fit_detail::integer(.5) == 1 &&
            fc_framework::fit_detail::integer(254.5) == 255 && fc_framework::fit_detail::integer(300) == 255,
            "整数舍入或饱和边界不符");
    bool rejected = false;
    try { (void)fc_framework::fit_detail::integer((std::numeric_limits<double>::quiet_NaN)()); }
    catch (const std::runtime_error&) { rejected = true; }
    require(rejected, "非有限拟合值未拒绝");
    std::puts("拟合Q16几何、设计矩阵、无支持节点和整数边界契约通过。");
    return 0;
}
