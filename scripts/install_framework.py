"""在用户框架内新增可独立编译的FlashChroma工程，保留原C/C++与计分代码。"""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def digest(path):
    with Path(path).open('rb') as stream:
        return hashlib.file_digest(stream, 'sha256').hexdigest()


def once(source, old, new):
    if source.count(old) != 1:
        raise ValueError('原框架结构发生变化，拒绝不明确的替换：' + old[:100])
    return source.replace(old, new, 1)


GLOBALS = r'''
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
'''


def generate_main(original):
    source = once(original, '#include <cstdio>', '''#define FLASH_CHROMA_IMPLEMENTATION
#define FLASH_CHROMA_ENABLE_OPENMP 0
#include "flash_chroma_framework.hpp"
#include <memory>
#include <filesystem>
#include <cstdio>''')
    source = once(source, '    int size = 0;                  // N',
                  '    std::shared_ptr<fc_framework::Stage> fc_stage; // 由LUT本身生成的稀疏模型/结构证明\n    int size = 0;                  // N')
    source = once(source, '// Read .3DL file:', GLOBALS + '\n// Read .3DL file:')
    source = once(source, '''    // add your code here
    return true;
}''', '''    try {
        auto stage = std::make_shared<fc_framework::Stage>(
            fc_framework::prepare_stage(lut256, static_cast<unsigned>(lut_size), fc_fit));
        out.size = static_cast<int>(stage->m);
        out.data.assign(stage->nodes_data(), stage->nodes_data() + stage->node_bytes());
        out.fc_stage = std::move(stage);
        return true;
    } catch (const std::exception& error) {
        std::fprintf(stderr, "稀疏预处理失败：%s\\n", error.what());
        return false;
    }
}''')
    source = once(source, '''    // add your code here
    out = img;

    return true;
}''', '''    if (!l1.fc_stage || !l2.fc_stage || !l3.fc_stage || !l4.fc_stage || img.C != 3 ||
        fc_prepared_stages != std::array<const fc_framework::Stage*, 4>{{
            l1.fc_stage.get(), l2.fc_stage.get(), l3.fc_stage.get(), l4.fc_stage.get()}})
        return false;
    // 输出申请/清零仍处于原框架apply计时内，不移到预处理阶段。
    out.H = img.H; out.W = img.W; out.C = img.C;
    out.data.resize(img.size());
    return fc_prepared.apply(img.ptr(), out.ptr(), static_cast<std::size_t>(img.H) * img.W)
        == fc::Status::Ok;
}''')
    # 严格输入解析只加速不计时的读取，不更改参考轴序、量化、色差和映射计时。
    start = source.index('bool lut_read_3dl(')
    end = source.index('// Port of sparse_lut().', start)
    source = source[:start] + '''bool lut_read_3dl(const std::string& path, std::vector<uint16_t>& out) {
    try { fc_framework_io::read_3dl(path, out); return true; }
    catch (const std::exception& error) {
        std::fprintf(stderr, "读取LUT失败：%s\\n", error.what()); return false;
    }
}

''' + source[end:]
    source = once(source, 'int main(int argc, char** argv) {', '''int main(int argc, char** argv) {
    if (argc >= 2 && std::string(argv[1]) == "--help") {
        std::puts("用法：main_flash_chroma.exe [data目录] [m或m1,m2,m3,m4] [auto|sparse|direct_u8|direct_u16|direct_rgb24] [auto|scalar|avx2] [uniform|framework] [图片数1..100] [sample|independent_ls|chain_ls]");
        std::puts("默认：../data 33 auto auto uniform 4；单线程，所有拟合/准备仅使用LUT。auto完整证明结构后才启用精确曲线，否则回退稀疏四面体。");
        std::puts("追加偏好选项：--preference A,B,C（各0..1且非全零） --candidate-sizes '17;25;33' --candidate-modes sparse,direct_rgb24");
        std::puts("预算：--max-mean-error 完整RGB域均值 --max-pixel-error 完整RGB域最大误差 --max-ms-per-mp 合成输入毫秒/百万像素 --max-runtime-mib 自有常驻容量 --max-workspace-mib 工作区");
        std::puts("其他：--selection-report 新JSON路径 --calibration-reps 3..31奇数 --allow-unstable-time（显式接受临时时间资格）。偏好选择在读图前，整批配置固定；位置参数中的m/mode由候选列表替代，grid/fit/backend仍生效。");
        return 0;
    }
    try { fc_arguments(argc, argv); }
    catch (const std::exception& error) { std::fprintf(stderr, "%s\\n", error.what()); return 2; }''')
    source = once(source, 'lut_sparse(luts_raw[i], 17,  lut17[i])',
                  'lut_sparse(luts_raw[i], static_cast<int>(fc_sizes[i]), lut17[i])')
    source = once(source, '    // free raw 16-bit LUTs', '''    // 赛方允许的LUT-only预处理：在读取任何图片前完成拟合与联合准备。
    std::unique_ptr<fc_framework::SelectionResult> fc_selection;
    try {
    if (fc_use_preference) {
        fc_framework::PreferenceOptions request;
        request.weights = fc_parse_preference(fc_preference_spec);
        request.sizes.clear();
        for (const auto& spec : fc_split(fc_candidate_sizes, ';')) request.sizes.push_back(fc_parse_sizes(spec));
        request.representations.clear();
        for (const auto& mode : fc_split(fc_candidate_modes, ',')) {
            if (mode == "sparse") request.representations.push_back(fc::Representation::Sparse);
            else if (mode == "direct_u8") request.representations.push_back(fc::Representation::DirectU8);
            else if (mode == "direct_u16") request.representations.push_back(fc::Representation::DirectU16);
            else request.representations.push_back(fc::Representation::DirectRGB24);
        }
        request.fit = fc_fit; request.fit_method = fc_fit_method; request.backend = fc_options.backend;
        request.max_runtime_bytes = fc_max_runtime_bytes; request.max_workspace_bytes = fc_max_workspace_bytes;
        if (fc_max_mean_error >= 0) request.max_domain_mean = fc_max_mean_error;
        if (fc_max_pixel_error >= 0) request.max_pixel_error = fc_max_pixel_error;
        if (fc_max_ms_per_mp >= 0) request.max_ms_per_megapixel = fc_max_ms_per_mp;
        request.allow_unstable = fc_allow_unstable_time; request.calibration_repetitions = fc_calibration_reps;
        fc_selection = std::make_unique<fc_framework::SelectionResult>(fc_framework::select_preferences(luts_raw, request));
        std::printf("PreferenceReport=%s\\n", fc_selection->report_json.c_str());
        std::fflush(stdout);
        if (!fc_selection_report_path.empty()) {
            if (std::filesystem::exists(fc_selection_report_path)) throw std::runtime_error("选择报告已存在，拒绝覆盖");
            std::ofstream report_file(fc_selection_report_path, std::ios::binary);
            report_file << fc_selection->report_json << '\\n';
            report_file.close();
            if (!report_file) throw std::runtime_error("无法完整写入选择报告");
        }
        if (!fc_selection->selected) {
            std::fprintf(stderr, "偏好选择失败：%s\\n", fc::selection_status_string(fc_selection->status)); return 2;
        }
        for (unsigned i = 0; i != 4; ++i) {
            *lut17[i].fc_stage = std::move(fc_selection->stages[i]);
            fc_sizes[i] = lut17[i].fc_stage->m;
        }
        fc_options = fc_selection->options;
    } else if (fc_fit_method == "independent_ls") {
        for (unsigned i = 0; i != 4; ++i) {
            fc_framework::FitReport report;
            *lut17[i].fc_stage = fc_framework::fit_full(luts_raw[i], *lut17[i].fc_stage, report);
            fc_print_fit(i + 1, report);
        }
    } else if (fc_fit_method == "chain_ls") {
        std::array<fc_framework::Stage, 4> sampled;
        for (unsigned i = 0; i != 4; ++i) sampled[i] = *lut17[i].fc_stage;
        fc_framework::FitReport report;
        *lut17[3].fc_stage = fc_framework::fit_chain_last(luts_raw, sampled, report);
        fc_print_fit(4, report);
    }
    for (auto& model : lut17) {
        const auto& stage = *model.fc_stage;
        model.size = static_cast<int>(stage.m);
        std::vector<std::uint8_t>(stage.nodes_data(), stage.nodes_data() + stage.node_bytes()).swap(model.data);
    }
    fc_prepared_stages = {{lut17[0].fc_stage.get(), lut17[1].fc_stage.get(), lut17[2].fc_stage.get(), lut17[3].fc_stage.get()}};
    const auto prep_status = fc_prepared.prepare(fc_prepared_stages, fc_options);
    if (prep_status != fc::Status::Ok) {
        std::fprintf(stderr, "链准备失败：%s\\n", fc::status_string(prep_status)); return 2;
    }
    const auto& info = fc_prepared.info();
    std::size_t wrapper_nodes = 0;
    for (const auto& model : lut17) wrapper_nodes += model.data.size();
    if (fc_selection) {
        const auto& expected = fc_selection->expected_info;
        const auto bytes = info.model_bytes + info.arena_bytes + info.object_bytes + wrapper_nodes +
            4 * (sizeof(std::shared_ptr<fc_framework::Stage>) + 2 * sizeof(void*));
        if (info.backend != expected.backend || info.representation != expected.representation ||
            info.structured != expected.structured || info.threads != 1 ||
            info.model_bytes != expected.model_bytes || info.arena_bytes != expected.arena_bytes ||
            info.object_bytes != expected.object_bytes || info.sidecar_bytes != expected.sidecar_bytes ||
            bytes != fc_selection->expected_runtime_bytes || bytes > fc_max_runtime_bytes ||
            info.arena_bytes > fc_max_workspace_bytes) {
            std::fprintf(stderr, "最终执行计划与选择回执或预算不符，拒绝读图运行\\n"); return 2;
        }
        fc_selection.reset();
    }
    std::printf("FlashChroma threads=1 m=%u,%u,%u,%u structured=%d backend=%u representation=%u model_bytes=%zu sidecar_bytes=%zu arena_bytes=%zu object_bytes=%zu wrapper_nodes_bytes=%zu\\n",
        fc_sizes[0],fc_sizes[1],fc_sizes[2],fc_sizes[3],int(info.structured),unsigned(info.backend),unsigned(info.representation),
        info.model_bytes,info.sidecar_bytes,info.arena_bytes,info.object_bytes,wrapper_nodes);
    } catch (const std::exception& error) {
        std::fprintf(stderr, "预处理/选择失败：%s\\n", error.what()); return 2;
    }
    // free raw 16-bit LUTs''')
    source = once(source, '    for (int i = 1; i <= 4; i++) {',
                  '    for (int i = 1; i <= fc_image_count; i++) {')
    # 输入失败的原模板最终仍可能退出0；提前验证完整请求批次，不靠打印哨兵认成功。
    source = once(source, '    print_time_now("SpareLut Time");', '''    // 选型和准备已完成；此后才打开图片，即使长度检查也不向选型提供信息。
    for (int i = 1; i <= fc_image_count; ++i) {
        const auto path = join("image/" + std::to_string(i) + ".bin");
        std::ifstream probe(path, std::ios::binary | std::ios::ate);
        if (!probe || probe.tellg() != std::streamoff(IMG_H) * IMG_W * IMG_C) {
            std::fprintf(stderr, "图片缺失或长度不符：%s\\n", path.c_str()); return 2;
        }
    }
    print_time_now("SpareLut Time");''')
    source = once(source, '    std::vector<double> deltas, perfs;',
                  '    int fc_success_count = 0;\n    std::vector<double> deltas, perfs;')
    source = once(source, '        deltas.push_back(delta2);',
                  '        ++fc_success_count;\n        deltas.push_back(delta2);')
    source = once(source, '    print_time_now("End Time");', '''    print_time_now("End Time");
    if (fc_success_count != fc_image_count) {
        std::fprintf(stderr, "批次处理不完整：%d/%d\\n", fc_success_count, fc_image_count); return 2;
    }''')
    return source


def amalgamate():
    """原核心与框架接入完整内嵌，部署只需一个hpp和框架main.cpp。"""
    names = ('include/flash_chroma.hpp', 'framework/flash_chroma_adapter.hpp', 'framework/framework_io.hpp',
             'framework/fit_experiment.hpp', 'framework/fit_chain_experiment.hpp', 'framework/preference_selection.hpp')
    parts = ['// 由scripts/install_framework.py生成；源文件SHA见source-manifest.json。\n']
    for name in names:
        code = (ROOT / name).read_text(encoding='utf-8-sig')
        if name.endswith('flash_chroma_adapter.hpp'):
            code = once(code, '#include "flash_chroma.hpp"', '// 运行库已完整内嵌于上文。')
        if name.endswith('fit_experiment.hpp'):
            code = once(code, '#include "flash_chroma_adapter.hpp"', '// 框架接入已内嵌于上文。')
        if name.endswith('fit_chain_experiment.hpp'):
            code = once(code, '#include "fit_experiment.hpp"', '// 完整域求解器已内嵌于上文。')
        if name.endswith('preference_selection.hpp'):
            code = once(code, '#include "fit_chain_experiment.hpp"', '// 链求解器已内嵌于上文。')
        parts.extend(['\n// ---- ' + name + ' ----\n', code, '\n'])
    return ''.join(parts), {name: digest(ROOT / name) for name in names}


def install(framework, output, compiler):
    framework = Path(framework).resolve()
    source_path = framework / 'C++/main.cpp'
    original = source_path.read_text(encoding='utf-8-sig')
    generated = generate_main(original)
    output = Path(output).resolve() if output else framework / 'FlashChroma'
    if output.exists():
        raise FileExistsError('交付目录已存在，拒绝覆盖；请指定新的--output')
    for name in ('include/flash_chroma.hpp', 'framework/flash_chroma_adapter.hpp', 'framework/framework_io.hpp'):
        if not (ROOT / name).is_file():
            raise FileNotFoundError(name)
    output.mkdir(parents=True)
    (output / 'main.cpp').write_text(generated, encoding='utf-8', newline='\n')
    header, component_hashes = amalgamate()
    (output / 'flash_chroma_framework.hpp').write_text(header, encoding='utf-8', newline='\n')
    config = {'compiler': str(Path(compiler).resolve()) if compiler else '',
              'framework': str(framework), 'original_main_sha256': digest(source_path), 'components': component_hashes,
              'scope': '新增独立工程，不改原C/C++模板；参考与计时函数保留，LUT-only联合准备明确位于图像读取前。'}
    (output / 'build-config.json').write_text(json.dumps(config, ensure_ascii=False, indent=2)+'\n', encoding='utf-8')
    launcher = r'''param(
    [switch]$BuildOnly,
    [string]$Data = '', [string]$GridSizes = '33',
    [ValidateSet('auto','sparse','direct_u8','direct_u16','direct_rgb24')][string]$Mode = 'auto',
    [ValidateSet('auto','scalar','avx2')][string]$Backend = 'auto',
    [ValidateSet('uniform','framework')][string]$Grid = 'uniform',
    [ValidateRange(1,100)][int]$Count = 4,
    [ValidateSet('sample','independent_ls','chain_ls')][string]$Fit = 'sample',
    [string]$Preference = '',
    [string]$CandidateSizes = '17;25;33',
    [string]$CandidateModes = 'sparse,direct_rgb24',
    [Nullable[double]]$MaxMeanError = $null,
    [Nullable[double]]$MaxPixelError = $null,
    [Nullable[double]]$MaxMsPerMP = $null,
    [Nullable[double]]$MaxRuntimeMiB = $null,
    [Nullable[double]]$MaxWorkspaceMiB = $null,
    [ValidateRange(3,31)][int]$CalibrationReps = 5,
    [switch]$AllowUnstableTime,
    [string]$SelectionReport = ''
)
$ErrorActionPreference = 'Stop'
$config = Get-Content -LiteralPath (Join-Path $PSScriptRoot 'build-config.json') -Raw | ConvertFrom-Json
if (-not $Data) { $Data = Join-Path $config.framework 'data' }
$compiler = $env:FLASH_CHROMA_CXX
if (-not $compiler -and $config.compiler -and (Test-Path -LiteralPath $config.compiler -PathType Leaf)) { $compiler = $config.compiler }
if (-not $compiler) { $compiler = (Get-Command g++ -ErrorAction Stop).Source }
$oldPath = $env:PATH
Push-Location -LiteralPath $PSScriptRoot
try {
    $env:PATH = (Split-Path -Parent $compiler) + ';' + $env:PATH
    & $compiler --version | Select-Object -First 1
    & $compiler '-O3' '-DNDEBUG' '-std=c++17' '-Wall' '-Wextra' '-static' '-DFLASH_CHROMA_ENABLE_OPENMP=0' 'main.cpp' '-o' 'main_flash_chroma.exe'
    if ($LASTEXITCODE -ne 0) { throw '编译失败，未运行旧程序。' }
    if (-not $BuildOnly) {
        $relativeData = Resolve-Path -LiteralPath $Data -Relative
        $runArguments = @($relativeData, $GridSizes, $Mode, $Backend, $Grid, [string]$Count, $Fit)
        $preferenceKeys = @('CandidateSizes','CandidateModes','MaxMeanError','MaxPixelError','MaxMsPerMP','MaxRuntimeMiB','MaxWorkspaceMiB','CalibrationReps','AllowUnstableTime','SelectionReport')
        if (-not $Preference) {
            foreach ($key in $preferenceKeys) {
                if ($PSBoundParameters.ContainsKey($key)) { throw "-$key 须与-Preference同时使用" }
            }
        } else {
            $runArguments += @('--preference', $Preference, '--candidate-sizes', $CandidateSizes, '--candidate-modes', $CandidateModes, '--calibration-reps', [string]$CalibrationReps)
            $budgets = @{'--max-mean-error'=$MaxMeanError; '--max-pixel-error'=$MaxPixelError; '--max-ms-per-mp'=$MaxMsPerMP; '--max-runtime-mib'=$MaxRuntimeMiB; '--max-workspace-mib'=$MaxWorkspaceMiB}
            foreach ($key in $budgets.Keys) {
                if ($null -ne $budgets[$key]) { $runArguments += @($key, ([double]$budgets[$key]).ToString('R', [System.Globalization.CultureInfo]::InvariantCulture)) }
            }
            if ($AllowUnstableTime) { $runArguments += '--allow-unstable-time' }
            if ($SelectionReport) { $runArguments += @('--selection-report', $SelectionReport) }
        }
        & '.\main_flash_chroma.exe' @runArguments
        if ($LASTEXITCODE -ne 0) { throw "框架执行失败：$LASTEXITCODE" }
    }
} finally { $env:PATH = $oldPath; Pop-Location }
'''
    (output / 'run.ps1').write_text(launcher, encoding='utf-8-sig', newline='\r\n')
    readme = '''# Flash Chroma 框架适配

在此目录执行 `.\\run.ps1`，编译后直接运行原框架的四张样图；无需Python或OpenMP运行时。完整接入只需一个 `flash_chroma_framework.hpp` 和 `main.cpp`。指定编译器可设置 `FLASH_CHROMA_CXX`。构建使用同一单线程O3，静态链接GCC运行库，不用GPU/NPU。原C、C++模板和数据未修改。当前实测GCC15.2；题面指定的13.2尚未执行，不能混称。

```powershell
.\\run.ps1 -GridSizes 17 -Mode auto
.\\run.ps1 -GridSizes 33 -Mode sparse -Backend avx2
.\\run.ps1 -GridSizes '17,25,33,33' -Mode sparse
.\\run.ps1 -GridSizes 33 -Mode direct_rgb24 -Backend auto
.\\run.ps1 -GridSizes 33 -Mode direct_rgb24 -Grid framework -Fit chain_ls
.\\run.ps1 -Preference '0.6,0.3,0.1' -Grid framework -Fit chain_ls -SelectionReport 'selection.json'
.\\run.ps1 -Preference '0.2,0,0.8' -Grid framework -Fit chain_ls -MaxRuntimeMiB 2 -SelectionReport 'compact.json'
```

auto只有在遍历原LUT全部256³节点、证明每个通道独立时，才采用每级768B精确曲线sidecar并组成查表；否则使用真实m³稀疏四面体。结构证明和拟合不读取图片。sparse显式关闭该结构分支，适合比较仅稀疏节点的方案；direct是额外内存较大的实验表示，不能把其磁盘或稀疏节点大小当作全部RAM。

`-Preference 'A,B,C'` 为连续精度/速度/紧凑偏好，各权重在0..1且不能全零，不要求和为1。它启用独立自动选型路径：在首次打开图片之前，为当前四表生成候选，以完整256³ RGB域核对原表误差、实际后端与Scalar输出，再用固定合成输入校准速度，调用hpp中的fc::select。候选默认m17/25/33各配Sparse/RGB24，`-CandidateSizes '17;25;33;17,25,33,33'`与`-CandidateModes 'sparse,direct_rgb24'`可收窄或扩展。Grid/Fit/Backend仍生效，GridSizes/Mode由候选列表替代；不传Preference时完全沿用手动模式。未知表首次准备和全域校验可能耗时，整批图片映射期间不重新选型。

预算含义须按实际范围使用：MaxMeanError是均匀完整RGB域mean，MaxPixelError是完整域max；前者不保证正式每张图mean达标，后者提供任意图片mean的保守上界。MaxMsPerMP是固定合成输入fresh输出分配+apply的毫秒/百万像素，不是正式照片TimeCost。MaxRuntimeMiB是所选计划的自有容量记账（含模型/arena/对象/包装副本及shared管理估算），不是RSS、分配器精确开销或准备峰值；MaxWorkspaceMiB限制所选运行工作区，原四张uint16源表和候选/校准暂态另计。速度权重为0且无时间预算时跳过计时；需要速度时每个候选独立检查前后A/A，失败默认剔除。AllowUnstableTime必须显式给出，结果标为provisional，不能据此宣称稳定性能。

SelectionReport必须为新路径，成功或无可行候选均保存选择JSON；没有合格候选时非零退出，不悄悄放松预算。报告绑定本次源表、模型、实际后端、全部候选拒绝原因、完整域误差和合成计时原样本；不读旧Cinema目录、不读测试照片训练或选择。最终重新准备后再次核对所选执行计划和资源，随后固定用于整批图片。直接运行EXE也支持同样的追加长选项，无需改代码或重编译，例如：

```powershell
.\\main_flash_chroma.exe '..\\data' 33 auto auto framework 4 chain_ls --preference '0.6,0.3,0.1' --candidate-sizes '17;33' --selection-report 'selection-exe.json'
```

RGB24的AVX2执行核已补齐八路独立查表和64像素成块普通写出，保持同一LUT表、精度与内存需求。高级编译选项 `FLASH_CHROMA_RGB24_STREAMING=1` 可切流式写，`FLASH_CHROMA_RGB24_LEGACY=1` 用于旧gather回归；默认脚本使用普通写新核，不在图片之间重新测速选核。

默认sample采样；independent_ls用全色域分别拟合各级，chain_ls固定前三层并针对原四级完整输出拟合末层。固定参数：正则1e-5、CG最多160轮/相对残差1e-8、整数精化最多8轮。实际全色域整数mean及SSE双门控失败会保留原模型，不读取测试图片挑选节点。完整域改善不保证每张照片改善；未知阈值时保持三档显式选择。DirectRGB24与相同拟合的Sparse逐字节等价，约多用48MiB缓存；U8/U16容量不足会非零退出。

输出分配仍在原apply计时区内，四LUT联合准备显式位于允许的不计时预处理区。参考查表、量化和平均RGB欧氏差公式保留。默认处理4张，`-Count 100`要求对应data/image/1.bin..100.bin完整存在；图片必须是1024×768连续RGB8，不能把PNG改名传入。

样例Test2/3/4相同，Test1是正式验收不会使用的线性表。样例最优不等于任意未知LUT最优；实际阈值与换分公式未提供，不宣称官方满分。资源行包含模型、sidecar、arena、对象和框架节点副本；sidecar是对象内子集，勿重复累加。
'''
    (output / 'README.md').write_text(readme, encoding='utf-8', newline='\n')
    manifest = dict(config, files={p.name: {'sha256': digest(p), 'bytes': p.stat().st_size}
                                 for p in output.iterdir() if p.is_file()})
    (output / 'source-manifest.json').write_text(json.dumps(manifest, ensure_ascii=False, indent=2)+'\n', encoding='utf-8')
    return {'directory': str(output), 'original_unchanged': digest(source_path) == config['original_main_sha256'],
            'files': len(manifest['files'])}


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--framework', type=Path, required=True)
    parser.add_argument('--output', type=Path)
    parser.add_argument('--compiler', type=Path)
    args = parser.parse_args()
    print(json.dumps(install(args.framework, args.output, args.compiler), ensure_ascii=False, indent=2))
