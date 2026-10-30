/* 历史非均匀轴及分输出几何的LUT-only原生入口。所有预算在读图前固定。 */
#ifndef FLASH_CHROMA_FRAMEWORK_PRECISION_GEOMETRY_HPP
#define FLASH_CHROMA_FRAMEWORK_PRECISION_GEOMETRY_HPP
#include "fit_chain_experiment.hpp"
#include <numeric>
#include <string>

namespace fc_framework {
namespace precision {
using Models = std::array<Stage, 4>;
using Sources = std::array<std::vector<std::uint16_t>, 4>;
using Axes = std::array<std::vector<unsigned>, 3>;
inline unsigned component(std::uint32_t rgb, unsigned c) { return (rgb >> (8 * c)) & 255u; }
inline std::uint32_t source_color(const std::vector<std::uint16_t> &raw, std::uint32_t rgb) {
    const auto at =
        ((std::size_t(component(rgb, 2)) * 256 + component(rgb, 1)) * 256 + component(rgb, 0)) * 3;
    return std::uint32_t(std::uint8_t(raw[at + 2] / 16)) |
           (std::uint32_t(std::uint8_t(raw[at + 1] / 16)) << 8) |
           (std::uint32_t(std::uint8_t(raw[at] / 16)) << 16);
}
struct Evaluator {
    std::array<fc_core::fc_model, 4> views;
    std::array<Interpolation, 4> kinds;
    explicit Evaluator(const Models &models) {
        for (unsigned i = 0; i < 4; ++i) {
            views[i] = detail::view(models[i]);
            kinds[i] = models[i].interpolation;
        }
    }
    std::uint32_t map(std::uint32_t rgb, unsigned begin = 0, unsigned end = 4) const {
        for (unsigned i = begin; i < end; ++i)
            rgb = detail::map(views[i], kinds[i], rgb);
        return rgb;
    }
};
struct Geometry {
    std::array<std::size_t, 8> node{};
    std::array<std::uint64_t, 8> weight{};
    unsigned count = 0, shift = 16;
};
inline Geometry geometry(const fc_core::fc_model &m, Interpolation kind, std::uint32_t rgb,
                         unsigned channel) {
    Geometry g;
    const unsigned v[3] = {component(rgb, 0), component(rgb, 1), component(rgb, 2)};
    const std::size_t d[3] = {std::size_t(m.m) * m.m, m.m, 1};
    const std::size_t base = m.index[v[0]] * d[0] + m.index[256 + v[1]] * d[1] + m.index[512 + v[2]];
    const auto *fractions = m.sidecar.data ? m.sidecar.data + channel * 3072 : m.fraction_le;
    std::uint32_t f[3];
    for (unsigned a = 0; a < 3; ++a)
        f[a] = fc_core::fc_detail_read32(fractions + (a * 256 + v[a]) * 4);
    if (kind == Interpolation::TrilinearQ16) {
        g.count = 8;
        g.shift = 48;
        for (unsigned mask = 0; mask < 8; ++mask) {
            g.node[mask] = base;
            g.weight[mask] = 1;
            for (unsigned a = 0; a < 3; ++a) {
                const bool hi = (mask & (4u >> a)) != 0;
                g.node[mask] += hi ? d[a] : 0;
                g.weight[mask] *= hi ? f[a] : 65536 - f[a];
            }
        }
    } else {
        unsigned order[3] = {0, 1, 2};
        if (f[order[0]] < f[order[1]])
            std::swap(order[0], order[1]);
        if (f[order[1]] < f[order[2]])
            std::swap(order[1], order[2]);
        if (f[order[0]] < f[order[1]])
            std::swap(order[0], order[1]);
        g.count = 4;
        g.node[0] = base;
        g.node[1] = base + d[order[0]];
        g.node[2] = g.node[1] + d[order[1]];
        g.node[3] = base + d[0] + d[1] + 1;
        g.weight[0] = 65536 - f[order[0]];
        g.weight[1] = f[order[0]] - f[order[1]];
        g.weight[2] = f[order[1]] - f[order[2]];
        g.weight[3] = f[order[2]];
    }
    return g;
}
inline void clear_proof(Stage &stage) {
    stage.separable_proven = false;
    stage.proof_nodes = 0;
}
inline Axes fixed_axes(unsigned m, Grid kind) {
    if (m < 17 || m > 33)
        throw std::invalid_argument("节点尺寸须在17..33");
    Axes axes;
    for (auto &a : axes) {
        a.resize(m);
        for (unsigned i = 0; i < m; ++i)
            a[i] = kind == Grid::FrameworkStep ? i * (256 / (m - 1)) : (i * 255 + (m - 1) / 2) / (m - 1);
        a.back() = 255;
    }
    return axes;
}
inline Axes curvature_axes(const std::vector<std::uint16_t> &raw, unsigned m) {
    if (raw.size() != dense_values)
        throw std::invalid_argument("非均匀网格要求完整LUT");
    Axes axes = fixed_axes(m, Grid::UniformRounded);
    for (unsigned a = 0; a < 3; ++a) {
        std::array<double, 256> density{}, cdf{};
        unsigned coord[3]{};
        for (unsigned u = 0; u < 256; u += 4)
            for (unsigned v = 0; v < 256; v += 4) {
                coord[(a + 1) % 3] = u;
                coord[(a + 2) % 3] = v;
                for (unsigned x = 1; x < 255; ++x)
                    for (unsigned c = 0; c < 3; ++c) {
                        coord[a] = x - 1;
                        const int left = detail::source(raw, coord[0], coord[1], coord[2], c);
                        coord[a] = x;
                        const int middle = detail::source(raw, coord[0], coord[1], coord[2], c);
                        coord[a] = x + 1;
                        const int right = detail::source(raw, coord[0], coord[1], coord[2], c);
                        density[x] += std::abs(left - 2 * middle + right);
                    }
            }
        density[0] = density[1];
        density[255] = density[254];
        double average = 0;
        for (auto &d : density) {
            d = std::pow(d / (64.0 * 64 * 3), .4);
            average += d / 256;
        }
        for (auto &d : density)
            d = .5 + .5 * d / (average + 1e-8);
        for (unsigned x = 1; x < 256; ++x)
            cdf[x] = cdf[x - 1] + (density[x - 1] + density[x]) * .5;
        for (unsigned i = 1; i < m - 1; ++i) {
            const double q = cdf.back() * i / (m - 1);
            unsigned x = 1;
            while (cdf[x] < q)
                ++x;
            const double value = x - 1 + (q - cdf[x - 1]) / (cdf[x] - cdf[x - 1]);
            axes[a][i] = (std::min)(255 - 2 * (m - 1 - i),
                                    (std::max)(axes[a][i - 1] + 2, unsigned(std::floor(value + .5))));
        }
    }
    return axes;
}
// 与历史轴弦SSE动态规划相同：所有256个轴位置、固定垂直LUT探针、间距2..ceil(2*ideal)。
inline Axes dp_axes(const std::vector<std::uint16_t> &raw, unsigned m, unsigned probes = 24) {
    if (raw.size() != dense_values || probes < 2 || probes > 64)
        throw std::invalid_argument("DP源或探针数非法");
    Axes axes = fixed_axes(m, Grid::UniformRounded);
    const unsigned width = probes * probes * 3;
    const double ideal = 255.0 / (m - 1);
    const unsigned max_step = unsigned(std::ceil(2 * ideal));
    for (unsigned a = 0; a < 3; ++a) {
        std::vector<double> y(256 * width), gram(256 * 256), prefix(256 * 257), weighted(256 * 257),
            norm(257), cost(256 * 256, INFINITY);
        unsigned coord[3]{};
        for (unsigned x = 0; x < 256; ++x) {
            coord[a] = x;
            for (unsigned u = 0; u < probes; ++u)
                for (unsigned v = 0; v < probes; ++v) {
                    coord[(a + 1) % 3] = (u * 255 + (probes - 1) / 2) / (probes - 1);
                    coord[(a + 2) % 3] = (v * 255 + (probes - 1) / 2) / (probes - 1);
                    for (unsigned c = 0; c < 3; ++c)
                        y[x * width + (u * probes + v) * 3 + c] =
                            detail::source(raw, coord[0], coord[1], coord[2], c);
                }
        }
        for (unsigned x = 0; x < 256; ++x)
            for (unsigned z = 0; z <= x; ++z) {
                double value = 0;
                for (unsigned k = 0; k < width; ++k)
                    value += y[x * width + k] * y[z * width + k];
                gram[x * 256 + z] = gram[z * 256 + x] = value / width;
            }
        for (unsigned x = 0; x < 256; ++x) {
            norm[x + 1] = norm[x] + gram[x * 256 + x];
            for (unsigned z = 0; z < 256; ++z) {
                prefix[x * 257 + z + 1] = prefix[x * 257 + z] + gram[x * 256 + z];
                weighted[x * 257 + z + 1] = weighted[x * 257 + z] + z * gram[x * 256 + z];
            }
        }
        for (unsigned x = 0; x < 254; ++x)
            for (unsigned z = x + 2; z < 256 && z <= x + max_step; ++z) {
                const double w = z - x, sa = prefix[x * 257 + z + 1] - prefix[x * 257 + x],
                             sb = prefix[z * 257 + z + 1] - prefix[z * 257 + x];
                const double xa = weighted[x * 257 + z + 1] - weighted[x * 257 + x],
                             xb = weighted[z * 257 + z + 1] - weighted[z * 257 + x];
                const double cross = 2 * (z * sa - xa + xb - x * sb) / w;
                const double predicted =
                    (w + 1) * (2 * w + 1) / (6 * w) * (gram[x * 256 + x] + gram[z * 256 + z]) +
                    (w + 1) * (w - 1) / (3 * w) * gram[x * 256 + z];
                cost[x * 256 + z] = (std::max)(0.0, norm[z + 1] - norm[x] - cross + predicted) +
                                    1e-6 * (w - ideal) * (w - ideal);
            }
        std::vector<double> dp(m * 256, INFINITY);
        std::vector<unsigned> parent(m * 256, 256);
        dp[0] = 0;
        for (unsigned s = 1; s < m; ++s)
            for (unsigned end = 2 * s; end < 256 && end <= max_step * s; ++end) {
                const unsigned start = (std::max)(2 * (s - 1), end > max_step ? end - max_step : 0u);
                for (unsigned begin = start; begin + 2 <= end; ++begin) {
                    const double value = dp[(s - 1) * 256 + begin] + cost[begin * 256 + end];
                    if (value < dp[s * 256 + end]) {
                        dp[s * 256 + end] = value;
                        parent[s * 256 + end] = begin;
                    }
                }
            }
        if (!std::isfinite(dp[(m - 1) * 256 + 255]))
            throw std::runtime_error("DP没有可行端点路径");
        unsigned end = 255;
        for (unsigned s = m - 1; s > 0; --s) {
            axes[a][s] = end;
            end = parent[s * 256 + end];
        }
        axes[a][0] = 0;
    }
    return axes;
}
inline void initialize_sidecar(Stage &stage) {
    if (!stage.fractions.empty())
        return;
    const auto m = detail::view(stage);
    stage.fractions.resize(9216);
    for (unsigned c = 0; c < 3; ++c)
        std::copy(m.fraction_le, m.fraction_le + 3072, stage.fractions.begin() + c * 3072);
}
inline Axes error_axes(const std::vector<std::uint16_t> &raw, unsigned m) {
    FitOptions f;
    f.prove_structure = false;
    f.grid = Grid::UniformRounded;
    const auto pilot = prepare_stage(raw, m, f);
    const auto view = detail::view(pilot);
    std::array<std::array<double, 32>, 3> profile{};
    std::array<unsigned, 32> code{};
    for (unsigned i = 0; i < 32; ++i)
        code[i] = (i * 255 + 15) / 31;
    for (unsigned r = 0; r < 32; ++r)
        for (unsigned g = 0; g < 32; ++g)
            for (unsigned b = 0; b < 32; ++b) {
                const auto rgb = code[r] | code[g] << 8 | code[b] << 16;
                const auto predicted = detail::map(view, Interpolation::TetraQ16, rgb),
                           target = source_color(raw, rgb);
                double error = 0;
                for (unsigned c = 0; c < 3; ++c) {
                    const int d = int(component(predicted, c)) - int(component(target, c));
                    error += d * d;
                }
                error = std::sqrt(error);
                profile[0][r] += error / 1024;
                profile[1][g] += error / 1024;
                profile[2][b] += error / 1024;
            }
    auto axes = fixed_axes(m, Grid::UniformRounded);
    for (unsigned a = 0; a < 3; ++a) {
        double average = 0;
        for (auto x : profile[a])
            average += x / 32;
        std::array<double, 32> density{}, cdf{};
        for (unsigned x = 0; x < 32; ++x)
            density[x] = .5 + .5 * (profile[a][x] + .25) / (average + .25);
        for (unsigned x = 1; x < 32; ++x)
            cdf[x] = cdf[x - 1] + (density[x] + density[x - 1]) * .5;
        for (unsigned i = 1; i < m - 1; ++i) {
            const double q = cdf.back() * i / (m - 1);
            unsigned x = 1;
            while (cdf[x] < q)
                ++x;
            const double value =
                code[x - 1] + (code[x] - code[x - 1]) * (q - cdf[x - 1]) / (cdf[x] - cdf[x - 1]);
            axes[a][i] = (std::min)(255 - 2 * (m - 1 - i),
                                    (std::max)(axes[a][i - 1] + 2, unsigned(std::floor(value + .5))));
        }
    }
    return axes;
}
struct MonotoneReport {
    bool source_proven = false, nodes_proven = false, feasible = false;
    std::array<unsigned, 3> axes{};
};
// 轴置换/共享均可；完整原表和节点张量逐值证明后，交舍入区间及单调域。
inline Stage exact_monotone(const std::vector<std::uint16_t> &raw, const Stage &initial,
                            MonotoneReport &report, unsigned max_shift = 4096) {
    if (raw.size() != dense_values || max_shift > 65536 || !initial.fractions.empty())
        throw std::invalid_argument("精确单调校准源、偏移或共享坐标非法");
    report = {};
    std::array<std::array<std::array<std::uint8_t, 256>, 3>, 3> curves{};
    bool possible[3][3];
    for (unsigned c = 0; c < 3; ++c)
        for (unsigned a = 0; a < 3; ++a) {
            possible[c][a] = true;
            for (unsigned v = 0; v < 256; ++v) {
                unsigned xyz[3]{};
                xyz[a] = v;
                curves[c][a][v] = detail::source(raw, xyz[0], xyz[1], xyz[2], c);
            }
        }
    for (std::uint32_t rgb = 0; rgb < dense_nodes; ++rgb) {
        const auto target = source_color(raw, rgb);
        for (unsigned c = 0; c < 3; ++c)
            for (unsigned a = 0; a < 3; ++a)
                possible[c][a] = possible[c][a] && (component(target, c) == curves[c][a][component(rgb, a)]);
    }
    for (unsigned c = 0; c < 3; ++c) {
        unsigned a = 0;
        while (a < 3 && !possible[c][a])
            ++a;
        if (a == 3)
            return initial;
        report.axes[c] = a;
    }
    report.source_proven = true;
    const auto view = detail::view(initial);
    const unsigned m = initial.m;
    const std::size_t stride[3] = {std::size_t(m) * m, m, 1};
    for (std::size_t i = 0; i < initial.node_bytes() / 3; ++i)
        for (unsigned c = 0; c < 3; ++c) {
            const auto a = report.axes[c];
            const auto at = (i / stride[a]) % m;
            if (initial.nodes_data()[3 * i + c] != initial.nodes_data()[3 * at * stride[a] + c])
                return initial;
        }
    report.nodes_proven = true;
    std::array<std::array<int, 256>, 3> lower{}, upper{}, original{};
    for (unsigned a = 0; a < 3; ++a)
        for (unsigned v = 0; v < 256; ++v) {
            const int f = int(fc_core::fc_detail_read32(view.fraction_le + 4 * (a * 256 + v)));
            original[a][v] = f;
            lower[a][v] = (std::max)(0, f - int(max_shift));
            upper[a][v] = (std::min)(65536, f + int(max_shift));
            if (v == 0 || v == 255)
                lower[a][v] = upper[a][v] = f;
        }
    for (unsigned c = 0; c < 3; ++c) {
        const auto a = report.axes[c];
        for (unsigned v = 0; v < 256; ++v) {
            const unsigned cell = view.index[a * 256 + v];
            const int left = initial.nodes_data()[3 * cell * stride[a] + c],
                      right = initial.nodes_data()[3 * (cell + 1) * stride[a] + c], target = curves[c][a][v];
            // 二分找到全部能舍入到target的Q16整数，递减曲线统一翻转坐标。
            const bool reverse = right < left;
            const int lo = (std::min)(left, right), hi = (std::max)(left, right);
            auto first = [&](int threshold) {
                int l = 0, h = 65537;
                while (l < h) {
                    const int mid = l + (h - l) / 2;
                    const int value = (lo * 65536 + (hi - lo) * mid + 32768) >> 16;
                    if (value >= threshold)
                        h = mid;
                    else
                        l = mid + 1;
                }
                return l;
            };
            int l = first(target), h = first(target + 1) - 1;
            if (reverse) {
                const int old = l;
                l = 65536 - h;
                h = 65536 - old;
            }
            lower[a][v] = (std::max)(lower[a][v], l);
            upper[a][v] = (std::min)(upper[a][v], h);
        }
    }
    Stage result = initial;
    for (unsigned a = 0; a < 3; ++a) {
        std::array<int, 256> low{}, high{};
        for (unsigned v = 0; v < 256; ++v) {
            const int offset = int(view.index[a * 256 + v]) * 65536;
            low[v] = lower[a][v] + offset;
            high[v] = upper[a][v] + offset;
            if (v && original[a][v] + offset < original[a][v - 1] + int(view.index[a * 256 + v - 1]) * 65536)
                return initial;
            if (v)
                low[v] = (std::max)(low[v], low[v - 1]);
        }
        for (int v = 254; v >= 0; --v)
            high[v] = (std::min)(high[v], high[v + 1]);
        for (unsigned v = 0; v < 256; ++v) {
            if (low[v] > high[v])
                return initial;
            const int offset = int(view.index[a * 256 + v]) * 65536;
            const int q = (std::min)(high[v], (std::max)(low[v], offset + original[a][v]));
            detail::put32(result.blob, 16 + 12 * m + 768 + 4 * (a * 256 + v), q - offset);
        }
    }
    // 原表证明只支持源函数，清除可绕过当前稀疏节点的旧资格。
    clear_proof(result);
    report.feasible = true;
    return result;
}
} // namespace precision
} // namespace fc_framework
#endif
