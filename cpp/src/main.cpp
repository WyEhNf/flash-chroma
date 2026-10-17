// jshc: command line driver for sparse-LUT colour mapping.
//
//   jshc apply  -i in.png -o out.png [-k auto] [-t N] a.slut [b.slut ...]
//   jshc ref    -i in.png -o out.png [-t N] a.lut256 [b.lut256 ...]
//   jshc cube   -o out.raw [-k K] [-t N] a.slut [...]   (all 2^24 colours, index order)
//   jshc bench  -l list.txt [-k K] [-t N] [-r reps] [--batch] [-w out_dir] a.slut [...]
//   jshc verify -l list.txt [-k K] [-t N] [--batch] [-o concatenated_rgb.raw] a.slut [...]
//   jshc info
//   jshc plan -k tetra_c99|tetra_structured_avx2 a.slut b.slut c.slut d.slut
// bench prints one JSON object with per-phase timings (ms).
#include <algorithm>
#include <chrono>
#include <cstdio>
#include <cstring>
#include <fstream>
#include <filesystem>
#include <numeric>
#include <stdexcept>
#include <string>
#include <thread>
#include <vector>

#include "jshc/lut.hpp"
#include "jshc/image_contract.hpp"

#define STB_IMAGE_IMPLEMENTATION
#define STBI_ONLY_PNG
#define STBI_ONLY_BMP
#define STBI_ONLY_PNM
#include "stb_image.h"
#define STB_IMAGE_WRITE_IMPLEMENTATION
#include "stb_image_write.h"

#if defined(_OPENMP)
#include <omp.h>
#endif

using namespace jshc;
using Clock = std::chrono::steady_clock;

static double ms_since(Clock::time_point t0) {
  return std::chrono::duration<double, std::milli>(Clock::now() - t0).count();
}

struct Image {
  int w = 0, h = 0;
  bool source_rgb8 = false;
  std::vector<uint8_t> rgb;
};

static Image load_image(const std::string& path) {
  Image im;
  int ch = 0;
  uint8_t* d = stbi_load(path.c_str(), &im.w, &im.h, &ch, 3);
  if (!d) throw std::runtime_error("cannot decode " + path);
  im.source_rgb8 = ch == 3 && !stbi_is_16_bit(path.c_str()) &&
                  jshc::detail::png_source_rgb8_or_other_container(path);
  im.rgb.assign(d, d + size_t(im.w) * im.h * 3);
  stbi_image_free(d);
  return im;
}

static bool ends_with(const std::string& s, const std::string& suf) {
  return s.size() >= suf.size() && s.compare(s.size() - suf.size(), suf.size(), suf) == 0;
}

static void save_image(const std::string& path, const Image& im) {
  int ok = 0;
  if (ends_with(path, ".png")) {
    stbi_write_png_compression_level = 1;
    ok = stbi_write_png(path.c_str(), im.w, im.h, 3, im.rgb.data(), im.w * 3);
  } else if (ends_with(path, ".bmp")) {
    ok = stbi_write_bmp(path.c_str(), im.w, im.h, 3, im.rgb.data());
  } else if (ends_with(path, ".ppm")) {
    FILE* f = std::fopen(path.c_str(), "wb");
    if (f) {
      std::fprintf(f, "P6\n%d %d\n255\n", im.w, im.h);
      ok = std::fwrite(im.rgb.data(), 1, im.rgb.size(), f) == im.rgb.size();
      std::fclose(f);
    }
  } else {
    throw std::runtime_error("unsupported output extension: " + path);
  }
  if (!ok) throw std::runtime_error("cannot write " + path);
}

struct Args {
  std::string cmd, in, out, list, write_dir;
  std::string kernel = "auto";
  bool competition = false;
  bool batch = false;
  int threads = 0, reps = 3;
  uint32_t m = 33;
  std::vector<std::string> luts;
};

static Args parse(int argc, char** argv) {
  if (argc < 2) throw std::runtime_error("usage: jshc {apply|ref|cube|bench|verify|fit-r14|info|plan} ...");
  Args a;
  a.cmd = argv[1];
  for (int i = 2; i < argc; ++i) {
    std::string s = argv[i];
    auto next = [&]() -> std::string {
      if (i + 1 >= argc) throw std::runtime_error("missing value for " + s);
      return argv[++i];
    };
    if (s == "-i") a.in = next();
    else if (s == "-o") a.out = next();
    else if (s == "-k") a.kernel = next();
    else if (s == "-t") a.threads = std::stoi(next());
    else if (s == "-r") a.reps = std::stoi(next());
    else if (s == "-m") a.m = uint32_t(std::stoul(next()));
    else if (s == "-l") a.list = next();
    else if (s == "-w") a.write_dir = next();
    else if (s == "--competition") a.competition = true;
    else if (s == "--batch") a.batch = true;
    else if (!s.empty() && s[0] == '-') throw std::runtime_error("unknown option " + s);
    else a.luts.push_back(s);
  }
  return a;
}

static int max_threads() {
#if defined(_OPENMP)
  return omp_get_max_threads();
#else
  return 1;
#endif
}

static constexpr bool openmp_enabled() {
#if defined(_OPENMP)
  return true;
#else
  return false;
#endif
}

static int thread_upper_bound(int requested) {
  return openmp_enabled() ? (requested > 0 ? requested : max_threads()) : 1;
}

static std::vector<SparseLut> load_sparse(const std::vector<std::string>& paths, bool competition) {
  std::vector<SparseLut> v;
  for (auto& p : paths) {
    v.push_back(SparseLut::load(p));
    if (competition && (v.back().m < 17 || v.back().m > 33))
      throw std::runtime_error("competition LUT m must be in [17,33]");
  }
  return v;
}

static void check_image(const Image& im, bool competition) {
  if (competition && (im.w != 1024 || im.h != 768 || !im.source_rgb8))
    throw std::runtime_error("competition image must be 1024x768 RGB8");
}

static void print_values(const char* key, const std::vector<double>& values) {
  std::printf(", \"%s\": [", key);
  for (size_t i = 0; i < values.size(); ++i) std::printf("%s%.6f", i ? ", " : "", values[i]);
  std::printf("]");
}

static std::vector<const SparseLut*> ptrs(const std::vector<SparseLut>& v) {
  std::vector<const SparseLut*> p;
  for (auto& x : v) p.push_back(&x);
  return p;
}

static double pct(std::vector<double> v, double q) {
  std::sort(v.begin(), v.end());
  size_t i = size_t(q * (v.size() - 1) + 0.5);
  return v[std::min(i, v.size() - 1)];
}

static void print_stage_sizes(const std::vector<SparseLut>& luts) {
  std::printf(", \"stage_m\": [");
  for (size_t i = 0; i < luts.size(); ++i) std::printf("%s%u", i ? ", " : "", luts[i].m);
  std::printf("]");
}

// Correctness preflight has its own command so hashing/writing never enters
// benchmark repetitions, alters their cache state, or requires time subtraction.
static void verify_images(const Args& a, const std::vector<Image>& imgs,
                          const std::vector<SparseLut>& luts, Kernel k) {
  constexpr uint64_t offset = UINT64_C(14695981039346656037);
  constexpr uint64_t prime = UINT64_C(1099511628211);
  const auto chain = ptrs(luts);
  std::ofstream raw;
  if (!a.out.empty()) {
    raw.open(a.out, std::ios::binary | std::ios::trunc);
    if (!raw) throw std::runtime_error("cannot write " + a.out);
  }
  uint64_t concatenated_hash = offset;
  size_t output_bytes = 0;
  std::vector<uint64_t> hashes(imgs.size());
  auto record = [&](size_t index, const std::vector<uint8_t>& pixels) {
    uint64_t hash = offset;
    for (uint8_t value : pixels) {
      hash = (hash ^ value) * prime;
      concatenated_hash = (concatenated_hash ^ value) * prime;
    }
    hashes[index] = hash;
    output_bytes += pixels.size();
    if (raw.is_open()) {
      raw.write(reinterpret_cast<const char*>(pixels.data()),
                static_cast<std::streamsize>(pixels.size()));
      if (!raw) throw std::runtime_error("incomplete verification output: " + a.out);
    }
  };
  if (a.batch) {
    std::vector<std::vector<uint8_t>> output;
    std::vector<RgbImageView> views;
    output.reserve(imgs.size());
    views.reserve(imgs.size());
    for (const auto& im : imgs) output.push_back(im.rgb);
    for (auto& pixels : output) views.push_back({pixels.data(), pixels.size() / 3});
    apply_chain_batch(chain, views, k, a.threads);
    for (size_t i = 0; i < output.size(); ++i) record(i, output[i]);
  } else {
    std::vector<uint8_t> output;
    for (size_t i = 0; i < imgs.size(); ++i) {
      output = imgs[i].rgb;
      apply_chain(chain, output.data(), output.size() / 3, k, a.threads);
      record(i, output);
    }
  }
  if (raw.is_open()) {
    raw.close();
    if (!raw) throw std::runtime_error("cannot close verification output: " + a.out);
  }
  std::printf("{\"cmd\": \"verify\", \"verification_only\": true, \"kernel\": \"%s\", "
              "\"stages\": %zu, \"images\": %zu, \"batch_mode\": %s, \"output_bytes\": %zu, "
              "\"checksum_algorithm\": \"fnv1a64\", \"output_checksum_fnv1a64\": \"%llu\", "
              "\"raw_output_written\": %s, \"output_layout\": \"list order; packed RGB8; no headers\", "
              "\"requested_threads\": %d, \"openmp_enabled\": %s",
              kernel_name(k), luts.size(), imgs.size(), a.batch ? "true" : "false", output_bytes,
              static_cast<unsigned long long>(concatenated_hash), a.out.empty() ? "false" : "true",
              a.threads, openmp_enabled() ? "true" : "false");
  print_stage_sizes(luts);
  std::printf(", \"per_image\": [");
  for (size_t i = 0; i < imgs.size(); ++i) {
    std::printf("%s{\"index\": %zu, \"width\": %d, \"height\": %d, \"output_bytes\": %zu, "
                "\"output_checksum_fnv1a64\": \"%llu\"}",
                i ? ", " : "", i, imgs[i].w, imgs[i].h, imgs[i].rgb.size(),
                static_cast<unsigned long long>(hashes[i]));
  }
  std::printf("]}\n");
}

int main(int argc, char** argv) try {
  Args a = parse(argc, argv);
  if (a.reps < 1) throw std::runtime_error("reps must be positive");
  if (a.threads < 0) throw std::runtime_error("threads must be nonnegative");
  if (a.batch && a.cmd != "bench" && a.cmd != "verify")
    throw std::runtime_error("--batch is only valid for bench or verify");
  if (a.cmd == "info") {
    std::printf("{\"avx2\": %s, \"openmp_threads\": %d, \"hw_threads\": %u, \"default_kernel\": \"%s\", \"available_kernels\": [",
                avx2_available() ? "true" : "false", max_threads(),
                std::thread::hardware_concurrency(), kernel_name(resolve_kernel(parse_kernel("auto"))));
    bool first = true;
    for (const auto name : {"tetra_scalar", "tetra_avx2", "tetra_avx2_madd", "tetra_avx2_scalar_gather", "tetra_avx2_exact_float", "tetra_c99", "tetra_structured_avx2", "tetra_cpp_simd", "tetra_zig_simd4",
                            "tetra_zig_simd8", "tetra_zig_simd", "tetra_zig_simd16", "tetra_rust_simd", "tri_float"}) {
      if (kernel_available(parse_kernel(name))) {
        std::printf("%s\"%s\"", first ? "" : ", ", name);
        first = false;
      }
    }
    std::printf("], \"openmp_enabled\": %s}\n", openmp_enabled() ? "true" : "false");
    return 0;
  }
  if (a.luts.empty()) throw std::runtime_error("no LUT files given");
  if (a.competition && (a.luts.size() != 4 || a.cmd == "fit-r14"))
    throw std::runtime_error("competition mode requires four independent stages; fit-r14 is a research composite fitter");
  if (a.cmd == "fit-r14") {
    auto t0 = Clock::now();
    std::vector<FullLut> F;
    for (auto& p : a.luts) F.push_back(FullLut::load(p));
    std::vector<const FullLut*> fp;
    for (auto& f : F) fp.push_back(&f);
    double load_ms = ms_since(t0);

    SparseLut out_lut;
    std::vector<double> fit_times;
    for (int r = 0; r < a.reps; ++r) {
      auto tf = Clock::now();
      out_lut = fit_r14(fp, a.m, a.threads, true);
      fit_times.push_back(ms_since(tf));
    }
    if (!a.out.empty()) out_lut.save(a.out);
    double best_ms = *std::min_element(fit_times.begin(), fit_times.end());
    double mean_ms = std::accumulate(fit_times.begin(), fit_times.end(), 0.0) / fit_times.size();
    std::printf(
        "{\"cmd\": \"fit-r14\", \"m\": %u, \"stages_in\": %zu, \"threads\": %d, \"reps\": %d, "
        "\"load_ms\": %.3f, \"fit_ms_best\": %.3f, \"fit_ms_mean\": %.3f, \"fit_ms_p50\": %.3f, "
        "\"slut_bytes\": %zu, \"requested_threads\": %d, \"openmp_enabled\": %s, "
        "\"thread_count_semantics\": \"upper bound; runtime may use fewer workers\"}\n",
        a.m, F.size(), thread_upper_bound(a.threads), a.reps, load_ms, best_ms,
        mean_ms, pct(fit_times, 0.5), size_t(a.m) * a.m * a.m * 3,
        a.threads, openmp_enabled() ? "true" : "false");
    return 0;
  }
  Kernel k = resolve_kernel(parse_kernel(a.kernel));

  if (a.cmd == "plan") {
    if (k != Kernel::TetraC99 && k != Kernel::TetraStructuredAvx2)
      throw std::runtime_error("plan requires -k tetra_c99 or -k tetra_structured_avx2");
    auto models = load_sparse(a.luts, a.competition);
    const auto plan = inspect_structured_chain(ptrs(models));
    size_t runtime_bytes = 0, payload = 0;
    for (const auto& model : models) {
      if (k == Kernel::TetraStructuredAvx2) (void)model.packed_tables();
      runtime_bytes += model.runtime_bytes(); payload += model.nodes.size();
    }
    std::printf("{\"cmd\":\"plan\",\"kernel\":\"%s\",\"proof_scope\":\"complete stored nodes and complete prefix-output superset\","
                "\"four_independent_stages\":true,\"serialized_copy_bytes\":%zu,\"prepared_workspace_bytes\":%zu,"
                "\"model_runtime_bytes\":%zu,\"model_node_payload_bytes\":%zu,\"stages\":[",
                kernel_name(k), plan.serialized_copy_bytes, plan.prepared_workspace_bytes, runtime_bytes, payload);
    const char* names[] = {"tetra", "curve", "vertex", "constant"};
    for (size_t s = 0; s < 4; ++s)
      std::printf("%s{\"stage\":%zu,\"path\":\"%s\",\"model_flags\":%u,\"effective_one_hot\":%s}",
                  s ? "," : "", s + 1, names[plan.path[s]], plan.model_flags[s], plan.effective_one_hot[s] ? "true" : "false");
    std::printf("]}\n");
    return 0;
  }

  if (a.cmd == "apply") {
    auto L = load_sparse(a.luts, a.competition);
    Image im = load_image(a.in);
    check_image(im, a.competition);
    apply_chain(ptrs(L), im.rgb.data(), size_t(im.w) * im.h, k, a.threads);
    save_image(a.out, im);
    return 0;
  }
  if (a.cmd == "ref") {
    std::vector<FullLut> F;
    for (auto& p : a.luts) F.push_back(FullLut::load(p));
    std::vector<const FullLut*> fp;
    for (auto& f : F) fp.push_back(&f);
    Image im = load_image(a.in);
    check_image(im, a.competition);
    apply_full_chain(fp, im.rgb.data(), size_t(im.w) * im.h, a.threads);
    save_image(a.out, im);
    return 0;
  }
  if (a.cmd == "cube") {
    auto L = load_sparse(a.luts, a.competition);
    const size_t n = size_t(1) << 24;
    std::vector<uint8_t> buf(n * 3);
    for (size_t i = 0; i < n; ++i) {
      buf[3 * i] = uint8_t(i >> 16);
      buf[3 * i + 1] = uint8_t(i >> 8);
      buf[3 * i + 2] = uint8_t(i);
    }
    apply_chain(ptrs(L), buf.data(), n, k, a.threads);
    FILE* f = std::fopen(a.out.c_str(), "wb");
    if (!f) throw std::runtime_error("cannot write " + a.out);
    const bool written = std::fwrite(buf.data(), 1, buf.size(), f) == buf.size();
    const int closed = std::fclose(f);
    if (!written || closed != 0) throw std::runtime_error("incomplete cube output: " + a.out);
    std::printf("{\"kernel\":\"%s\",\"pixels\":%zu,\"stages\":%zu}\n", kernel_name(k), n, L.size());
    return 0;
  }
  if (a.cmd == "bench" || a.cmd == "verify") {
    auto t0 = Clock::now();
    auto L = load_sparse(a.luts, a.competition);
    double setup_ms = ms_since(t0);
    std::vector<std::string> files;
    {
      std::ifstream fl(a.list);
      std::string line;
      while (std::getline(fl, line))
        if (!line.empty()) {
          if (line.back() == '\r') line.pop_back();
          if (!line.empty()) files.push_back(line);
        }
    }
    if (files.empty()) throw std::runtime_error("empty image list");
    std::vector<Image> imgs;
    std::vector<double> dec;
    for (auto& f : files) {
      auto t = Clock::now();
      imgs.push_back(load_image(f));
      check_image(imgs.back(), a.competition);
      dec.push_back(ms_since(t));
    }
    if (a.cmd == "verify") {
      if (!a.write_dir.empty()) throw std::runtime_error("verify uses -o for concatenated raw RGB output");
      verify_images(a, imgs, L, k);
      return 0;
    }
    auto P = ptrs(L);
    std::vector<uint8_t> work;
    std::vector<std::vector<uint8_t>> batch_work;
    std::vector<RgbImageView> batch_views;
    // Preserve the cold first application instead of silently discarding it.
    if (a.batch) {
      batch_work.reserve(imgs.size());
      batch_views.reserve(imgs.size());
      for (const auto& im : imgs) batch_work.push_back(im.rgb);
      for (auto& pixels : batch_work) batch_views.push_back({pixels.data(), pixels.size() / 3});
    } else {
      work = imgs[0].rgb;
    }
    auto cold = Clock::now();
    if (a.batch) apply_chain_batch(P, batch_views, k, a.threads);
    else apply_chain(P, work.data(), work.size() / 3, k, a.threads);
    const double cold_apply_ms = ms_since(cold);
    std::vector<double> per_img;      // best-of-reps per image
    std::vector<double> rep_totals;   // whole-set time per rep
    std::vector<double> copy_totals, apply_totals;
    per_img.assign(imgs.size(), 1e30);
    for (int r = 0; r < a.reps; ++r) {
      auto tr = Clock::now();
      double copy_ms = 0.0, apply_ms = 0.0;
      if (a.batch) {
        auto tc = Clock::now();
        for (size_t i = 0; i < imgs.size(); ++i)
          std::copy(imgs[i].rgb.begin(), imgs[i].rgb.end(), batch_work[i].begin());
        copy_ms = ms_since(tc);
        auto ta = Clock::now();
        apply_chain_batch(P, batch_views, k, a.threads);
        apply_ms = ms_since(ta);
      } else for (size_t i = 0; i < imgs.size(); ++i) {
        auto tc = Clock::now();
        work = imgs[i].rgb;  // copy excluded from per-image apply time
        copy_ms += ms_since(tc);
        auto t = Clock::now();
        apply_chain(P, work.data(), work.size() / 3, k, a.threads);
        const double elapsed = ms_since(t);
        apply_ms += elapsed;
        per_img[i] = std::min(per_img[i], elapsed);
      }
      rep_totals.push_back(ms_since(tr));
      copy_totals.push_back(copy_ms);
      apply_totals.push_back(apply_ms);
    }
    double enc_ms = 0;
    if (!a.write_dir.empty()) {
      std::filesystem::create_directories(a.write_dir);
      auto t = Clock::now();
      for (size_t i = 0; i < imgs.size(); ++i) {
        Image o = imgs[i];
        apply_chain(P, o.rgb.data(), o.rgb.size() / 3, k, a.threads);
        std::string name = files[i].substr(files[i].find_last_of("/\\") + 1);
        name = name.substr(0, name.find_last_of('.')) + ".png";
        save_image(a.write_dir + "/" + name, o);
      }
      enc_ms = ms_since(t) / imgs.size();
    }
    double mean = a.batch ? 0.0 : std::accumulate(per_img.begin(), per_img.end(), 0.0) / per_img.size();
    double dmean = std::accumulate(dec.begin(), dec.end(), 0.0) / dec.size();
    const double set_best = *std::min_element(rep_totals.begin(), rep_totals.end());
    const double set_p50 = pct(rep_totals, 0.5);
    const double set_ms_per_image = set_best / imgs.size();
    size_t image_bytes = 0, runtime_bytes = 0, payload_bytes = 0;
    for (const auto& im : imgs) image_bytes += im.rgb.size();
    for (const auto& lut : L) {
      runtime_bytes += lut.runtime_bytes();
      payload_bytes += lut.nodes.size();
    }
    const double pixels_per_image = double(image_bytes) / (3.0 * imgs.size());
    size_t work_bytes = work.capacity();
    for (const auto& pixels : batch_work) work_bytes += pixels.capacity();
    std::printf(
        "{\"kernel\": \"%s\", \"threads\": %d, \"stages\": %zu, \"m\": %u, \"images\": %zu, "
        "\"reps\": %d, \"setup_ms\": %.3f, \"decode_ms_mean\": %.3f, ",
        kernel_name(k), thread_upper_bound(a.threads), L.size(), L[0].m,
        imgs.size(), a.reps, setup_ms, dmean);
    if (a.batch) {
      std::printf("\"apply_ms_mean\": null, \"apply_ms_p50\": null, \"apply_ms_p95\": null, \"apply_ms_max\": null, \"mpix_per_s\": null, ");
    } else {
      std::printf("\"apply_ms_mean\": %.4f, \"apply_ms_p50\": %.4f, \"apply_ms_p95\": %.4f, \"apply_ms_max\": %.4f, \"mpix_per_s\": %.1f, ",
                  mean, pct(per_img, 0.5), pct(per_img, 0.95), pct(per_img, 1.0), pixels_per_image / (mean * 1e3));
    }
    std::printf(
        "\"set_ms_best_rep\": %.3f, \"set_ms_p50_rep\": %.3f, \"set_ms_per_image_best_rep\": %.4f, "
        "\"set_mpix_per_s_best_rep\": %.1f, \"apply_write_png_ms_mean\": %.3f",
        set_best, set_p50, set_ms_per_image, pixels_per_image / (set_ms_per_image * 1e3), enc_ms);
    if (a.batch) std::printf(", \"cold_apply_ms\": null, \"cold_batch_ms\": %.6f", cold_apply_ms);
    else std::printf(", \"cold_apply_ms\": %.6f, \"cold_batch_ms\": null", cold_apply_ms);
    std::printf(", \"batch_mode\": %s, \"work_image_bytes\": %zu, \"set_ms_per_image_p50_rep\": %.6f, "
                "\"model_runtime_bytes\": %zu, \"model_node_payload_bytes\": %zu, "
                "\"kernel_block_scratch_bytes_per_worker\": %zu, "
                "\"preloaded_image_bytes\": %zu, \"driver_elapsed_ms\": %.6f, "
                "\"timing_scope\": \"whole set includes copy and mapping; excludes fitting, model load, decoding and output encoding\"",
                a.batch ? "true" : "false", work_bytes, set_p50 / imgs.size(), runtime_bytes, payload_bytes,
                kernel_scratch_bytes(k), image_bytes, ms_since(t0));
    print_values("set_ms_reps", rep_totals);
    print_values("copy_ms_reps", copy_totals);
    print_values("apply_ms_reps", apply_totals);
    print_stage_sizes(L);
    std::printf(", \"requested_threads\": %d, \"openmp_enabled\": %s, "
                "\"thread_count_semantics\": \"upper bound; small inputs and OpenMP dynamic teams may use fewer workers\"}\n",
                a.threads, openmp_enabled() ? "true" : "false");
    return 0;
  }
  throw std::runtime_error("unknown command " + a.cmd);
} catch (const std::exception& e) {
  std::fprintf(stderr, "jshc: %s\n", e.what());
  return 1;
}
