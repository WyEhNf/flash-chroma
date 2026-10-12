// jshc: command line driver for sparse-LUT colour mapping.
//
//   jshc apply  -i in.png -o out.png [-k tetra_zig_simd] [-t N] a.slut [b.slut ...]
//   jshc ref    -i in.png -o out.png [-t N] a.lut256 [b.lut256 ...]
//   jshc cube   -o out.raw [-k K] [-t N] a.slut [...]   (all 2^24 colours, index order)
//   jshc bench  -l list.txt [-k K] [-t N] [-r reps] [-w out_dir] a.slut [...]
//   jshc info
// bench prints one JSON object with per-phase timings (ms).
#include <algorithm>
#include <chrono>
#include <cstdio>
#include <cstring>
#include <fstream>
#include <numeric>
#include <stdexcept>
#include <string>
#include <thread>
#include <vector>

#include "jshc/lut.hpp"

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
  std::vector<uint8_t> rgb;
};

static Image load_image(const std::string& path) {
  Image im;
  int ch = 0;
  uint8_t* d = stbi_load(path.c_str(), &im.w, &im.h, &ch, 3);
  if (!d) throw std::runtime_error("cannot decode " + path);
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
  std::string kernel = "tetra_zig_simd";
  int threads = 0, reps = 3;
  uint32_t m = 33;
  std::vector<std::string> luts;
};

static Args parse(int argc, char** argv) {
  if (argc < 2) throw std::runtime_error("usage: jshc {apply|ref|cube|bench|fit-r14|info} ...");
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

static std::vector<SparseLut> load_sparse(const std::vector<std::string>& paths) {
  std::vector<SparseLut> v;
  for (auto& p : paths) v.push_back(SparseLut::load(p));
  return v;
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

int main(int argc, char** argv) try {
  Args a = parse(argc, argv);
  if (a.reps < 1) throw std::runtime_error("reps must be positive");
  if (a.threads < 0) throw std::runtime_error("threads must be nonnegative");
  if (a.cmd == "info") {
    std::printf("{\"avx2\": %s, \"openmp_threads\": %d, \"hw_threads\": %u}\n",
                avx2_available() ? "true" : "false", max_threads(),
                std::thread::hardware_concurrency());
    return 0;
  }
  if (a.luts.empty()) throw std::runtime_error("no LUT files given");
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
        "\"slut_bytes\": %zu}\n",
        a.m, F.size(), a.threads > 0 ? a.threads : max_threads(), a.reps, load_ms, best_ms,
        mean_ms, pct(fit_times, 0.5), size_t(a.m) * a.m * a.m * 3);
    return 0;
  }
  Kernel k = parse_kernel(a.kernel);

  if (a.cmd == "apply") {
    auto L = load_sparse(a.luts);
    Image im = load_image(a.in);
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
    apply_full_chain(fp, im.rgb.data(), size_t(im.w) * im.h, a.threads);
    save_image(a.out, im);
    return 0;
  }
  if (a.cmd == "cube") {
    auto L = load_sparse(a.luts);
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
    std::fwrite(buf.data(), 1, buf.size(), f);
    std::fclose(f);
    return 0;
  }
  if (a.cmd == "bench") {
    auto t0 = Clock::now();
    auto L = load_sparse(a.luts);
    double setup_ms = ms_since(t0);
    std::vector<std::string> files;
    {
      std::ifstream fl(a.list);
      std::string line;
      while (std::getline(fl, line))
        if (!line.empty()) files.push_back(line);
    }
    if (files.empty()) throw std::runtime_error("empty image list");
    std::vector<Image> imgs;
    std::vector<double> dec;
    for (auto& f : files) {
      auto t = Clock::now();
      imgs.push_back(load_image(f));
      dec.push_back(ms_since(t));
    }
    auto P = ptrs(L);
    std::vector<uint8_t> work;
    // warm-up
    work = imgs[0].rgb;
    apply_chain(P, work.data(), work.size() / 3, k, a.threads);
    std::vector<double> per_img;      // best-of-reps per image
    std::vector<double> rep_totals;   // whole-set time per rep
    per_img.assign(imgs.size(), 1e30);
    for (int r = 0; r < a.reps; ++r) {
      auto tr = Clock::now();
      for (size_t i = 0; i < imgs.size(); ++i) {
        work = imgs[i].rgb;  // copy excluded from per-image apply time
        auto t = Clock::now();
        apply_chain(P, work.data(), work.size() / 3, k, a.threads);
        per_img[i] = std::min(per_img[i], ms_since(t));
      }
      rep_totals.push_back(ms_since(tr));
    }
    double enc_ms = 0;
    if (!a.write_dir.empty()) {
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
    double mean = std::accumulate(per_img.begin(), per_img.end(), 0.0) / per_img.size();
    double dmean = std::accumulate(dec.begin(), dec.end(), 0.0) / dec.size();
    const double set_best = *std::min_element(rep_totals.begin(), rep_totals.end());
    const double set_ms_per_image = set_best / imgs.size();
    const double pixels_per_image = imgs[0].rgb.size() / 3;
    std::printf(
        "{\"kernel\": \"%s\", \"threads\": %d, \"stages\": %zu, \"m\": %u, \"images\": %zu, "
        "\"reps\": %d, \"setup_ms\": %.3f, \"decode_ms_mean\": %.3f, \"apply_ms_mean\": %.4f, "
        "\"apply_ms_p50\": %.4f, \"apply_ms_p95\": %.4f, \"apply_ms_max\": %.4f, "
        "\"set_ms_best_rep\": %.3f, \"set_ms_per_image_best_rep\": %.4f, "
        "\"set_mpix_per_s_best_rep\": %.1f, \"apply_write_png_ms_mean\": %.3f, "
        "\"mpix_per_s\": %.1f}\n",
        kernel_name(k), a.threads > 0 ? a.threads : max_threads(), L.size(), L[0].m,
        imgs.size(), a.reps, setup_ms, dmean, mean, pct(per_img, 0.5), pct(per_img, 0.95),
        pct(per_img, 1.0), set_best, set_ms_per_image,
        pixels_per_image / (set_ms_per_image * 1e3), enc_ms,
        pixels_per_image / (mean * 1e3));
    return 0;
  }
  throw std::runtime_error("unknown command " + a.cmd);
} catch (const std::exception& e) {
  std::fprintf(stderr, "jshc: %s\n", e.what());
  return 1;
}
