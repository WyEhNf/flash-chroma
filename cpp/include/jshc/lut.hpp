// Sparse 3D LUT core: file formats, portable interpolation kernels, and offline R14 solver.
//
// Formats (little endian):
//   Full LUT  (.lut256): 256*256*256*3 uint8, index ((r*256+g)*256+b)*3+c.
//   Sparse LUT (.slut):
//     char[4]  "SLUT"
//     u32      version (=1)
//     u32      m (lattice points per axis, 2..256)
//     u32      reserved (0)
//     f32[3][m] grid positions (metadata only)
//     u8 [3][256]  idx table   : cell index for input value x on each axis (0..m-2)
//     u32[3][256]  frac table  : Q16 fractional position inside the cell (0..65536)
//     u8 [m*m*m*3] nodes, index ((i*m+j)*m+k)*3+c with i=R, j=G, k=B
#pragma once

#include <array>
#include <cstddef>
#include <cstdint>
#include <memory>
#include <string>
#include <vector>

namespace jshc {

constexpr int kQ = 16;
constexpr int32_t kOne = 1 << kQ;
constexpr int32_t kHalf = 1 << (kQ - 1);

struct FullLut {
  std::vector<uint8_t> data;  // 256^3 * 3
  static FullLut load(const std::string& path);
};

struct SparseLut {
  uint32_t m = 0;
  std::vector<float> grid[3];
  uint8_t idx[3][256]{};
  uint32_t frac[3][256]{};
  std::vector<uint8_t> nodes;  // m^3 * 3

  // Scalar/tri kernels use only the canonical RGB nodes. SIMD tables are created
  // on first use and shared by copies; no duplicate RGBA representation is kept.
  struct PackedTables {
    std::array<uint32_t, 3 * 256> axis;  // (cell index << 17) | Q16 fraction
    std::vector<uint32_t> nodes;         // r | (g << 8) | (b << 16)
  };
  int32_t off[3][256]{};
  int32_t stride[3]{};  // {m^2, m, 1}

  static SparseLut load(const std::string& path);
  void save(const std::string& path) const;
  // Call after editing nodes/axis tables, before applying the LUT. Editing a LUT
  // concurrently with readers is unsupported; concurrent first use is safe.
  void prepare();
  const PackedTables& packed_tables() const;
  // Object and owned vector allocations, including a SIMD cache if materialized.
  // This is a model-memory estimate, not peak process RSS or allocator overhead.
  size_t runtime_bytes() const;

 private:
  mutable std::shared_ptr<const PackedTables> packed_cache_;
};

enum class Kernel {
  TetraAuto,
  TetraScalar,
  TetraCppSimd,
  TetraZigSimd,
  TetraZigSimd4,
  TetraZigSimd8,
  TetraZigSimd16,
  TetraRustSimd,
  TetraAvx2,
  TetraAvx2Madd,
  TetraAvx2ScalarGather,
  TetraAvx2ExactFloat,
  TetraAsm,
  TriFloat,
};
Kernel parse_kernel(const std::string& s);
const char* kernel_name(Kernel k);
bool avx2_available();
bool kernel_available(Kernel k);
Kernel default_kernel();
Kernel resolve_kernel(Kernel k);
// Maximum block workspace per worker; excludes stack frames and model tables.
size_t kernel_scratch_bytes(Kernel k);

// In-place colour mapping of n interleaved RGB pixels through a chain of sparse LUTs.
void apply_chain(const std::vector<const SparseLut*>& chain, uint8_t* rgb, size_t n,
                 Kernel k, int threads);
struct RgbImageView {
  uint8_t* rgb;
  size_t pixels;
};
// Apply to non-overlapping, possibly noncontiguous images in one worker team.
// The images remain independently rounded four-stage chains; no LUT composition.
void apply_chain_batch(const std::vector<const SparseLut*>& chain,
                       const std::vector<RgbImageView>& images, Kernel k, int threads);
void tetra_zig_simd_lanes(const SparseLut& L, const uint8_t* in, uint8_t* out, size_t n,
                          size_t lanes);

// Reference: chain of full 256^3 LUTs (exact lookups).
void apply_full_chain(const std::vector<const FullLut*>& chain, uint8_t* rgb, size_t n,
                      int threads);

// Single-LUT portable kernels on a contiguous pixel block.
void tetra_scalar(const SparseLut& L, const uint8_t* in, uint8_t* out, size_t n);
void tetra_cpp_simd(const SparseLut& L, const uint8_t* in, uint8_t* out, size_t n);
void tetra_zig_simd(const SparseLut& L, const uint8_t* in, uint8_t* out, size_t n);
void tetra_rust_simd(const SparseLut& L, const uint8_t* in, uint8_t* out, size_t n);
void tetra_avx2(const SparseLut& L, const uint8_t* in, uint8_t* out, size_t n);
void tetra_asm(const SparseLut& L, const uint8_t* in, uint8_t* out, size_t n);
void tri_float(const SparseLut& L, const uint8_t* in, uint8_t* out, size_t n);

// Portable C++17 offline solver for R14 (composite 1-stage adaptive + exact tetra LS + 8-colour int_refine).
SparseLut fit_r14(const std::vector<const FullLut*>& chain, uint32_t m, int threads = 0,
                  bool adaptive = true);

}  // namespace jshc
