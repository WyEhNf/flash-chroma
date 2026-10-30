// 同表、单线程RGB24前后对照。拟合与建表在读取任何图片之前完成。
#define FLASH_CHROMA_IMPLEMENTATION
#define FLASH_CHROMA_ENABLE_OPENMP 0
#include "fit_chain_experiment.hpp"
#include "framework_io.hpp"
#include <algorithm>
#include <chrono>
#include <cmath>
#include <filesystem>
#include <fstream>
#include <iomanip>
#include <iostream>
#include <numeric>
#include <random>
#include <sstream>

namespace fs = std::filesystem;
using Clock = std::chrono::steady_clock;
constexpr std::size_t block_pixels = 65536, table_bytes = (std::size_t{1} << 24) * 3;
volatile std::uint64_t consumed = 0;

std::string quote(const std::string& value) {
    std::ostringstream out; out << '"';
    for (const unsigned char c : value) {
        if (c == '"' || c == '\\') out << '\\' << c;
        else if (c < 32) out << "\\u" << std::hex << std::setw(4) << std::setfill('0') << unsigned(c) << std::dec;
        else out << c;
    }
    return out.str() + '"';
}
std::uint64_t hash(const std::vector<std::uint8_t>& value) {
    std::uint64_t result = 14695981039346656037ULL;
    for (const auto byte : value) result = (result ^ byte) * 1099511628211ULL;
    return result;
}
std::string hex(std::uint64_t value) {
    std::ostringstream out; out << std::hex << std::setw(16) << std::setfill('0') << value; return out.str();
}
double milliseconds(Clock::time_point start) {
    return std::chrono::duration<double, std::milli>(Clock::now() - start).count();
}
double median(std::vector<double> values) {
    if (values.empty()) throw std::runtime_error("空计时样本");
    std::sort(values.begin(), values.end()); const auto n = values.size();
    return n % 2 ? values[n / 2] : (values[n / 2 - 1] + values[n / 2]) / 2;
}
void save(const fs::path& path, const std::string& value) {
    if (fs::exists(path)) throw std::runtime_error("拒绝覆盖输出：" + path.string());
    std::ofstream out(path, std::ios::binary); out << value;
    if (!out) throw std::runtime_error("写入失败：" + path.string());
}
enum class Kernel { Legacy, Cached, Stream };
const char* name(Kernel kernel) {
    return kernel == Kernel::Legacy ? "legacy" : kernel == Kernel::Cached ? "cached" : "stream";
}
// 三条路径具有相同分块与分派开销，匹配Runtime的默认65536像素块边界。
__attribute__((noinline)) void invoke(Kernel kernel, const std::uint8_t* table,
                                    const std::uint8_t* input, std::uint8_t* output, std::size_t pixels) {
#if FLASH_CHROMA_ENABLE_AVX2
    for (std::size_t offset = 0; offset < pixels; offset += block_pixels) {
        const auto count = (std::min)(block_pixels, pixels - offset);
        if (kernel == Kernel::Legacy) fc::detail::direct_rgb24_gather_run(table, input + offset * 3, output + offset * 3, count);
        else if (kernel == Kernel::Cached) fc::detail::direct_rgb24_block_run<false>(table, input + offset * 3, output + offset * 3, count);
        else fc::detail::direct_rgb24_block_run<true>(table, input + offset * 3, output + offset * 3, count);
    }
#else
    (void)kernel; (void)table; (void)input; (void)output; (void)pixels;
    throw std::runtime_error("当前构建没有AVX2");
#endif
}
struct Image {
    std::string path;
    std::vector<std::uint8_t> input, expected;
    std::uint64_t input_hash = 0, expected_hash = 0;
};
struct Run {
    std::string scope, phase, kernel, group, sequence;
    unsigned round = 0;
    std::vector<double> image_ms;
    bool verified = false;
    std::uint64_t output_hash = 0;
    double batch_ms() const { return std::accumulate(image_ms.begin(), image_ms.end(), 0.0); }
};
struct AA {
    std::string scope, phase, kernel;
    double median_a = 0, median_b = 0, drift = 0;
    bool passed = false;
};

void batch(std::vector<Run>& runs, const std::vector<Image>& images,
           const std::vector<std::uint8_t>& table, std::vector<std::uint8_t>& hot,
           Kernel kernel, const std::string& scope, const std::string& phase,
           unsigned round, const std::string& group, const std::string& sequence) {
    runs.push_back({scope, phase, name(kernel), group, sequence, round, {}, false, 0});
    auto& run = runs.back();
    for (const auto& image : images) {
        std::vector<std::uint8_t> allocated;
        std::vector<std::uint8_t>* output = &hot;
        if (scope == "hot") {
            // 每个字节均与正确输出不同，避免遗漏写入借用上一轮正确结果。
            for (std::size_t i = 0; i < hot.size(); ++i) hot[i] = image.expected[i] ^ 255u;
            const auto start = Clock::now();
            invoke(kernel, table.data(), image.input.data(), hot.data(), image.input.size() / 3);
            run.image_ms.push_back(milliseconds(start));
        } else {
            const auto start = Clock::now();
            // fresh vector本体构造也位于计时区；分配和零初始化均计入。
            std::vector<std::uint8_t> fresh;
            fresh.resize(image.input.size());
            invoke(kernel, table.data(), image.input.data(), fresh.data(), image.input.size() / 3);
            run.image_ms.push_back(milliseconds(start));
            allocated.swap(fresh); output = &allocated;
        }
        const auto actual_hash = hash(*output); consumed ^= actual_hash;
        run.output_hash = (run.output_hash ^ actual_hash) * 1099511628211ULL;
        if (actual_hash != image.expected_hash || *output != image.expected)
            throw std::runtime_error("输出逐字节核验失败：" + run.kernel + "/" + scope + "/" + image.path);
    }
    run.verified = true;
}

AA aa(std::vector<Run>& runs, const std::vector<Image>& images,
      const std::vector<std::uint8_t>& table, std::vector<std::uint8_t>& hot,
      Kernel kernel, const std::string& scope, const std::string& phase,
      unsigned repetitions, double limit) {
    std::vector<double> a, b;
    for (unsigned i = 0; i < repetitions; ++i) {
        for (unsigned j = 0; j < 2; ++j) {
            const bool first = ((i + j) % 2) == 0;
            batch(runs, images, table, hot, kernel, scope, phase, i,
                  first ? "A" : "B", i % 2 ? "BA" : "AB");
            (first ? a : b).push_back(runs.back().batch_ms());
        }
    }
    const auto ma = median(a), mb = median(b);
    const auto drift = std::abs(ma - mb) / (std::min)(ma, mb);
    return {scope, phase, name(kernel), ma, mb, drift, std::isfinite(drift) && drift <= limit};
}

int self_test() {
    if (!(fc::available_backends() & 2u)) throw std::runtime_error("机器不支持AVX2");
    std::vector<std::uint8_t> table(256 * 3 + 64);
    for (unsigned i = 0; i != 256; ++i) {
        table[i * 3] = static_cast<std::uint8_t>(i ^ 35);
        table[i * 3 + 1] = static_cast<std::uint8_t>(i * 5);
        table[i * 3 + 2] = static_cast<std::uint8_t>(255 - i);
    }
    for (unsigned pixels = 0; pixels != 130; ++pixels) {
        std::vector<std::uint8_t> input(pixels * 3), expected(pixels * 3), output(pixels * 3);
        for (unsigned i = 0; i != pixels; ++i) {
            input[i * 3] = static_cast<std::uint8_t>(i * 11);
            for (unsigned c = 0; c != 3; ++c) expected[i * 3 + c] = table[input[i * 3] * 3 + c];
        }
        for (const auto kernel : {Kernel::Legacy, Kernel::Cached, Kernel::Stream}) {
            for (std::size_t i = 0; i < output.size(); ++i) output[i] = expected[i] ^ 255u;
            invoke(kernel, table.data(), input.data(), output.data(), pixels);
            if (output != expected) throw std::runtime_error("小型接口自检失败");
        }
    }
    std::cout << "{\"passed\":true,\"self_test\":true,\"timing_performed\":false}\n"; return 0;
}

int main(int argc, char** argv) try {
    if (argc == 2 && std::string(argv[1]) == "--self-test") return self_test();
    fs::path output, image_list;
    std::array<std::string, 4> caches;
    unsigned reps = 7, aa_reps = 7, warmup = 2, seed = 20261030;
    double aa_limit = .05; bool screen = false; Kernel selected = Kernel::Stream;
    auto next = [&](int& i) -> std::string { if (++i >= argc) throw std::runtime_error("缺少参数值"); return argv[i]; };
    auto integer = [](const std::string& value) -> unsigned {
        if (value.empty() || value.find_first_not_of("0123456789") != std::string::npos) throw std::runtime_error("非法整数参数");
        const auto result = std::stoull(value); if (result > 0xffffffffULL) throw std::runtime_error("整数溢出");
        return static_cast<unsigned>(result);
    };
    for (int i = 1; i < argc; ++i) {
        const std::string key = argv[i];
        if (key == "--cache") for (auto& path : caches) path = next(i);
        else if (key == "--images") image_list = next(i);
        else if (key == "--output") output = next(i);
        else if (key == "--reps") reps = integer(next(i));
        else if (key == "--aa-reps") aa_reps = integer(next(i));
        else if (key == "--warmup") warmup = integer(next(i));
        else if (key == "--seed") seed = integer(next(i));
        else if (key == "--aa-limit") aa_limit = std::stod(next(i));
        else if (key == "--screen") screen = true;
        else if (key == "--variant") {
            const auto variant = next(i);
            if (variant != "cached" && variant != "stream") throw std::runtime_error("variant必须是cached或stream");
            selected = variant == "cached" ? Kernel::Cached : Kernel::Stream;
        } else throw std::runtime_error("未知参数：" + key);
    }
    if (output.empty() || image_list.empty() || caches[0].empty() || reps < 3 || reps > 50 ||
        aa_reps < 3 || aa_reps > 50 || warmup > 10 || !std::isfinite(aa_limit) || aa_limit < 0 || aa_limit > .1)
        throw std::runtime_error("回归测试参数非法");
    if (!(fc::available_backends() & 2u)) throw std::runtime_error("机器不支持AVX2");
    if (fs::exists(output)) throw std::runtime_error("输出目录已存在，拒绝覆盖");
    fs::create_directories(output);
    std::vector<Run> runs; std::vector<AA> aa_results; std::vector<Image> images;
    bool stable = true, complete = false; std::string error;
    double load_ms = 0, prepare_ms = 0, table_ms = 0;
    std::uint64_t table_hash = 0; fc_framework::FitReport fit_report;
    try {
        const auto loading = Clock::now();
        std::array<std::vector<std::uint16_t>, 4> raw;
        for (unsigned i = 0; i != 4; ++i) fc_framework_io::read_u16_cache(caches[i], raw[i]);
        load_ms = milliseconds(loading);
        const auto preparing = Clock::now();
        fc_framework::FitOptions fit_options; fit_options.grid = fc_framework::Grid::FrameworkStep;
        std::array<fc_framework::Stage, 4> stages;
        for (unsigned i = 0; i != 4; ++i) stages[i] = fc_framework::prepare_stage(raw[i], 33, fit_options);
        stages[3] = fc_framework::fit_chain_last(raw, stages, fit_report);
        fc_framework::Options options; options.structure = false; options.backend = fc::Backend::Avx2;
        options.threads = 1; options.representation = fc::Representation::Sparse; options.block_pixels = block_pixels;
        fc_framework::Chain chain;
        if (chain.prepare({{&stages[0], &stages[1], &stages[2], &stages[3]}}, options) != fc::Status::Ok)
            throw std::runtime_error("固定稀疏链准备失败");
        prepare_ms = milliseconds(preparing);
        for (unsigned i = 0; i != 4; ++i) {
            fc_framework_io::write_rgb_file_new((output / ("stage-" + std::to_string(i + 1) + ".slut")).string(), stages[i].blob);
            std::vector<std::uint16_t>().swap(raw[i]);
        }
        const auto table_start = Clock::now();
        std::vector<std::uint8_t> table(table_bytes + 64, 0), codes(block_pixels * 3);
        for (std::size_t first = 0; first < (std::size_t{1} << 24); first += block_pixels) {
            for (std::size_t i = 0; i != block_pixels; ++i) {
                const auto code = first + i;
                codes[i * 3] = static_cast<std::uint8_t>(code);
                codes[i * 3 + 1] = static_cast<std::uint8_t>(code >> 8);
                codes[i * 3 + 2] = static_cast<std::uint8_t>(code >> 16);
            }
            if (chain.apply(codes.data(), table.data() + first * 3, block_pixels) != fc::Status::Ok)
                throw std::runtime_error("完整RGB域共同建表失败");
        }
        table_ms = milliseconds(table_start); table_hash = hash(table);
        fc_framework_io::write_rgb_file_new((output / "shared-table.rgb24").string(), table);
        // 从此处才读取图片列表与像素，拟合/建表没有图片信息。
        std::ifstream list(image_list); if (!list) throw std::runtime_error("图片列表读取失败");
        std::string line;
        while (std::getline(list, line)) {
            if (!line.empty() && line.back() == '\r') line.pop_back();
            if (line.empty() || line[0] == '#') continue;
            Image image; image.path = line;
            image.input = fc_framework_io::read_rgb_file(line, 1024 * 768 * 3);
            image.expected.resize(image.input.size());
            for (std::size_t i = 0; i < image.input.size(); i += 3) {
                const auto index = (std::size_t(image.input[i]) | (std::size_t(image.input[i + 1]) << 8) |
                                    (std::size_t(image.input[i + 2]) << 16)) * 3;
                std::copy_n(table.data() + index, 3, image.expected.data() + i);
            }
            image.input_hash = hash(image.input); image.expected_hash = hash(image.expected);
            images.push_back(std::move(image));
        }
        if (images.empty() || images.size() > 100 || (screen && images.size() != 4) || (!screen && images.size() != 100))
            throw std::runtime_error("screen必须恰4图，正式回归必须恰100图");
        std::vector<std::uint8_t> hot(images[0].input.size()); std::mt19937 rng(seed);
        for (const std::string scope : {"hot", "allocated"}) {
            const std::vector<Kernel> kernels = screen ? std::vector<Kernel>{Kernel::Legacy, Kernel::Cached, Kernel::Stream}
                                                      : std::vector<Kernel>{Kernel::Legacy, selected};
            for (unsigned i = 0; i < warmup; ++i) for (const auto kernel : kernels)
                batch(runs, images, table, hot, kernel, scope, "warmup", i, "", "");
            if (!screen) {
                for (const auto kernel : kernels) {
                    aa_results.push_back(aa(runs, images, table, hot, kernel, scope, "pre_aa", aa_reps, aa_limit));
                    stable = stable && aa_results.back().passed;
                }
                if (!stable) break;
            }
            for (unsigned i = 0; i < reps; ++i) {
                if (screen) {
                    auto order = kernels; std::shuffle(order.begin(), order.end(), rng);
                    for (const auto kernel : order) batch(runs, images, table, hot, kernel, scope, "screen", i, "", "randomized");
                } else {
                    const bool abba = (rng() & 1u) != 0;
                    const std::array<Kernel, 4> order = abba ? std::array<Kernel, 4>{{Kernel::Legacy, selected, selected, Kernel::Legacy}}
                                                           : std::array<Kernel, 4>{{selected, Kernel::Legacy, Kernel::Legacy, selected}};
                    for (const auto kernel : order) batch(runs, images, table, hot, kernel, scope, "comparison", i, "", abba ? "ABBA" : "BAAB");
                }
            }
            if (!screen) for (const auto kernel : kernels) {
                aa_results.push_back(aa(runs, images, table, hot, kernel, scope, "post_aa", aa_reps, aa_limit));
                stable = stable && aa_results.back().passed;
            }
            if (!stable) break;
        }
        complete = true;
    } catch (const std::exception& failure) { error = failure.what(); }
    std::ostringstream out; out << std::setprecision(17);
    out << "{\"schema\":\"rgb24_regression_v1\",\"completed\":" << (complete ? "true" : "false")
        << ",\"error\":" << quote(error) << ",\"screen\":" << (screen ? "true" : "false")
        << ",\"stable\":" << (screen ? "null" : stable ? "true" : "false") << ",\"variant\":" << quote(name(selected))
        << ",\"threads\":1,\"block_pixels\":" << block_pixels << ",\"seed\":" << seed << ",\"reps\":" << reps
        << ",\"aa_reps\":" << aa_reps << ",\"aa_limit\":" << aa_limit << ",\"warmup\":" << warmup
        << ",\"model\":{\"m\":[33,33,33,33],\"grid\":\"framework\",\"fit\":\"chain_ls\",\"fit_uses_images\":false,\"candidate_used\":"
        << (fit_report.candidate_used ? "true" : "false") << ",\"samples\":" << fit_report.samples
        << ",\"baseline_full_domain_mean\":" << fit_report.baseline.mean << ",\"candidate_full_domain_mean\":" << fit_report.candidate.mean
        << ",\"baseline_full_domain_sse\":" << fit_report.baseline.sse << ",\"candidate_full_domain_sse\":" << fit_report.candidate.sse << '}'
        << ",\"source_cache_load_ms\":" << load_ms << ",\"model_prepare_ms\":" << prepare_ms << ",\"shared_table_build_ms\":" << table_ms
        << ",\"shared_table_bytes\":" << table_bytes + 64 << ",\"shared_table_fnv1a64\":" << quote(hex(table_hash))
        << ",\"output_consumed\":true,\"timing_scope\":\"hot预分配且计时外逐字节poison；allocated从fresh输出构造/resize起计；三核均每65536像素分块；不含Chain状态检查，须另用原main确认。校验和hash在计时外。\",\"images\":[";
    for (std::size_t i = 0; i < images.size(); ++i) {
        if (i) out << ',';
        out << "{\"index\":" << i + 1 << ",\"path\":" << quote(images[i].path) << ",\"bytes\":" << images[i].input.size()
            << ",\"input_fnv1a64\":" << quote(hex(images[i].input_hash)) << ",\"expected_fnv1a64\":" << quote(hex(images[i].expected_hash)) << '}';
    }
    out << "],\"aa\":[";
    for (std::size_t i = 0; i < aa_results.size(); ++i) {
        if (i) out << ',';
        const auto& value = aa_results[i];
        out << "{\"scope\":" << quote(value.scope) << ",\"phase\":" << quote(value.phase) << ",\"kernel\":" << quote(value.kernel)
            << ",\"median_a_ms\":" << value.median_a << ",\"median_b_ms\":" << value.median_b << ",\"relative_drift\":" << value.drift
            << ",\"passed\":" << (value.passed ? "true" : "false") << '}';
    }
    out << "],\"runs\":[";
    for (std::size_t i = 0; i < runs.size(); ++i) {
        if (i) out << ',';
        const auto& value = runs[i];
        out << "{\"scope\":" << quote(value.scope) << ",\"phase\":" << quote(value.phase) << ",\"kernel\":" << quote(value.kernel)
            << ",\"group\":" << quote(value.group) << ",\"sequence\":" << quote(value.sequence) << ",\"round\":" << value.round
            << ",\"verified\":" << (value.verified ? "true" : "false") << ",\"output_fnv1a64\":" << quote(hex(value.output_hash))
            << ",\"batch_ms\":" << value.batch_ms() << ",\"image_ms\":[";
        for (std::size_t j = 0; j < value.image_ms.size(); ++j) { if (j) out << ','; out << value.image_ms[j]; }
        out << "]}";
    }
    out << "]}\n"; save(output / "results.json", out.str());
    std::cout << "{\"completed\":" << (complete ? "true" : "false") << ",\"screen\":" << (screen ? "true" : "false")
              << ",\"stable\":" << (screen ? "null" : stable ? "true" : "false") << "}\n";
    return !complete ? 1 : !screen && !stable ? 3 : 0;
} catch (const std::exception& error) { std::cerr << error.what() << '\n'; return 1; }
