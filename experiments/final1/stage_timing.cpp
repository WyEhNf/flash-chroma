// 分段诊断入口；正式 main 原字节内嵌，不向其原函数添加计时语句。
#define main final1_original_main
#include "main.cpp"
#undef main
#include <iomanip>
#include <iostream>
#include <numeric>

int main(int argc, char** argv) {
    if (argc != 4) return 2;
    const std::string data_dir = argv[1];
    const int count = std::atoi(argv[2]);
    if (count < 1 || count > 100) return 2;
    struct Row { double load, map, reference, delta1, delta2, mean; };
    std::vector<Row> rows;
    rows.reserve(count);
    const auto begin = now_sec();
    print_time_now("Start Time");
    std::array<std::vector<uint16_t>, 4> raw;
    for (int i = 0; i < 4; ++i)
        if (!lut_read_3dl(data_dir + "/LUT/Test" + std::to_string(i+1) + ".3DL", raw[i])) return 3;
    const auto read_end = now_sec();
    print_time_now("getLut Time");
    std::array<Lut3D, 4> ref, model;
    double reference_prepare = 0, sample = 0;
    for (int i = 0; i < 4; ++i) {
        auto at = now_sec();
        if (!lut_sparse_ref(raw[i], 256, ref[i])) return 4;
        reference_prepare += now_sec()-at;
        at = now_sec();
        if (!lut_sparse(raw[i], 33, model[i])) return 4;
        sample += now_sec()-at;
    }
    auto at = now_sec();
    if (!fc_delivery_pipeline.prepare(raw, model)) return 5;
    const double prepare = now_sec()-at;
    at = now_sec();
    for (auto& values : raw) std::vector<uint16_t>().swap(values);
    const double raw_release = now_sec()-at;
    const auto sparse_end = now_sec();
    print_time_now("SpareLut Time");
    std::vector<double> deltas, perfs;
    deltas.reserve(MAX_IMAGES); perfs.reserve(MAX_IMAGES);
    for (int i = 1; i <= count; ++i) {
        const std::string path = data_dir + "/image/" + std::to_string(i) + ".bin";
        at = now_sec();
        if (!file_exists(path)) return 6;
        Image img;
        if (!image_load_bin(path, img)) return 6;
        Row row{}; row.load = now_sec()-at;
        double t0 = now_sec();
        Image result17;
        if (!apply_3d_lut(img, model[0], model[1], model[2], model[3], result17)) return 7;
        double t1 = now_sec();
        double cost = t1-t0;
        row.map = cost;
        at = now_sec();
        Image result256;
        if (!apply_3d_lut_ref(img, ref[0], ref[1], ref[2], ref[3], result256)) return 8;
        row.reference = now_sec()-at;
        at = now_sec();
        double delta1 = color_dalta_calc(img, result256);
        row.delta1 = now_sec()-at;
        at = now_sec();
        double delta2 = color_dalta_calc(result256, result17);
        row.delta2 = now_sec()-at; row.mean = delta2;
        std::printf("Img: %s TimeCost: %.6f, Delta: %.6f %.6f\n", path.c_str(), cost, delta1, delta2);
        deltas.push_back(delta2); perfs.push_back(cost); rows.push_back(row);
    }
    const auto end = now_sec();
    print_time_now("End Time");
    std::ofstream out(argv[3]);
    if (!out) return 9;
    out << std::setprecision(17)
        << "{\"images\":" << count << ",\"backend\":" << unsigned(fc_delivery_pipeline.info().backend)
        << ",\"read_seconds\":" << read_end-begin
        << ",\"reference_prepare_seconds\":" << reference_prepare
        << ",\"sample_seconds\":" << sample
        << ",\"prepare_seconds\":" << prepare
        << ",\"fit_seconds\":" << fc_delivery_pipeline.fit_seconds()
        << ",\"search_seconds\":" << fc_delivery_pipeline.search_seconds()
        << ",\"direct_prepare_seconds\":" << fc_delivery_pipeline.prepare_seconds()
        << ",\"raw_release_seconds\":" << raw_release
        << ",\"getLut_to_SpareLut_seconds\":" << sparse_end-read_end
        << ",\"SpareLut_to_End_seconds\":" << end-sparse_end
        << ",\"Start_to_End_seconds\":" << end-begin << ",\"per_image\":[";
    bool first = true;
    for (const auto& row : rows) {
        if (!first) out << ',';
        first = false;
        out << "{\"load_seconds\":" << row.load << ",\"mapping_seconds\":" << row.map
            << ",\"reference_seconds\":" << row.reference << ",\"delta1_seconds\":" << row.delta1
            << ",\"delta2_seconds\":" << row.delta2 << ",\"mean\":" << row.mean << '}';
    }
    out << "]}\n";
    return out ? 0 : 9;
}
