// main.cpp -- 3D LUT color correction pipeline (port of Python/main.py)
//
// Algorithm-equivalent port:
//   - apply_lut_linear : 8-vertex trilinear interpolation
//   - apply_lut_nearest: nearest-neighbor LUT lookup
//   - apply_3d_lut     : chain 4 LUTs sequentially
//   - sparse_lut       : sample 256^3 full LUT into size^3 sparse LUT (/16 quant)
//   - color_dalta_calc : average euclidean deltaE (matches Python logic)
//
// Image input: raw RGB .bin files (768*1024*3 bytes, no header),
//             matching Python's np.fromfile(...).reshape(768,1024,3).
//
// Build:
//   g++ -O2 -std=c++17 -o lut3d main.cpp
//
// Usage:
//   ./lut3d <data_dir>
//     data_dir contains: image/1.bin ... image/100.bin, LUT/Test1.3DL

#define FLASH_CHROMA_IMPLEMENTATION
#define FLASH_CHROMA_ENABLE_OPENMP 0
#include "flash_chroma_framework.hpp"
#include <memory>
#include <filesystem>
#include <cstdio>
#include <cstdlib>
#include <cstdint>
#include <cstring>
#include <cmath>
#include <string>
#include <vector>
#include <array>
#include <fstream>
#include <chrono>
#include <ctime>
#include <sys/stat.h>

namespace {

constexpr int IMG_H = 768;
constexpr int IMG_W = 1024;
constexpr int IMG_C = 3;
constexpr int MAX_IMAGES = 100;

// ------------------------------------------------------------------
// Image
// ------------------------------------------------------------------

struct Image {
    int H = 0, W = 0, C = 0;
    std::vector<uint8_t> data;

    uint8_t* ptr() { return data.data(); }
    const uint8_t* ptr() const { return data.data(); }
    size_t size() const { return (size_t)H * W * C; }
};

int clamp_i(int v, int lo, int hi) {
    return v < lo ? lo : (v > hi ? hi : v);
}

double now_sec() {
    using namespace std::chrono;
    return duration<double>(steady_clock::now().time_since_epoch()).count();
}

// Load raw RGB .bin file: exactly H*W*C bytes, no header.
// Mirrors Python: np.fromfile(file, dtype=np.uint8).reshape(768,1024,3)
bool image_load_bin(const std::string& path, Image& out) {
    std::ifstream f(path, std::ios::binary | std::ios::ate);
    if (!f) { std::fprintf(stderr, "cannot open %s\n", path.c_str()); return false; }
    std::streamsize sz = f.tellg();
    f.seekg(0, std::ios::beg);
    size_t n = (size_t)IMG_H * IMG_W * IMG_C;
    if ((size_t)sz != n) {
        std::fprintf(stderr, "%s: size %zd != %zu\n", path.c_str(), (ssize_t)sz, n);
        return false;
    }
    out.H = IMG_H; out.W = IMG_W; out.C = IMG_C;
    out.data.resize(n);
    if (!f.read(reinterpret_cast<char*>(out.data.data()), (std::streamsize)n)) {
        std::fprintf(stderr, "%s: read failed\n", path.c_str());
        return false;
    }
    return true;
}

// ------------------------------------------------------------------
// LUT
// ------------------------------------------------------------------

struct Lut3D {
    std::shared_ptr<fc_framework::Stage> fc_stage; // 由LUT本身生成的稀疏模型/结构证明
    int size = 0;                  // N
    std::vector<uint8_t> data;     // size^3 * 3, indexed [r][g][b]
    const uint8_t* at(int r, int g, int b) const {
        return &data[(((size_t)r * size + g) * size + b) * 3];
    }
};


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

// Read .3DL file: 256^3 lines, each "R G B". Values are 0..4080 (16x scale);
// store raw 16-bit values so sparse_lut can do /16 like Python.
bool lut_read_3dl(const std::string& path, std::vector<uint16_t>& out) {
    try { fc_framework_io::read_3dl(path, out); return true; }
    catch (const std::exception& error) {
        std::fprintf(stderr, "读取LUT失败：%s\n", error.what()); return false;
    }
}

// Port of sparse_lut().
bool lut_sparse(const std::vector<uint16_t>& lut256, int lut_size, Lut3D& out) {
    try {
        auto stage = std::make_shared<fc_framework::Stage>(
            fc_framework::prepare_stage(lut256, static_cast<unsigned>(lut_size), fc_fit));
        out.size = static_cast<int>(stage->m);
        out.data.assign(stage->nodes_data(), stage->nodes_data() + stage->node_bytes());
        out.fc_stage = std::move(stage);
        return true;
    } catch (const std::exception& error) {
        std::fprintf(stderr, "稀疏预处理失败：%s\n", error.what());
        return false;
    }
}

bool lut_sparse_ref(const std::vector<uint16_t>& lut256, int lut_size, Lut3D& out) {
    std::vector<int> sample_step(lut_size);
    int step = 256 / (lut_size - 1);
    for (int i = 0; i < lut_size; i++) sample_step[i] = i * step;
    sample_step[lut_size - 1] = 255;

    size_t total = (size_t)lut_size * lut_size * lut_size * 3;
    out.size = lut_size;
    out.data.resize(total);

    for (int b = 0; b < lut_size; b++) {
        for (int g = 0; g < lut_size; g++) {
            for (int r = 0; r < lut_size; r++) {
                size_t idx = ((size_t)sample_step[b] * 256 * 256
                            + (size_t)sample_step[g] * 256
                            + (size_t)sample_step[r]) * 3;
                size_t oidx = (((size_t)r * lut_size + g) * lut_size + b) * 3;
                out.data[oidx + 0] = (uint8_t)(lut256[idx + 2] / 16);
                out.data[oidx + 1] = (uint8_t)(lut256[idx + 1] / 16);
                out.data[oidx + 2] = (uint8_t)(lut256[idx + 0] / 16);
            }
        }
    }
    return true;
}

// apply_lut_256
bool apply_lut256(const Image& img, const Lut3D& lut, Image& out) {
    int N = lut.size;
    int H = img.H, W = img.W;
    out.H = H; out.W = W; out.C = 3;
    out.data.resize((size_t)H * W * 3);

    for (int y = 0; y < H; y++) {
        for (int x = 0; x < W; x++) {
            const uint8_t* pin = &img.ptr()[((size_t)y * W + x) * 3];
            int ir = (uint8_t)clamp_i(pin[0], 0, 255);
            int ig = (uint8_t)clamp_i(pin[1], 0, 255);
            int ib = (uint8_t)clamp_i(pin[2], 0, 255);
            const uint8_t* src = lut.at(ir, ig, ib);
            uint8_t* o = &out.ptr()[((size_t)y * W + x) * 3];
            o[0] = (uint8_t)clamp_i(src[0], 0, 255);
            o[1] = (uint8_t)clamp_i(src[1], 0, 255);
            o[2] = (uint8_t)clamp_i(src[2], 0, 255);
        }
    }
    return true;
}

// Apply 4 LUTs sequentially.
bool apply_3d_lut(const Image& img,
                  const Lut3D& l1, const Lut3D& l2,
                  const Lut3D& l3, const Lut3D& l4,
                  Image& out) {
    if (!l1.fc_stage || !l2.fc_stage || !l3.fc_stage || !l4.fc_stage || img.C != 3 ||
        fc_prepared_stages != std::array<const fc_framework::Stage*, 4>{{
            l1.fc_stage.get(), l2.fc_stage.get(), l3.fc_stage.get(), l4.fc_stage.get()}})
        return false;
    // 输出申请/清零仍处于原框架apply计时内，不移到预处理阶段。
    out.H = img.H; out.W = img.W; out.C = img.C;
    out.data.resize(img.size());
    return fc_prepared.apply(img.ptr(), out.ptr(), static_cast<std::size_t>(img.H) * img.W)
        == fc::Status::Ok;
}

bool apply_3d_lut_ref(const Image& img,
                  const Lut3D& l1, const Lut3D& l2,
                  const Lut3D& l3, const Lut3D& l4,
                  Image& out) {
    Image tmp0, tmp1;
    const Image* cur = &img;
    Image* nxt = &tmp0;
    if (!apply_lut256(*cur, l1, *nxt)) return false;
    cur = nxt; nxt = &tmp1;
    if (!apply_lut256(*cur, l2, *nxt)) return false;
    cur = nxt; nxt = &tmp0;
    if (!apply_lut256(*cur, l3, *nxt)) return false;
    cur = nxt; nxt = &tmp1;
    if (!apply_lut256(*cur, l4, *nxt)) return false;
    out = std::move(tmp1);
    return true;
}

// ------------------------------------------------------------------
// color_dalta_calc -- average euclidean deltaE (matches Python)
// ------------------------------------------------------------------

double color_dalta_calc(const Image& a, const Image& b) {
    if (a.H != b.H || a.W != b.W || a.C != b.C) {
        std::fprintf(stderr, "image size mismatch\n");
        return -1.0;
    }
    const uint8_t* pa = a.ptr();
    const uint8_t* pb = b.ptr();
    double sum = 0.0;
    size_t n = (size_t)a.H * a.W;
    for (size_t i = 0; i < n; i++) {
        int r  = pa[i * 3 + 0] - pb[i * 3 + 0];
        int g  = pa[i * 3 + 1] - pb[i * 3 + 1];
        int bb = pa[i * 3 + 2] - pb[i * 3 + 2];
        sum += std::sqrt((double)r * r + (double)g * g + (double)bb * bb);
    }
    return sum / ((double)a.H * a.W);
}

// ------------------------------------------------------------------
// helpers
// ------------------------------------------------------------------

bool file_exists(const std::string& p) {
    struct stat st;
    return stat(p.c_str(), &st) == 0;
}

void print_time_now(const char* tag) {
    std::time_t t = std::time(nullptr);
    char buf[64];
    std::strftime(buf, sizeof(buf), "%Y-%m-%d %H:%M:%S", std::localtime(&t));
    std::printf("%s: %s\n", tag, buf);
}

} // namespace

int main(int argc, char** argv) {
    if (argc >= 2 && std::string(argv[1]) == "--help") {
        std::puts("用法：main_flash_chroma.exe [data目录] [m或m1,m2,m3,m4] [auto|sparse|direct_u8|direct_u16|direct_rgb24] [auto|scalar|avx2] [uniform|framework] [图片数1..100] [sample|independent_ls|chain_ls]");
        std::puts("默认：../data 33 auto auto uniform 4；单线程，所有拟合/准备仅使用LUT。auto完整证明结构后才启用精确曲线，否则回退稀疏四面体。");
        std::puts("追加偏好选项：--preference A,B,C（各0..1且非全零） --candidate-sizes '17;25;33' --candidate-modes sparse,direct_rgb24");
        std::puts("预算：--max-mean-error 完整RGB域均值 --max-pixel-error 完整RGB域最大误差 --max-ms-per-mp 合成输入毫秒/百万像素 --max-runtime-mib 自有常驻容量 --max-workspace-mib 工作区");
        std::puts("其他：--selection-report 新JSON路径 --calibration-reps 3..31奇数 --allow-unstable-time（显式接受临时时间资格）。偏好选择在读图前，整批配置固定；位置参数中的m/mode由候选列表替代，grid/fit/backend仍生效。");
        return 0;
    }
    try { fc_arguments(argc, argv); }
    catch (const std::exception& error) { std::fprintf(stderr, "%s\n", error.what()); return 2; }
    std::string data_dir = "../data";
    if (argc >= 2) data_dir = argv[1];

    auto join = [&](const std::string& sub) {
        return data_dir + "/" + sub;
    };

    for (int i = 1; i <= fc_image_count; ++i) {
        const auto path = join("image/" + std::to_string(i) + ".bin");
        std::ifstream probe(path, std::ios::binary | std::ios::ate);
        if (!probe || probe.tellg() != std::streamoff(IMG_H) * IMG_W * IMG_C) {
            std::fprintf(stderr, "图片缺失或长度不符：%s\n", path.c_str()); return 2;
        }
    }
    print_time_now("Start Time");

    // Read LUTs (Python main.py uses Test1.3DL for all 4)
    std::vector<std::string> lut_paths = {
        join("LUT/Test1.3DL"),
        join("LUT/Test2.3DL"),
        join("LUT/Test3.3DL"),
        join("LUT/Test4.3DL"),
    };
    std::array<std::vector<uint16_t>, 4> luts_raw;
    for (int i = 0; i < 4; i++) {
        if (!lut_read_3dl(lut_paths[i], luts_raw[i])) return 1;
    }

    print_time_now("getLut Time");

    std::array<Lut3D, 4> lut256, lut17;
    for (int i = 0; i < 4; i++) {
        if (!lut_sparse_ref(luts_raw[i], 256, lut256[i])) return 1;
        if (!lut_sparse(luts_raw[i], static_cast<int>(fc_sizes[i]), lut17[i]))  return 1;
    }
    // 赛方允许的LUT-only预处理：在读取任何图片前完成拟合与联合准备。
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
        std::printf("PreferenceReport=%s\n", fc_selection->report_json.c_str());
        std::fflush(stdout);
        if (!fc_selection_report_path.empty()) {
            if (std::filesystem::exists(fc_selection_report_path)) throw std::runtime_error("选择报告已存在，拒绝覆盖");
            std::ofstream report_file(fc_selection_report_path, std::ios::binary);
            report_file << fc_selection->report_json << '\n';
            report_file.close();
            if (!report_file) throw std::runtime_error("无法完整写入选择报告");
        }
        if (!fc_selection->selected) {
            std::fprintf(stderr, "偏好选择失败：%s\n", fc::selection_status_string(fc_selection->status)); return 2;
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
        std::fprintf(stderr, "链准备失败：%s\n", fc::status_string(prep_status)); return 2;
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
            std::fprintf(stderr, "最终执行计划与选择回执或预算不符，拒绝读图运行\n"); return 2;
        }
        fc_selection.reset();
    }
    std::printf("FlashChroma threads=1 m=%u,%u,%u,%u structured=%d backend=%u representation=%u model_bytes=%zu sidecar_bytes=%zu arena_bytes=%zu object_bytes=%zu wrapper_nodes_bytes=%zu\n",
        fc_sizes[0],fc_sizes[1],fc_sizes[2],fc_sizes[3],int(info.structured),unsigned(info.backend),unsigned(info.representation),
        info.model_bytes,info.sidecar_bytes,info.arena_bytes,info.object_bytes,wrapper_nodes);
    } catch (const std::exception& error) {
        std::fprintf(stderr, "预处理/选择失败：%s\n", error.what()); return 2;
    }
    // free raw 16-bit LUTs
    for (int i = 0; i < 4; i++) std::vector<uint16_t>().swap(luts_raw[i]);

    print_time_now("SpareLut Time");

    int fc_success_count = 0;
    std::vector<double> deltas, perfs;
    deltas.reserve(MAX_IMAGES);
    perfs.reserve(MAX_IMAGES);

    for (int i = 1; i <= fc_image_count; i++) {
        std::string path = data_dir + "/image/" + std::to_string(i) + ".bin";
        if (!file_exists(path)) {
            deltas.push_back(255);
            perfs.push_back(255);
            continue;
        }

        Image img;
        if (!image_load_bin(path, img)) {
            std::fprintf(stderr, "skip %s (load failed)\n", path.c_str());
            deltas.push_back(255);
            perfs.push_back(255);
            continue;
        }

        double t0 = now_sec();
        Image result17;
        if (!apply_3d_lut(img, lut17[0], lut17[1], lut17[2], lut17[3], result17)) {
            deltas.push_back(255);
            perfs.push_back(255);
            continue;
        }
        double t1 = now_sec();
        double cost = t1 - t0;

        Image result256;
        if (!apply_3d_lut_ref(img, lut256[0], lut256[1], lut256[2], lut256[3], result256)) {
            deltas.push_back(255);
            perfs.push_back(255);
            continue;
        }

        double delta1 = color_dalta_calc(img, result256);
        double delta2 = color_dalta_calc(result256, result17);
        std::printf("Img: %s TimeCost: %.6f, Delta: %.6f %.6f\n",
                    path.c_str(), cost, delta1, delta2);

        ++fc_success_count;
        deltas.push_back(delta2);
        perfs.push_back(cost);
    }

    print_time_now("End Time");
    if (fc_success_count != fc_image_count) {
        std::fprintf(stderr, "批次处理不完整：%d/%d\n", fc_success_count, fc_image_count); return 2;
    }

    return 0;
}
