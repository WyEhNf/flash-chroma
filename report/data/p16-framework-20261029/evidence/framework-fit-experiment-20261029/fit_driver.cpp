// 独立拟合实验：所有LUT模型完成并保存以后，才读取图像计算误差。
#define FLASH_CHROMA_IMPLEMENTATION
#define FLASH_CHROMA_ENABLE_OPENMP 0
#include "fit_chain_experiment.hpp"
#include "framework_io.hpp"
#include <filesystem>
#include <iomanip>
#include <iostream>
#include <sstream>

namespace fs = std::filesystem;
using namespace fc_framework;

void save(const fs::path& path, const std::string& data) {
    fc_framework_io::write_rgb_file_new(path.string(), {data.begin(), data.end()});
}
void error_json(std::ostream& out, const FitError& e) {
    out << "{\"sse\":" << e.sse << ",\"mean\":" << e.mean
        << ",\"rms\":" << std::sqrt(double(e.sse) / dense_nodes)
        << ",\"max\":" << std::sqrt(double(e.max_squared)) << ",\"linear_sse\":" << e.linear_sse << '}';
}
void fit_json(std::ostream& out, const FitReport& r, int reused) {
    out << "{\"reused_from\":" << reused << ",\"m\":" << r.m << ",\"samples\":" << r.samples
        << ",\"source_separable_skipped\":" << r.source_separable_skipped
        << ",\"candidate_used\":" << r.candidate_used << ",\"changed_nodes\":" << r.changed_nodes
        << ",\"integer_sweeps\":" << r.integer_sweeps << ",\"matrix_bytes\":" << r.matrix_bytes
        << ",\"temporary_payload_estimate_bytes\":" << r.temporary_bytes
        << ",\"assembly_seconds\":" << r.assembly_seconds << ",\"solve_seconds\":" << r.solve_seconds
        << ",\"evaluation_seconds\":" << r.evaluation_seconds << ",\"linear_sse_before\":" << r.linear_sse_before
        << ",\"linear_sse_after\":" << r.linear_sse_after << ",\"baseline\":";
    error_json(out, r.baseline); out << ",\"candidate\":"; error_json(out, r.candidate);
    out << ",\"channels\":[";
    for (unsigned c = 0; c != 3; ++c) {
        if (c) out << ',';
        out << "{\"iterations\":" << r.channels[c].iterations << ",\"relative_residual\":" << r.channels[c].relative_residual
            << ",\"converged\":" << r.channels[c].converged << '}';
    }
    out << "]}";
}
std::vector<std::uint8_t> reference(const std::array<std::vector<std::uint16_t>, 4>& raw,
                                    std::vector<std::uint8_t> image) {
    for (const auto& table : raw) for (std::size_t i = 0; i < image.size(); i += 3) {
        const std::size_t at = ((std::size_t(image[i + 2]) * 256 + image[i + 1]) * 256 + image[i]) * 3;
        const auto r = static_cast<std::uint8_t>(table[at + 2] / 16);
        const auto g = static_cast<std::uint8_t>(table[at + 1] / 16);
        const auto b = static_cast<std::uint8_t>(table[at] / 16);
        image[i] = r; image[i + 1] = g; image[i + 2] = b;
    }
    return image;
}
void metric(std::ostream& out, const std::vector<std::uint8_t>& actual, const std::vector<std::uint8_t>& expected) {
    std::uint64_t sse = 0; unsigned max_squared = 0; double mean = 0;
    for (std::size_t i = 0; i < actual.size(); i += 3) {
        unsigned sq = 0;
        for (unsigned c = 0; c != 3; ++c) { const int d = int(actual[i + c]) - int(expected[i + c]); sq += unsigned(d * d); }
        sse += sq; mean += std::sqrt(double(sq)); max_squared = (std::max)(max_squared, sq);
    }
    const auto pixels = actual.size() / 3;
    out << "{\"sse\":" << sse << ",\"mean\":" << mean / pixels << ",\"rms\":" << std::sqrt(double(sse) / pixels)
        << ",\"max\":" << std::sqrt(double(max_squared)) << '}';
}
void check(fc::Status status) {
    if (status != fc::Status::Ok) throw std::runtime_error("模型执行失败，状态" + std::to_string(unsigned(status)));
}
int main(int argc, char** argv) {
    try {
        const bool chain_mode = argc == 9 && std::string(argv[8]) == "--chain-last";
        if (argc != 8 && !chain_mode) throw std::runtime_error("参数：四个u16le缓存、输入图片目录、新输出目录、m，可选--chain-last");
        const unsigned m = static_cast<unsigned>(std::stoul(argv[7]));
        const fs::path output(argv[6]), images(argv[5]);
        if (fs::exists(output)) throw std::runtime_error("实验输出目录已存在");
        fs::create_directories(output / "models"); fs::create_directory(output / "sample"); fs::create_directory(output / "fitted");
        std::array<std::vector<std::uint16_t>, 4> raw;
        std::array<Stage, 4> sampled, fitted;
        std::array<FitReport, 4> reports;
        std::array<int, 4> reused = {-1, -1, -1, -1};
        const auto start = fit_detail::seconds();
        for (unsigned i = 0; i != 4; ++i) {
            fc_framework_io::read_u16_cache(argv[i + 1], raw[i]);
            sampled[i] = prepare_stage(raw[i], m);
        }
        for (unsigned i = 0; i != 4; ++i) {
            if (chain_mode) {
                reports[i].m = m;
                fitted[i] = i == 3 ? fit_chain_last(raw, sampled, reports[i]) : sampled[i];
            } else {
                for (unsigned j = 0; j < i; ++j) if (raw[i] == raw[j] && sampled[i].blob == sampled[j].blob) { reused[i] = int(j); break; }
                if (reused[i] >= 0) { fitted[i] = fitted[reused[i]]; reports[i] = reports[reused[i]]; }
                else fitted[i] = fit_full(raw[i], sampled[i], reports[i]);
            }
            fc_framework_io::write_rgb_file_new((output / "models" / ("sample-" + std::to_string(i + 1) + ".slut")).string(), sampled[i].blob);
            fc_framework_io::write_rgb_file_new((output / "models" / ("fitted-" + std::to_string(i + 1) + ".slut")).string(), fitted[i].blob);
            std::cout << "第" << i + 1 << "级完成，复用来源=" << reused[i] << "，采用候选=" << reports[i].candidate_used << std::endl;
        }
        const double preparation_seconds = fit_detail::seconds() - start;
        std::ostringstream report; report << std::setprecision(17) << std::boolalpha;
        report << "{\"schema\":\"framework_fit_experiment_v1\",\"cpu_threads\":1,\"fit_uses_images\":false,\"performance_test\":false,"
               << "\"chain_last_only\":" << chain_mode << ",\"m\":" << m << ",\"preparation_seconds\":" << preparation_seconds
               << ",\"fixed_parameters\":{\"cg_max_iterations\":160,\"relative_tolerance\":1e-8,\"regularization\":1e-5,\"integer_sweeps\":8,\"guard_full_domain\":true},\"stages\":[";
        for (unsigned i = 0; i != 4; ++i) { if (i) report << ','; fit_json(report, reports[i], reused[i]); }
        report << ']';
        save(output / "fit-before-images.json", report.str() + '}');
        std::array<const Stage*, 4> sp{}, fp{};
        for (unsigned i = 0; i != 4; ++i) { sp[i] = &sampled[i]; fp[i] = &fitted[i]; }
        Chain sample_chain, fitted_chain, avx_chain; Options options;
        options.structure = false; options.backend = fc::Backend::Scalar;
        check(sample_chain.prepare(sp, options)); check(fitted_chain.prepare(fp, options));
        options.backend = fc::Backend::Avx2;
        const auto avx_status = avx_chain.prepare(fp, options);
        report << ",\"avx2_available\":" << (avx_status == fc::Status::Ok) << ",\"images\":[";
        // 这是本进程第一次打开图像；拟合参数及所有模型在此之前已固定并落盘。
        for (unsigned i = 1; i <= 4; ++i) {
            auto input = fc_framework_io::read_rgb_file((images / ("image-" + std::to_string(i) + ".bin")).string(), 1024 * 768 * 3);
            const auto expected = reference(raw, input);
            std::vector<std::uint8_t> sample(input.size()), result(input.size()), avx(input.size());
            check(sample_chain.apply(input.data(), sample.data(), input.size() / 3));
            check(fitted_chain.apply(input.data(), result.data(), input.size() / 3));
            if (avx_status == fc::Status::Ok) {
                check(avx_chain.apply(input.data(), avx.data(), input.size() / 3));
                if (avx != result) throw std::runtime_error("拟合模型Scalar与AVX2输出不同");
            }
            fc_framework_io::write_rgb_file_new((output / "sample" / ("image-" + std::to_string(i) + ".bin")).string(), sample);
            fc_framework_io::write_rgb_file_new((output / "fitted" / ("image-" + std::to_string(i) + ".bin")).string(), result);
            if (i > 1) report << ',';
            report << "{\"id\":" << i << ",\"sample\":"; metric(report, sample, expected);
            report << ",\"fitted\":"; metric(report, result, expected); report << '}';
        }
        report << "]}";
        save(output / "report.json", report.str());
        std::cout << "拟合及四张图片误差验证完成；未测性能。" << std::endl;
        return 0;
    } catch (const std::exception& e) { std::cerr << "实验失败：" << e.what() << '\n'; return 1; }
}
