// Optional standalone CUDA backend. All four stages use the serialized Q16 tables.
#include <cuda_runtime.h>
#include <algorithm>
#include <array>
#include <chrono>
#include <cmath>
#include <cstdint>
#include <cstdio>
#include <cstring>
#include <filesystem>
#include <fstream>
#include <iomanip>
#include <iostream>
#include <limits>
#include <memory>
#include <sstream>
#include <stdexcept>
#include <string>
#include <vector>

#define STB_IMAGE_IMPLEMENTATION
#define STBI_FAILURE_USERMSG
#define STBI_ONLY_PNG
#define STBI_ONLY_BMP
#define STBI_ONLY_PNM
#include "stb_image.h"
#define STB_IMAGE_WRITE_IMPLEMENTATION
#include "stb_image_write.h"

using Clock = std::chrono::steady_clock;
static double milliseconds(Clock::time_point start) {
  return std::chrono::duration<double, std::milli>(Clock::now() - start).count();
}
static void check(cudaError_t status, const char* expression) {
  if (status != cudaSuccess) throw std::runtime_error(std::string(expression) + ": " + cudaGetErrorString(status));
}
#define CUDA(expression) check((expression), #expression)

struct DeviceBuffer {
  void* pointer = nullptr;
  size_t bytes = 0;
  explicit DeviceBuffer(size_t size) : bytes(size) { CUDA(cudaMalloc(&pointer, size)); }
  ~DeviceBuffer() { if (pointer) cudaFree(pointer); }
  DeviceBuffer(const DeviceBuffer&) = delete;
  DeviceBuffer& operator=(const DeviceBuffer&) = delete;
};
struct PinnedBuffer {
  uint8_t* pointer = nullptr;
  explicit PinnedBuffer(size_t size) { CUDA(cudaMallocHost(reinterpret_cast<void**>(&pointer), size)); }
  ~PinnedBuffer() { if (pointer) cudaFreeHost(pointer); }
  PinnedBuffer(const PinnedBuffer&) = delete;
  PinnedBuffer& operator=(const PinnedBuffer&) = delete;
};
struct Event {
  cudaEvent_t value{};
  Event() { CUDA(cudaEventCreate(&value)); }
  ~Event() { cudaEventDestroy(value); }
  Event(const Event&) = delete;
  Event& operator=(const Event&) = delete;
  void record() { CUDA(cudaEventRecord(value)); }
  void sync() { CUDA(cudaEventSynchronize(value)); }
};
static float elapsed(const Event& first, const Event& last) {
  float result = 0;
  CUDA(cudaEventElapsedTime(&result, first.value, last.value));
  return result;
}

struct KernelTables {
  const uint32_t* nodes;
  const unsigned long long* axes; // fraction in high 32 bits, precomputed node offset in low bits
  uint32_t node_offsets[4];
  uint32_t strides[4][3];
};

__device__ __forceinline__ void compare_swap(int& f1, int& s1, int& f2, int& s2) {
  const bool swap = f2 > f1;
  const int old_f = f1, old_s = s1;
  f1 = swap ? f2 : f1; s1 = swap ? s2 : s1;
  f2 = swap ? old_f : f2; s2 = swap ? old_s : s2;
}

__device__ __forceinline__ uint32_t map_pixel(KernelTables tables, uint32_t rgb) {
#pragma unroll
  for (int stage = 0; stage < 4; ++stage) {
    const unsigned long long* axes = tables.axes + stage * 768;
    const unsigned long long ar = __ldg(axes + (rgb & 255));
    const unsigned long long ag = __ldg(axes + 256 + ((rgb >> 8) & 255));
    const unsigned long long ab = __ldg(axes + 512 + ((rgb >> 16) & 255));
    int f1 = int(ar >> 32), f2 = int(ag >> 32), f3 = int(ab >> 32);
    int s1 = int(tables.strides[stage][0]);
    int s2 = int(tables.strides[stage][1]);
    int s3 = int(tables.strides[stage][2]);
    compare_swap(f1, s1, f2, s2);
    compare_swap(f1, s1, f3, s3);
    compare_swap(f2, s2, f3, s3);
    const uint32_t* nodes = tables.nodes + tables.node_offsets[stage] + uint32_t(ar) + uint32_t(ag) + uint32_t(ab);
    const uint32_t v0 = __ldg(nodes), v1 = __ldg(nodes + s1);
    const uint32_t v2 = __ldg(nodes + s1 + s2), v3 = __ldg(nodes + s1 + s2 + s3);
    rgb = 0;
#pragma unroll
    for (int channel = 0; channel < 3; ++channel) {
      const int shift = channel * 8;
      const int c0 = int((v0 >> shift) & 255), c1 = int((v1 >> shift) & 255);
      const int c2 = int((v2 >> shift) & 255), c3 = int((v3 >> shift) & 255);
      const int value = ((c0 << 16) + (c1 - c0) * f1 + (c2 - c1) * f2 + (c3 - c2) * f3 + 32768) >> 16;
      rgb |= uint32_t(value) << shift;
    }
  }
  return rgb;
}

template<bool Cube>
__global__ void apply_fused4(KernelTables tables, const uint8_t* input, uint8_t* output, size_t pixels) {
  const size_t pixel = size_t(blockIdx.x) * blockDim.x + threadIdx.x;
  if (pixel >= pixels) return;
  const size_t offset = 3 * pixel;
  uint32_t rgb;
  if constexpr (Cube) {
    rgb = uint32_t((pixel >> 16) & 255) | uint32_t((pixel >> 8) & 255) << 8 | uint32_t(pixel & 255) << 16;
  } else {
    rgb = uint32_t(input[offset]) | uint32_t(input[offset + 1]) << 8 | uint32_t(input[offset + 2]) << 16;
  }
  rgb = map_pixel(tables, rgb);
  output[offset] = uint8_t(rgb); output[offset + 1] = uint8_t(rgb >> 8); output[offset + 2] = uint8_t(rgb >> 16);
}

static std::vector<uint8_t> read_bytes(const std::string& path) {
  std::ifstream stream(path, std::ios::binary | std::ios::ate);
  if (!stream) throw std::runtime_error("cannot read " + path);
  const auto size = stream.tellg();
  if (size < 0) throw std::runtime_error("cannot size " + path);
  std::vector<uint8_t> bytes(static_cast<size_t>(size));
  stream.seekg(0);
  if (!stream.read(reinterpret_cast<char*>(bytes.data()), bytes.size())) throw std::runtime_error("short read " + path);
  return bytes;
}
static uint32_t little32(const uint8_t* pointer) {
  return uint32_t(pointer[0]) | uint32_t(pointer[1]) << 8 | uint32_t(pointer[2]) << 16 | uint32_t(pointer[3]) << 24;
}
static uint64_t checksum(const uint8_t* bytes, size_t size) {
  uint64_t value = 14695981039346656037ull;
  for (size_t index = 0; index < size; ++index) value = (value ^ bytes[index]) * 1099511628211ull;
  return value;
}
static void write_bytes(const std::string& path, const uint8_t* bytes, size_t size) {
  std::ofstream stream(path, std::ios::binary);
  if (!stream.write(reinterpret_cast<const char*>(bytes), size)) throw std::runtime_error("cannot write " + path);
  stream.close();
  if (!stream) throw std::runtime_error("cannot complete output " + path);
}
struct Image {
  int width = 0, height = 0;
  std::vector<uint8_t> rgb;
};
static Image load_rgb8(const std::string& path, bool competition) {
  Image image;
  int channels = 0;
  if (stbi_is_16_bit(path.c_str()) || stbi_is_hdr(path.c_str()))
    throw std::runtime_error("image must have 8-bit RGB channels: " + path);
  std::unique_ptr<uint8_t, decltype(&stbi_image_free)> pixels(
      stbi_load(path.c_str(), &image.width, &image.height, &channels, 0), stbi_image_free);
  if (!pixels) throw std::runtime_error("cannot decode " + path);
  if (channels != 3 || image.width <= 0 || image.height <= 0)
    throw std::runtime_error("image must have exactly three RGB8 channels: " + path);
  if (competition && (image.width != 1024 || image.height != 768))
    throw std::runtime_error("competition image must be 1024x768 RGB8: " + path);
  image.rgb.assign(pixels.get(), pixels.get() + size_t(image.width) * image.height * 3);
  return image;
}
struct HostTables {
  std::vector<uint32_t> nodes;
  std::array<unsigned long long, 4 * 768> axes{};
  KernelTables config{};
  std::array<uint32_t, 4> sizes{};
  size_t serialized_bytes = 0;
  explicit HostTables(const std::vector<std::string>& paths) {
    if (paths.size() != 4) throw std::runtime_error("exactly four sparse stages are required");
    for (int stage = 0; stage < 4; ++stage) {
      const auto bytes = read_bytes(paths[stage]);
      if (bytes.size() < 16 || std::memcmp(bytes.data(), "SLUT", 4) != 0) throw std::runtime_error("bad SLUT header");
      const uint32_t m = little32(bytes.data() + 8);
      const size_t expected = 16 + 12 * size_t(m) + 768 + 3072 + 3 * size_t(m) * m * m;
      if (little32(bytes.data() + 4) != 1 || little32(bytes.data() + 12) != 0 || m < 17 || m > 33 || bytes.size() != expected)
        throw std::runtime_error("SLUT must be v1, uint8 RGB, 17<=m<=33 with exact file size");
      sizes[stage] = m; serialized_bytes += bytes.size();
      for (int axis = 0; axis < 3; ++axis) {
        float previous = -std::numeric_limits<float>::infinity();
        for (uint32_t knot = 0; knot < m; ++knot) {
          float value = 0; std::memcpy(&value, bytes.data() + 16 + 4 * (axis * m + knot), 4);
          if (!std::isfinite(value) || value <= previous || (knot == 0 && value > 0) || (knot == m - 1 && value < 255))
            throw std::runtime_error("invalid sparse grid");
          previous = value;
        }
      }
      config.node_offsets[stage] = static_cast<uint32_t>(nodes.size());
      const uint32_t strides[] = {m * m, m, 1};
      for (int axis = 0; axis < 3; ++axis) {
        config.strides[stage][axis] = strides[axis];
        for (int value = 0; value < 256; ++value) {
          const size_t index = axis * 256 + value;
          const uint32_t cell = bytes[16 + 12 * m + index];
          const uint32_t fraction = little32(bytes.data() + 16 + 12 * m + 768 + 4 * index);
          if (cell > m - 2 || fraction > 65536) throw std::runtime_error("invalid Q16 axis table");
          axes[stage * 768 + index] = (static_cast<unsigned long long>(fraction) << 32) | (cell * strides[axis]);
        }
      }
      const uint8_t* rgb = bytes.data() + 16 + 12 * m + 768 + 3072;
      for (size_t node = 0; node < size_t(m) * m * m; ++node)
        nodes.push_back(uint32_t(rgb[node * 3]) | uint32_t(rgb[node * 3 + 1]) << 8 | uint32_t(rgb[node * 3 + 2]) << 16);
    }
  }
};
struct Model {
  DeviceBuffer nodes, axes;
  KernelTables config;
  explicit Model(const HostTables& host) : nodes(host.nodes.size() * sizeof(uint32_t)), axes(sizeof(host.axes)), config(host.config) {
    CUDA(cudaMemcpy(nodes.pointer, host.nodes.data(), nodes.bytes, cudaMemcpyHostToDevice));
    CUDA(cudaMemcpy(axes.pointer, host.axes.data(), axes.bytes, cudaMemcpyHostToDevice));
    config.nodes = static_cast<uint32_t*>(nodes.pointer);
    config.axes = static_cast<unsigned long long*>(axes.pointer);
  }
  void apply(const uint8_t* input, uint8_t* output, size_t pixels, int block) const {
    apply_fused4<false><<<static_cast<unsigned int>((pixels + block - 1) / block), block>>>(config, input, output, pixels);
    CUDA(cudaGetLastError());
  }
};
static void print_vector(const char* name, const std::vector<double>& values) {
  std::cout << ",\"" << name << "\":[";
  for (size_t index = 0; index < values.size(); ++index) { if (index) std::cout << ','; std::cout << values[index]; }
  std::cout << ']';
}
static double median(std::vector<double> values) {
  std::sort(values.begin(), values.end());
  const size_t middle = values.size() / 2;
  return values.size() % 2 ? values[middle] : (values[middle - 1] + values[middle]) * 0.5;
}
struct Options {
  std::string command, input, output, list;
  std::vector<std::string> models;
  int device = 0, reps = 5, batch = 100, block = 256;
  bool competition = false;
};
static Options parse(int argc, char** argv) {
  if (argc < 2) throw std::runtime_error("usage: jshc_gpu info|apply -i image -o image.png|pixels -i RGB.raw -o RGB.raw|cube -o RGB.raw|verify -l list [-o RGB.raw]|bench -l list [-r reps] [--batch-images N] [--competition] stage1..4.slut");
  Options options; options.command = argv[1];
  for (int index = 2; index < argc; ++index) {
    const std::string argument = argv[index];
    auto value = [&]() { if (++index >= argc) throw std::runtime_error("missing option value"); return std::string(argv[index]); };
    if (argument == "-i") options.input = value();
    else if (argument == "-o") options.output = value();
    else if (argument == "-l") options.list = value();
    else if (argument == "-r") options.reps = std::stoi(value());
    else if (argument == "--device") options.device = std::stoi(value());
    else if (argument == "--batch-images") options.batch = std::stoi(value());
    else if (argument == "--block") options.block = std::stoi(value());
    else if (argument == "--competition") options.competition = true;
    else if (!argument.empty() && argument[0] == '-') throw std::runtime_error("unknown option " + argument);
    else options.models.push_back(argument);
  }
  if (options.device < 0 || options.reps < 1 || options.batch < 1 || options.batch > 100 || options.block < 32 || options.block > 1024 || options.block % 32)
    throw std::runtime_error("invalid reps, batch-images, or block size");
  if (options.command != "info" && options.command != "apply" && options.command != "pixels" && options.command != "cube" && options.command != "verify" && options.command != "bench")
    throw std::runtime_error("unknown command " + options.command);
  return options;
}

int main(int argc, char** argv) try {
  const auto process_start = Clock::now();
  const Options options = parse(argc, argv);
  CUDA(cudaSetDevice(options.device));
  cudaDeviceProp properties{}; CUDA(cudaGetDeviceProperties(&properties, options.device));
  int driver_version = 0, runtime_version = 0;
  CUDA(cudaDriverGetVersion(&driver_version)); CUDA(cudaRuntimeGetVersion(&runtime_version));
  std::cout << std::setprecision(10);
  if (options.command == "info") {
    std::cout << "{\"device\":\"" << properties.name << "\",\"device_id\":" << options.device
              << ",\"compute_major\":" << properties.major << ",\"compute_minor\":" << properties.minor
              << ",\"cuda_driver_version\":" << driver_version << ",\"cuda_runtime_version\":" << runtime_version
              << ",\"global_memory_bytes\":" << properties.totalGlobalMem << ",\"multiprocessors\":" << properties.multiProcessorCount
              << ",\"kernel\":\"cuda_q16_fused4\",\"default_kernel\":\"cuda_q16_fused4\",\"available_kernels\":[\"cuda_q16_fused4\"]"
              << ",\"commands\":[\"info\",\"apply\",\"pixels\",\"cube\",\"verify\",\"bench\"],\"benchmark_schema_version\":2"
              << ",\"cpu_main_integration\":false}\n";
    return 0;
  }
  if (options.block > properties.maxThreadsPerBlock) throw std::runtime_error("block exceeds device limit");
  const auto model_start = Clock::now();
  const HostTables host(options.models); const Model model(host);
  const double model_ms = milliseconds(model_start);
  if (options.command == "apply") {
    if (options.input.empty() || options.output.empty()) throw std::runtime_error("apply requires -i image and -o image.png");
    if (std::filesystem::path(options.output).extension() != ".png") throw std::runtime_error("apply output must use .png extension");
    const Image input = load_rgb8(options.input, options.competition);
    std::vector<uint8_t> output(input.rgb.size());
    DeviceBuffer device_input(input.rgb.size()), device_output(input.rgb.size());
    const auto host_start = Clock::now();
    CUDA(cudaMemcpy(device_input.pointer, input.rgb.data(), input.rgb.size(), cudaMemcpyHostToDevice));
    model.apply(static_cast<uint8_t*>(device_input.pointer), static_cast<uint8_t*>(device_output.pointer), input.rgb.size() / 3, options.block);
    CUDA(cudaMemcpy(output.data(), device_output.pointer, output.size(), cudaMemcpyDeviceToHost));
    const double host_ms = milliseconds(host_start);
    stbi_write_png_compression_level = 1;
    if (!stbi_write_png(options.output.c_str(), input.width, input.height, 3, output.data(), input.width * 3))
      throw std::runtime_error("cannot write PNG " + options.output);
    std::cout << "{\"width\":" << input.width << ",\"height\":" << input.height << ",\"stages\":4,\"output_bytes\":" << output.size()
              << ",\"output_checksum_fnv1a64\":\"" << checksum(output.data(), output.size()) << "\",\"host_to_host_ms\":" << host_ms
              << ",\"host_scope\":\"one synchronous pageable-host H2D + fused four-stage kernel + pageable-host D2H; excludes decode, encode, allocation and model setup\"}\n";
    return 0;
  }
  if (options.command == "pixels") {
    if (options.input.empty() || options.output.empty()) throw std::runtime_error("pixels requires -i and -o raw RGB8 files");
    const auto input = read_bytes(options.input);
    if (input.empty() || input.size() % 3) throw std::runtime_error("raw RGB input must contain a positive whole number of pixels");
    DeviceBuffer device_input(input.size()), device_output(input.size());
    std::vector<uint8_t> output(input.size());
    CUDA(cudaMemcpy(device_input.pointer, input.data(), input.size(), cudaMemcpyHostToDevice));
    model.apply(static_cast<uint8_t*>(device_input.pointer), static_cast<uint8_t*>(device_output.pointer), input.size() / 3, options.block);
    CUDA(cudaMemcpy(output.data(), device_output.pointer, output.size(), cudaMemcpyDeviceToHost));
    write_bytes(options.output, output.data(), output.size());
    std::cout << "{\"pixels\":" << input.size() / 3 << ",\"stages\":4,\"output_bytes\":" << output.size() << "}\n";
    return 0;
  }
  if (options.command == "cube") {
    if (options.output.empty()) throw std::runtime_error("cube requires -o");
    constexpr size_t pixels = size_t(1) << 24;
    DeviceBuffer device_output(pixels * 3); std::vector<uint8_t> output(pixels * 3);
    apply_fused4<true><<<static_cast<unsigned int>((pixels + options.block - 1) / options.block), options.block>>>(model.config, nullptr, static_cast<uint8_t*>(device_output.pointer), pixels);
    CUDA(cudaGetLastError()); CUDA(cudaMemcpy(output.data(), device_output.pointer, output.size(), cudaMemcpyDeviceToHost));
    write_bytes(options.output, output.data(), output.size());
    std::cout << "{\"colors\":" << pixels << ",\"stages\":4,\"output_bytes\":" << output.size() << ",\"wall_ms\":" << milliseconds(process_start) << "}\n";
    return 0;
  }
  if (options.list.empty()) throw std::runtime_error("bench and verify require -l");
  const auto decode_start = Clock::now();
  std::ifstream listing(options.list); if (!listing) throw std::runtime_error("cannot read image list");
  constexpr size_t image_pixels = 1024 * 768, image_bytes = image_pixels * 3;
  std::vector<uint8_t> images; images.reserve(image_bytes * 100);
  for (std::string path; std::getline(listing, path);) {
    if (!path.empty() && path.back() == '\r') path.pop_back();
    if (path.empty()) continue;
    if (images.size() / image_bytes >= 100) throw std::runtime_error("bench and verify require exactly 100 images");
    const Image image = load_rgb8(path, true);
    images.insert(images.end(), image.rgb.begin(), image.rgb.end());
  }
  const size_t count = images.size() / image_bytes;
  if (count != 100) throw std::runtime_error("benchmark requires exactly 100 RGB8 images");
  const double decode_ms = milliseconds(decode_start);
  const auto staging_start = Clock::now();
  PinnedBuffer input(images.size()), output(images.size());
  std::memcpy(input.pointer, images.data(), images.size());
  const double staging_ms = milliseconds(staging_start);
  const size_t group_bytes = image_bytes * options.batch;
  DeviceBuffer device_input(group_bytes), device_output(group_bytes);
  std::vector<uint8_t> host_output(images.size());
  auto map_pinned_images = [&]() {
    for (size_t image = 0; image < count; image += options.batch) {
      const size_t group = std::min<size_t>(options.batch, count - image), bytes = group * image_bytes;
      CUDA(cudaMemcpyAsync(device_input.pointer, input.pointer + image * image_bytes, bytes, cudaMemcpyHostToDevice));
      model.apply(static_cast<uint8_t*>(device_input.pointer), static_cast<uint8_t*>(device_output.pointer), group * image_pixels, options.block);
      CUDA(cudaMemcpyAsync(output.pointer + image * image_bytes, device_output.pointer, bytes, cudaMemcpyDeviceToHost));
    }
    CUDA(cudaStreamSynchronize(nullptr));
  };
  if (options.command == "verify") {
    map_pinned_images();
    std::memcpy(host_output.data(), output.pointer, host_output.size());
    if (!options.output.empty()) write_bytes(options.output, host_output.data(), host_output.size());
    std::cout << "{\"verification_only\":true,\"kernel\":\"cuda_q16_fused4\",\"stages\":4,\"images\":" << count
              << ",\"batch_images\":" << options.batch << ",\"output_bytes\":" << host_output.size()
              << ",\"output_checksum_fnv1a64\":\"" << checksum(host_output.data(), host_output.size()) << "\",\"per_image\":[";
    for (size_t image = 0; image < count; ++image) {
      if (image) std::cout << ',';
      std::cout << "{\"index\":" << image << ",\"width\":1024,\"height\":768,\"output_bytes\":" << image_bytes
                << ",\"output_checksum_fnv1a64\":\"" << checksum(host_output.data() + image * image_bytes, image_bytes) << "\"}";
    }
    std::cout << "]}\n";
    return 0;
  }
  Event start, uploaded, applied, downloaded;
  struct TransferEvents { Event start, uploaded, applied, downloaded; };
  std::vector<std::unique_ptr<TransferEvents>> transfer_events;
  for (size_t image = 0; image < count; image += options.batch)
    transfer_events.emplace_back(std::make_unique<TransferEvents>());
  std::vector<double> h2d, kernel, d2h, transfer_event, transfer_wall, resident_event, resident_wall, host_wall;
  double cold_transfer_wall_ms = 0;
  for (int repetition = -1; repetition < options.reps; ++repetition) {
    const auto wall_start = Clock::now();
    size_t group_index = 0;
    for (size_t image = 0; image < count; image += options.batch) {
      const size_t group = std::min<size_t>(options.batch, count - image), bytes = group * image_bytes;
      auto& events = *transfer_events[group_index++];
      events.start.record();
      CUDA(cudaMemcpyAsync(device_input.pointer, input.pointer + image * image_bytes, bytes, cudaMemcpyHostToDevice)); events.uploaded.record();
      model.apply(static_cast<uint8_t*>(device_input.pointer), static_cast<uint8_t*>(device_output.pointer), group * image_pixels, options.block); events.applied.record();
      CUDA(cudaMemcpyAsync(output.pointer + image * image_bytes, device_output.pointer, bytes, cudaMemcpyDeviceToHost)); events.downloaded.record();
    }
    // Stream ordering protects reused device buffers; one synchronization covers
    // all 100 original images. Timing queries are outside the measured wall span.
    transfer_events.back()->downloaded.sync();
    const double wall = milliseconds(wall_start);
    if (repetition == -1) { cold_transfer_wall_ms = wall; continue; }
    double h = 0, k = 0, d = 0;
    for (const auto& events : transfer_events) {
      h += elapsed(events->start, events->uploaded);
      k += elapsed(events->uploaded, events->applied);
      d += elapsed(events->applied, events->downloaded);
    }
    const double total = elapsed(transfer_events.front()->start, transfer_events.back()->downloaded);
    h2d.push_back(h); kernel.push_back(k); d2h.push_back(d); transfer_event.push_back(total); transfer_wall.push_back(wall);
  }
  const uint64_t transfer_checksum = checksum(output.pointer, images.size());
  double cold_host_wall_ms = 0;
  for (int repetition = -1; repetition < options.reps; ++repetition) {
    const auto wall_start = Clock::now();
    // Every repetition starts with the immutable decoded ordinary-host images.
    // Allocation and decoding are outside this interval; both staging copies
    // and the final completion wait are inside it.
    std::memcpy(input.pointer, images.data(), images.size());
    map_pinned_images();
    std::memcpy(host_output.data(), output.pointer, host_output.size());
    const double wall = milliseconds(wall_start);
    if (repetition < 0) cold_host_wall_ms = wall;
    else host_wall.push_back(wall);
  }
  const uint64_t host_checksum = checksum(host_output.data(), host_output.size());
  if (host_checksum != transfer_checksum) throw std::runtime_error("ordinary-host and pinned-transfer output checksums differ");
  // Keep all original images resident so the device-only measure processes the
  // same 100 distinct inputs, and never reapplies the transform to prior output.
  DeviceBuffer resident_input(images.size()), resident_output(images.size());
  CUDA(cudaMemcpy(resident_input.pointer, input.pointer, images.size(), cudaMemcpyHostToDevice));
  for (int repetition = -1; repetition < options.reps; ++repetition) {
    const auto wall_start = Clock::now(); start.record();
    for (size_t image = 0; image < count; image += options.batch) {
      const size_t group = std::min<size_t>(options.batch, count - image);
      model.apply(static_cast<uint8_t*>(resident_input.pointer) + image * image_bytes,
                  static_cast<uint8_t*>(resident_output.pointer) + image * image_bytes, group * image_pixels, options.block);
    }
    applied.record(); applied.sync();
    if (repetition >= 0) { resident_event.push_back(elapsed(start, applied)); resident_wall.push_back(milliseconds(wall_start)); }
  }
  if (!options.output.empty()) {
    write_bytes(options.output, host_output.data(), host_output.size());
  }
  std::cout << "{\"benchmark_schema_version\":2,\"kernel\":\"cuda_q16_fused4\",\"device\":\"" << properties.name << "\",\"images\":" << count
            << ",\"reps\":" << options.reps << ",\"batch_images\":" << options.batch << ",\"block_threads\":" << options.block
            << ",\"model_setup_ms\":" << model_ms << ",\"decode_ms\":" << decode_ms << ",\"host_pinned_staging_ms\":" << staging_ms
            << ",\"cold_transfer_wall_ms\":" << cold_transfer_wall_ms
            << ",\"cold_host_wall_ms\":" << cold_host_wall_ms << ",\"set_host_wall_ms_p50\":" << median(host_wall)
            << ",\"set_transfer_wall_ms_p50\":" << median(transfer_wall) << ",\"set_transfer_event_ms_p50\":" << median(transfer_event)
            << ",\"set_resident_event_ms_p50\":" << median(resident_event) << ",\"set_resident_wall_ms_p50\":" << median(resident_wall)
            << ",\"model_device_bytes\":" << model.nodes.bytes + model.axes.bytes
            << ",\"model_serialized_bytes\":" << host.serialized_bytes << ",\"image_device_buffers_bytes\":" << 2 * group_bytes + 2 * images.size()
            << ",\"host_image_bytes\":" << images.size() << ",\"host_output_bytes\":" << host_output.size() << ",\"host_pinned_bytes\":" << 2 * images.size()
            << ",\"output_bytes\":" << host_output.size() << ",\"output_checksum_fnv1a64\":\"" << host_checksum
            << "\",\"transfer_output_checksum_fnv1a64\":\"" << transfer_checksum << "\",\"host_transfer_output_checksums_match\":true"
            << ",\"process_wall_ms\":" << milliseconds(process_start)
            << ",\"host_scope\":\"ordinary decoded host RGB8 -> pinned copy -> H2D -> fused four-stage kernel -> D2H and synchronization -> ordinary host RGB8 copy; excludes allocation, decode, model setup and checksum\""
            << ",\"transfer_scope\":\"pinned H2D + fused four-stage kernel + D2H; excludes decode, initial pinned staging, model setup and checksum\""
            << ",\"resident_scope\":\"100 original images already on device; kernel sequence and synchronization; excludes H2D and D2H\"";
  print_vector("h2d_ms_reps", h2d); print_vector("kernel_ms_reps", kernel); print_vector("d2h_ms_reps", d2h);
  print_vector("transfer_event_ms_reps", transfer_event); print_vector("transfer_wall_ms_reps", transfer_wall);
  print_vector("set_host_wall_ms_reps", host_wall);
  print_vector("resident_event_ms_reps", resident_event); print_vector("resident_wall_ms_reps", resident_wall);
  std::cout << "}\n";
  return 0;
} catch (const std::exception& error) {
  std::fprintf(stderr, "jshc_gpu: %s\n", error.what()); return 1;
}
