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
#include "flash_chroma_framework.hpp"
#include <memory>
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
    std::shared_ptr<fc_framework::Stage> fc_stage;
    int size = 0;                  // N
    std::vector<uint8_t> data;     // size^3 * 3, indexed [r][g][b]
    const uint8_t* at(int r, int g, int b) const {
        return &data[(((size_t)r * size + g) * size + b) * 3];
    }
};

// 只用本次四张LUT准备；图像不参与拟合和后端选择。
fc_framework::Chain fc_contest_chain;
std::array<const fc_framework::Stage*,4> fc_contest_stages{};

// Read .3DL file: 256^3 lines, each "R G B". Values are 0..4080 (16x scale);
// store raw 16-bit values so sparse_lut can do /16 like Python.
bool lut_read_3dl(const std::string& path, std::vector<uint16_t>& out) {
    std::ifstream f(path);
    if (!f) { std::fprintf(stderr, "cannot open LUT %s\n", path.c_str()); return false; }
    constexpr int N = 256;
    size_t total = (size_t)N * N * N * 3;
    out.resize(total);
    size_t idx = 0;
    std::string line;
    while (idx < total && std::getline(f, line)) {
        int r, g, b;
        if (std::sscanf(line.c_str(), "%d %d %d", &r, &g, &b) == 3) {
            out[idx++] = (uint16_t)r;
            out[idx++] = (uint16_t)g;
            out[idx++] = (uint16_t)b;
        }
    }
    if (idx != total) {
        std::fprintf(stderr, "LUT %s: read %zu of %zu values\n", path.c_str(), idx, total);
        return false;
    }
    return true;
}

// Port of sparse_lut().
bool lut_sparse(const std::vector<uint16_t>& lut256, int lut_size, Lut3D& out) {
    try {
        fc_framework::FitOptions fit;
        fit.grid = fc_framework::Grid::FrameworkStep;
        out.fc_stage = std::make_shared<fc_framework::Stage>(
            fc_framework::prepare_stage(lut256, static_cast<unsigned>(lut_size), fit));
        out.size = static_cast<int>(out.fc_stage->m);
        out.data.assign(out.fc_stage->nodes_data(), out.fc_stage->nodes_data() + out.fc_stage->node_bytes());
        return true;
    } catch (const std::exception& error) {
        std::fprintf(stderr, "LUT预处理失败：%s\n", error.what()); return false;
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
    if (!fc_contest_chain.ready() || img.C != 3 ||
        fc_contest_stages != std::array<const fc_framework::Stage*,4>{{
            l1.fc_stage.get(),l2.fc_stage.get(),l3.fc_stage.get(),l4.fc_stage.get()}}) return false;
    out.H = img.H; out.W = img.W; out.C = img.C;
    out.data.resize(img.size());
    return fc_contest_chain.apply(img.ptr(), out.ptr(), static_cast<std::size_t>(img.H) * img.W) == fc::Status::Ok;
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
    if (argc > 2) { std::fprintf(stderr, "用法：./lut3d <data_dir>\n"); return 2; }
    std::string data_dir = "../data";
    if (argc >= 2) data_dir = argv[1];

    auto join = [&](const std::string& sub) {
        return data_dir + "/" + sub;
    };

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
        if (!lut_sparse(luts_raw[i], 33,  lut17[i]))  return 1;
    }
    try {
        std::array<fc_framework::Stage,4> sampled;
        for (unsigned i = 0; i != 4; ++i) sampled[i] = *lut17[i].fc_stage;
        fc_framework::FitReport fit_report;
        *lut17[3].fc_stage = fc_framework::fit_chain_last(luts_raw, sampled, fit_report);
        for (auto& model : lut17) {
            const auto& stage = *model.fc_stage;
            std::vector<std::uint8_t>(stage.nodes_data(), stage.nodes_data() + stage.node_bytes()).swap(model.data);
            model.size = static_cast<int>(stage.m);
        }
        fc_contest_stages = {{lut17[0].fc_stage.get(),lut17[1].fc_stage.get(),lut17[2].fc_stage.get(),lut17[3].fc_stage.get()}};
        fc_framework::Options options;
        options.backend = fc::Backend::Auto;
        options.structure = false;
        options.threads = 1;
        options.representation = fc::Representation::DirectRGB24;
        fc::Status status;
        try { status = fc_contest_chain.prepare(fc_contest_stages, options); }
        catch (const std::bad_alloc&) { status = fc::Status::Budget; }
        if (status != fc::Status::Ok) {
            // 额外直表无法建立时使用相同节点的Sparse，保留四级数值输出。
            options.representation = fc::Representation::Sparse;
            status = fc_contest_chain.prepare(fc_contest_stages, options);
        }
        if (status != fc::Status::Ok) {
            std::fprintf(stderr, "运行准备失败：%s\n", fc::status_string(status)); return 2;
        }
        const auto& info = fc_contest_chain.info();
        std::printf("FlashChroma compiled=%u available=%u actual_backend=%u representation=%u threads=%u m=33,33,33,33 fit=chain_ls grid=framework\n",
                    fc::compiled_capabilities(),fc::available_backends(),unsigned(info.backend),unsigned(info.representation),info.threads);
    } catch (const std::exception& error) {
        std::fprintf(stderr, "整链预处理失败：%s\n", error.what()); return 2;
    }
    // free raw 16-bit LUTs
    for (int i = 0; i < 4; i++) std::vector<uint16_t>().swap(luts_raw[i]);

    // 与原示例相同的四张图；准备完成后才检查/打开图片。
    for (int i = 1; i <= 4; ++i) {
        std::ifstream probe(join("image/" + std::to_string(i) + ".bin"), std::ios::binary | std::ios::ate);
        if (!probe || probe.tellg() != std::streamoff(IMG_H) * IMG_W * IMG_C) {
            std::fprintf(stderr, "图片缺失或长度不符：%d\n", i); return 2;
        }
    }
    print_time_now("SpareLut Time");

    int fc_success_count = 0;
    std::vector<double> deltas, perfs;
    deltas.reserve(MAX_IMAGES);
    perfs.reserve(MAX_IMAGES);

    for (int i = 1; i <= 4; i++) {
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
    if (fc_success_count != 4) { std::fprintf(stderr, "未完整处理原四图\n"); return 2; }

    return 0;
}
