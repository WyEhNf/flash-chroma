
#define FLASH_CHROMA_IMPLEMENTATION
#define FLASH_CHROMA_ENABLE_OPENMP 0
#include "flash_chroma_framework.hpp"
#include <cstdio>
#include <filesystem>
#include <memory>

// 比赛适配只允许单线程；全部准备仅使用LUT，发生在图像读取之前。
std::array<unsigned, 4> fc_sizes{{33, 33, 33, 33}};
fc_framework::FitOptions fc_fit;
fc_framework::Options fc_options;
fc_framework::Chain fc_prepared;
std::array<const fc_framework::Stage*, 4> fc_prepared_stages{};
int fc_image_count = 4;
std::string fc_fit_method = "sample";
// 偏好请求只在批次开始前解析，映射期间不读取控制文件或重选。
bool fc_use_preference = false;
std::string fc_preference_spec;
std::string fc_candidate_sizes = "17;25;33";
std::string fc_candidate_modes = "sparse,direct_rgb24";
double fc_max_mean_error = -1, fc_max_pixel_error = -1, fc_max_ms_per_mp = -1;
std::size_t fc_max_runtime_bytes = (std::numeric_limits<std::size_t>::max)();
std::size_t fc_max_workspace_bytes = 64 * fc::MiB;
bool fc_allow_unstable_time = false;
unsigned fc_calibration_reps = 5;
std::string fc_selection_report_path;

double fc_nonnegative_number(const std::string& text) {
    if (text.empty() || text.find_first_of(" \t\r\n") != std::string::npos)
        throw std::runtime_error("数值参数必须是有限非负数");
    std::size_t used = 0;
    const double value = std::stod(text, &used);
    if (used != text.size() || !std::isfinite(value) || value < 0)
        throw std::runtime_error("数值参数必须是有限非负数");
    return value;
}

std::vector<std::string> fc_split(const std::string& text, char separator) {
    std::vector<std::string> result;
    std::size_t start = 0;
    while (start <= text.size()) {
        const auto end = text.find(separator, start);
        auto item = text.substr(start, end == std::string::npos ? end : end - start);
        if (item.empty()) throw std::runtime_error("参数列表不能含空项");
        result.push_back(std::move(item));
        if (end == std::string::npos) break;
        start = end + 1;
    }
    return result;
}

fc::Preference fc_parse_preference(const std::string& text) {
    const auto parts = fc_split(text, ',');
    if (parts.size() != 3) throw std::runtime_error("偏好必须为A,B,C三个0..1的连续权重");
    fc::Preference value{fc_nonnegative_number(parts[0]), fc_nonnegative_number(parts[1]), fc_nonnegative_number(parts[2])};
    if (value.accuracy > 1 || value.speed > 1 || value.compactness > 1 ||
        !(value.accuracy + value.speed + value.compactness > 0))
        throw std::runtime_error("偏好权重各自必须在0..1内且不能全零");
    return value;
}

std::array<unsigned, 4> fc_parse_sizes(const std::string& text) {
    const auto parts = fc_split(text, ',');
    if (parts.size() != 1 && parts.size() != 4) throw std::runtime_error("必须给一个统一m或四个逐级m");
    std::array<unsigned, 4> result{};
    for (unsigned i = 0; i != 4; ++i) {
        const auto& token = parts[parts.size() == 1 ? 0 : i];
        if (token.find_first_not_of("0123456789") != std::string::npos)
            throw std::runtime_error("m必须为17..33的整数");
        const auto number = std::stoul(token);
        if (number < 17 || number > 33) throw std::runtime_error("m必须在17..33内");
        result[i] = static_cast<unsigned>(number);
    }
    return result;
}

std::size_t fc_mib_budget(const std::string& text) {
    const auto value = fc_nonnegative_number(text);
    // 避免double将SIZE_MAX向上取整后触发浮点到整数的越界转换。
    const long double bytes = static_cast<long double>(value) * fc::MiB;
    if (bytes >= static_cast<long double>((std::numeric_limits<std::size_t>::max)()))
        throw std::runtime_error("内存预算超出平台范围");
    return static_cast<std::size_t>(bytes);
}

void fc_print_fit(unsigned stage, const fc_framework::FitReport& report) {
    std::printf("Fit stage=%u method=%s accepted=%d samples=%zu before_mean=%.12f after_mean=%.12f before_sse=%llu after_sse=%llu seconds=%.6f\n",
        stage, fc_fit_method.c_str(), int(report.candidate_used), report.samples,
        report.baseline.mean, report.candidate.mean,
        static_cast<unsigned long long>(report.baseline.sse), static_cast<unsigned long long>(report.candidate.sse),
        report.assembly_seconds + report.solve_seconds + report.evaluation_seconds);
}

void fc_arguments(int argc, char** argv) {
    int positional_end = 1;
    while (positional_end < argc && std::string(argv[positional_end]).rfind("--", 0) != 0) ++positional_end;
    if (positional_end > 8) throw std::runtime_error("位置参数过多，请用--help查看接口");
    if (positional_end == 1 && argc > 1) throw std::runtime_error("偏好选项前须先提供data目录");
    const int total = argc;
    argc = positional_end;
    if (argc >= 3) {
        std::string spec = argv[2];
        std::vector<unsigned> sizes;
        std::size_t start = 0;
        while (start <= spec.size()) {
            const auto end = spec.find(',', start);
            const auto token = spec.substr(start, end == std::string::npos ? end : end-start);
            if (token.empty() || token.find_first_not_of("0123456789") != std::string::npos)
                throw std::runtime_error("m必须为17..33的整数或四个逗号分隔整数");
            const auto value = std::stoul(token);
            if (value < 17 || value > 33) throw std::runtime_error("m必须在17..33内");
            sizes.push_back(static_cast<unsigned>(value));
            if (end == std::string::npos) break;
            start = end + 1;
        }
        if (sizes.size() == 1) fc_sizes.fill(sizes[0]);
        else if (sizes.size() == 4) std::copy(sizes.begin(), sizes.end(), fc_sizes.begin());
        else throw std::runtime_error("必须给一个统一m或四个逐级m");
    }
    if (argc >= 4) {
        const std::string mode = argv[3];
        fc_options.structure = mode == "auto";
        if (mode == "auto" || mode == "sparse") fc_options.representation = fc::Representation::Sparse;
        else if (mode == "direct_u8") fc_options.representation = fc::Representation::DirectU8;
        else if (mode == "direct_u16") fc_options.representation = fc::Representation::DirectU16;
        else if (mode == "direct_rgb24") fc_options.representation = fc::Representation::DirectRGB24;
        else throw std::runtime_error("模式应为auto/sparse/direct_u8/direct_u16/direct_rgb24");
    }
    if (argc >= 5) {
        const std::string backend = argv[4];
        if (backend == "auto") fc_options.backend = fc::Backend::Auto;
        else if (backend == "scalar") fc_options.backend = fc::Backend::Scalar;
        else if (backend == "avx2") fc_options.backend = fc::Backend::Avx2;
        else throw std::runtime_error("后端应为auto/scalar/avx2");
    }
    if (argc >= 6) {
        const std::string grid = argv[5];
        if (grid == "uniform") fc_fit.grid = fc_framework::Grid::UniformRounded;
        else if (grid == "framework") fc_fit.grid = fc_framework::Grid::FrameworkStep;
        else throw std::runtime_error("网格应为uniform/framework");
    }
    if (argc >= 7) {
        const std::string count = argv[6];
        if (count.empty() || count.find_first_not_of("0123456789") != std::string::npos)
            throw std::runtime_error("图片数必须为1..100整数");
        fc_image_count = std::stoi(count);
        if (fc_image_count < 1 || fc_image_count > 100) throw std::runtime_error("图片数必须为1..100");
    }
    if (argc >= 8) {
        fc_fit_method = argv[7];
        if (fc_fit_method != "sample" && fc_fit_method != "independent_ls" && fc_fit_method != "chain_ls")
            throw std::runtime_error("拟合应为sample/independent_ls/chain_ls");
    }
    std::vector<std::string> seen;
    for (int i = positional_end; i < total; ++i) {
        const std::string key = argv[i];
        if (std::find(seen.begin(), seen.end(), key) != seen.end()) throw std::runtime_error("选项重复：" + key);
        seen.push_back(key);
        if (key == "--allow-unstable-time") { fc_allow_unstable_time = true; continue; }
        if (i + 1 >= total) throw std::runtime_error("选项缺少参数：" + key);
        const std::string value = argv[++i];
        if (key == "--preference") { fc_parse_preference(value); fc_preference_spec = value; fc_use_preference = true; }
        else if (key == "--candidate-sizes") {
            const auto groups = fc_split(value, ';');
            if (groups.size() > 16) throw std::runtime_error("最多16组候选尺寸");
            for (const auto& group : groups) fc_parse_sizes(group);
            fc_candidate_sizes = value;
        }
        else if (key == "--candidate-modes") {
            for (const auto& mode : fc_split(value, ','))
                if (mode != "sparse" && mode != "direct_rgb24" && mode != "direct_u8" && mode != "direct_u16")
                    throw std::runtime_error("候选模式应为sparse/direct_rgb24/direct_u8/direct_u16");
            fc_candidate_modes = value;
        }
        else if (key == "--max-mean-error") fc_max_mean_error = fc_nonnegative_number(value);
        else if (key == "--max-pixel-error") fc_max_pixel_error = fc_nonnegative_number(value);
        else if (key == "--max-ms-per-mp") fc_max_ms_per_mp = fc_nonnegative_number(value);
        else if (key == "--max-runtime-mib") fc_max_runtime_bytes = fc_mib_budget(value);
        else if (key == "--max-workspace-mib") fc_max_workspace_bytes = fc_mib_budget(value);
        else if (key == "--selection-report") {
            if (value.empty() || std::filesystem::exists(value)) throw std::runtime_error("选择报告路径必须尚不存在");
            fc_selection_report_path = value;
        }
        else if (key == "--calibration-reps") {
            if (value.empty() || value.find_first_not_of("0123456789") != std::string::npos)
                throw std::runtime_error("校准次数必须为3..31的奇数");
            const auto repetitions = std::stoul(value);
            if (repetitions < 3 || repetitions > 31 || repetitions % 2 == 0)
                throw std::runtime_error("校准次数必须为3..31的奇数");
            fc_calibration_reps = static_cast<unsigned>(repetitions);
        }
        else throw std::runtime_error("未知选项：" + key);
    }
    if (!seen.empty() && !fc_use_preference) throw std::runtime_error("偏好选项必须同时提供--preference");
    fc_options.threads = 1;
    fc_fit.prove_structure = true;
}

int main(int argc, char** argv) {
    try {
        fc_arguments(argc, argv);
        const auto weights = fc_use_preference ? fc_parse_preference(fc_preference_spec) : fc::Preference{};
        std::printf("{\"enabled\":%s,\"weights\":[%.17g,%.17g,%.17g],"
                    "\"runtime\":%zu,\"workspace\":%zu,\"mean\":%.17g,\"pixel\":%.17g,"
                    "\"time\":%.17g,\"reps\":%u,\"unstable\":%s,\"threads\":%u,"
                    "\"sizes\":[%u,%u,%u,%u]}\n",
                    fc_use_preference ? "true" : "false", weights.accuracy, weights.speed, weights.compactness,
                    fc_max_runtime_bytes, fc_max_workspace_bytes, fc_max_mean_error, fc_max_pixel_error,
                    fc_max_ms_per_mp, fc_calibration_reps, fc_allow_unstable_time ? "true" : "false",
                    fc_options.threads, fc_sizes[0], fc_sizes[1], fc_sizes[2], fc_sizes[3]);
        return 0;
    } catch (const std::exception& error) { std::fprintf(stderr, "%s\n", error.what()); return 2; }
}
